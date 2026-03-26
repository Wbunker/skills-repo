# Jira Agile Reference (Boards, Sprints, Backlogs)

Base URL for Jira Software API: `https://your-domain.atlassian.net/rest/agile/1.0/`

This is a separate API from the platform REST API (`/rest/api/3/`). Both are needed for full Jira Software workflows.

---

## Boards

| Operation | Method | Path |
|---|---|---|
| List all boards | GET | `/rest/agile/1.0/board` |
| Get board | GET | `/rest/agile/1.0/board/{boardId}` |
| Create board | POST | `/rest/agile/1.0/board` |
| Delete board | DELETE | `/rest/agile/1.0/board/{boardId}` |
| Get board configuration | GET | `/rest/agile/1.0/board/{boardId}/configuration` |
| Get issues on board | GET | `/rest/agile/1.0/board/{boardId}/issue` |
| Get backlog issues | GET | `/rest/agile/1.0/board/{boardId}/backlog` |
| Get epics on board | GET | `/rest/agile/1.0/board/{boardId}/epic` |

### List boards
```
GET /rest/agile/1.0/board?type=scrum&projectKeyOrId=PROJ&maxResults=50&startAt=0
```

`type` filter: `scrum`, `kanban`, `simple`

### Get board configuration
```
GET /rest/agile/1.0/board/{boardId}/configuration
```
Returns columns, swimlanes, card layout, and ranking configuration.

### Get all issues on a board (including all sprints)
```
GET /rest/agile/1.0/board/{boardId}/issue?maxResults=100&startAt=0&jql=status!="Done"
```

---

## Sprints

| Operation | Method | Path |
|---|---|---|
| List sprints for board | GET | `/rest/agile/1.0/board/{boardId}/sprint` |
| Get sprint | GET | `/rest/agile/1.0/sprint/{sprintId}` |
| Create sprint | POST | `/rest/agile/1.0/sprint` |
| Update sprint | PUT | `/rest/agile/1.0/sprint/{sprintId}` |
| Delete sprint | DELETE | `/rest/agile/1.0/sprint/{sprintId}` |
| Start sprint | PUT | `/rest/agile/1.0/sprint/{sprintId}` |
| Complete sprint | PUT | `/rest/agile/1.0/sprint/{sprintId}` |
| Get sprint issues | GET | `/rest/agile/1.0/sprint/{sprintId}/issue` |
| Move issues to sprint | POST | `/rest/agile/1.0/sprint/{sprintId}/issue` |
| Swap sprint | POST | `/rest/agile/1.0/sprint/swap` |

### List sprints for a board
```
GET /rest/agile/1.0/board/{boardId}/sprint?state=active,future&maxResults=50
```

`state` filter: `active`, `closed`, `future` (comma-separated for multiple)

### Create a sprint
```http
POST /rest/agile/1.0/sprint
{
  "name": "Sprint 7",
  "startDate": "2026-04-01T09:00:00.000Z",
  "endDate": "2026-04-14T17:00:00.000Z",
  "goal": "Complete authentication module",
  "originBoardId": 42
}
```

### Start a sprint
```http
PUT /rest/agile/1.0/sprint/{sprintId}
{
  "state": "active",
  "startDate": "2026-04-01T09:00:00.000Z",
  "endDate": "2026-04-14T17:00:00.000Z"
}
```

### Complete a sprint (move incomplete issues to backlog or next sprint)
```http
PUT /rest/agile/1.0/sprint/{sprintId}
{
  "state": "closed",
  "completeDate": "2026-04-14T17:00:00.000Z"
}
```

Incomplete issues are moved to the backlog automatically. Use `POST /sprint/{nextId}/issue` to move them to the next sprint instead.

### Get issues in a sprint
```
GET /rest/agile/1.0/sprint/{sprintId}/issue?maxResults=100&jql=status!="Done"
```

### Move issues into a sprint
```http
POST /rest/agile/1.0/sprint/{sprintId}/issue
{
  "issues": ["PROJ-1", "PROJ-2", "PROJ-3"]
}
```

### Find active sprint for a project (JQL)
```jql
project = PROJ AND sprint in openSprints()
```
Or via API:
```
GET /rest/agile/1.0/board/{boardId}/sprint?state=active
```

---

## Backlog

### Get backlog issues
```
GET /rest/agile/1.0/board/{boardId}/backlog
  ?maxResults=100
  &startAt=0
  &jql=issuetype != Epic
```

### Move issues to backlog (remove from sprint)
```http
POST /rest/agile/1.0/backlog/issue
{
  "issues": ["PROJ-10", "PROJ-11"]
}
```

---

## Epics

### Get epics for a board
```
GET /rest/agile/1.0/board/{boardId}/epic?done=false&maxResults=50
```

### Get issues for an epic
```
GET /rest/agile/1.0/epic/{epicId}/issue
```

### Move issues into an epic
```http
POST /rest/agile/1.0/epic/{epicId}/issue
{
  "issues": ["PROJ-5", "PROJ-6"]
}
```

### Remove issues from epic
```http
POST /rest/agile/1.0/epic/none/issue
{
  "issues": ["PROJ-5"]
}
```

---

## Issue Ranking

Ranking determines order within backlog and sprint boards.

### Rank issue before another
```http
PUT /rest/agile/1.0/issue/rank
{
  "issues": ["PROJ-10"],
  "rankBeforeIssue": "PROJ-5"
}
```

### Rank issue after another
```http
PUT /rest/agile/1.0/issue/rank
{
  "issues": ["PROJ-10"],
  "rankAfterIssue": "PROJ-5"
}
```

Ranking requires the `rank` field to be enabled on the board configuration.

---

## Scrum vs Kanban Board Differences

| Feature | Scrum | Kanban |
|---|---|---|
| Sprints | Yes — time-boxed iterations | No |
| Backlog | Visible, sprint-based | Continuous flow |
| Velocity tracking | Yes | No |
| WIP limits | No (optional plugins) | Yes (native) |
| `state` filter on sprints | `active`, `closed`, `future` | N/A |
| Backlog API | `/board/{id}/backlog` | `/board/{id}/issue` |

---

## Velocity Reports (Scrum boards)

```
GET /rest/agile/1.0/rapid/charts/velocity?rapidViewId={boardId}
```

Returns completed story points per sprint for the board.

---

## Common Agile JQL Patterns

```jql
# All issues in active sprint
project = PROJ AND sprint in openSprints()

# Unfinished work from closed sprints (spillover)
project = PROJ AND sprint in closedSprints() AND statusCategory != Done

# Issues in a specific sprint by name
project = PROJ AND sprint = "Sprint 7"

# Epics not yet done
project = PROJ AND issuetype = Epic AND statusCategory != Done

# Stories without story points
project = PROJ AND issuetype = Story AND "Story Points" is EMPTY AND sprint in openSprints()

# Issues added to sprint after it started (scope creep)
project = PROJ AND sprint = "Sprint 7" AND sprint CHANGED AFTER "2026-04-01"
```

---

## Getting Board ID from Project Key

Boards aren't directly linked to project keys in the API — use this pattern:
```
GET /rest/agile/1.0/board?projectKeyOrId=PROJ
```
Returns boards associated with the project. A project can have multiple boards.
