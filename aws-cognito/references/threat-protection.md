# Threat Protection (Advanced Security)

Cognito's **Plus-plan** account-takeover defense: detect compromised passwords, risk-score sign-ins, and auto-respond (block / force MFA / notify). Formerly "advanced security features." Application-layer and per-user — for **volumetric/DDoS** defense use [AWS WAF](security.md#network-protection-waf--sms-abuse) instead. Doesn't apply to **federated** sign-in or **M2M** client-credentials.

## Table of Contents
1. [Components & prerequisites](#components--prerequisites)
2. [Modes & scoping](#modes--scoping)
3. [Compromised credentials](#compromised-credentials)
4. [Adaptive authentication](#adaptive-authentication)
5. [Passing device/context data](#passing-devicecontext-data)
6. [IP allow/block lists](#ip-allowblock-lists)
7. [Event history, feedback & log export](#event-history-feedback--log-export)
8. [SetRiskConfiguration shape](#setriskconfiguration-shape)

---

## Components & prerequisites

Four capabilities: **compromised-credentials** detection, **adaptive authentication** (risk-based response), **IP allow/block** lists, and **log export**.

- **Requires the Plus feature plan.** Turn on with `UserPoolAddOns.AdvancedSecurityMode` = `AUDIT` or `ENFORCED` (`OFF` disables) — this also forces the pool tier to Plus.
- **Adaptive auth requires MFA = `OPTIONAL`** ([mfa.md](mfa.md)).
- Email notifications need an **SES** config ([messaging.md](messaging.md#email-default-vs-ses)).

## Modes & scoping

- **Audit** — score risk, log, take **no action**. **Run audit-only ≥2 weeks** before enforcing so the model learns your traffic and you can feed it [event feedback](#event-history-feedback--log-export).
- **Full function** (`ENFORCED`) — apply the configured automatic responses.
- **No enforcement** — disable monitoring for one auth type without affecting the other.

Scope is layered: a **pool-level** config covers all app clients; an **app-client-level** config **overrides** it. And **standard vs. custom authentication** are configured separately (same automated-response set in full-function, but independent enforcement modes) — e.g. only notify on a risky *custom-auth* sign-in but block the same risk on username-password.

## Compromised credentials

Compares submitted passwords against leaked-credential corpora **and** commonly-guessed passwords.

- **Only sees plaintext-password flows**: `USER_PASSWORD_AUTH`, `ADMIN_USER_PASSWORD_AUTH`, and the `PASSWORD` option of `USER_AUTH`. **SRP (`USER_SRP_AUTH`) and custom auth are invisible to it** — Cognito never receives the plaintext, so it can't check. (SRP still gets adaptive auth.)
- **Events** (`EventFilter`): `SIGN_UP`, `SIGN_IN`, `PASSWORD_CHANGE`. Checks `SignUp`, password sign-in, and `ConfirmForgotPassword`; also `NEW_PASSWORD_REQUIRED` responses — but **not** admin-set passwords (`AdminSetUserPassword`).
- **Actions**: `BLOCK` or `ALLOW` (both log). **Block sets the user to `RESET_REQUIRED`** — they must reset before signing in again.

## Adaptive authentication

Assigns each session a risk level — **High / Medium / Low / NoRisk** — from IP, user-agent, and geographic/behavioral distance. Per-level response:

| Response | Effect |
|---|---|
| `NO_ACTION` (Allow) | sign in normally |
| `MFA_IF_CONFIGURED` (Optional MFA) | force MFA **if** the user has a factor; else allow |
| `MFA_REQUIRED` (Require MFA) | force MFA; if none configured, **prompt setup** (have phone/TOTP capture ready first) |
| `BLOCK` | deny sign-in |
| + `Notify` | email the user about the risk (works with any action) |

- **You can't assign a *less*-restrictive response to a *higher* risk level.**
- Works across `USER_PASSWORD_AUTH`, `ADMIN_USER_PASSWORD_AUTH`, `USER_SRP_AUTH`, and `CUSTOM_AUTH`. In a **custom-auth** flow, risk is evaluated **after the final Define Auth Challenge, before tokens issue** — a `BLOCK`/require-MFA response still applies on top of your Lambda-graded challenges. You must populate `UserContextData` yourself (custom auth is SDK-only, so no managed login to auto-collect the fingerprint).
- **Feedback loop:** marking events valid/invalid ([below](#event-history-feedback--log-export)) retrains scoring — and applying an `Allow` to a high-risk session lowers the risk of *similar* future sessions.
- **Notifications fire only when an automated response fires** (block/allow/optional-MFA/require-MFA). A failed password logged with a risk score but no response → no email. Emails send even to **unverified** addresses.

## Passing device/context data

Accurate risk scoring needs a **device fingerprint**; without it, Cognito only sees the source IP (and only when the client calls it directly).

- **Client-side / unauthenticated ops** (`InitiateAuth`, `SignUp`, …): send **`UserContextData`** with `EncodedData` from the JS/iOS/Android fingerprint module (`amazon-cognito-advanced-security-data.min.js` → `AmazonCognitoAdvancedSecurityData.getData(user, poolId, clientId)`). Managed login and Amplify (except Amplify JS) collect it automatically.
- **Server-side / authenticated ops** (`AdminInitiateAuth`, `AdminRespondToAuthChallenge`): send **`ContextData`** = the client's `EncodedData` **plus** the real user IP, server name, and path extracted from the inbound HTTP request (so risk reflects the *user's* endpoint, not your proxy).
- To let an **unauthenticated** op carry a real client **IP** (not just fingerprint), set `EnablePropagateAdditionalUserContextData: true` on the app client — requires Plus **and a client secret**.

## IP allow/block lists

Full-function only; `RiskExceptionConfiguration` with CIDR ranges (`192.0.2.0/24`, `.../32` for one IP):
- **`BlockedIPRangeList`** — sessions are denied and get **no** risk scoring; blocked users can't use SDK/managed login (**but can still sign in via a third-party IdP**). Blocked requests **still count** toward request-rate quotas.
- **`SkippedIPRangeList`** (always-allow) — no adaptive-auth MFA applied, **but compromised-credentials checks still run**.
- Neither list affects **token refresh**.

## Event history, feedback & log export

- **Per-user event log**: console **Users** menu or `AdminListUserAuthEvents`. Each event has an `EventId`, `EventType`, `EventResponse`, `EventRisk` (`RiskDecision`, `CompromisedCredentialsDetected`), and `EventContextData` (IP/device/city/country). **Retained 2 years.**
- **Token correlation**: the `EventId` is embedded in the ID/access token payload (`event_id`) and carried through refresh — trace any token back to its sign-in event.
- **Feedback**: `AdminUpdateAuthEventFeedback` / `UpdateAuthEventFeedback` (or console **Provide event feedback** / the one-click link in a notification email) with `FeedbackValue` `valid`|`invalid` — trains risk scoring in real time.
- **Log export**: `SetLogDeliveryConfiguration` with `EventSource: "userAuthEvents"` → S3, CloudWatch Logs, or Firehose (console: **Log streaming**). Disabling export is a prerequisite for leaving the Plus tier.

## SetRiskConfiguration shape

`SetRiskConfiguration` sets the risk rules; omit `ClientId` for the pool, include it for an app-client override. `AdvancedSecurityMode` (on `Update/CreateUserPool`) still has to be `ENFORCED` for actions to fire.

```json
{
  "UserPoolId": "us-west-2_EXAMPLE",
  "AccountTakeoverRiskConfiguration": {
    "Actions": {
      "LowAction":    { "EventAction": "NO_ACTION",       "Notify": true },
      "MediumAction": { "EventAction": "MFA_IF_CONFIGURED","Notify": true },
      "HighAction":   { "EventAction": "MFA_REQUIRED",     "Notify": true }
    },
    "NotifyConfiguration": {
      "From": "admin@example.com", "ReplyTo": "admin@example.com",
      "SourceArn": "arn:aws:ses:us-west-2:123456789012:identity/admin@example.com",
      "BlockEmail":    { "Subject": "Blocked",  "TextBody": "Blocked {username} at {login-time} from {ip-address}." },
      "MfaEmail":      { "Subject": "MFA",      "TextBody": "Sign-in from {city},{country} needs MFA." },
      "NoActionEmail": { "Subject": "Heads up", "TextBody": "New sign-in by {username} — reset if not you." }
    }
  },
  "CompromisedCredentialsRiskConfiguration": {
    "Actions": { "EventAction": "BLOCK" },
    "EventFilter": ["SIGN_UP", "SIGN_IN", "PASSWORD_CHANGE"]
  },
  "RiskExceptionConfiguration": {
    "BlockedIPRangeList": ["192.0.2.0/24"],
    "SkippedIPRangeList": ["203.0.113.0/24"]
  }
}
```

Notification placeholders (`{username}`, `{ip-address}`, `{city}`, `{country}`, `{login-time}`, `{device-name}`, one-click feedback links) are in [messaging.md](messaging.md#message-templates--placeholders).
</content>
