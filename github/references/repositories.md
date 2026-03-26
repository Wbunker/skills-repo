# GitHub Repositories, Contents, and Git Data Reference

## Table of Contents
1. [Repository CRUD](#1-repository-crud)
2. [Branches and Tags](#2-branches-and-tags)
3. [Repository Contents API](#3-repository-contents-api)
4. [Git Data API](#4-git-data-api)
5. [Programmatic Commit Workflow](#5-programmatic-commit-workflow)
6. [Forks](#6-forks)
7. [Collaborators and Permissions](#7-collaborators-and-permissions)
8. [Topics and Metadata](#8-topics-and-metadata)

---

## 1. Repository CRUD

### List Repositories

```http
GET /user/repos
GET /orgs/{org}/repos
GET /users/{username}/repos
```

**`/user/repos` params:** `visibility` (all/public/private), `affiliation` (owner/collaborator/organization_member), `type`, `sort` (created/updated/pushed/full_name), `direction`, `per_page`, `page`, `since`, `before`

**`/orgs/{org}/repos` params:** `type` (all/public/private/forks/sources/member/internal), `sort`, `direction`, `per_page`, `page`

**Response object key fields:** `id`, `name`, `full_name`, `owner`, `private`, `visibility`, `html_url`, `description`, `fork`, `default_branch`, `topics`, `archived`, `disabled`, `pushed_at`, `created_at`, `updated_at`, `size`, `stargazers_count`, `forks_count`, `open_issues_count`, `license`, `permissions`

### Get a Repository

```http
GET /repos/{owner}/{repo}
```

Returns the full detailed representation including `network_count`, `subscribers_count`, `allow_squash_merge`, `allow_merge_commit`, `allow_rebase_merge`, `allow_auto_merge`, `delete_branch_on_merge`, `allow_forking`, `is_template`.

### Create a Repository

```http
POST /user/repos          # for authenticated user
POST /orgs/{org}/repos    # for an organization
```

**Request body:**

| Field | Type | Required | Description |
|---|---|---|---|
| `name` | string | ✓ | Repo name |
| `description` | string | | Short description |
| `homepage` | string | | URL |
| `private` | boolean | | Default: false |
| `visibility` | string | | public/private/internal (org only) |
| `has_issues` | boolean | | Default: true |
| `has_projects` | boolean | | Default: true |
| `has_wiki` | boolean | | Default: true |
| `has_discussions` | boolean | | Default: false |
| `auto_init` | boolean | | Create initial commit with README |
| `gitignore_template` | string | | e.g. "Node", "Python" |
| `license_template` | string | | SPDX identifier, e.g. "mit" |
| `allow_squash_merge` | boolean | | Default: true |
| `allow_merge_commit` | boolean | | Default: true |
| `allow_rebase_merge` | boolean | | Default: true |
| `allow_auto_merge` | boolean | | Default: false |
| `delete_branch_on_merge` | boolean | | Default: false |
| `is_template` | boolean | | Mark as template repo |
| `team_id` | integer | | Grant team access (org repos) |

**Response:** 201 Created — full repository object

### Update a Repository

```http
PATCH /repos/{owner}/{repo}
```

Same fields as create, plus:
- `default_branch` — rename the default branch
- `archived` — set `true` to archive (irreversible via API; must unarchive via UI)
- `security_and_analysis` — object to enable/disable secret scanning, code scanning

**Response:** 200 — full repository object

### Delete a Repository

```http
DELETE /repos/{owner}/{repo}
```

Requires `delete_repo` scope (classic PAT) or `administration: write` (fine-grained PAT). **Response:** 204 No Content

### Transfer a Repository

```http
POST /repos/{owner}/{repo}/transfer
```

**Body:** `new_owner` (required), `new_name`, `team_ids` (array of int — grant access to teams in new org)

**Response:** 202 Accepted — repository object (transfer is async)

### Create from Template

```http
POST /repos/{template_owner}/{template_repo}/generate
```

**Body:** `owner` (required), `name` (required), `description`, `include_all_branches`, `private`

---

## 2. Branches and Tags

### Branches

```http
GET  /repos/{owner}/{repo}/branches              # list
GET  /repos/{owner}/{repo}/branches/{branch}     # get one
POST /repos/{owner}/{repo}/branches              # rename (via update default branch)
```

**List params:** `protected` (bool filter), `per_page`, `page`

**Branch object:** `name`, `commit` (`sha`, `url`), `protected` (bool), `protection` (rules object if protected)

### Branch Protection

```http
GET    /repos/{owner}/{repo}/branches/{branch}/protection
PUT    /repos/{owner}/{repo}/branches/{branch}/protection
DELETE /repos/{owner}/{repo}/branches/{branch}/protection
```

**PUT body (key fields):**
```json
{
  "required_status_checks": {
    "strict": true,
    "contexts": ["ci/test", "ci/lint"]
  },
  "enforce_admins": true,
  "required_pull_request_reviews": {
    "dismissal_restrictions": { "users": [], "teams": [] },
    "dismiss_stale_reviews": true,
    "require_code_owner_reviews": true,
    "required_approving_review_count": 2,
    "require_last_push_approval": false
  },
  "restrictions": {
    "users": ["admin-user"],
    "teams": ["ops-team"],
    "apps": []
  },
  "required_linear_history": false,
  "allow_force_pushes": false,
  "allow_deletions": false,
  "block_creations": false,
  "required_conversation_resolution": true,
  "lock_branch": false,
  "allow_fork_syncing": false
}
```

All fields required in the PUT body (use `null` where not wanted). Returns 200 — protection object.

### Tags

```http
GET /repos/{owner}/{repo}/tags           # list lightweight + annotated tags
GET /repos/{owner}/{repo}/git/tags/{sha} # get annotated tag object
POST /repos/{owner}/{repo}/git/tags      # create annotated tag object
```

**Tag listing response items:** `name`, `commit` (`sha`, `url`), `zipball_url`, `tarball_url`

**Create annotated tag body:**
```json
{
  "tag": "v1.0.0",
  "message": "Release v1.0.0",
  "object": "<commit-sha>",
  "type": "commit",
  "tagger": { "name": "Bot", "email": "bot@example.com", "date": "2024-01-01T00:00:00Z" }
}
```

After creating the tag object, create a ref to make it visible:
```http
POST /repos/{owner}/{repo}/git/refs
{ "ref": "refs/tags/v1.0.0", "sha": "<tag-object-sha>" }
```

For a **lightweight tag**, skip the tag object and create the ref pointing directly to the commit SHA.

---

## 3. Repository Contents API

### Get File or Directory

```http
GET /repos/{owner}/{repo}/contents/{path}
```

**Query params:** `ref` (branch name, tag, or commit SHA — defaults to default branch)

**File response:**
```json
{
  "type": "file",
  "encoding": "base64",
  "content": "SGVsbG8gV29ybGQK",
  "sha": "980a0d5f19a64b4b30a87d4206aade58726b60e3",
  "name": "README.md",
  "path": "README.md",
  "size": 12,
  "url": "https://api.github.com/repos/owner/repo/contents/README.md",
  "html_url": "https://github.com/owner/repo/blob/main/README.md",
  "git_url": "https://api.github.com/repos/owner/repo/git/blobs/980a0d5f...",
  "download_url": "https://raw.githubusercontent.com/owner/repo/main/README.md",
  "_links": { "self": "...", "git": "...", "html": "..." }
}
```

Decode content: `base64.b64decode(content.replace('\n', ''))`

**Directory response:** Array of objects with same shape but no `encoding`/`content` (too large to inline).

**Size limits:**
- ≤ 1 MB: full response with `content` field
- 1–100 MB: use raw media type: `Accept: application/vnd.github.raw+json`
- > 100 MB: not supported via contents API — use Git Data API (blob endpoint)

### Get README

```http
GET /repos/{owner}/{repo}/readme
GET /repos/{owner}/{repo}/readme/{dir}
```

**Query params:** `ref`
Returns the repo's README as a file content object (base64 encoded).

### Create or Update a File

```http
PUT /repos/{owner}/{repo}/contents/{path}
```

**Request body:**

| Field | Required | Description |
|---|---|---|
| `message` | ✓ | Commit message |
| `content` | ✓ | **Base64-encoded** file content |
| `sha` | ✓ for updates | Current blob SHA (from a prior GET of the file) |
| `branch` | | Target branch (defaults to default branch) |
| `committer` | | `{ name, email, date }` |
| `author` | | `{ name, email, date }` |

**Response:** 200 (update) or 201 (create)
```json
{
  "content": { "name", "path", "sha", "size", "url", "html_url", ... },
  "commit": { "sha", "message", "author", "committer", "tree", "parents", "verification" }
}
```

**Creating a file:**
```python
import base64, requests

content = base64.b64encode("Hello World\n".encode()).decode()
requests.put(
    "https://api.github.com/repos/owner/repo/contents/hello.txt",
    headers={"Authorization": "Bearer TOKEN", "Accept": "application/vnd.github+json"},
    json={"message": "Add hello.txt", "content": content}
)
```

**Updating a file (must include sha):**
```python
# First GET the file to retrieve its sha
r = requests.get("https://api.github.com/repos/owner/repo/contents/hello.txt", headers=headers)
sha = r.json()["sha"]

new_content = base64.b64encode("Hello Updated World\n".encode()).decode()
requests.put(
    "https://api.github.com/repos/owner/repo/contents/hello.txt",
    headers=headers,
    json={"message": "Update hello.txt", "content": new_content, "sha": sha}
)
```

### Delete a File

```http
DELETE /repos/{owner}/{repo}/contents/{path}
```

**Body:** `message` (required), `sha` (required — blob SHA), `branch`, `committer` (`name`, `email`), `author` (`name`, `email`)

**Response:** 200 — `{ content: null, commit: {...} }`

### Download Archive

```http
GET /repos/{owner}/{repo}/tarball/{ref}    → 302 redirect to .tar.gz
GET /repos/{owner}/{repo}/zipball/{ref}    → 302 redirect to .zip
```

Follow the redirect to download. `{ref}` can be a branch, tag, or SHA.

---

## 4. Git Data API

For low-level git operations — building commits without using the contents API.

### Refs

```http
GET    /repos/{owner}/{repo}/git/ref/{ref}              # get one ref
GET    /repos/{owner}/{repo}/git/matching-refs/{ref}    # list refs by prefix
POST   /repos/{owner}/{repo}/git/refs                   # create ref
PATCH  /repos/{owner}/{repo}/git/refs/{ref}             # update ref
DELETE /repos/{owner}/{repo}/git/refs/{ref}             # delete ref
```

**Ref path format in URL:** `heads/branch-name` or `tags/tag-name` (no `refs/` prefix)

**Create body:**
```json
{
  "ref": "refs/heads/new-branch",
  "sha": "aa218f56ec189cfe7e8a7ca8aef91344fa7....."
}
```
Note: `ref` in the create body **must** be fully qualified (starts with `refs/`).

**Update body:**
```json
{ "sha": "new-commit-sha", "force": false }
```
Set `force: true` for non-fast-forward updates (force push equivalent).

**Ref response:**
```json
{
  "ref": "refs/heads/main",
  "node_id": "...",
  "url": "...",
  "object": { "type": "commit", "sha": "...", "url": "..." }
}
```

### Commits (Low-level Objects)

```http
GET  /repos/{owner}/{repo}/git/commits/{commit_sha}    # get commit object
POST /repos/{owner}/{repo}/git/commits                 # create commit object
```

**Create body:**
```json
{
  "message": "feat: add new feature",
  "tree": "<tree-sha>",
  "parents": ["<parent-commit-sha>"],
  "author": { "name": "Bot", "email": "bot@example.com", "date": "2024-01-01T00:00:00Z" }
}
```

**Commit response:**
```json
{
  "sha": "...",
  "url": "...",
  "html_url": "...",
  "message": "feat: add new feature",
  "author": { "name", "email", "date" },
  "committer": { "name", "email", "date" },
  "tree": { "sha", "url" },
  "parents": [{ "sha", "url", "html_url" }],
  "verification": { "verified": true, "reason": "valid", "signature": "...", "payload": "..." }
}
```

### Trees

```http
GET  /repos/{owner}/{repo}/git/trees/{tree_sha}    # get tree
POST /repos/{owner}/{repo}/git/trees               # create tree
```

**Get params:** `recursive` (any truthy string) — returns flattened tree; `truncated: true` if too large

**Create body:**
```json
{
  "base_tree": "<existing-tree-sha>",
  "tree": [
    {
      "path": "src/main.py",
      "mode": "100644",
      "type": "blob",
      "content": "print('hello')"
    },
    {
      "path": "deleted-file.txt",
      "mode": "100644",
      "type": "blob",
      "sha": null
    }
  ]
}
```

**Mode values:**
| Mode | Type | Meaning |
|---|---|---|
| `100644` | blob | Regular file |
| `100755` | blob | Executable file |
| `040000` | tree | Subdirectory |
| `160000` | commit | Git submodule (gitlink) |
| `120000` | blob | Symlink |

Use `sha: null` to delete a path. Use `content` instead of `sha` to inline file content (GitHub creates the blob).

### Blobs

```http
GET  /repos/{owner}/{repo}/git/blobs/{file_sha}    # get blob (always base64)
POST /repos/{owner}/{repo}/git/blobs               # create blob
```

**Create body:**
```json
{ "content": "Hello World\n", "encoding": "utf-8" }
```
Or with base64: `{ "content": "SGVsbG8gV29ybGQK", "encoding": "base64" }`

**Create response:** `{ "sha": "...", "url": "..." }`

**Get response:** Content is **always** base64-encoded in the response, regardless of how it was stored. Supports blobs up to 100 MB.

---

## 5. Programmatic Commit Workflow

To create a commit without using the contents API (useful for multi-file commits or when you need full control):

```
1. GET current branch ref
   GET /repos/{owner}/{repo}/git/ref/heads/{branch}
   → save object.sha as CURRENT_COMMIT_SHA

2. GET current commit to find its tree
   GET /repos/{owner}/{repo}/git/commits/{CURRENT_COMMIT_SHA}
   → save tree.sha as BASE_TREE_SHA

3. Create blobs for changed files
   POST /repos/{owner}/{repo}/git/blobs
   { "content": "<file content>", "encoding": "utf-8" }
   → save sha as BLOB_SHA for each file

4. Create a new tree
   POST /repos/{owner}/{repo}/git/trees
   {
     "base_tree": BASE_TREE_SHA,
     "tree": [
       { "path": "file.txt", "mode": "100644", "type": "blob", "sha": BLOB_SHA },
       { "path": "deleted.txt", "mode": "100644", "type": "blob", "sha": null }
     ]
   }
   → save sha as NEW_TREE_SHA

5. Create the commit
   POST /repos/{owner}/{repo}/git/commits
   {
     "message": "your commit message",
     "tree": NEW_TREE_SHA,
     "parents": [CURRENT_COMMIT_SHA]
   }
   → save sha as NEW_COMMIT_SHA

6. Update the branch ref
   PATCH /repos/{owner}/{repo}/git/refs/heads/{branch}
   { "sha": NEW_COMMIT_SHA, "force": false }
```

This approach supports multi-file changes in a single atomic commit. Use `force: true` on step 6 only if you're intentionally rewriting history.

---

## 6. Forks

### Fork a Repository

```http
POST /repos/{owner}/{repo}/forks
```

**Body:** `organization` (fork into org), `name` (rename the fork), `default_branch_only` (bool)

**Response:** 202 Accepted — repository object (fork is async; the repo may not be ready immediately)

### List Forks

```http
GET /repos/{owner}/{repo}/forks
```

**Params:** `sort` (newest/oldest/stargazers/watchers), `per_page`, `page`

---

## 7. Collaborators and Permissions

### Manage Collaborators

```http
GET    /repos/{owner}/{repo}/collaborators                            # list
GET    /repos/{owner}/{repo}/collaborators/{username}                 # check if collaborator
PUT    /repos/{owner}/{repo}/collaborators/{username}                 # add/update
DELETE /repos/{owner}/{repo}/collaborators/{username}                 # remove
GET    /repos/{owner}/{repo}/collaborators/{username}/permission      # get permission level
```

**PUT body:** `permission` — `pull` / `triage` / `push` / `maintain` / `admin`

**Permission levels:**
| Level | Access |
|---|---|
| `pull` (read) | Clone, pull |
| `triage` | `pull` + manage issues/PRs without write |
| `push` (write) | `triage` + push, create branches |
| `maintain` | `push` + manage releases, non-destructive admin |
| `admin` | Full control including sensitive operations |

### Invitations

```http
GET  /repos/{owner}/{repo}/invitations           # list pending invitations
PATCH /repos/{owner}/{repo}/invitations/{id}     # update invitation
DELETE /repos/{owner}/{repo}/invitations/{id}    # cancel invitation
GET  /user/repository_invitations                # list invitations for authenticated user
PATCH /user/repository_invitations/{id}          # accept invitation
DELETE /user/repository_invitations/{id}         # decline invitation
```

---

## 8. Topics and Metadata

### Repository Topics

```http
GET /repos/{owner}/{repo}/topics
PUT /repos/{owner}/{repo}/topics
```

**GET response:** `{ "names": ["machine-learning", "python", ...] }`

**PUT body:** `{ "names": ["topic1", "topic2"] }` — replaces all existing topics
Topics must be lowercase, alphanumeric, or hyphens, max 50 chars, up to 20 per repo.

### Languages

```http
GET /repos/{owner}/{repo}/languages
```

**Response:** Object mapping language name to bytes: `{ "JavaScript": 123456, "Python": 78901 }`

### Contributors

```http
GET /repos/{owner}/{repo}/contributors
```

**Params:** `anon` (include anonymous contributors), `per_page`, `page`
**Response:** Array of user objects with added `contributions` count

### Traffic (requires push access)

```http
GET /repos/{owner}/{repo}/traffic/clones
GET /repos/{owner}/{repo}/traffic/views
GET /repos/{owner}/{repo}/traffic/popular/paths
GET /repos/{owner}/{repo}/traffic/popular/referrers
```

**Params for clones/views:** `per` — `day` or `week`
