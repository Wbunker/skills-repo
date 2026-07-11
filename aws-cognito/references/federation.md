# Federation (OIDC & shared concepts)

Sign users in through an external IdP; the user pool re-issues its own Cognito JWTs so your app speaks one token format. This file covers **OIDC** setup and the concepts **shared across all federation types** — attribute mapping, account linking, IdP routing, behaviors, gotchas. For **SAML 2.0** see [saml.md](saml.md). For consumer **social** login (Google/Apple/Facebook/Amazon) see [social-providers.md](social-providers.md).

## Table of Contents
1. [How user-pool federation works](#how-user-pool-federation-works)
2. [OIDC setup](#oidc-setup)
3. [Attribute mapping](#attribute-mapping)
4. [Account linking](#account-linking)
5. [IdP routing (identifiers)](#idp-routing-identifiers)
6. [Adding an external IdP (console flow)](#adding-an-external-idp-console-flow)
7. [Behaviors to know](#behaviors-to-know)
8. [Gotchas](#gotchas)

---

## How user-pool federation works

A user pool acts as a **service provider / relying party** to the external IdP and re-issues its **own** Cognito JWTs to your app. Your app only ever speaks OIDC to Cognito — Cognito absorbs the SAML/OIDC differences. Federated users get a profile in the pool like local users, but the external IdP remains authoritative for authentication.

Federation **requires a domain and managed login** (redirect flow) — you cannot federate through the AWS-SDK auth API. All external callbacks land on fixed Cognito endpoints:

| Protocol | Cognito endpoint the IdP posts to |
|---|---|
| OIDC / social | `https://<domain>/oauth2/idpresponse` |
| SAML 2.0 (ACS) | `https://<domain>/saml2/idpresponse` (POST binding) — see [saml.md](saml.md) |
| SAML 2.0 sign-out | `https://<domain>/saml2/logout` (POST binding) — see [saml.md](saml.md) |

## OIDC setup

For a generic OIDC IdP (any standards-compliant provider):

```bash
aws cognito-idp create-identity-provider \
  --user-pool-id "$POOL_ID" \
  --provider-name MyOIDC \
  --provider-type OIDC \
  --provider-details '{
    "client_id": "…",
    "client_secret": "…",
    "oidc_issuer": "https://auth.example.com",
    "authorize_scopes": "openid email profile",
    "attributes_request_method": "GET"
  }' \
  --attribute-mapping email=email,name=name
```

Cognito discovers endpoints from `<oidc_issuer>/.well-known/openid-configuration` (or set them manually). The IdP's redirect URI is `https://<domain>/oauth2/idpresponse`. Constraints:
- `oidc_issuer` must start with `https://` and **not** end in `/` (e.g. `https://login.salesforce.com`).
- Discovery/auth/token/userInfo/jwks URLs must be **HTTPS on standard ports 80 or 443 only** — a non-standard port makes logins fail.
- `attributes_request_method` is the HTTP verb (`GET`/`POST`) Cognito uses against the IdP's `userInfo` endpoint.
- The OIDC `sub` claim maps to the pool `username` by default; map `email` etc. explicitly.

**Your OIDC IdP must** (else sign-in fails): support **`client_secret_post`** client auth (Cognito does *not* support `client_secret_basic`, and doesn't check `token_endpoint_auth_methods_supported`); sign ID tokens with **RSA, HMAC-SHA, or ECDSA**; publish a `kid` at `jwks_uri` and include `kid` in tokens; present a non-expired key with a valid root-CA chain. `openid` scope is required; `email`→`email`/`email_verified`, `profile`→all attributes, `phone`→phone claims.

**IdP requires `private_key_jwt`?** Cognito can't do asymmetric client-assertion auth (RFC 7521/7523) natively. Point the OIDC provider's **token** endpoint (only) at an **API Gateway + Lambda** proxy that mints a signed `client_assertion` (`client_assertion_type=urn:ietf:params:oauth:client-assertion-type:jwt-bearer`; JWT with `iss`=`sub`=client_id, `aud`=IdP token URL, `exp` ≈ now+300s, **RS256**, `kid` header; private key in **Secrets Manager**) and forwards to the real IdP. Leave the authorize/userInfo/jwks endpoints pointing at the IdP directly — only the token call needs the proxy.

**How Cognito processes an OIDC sign-in** (authorization-code flow, run by the pool — your app never sees the IdP's tokens):
1. Exchanges the IdP's code for the IdP's **ID + access tokens** at the IdP token endpoint.
2. **Validates the ID token**: signing alg in {RSA, HMAC, EC}; `kid` present at `jwks_uri` (refreshed per token); `iss` = configured issuer; `aud` = (or contains) the configured client ID; `exp` not past.
3. Calls the IdP **`userInfo`** endpoint with the IdP access token to fetch attributes. **Cognito does not independently validate the IdP access token** — it relies on `userInfo` rejecting an invalid one.
4. Maps ID-token + `userInfo` claims to the profile per your rules (unmapped non-required claims are ignored), then issues its **own** Cognito JWTs.

**Best practice:** request only the scopes whose attributes you map — `openid profile` returns everything, `openid email phone` narrows to those. The scopes you request *from the IdP* can differ from those your app client authorizes.

## Attribute mapping

Applies to **all** IdP types (SAML/OIDC/social). Maps IdP claims → user-pool attributes (`--attribute-mapping upAttr=idpClaim`). Each IdP has its own mapping schema; source claim names vary by vendor (`email` vs `emailaddress` vs the URL-formatted SAML name). Rules that trip people up:

- **Map every required pool attribute**, or user creation fails on first federated sign-in (e.g. `email` is usually required).
- **Mapped emails are UNVERIFIED by default** — you can't verify a federated email with an OTP. Map the IdP's `email_verified` claim (Google/most OIDC send it) to carry verification status; don't trust email for authorization otherwise.
- **Mutable vs. writable — two different failure modes.** A mapped attribute must be **mutable** in the schema *and* in the app client's `WriteAttributes`. If it's **immutable**, a value from the IdP makes **sign-in fail**. If it's not **writable**, Cognito silently skips it and continues. Custom attributes you map must be mutable.
- **2,048-char value limit.** A mapped value longer than 2048 chars fails sign-in. You can pass an IdP token through by mapping `access_token`/`id_token` to a writable custom attribute (≤2048 chars) — useful for calling the IdP's APIs downstream.
- **Multi-value claims are flattened** to `[v1,v2,v3]` (comma-delimited, bracketed, URL-form-encoded except `.-*_`) — decode/parse in your app.
- **Values aren't removed when the source stops appearing.** Cognito only overwrites on change; a claim that disappears from the token leaves the old value in place. To clear it, the IdP must send a blank value, or delete it with `(Admin)DeleteUserAttributes`, or drop it in a pre-authentication trigger so it repopulates.
- **Case-insensitive pools lowercase the username source** in generated federated usernames (`MySAML_testuser@example.com`); account for this in Lambda triggers. Linking across pools of differing case-sensitivity requires a new pool.
- Mappings update on every sign-in and token refresh; users only pick up new/added scopes after re-authenticating.

For logic beyond static `upAttr=idpClaim` rules (conditional mapping, IdP-group→Cognito-group, truncating oversized claims), use the **inbound federation Lambda trigger** — it receives the raw IdP `attributes` and returns `userAttributesToMap`. See [lambda-triggers.md](lambda-triggers.md#recipes).

**RBAC from federated groups (common recipe):** map the IdP's multi-value group claim → a **`custom:groups`** string attribute, then a **pre-token-generation trigger** parses it and emits the standard **`cognito:groups`** claim (an array) into the token — so your app authorizes on `cognito:groups` exactly as for local users, **without creating or managing any real Cognito groups**. Keep `custom:groups` **read-only to the app client** (prevent self-elevation) and **filter to app-relevant groups** (the 2,048-char attribute limit truncates large enterprise group lists). See [lambda-triggers.md](lambda-triggers.md#pre-token-generation--add-a-custom-claim--group--scope).

## Account linking

Two sign-ins for the same person (e.g. local `jane@x.com` and a SAML `jane@x.com`) are **separate profiles** — a **linked user** merges them so they share one profile. Link with `AdminLinkProviderForUser` **before** the federated user's first sign-in (a pre-staging job or a pre sign-up Lambda trigger); if they've already signed in, delete the auto-created `<Provider>_<id>` profile first.

```python
client.admin_link_provider_for_user(
    UserPoolId=POOL_ID,
    # Destination = the local user to merge INTO (ProviderName "Cognito"):
    DestinationUser={"ProviderName": "Cognito", "ProviderAttributeValue": local_username},
    # Source = the federated identity:
    SourceUser={"ProviderName": "MyOrgSAML",
                "ProviderAttributeName": "email",         # SAML/OIDC: a specific claim
                "ProviderAttributeValue": "jane@x.com"},
)
```

- **`ProviderAttributeName` differs by IdP type:** for **social** IdPs it must be `Cognito_Subject` (link on the provider's unique subject id). For **SAML/OIDC** you can link on a specific claim like `email`.
- **Limits:** up to **5 federated identities per profile**; across a pool you can link on at most **5 distinct source attribute names**.
- The merged profile's ID token carries all providers in the **`identities`** claim (objects with `userId`, `providerName`, `providerType`, `issuer`, `primary`, `dateCreated`).
- **Attribute priority on sign-in:** ID-token claims over `userInfo`.
- **Unlink** a stale identity with `AdminDisableProviderForUser` (same provider/attr params).
- A federated profile has status **`EXTERNAL_PROVIDER`**; setting a password (`AdminSetUserPassword`) flips it to `CONFIRMED` and lets it sign in as a local user — **avoid this**; keep federated users password-less and linked.
- **Only link on a verified, trusted attribute** — auto-linking on an unverified email is an account-takeover vector. Billing: a profile plus any number of linked identities counts as **one MAU**.

## IdP routing (identifiers)

Set **identifiers** (up to **50** per IdP, unique within the pool) so managed login routes users automatically: a user typing `@example.com` is sent to the matching IdP. One IdP can hold several identifiers (an org with multiple domains). Configure with `--idp-identifiers`.

Two redirect params on `/oauth2/authorize` (both skip the IdP-picker and go straight to the provider):
- `idp_identifier=example.com` — routes by a friendly identifier (e.g. email domain).
- `identity_provider=MyOrgSAML` — routes by the exact provider **name**.

**Managed-login display logic depends on identifiers:**
- Identifiers on **every** IdP for the app client → managed login shows an **email-domain input** (no IdP buttons), derives the domain, and redirects to the matching IdP. In managed login (not classic hosted UI) you must also enable this in the branding editor: **Authentication behavior → Provider display → Domain search input**.
- Identifiers on **none** (or only some) → managed login shows a **button per assigned IdP**.
- Want both domain-search *and* buttons? Add one IdP with **no** identifier, or a separate app client. **Gotcha:** deleting and re-adding an IdP without an identifier makes federated users create **new profiles** (possible billing impact that month).

Send users directly to an IdP with either param, e.g. `/oauth2/authorize?identity_provider=MyOrgSAML&response_type=code&client_id=…&redirect_uri=…` ([managed-login.md](managed-login.md#federated-sign-in)).

## Adding an external IdP (console flow)

1. User pool → **Social and external providers** → **Add an identity provider**.
2. Pick **SAML**, **OpenID Connect**, or a social provider.
3. Supply metadata (SAML) / issuer + client creds (OIDC) / app id + secret (social).
4. Enter **Authorized scopes** and **map attributes** (include required attrs).
5. Create — then go to **App clients** → your client → edit login/hosted-UI settings and **add the IdP under Identity providers** (a new IdP is not usable until enabled on the app client) and confirm callback URLs.

## Behaviors to know

Non-obvious things Cognito does with federated users:
- **Auto-created IdP group.** Cognito creates a user pool group per IdP named `<poolId>_<IdPname>` (e.g. `us-east-1_EXAMPLE_Google`) and adds each federated user to it automatically. Linked users are *not* auto-added — add them yourself if needed.
- **The `identities` claim/attribute** records the provider + the user's unique ID at that provider. It appears in the ID token and can't be edited directly; it's what account-linking keys on.
- **Federated username format** is `<IdPname>_<id>` (e.g. `Google_1234…`, `MyIDP_bob@example.com`). To present a clean username, map the IdP claim to **`preferred_username`**.
- **Attribute values refresh on every sign-in** — a mapped attribute updates in the pool whenever it changes at the IdP; users pick up newly-added scopes only after re-authenticating.
- **Federated users sign in only via the Login/Authorize endpoints**, never `InitiateAuth`/`AdminInitiateAuth`. The `/oauth2/authorize` endpoint is a *redirect* — add `identity_provider`/`idp_identifier` to skip managed login and go straight to the IdP.
- **IdP config changes take up to ~1 minute** to appear in managed login. Cognito follows up to **20 HTTP redirects** between itself and an IdP, and tags its redirect requests with a `User-Agent: Amazon/Cognito` header.

## Gotchas

- **The IdP must be enabled on the app client**, not just created on the pool — the #1 "my provider doesn't show up" cause.
- **Federation needs managed login** — no SDK-based federated sign-in.
- **`redirect_uri` must exactly match** an app-client callback URL.
- **Required-but-unmapped attributes** break first sign-in — map them all.
- SAML-specific gotchas (metadata URL, SP URN, NameID) are in [saml.md](saml.md).
