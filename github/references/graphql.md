# GitHub GraphQL API Reference

## Endpoint and Request Format

All requests go to a single endpoint: `POST https://api.github.com/graphql`

| Header | Value |
|--------|-------|
| `Authorization` | `bearer TOKEN` |
| `Content-Type` | `application/json` |
| `X-Github-Next-Global-ID` | `1` (opt-in to new global ID format) |

Request body: `{ "query": "...", "variables": { ... }, "operationName": "Optional" }`

```bash
curl -X POST https://api.github.com/graphql \
  -H "Authorization: bearer $GITHUB_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query": "{ viewer { login } }"}'
```

---

## Rate Limits

GitHub GraphQL uses a **point-based** system (not per-request). Unauthenticated access is not supported.

- **Limit**: 5000 points/hour per authenticated user
- **Cost**: Based on nodes requested — roughly `max(1, ceil(nodes_requested / 100))`. Deeper nesting multiplies cost.

```graphql
query { rateLimit { limit cost remaining resetAt used nodeCount } }
```

`cost` reflects the cost of that specific query. `resetAt` is ISO 8601 UTC.

---

## Pagination

GitHub uses the **Relay cursor connection** pattern.

```graphql
query($cursor: String) {
  repository(owner: "octocat", name: "Hello-World") {
    issues(first: 25, after: $cursor) {
      totalCount
      pageInfo { hasNextPage endCursor hasPreviousPage startCursor }
      nodes { id title }   # prefer nodes over edges unless you need per-edge cursors
    }
  }
}
```

| Argument | Description |
|----------|-------------|
| `first: N` / `after: CURSOR` | Forward pagination |
| `last: N` / `before: CURSOR` | Backward pagination |

Pass `endCursor` as `after` to fetch the next page. Stop when `hasNextPage` is false.

---

## Common Query Patterns

### Repository Metadata
```graphql
query($owner: String!, $name: String!) {
  repository(owner: $owner, name: $name) {
    id nameWithOwner description url isPrivate isFork
    stargazerCount forkCount primaryLanguage { name }
    defaultBranchRef { name } createdAt pushedAt
  }
}
```

### Issues with Labels and Assignees
```graphql
query($owner: String!, $name: String!, $cursor: String) {
  repository(owner: $owner, name: $name) {
    issues(first: 25, after: $cursor, states: [OPEN], orderBy: {field: CREATED_AT, direction: DESC}) {
      pageInfo { hasNextPage endCursor }
      nodes {
        id number title state url createdAt author { login }
        labels(first: 10) { nodes { name color } }
        assignees(first: 5) { nodes { login } }
      }
    }
  }
}
```

### Pull Requests with Review State
```graphql
query($owner: String!, $name: String!, $cursor: String) {
  repository(owner: $owner, name: $name) {
    pullRequests(first: 20, after: $cursor, states: [OPEN]) {
      pageInfo { hasNextPage endCursor }
      nodes {
        id number title state url isDraft headRefName baseRefName reviewDecision
        author { login }
        reviews(first: 10) { nodes { author { login } state submittedAt } }
        reviewRequests(first: 5) {
          nodes { requestedReviewer { ... on User { login } ... on Team { name } } }
        }
      }
    }
  }
}
```

Review `state` values: `APPROVED`, `CHANGES_REQUESTED`, `COMMENTED`, `DISMISSED`, `PENDING`

### User Profile and Repos
```graphql
query($login: String!) {
  user(login: $login) {
    id login name email bio company location avatarUrl createdAt
    repositories(first: 20, ownerAffiliations: [OWNER], orderBy: {field: UPDATED_AT, direction: DESC}) {
      nodes { name isPrivate stargazerCount primaryLanguage { name } }
    }
  }
}
```

### Organization Members and Teams
```graphql
query($org: String!) {
  organization(login: $org) {
    id login name
    membersWithRole(first: 50) { nodes { login name } }
    teams(first: 20) {
      nodes {
        id name slug description
        members(first: 20) { nodes { login } }
        repositories(first: 10) { nodes { name } }
      }
    }
  }
}
```

---

## Common Mutation Patterns

### Create Issue
```graphql
mutation($input: CreateIssueInput!) {
  createIssue(input: $input) { issue { id number url } }
}
```
```json
{ "input": { "repositoryId": "R_kgDO...", "title": "Title", "body": "Body",
             "labelIds": ["LA_kwDO..."], "assigneeIds": ["U_kgDO..."] } }
```

### Add Comment
```graphql
mutation($input: AddCommentInput!) {
  addComment(input: $input) { commentEdge { node { id url } } }
}
```
```json
{ "input": { "subjectId": "I_kwDO...", "body": "Comment text." } }
```

### Close / Reopen Issue
```graphql
mutation($input: CloseIssueInput!)   { closeIssue(input: $input)   { issue { id state } } }
mutation($input: ReopenIssueInput!)  { reopenIssue(input: $input)  { issue { id state } } }
```
Both take `{ "input": { "issueId": "I_kwDO..." } }`

### Add Label to Issue/PR
```graphql
mutation($input: AddLabelsToLabelableInput!) {
  addLabelsToLabelable(input: $input) { labelable { labels(first: 10) { nodes { name } } } }
}
```
```json
{ "input": { "labelableId": "I_kwDO...", "labelIds": ["LA_kwDO..."] } }
```

### Create Pull Request
```graphql
mutation($input: CreatePullRequestInput!) {
  createPullRequest(input: $input) { pullRequest { id number url } }
}
```
```json
{ "input": { "repositoryId": "R_kgDO...", "title": "PR title", "body": "Description",
             "headRefName": "feature-branch", "baseRefName": "main", "draft": false } }
```

### Merge Pull Request
```graphql
mutation($input: MergePullRequestInput!) {
  mergePullRequest(input: $input) { pullRequest { id state mergedAt } }
}
```
```json
{ "input": { "pullRequestId": "PR_kwDO...", "mergeMethod": "SQUASH", "commitHeadline": "Optional title" } }
```
`mergeMethod` options: `MERGE`, `SQUASH`, `REBASE`

### Request Review
```graphql
mutation($input: RequestReviewsInput!) {
  requestReviews(input: $input) {
    pullRequest {
      reviewRequests(first: 5) {
        nodes { requestedReviewer { ... on User { login } ... on Team { name } } }
      }
    }
  }
}
```
```json
{ "input": { "pullRequestId": "PR_kwDO...", "userIds": ["U_kgDO..."], "teamIds": ["T_kgDO..."] } }
```

---

## Fragments

**Named fragment** — reuse field selections:
```graphql
fragment IssueFields on Issue { id number title state createdAt author { login } }

query { repository(owner: "octocat", name: "Hello-World") {
  issues(first: 10) { nodes { ...IssueFields } }
} }
```

**Inline fragment** — type conditions on union/interface fields:
```graphql
query { node(id: "MDQ6VXNlcjE=") {
  ... on User         { login name }
  ... on Organization { login description }
} }
```

Common interfaces: `Actor` (User, Bot, Organization), `Assignable`, `Closable`, `Labelable`, `Reactable`.

---

## Variables

Declare variables in the operation signature with their GraphQL types:

```graphql
query GetRepo($owner: String!, $name: String!, $first: Int = 10) {
  repository(owner: $owner, name: $name) {
    issues(first: $first) { nodes { title } }
  }
}
```

Pass variables in the request body under `"variables"`. Type syntax: `String!` (non-null), `Int`, `Boolean`, `ID!`, `CreateIssueInput!`.

---

## Introspection

```graphql
# List all types
query { __schema { types { name kind description } } }

# Inspect a specific type
query { __type(name: "Issue") { name fields { name description type { name kind ofType { name kind } } } } }

# Available mutations
query { __schema { mutationType { fields { name description args { name type { name kind } } } } } }
```

---

## Node IDs

Every GitHub object has a globally unique **Node ID** usable in GraphQL mutations and the `node()` / `nodes()` root queries.

**From REST**: All REST responses include `node_id` — use it directly as the GraphQL `id`.

```graphql
# Fetch any object by its Node ID
query { node(id: "R_kgDOABCDEF") { ... on Repository { name nameWithOwner } } }

# Bulk fetch
query { nodes(ids: ["R_kgDO...", "I_kwDO..."]) { id ... on Issue { title } } }
```

**Common ID prefixes** (Node IDs are opaque — do not construct them manually):

| Prefix | Type |
|--------|------|
| `R_` | Repository |
| `I_` | Issue |
| `PR_` | PullRequest |
| `U_` | User |
| `O_` | Organization |
| `T_` | Team |
| `LA_` | Label |
| `RC_` | IssueComment |

---

## Error Handling

GraphQL always returns **HTTP 200**. Check the response body:

```json
{
  "data": { "repository": null },
  "errors": [{ "message": "Could not resolve to a Repository with the name 'missing'.",
               "locations": [{"line": 2, "column": 3}], "path": ["repository"], "type": "NOT_FOUND" }]
}
```

`data` and `errors` can both be non-null (partial success). Fields that errored appear as `null` in `data`; `path` indicates which field failed.

| Error type | Meaning |
|------------|---------|
| `NOT_FOUND` | Resource absent or not visible |
| `FORBIDDEN` | Insufficient permission |
| `MAX_NODE_LIMIT_EXCEEDED` | Query exceeds node limit (~500,000) |
| `RATE_LIMITED` | Point budget exhausted |
| `UNPROCESSABLE` | Invalid mutation input |
| `SERVICE_UNAVAILABLE` | GitHub-side error |

---

## GitHub-Specific Scalars

| Scalar | Description | Example |
|--------|-------------|---------|
| `URI` | Absolute URI string | `"https://github.com/octocat"` |
| `DateTime` | ISO 8601 UTC timestamp | `"2024-01-15T10:30:00Z"` |
| `HTML` | Rendered HTML string | `"<p>Hello</p>"` |
| `GitObjectID` | 40-char SHA-1 hex | `"abc123def456..."` |
| `Date` | ISO 8601 date (no time) | `"2024-01-15"` |
| `Base64String` | Base64-encoded string | Used for blob content |

---

## Key GitHub GraphQL Types

| Type | Key Fields |
|------|------------|
| `Repository` | `id`, `name`, `owner`, `issues`, `pullRequests`, `refs`, `defaultBranchRef`, `labels` |
| `Issue` | `id`, `number`, `title`, `body`, `state`, `labels`, `assignees`, `comments`, `closedAt` |
| `PullRequest` | `id`, `number`, `headRefName`, `baseRefName`, `reviewDecision`, `commits`, `files`, `isDraft` |
| `User` | `id`, `login`, `name`, `email`, `repositories`, `organizations`, `contributionsCollection` |
| `Organization` | `id`, `login`, `members`, `teams`, `repositories`, `samlIdentityProvider` |
| `Team` | `id`, `name`, `slug`, `members`, `repositories`, `parentTeam`, `childTeams` |
| `Commit` | `oid`, `message`, `author`, `committedDate`, `parents`, `status`, `tree` |
| `Ref` | `id`, `name`, `prefix`, `target` (→ `Commit` via `... on Commit`) |

---

## Explorer and Schema Discovery

- **GitHub GraphQL Explorer**: https://docs.github.com/en/graphql/overview/explorer — browser IDE with your GitHub session, full autocomplete and inline docs.
- **Schema reference**: https://docs.github.com/en/graphql/reference
- **GitHub CLI**:
```bash
gh api graphql -f query='{ viewer { login } }'
gh api graphql -F owner=octocat -F name=Hello-World \
  -f query='query($owner:String!,$name:String!){ repository(owner:$owner,name:$name){ stargazerCount } }'
```
