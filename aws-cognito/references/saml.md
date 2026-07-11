# SAML 2.0 Federation

Enterprise sign-in through a SAML 2.0 IdP (Entra ID/ADFS, Okta, Ping, Shibboleth, …). This file is SAML-specific; the concepts shared with OIDC/social — **attribute mapping, account linking, IdP routing, the console flow, and general federation behavior** — live in [federation.md](federation.md). SAML requires a **domain + managed login** (redirect flow); you can't federate via the AWS-SDK auth API.

## Table of Contents
1. [Setup](#setup)
2. [Things to know](#things-to-know)
3. [Third-party SAML providers](#third-party-saml-providers)
4. [SAML gotchas](#saml-gotchas)

---

## Setup

Two sides must be configured: **your IdP** (add Cognito as a relying party) and **your user pool** (add the IdP).

**Give your IdP these values:**
- **ACS URL** (assertion consumer service, POST binding): `https://<domain>/saml2/idpresponse`
- **SP entity ID / audience URI / SP URN** (some IdPs require it): `urn:amazon:cognito:sp:<userPoolId>`
- **Sign-out URL** (if enabling SLO): `https://<domain>/saml2/logout`
- Required claims: at minimum the pool's required attributes (usually `email`).

**Configure the IdP in the pool** — provide a **metadata document**, prefer a URL over an upload so Cognito auto-refreshes it (~every 6 hours or before expiry):

```bash
aws cognito-idp create-identity-provider \
  --user-pool-id "$POOL_ID" \
  --provider-name MyOrgSAML \
  --provider-type SAML \
  --provider-details '{
    "MetadataURL": "https://idp.example.com/app/metadata",
    "IDPSignout": "true",
    "RequestSigningAlgorithm": "rsa-sha256",
    "EncryptedResponses": "true",
    "IDPInit": "false"
  }' \
  --attribute-mapping email=http://schemas.xmlsoap.org/ws/2005/05/identity/claims/emailaddress
```

`ProviderDetails` fields: `MetadataURL` **or** `MetadataFile` (the raw XML — escape any `"` as `\"`), `IDPSignout` (send signed SLO requests), `RequestSigningAlgorithm` (sign SSO requests, `rsa-sha256`), `EncryptedResponses` (require encrypted assertions), `IDPInit` (allow IdP-initiated sign-in).

- Use `MetadataFile` instead of `MetadataURL` if the IdP has no public metadata endpoint. Metadata URL must be on **standard ports 80/443** with a valid SSL cert (console accepts `https://` only); a bad cert yields `InvalidParameterException: Error retrieving metadata`.
- Cognito supports **only POST binding** and receives the assertion via the browser — your app never parses SAML.
- Manage the IdP lifecycle with `update-identity-provider` (swap metadata/mapping), `describe-identity-provider`, `list-identity-providers`, `delete-identity-provider`.
- Map every **required** pool attribute (usually `email`); see [federation.md#attribute-mapping](federation.md#attribute-mapping).

## Things to know

The high-value, non-obvious SAML rules:

- **`NameID` must be persistent and is case-sensitive.** Cognito keys a SAML user's profile on `NameID`. **Any change to the value — including letter case — creates a new user profile.** Never map `NameID` to a mutable attribute like `email`; use a stable identifier and ideally `Format="urn:oasis:names:tc:SAML:1.1:nameid-format:persistent"`. If a user is locked out after their `NameID` changed, delete the stale profile — Cognito recreates it on next sign-in.
- **SP-initiated vs IdP-initiated.** Default to **SP-initiated only** (`IDPInit: false`) — it's the secure default (Cognito sets state params that guard against CSRF and validate the response against its request). Only enable IdP-initiated (`IDPInit: true`) if you've prepared for unsolicited sign-ins (spoofing/CSRF risk). Assertion differences: SP-initiated must carry `InResponseTo` = the original request ID; **IdP-initiated must NOT contain `InResponseTo`** and must be **issued within the last 6 minutes**.
- **An app client with IdP-initiated SAML can host *only* SAML IdPs** — you can't also add the local user directory or any non-SAML IdP to that client.
- **Submitting an IdP-initiated assertion:** POST it to `/saml2/idpresponse` as a `SAMLResponse` form field (Base64-encoded assertion, **≤ 100,000 chars**), with the app-client/scope/redirect details URL-encoded into a `RelayState` field (`identity_provider=…&client_id=…&redirect_uri=…&response_type=code&scope=…`). Cognito replies `302` with the authorization code. (SP-initiated instead uses `GET /oauth2/authorize` query params.)
- **Request signing & response encryption.** Every SAML-configured pool generates a signing key pair + **signing certificate**; give it to your IdP so it trusts signed requests. SLO requests are **always signed**; SSO signing is opt-in via `RequestSigningAlgorithm`. For encryption, Cognito generates a per-IdP **encryption certificate**; once you enable `EncryptedResponses`, the IdP must encrypt **all** responses (the connection is non-functional until it does). You **can't** use external keys — only Cognito-generated ones. Download certs from the IdP's console page, or read `ActiveEncryptionCertificate` from `DescribeIdentityProvider`.
- **Cognito certificate lifecycle:** user-pool certs are valid **10 years**, but Cognito generates fresh signing + encryption certs **once a year**. The public key is unchanged across certs and old certs stay valid for their full life — but **update the cert in your IdP config annually** as a best practice.
- **Single logout (SLO).** With `IDPSignout` on, hitting your app's `/logout` makes Cognito send a signed `SAMLRequest` (`SigAlg=…rsa-sha256`, `Signature=…`) to the IdP's `SingleLogoutService` URL from metadata; the IdP returns a `LogoutResponse` via **POST** to `/saml2/logout`, then Cognito redirects to the original destination. **Gotcha:** if the `LogoutResponse` has multiple `AuthnStatement`s, the **first** one's `sessionIndex` must match the sign-in's `sessionIndex`, or the user isn't signed out.
- **Multiple signing certs are allowed** (an assertion is valid if it matches *any* cert in metadata); each cert ≤ 4096 chars. **Cert rotation:** publish both old and new certs in metadata for **≥ 6 hours** (Cognito caches metadata up to 6h) before removing the old one.
- **Required assertion elements:** `NameID`; an `AudienceRestriction` whose `Audience` = `urn:amazon:cognito:sp:<poolId>`; `Recipient` = your `saml2/idpresponse` endpoint.
- **No replayed assertions** — a duplicate assertion ID is rejected.
- **`relayState`** is an opaque session reference; Cognito accepts values > 80 bytes (violating the SAML spec letter, matching industry practice) — never parse it.
- **4-byte UTF-8 characters (emoji) in attribute values are rejected** — base64-encode them and decode in your app.
- Logout responses to `/saml2/logout` must use **POST binding** (no GET).

## Third-party SAML providers

Cognito only needs the IdP's **metadata document** — retrieve it (static file or active URL) and do the rest of the config in the user pool. Give the provider your **ACS URL** (`/saml2/idpresponse`) and **SP entity ID** (`urn:amazon:cognito:sp:<poolId>`); to sign requests, configure the IdP to trust your signing cert; to encrypt, configure it to encrypt all responses.

| Provider | Metadata source |
|---|---|
| Microsoft Entra ID (Azure AD) / ADFS | Enterprise app → Federation Metadata (supports token encryption) |¹
| Okta | App integration → download IdP metadata XML + signing cert |
| Auth0 | Configure Auth0 as SAML IdP |
| Ping Identity (PingFederate) | Export SAML metadata |
| JumpCloud / SecureAuth / Shibboleth | provider's SAML config docs |

¹ **Entra ID specifics:** register Cognito as a **Non-gallery** enterprise app; Reply URL (ACS) = `https://<domain>/saml2/idpresponse`, Identifier (Entity ID) = `urn:amazon:cognito:sp:<poolId>`. Claim URIs to map: **email** = `http://schemas.xmlsoap.org/ws/2005/05/identity/claims/emailaddress`, **groups** = `http://schemas.microsoft.com/ws/2008/06/identity/claims/groups`. To receive groups, first create a **custom attribute** in the pool and map the groups claim to it (Entra's SAML groups claim releases when you set **Groups assigned to the application** with Source attribute **Group ID**). Then translate that attribute into Cognito groups/claims with the [inbound-federation trigger](lambda-triggers.md#inbound-federation--transform-idp-claims-programmatically) — enterprise group lists routinely exceed the 2048-char attribute limit.

## SAML gotchas

- Enterprise SAML often needs the **SP URN** `urn:amazon:cognito:sp:<userPoolId>` even though Cognito derives the ACS URL from the domain.
- Prefer a **metadata URL** (auto-refresh) over an uploaded file (goes stale, causing signature failures when the IdP rotates certs).
- The **IdP must be enabled on the app client**, not just created on the pool — the #1 "my provider doesn't show up" cause.
- Route users to the right SAML IdP with **identifiers** (email domains) — see [federation.md#idp-routing-identifiers](federation.md#idp-routing-identifiers).
