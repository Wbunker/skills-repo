# Jira Search & JQL Reference

## Search Endpoints

| Method | Endpoint | Use when |
|---|---|---|
| `GET` | `/rest/api/3/search/jql` | Short JQL queries (query param) |
| `POST` | `/rest/api/3/search/jql` | Long JQL queries (request body) |
| `GET` | `/rest/api/3/search` | Legacy v2-style endpoint |

### GET search
```
GET /rest/api/3/search/jql
  ?jql=project=PROJ AND status="In Progress"
  &fields=summary,status,assignee,priority
  &maxResults=50
  &startAt=0
  &expand=renderedFields,changelog
```

### POST search (recommended for complex queries)
```http
POST /rest/api/3/search/jql
Content-Type: application/json

{
  "jql": "project = PROJ AND status in ('In Progress', 'Review') AND assignee = currentUser() ORDER BY updated DESC",
  "fields": ["summary", "status", "assignee", "priority", "labels", "fixVersions"],
  "maxResults": 100,
  "startAt": 0,
  "expand": ["renderedFields"]
}
```

**Response:**
```json
{
  "startAt": 0,
  "maxResults": 100,
  "total": 342,
  "issues": [
    {
      "id": "10001",
      "key": "PROJ-42",
      "fields": {
        "summary": "Login fails on Safari",
        "status": { "name": "In Progress" },
        "assignee": { "displayName": "Alice", "accountId": "..." }
      }
    }
  ]
}
```

**Pagination pattern:**
```python
def get_all_issues(jira, jql, fields):
    start = 0
    batch = 100
    all_issues = []
    while True:
        r = jira.post("/rest/api/3/search/jql", json={
            "jql": jql, "fields": fields,
            "startAt": start, "maxResults": batch
        })
        data = r.json()
        all_issues.extend(data["issues"])
        if start + batch >= data["total"]:
            break
        start += batch
    return all_issues
```

> **Important:** Unbounded JQL (no project/date restriction) is rejected by Jira Cloud. Always include at least one limiting clause.

---

## JQL Syntax

### Basic structure
```
field operator value [AND|OR|NOT field operator value] [ORDER BY field [ASC|DESC]]
```

### Operators

| Operator | Meaning | Example |
|---|---|---|
| `=` | Exact match | `status = "Done"` |
| `!=` | Not equal | `status != "Done"` |
| `>` `<` `>=` `<=` | Comparison (numeric/date) | `priority > Medium` |
| `IN` | Match any in list | `status IN ("To Do", "In Progress")` |
| `NOT IN` | Exclude list | `status NOT IN ("Won't Fix", "Duplicate")` |
| `~` | Contains (text search) | `summary ~ "login"` |
| `!~` | Does not contain | `summary !~ "deprecated"` |
| `IS EMPTY` / `IS NULL` | Field has no value | `assignee IS EMPTY` |
| `IS NOT EMPTY` | Field has a value | `fixVersion IS NOT EMPTY` |
| `WAS` | Was in state at some point | `status WAS "In Review"` |
| `WAS IN` | Was in any of the states | `status WAS IN ("Review", "QA")` |
| `WAS NOT` | Was never in state | `status WAS NOT "Done"` |
| `CHANGED` | Field value changed | `status CHANGED AFTER -7d` |
| `CHANGED BY` | Changed by user | `status CHANGED BY currentUser()` |

### Logical keywords
- `AND` — both conditions must be true
- `OR` — either condition
- `NOT` — negation
- `(` `)` — grouping: `(status = "Done" OR status = "Closed") AND project = PROJ`

---

## JQL Fields Reference

### Core issue fields

| Field | Notes |
|---|---|
| `project` | Project key or name: `project = PROJ` |
| `issueType` / `type` | Issue type: `issuetype = Bug` |
| `status` | Workflow status name |
| `priority` | `Highest`, `High`, `Medium`, `Low`, `Lowest` |
| `assignee` | accountId, display name, or `currentUser()`, `EMPTY` |
| `reporter` | Same as assignee |
| `summary` | Text search with `~` operator |
| `description` | Text search with `~` |
| `labels` | `labels = "regression"` |
| `component` | Component name |
| `fixVersion` | Fix version name |
| `affectedVersion` | Affected version name |
| `resolution` | `Fixed`, `Won't Fix`, `Duplicate`, etc. |
| `created` | Creation date |
| `updated` | Last update date |
| `duedate` | Due date |
| `resolutiondate` | When resolved |
| `sprint` | Sprint name or ID |
| `epic link` | Epic key (classic projects) |
| `parent` | Parent issue key |
| `subtask` | `true` or `false` |
| `issuekey` / `key` | Issue key: `issueKey = PROJ-123` |
| `id` | Numeric issue ID |
| `watcher` | `watcher = currentUser()` |
| `comment` | Text in comments: `comment ~ "deployment"` |
| `voter` | Users who voted on issue |

### Date field formats
- Absolute: `created >= "2026-01-01"` or `created >= "2026-01-01 09:00"`
- Relative: `created >= -7d` (last 7 days), `-2w`, `-1h`, `-30m`
- Functions: see Functions section below

---

## JQL Functions

### User functions
| Function | Returns |
|---|---|
| `currentUser()` | Logged-in user's accountId |
| `membersOf("group-name")` | All members of a group |

### Date functions
| Function | Returns |
|---|---|
| `now()` | Current timestamp |
| `startOfDay()` | Midnight today |
| `endOfDay()` | End of today |
| `startOfWeek()` | Start of current week (Monday) |
| `endOfWeek()` | End of current week |
| `startOfMonth()` | First day of current month |
| `endOfMonth()` | Last day of current month |
| `startOfYear()` | January 1 of current year |
| `endOfYear()` | December 31 of current year |

Date functions accept an optional offset: `startOfDay(-1)` = yesterday, `startOfWeek("+1")` = next week start.

### Version functions
| Function | Returns |
|---|---|
| `latestReleasedVersion("PROJ")` | Most recently released version |
| `earliestUnreleasedVersion("PROJ")` | Oldest unreleased version |
| `releasedVersions("PROJ")` | All released versions |
| `unreleasedVersions("PROJ")` | All unreleased versions |

### Sprint functions
| Function | Returns |
|---|---|
| `openSprints()` | All currently open sprints |
| `closedSprints()` | All closed sprints |
| `futureSprints()` | All future sprints |

### History/change functions
| Function | Returns |
|---|---|
| `issueHistory()` | Issues you've recently viewed |
| `linkedIssues("KEY", "link-type")` | Issues linked to KEY with type |
| `watchedIssues()` | Issues you're watching |
| `votedIssues()` | Issues you've voted for |
| `updatedBy(user, date)` | Issues updated by user since date |

---

## Common JQL Queries

### My open issues in a project
```jql
project = PROJ AND assignee = currentUser() AND statusCategory != Done ORDER BY priority DESC
```

### All unresolved bugs in current sprint
```jql
project = PROJ AND issuetype = Bug AND sprint in openSprints() AND resolution = Unresolved
```

### Issues created or updated in last 7 days
```jql
project = PROJ AND (created >= -7d OR updated >= -7d) ORDER BY updated DESC
```

### Overdue issues
```jql
duedate < now() AND statusCategory != Done AND project = PROJ
```

### Issues blocking other issues
```jql
issue in linkedIssues("PROJ-100", "is blocked by")
```

### Epic and all its children
```jql
project = PROJ AND "Epic Link" = PROJ-50 ORDER BY created ASC
```

### Unassigned high-priority issues
```jql
project = PROJ AND assignee IS EMPTY AND priority in (High, Highest) AND statusCategory != Done
```

### Issues changed to Done this week
```jql
project = PROJ AND status CHANGED TO "Done" AFTER startOfWeek()
```

### Text search in summary or description
```jql
project = PROJ AND (summary ~ "payment" OR description ~ "payment") AND statusCategory != Done
```

### Issues with a specific label across all projects
```jql
labels = "security-review" AND statusCategory != Done ORDER BY created DESC
```

### Recently created issues not yet triaged
```jql
project = PROJ AND status = "To Do" AND created >= -3d ORDER BY created DESC
```

---

## Field Filtering (reducing response size)

Request only the fields you need — this reduces response size and cuts points costs:
```
?fields=summary,status,assignee,priority
```

Special values:
- `*all` — return all fields (default)
- `*navigable` — return navigable fields only
- `-description` — return all except description (prefix with `-` to exclude)

---

## Expanding Additional Data

Use `expand` to include extra data not returned by default:

| Expand value | What it adds |
|---|---|
| `renderedFields` | HTML-rendered versions of ADF fields |
| `changelog` | History of field changes |
| `transitions` | Available workflow transitions |
| `operations` | Available UI operations |
| `editmeta` | Editable field metadata |
| `names` | Friendly names for all fields |
| `schema` | Field type schema |

```
GET /rest/api/3/issue/PROJ-123?expand=changelog,transitions
```

---

## Jira Expressions

Jira Expressions are a server-side scripting language (JavaScript-like syntax) for computing dynamic values.

### Evaluate an expression
```http
POST /rest/api/3/expression/eval
{
  "expression": "issue.summary + ' (' + issue.key + ')'",
  "context": {
    "issue": { "key": "PROJ-123" }
  }
}
```

### What expressions can access
- `issue` — current issue entity
- `user` — current user
- `project` — current project
- `sprint`, `board` — agile context
- `issues` — a list of issues (from JQL)
- `new Issue("KEY")` — load any issue by key

### Use cases vs JQL
- **JQL**: filtering and searching — "find all issues matching criteria"
- **Jira Expressions**: computing values, conditional logic, transforming data — "given this issue, compute X"

### Example: count open blockers
```http
POST /rest/api/3/expression/eval
{
  "expression": "issue.links.filter(link => link.type.name == 'Blocks' && link.outwardIssue.status.statusCategory.key != 'done').length",
  "context": { "issue": { "key": "PROJ-123" } }
}
```
