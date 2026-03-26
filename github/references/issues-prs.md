# GitHub Issues and Pull Requests Reference

## Table of Contents
1. [Issues](#1-issues)
2. [Labels](#2-labels)
3. [Milestones](#3-milestones)
4. [Issue Comments](#4-issue-comments)
5. [Issue Events and Timeline](#5-issue-events-and-timeline)
6. [Pull Requests](#6-pull-requests)
7. [PR Reviews](#7-pr-reviews)
8. [PR Review Comments (Inline)](#8-pr-review-comments-inline)
9. [Requested Reviewers](#9-requested-reviewers)
10. [Checks API](#10-checks-api)

---

## 1. Issues

### List and Get

```http
GET /repos/{owner}/{repo}/issues
GET /repos/{owner}/{repo}/issues/{issue_number}
GET /issues                                          # all issues across repos (authenticated user)
GET /user/issues                                     # issues assigned/mentioned/created
GET /orgs/{org}/issues                               # issues in org repos
```

**`/repos/.../issues` query params:**

| Param | Values | Default |
|---|---|---|
| `state` | open / closed / all | open |
| `assignee` | username / none / * | — |
| `creator` | username | — |
| `mentioned` | username | — |
| `labels` | comma-separated label names | — |
| `milestone` | milestone number / none / * | — |
| `sort` | created / updated / comments | created |
| `direction` | asc / desc | desc |
| `since` | ISO 8601 timestamp | — |
| `per_page` | 1–100 | 30 |
| `page` | | 1 |

Note: List issues returns both issues AND pull requests. Filter to issues only with `GET /issues?pulls=false` or by checking `pull_request` field is absent.

**Issue object key fields:** `id`, `number`, `state`, `state_reason` (completed/not_planned/duplicate/reopened), `title`, `body`, `user` (creator), `labels` (array), `assignees` (array), `milestone`, `locked`, `active_lock_reason`, `comments` (count), `pull_request` (present if this is a PR), `reactions`, `created_at`, `updated_at`, `closed_at`, `html_url`

### Create an Issue

```http
POST /repos/{owner}/{repo}/issues
```

**Body:**

| Field | Required | Description |
|---|---|---|
| `title` | ✓ | Issue title |
| `body` | | Markdown body |
| `assignees` | | Array of login strings |
| `milestone` | | Milestone number |
| `labels` | | Array of label name strings |

**Response:** 201 — full issue object

### Update an Issue

```http
PATCH /repos/{owner}/{repo}/issues/{issue_number}
```

**Body:** `title`, `body`, `state` (open/closed), `state_reason`, `milestone` (number or null), `labels` (array replaces all), `assignees` (array replaces all)

### Close with Reason

```http
PATCH /repos/{owner}/{repo}/issues/{issue_number}
{ "state": "closed", "state_reason": "completed" }
```

`state_reason` values: `completed`, `not_planned`, `duplicate`, `reopened`

### Lock / Unlock

```http
PUT    /repos/{owner}/{repo}/issues/{issue_number}/lock
DELETE /repos/{owner}/{repo}/issues/{issue_number}/lock
```

**Lock body:** `lock_reason` — off-topic / too-heated / resolved / spam
Both respond 204 No Content.

### Assignees

```http
GET    /repos/{owner}/{repo}/issues/{issue_number}/assignees          # not a real endpoint — use issue object
POST   /repos/{owner}/{repo}/issues/{issue_number}/assignees          # add
DELETE /repos/{owner}/{repo}/issues/{issue_number}/assignees          # remove
GET    /repos/{owner}/{repo}/assignees                                 # list assignable users
GET    /repos/{owner}/{repo}/assignees/{assignee}                     # check assignability
```

**POST/DELETE body:** `{ "assignees": ["username1", "username2"] }`
**POST response:** 201 — full issue object; **DELETE response:** 200 — full issue object
**Check response:** 204 (can be assigned) or 404

---

## 2. Labels

### Repo-Level Label Management

```http
GET    /repos/{owner}/{repo}/labels                    # list all labels in repo
GET    /repos/{owner}/{repo}/labels/{name}             # get one label
POST   /repos/{owner}/{repo}/labels                    # create label
PATCH  /repos/{owner}/{repo}/labels/{name}             # update label
DELETE /repos/{owner}/{repo}/labels/{name}             # delete label
```

**Create/update body:** `name` (required for create), `color` (6-char hex without #), `description`

**Label object:** `id`, `node_id`, `url`, `name`, `color`, `default` (bool), `description`

### Issue-Level Label Operations

```http
GET    /repos/{owner}/{repo}/issues/{issue_number}/labels        # list labels on issue
POST   /repos/{owner}/{repo}/issues/{issue_number}/labels        # add labels
PUT    /repos/{owner}/{repo}/issues/{issue_number}/labels        # replace all labels
DELETE /repos/{owner}/{repo}/issues/{issue_number}/labels/{name} # remove one label
DELETE /repos/{owner}/{repo}/issues/{issue_number}/labels        # remove all labels
```

**POST/PUT body:** `{ "labels": ["bug", "enhancement"] }`
**Remove one response:** Array of remaining label objects
**Remove all response:** 204 No Content

---

## 3. Milestones

```http
GET    /repos/{owner}/{repo}/milestones                          # list
GET    /repos/{owner}/{repo}/milestones/{milestone_number}       # get
POST   /repos/{owner}/{repo}/milestones                          # create
PATCH  /repos/{owner}/{repo}/milestones/{milestone_number}       # update
DELETE /repos/{owner}/{repo}/milestones/{milestone_number}       # delete
```

**List params:** `state` (open/closed/all), `sort` (due_on/completeness), `direction`, `per_page`, `page`

**Create/Update body:**

| Field | Required | Description |
|---|---|---|
| `title` | ✓ (create) | Milestone title |
| `state` | | open / closed |
| `description` | | Markdown description |
| `due_on` | | ISO 8601 timestamp |

**Milestone object:** `id`, `number`, `title`, `description`, `state`, `open_issues`, `closed_issues`, `due_on`, `created_at`, `updated_at`, `closed_at`, `html_url`

**Delete response:** 204 No Content

---

## 4. Issue Comments

```http
GET    /repos/{owner}/{repo}/issues/{issue_number}/comments      # list on issue
GET    /repos/{owner}/{repo}/issues/comments                     # list all repo issue comments
GET    /repos/{owner}/{repo}/issues/comments/{comment_id}        # get one
POST   /repos/{owner}/{repo}/issues/{issue_number}/comments      # create
PATCH  /repos/{owner}/{repo}/issues/comments/{comment_id}        # update
DELETE /repos/{owner}/{repo}/issues/comments/{comment_id}        # delete
```

**List params:** `sort` (created/updated), `direction`, `since`, `per_page`, `page`
**Create/Update body:** `{ "body": "Comment text in **markdown**" }`
**Comment object:** `id`, `body`, `user`, `created_at`, `updated_at`, `reactions`, `html_url`
**Delete response:** 204 No Content

### Reactions on Comments

```http
GET    /repos/{owner}/{repo}/issues/comments/{comment_id}/reactions
POST   /repos/{owner}/{repo}/issues/comments/{comment_id}/reactions
DELETE /repos/{owner}/{repo}/issues/comments/{comment_id}/reactions/{reaction_id}
```

**Reaction content values:** `+1`, `-1`, `laugh`, `confused`, `heart`, `hooray`, `rocket`, `eyes`
**POST body:** `{ "content": "+1" }`

---

## 5. Issue Events and Timeline

```http
GET /repos/{owner}/{repo}/issues/{issue_number}/events     # issue events
GET /repos/{owner}/{repo}/issues/events                    # all repo issue events
GET /repos/{owner}/{repo}/issues/{issue_number}/timeline   # full timeline (events + comments)
GET /repos/{owner}/{repo}/issues/events/{event_id}         # get one event
```

**Common event types:** `labeled`, `unlabeled`, `assigned`, `unassigned`, `milestoned`, `demilestoned`, `renamed` (`rename.from`, `rename.to`), `review_requested`, `review_dismissed`, `locked`, `unlocked`, `closed`, `reopened`, `transferred`, `mentioned`, `subscribed`, `merged`, `head_ref_deleted`, `head_ref_restored`, `referenced`

**Timeline** additionally includes: `commented`, `committed`, `reviewed`, `line-commented`, `cross-referenced`

---

## 6. Pull Requests

### List and Get

```http
GET /repos/{owner}/{repo}/pulls
GET /repos/{owner}/{repo}/pulls/{pull_number}
```

**List params:**

| Param | Values | Default |
|---|---|---|
| `state` | open / closed / all | open |
| `head` | `username:branch` or just `branch` | — |
| `base` | branch name | — |
| `sort` | created / updated / popularity / long-running | created |
| `direction` | asc / desc | desc |
| `per_page` | | 30 |
| `page` | | 1 |

**PR object key fields:** `id`, `number`, `state`, `title`, `body`, `draft`, `user`, `head` (`ref`, `sha`, `repo`, `label`), `base` (`ref`, `sha`, `repo`, `label`), `mergeable` (bool or null — null means not yet calculated), `mergeable_state` (clean/dirty/blocked/behind/unstable/has_hooks/unknown), `merged` (bool), `merge_commit_sha`, `merged_by`, `commits` (count), `additions`, `deletions`, `changed_files`, `labels`, `assignees`, `requested_reviewers`, `requested_teams`, `auto_merge`, `maintainer_can_modify`, `rebaseable`

### Create a Pull Request

```http
POST /repos/{owner}/{repo}/pulls
```

**Body:**

| Field | Required | Description |
|---|---|---|
| `title` | ✓ (unless `issue` set) | PR title |
| `head` | ✓ | Source branch; use `username:branch` for cross-repo |
| `head_repo` | | Required for cross-repo PRs in same org network |
| `base` | ✓ | Target branch |
| `body` | | PR description (markdown) |
| `draft` | | Create as draft PR |
| `maintainer_can_modify` | | Allow maintainers to push |
| `issue` | | Convert existing issue number to PR |

**Response:** 201 — full PR object

### Update a Pull Request

```http
PATCH /repos/{owner}/{repo}/pulls/{pull_number}
```

**Body:** `title`, `body`, `state` (open/closed), `base` (change target branch), `maintainer_can_modify`

### Merge a Pull Request

```http
PUT /repos/{owner}/{repo}/pulls/{pull_number}/merge
```

**Body:**

| Field | Description |
|---|---|
| `merge_method` | `merge` / `squash` / `rebase` |
| `commit_title` | Title for the merge commit |
| `commit_message` | Extra detail for merge commit body |
| `sha` | Expected HEAD SHA (optimistic lock — fails if PR has new commits) |

**Response:** `{ "sha": "<merge-commit-sha>", "merged": true, "message": "Pull Request successfully merged" }`

**Error cases:**
- 405 — PR not mergeable (conflicts)
- 409 — SHA mismatch (head has changed)

### Check if Merged

```http
GET /repos/{owner}/{repo}/pulls/{pull_number}/merge
```
204 = merged; 404 = not merged

### Update Branch

```http
PUT /repos/{owner}/{repo}/pulls/{pull_number}/update-branch
```

Updates PR branch with latest commits from the base branch.
**Body:** `{ "expected_head_sha": "<current-head-sha>" }`
**Response:** 202 — `{ "message": "Updating pull request branch.", "url": "..." }`

### List PR Commits and Files

```http
GET /repos/{owner}/{repo}/pulls/{pull_number}/commits    # max 250 commits
GET /repos/{owner}/{repo}/pulls/{pull_number}/files      # max 3000 files
```

**File response items:** `filename`, `status` (added/removed/modified/renamed/copied/changed/unchanged), `additions`, `deletions`, `changes`, `patch` (unified diff), `previous_filename` (for renames), `blob_url`, `raw_url`, `contents_url`

### Convert Draft ↔ Ready

```http
# Mark ready for review (un-draft)
POST /graphql
{ "query": "mutation { convertPullRequestToDraft(input: {pullRequestId: \"PR_NODE_ID\"}) { pullRequest { isDraft } } }" }

# Mark ready for review
POST /graphql
{ "query": "mutation { markPullRequestReadyForReview(input: {pullRequestId: \"PR_NODE_ID\"}) { pullRequest { isDraft } } }" }
```

Draft PRs can also be managed via REST by updating the PR (setting `draft` on creation only — can't change via PATCH, use GraphQL).

---

## 7. PR Reviews

### List and Get

```http
GET /repos/{owner}/{repo}/pulls/{pull_number}/reviews
GET /repos/{owner}/{repo}/pulls/{pull_number}/reviews/{review_id}
```

**Review object:** `id`, `user`, `body`, `state` (APPROVED/CHANGES_REQUESTED/COMMENTED/PENDING/DISMISSED), `commit_id`, `submitted_at`, `html_url`

### Create a Review

```http
POST /repos/{owner}/{repo}/pulls/{pull_number}/reviews
```

**Body:**

| Field | Required | Description |
|---|---|---|
| `event` | | APPROVE / REQUEST_CHANGES / COMMENT (omit = PENDING) |
| `body` | ✓ for REQUEST_CHANGES/COMMENT | Review summary comment |
| `commit_id` | | Commit to attach review to |
| `comments` | | Array of inline review comments |

**Inline comment object:**
```json
{
  "path": "src/main.py",
  "line": 42,
  "side": "RIGHT",
  "body": "This should handle None case",
  "start_line": 40,
  "start_side": "RIGHT"
}
```

### Submit a Pending Review

```http
POST /repos/{owner}/{repo}/pulls/{pull_number}/reviews/{review_id}/events
```

**Body:** `event` (required: APPROVE/REQUEST_CHANGES/COMMENT), `body`

### Dismiss a Review

```http
PUT /repos/{owner}/{repo}/pulls/{pull_number}/reviews/{review_id}/dismissals
```

**Body:** `message` (required — reason for dismissal), `event`: "DISMISS"

### Update and Delete Pending Review

```http
PUT    /repos/{owner}/{repo}/pulls/{pull_number}/reviews/{review_id}         # update body
DELETE /repos/{owner}/{repo}/pulls/{pull_number}/reviews/{review_id}         # delete (only PENDING)
```

### List Review Comments for a Review

```http
GET /repos/{owner}/{repo}/pulls/{pull_number}/reviews/{review_id}/comments
```

---

## 8. PR Review Comments (Inline)

These are diff-level comments on specific lines of files, separate from issue-style PR comments.

```http
GET    /repos/{owner}/{repo}/pulls/{pull_number}/comments          # list on PR
GET    /repos/{owner}/{repo}/pulls/comments                        # list all repo review comments
GET    /repos/{owner}/{repo}/pulls/comments/{comment_id}           # get one
POST   /repos/{owner}/{repo}/pulls/{pull_number}/comments          # create
POST   /repos/{owner}/{repo}/pulls/{pull_number}/comments/{comment_id}/replies  # reply
PATCH  /repos/{owner}/{repo}/pulls/comments/{comment_id}           # update
DELETE /repos/{owner}/{repo}/pulls/comments/{comment_id}           # delete
```

**Create comment body:**

| Field | Required | Description |
|---|---|---|
| `body` | ✓ | Comment text |
| `commit_id` | ✓ (new comment) | Latest commit SHA in the PR |
| `path` | ✓ (new comment) | Relative file path |
| `line` | | Line number in the diff |
| `side` | | LEFT (deletion) or RIGHT (addition) |
| `start_line` | | For multi-line: first line |
| `start_side` | | LEFT or RIGHT for start line |
| `in_reply_to` | | Reply to existing comment (replaces path/line fields) |
| `subject_type` | | `line` or `file` |

**Reply body:** just `body` (required)

**Comment object:** `id`, `path`, `position`, `line`, `side`, `commit_id`, `original_commit_id`, `body`, `user`, `created_at`, `updated_at`, `reactions`, `in_reply_to_id`, `pull_request_review_id`

---

## 9. Requested Reviewers

```http
GET    /repos/{owner}/{repo}/pulls/{pull_number}/requested_reviewers
POST   /repos/{owner}/{repo}/pulls/{pull_number}/requested_reviewers
DELETE /repos/{owner}/{repo}/pulls/{pull_number}/requested_reviewers
```

**POST/DELETE body:**
```json
{
  "reviewers": ["user1", "user2"],
  "team_reviewers": ["team-slug"]
}
```

**GET response:** `{ "users": [...], "teams": [...] }`
**POST response:** 201 — full PR object; **DELETE response:** 200 — full PR object

---

## 10. Checks API

The Checks API is used to report CI results, test outcomes, and status information on commits.

### Check Runs

```http
POST  /repos/{owner}/{repo}/check-runs                             # create
GET   /repos/{owner}/{repo}/check-runs/{check_run_id}             # get
PATCH /repos/{owner}/{repo}/check-runs/{check_run_id}             # update
GET   /repos/{owner}/{repo}/commits/{ref}/check-runs              # list for commit
GET   /repos/{owner}/{repo}/check-suites/{check_suite_id}/check-runs  # list for suite
```

**Create body:**

| Field | Required | Description |
|---|---|---|
| `name` | ✓ | Check name (shown in UI) |
| `head_sha` | ✓ | Commit SHA |
| `status` | | queued / in_progress / completed |
| `conclusion` | ✓ if completed | action_required / cancelled / failure / neutral / success / skipped / stale / timed_out |
| `started_at` | | ISO 8601 |
| `completed_at` | | ISO 8601 (required if status=completed) |
| `output` | | `{ title, summary, text, annotations[], images[] }` |
| `actions` | | Array of action buttons shown in PR UI |
| `details_url` | | Link to full check details |
| `external_id` | | ID in your system |

**Annotation object:**
```json
{
  "path": "src/main.py",
  "start_line": 10,
  "end_line": 10,
  "annotation_level": "warning",
  "message": "Division by zero possible here",
  "title": "Potential division by zero",
  "raw_details": "..."
}
```
`annotation_level`: `notice`, `warning`, `failure`. Max 50 annotations per request; make multiple PATCH requests for more.

### Check Suites

```http
POST  /repos/{owner}/{repo}/check-suites                           # create (optional; auto-created on push)
GET   /repos/{owner}/{repo}/check-suites/{check_suite_id}         # get
GET   /repos/{owner}/{repo}/commits/{ref}/check-suites            # list for commit
POST  /repos/{owner}/{repo}/check-suites/{check_suite_id}/rerequest  # re-run
PATCH /repos/{owner}/{repo}/check-suites/preferences              # set auto-creation preferences
```

### Commit Statuses (Legacy)

Older alternative to Checks API (still widely used):

```http
POST /repos/{owner}/{repo}/statuses/{sha}                          # create status
GET  /repos/{owner}/{repo}/commits/{ref}/statuses                  # list statuses
GET  /repos/{owner}/{repo}/commits/{ref}/status                    # get combined status
```

**Status body:**
```json
{
  "state": "success",
  "target_url": "https://ci.example.com/build/123",
  "description": "All tests passed",
  "context": "ci/my-pipeline"
}
```

`state` values: `error`, `failure`, `pending`, `success`

**Combined status:** `{ "state": "success/failure/pending", "statuses": [...], "total_count": N }`
