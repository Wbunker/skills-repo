# Multi-Factor Authentication (MFA)

Configuring MFA, per-user factor preferences, the challenge state machine, and per-factor setup. MFA applies to **local users only** — federated users' second factor is the IdP's responsibility. The MFA⇄account-recovery lockout is detailed in [user-management.md](user-management.md#passwords--account-recovery); remembered devices that skip MFA are in [devices.md](devices.md).

## Table of Contents
1. [Modes & methods](#modes--methods)
2. [Required vs. optional behavior](#required-vs-optional-behavior)
3. [Per-user MFA preferences](#per-user-mfa-preferences)
4. [The challenge state machine](#the-challenge-state-machine)
5. [Setting up each factor](#setting-up-each-factor)
6. [Interactions & gotchas](#interactions--gotchas)

---

## Modes & methods

**Mode** (`MfaConfiguration` on `CreateUserPool`/`UpdateUserPool`, or the dedicated `SetUserPoolMfaConfig`):
- **`OFF`** — no second factor; users can't register one.
- **`OPTIONAL`** — per-user opt-in; **required for adaptive authentication** (threat protection).
- **`ON`** (required) — every user must set up and use MFA.

**Methods** (the `MFA methods` setting = `SetUserPoolMfaConfig`):

| Factor | Challenge | Gating |
|---|---|---|
| **SMS** | `SMS_MFA` | An active [SMS/SNS config](messaging.md#sms-sns-setup) auto-enables it. **Once SMS is configured you can't disable it as an MFA factor.** |
| **TOTP** (authenticator app) | `SOFTWARE_TOKEN_MFA` | Always available; no external service. |
| **Email** | `EMAIL_OTP` | **Essentials/Plus plan + your own SES config** ([messaging.md](messaging.md#email-default-vs-ses)). Auto-enabled once both hold. |

## Required vs. optional behavior

- **Required**: **managed login** prompts users to enrol at first opportunity and collects the email/phone/TOTP for them. Users **can't enable/disable** methods — you can only set the *preferred* one. Include MFA setup in onboarding or users can't sign in.
- **Optional**: managed login **won't** prompt users to set up MFA (build your own "enable MFA" UI with the APIs below) — but it *will* prompt for a code if the user has a preferred method. Use optional for adaptive auth.
- **First sign-in nuance:** on a brand-new user's **first** sign-in, Cognito issues tokens even in a required-MFA pool — confirming the sign-up verification message *is* their second factor that one time. MFA enrolment is prompted on **subsequent** sign-ins.

## Per-user MFA preferences

A user can register **multiple** factors but only **one is active/preferred** at a time.

- **Self-service** (public app, user's access token): `SetUserMFAPreference` — sets each factor `Enabled` and one `PreferredMfa: true`.
- **Admin** (server-side, IAM): `AdminSetUserMFAPreference`.
- Also settable from the console **Users** menu.

A user with no preference set receives a `SELECT_MFA_TYPE` challenge at sign-in to choose one. If only one method is available pool-wide, you don't need to manage preferences at all.

## The challenge state machine

MFA surfaces through the [request/challenge loop](auth-flows.md#the-requestchallenge-model). After username/password, Cognito may return:

| Challenge | Meaning | Respond with |
|---|---|---|
| `SMS_MFA` | code sent by SMS | `SMS_MFA_CODE` |
| `EMAIL_OTP` | code sent by email | `EMAIL_OTP_CODE` |
| `SOFTWARE_TOKEN_MFA` | enter TOTP | `SOFTWARE_TOKEN_MFA_CODE` |
| `SELECT_MFA_TYPE` | user has >1 eligible factor, no preference | `ANSWER` = chosen type (options in `MFAS_CAN_SELECT`) |
| `MFA_SETUP` | required MFA, nothing enrolled yet | enrol a factor, then echo `SESSION` (options in `MFAS_CAN_SETUP`) |

The response's `CODE_DELIVERY_DESTINATION` tells you where a code went (masked). The code is valid for the app client's **`AuthSessionValidity`** (auth-flow session duration), not a fixed time.

## Setting up each factor

**TOTP** (before it can be used, or to satisfy an `MFA_SETUP` challenge):
1. `AssociateSoftwareToken` (access token *or* the challenge session) → returns a `SecretCode`.
2. User adds it to their authenticator app (show a QR of `otpauth://totp/...?secret=<SecretCode>`).
3. `VerifySoftwareToken` with a current code → returns a `Session`.
4. If mid-sign-in, answer `MFA_SETUP` with `{ USERNAME, SESSION }` from step 3, then respond to the follow-up `SOFTWARE_TOKEN_MFA`.

TOTP specifics:
- **Authenticator apps must use HMAC-SHA1.** A SHA-256 authenticator returns `Code mismatch`. Cognito allows **±30 s** clock skew.
- **No hardware tokens**, software TOTP only. TOTP must be enabled at the pool level or `AssociateSoftwareToken` throws `SoftwareTokenMFANotFoundException`.
- **You can't delete a TOTP token** — to *replace* it, associate + verify a new one; to *disable* it, `SetUserMFAPreference` to no MFA (or another factor). Users who set up TOTP keep it working even if you later disable TOTP pool-wide.
- **WAF CAPTCHA breaks managed-login TOTP registration.** A CAPTCHA rule fires on the background `AssociateSoftwareToken`/`VerifySoftwareToken` calls → "Request not allowed due to WAF captcha." Exclude those two `x-amzn-cognito-operation-name` header values from the CAPTCHA action ([security.md](security.md#network-protection-waf--sms-abuse)). SMS MFA is unaffected.

**SMS / email** — no setup call: as soon as the user has a `phone_number`/`email` attribute the factor works. Cognito can send the MFA code to an **unverified** address/number, and **marks it verified** after the first successful MFA. (Self-service change of an MFA email/phone requires signing in with an access token — if the user loses access to it, an admin must fix it via `AdminUpdateUserAttributes`.)

## Interactions & gotchas

- **MFA vs. passwordless are mutually exclusive**, with one exception: you **can't** set MFA required in a pool that allows email/SMS **OTP first factors** (`AllowedFirstAuthFactors`), and vice-versa. The exception is **passkeys** — a `WEB_AUTHN` factor with `MULTI_FACTOR_WITH_USER_VERIFICATION` satisfies the MFA requirement.
- **Choice-based sign-in narrows under required MFA** — only `PASSWORD`/`PASSWORD_SRP` first factors are offered when MFA is required.
- **Adaptive authentication requires MFA = optional** (full-function threat protection assigns MFA per risk; it can't do that if MFA is off or hard-required).
- **Same-factor lockout:** a user's MFA channel can't also be their password-recovery channel. Email-MFA users can't recover by email; SMS-MFA users can't recover by SMS. A user with only one contact attribute in a required-MFA pool can be **unable to sign in *and* unable to reset** — Cognito returns an error. Fix: require **both** `email` and `phone_number` (Cognito then auto-assigns the non-recovery channel as MFA). Full treatment: [user-management.md](user-management.md#passwords--account-recovery).
- **5 wrong MFA codes** starts the [exponential lockout](auth-flows.md).
- **SMS sandbox** blocks MFA texts to unverified numbers until you move to production ([messaging.md](messaging.md#sms-sns-setup)).
- **Security note:** SMS is the weakest factor (SIM-swap, number reassignment). Prefer **TOTP or passkeys**; treat SMS MFA as a fallback.
</content>
