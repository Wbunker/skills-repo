# Authentication Flows (AWS SDK)

How to authenticate users with the Cognito user pools API when you build your **own** UI. For Cognito-hosted pages, see [managed-login.md](managed-login.md). For token verification after sign-in, see [backend.md](backend.md).

## Table of Contents
1. [The request/challenge model](#the-requestchallenge-model)
2. [Authorization models & API operation classes](#authorization-models)
3. [Flow selection](#flow-selection)
4. [USER_SRP_AUTH (recommended password flow)](#user_srp_auth)
5. [USER_PASSWORD_AUTH (simple)](#user_password_auth)
6. [USER_AUTH (choice-based / passwordless / passkeys)](#user_auth)
7. [ADMIN_USER_PASSWORD_AUTH (server-side)](#admin_user_password_auth)
8. [CUSTOM_AUTH (Lambda challenge)](#custom_auth)
9. [Refresh tokens](#refresh-tokens)
10. [Remembered devices](#remembered-devices)
11. [Handling challenges](#handling-challenges)
12. [SECRET_HASH](#secret_hash)

---

## The request/challenge model

Sign-in is a loop: start with `InitiateAuth` (public) or `AdminInitiateAuth` (server, IAM-signed). Cognito either returns tokens (`AuthenticationResult`) or a **challenge** (`ChallengeName` + `Session`). Answer each challenge with `RespondToAuthChallenge` (or `AdminRespondToAuthChallenge`), passing back the `Session` string, until tokens are issued.

```
InitiateAuth ──► tokens?  ──────────────► done
     │              │
     └► ChallengeName + Session
                    │
        RespondToAuthChallenge (echo Session) ──► tokens? or next challenge ─┐
                    ▲                                                        │
                    └────────────────────────────────────────────────────────┘
```

Each challenge must be answered within the app client's **auth session duration** (default 3 min, `AuthSessionValidity`). Managed login uses fixed durations: 3 min for MFA, 8 min for password-reset codes.

## Authorization models

Every user pools API operation falls into one of **three authorization models** — this determines what you must present to call it, and only two of them are IAM-gated:

| Model | Authorized by | Example operations |
|---|---|---|
| **IAM-authorized** | SigV4 signature (AWS creds) | Management: `CreateUserPool`, `UpdateUserPoolClient`, `CreateIdentityProvider`. User: all `Admin*` (`AdminInitiateAuth`, `AdminCreateUser`, `AdminSetUserPassword`) |
| **Public (unauthenticated)** | nothing (+ `SECRET_HASH` if the client has a secret) | `SignUp`, `ConfirmSignUp`, `ResendConfirmationCode`, `ForgotPassword`, `ConfirmForgotPassword`, `InitiateAuth` |
| **Token-authorized** | an **access token** or an in-flight **session** token | `RespondToAuthChallenge` (session), `GetUser`/`ChangePassword`/`UpdateUserAttributes`/`GlobalSignOut` (access), WebAuthn registration, `RevokeToken` (refresh token) |

Consequences:
- **You can only write IAM policies for the IAM-authorized operations.** `InitiateAuth`/`SignUp`/`GetUser` ignore IAM — constrain them with app-client settings, not policy ([security.md](security.md)).
- **Every public op has an `Admin*` server-side twin** (e.g. `UpdateUserAttributes`↔`AdminUpdateUserAttributes`). Public ops are user-initiated and often need confirmation; admin ops assume an administrator and take effect immediately.
- **Public (client-side) = mobile/SPA** with no secret and no AWS creds, using `InitiateAuth` + token-authorized ops. **Server-side = confidential** with a secret and AWS creds, using `AdminInitiateAuth`.
- Token-authorized ops take the access token as `Authorization: Bearer <token>`.

## Flow selection

Every flow must be enabled in the app client's `ExplicitAuthFlows`, else `NotAuthorizedException`. Prefix with `ALLOW_`.

| `AuthFlow` value | ExplicitAuthFlows | Use |
|---|---|---|
| `USER_SRP_AUTH` | `ALLOW_USER_SRP_AUTH` | Password without sending it over the wire (**default choice**) |
| `USER_PASSWORD_AUTH` | `ALLOW_USER_PASSWORD_AUTH` | Simple; password sent to Cognito over TLS |
| `USER_AUTH` | `ALLOW_USER_AUTH` | Choice-based: password, email/SMS OTP, passkey (**passwordless lives here**) |
| `ADMIN_USER_PASSWORD_AUTH` | `ALLOW_ADMIN_USER_PASSWORD_AUTH` | Trusted backend authenticates on behalf of user |
| `CUSTOM_AUTH` | `ALLOW_CUSTOM_AUTH` | Your own challenge sequence via Lambda triggers |
| `REFRESH_TOKEN_AUTH` | `ALLOW_REFRESH_TOKEN_AUTH` | Exchange refresh token for new tokens |

## USER_SRP_AUTH

Secure Remote Password — the password never leaves the client; SRP proves knowledge of it. Preferred for password auth. The SRP math is nontrivial; **use an SDK/library that implements it** rather than hand-rolling:

- Browser/JS: `amazon-cognito-identity-js` or Amplify (`signIn`) — SRP by default. See [web-frontend.md](web-frontend.md).
- Node backend: `amazon-cognito-identity-js`, or `warrant`/`pysrp` in Python.

You rarely call `InitiateAuth USER_SRP_AUTH` by hand; let the library do the `SRP_A`/`PASSWORD_VERIFIER` exchange.

## USER_PASSWORD_AUTH

Send username + password directly. Simplest to script; fine over TLS; enables server-side migration triggers. Node SDK v3:

```js
import { CognitoIdentityProviderClient, InitiateAuthCommand } from "@aws-sdk/client-cognito-identity-provider";

const client = new CognitoIdentityProviderClient({ region: "us-east-1" });
const res = await client.send(new InitiateAuthCommand({
  AuthFlow: "USER_PASSWORD_AUTH",
  ClientId: CLIENT_ID,
  AuthParameters: {
    USERNAME: "user@example.com",
    PASSWORD: "…",
    // SECRET_HASH: "…"  // only if the app client has a secret
  },
}));
if (res.AuthenticationResult) {
  const { IdToken, AccessToken, RefreshToken } = res.AuthenticationResult;
} else {
  // res.ChallengeName / res.Session — handle challenge
}
```

Python (boto3):

```python
import boto3
client = boto3.client("cognito-idp", region_name="us-east-1")
res = client.initiate_auth(
    ClientId=CLIENT_ID,
    AuthFlow="USER_PASSWORD_AUTH",
    AuthParameters={"USERNAME": "user@example.com", "PASSWORD": "…"},
)
tokens = res.get("AuthenticationResult")
```

## USER_AUTH

Choice-based sign-in and the **only** flow with passwordless (email/SMS OTP) and passkeys. First call discovers available factors, or you declare one directly.

Enable factors on the pool with a sign-in policy:
```bash
aws cognito-idp update-user-pool --user-pool-id "$POOL_ID" \
  --policies 'SignInPolicy={AllowedFirstAuthFactors=[PASSWORD,EMAIL_OTP,SMS_OTP,WEB_AUTHN]}'
```

Choice factor names map to the client-based flows: **`PASSWORD`** = `USER_PASSWORD_AUTH`, **`PASSWORD_SRP`** = `USER_SRP_AUTH`, plus `EMAIL_OTP` / `SMS_OTP` / `WEB_AUTHN`.

Three ways to drive it:
- **Discover** — send only `USERNAME` → Cognito returns `SELECT_CHALLENGE` + `AvailableChallenges`; show them and let the user pick.
- **Prefer** — send `PREFERRED_CHALLENGE`. If available, Cognito returns that challenge's next step (`PASSWORD_SRP` also requires `SRP_A` and returns `PASSWORD_VERIFIER`; `EMAIL_OTP`/`SMS_OTP` return `CodeDeliveryDetails`). If not available, you get `SELECT_CHALLENGE` + the list.
- **Sign in first, then branch** — after a normal sign-in, `GetUserAuthFactors` (access token) returns a user's available choice-based factors and MFA settings, so they can add or switch a method.

**Discover options** (returns `AvailableChallenges`):
```js
await client.send(new InitiateAuthCommand({
  AuthFlow: "USER_AUTH",
  ClientId: CLIENT_ID,
  AuthParameters: { USERNAME: "user@example.com" },
}));
// → ChallengeName: "SELECT_CHALLENGE", AvailableChallenges: ["PASSWORD","EMAIL_OTP","WEB_AUTHN"]
```

**Email OTP** (passwordless): declare the preference, Cognito emails a code, answer it:
```js
// 1. start with preferred factor
await client.send(new InitiateAuthCommand({
  AuthFlow: "USER_AUTH", ClientId: CLIENT_ID,
  AuthParameters: { USERNAME: "user@example.com", PREFERRED_CHALLENGE: "EMAIL_OTP" },
})); // → ChallengeName: "EMAIL_OTP", Session

// 2. user enters the emailed code
await client.send(new RespondToAuthChallengeCommand({
  ClientId: CLIENT_ID, ChallengeName: "EMAIL_OTP", Session: session,
  ChallengeResponses: { USERNAME: "user@example.com", EMAIL_OTP_CODE: "123456" },
})); // → AuthenticationResult
```

**Passkeys / WebAuthn** (`WEB_AUTHN` challenge) require a browser WebAuthn ceremony, available through managed login or an SDK that implements the credential exchange (Amplify JS). The passkey relying-party ID must be a domain you own and **not on the public suffix list**.
- **Registration is separate from sign-in** and happens *after* a user is signed in, via token-authorized ops: `StartWebAuthnRegistration` → (browser creates the credential) → `CompleteWebAuthnRegistration`. Manage with `ListWebAuthnCredentials` / `DeleteWebAuthnCredential`.
- A passkey with user verification can satisfy MFA when the pool is set to `MULTI_FACTOR_WITH_USER_VERIFICATION`. A user who signed in with an **OTP first factor cannot then add MFA** in that session.

## ADMIN_USER_PASSWORD_AUTH

Server-side: a trusted backend (with IAM permissions) authenticates the user. Uses `AdminInitiateAuth` and hits the pool directly. Requires the app client to allow the flow and typically an app client **secret**.

```python
res = client.admin_initiate_auth(
    UserPoolId=POOL_ID, ClientId=CLIENT_ID,
    AuthFlow="ADMIN_USER_PASSWORD_AUTH",
    AuthParameters={"USERNAME": u, "PASSWORD": p, "SECRET_HASH": secret_hash},
)
```

Use for backend-for-frontend patterns where the browser never talks to Cognito. Don't use from public clients. Requires `cognito-idp:AdminInitiateAuth` + `cognito-idp:AdminRespondToAuthChallenge`.

Two admin-flow gotchas:
- **`USER_ID_FOR_SRP`** in the `AdminInitiateAuth` response `ChallengeParameters` is the user's *actual* username (not an alias like email). Pass **that** value as `USERNAME` in `AdminRespondToAuthChallenge`, or the challenge fails.
- **The admin flow doesn't support remembered devices.** With device tracking on, admin sign-in succeeds but subsequent **refresh-token calls fail** — don't combine admin auth with device tracking for long-lived sessions.

## CUSTOM_AUTH

Your own challenge sequence, orchestrated by three Lambda triggers: **Define auth challenge** (decides next step), **Create auth challenge** (produces it), **Verify auth challenge response** (grades it). Start with `AuthFlow: "CUSTOM_AUTH"`; Cognito returns `CUSTOM_CHALLENGE`; answer with `RespondToAuthChallenge` carrying `ANSWER`. Classic use: magic links, CAPTCHA gates, custom OTP, **third-party MFA** (Duo/Okta via redirect+callback), and **WebAuthn/passkeys the DIY way** — before native passkey support you stored the credential public key in a write-only custom attribute and verified the signature in the verify trigger. **Prefer native passkeys via `USER_AUTH`** now ([above](#user_auth)); reach for custom auth only when you need a factor Cognito doesn't offer. **Not compatible with managed login.** See [lambda-triggers.md](lambda-triggers.md).

## Refresh tokens

```js
await client.send(new InitiateAuthCommand({
  AuthFlow: "REFRESH_TOKEN_AUTH",
  ClientId: CLIENT_ID,
  AuthParameters: { REFRESH_TOKEN: refreshToken /*, SECRET_HASH */ },
}));
// → AuthenticationResult with new IdToken + AccessToken (no new RefreshToken unless rotation on)
```

- The refresh token itself is not re-issued unless refresh-token rotation is enabled.
- Revoke a refresh token (and its descendants) with `RevokeToken` or `AdminUserGlobalSignOut`.
- Newer API `GetTokensFromRefreshToken` supports rotation explicitly.

## Remembered devices

With device tracking on, a trusted device **substitutes for the MFA step** (a `DEVICE_SRP_AUTH` challenge) on later sign-ins — pass the stored `DEVICE_KEY` in `AuthParameters`. After the first sign-in, confirm the device with the token-authorized `ConfirmDevice`. Full flow, modes, the device SRP exchange, management APIs, and caveats: [devices.md](devices.md). Caveat: **not supported in the admin auth flow** (see above).

## Handling challenges

Common `ChallengeName` values and required `ChallengeResponses`:

| ChallengeName | Respond with |
|---|---|
| `NEW_PASSWORD_REQUIRED` | `NEW_PASSWORD`, `USERNAME` (admin-created temp password) |
| `SMS_MFA` | `SMS_MFA_CODE`, `USERNAME` |
| `SOFTWARE_TOKEN_MFA` | `SOFTWARE_TOKEN_MFA_CODE`, `USERNAME` |
| `EMAIL_OTP` / `SMS_OTP` | `EMAIL_OTP_CODE` / `SMS_OTP_CODE`, `USERNAME` |
| `SELECT_CHALLENGE` | `ANSWER` = chosen factor (USER_AUTH) |
| `CUSTOM_CHALLENGE` | `ANSWER` (+ whatever your Lambda expects) |
| `MFA_SETUP` | associate a TOTP first (`AssociateSoftwareToken` → `VerifySoftwareToken`) |

Always echo the `Session` from the previous response.

## SECRET_HASH

If the app client has a secret, every unauthenticated call (`InitiateAuth`, `RespondToAuthChallenge`, `SignUp`, `ConfirmSignUp`, `ForgotPassword`) needs a `SECRET_HASH`:

```python
import base64, hmac, hashlib
def secret_hash(username, client_id, client_secret):
    msg = (username + client_id).encode()
    return base64.b64encode(
        hmac.new(client_secret.encode(), msg, hashlib.sha256).digest()
    ).decode()
```

```js
import { createHmac } from "crypto";
const secretHash = (username, clientId, clientSecret) =>
  createHmac("sha256", clientSecret).update(username + clientId).digest("base64");
```

The best fix is usually to **not** give public clients a secret.
