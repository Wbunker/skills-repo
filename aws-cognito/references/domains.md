# User Pool Domains

A domain turns on managed login + the OAuth/OIDC endpoints ([managed-login.md](managed-login.md)). Two kinds: an AWS-hosted **prefix** domain (instant, free) or a **custom** domain you own (trust, but ACM + CloudFront + DNS overhead). No cost difference between them.

## Table of Contents
1. [Prefix domain](#prefix-domain)
2. [Custom domain](#custom-domain)
3. [Discovery endpoints live elsewhere](#discovery-endpoints-live-elsewhere)
4. [Running both domains](#running-both-domains)
5. [Domain hierarchy & cookie trap](#domain-hierarchy--cookie-trap)
6. [Propagation & change timing](#propagation--change-timing)

---

## Prefix domain

```bash
aws cognito-idp create-user-pool-domain \
  --user-pool-id "$POOL_ID" --domain myapp-auth --managed-login-version 2
# → https://myapp-auth.auth.<region>.amazoncognito.com
```
Format: `<prefix>.auth.<region>.amazoncognito.com`. Manage with `describe-user-pool-domain` / `delete-user-pool-domain`.

- **Reserved words:** the prefix can't contain `aws`, `amazon`, or `cognito`. Must be globally unique.
- Parent domains (`auth.<region>.amazoncognito.com`, `auth-fips.<region>.amazoncognito.com`) are on the **Public Suffix List** — this is why they're safe cookie boundaries.
- `--managed-login-version 2` = managed login; `1` = classic hosted UI. Branding version applies to **all** app clients on the domain.

## Custom domain

E.g. `auth.example.com`. Prerequisites (all required):

- **Must be a subdomain, not a root/TLD.** Recommended `auth.example.com`. Cognito refuses TLDs to avoid hijacking production domains.
- **The parent domain must have a valid DNS `A` record** (any value; an SOA record is *not* sufficient). Cognito verifies this to prevent accidental domain takeover — e.g. for `auth.xyz.example.com`, `xyz.example.com` must resolve.
- **ACM certificate in us-east-1** regardless of the pool's Region (it backs a CloudFront distribution, a global service). You may need a cert for the subdomain unless you hold a wildcard cert.
- Browser clients must support **SNI**.
- IAM permission **`cloudfront:UpdateDistribution`** (Cognito creates an AWS-managed CloudFront distribution; you can't change its config, including TLS policy).
- **Don't set your app's own cookies on the auth subdomain** — Cognito sets several (`cognito`, `cognito-fl`, `XSRF-TOKEN`, …) that can grow; an ALB/proxy header-size limit plus your cookies can overflow.

```bash
aws cognito-idp create-user-pool-domain \
  --user-pool-id "$POOL_ID" --domain auth.example.com --managed-login-version 2 \
  --custom-domain-config CertificateArn=arn:aws:acm:us-east-1:111122223333:certificate/EXAMPLE
```

Then Cognito returns an **alias target** (a `*.cloudfront.net` name). Point DNS at it:
- **Record for the custom domain** (`auth`): type `A`, Alias **enabled**, target = the CloudFront alias target, simple routing.
- **Record for the parent** (`example.com`): type `A`, Alias disabled, any value — this is the verification record Cognito checks.
- Route 53 makes this a few clicks; any DNS provider works. Public hosted zone only (private not supported).

**Changing the cert:** ACM *renewal* keeps the same ARN → picked up automatically. *Replacing* the cert yields a new ARN → provide it via `UpdateUserPoolDomain`; up to **1 hour** to distribute.

## Discovery endpoints live elsewhere

`/.well-known/openid-configuration` and `/.well-known/jwks.json` are **not** on your prefix/custom domain — they're at the API host:
```
https://cognito-idp.<region>.amazonaws.com/<poolId>/.well-known/openid-configuration
https://cognito-idp.<region>.amazonaws.com/<poolId>/.well-known/jwks.json
```
Point OIDC auto-discovery at the first URL.

## Running both domains

You can have a custom **and** a prefix domain on one pool. But because discovery is served per-domain, **discovery/jwks resolve only to the custom domain** — the prefix domain then lacks discovery/token-signing endpoints, so use it only for flows that don't need them.

**Passkey relying-party ID:** with both domains, the RP ID can be set only to the **custom** domain (or add the prefix FQDN as a "Third-party domain"). Custom domains are the preferred passkey RP.

## Domain hierarchy & cookie trap

The managed-login session cookie is valid for a custom domain **and all its subdomains** (`*.auth.example.com`). So **don't put custom domains at different levels of the same hierarchy.** If pool A uses `auth.example.com` and pool B uses `uk.auth.example.com`, a user who signed in at A carries a cookie into B's wildcard path and gets an **error instead of a sign-in prompt**. Keep custom domains at the **same subdomain level** (`auth.example.com`, `auth2.example.com` — fine).

## Propagation & change timing

- New **prefix** domain / branding change on prefix: up to **60 s**.
- New/changed **custom** domain: up to **5 min**; a brand-new custom domain up to **1 hour**.
- Changing branding version: up to **4 min**.
- **Switching between managed login and hosted UI branding does not preserve sessions** — everyone must sign in again.
- Deleting a domain removes managed login + all OAuth endpoints for every app client.
