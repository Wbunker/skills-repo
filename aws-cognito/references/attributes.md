# User Attributes & Sign-in Aliases

Standard/custom attributes, the alias-vs-username-attributes decision, and per-app-client attribute permissions. Attribute *mapping from IdPs* is in [federation.md](federation.md#attribute-mapping).

## Table of Contents
1. [Standard attributes](#standard-attributes)
2. [Custom & developer attributes](#custom--developer-attributes)
3. [Aliases vs. username attributes](#aliases-vs-username-attributes)
4. [Case sensitivity](#case-sensitivity)
5. [Attribute permissions (per app client)](#attribute-permissions-per-app-client)

---

## Standard attributes

The OIDC standard set: `name`, `given_name`, `family_name`, `middle_name`, `nickname`, `preferred_username`, `profile`, `picture`, `website`, `gender`, `birthdate`, `zoneinfo`, `locale`, `updated_at`, `address`, `email`, `phone_number`, `sub`.

- **Only `email` and `phone_number` can be verified.** `sub` is the pool-unique, **immutable** user id — index/reference users by `sub`, never by a mutable/sign-in attribute.
- Default max length is **2048 chars**. Format rules: `birthdate` = `YYYY-MM-DD`; `phone_number` = `+` then country code then digits only (`+12065551212`).
- **Required attributes are set only at pool creation and can't be toggled later.** A required attribute blocks self-sign-up without a value — but `AdminCreateUser` can omit them (user supplies them at first sign-in via `NEW_PASSWORD_REQUIRED`). Admins can mark `email`/`phone_number` verified via `AdminUpdateUserAttributes` (`email_verified`/`phone_number_verified` = true).

## Custom & developer attributes

- **Up to 50 custom attributes.** Referenced with the **`custom:`** prefix in tokens/rules. String / number / boolean / `DateTime` (the **console only offers string & number** — boolean/DateTime need the `SchemaAttributes` API). Written to the ID token **as strings**.
- **You can't require, delete, or rename a custom attribute** — only add. Set min/max length (≤2048).
- **Mutable vs. immutable:** an **immutable** custom attribute can be set **once, at user creation** (`SignUp` / `AdminCreateUser` / first federated sign-in with a mapping — but mapping to an immutable attr breaks *later* federated sign-ins). Mutable attrs need app-client write permission to change.
- **`dev:` (developer) attributes** are a legacy feature (modifiable only with AWS credentials), superseded by app-client read/write permissions — prefer custom attributes + permissions.

## Aliases vs. username attributes

How users sign in — **fixed at pool creation, unchangeable after**. `username` is always a distinct, immutable attribute (auto-generated for federated users; a UUID = `sub` when you use username attributes).

| | **Alias attributes** | **Username attributes** |
|---|---|---|
| Setup | Select **Username** + email/phone/preferred_username | Select email and/or phone, **not** Username |
| Sign in with | username **or** any alias | the email/phone *is* the username |
| Multiple sign-in identifiers | Yes | No (email or phone) |
| Must verify before alias works | Yes | n/a |
| Avoids `UsernameExistsException` on dup email/phone at sign-up | Yes | No |

- **Alias values must be verified to be usable, and unique.** At sign-up a duplicate alias succeeds, but `ConfirmSignUp` throws **`AliasExistsException`** — call `ConfirmSignUp` with **`forceAliasCreation: true`** to move the alias to the new account (marking it unverified on the old one). Auto-verify aliases.
- **`preferred_username` can be an alias OR required, not both.** As an alias it's set only at confirmation (via `UpdateUserAttributes`), letting users change their sign-in name while `username` stays fixed. **The console can't set a `preferred_username` alias** — use the `AliasAttributes` API.
- **Username attributes:** `SignUp` auto-populates `email`/`phone_number` from the `Username` if it's in that format; a non-matching format throws. You can use email/phone in place of the username in every API **except `ListUsers`** (there, filter by `email`/`phone_number`, or pass the UUID for a `username` filter).
- **Case-insensitive pools** accept either case for aliases.

## Case sensitivity

Whether `Username` is fixed at pool creation (like aliases) — `UsernameConfiguration.CaseSensitive`:

- **The API/CLI default is `true` (case-*sensitive*); the console always creates case-*insensitive* pools.** So a `CreateUserPool` without `CaseSensitive: false` behaves differently from a console pool. (Before 2020-02-12 everything defaulted case-sensitive.)
- Case-insensitive means `User@x.com` == `user@x.com` for `username`, `email`, **and** `preferred_username` — and it **flattens outputs to lowercase**: `userInfo`, `GetUser`, and **Lambda trigger input events** all receive the lowercased value. Don't rely on stored casing.
- **You can't switch a pool's case sensitivity** — migrate users to a new pool with a [migrate-user trigger](lambda-triggers.md#migrate-user--import-from-a-legacy-directory-on-first-sign-in) that resolves case collisions (two rows unique when case-sensitive can collide when insensitive).
- **Federated `NameID`/`sub` is always case-sensitive** regardless of this setting — a case change in a SAML/OIDC identifier creates a *new* user ([saml.md](saml.md#things-to-know)).
- As always, key users on immutable **`sub`**, never a case-variable sign-in attribute.

## Attribute permissions (per app client)

Each app client has **read** and **write** attribute lists (standard + custom). Defaults: a new client can read/write **all** attributes; new custom attributes are **unavailable until you grant permissions**.

- **Readable attributes** appear in the ID token and `GetUser` responses — unreadable ones don't. Writing an unauthorized attribute → `NotAuthorizedException`.
- **All app clients can always write required attributes** (the console sets required attrs writable automatically).
- **You can't grant an app client write access to `email_verified` / `phone_number_verified`.** Only a pool **admin** (`AdminUpdateUserAttributes`) or the user completing [attribute verification](user-management.md#verifying-a-second-contact-method) can change them.
- **Immutable custom attributes are writable only at create/sign-up.** Grant write permission and the client can set them during `SignUp`/`AdminCreateUser`; after that they're locked for that user.
- Grant the **minimum** attributes an app needs (security best practice); permissions are changeable after creation.
- Shortcut: the **`oidc:profile`** scope in `ReadAttributes`/`WriteAttributes` covers the OIDC profile-scope attributes (everything except `email`, `phone_number`, `sub`, `address`).
