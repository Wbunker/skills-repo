# GitHub Organizations and Teams Reference

## Table of Contents
1. [Org REST API](#1-org-rest-api)
2. [Org Members](#2-org-members)
3. [Member Roles](#3-member-roles)
4. [Org Invitations](#4-org-invitations)
5. [Org Webhooks](#5-org-webhooks)
6. [Org Secrets](#6-org-secrets)
7. [Org Variables](#7-org-variables)
8. [Audit Log](#8-audit-log)
9. [Teams REST API](#9-teams-rest-api)
10. [Team Membership](#10-team-membership)
11. [Team Repos](#11-team-repos)
12. [Nested Teams](#12-nested-teams)
13. [Team Permissions](#13-team-permissions)
14. [Team Discussions](#14-team-discussions)
15. [Repository Collaborators](#15-repository-collaborators)
16. [CODEOWNERS](#16-codeowners)
17. [Deploy Keys](#17-deploy-keys)

---

## 1. Org REST API

```http
GET    /orgs/{org}
PATCH  /orgs/{org}
GET    /user/orgs                     # orgs for authenticated user
GET    /users/{username}/orgs         # public orgs for a user
DELETE /orgs/{org}                    # requires owner; deletes org
```

**Get org key fields:** `login`, `id`, `name`, `description`, `email`, `plan`, `public_repos`, `total_private_repos`, `disk_usage`, `collaborators`, `billing_email`, `default_repository_permission`, `members_can_create_repositories`, `two_factor_requirement_enabled`, `created_at`, `updated_at`

**Update org (`PATCH /orgs/{org}`) settable fields:** `billing_email`, `company`, `email`, `location`, `name`, `description`, `default_repository_permission` (read/write/admin/none), `members_can_create_repositories`, `members_can_create_public_repositories`, `members_can_create_private_repositories`, `members_can_fork_private_repositories`, `web_commit_signoff_required`, `advanced_security_enabled_for_new_repositories`, `secret_scanning_enabled_for_new_repositories`

---

## 2. Org Members

```http
GET    /orgs/{org}/members                             # list members
GET    /orgs/{org}/members/{username}                  # check membership (204 = member, 302/404 = not)
DELETE /orgs/{org}/members/{username}                  # remove member
GET    /orgs/{org}/outside_collaborators               # list outside collaborators
DELETE /orgs/{org}/outside_collaborators/{username}    # remove outside collaborator
PUT    /orgs/{org}/outside_collaborators/{username}    # convert member to outside collaborator
```

**List members params:** `filter` (2fa_disabled | all), `role` (all | admin | member), `per_page`, `page`

**Check membership** returns 204 (is a member), 302 (requester not a member, redirect), or 404 (not a member).

**Outside collaborators** are users with access to one or more org repos but are not org members. They have no org-level permissions.

**Convert member to outside collaborator** (`PUT /orgs/{org}/outside_collaborators/{username}`): demotes a member, revoking org membership while keeping their direct repo access. Returns 202 if conversion is async, 204 if immediate.

---

## 3. Member Roles

| Role   | API value | Capabilities |
|--------|-----------|--------------|
| Member | `member`  | Access to org repos per team/direct grants; can create repos if org allows; cannot manage org settings |
| Owner  | `admin`   | Full admin: manage members, teams, billing, settings, delete org |

```http
GET  /orgs/{org}/memberships/{username}    # get membership (includes role, state)
PUT  /orgs/{org}/memberships/{username}    # set role: body {"role": "member"|"admin"}
DELETE /orgs/{org}/memberships/{username}  # remove from org
GET  /user/memberships/orgs                # list authenticated user's org memberships
GET  /user/memberships/orgs/{org}          # get authenticated user's membership in specific org
PATCH /user/memberships/orgs/{org}         # accept/decline invitation: body {"state": "active"}
```

**Membership states:** `active` (accepted), `pending` (invitation sent, not yet accepted).

---

## 4. Org Invitations

```http
POST   /orgs/{org}/invitations                         # create invitation
GET    /orgs/{org}/invitations                         # list pending invitations
GET    /orgs/{org}/failed_invitations                  # list failed invitations
DELETE /orgs/{org}/invitations/{invitation_id}         # cancel invitation
GET    /orgs/{org}/invitations/{invitation_id}/teams   # list teams for invitation
```

**Create invitation body:**

```json
{
  "email": "user@example.com",
  "invitee_id": 12345,
  "role": "direct_member",
  "team_ids": [123, 456]
}
```

`role` options: `owner`, `direct_member`, `billing_manager`. Provide either `email` or `invitee_id`, not both.

**Failed invitations** are those where the email bounced or the invite expired (7 days). The response includes `failed_at` and `failed_reason`.

---

## 5. Org Webhooks

Same CRUD pattern as repo webhooks but scoped to org-level events.

```http
GET    /orgs/{org}/hooks
POST   /orgs/{org}/hooks
GET    /orgs/{org}/hooks/{hook_id}
PATCH  /orgs/{org}/hooks/{hook_id}
DELETE /orgs/{org}/hooks/{hook_id}
POST   /orgs/{org}/hooks/{hook_id}/pings
```

**Create/update body:**

```json
{
  "name": "web",
  "active": true,
  "events": ["member", "team", "repository", "organization"],
  "config": {
    "url": "https://example.com/webhook",
    "content_type": "json",
    "secret": "mysecret",
    "insecure_ssl": "0"
  }
}
```

**Org-specific events:** `member`, `membership`, `team`, `team_add`, `organization`, `org_block`, `repository`, `deploy_key`, `meta`

---

## 6. Org Secrets

Org secrets are available to selected or all org repos and are injected into Actions workflows.

```http
GET    /orgs/{org}/actions/secrets                              # list secrets (names only, no values)
GET    /orgs/{org}/actions/secrets/{secret_name}               # get secret metadata
PUT    /orgs/{org}/actions/secrets/{secret_name}               # create or update
DELETE /orgs/{org}/actions/secrets/{secret_name}               # delete
GET    /orgs/{org}/actions/secrets/public-key                  # get encryption public key

GET    /orgs/{org}/actions/secrets/{secret_name}/repositories  # list repos with access
PUT    /orgs/{org}/actions/secrets/{secret_name}/repositories  # set repos (replaces list)
PUT    /orgs/{org}/actions/secrets/{secret_name}/repositories/{repo_id}    # add repo
DELETE /orgs/{org}/actions/secrets/{secret_name}/repositories/{repo_id}    # remove repo
```

**Create/update body:**

```json
{
  "encrypted_value": "<libsodium sealed box, base64>",
  "key_id": "<public key id>",
  "visibility": "all" | "private" | "selected"
}
```

`visibility`: `all` (all org repos), `private` (all private repos), `selected` (only listed repos — requires managing repo list).

Encrypt using the org's public key with `libsodium` (`crypto_box_seal`).

---

## 7. Org Variables

Same pattern as secrets but values are stored and returned in plaintext.

```http
GET    /orgs/{org}/actions/variables
POST   /orgs/{org}/actions/variables
GET    /orgs/{org}/actions/variables/{variable_name}
PATCH  /orgs/{org}/actions/variables/{variable_name}
DELETE /orgs/{org}/actions/variables/{variable_name}

GET    /orgs/{org}/actions/variables/{variable_name}/repositories
PUT    /orgs/{org}/actions/variables/{variable_name}/repositories
PUT    /orgs/{org}/actions/variables/{variable_name}/repositories/{repo_id}
DELETE /orgs/{org}/actions/variables/{variable_name}/repositories/{repo_id}
```

**Create body:** `{ "name": "VAR_NAME", "value": "plaintext", "visibility": "all"|"private"|"selected" }`

**Update (`PATCH`) body:** same fields, all optional.

Variables differ from secrets in that `value` is returned in GET responses.

---

## 8. Audit Log

```http
GET /orgs/{org}/audit-log
```

**Query params:**

| Param    | Description |
|----------|-------------|
| `phrase` | Free-text or structured filter (see below) |
| `include`| `web`, `git`, `all` (default: `web`) |
| `after`  | Cursor for forward pagination |
| `before` | Cursor for backward pagination |
| `order`  | `asc` or `desc` |
| `per_page` | 1–100, default 30 |

**Structured `phrase` filters:** `action:org.invite_member`, `actor:octocat`, `repo:myorg/myrepo`, `created:>2024-01-01`, `created:2024-01-01..2024-06-30`. Combine with spaces (AND). Common prefixes: `org.*`, `repo.*`, `team.*`, `hook.*`, `secret.*`, `protected_branch.*`.

**Response fields per event:** `@timestamp`, `action`, `actor`, `actor_id`, `user`, `org`, `repo`, `created_at`, `_document_id`, plus action-specific fields.

Audit log is also queryable via GraphQL (`auditLog` connection on `Organization`).

---

## 9. Teams REST API

Teams are groups within an org that can be granted access to repos.

```http
GET    /orgs/{org}/teams                                  # list teams
POST   /orgs/{org}/teams                                  # create team
GET    /orgs/{org}/teams/{team_slug}                      # get by slug
PATCH  /orgs/{org}/teams/{team_slug}                      # update
DELETE /orgs/{org}/teams/{team_slug}                      # delete
GET    /user/teams                                         # teams for authenticated user
```

**Create body:**

```json
{
  "name": "backend-engineers",
  "description": "Backend team",
  "maintainers": ["user1", "user2"],
  "repo_names": ["myorg/myrepo"],
  "privacy": "secret" | "closed",
  "notification_setting": "notifications_enabled" | "notifications_disabled",
  "permission": "pull" | "push" | "admin",
  "parent_team_id": 456
}
```

`privacy`: `secret` = visible only to members and owners; `closed` = visible to all org members.

**Team slug** is auto-generated from the name (lowercased, spaces to hyphens). Use slug in API paths, not name.

---

## 10. Team Membership

```http
GET    /orgs/{org}/teams/{team_slug}/members               # list members
GET    /orgs/{org}/teams/{team_slug}/memberships/{username} # check/get membership
PUT    /orgs/{org}/teams/{team_slug}/memberships/{username} # add or update
DELETE /orgs/{org}/teams/{team_slug}/memberships/{username} # remove
```

**List members params:** `role` (all | maintainer | member), `per_page`, `page`

**Add/update body:** `{ "role": "member" | "maintainer" }`. `maintainer` can manage team membership and settings.

**Membership states:** `active` (accepted), `pending` (org invite not yet accepted).

---

## 11. Team Repos

```http
GET    /orgs/{org}/teams/{team_slug}/repos                         # list repos
GET    /orgs/{org}/teams/{team_slug}/repos/{owner}/{repo}          # check if team manages repo
PUT    /orgs/{org}/teams/{team_slug}/repos/{owner}/{repo}          # add repo or update permission
DELETE /orgs/{org}/teams/{team_slug}/repos/{owner}/{repo}          # remove repo
```

**Add/update body:** `{ "permission": "pull" | "triage" | "push" | "maintain" | "admin" }`

The check endpoint returns 204 if the team has access, 404 if not. The response object includes a `permissions` map and `role_name`.

---

## 12. Nested Teams

Teams can have a parent, forming a hierarchy. Child teams inherit parent team's repo permissions (child permissions can be equal or higher, never lower).

```http
GET /orgs/{org}/teams/{team_slug}/teams     # list child teams
```

Set `parent_team_id` in create or update to establish the relationship. Set to `null` in an update to detach from parent.

**Rules:**
- A team can have only one parent.
- Circular references are rejected.
- Deleting a parent does not delete children; they become top-level.
- Members of a child team are implicitly included in the parent team's member list.

---

## 13. Team Permissions

| Permission | Level | Description |
|------------|-------|-------------|
| `pull`     | Read  | Clone, pull, view issues/PRs |
| `triage`   | Triage | Read + manage issues/PRs (label, close, assign) without write |
| `push`     | Write | Triage + push to non-protected branches |
| `maintain` | Maintain | Push + manage repo settings (no destructive actions) |
| `admin`    | Admin | Full repo control including branch protection, add collaborators |

Set via `PUT /orgs/{org}/teams/{team_slug}/repos/{owner}/{repo}` with a `permission` body field.

---

## 14. Team Discussions

Teams have a discussion board for internal communication.

```http
GET    /orgs/{org}/teams/{team_slug}/discussions
POST   /orgs/{org}/teams/{team_slug}/discussions
GET    /orgs/{org}/teams/{team_slug}/discussions/{discussion_number}
PATCH  /orgs/{org}/teams/{team_slug}/discussions/{discussion_number}
DELETE /orgs/{org}/teams/{team_slug}/discussions/{discussion_number}

GET    /orgs/{org}/teams/{team_slug}/discussions/{discussion_number}/comments
POST   /orgs/{org}/teams/{team_slug}/discussions/{discussion_number}/comments
PATCH  /orgs/{org}/teams/{team_slug}/discussions/{discussion_number}/comments/{comment_number}
DELETE /orgs/{org}/teams/{team_slug}/discussions/{discussion_number}/comments/{comment_number}
```

**Create discussion body:** `{ "title": "...", "body": "...", "private": false }`. Private discussions are only visible to team members.

Reactions are supported via `/reactions` sub-endpoints on both discussions and comments.

---

## 15. Repository Collaborators

Direct collaborators are individuals (not teams) granted repo access.

```http
GET    /repos/{owner}/{repo}/collaborators
GET    /repos/{owner}/{repo}/collaborators/{username}          # check (204/404)
PUT    /repos/{owner}/{repo}/collaborators/{username}          # add or update
DELETE /repos/{owner}/{repo}/collaborators/{username}          # remove
GET    /repos/{owner}/{repo}/collaborators/{username}/permission
```

**Add body:** `{ "permission": "pull" | "triage" | "push" | "maintain" | "admin" }` (default: `push`)

**List params:** `affiliation` (outside | direct | all), `permission` (pull | triage | push | maintain | admin), `per_page`, `page`

**Permission endpoint response:** `{ "permission": "write", "role_name": "write", "user": { ... } }`

**Permission levels:**

| Value      | Alias  | Description |
|------------|--------|-------------|
| `pull`     | read   | View and clone |
| `triage`   | triage | Read + manage issues/PRs |
| `push`     | write  | Triage + push code |
| `maintain` | maintain | Write + repo management |
| `admin`    | admin  | Full control |

For org repos, adding a collaborator outside the org makes them an outside collaborator.

---

## 16. CODEOWNERS

CODEOWNERS automatically assigns review requests when a PR touches owned files.

### File Locations (checked in order)

1. `CODEOWNERS` (repo root)
2. `.github/CODEOWNERS`
3. `docs/CODEOWNERS`

The first file found is used; others are ignored.

### Syntax

```gitignore
# Whole repo default owner
*       @org/platform-team

# Specific path
/src/api/   @alice @bob

# File extension
*.go        @org/golang-team

# Negation (remove from previous rule) — only works on later, more specific rules
*.md        @org/docs-team
/src/*.md   @alice   # overrides above for this path

# Multiple owners
/infra/     @org/sre @devops-lead@example.com

# Email-based owners
/legal/     legal@example.com
```

**Rules:**
- Patterns follow `.gitignore` syntax.
- Later rules take precedence over earlier ones for the same path.
- Negation (`!`) removes a file from matching, it does not remove an owner.
- `@username` = individual GitHub user; `@org/team-slug` = team; `email` = email (must be associated with a GitHub account).

### Interaction with Branch Protection

In branch protection rules, **"Require a review from Code Owners"** means:

- At least one owner of every changed file must approve the PR.
- If a file has no CODEOWNERS entry, the requirement is waived for that file.
- This is enforced per-file; a single approver can satisfy ownership for multiple files if they own all of them.
- Dismissing a stale review resets the CODEOWNERS requirement.
- The CODEOWNERS check appears as a separate required check in the PR UI.

---

## 17. Deploy Keys

Deploy keys are SSH public keys attached to a single repository, granting read-only or read-write access without a user account.

```http
GET    /repos/{owner}/{repo}/keys
POST   /repos/{owner}/{repo}/keys
GET    /repos/{owner}/{repo}/keys/{key_id}
DELETE /repos/{owner}/{repo}/keys/{key_id}
```

**Create body:**

```json
{
  "title": "CI deploy key",
  "key": "ssh-ed25519 AAAA...",
  "read_only": true
}
```

`read_only: true` = clone/pull only. `read_only: false` = push access.

**Response fields:** `id`, `key`, `url`, `title`, `verified`, `created_at`, `read_only`, `added_by`, `last_used`

**Key rules:**
- The same public key cannot be used as a deploy key on more than one repository (use a unique key pair per repo).
- A public key already associated with a user account cannot be added as a deploy key.
- Deploy keys do not expire and are not tied to a user's account lifecycle.

**Use cases:**
- CI/CD runners that need to clone a private repo without a service account.
- Read-only access for monitoring or deployment tooling.
- Environments where scoped SSH keys are preferable to PATs.

**Workflow:** Generate a unique key pair (`ssh-keygen -t ed25519`), register the public key via the API or GitHub UI, store the private key in CI secrets, and set `GIT_SSH_COMMAND="ssh -i /path/to/key"` when cloning.
