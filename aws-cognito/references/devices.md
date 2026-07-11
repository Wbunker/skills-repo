# Remembered Devices

Let a trusted device **skip the MFA step** on later sign-ins, and/or tie threat-protection activity logs to a device. Only meaningful in [MFA](mfa.md)-active pools. Applies to **local users signing in with the user pools API** — [managed login](managed-login.md) and federated users don't get remember-device (see [caveats](#caveats)).

## Table of Contents
1. [The three modes](#the-three-modes)
2. [What a remembered device does](#what-a-remembered-device-does)
3. [Confirming a device](#confirming-a-device)
4. [Signing in with a remembered device](#signing-in-with-a-remembered-device)
5. [Managing devices](#managing-devices)
6. [Time-limited trust](#time-limited-trust)
7. [Caveats](#caveats)

---

## The three modes

Set in the console (**Sign-in → Device tracking**) or `DeviceConfiguration` on `CreateUserPool`/`UpdateUserPool`:

- **Don't remember** — no device tracking.
- **Always remember** — every confirmed device is remembered automatically (skips MFA on future device sign-ins).
- **User opt-in** — devices are tracked, but each device is remembered only if the user explicitly chooses to (you prompt them).

With **Always** or **User opt-in**, Cognito issues a **device key + secret** on every sign-in from an unrecognized device.

## What a remembered device does

A remembered device **replaces the MFA challenge with a device-authentication challenge (`DEVICE_SRP_AUTH`)** — it does **not** replace primary authentication. The user still completes their password (or custom challenge) first; the device only stands in for the *second* factor. You **can't** sign a user in with device auth alone, and remembered devices override MFA **only in pools where MFA is active**.

A device that's **confirmed but not remembered** still gets the security benefit: with threat protection on and a device fingerprint in the request, Cognito associates user activity/risk logs with that device — it just doesn't skip MFA.

## Confirming a device

Any sign-in that doesn't already carry a `DEVICE_KEY` returns **`NewDeviceMetadata`** (`DeviceGroupKey` + `DeviceKey`, format `<Region>_<UUID>`) in the `InitiateAuth`/`RespondToAuthChallenge` result. Store it client-side (public app: secure app storage; confidential app: a browser cookie), then:

1. Generate a **new SRP secret for the device** — a fresh high-entropy `DeviceSecret`, a salt, and a password verifier (SRP libraries in the AWS SDKs do this). These are **device-only**, distinct from the user's password/verifier, and never leave the device.
2. Call **`ConfirmDevice`** (token-authorized) with the access token, `DeviceKey`, a friendly device name, and the salt + password verifier.
3. **Always remember** pool → done, device is remembered.
   **User opt-in** pool → `ConfirmDevice` returns `"UserConfirmationNecessary": true`; prompt the user, and if they agree call **`UpdateDeviceStatus`** with `DeviceRememberedStatus: "remembered"`.

## Signing in with a remembered device

Include the stored `DEVICE_KEY` in `AuthParameters` of `InitiateAuth` (works with `USER_SRP_AUTH`, `USER_PASSWORD_AUTH`, `REFRESH_TOKEN_AUTH`, or `CUSTOM_AUTH`; you can also pass it in a `PASSWORD_VERIFIER` response). After primary auth, instead of an MFA challenge Cognito returns:

1. **`DEVICE_SRP_AUTH`** → respond with `USERNAME`, `DEVICE_KEY`, `SRP_A`.
2. **`DEVICE_PASSWORD_VERIFIER`** (carries `SECRET_BLOCK`, `SRP_B`) → compute and respond with `PASSWORD_CLAIM_SIGNATURE`, `PASSWORD_CLAIM_SECRET_BLOCK`, `TIMESTAMP`, `USERNAME`, `DEVICE_KEY` using your SRP library (same SRP math as user sign-in, keyed on `DeviceGroupKey`+`DeviceKey`+`DeviceSecret`).

Tokens are issued after the device verifier passes. In a `CUSTOM_AUTH` flow, the final `DEVICE_SRP_AUTH` comes **after** your custom challenges resolve to `issueTokens: true`.

## Managing devices

All require the `aws.cognito.signin.user.admin` scope (public) or IAM (Admin variants):

| Purpose | Public (access token) | Server-side (IAM) |
|---|---|---|
| List a user's devices | `ListDevices` | `AdminListDevices` |
| Get one device | `GetDevice` | `AdminGetDevice` |
| Set remembered / not-remembered | `UpdateDeviceStatus` | `AdminUpdateDeviceStatus` |
| Forget (delete the device key) | `ForgetDevice` | `AdminForgetDevice` |

Forgetting a device deletes its key — to re-trust it later you must generate and store a **new** device key. Forget (or set not-remembered) when you detect unusual activity and want to force MFA again.

## Time-limited trust

Cognito has no built-in "trust for 30 days." Implement it yourself: on `ConfirmDevice`, store an expiry date in a **custom attribute**; on/after that date, call `UpdateDeviceStatus` → `not_remembered` so the next sign-in re-prompts MFA, then set the device remembered again after the user re-authenticates.

## Caveats

- **Managed login doesn't offer remember-device.** It adds device info to advanced-security (threat-protection) logs, but never prompts to trust a device or skips MFA on one — remember-device is an SDK-only capability.
- **The admin auth flow doesn't support remembered devices** — `AdminInitiateAuth` sign-in works, but later refresh-token calls fail if you rely on device tracking. Don't combine `ADMIN_USER_PASSWORD_AUTH` with device tracking for long-lived sessions.
- **Federated / third-party IdP users** manage their own devices and MFA at the IdP; Cognito device tracking doesn't apply to them.
- With **device remembering on**, refresh via `GetTokensFromRefreshToken` must include the `device_key` ([tokens.md](tokens.md#refresh-tokens--rotation)).
</content>
