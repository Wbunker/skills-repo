# User Management (Lifecycle, Verification, Groups)

Managing the user directory: how users enter the pool, account states, confirmation vs. verification, admin-created users, and groups. Attributes/aliases are in [attributes.md](attributes.md); message delivery in [messaging.md](messaging.md); server-side admin API code in [backend.md](backend.md#admin--server-side-operations).

## Table of Contents
1. [Account states](#account-states)
2. [How users enter the pool](#how-users-enter-the-pool)
3. [Confirmation vs. verification](#confirmation-vs-verification)
4. [Verifying a second contact method](#verifying-a-second-contact-method)
5. [Attribute-update verification (aliases)](#attribute-update-verification-aliases)
6. [Admin-created users](#admin-created-users)
7. [Disabling self-service sign-up](#disabling-self-service-sign-up)
8. [Find & manage users](#find--manage-users)
9. [Passwords & account recovery](#passwords--account-recovery)
10. [Importing users](#importing-users)
11. [Detecting inactive users](#detecting-inactive-users)
12. [Groups](#groups)

---

## Account states

| Status | Meaning | Enters this way |
|---|---|---|
| `UNCONFIRMED` | Signed up, can't sign in until confirmed | Self sign-up |
| `CONFIRMED` | Can sign in | After confirmation; passwordless admin-created; permanent password set |
| `FORCE_CHANGE_PASSWORD` | Temp password works once; must set a new one (via `NEW_PASSWORD_REQUIRED`) | Admin-created **with** a temp password |
| `RESET_REQUIRED` | Must reset password before first sign-in (`ForgotPassword`→`ConfirmForgotPassword`) | CSV-imported users |
| `EXTERNAL_PROVIDER` | Federated user | IdP sign-in ([federation.md](federation.md#account-linking)) |
| `DISABLED` | Sign-in blocked | `AdminDisableUser`; **required before you can delete a user** |

## How users enter the pool

1. **Self sign-up** — `SignUp` (public) → `UNCONFIRMED` → `ConfirmSignUp` with the code → `CONFIRMED`. Managed login does this for you.
2. **Admin-created** — `AdminCreateUser` → `FORCE_CHANGE_PASSWORD` (or `CONFIRMED`; see below), sends an invitation with username + temp password.
3. **CSV import** — bulk load → `RESET_REQUIRED`, **no invitation sent**; users run the forgot-password flow to set a password. At least one of email/phone must be imported as verified.
4. **Federation** — first IdP sign-in creates an `EXTERNAL_PROVIDER` profile ([federation.md](federation.md)).

**Password at sign-up is required** unless *all* hold: passwordless is enabled, you use the SDK (not managed login, which always asks), the user supplies a passwordless factor attribute, that attribute auto-verifies, and the `SignUp` omits `Password`.

## Confirmation vs. verification

Two different things people conflate:
- **Confirmation** — the gate that lets a user *sign in* (`UNCONFIRMED`→`CONFIRMED`).
- **Verification** — proof the user *owns* an email/phone (sets `email_verified`/`phone_number_verified`).

With Cognito-assisted verification on, `SignUp` triggers a **code or link, valid 24 hours**; entering it via `ConfirmSignUp` both confirms the account **and** marks that one contact attribute verified. Expired? `ResendConfirmationCode`.

- **A verified email or phone is required for password recovery** (`ForgotPassword` delivers the code there). Auto-confirming via a pre-sign-up trigger **without** auto-verifying a contact method can permanently lock a user out — always auto-verify at least one.
- **Admin confirmation** (`AdminConfirmSignUp`) works only for *self-signup* users. To "confirm" an admin-created user instead, set a permanent password (`AdminSetUserPassword` `Permanent=true`).
- Successfully completing **email/SMS OTP** (passwordless or MFA) also marks that attribute verified.

## Verifying a second contact method

Cognito verifies **only one** contact method at sign-up — if both email and phone are provided, it verifies the **phone** (SMS code) and leaves email unverified. To verify the second one, *after* the user signs in (needs an access token):
`GetUserAttributeVerificationCode(AccessToken, AttributeName="email")` → user gets a code → `VerifyUserAttribute(AccessToken, AttributeName="email", Code=…)`.

## Attribute-update verification (aliases)

When a user changes a sign-in `email`/`phone_number`, the pool property **`AttributesRequireVerificationBeforeUpdate`** ("Keep original attribute value active when an update is pending") controls the risk:
- **On (recommended):** the old value stays verified and sign-in-eligible until the user verifies the new one (via `VerifyUserAttribute`). A typo can't lock them out.
- **Off:** with **alias** attributes, the user can sign in with *neither* old nor new value until they verify the new one; with **username** attributes, the new value becomes active immediately.
- Setting `email_verified`/`phone_number_verified: true` via `AdminUpdateUserAttributes` bypasses the pending state.

## Admin-created users

`AdminCreateUser` — parameters that matter:
- **`TemporaryPassword`** — omit to auto-generate; the user lands in `FORCE_CHANGE_PASSWORD` and must change it at first sign-in. Temp passwords are valid up to **90 days** (`TemporaryPasswordValidityDays`).
- **`MessageAction`** — `SUPPRESS` (create silently, no invite) or `RESEND` (re-send the invite to an existing user).
- **`DesiredDeliveryMediums`** — `EMAIL` and/or `SMS`.
- **`ForceAliasCreation`** — steal an email/phone alias already held by another user.
- **Immutable custom attributes can only be set here** (not in the console, not later).

Special cases:
- **Passwordless users go straight to `CONFIRMED`** (no temp password), and you **can't resend confirmation codes** to them. They must have values for **all required attributes** at creation.
- **Missing required attributes + temp password:** the user gets a `NEW_PASSWORD_REQUIRED` challenge at first sign-in and supplies the missing values in `requiredAttributes` — only works if those attributes are **mutable** and **writable** by the app client.
- Setting a **permanent** password → `CONFIRMED`, no new-password/required-attribute prompt.

Node SDK v3 / boto3 examples: [backend.md](backend.md#admin--server-side-operations).

## Disabling self-service sign-up

Set `AdminCreateUserConfig.AllowAdminCreateUserOnly: true` (console: **Sign-up → Self-service sign-up → disable**). Then public `SignUp` returns `NotAuthorizedException` and managed login hides the **Sign up** link — only `AdminCreateUser`, import, or federation add users. **A pool open to self-signup lets anyone with your (public) app client id create an account** — set this deliberately.

## Find & manage users

**Search** with `ListUsers` (no cost; `AdminGetUser` *does* cost). Server-side `Filter` = `AttributeName Filter-Type "Value"` — `=` exact, `^=` prefix (`"family_name = \"Reddy\""`, `"phone_number ^= \"+1312\""`), **one attribute at a time**, case-insensitive. Searchable: `username`, `email`, `phone_number`, `name`, `given_name`, `family_name`, `preferred_username`, `cognito:user_status`, `status`, `sub`. **Custom attributes aren't searchable** (unindexed). For multi-attribute search use a client-side `--query`; pagination tokens expire after 1 hour and pages can be empty.

**Lifecycle ops** (`Admin*`, IAM-authorized; self-service `DeleteUser` uses an access token):
- `AdminDisableUser` — **invalidates all sessions and revokes access + refresh tokens**; sign-in returns `User is not enabled`. Re-enable with `AdminEnableUser` (attributes/password intact; already-revoked tokens stay dead). **Disable is required before `AdminDeleteUser`.**
- `AdminUpdateUserAttributes` (also marks email/phone verified), `AdminUserGlobalSignOut` (revoke all sessions without disabling).

## Passwords & account recovery

- **Policy** (`Policies.PasswordPolicy`): min length up to 99 (users may set up to 256), require upper/lower/number/special, non-leading/trailing spaces allowed. **Password history** (Essentials/Plus): block reuse of the current + up to **23** previous (24 total). Passwords are salted-hashed (unrecoverable) and **never expire** — log reset dates externally if you need aging.
- **Self-service reset:** `ForgotPassword` → code (valid **1 hour**, 5–20 attempts/hour) → `ConfirmForgotPassword`. Needs a **verified** email/phone. **Admin:** `AdminResetUserPassword` (sends a code, sets `RESET_REQUIRED`) or `AdminSetUserPassword` (set temp or `Permanent`).
- **`AccountRecoverySetting`** ranks delivery: `RecoveryMechanisms` of `verified_email`/`verified_phone_number` with `Priority` (1 = highest), or `admin_only` (disables self-service; can't combine). Default: phone first, then email.
- **MFA ⇄ recovery conflict (important):** a user's MFA channel can't also be their recovery channel — email MFA users can't recover by email; SMS MFA users can't recover by SMS. In an MFA pool, a user with only one contact attribute can get **locked out**. Fix: require **both** `email` and `phone_number` so Cognito sends recovery to the non-MFA channel. No valid method → `InvalidParameterException`.

## Importing users

Three approaches (mix them — e.g. **JIT for active users, CSV for the dormant tail**, to decommission the legacy directory sooner):

- **Just-in-time migrate-user trigger** — users keep their passwords; migrated on first sign-in / forgot-password. Requires the app client to allow **`USER_PASSWORD_AUTH`/`ADMIN_USER_PASSWORD_AUTH`** (SRP hides the password from your function); switch back to SRP after migrating. Full recipe: [lambda-triggers.md](lambda-triggers.md#migrate-user--import-from-a-legacy-directory-on-first-sign-in).
- **CSV bulk import** — no passwords (hashes unsupported); users land in **`RESET_REQUIRED`** (or `CONFIRMED` if a passwordless factor is available). Steps: `get-csv-header` → fill template → create a CloudWatch-Logs IAM role (trusts `cognito-idp.amazonaws.com`) → `create-user-import-job` (returns a presigned URL valid **15 min**) → upload CSV with header `x-amz-server-side-encryption:aws:kms` → `start-user-import-job`.
  - **Required columns:** `cognito:username` (unique, no spaces/tabs) and **at least one of `email_verified`/`phone_number_verified` = `TRUE`** (plus the matching `email`/`phone_number` and any required attributes). No auto-verified attribute set → the user is skipped; pool has none → the job won't start.
  - **Format:** no quotes around strings, escape literal commas with `\`, UTF-8 **no BOM**, `birthdate` = `mm/dd/yyyy`, `updated_at` = epoch seconds, `cognito:mfa_enabled` must match the pool's MFA setting.
  - **Limits:** 16,000 chars/row, **100 MB** file, **500,000** rows; **one import job active at a time**; job `Expired` if not started within 24–48 h. Imported users don't count as MAUs, but their password resets do. Results (per line number, no PII) go to CloudWatch Logs.
- **Backend-driven (dual-write) migration** — keep the legacy IdP as the front end and **silently provision each user in Cognito** from your backend: `AdminCreateUser` (`MessageAction: SUPPRESS`) + `AdminSetUserPassword` (`Permanent=true`) using the password you captured at the legacy sign-in, so users keep their password with no reset. Sync new signups/attribute changes both ways until you cut over. More control than JIT (no `USER_PASSWORD_AUTH` requirement), but you own the sync logic.

**Migration gotchas:** JIT/migrate-user **can't reproduce a legacy MFA** step (the Lambda can't run multi-round challenges) — re-enrol MFA post-migration. CSV-imported and migrate-user users both need a **verified** email/phone for reset codes.

## Detecting inactive users

**Cognito has no native last-sign-in attribute** — you must record activity yourself, then remediate on a schedule.

- **Capture sign-ins** with a **post-authentication Lambda trigger** ([lambda-triggers.md](lambda-triggers.md)): on each successful auth, write `{sub, username, userPoolId, timestamp}` to an external store (e.g. **DynamoDB**). Don't stuff last-login into a custom attribute — every update is a directory write (rate-limited, and attributes are for identity, not activity logs).
- **Remediate automatically** with a **DynamoDB TTL + Streams** pattern: set each record's TTL to `now + inactivity_threshold`; a fresh sign-in rewrites the record (pushing TTL out). When a record finally expires, DynamoDB Streams fires a Lambda that **`AdminDisableUser`**s the account (revokes tokens, keeps the profile; re-enable later with `AdminEnableUser`). Disable before any eventual `AdminDeleteUser`.
- **This is a background process, not real-time.** Admin ops are rate-limited (the `UserUpdate` category is ~25 RPS, [quotas.md](quotas.md#api-request-rate-quotas-rps)) — throttle the disabler and run it **per Region** to stay under the limit at scale.
- Alternatively, reconstruct activity from **CloudTrail** sign-in events ([monitoring.md](monitoring.md#cloudtrail)) if you didn't instrument a trigger up front.

## Groups

Collections of users for RBAC and IAM-role assignment. Create with `CreateGroup`; manage membership with `AdminAddUserToGroup` / `AdminRemoveUserFromGroup` / `ListUsersInGroup`. No extra cost.

- **Claims:** membership appears as **`cognito:groups`** in *both* ID and access tokens. The ID token also carries **`cognito:roles`** and **`cognito:preferred_role`** (from the group's IAM role).
- **Precedence:** a group's precedence is a non-negative number, **0 = highest**; the lowest value wins and its role becomes `cognito:preferred_role`. Ties → `cognito:preferred_role` is set only if both groups share the same role ARN, else it's omitted.
- **IAM role selection:** groups drive identity-pool role choice ([identity-pools.md](identity-pools.md#role-selection)); a client can override with `GetCredentialsForIdentity`'s `CustomRoleARN` (must be one of the user's available roles).
- **Authorization:** feed `cognito:groups` to an API Gateway Cognito authorizer, or to Verified Permissions ([verified-permissions.md](verified-permissions.md)).
- **Limitations:** groups **can't be nested**, you **can't search users within a group** (only list) or **search groups by name** (only list), and the max group count is a [service quota](quotas.md#resource-limits) (10,000/pool, 100/user).
- Cognito auto-creates a `<poolId>_<IdP>` group per external IdP ([federation.md](federation.md#behaviors-to-know)).
