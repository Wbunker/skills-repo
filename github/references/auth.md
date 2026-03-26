# GitHub Authentication Reference

## Table of Contents
1. [Authentication Methods Overview](#authentication-methods-overview)
2. [Personal Access Tokens (PATs)](#personal-access-tokens-pats)
3. [GitHub Apps](#github-apps)
4. [OAuth Apps](#oauth-apps)
5. [GITHUB_TOKEN (Actions)](#github_token-actions)
6. [Required Headers](#required-headers)
7. [SAML SSO Organizations](#saml-sso-organizations)
8. [Choosing the Right Method](#choosing-the-right-method)

---

## Authentication Methods Overview

| Method | Auth Header Value | Expiry | Scoped to repos? | Best for |
|---|---|---|---|---|
| Fine-grained PAT | `Bearer <token>` | 1–366 days or never | Yes (specific repos) | Personal automation, CI bots |
| Classic PAT | `Bearer <token>` | Optional | No (all accessible repos) | Legacy integrations |
| GitHub App installation token | `Bearer <token>` | 1 hour | Yes (up to 500 repos) | Production org integrations |
| GitHub App JWT | `Bearer <jwt>` | 10 minutes | App-level only | Generating installation tokens |
| OAuth App token | `Bearer <token>` | Until revoked | No | User-facing web apps |
| `GITHUB_TOKEN` | `Bearer ${{ secrets.GITHUB_TOKEN }}` | Job duration | Current repo only | GitHub Actions |
| HTTP Basic (app credentials) | `Basic base64(id:secret)` | n/a | n/a | GitHub App/OAuth App endpoints only |

All modern tokens use `Bearer`. The legacy `token` prefix also works for PATs and OAuth tokens but `Bearer` is preferred.

---

## Personal Access Tokens (PATs)

### Fine-Grained PATs (Recommended)

Created at **Settings → Developer settings → Personal access tokens → Fine-grained tokens**.

**Key properties:**
- Scoped to a single user account or one organization (org must allow fine-grained PATs)
- Can restrict to specific repositories (or all repos you own)
- Per-permission granularity: each permission category set independently to `read`, `write`, or `none`
- Max 50 tokens per user
- Expiry: 1–366 days, or no expiration (subject to org policy)
- Organization admin approval may be required before the token can access org resources

**Permission categories (selection):**

| Category | What it controls |
|---|---|
| Actions | Workflows, runs, artifacts, secrets |
| Administration | Repo admin settings, teams |
| Checks | Check runs and suites |
| Code scanning alerts | SAST alerts |
| Codespaces | Codespace management |
| Commit statuses | Status checks |
| Contents | Files, commits, releases (core repo data) |
| Dependabot alerts | Dependency vulnerability alerts |
| Deployments | Deployment records |
| Environments | Protected environment settings |
| Issues | Issues and comments |
| Metadata | Repo metadata (always read-only, always granted) |
| Packages | GitHub Packages |
| Pull requests | PRs, reviews, comments |
| Secrets | Repository secrets |
| Variables | Actions variables |
| Webhooks | Repository webhooks |
| Workflows | Workflow files (distinct from running them) |

**Usage:**
```http
GET /repos/owner/repo/issues
Authorization: Bearer github_pat_11AAAA...
Accept: application/vnd.github+json
X-GitHub-Api-Version: 2022-11-28
```

### Classic PATs

Created at **Settings → Developer settings → Personal access tokens → Tokens (classic)**.

**Scopes (most common):**

| Scope | Access granted |
|---|---|
| `repo` | Full control of private repos (includes sub-scopes below) |
| `repo:status` | Commit status access |
| `repo_deployment` | Deployment status |
| `public_repo` | Public repos only |
| `repo:invite` | Repo invitations |
| `security_events` | Security alerts |
| `workflow` | Update GitHub Actions workflow files |
| `write:packages` | Upload packages |
| `read:packages` | Download packages |
| `delete:packages` | Delete packages |
| `admin:org` | Full org management |
| `read:org` | Read org membership |
| `admin:public_key` | Manage public SSH keys |
| `admin:repo_hook` | Manage repo webhooks |
| `admin:org_hook` | Manage org webhooks |
| `gist` | Create gists |
| `notifications` | Read notifications |
| `user` | Full user profile read/write |
| `read:user` | Read user profile |
| `user:email` | Read user email addresses |
| `user:follow` | Follow/unfollow users |
| `delete_repo` | Delete repos |
| `write:discussion` | Manage team discussions |
| `admin:gpg_key` | Manage GPG keys |
| `admin:ssh_signing_key` | Manage SSH signing keys |

**Classic PATs have access to all repos** the owner can access, within any org they're a member of — you cannot restrict them to specific repos.

---

## GitHub Apps

GitHub Apps are the recommended integration type for org-level automation. They act as their own identity (not a user) and get higher rate limits.

### Concepts

- **GitHub App** — The app registration, owned by a user or org. Has an App ID and a private key.
- **Installation** — When a user/org installs the app on their account or repos. Each installation has an Installation ID.
- **JWT** — Short-lived token (10 min) signed with the app's private key. Used only to authenticate as the app itself (e.g., to list installations or generate installation tokens).
- **Installation access token** — Short-lived token (1 hour) scoped to a specific installation. Used for actual resource access.

### Creating a JWT

```python
import jwt, time, cryptography

app_id = "123456"
private_key = open("private-key.pem").read()

payload = {
    "iat": int(time.time()) - 60,   # issued 60s ago (clock skew buffer)
    "exp": int(time.time()) + 600,  # expires in 10 minutes
    "iss": app_id
}

token = jwt.encode(payload, private_key, algorithm="RS256")
```

```bash
# Usage
curl -H "Authorization: Bearer <JWT>" \
     -H "Accept: application/vnd.github+json" \
     https://api.github.com/app
```

### Getting an Installation Access Token

```http
POST /app/installations/{installation_id}/access_tokens
Authorization: Bearer <JWT>
Accept: application/vnd.github+json
```

**Optional request body:**
```json
{
  "repositories": ["repo-name-1", "repo-name-2"],
  "permissions": {
    "issues": "write",
    "contents": "read"
  }
}
```

**Response:**
```json
{
  "token": "ghs_16C7e42F292c6912E7710c838347Ae178B4a",
  "expires_at": "2016-07-11T22:14:10Z",
  "permissions": { "issues": "write", "contents": "read" },
  "repositories": [...]
}
```

Use the `token` value as `Authorization: Bearer ghs_...` for all subsequent resource requests.

### Key App Endpoints

| Operation | Method | Path | Auth |
|---|---|---|---|
| Get the authenticated app | GET | `/app` | JWT |
| List app installations | GET | `/app/installations` | JWT |
| Get an installation | GET | `/app/installations/{id}` | JWT |
| Create installation token | POST | `/app/installations/{id}/access_tokens` | JWT |
| Get repos accessible to installation | GET | `/installation/repositories` | Installation token |
| List installations for authenticated user | GET | `/user/installations` | User OAuth token |
| Get app by slug | GET | `/apps/{app_slug}` | JWT or PAT |
| Suspend installation | PUT | `/app/installations/{id}/suspended` | JWT |
| Unsuspend installation | DELETE | `/app/installations/{id}/suspended` | JWT |
| Delete installation | DELETE | `/app/installations/{id}` | JWT |

### GitHub App vs OAuth App Comparison

| Aspect | GitHub App | OAuth App |
|---|---|---|
| Identity | Acts as itself (not a user) | Acts as the authorizing user |
| Rate limit | 5,000–12,500/hr (scales) | 5,000/hr |
| Permissions | Fine-grained per-resource | Broad scopes |
| Repo scope | Can be restricted to specific repos | All repos the user can access |
| Webhooks | Built-in (configured once on app) | Per-repo/org webhook |
| Audit log | Shows as app name | Shows as user |
| Recommended for | New org integrations, CI, bots | User-facing web apps (legacy) |

---

## OAuth Apps

GitHub recommends GitHub Apps for new integrations, but OAuth Apps remain supported.

### Authorization Code Flow

**Step 1 — Redirect user:**
```
GET https://github.com/login/oauth/authorize
  ?client_id=CLIENT_ID
  &redirect_uri=https://example.com/callback
  &scope=repo,read:user
  &state=RANDOM_STRING
```

**Step 2 — Exchange code for token:**
```http
POST https://github.com/login/oauth/access_token
Content-Type: application/json
Accept: application/json

{
  "client_id": "CLIENT_ID",
  "client_secret": "CLIENT_SECRET",
  "code": "CODE_FROM_CALLBACK",
  "redirect_uri": "https://example.com/callback"
}
```

Response: `{ "access_token": "gho_...", "token_type": "bearer", "scope": "repo,read:user" }`

**Step 3 — Use the token:**
```
Authorization: Bearer gho_...
```

### Device Flow (for CLIs and headless apps)

```http
POST https://github.com/login/device/code
Content-Type: application/json
Accept: application/json

{ "client_id": "CLIENT_ID", "scope": "repo" }
```

Response includes `device_code`, `user_code`, `verification_uri`, `interval`, `expires_in`.

Display `verification_uri` and `user_code` to the user. Poll:
```http
POST https://github.com/login/oauth/access_token
{ "client_id": "...", "device_code": "...", "grant_type": "urn:ietf:params:oauth:grant-type:device_code" }
```

Poll at the `interval` (seconds) until `access_token` is returned or the code expires.

### Token Management

```http
# Check token
POST /applications/{client_id}/token
Authorization: Basic base64(CLIENT_ID:CLIENT_SECRET)
{ "access_token": "TOKEN" }

# Reset token (issues new token, old one is invalidated)
PATCH /applications/{client_id}/token
Authorization: Basic base64(CLIENT_ID:CLIENT_SECRET)
{ "access_token": "TOKEN" }

# Revoke token
DELETE /applications/{client_id}/token
Authorization: Basic base64(CLIENT_ID:CLIENT_SECRET)
{ "access_token": "TOKEN" }
```

---

## GITHUB_TOKEN (Actions)

Automatically created for each workflow job. No setup required.

**Accessing it:**
```yaml
steps:
  - name: Call API
    run: |
      curl -H "Authorization: Bearer ${{ secrets.GITHUB_TOKEN }}" \
           https://api.github.com/repos/${{ github.repository }}/issues
```

Or via `github.token` context: `${{ github.token }}`

### Permissions Block

Default permissions vary by org/repo settings (`permissive` or `restrictive`). Override explicitly in your workflow:

```yaml
# At workflow level
permissions:
  contents: read
  issues: write
  pull-requests: write

# At job level (overrides workflow-level)
jobs:
  my-job:
    permissions:
      contents: write
      packages: write
```

**All available permission keys:**

`actions`, `attestations`, `checks`, `contents`, `deployments`, `discussions`, `id-token`, `issues`, `packages`, `pages`, `pull-requests`, `repository-projects`, `security-events`, `statuses`

Each set to `read`, `write`, or `none`.

**Set all to none then grant only what's needed:**
```yaml
permissions: {}  # or: read-all / write-all
```

### GITHUB_TOKEN Limitations

- Cannot trigger new workflow runs (to prevent infinite loops) — use a PAT or GitHub App token for that
- Scoped to the current repository only
- Rate limit: 1,000 requests/hour per repo (15,000 on Enterprise Cloud)
- Some admin operations not available regardless of permissions granted

---

## Required Headers

Every GitHub API request should include:

```http
Authorization: Bearer <token>
Accept: application/vnd.github+json
X-GitHub-Api-Version: 2022-11-28
User-Agent: your-app-name
```

**`User-Agent`** is required — requests without it receive `403 Forbidden`. Most HTTP libraries set this automatically; verify it isn't being suppressed.

**`X-GitHub-Api-Version`**: `2022-11-28` is the stable baseline; `2026-03-10` is the latest. If omitted, defaults to `2022-11-28`.

---

## SAML SSO Organizations

For organizations enforcing SAML SSO, classic PATs must be authorized for that org after creation:

1. Create the PAT
2. Go to the token's settings → "Configure SSO" → authorize for the org

Fine-grained PATs handle SSO at creation time — no separate step needed.

GitHub App installation tokens are not subject to SAML SSO restrictions.

---

## Choosing the Right Method

```
Building a CI/CD bot for an org?
  → GitHub App (higher rate limits, scoped permissions, audit log)

Writing a personal script to manage your own repos?
  → Fine-grained PAT (scoped to exactly what you need)

Running automation inside GitHub Actions?
  → GITHUB_TOKEN (free, automatic, no secret management)
  → PAT or GitHub App token only if you need to trigger other workflows

Building a web app where users log in with GitHub?
  → OAuth App (user-facing auth flow)

Legacy integration that predates GitHub Apps?
  → Classic PAT (but migrate when possible)
```
