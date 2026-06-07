# Dynamic Workflows

A **dynamic workflow** is a JavaScript orchestration script that Claude Code writes for a task you
describe, then runs in the background — coordinating tens to hundreds of [subagents](claude-code.md)
across phases, cross-checking their work, and returning one finished result. The plan lives **in
code**, not in the conversation: intermediate results stay in script variables, so your context
holds only the final answer and the run scales past what one conversation could coordinate.

Research preview. Requires **Claude Code v2.1.154+**; available on all paid plans, the Anthropic
API, and Bedrock / Vertex / Foundry. On Pro, enable it from the **Dynamic workflows** row in
`/config`.

Docs: https://code.claude.com/docs/en/workflows · Announcement: https://claude.com/blog/introducing-dynamic-workflows-in-claude-code

## Table of Contents

- [When to use a workflow](#when-to-use-a-workflow)
- [Triggering a workflow](#triggering-a-workflow)
- [Approval before it runs](#approval-before-it-runs)
- [The `/workflows` TUI](#the-workflows-tui)
- [Save & reuse](#save--reuse)
- [How it runs, limits & permissions](#how-it-runs-limits--permissions)
- [Authoring & editing the script](#authoring--editing-the-script)
- [Cost control](#cost-control)
- [Turning workflows off](#turning-workflows-off)
- [Gotchas](#gotchas)

## When to use a workflow

Subagents, skills, agent teams, and workflows all run multi-step work; the difference is **who
holds the plan**.

| | Subagents | Skills | Agent teams | Workflows |
|---|---|---|---|---|
| What it is | A worker Claude spawns | Instructions Claude follows | A lead supervising peer sessions | A script the runtime executes |
| Who decides what runs next | Claude, turn by turn | Claude, per prompt | The lead, turn by turn | **The script** |
| Intermediate results live in | Context window | Context window | A shared task list | **Script variables** |
| What's repeatable | The worker def | The instructions | The team def | **The orchestration itself** |
| Scale | A few per turn | Same | A handful of peers | **Dozens–hundreds per run** |

Reach for a workflow when a task needs **more agents than one conversation can coordinate**, or
when you want the orchestration **codified as a readable, rerunnable script**: codebase-wide bug
sweeps, 500-file migrations, research questions whose sources must be cross-checked, or a hard plan
worth drafting from several independent angles before committing. The payoff beyond scale is a
**repeatable quality pattern** — e.g. independent agents *adversarially review* each other's
findings, and the script doesn't deliver until results converge.

Don't use one for small tasks: if the work doesn't have ~3+ independent subtasks that benefit from
cross-verification, a single conversation or a plain subagent is faster and cheaper.

## Triggering a workflow

Three ways:

1. **Keyword `ultracode` in your prompt** — run a single task as a workflow without changing the
   session's effort level:
   ```text
   ultracode: audit every API endpoint under src/routes/ for missing auth checks
   ```
   Natural-language requests ("use a workflow", "run a workflow") work too. *(Before v2.1.160 the
   literal keyword was `workflow`; natural language works in both versions.)* Dismiss an
   unintended highlight with `Option/Alt+W`, or backspace right after the keyword.
2. **`/effort ultracode`** — session-wide autonomous mode: `xhigh` reasoning **+** automatic
   orchestration. Claude decides when each substantive task warrants a workflow (a single request
   may become several workflows: understand → change → verify). Session-scoped; resets on a new
   session; drop back with `/effort high`. Only on models that support `xhigh` (Opus 4.8 / 4.7).
3. **Run an existing workflow command** — the bundled `/deep-research <question>` (needs the
   WebSearch tool), or one you [saved](#save--reuse). Saved workflows appear in `/` autocomplete.

## Approval before it runs

The launch prompt shows the planned phases. `Ctrl+G` opens the script in your editor; `Tab` lets
you adjust the prompt first. Options: **Yes, run it** · **Yes, and don't ask again for `<name>` in
`<path>`** · **View raw script** · **No**.

| Permission mode | When prompted |
|---|---|
| Default / accept edits | Every run, unless you chose "don't ask again" for that workflow in this project |
| Auto | First launch only; **Yes** records consent in user settings. Skipped entirely when ultracode is on |
| Bypass permissions, `claude -p`, Agent SDK | Never — the run starts immediately |

## The `/workflows` TUI

Run `/workflows` to list running/completed runs; Enter opens the progress view (phases with agent
counts, token totals, elapsed time). A one-line summary also appears in the task panel below the
input box.

| Key | Action |
|---|---|
| `↑`/`↓` | Select phase or agent |
| `Enter`/`→` | Drill into phase, then agent (its prompt, recent tool calls, result) |
| `Esc` | Back out one level |
| `j`/`k` | Scroll within agent detail |
| `p` | **Pause / resume** the run |
| `x` | Stop the selected agent, or the whole workflow when focus is on the run |
| `r` | Restart the selected running agent |
| `s` | **Save** the run's script as a command |

## Save & reuse

When a run did what you wanted: `/workflows` → select → `s`. In the save dialog, `Tab` toggles the
location, Enter saves:

- `.claude/workflows/` (project) — shared with everyone who clones the repo.
- `~/.claude/workflows/` (home) — available in every project, just for you.

It then runs as `/<name>` in future sessions. On a name clash, the **project** workflow wins. This
turns "how we audit the API layer" into a version-controlled, auditable, executable playbook
instead of tribal knowledge.

**Pass input** via the `args` global: `Run /triage-issues on issues 1024, 1025, 1030` — Claude
passes the list as structured data the script can use directly (`args` is `undefined` if omitted).

## How it runs, limits & permissions

- **Isolated runtime**, separate from your conversation; intermediate results stay in script
  variables. The script is written to a file under `~/.claude/projects/<session>/` — ask Claude
  for the path to read, diff, or edit it and relaunch from the edited version.
- **Limits:** up to **16 concurrent agents** (fewer on limited-CPU machines); **1,000 agents total
  per run** (runaway backstop).
- **No mid-run user input** — only agent permission prompts can pause a run. For sign-off between
  stages, run each stage as its own workflow.
- **The script has no direct filesystem/shell access** — only the agents read/write/run; the
  script just coordinates them.
- **Permissions:** spawned subagents **always run in `acceptEdits` mode and inherit your tool
  allowlist, regardless of your session's permission mode — file edits are auto-approved.** Know
  what you're authorizing before a migration that rewrites hundreds of files. Non-allowlisted
  shell/web/MCP calls can still prompt mid-run; pre-add what agents need to the allowlist for long
  unattended runs.

## Authoring & editing the script

The script is plain JavaScript run in an async context by the workflow runtime. You rarely write
one from scratch — Claude generates it — but you read it before approving, and edit it to refine a
run (then relaunch from the edited file). The public docs cover *usage*; the primitives below are
the runtime's scripting contract.

**Required `meta` header** — must be the first statement and a **pure literal** (no variables,
calls, or interpolation):

```javascript
export const meta = {
  name: 'find-flaky-tests',
  description: 'Find flaky tests and propose fixes',   // shown in the approval dialog
  phases: [                                            // one entry per phase() call; titles matched exactly
    { title: 'Scan', detail: 'grep CI logs for retry markers' },
    { title: 'Fix',  detail: 'one agent per flaky test' },
  ],
}
// body follows
```

`name` + `description` are required; `whenToUse`, `phases`, and `model` are optional. Add `model`
to a phase entry when that phase overrides the model.

**Body primitives:**

| Hook | Purpose |
|---|---|
| `agent(prompt, opts?)` | Spawn one subagent. Returns its final text (string). With `opts.schema` (a JSON Schema) it's forced to emit structured output and returns the **validated object**. `opts`: `label`, `phase`, `schema`, `model`, `agentType` (custom subagent type, e.g. `'Explore'`), `isolation:'worktree'` (only when agents mutate files in parallel — expensive). Returns `null` if the user skips it — `.filter(Boolean)`. |
| `pipeline(items, s1, s2, …)` | **Default for multi-stage work.** Each item flows through all stages independently — **no barrier**; item A can be in stage 3 while B is in stage 1. Each stage gets `(prevResult, originalItem, index)`. A throwing stage drops that item to `null`. Wall-clock = slowest single chain. |
| `parallel(thunks)` | Run thunks concurrently, **awaiting all (a barrier)**. A throwing thunk → `null` (the call never rejects; `.filter(Boolean)`). Use **only** when stage N genuinely needs *all* of stage N-1 (dedup/merge across the full set, early-exit on zero, cross-item comparison). |
| `phase(title)` | Start a phase; subsequent `agent()` calls group under it. Inside `pipeline`/`parallel` stages pass `opts.phase` instead, to avoid racing the global state. |
| `log(message)` | Emit a narrator line to the user. `log()` anything you silently cap (top-N, no-retry) — silent truncation reads as full coverage. |
| `args` | The `args` input value passed at invocation, verbatim (`undefined` if none). |
| `budget` | `{ total, spent(), remaining() }` — token target from a `+500k`-style directive (`total` is `null` if unset; `remaining()` is `Infinity` then). Scale fleet size or loop depth to it; guard loops on `budget.total` or they run to the 1,000-agent cap. |
| `workflow(nameOrRef, args?)` | Run another saved workflow (or `{scriptPath}`) inline as a sub-step. One level of nesting only. |

**Structured output:** pass `schema` so validation happens at the tool-call layer (the model
retries on mismatch) and `agent()` returns a typed object — no parsing. Prefer this over free text
whenever a later stage consumes the result.

**The pipeline-vs-parallel rule of thumb:** reach for `pipeline()` by default. A barrier
(`parallel`) is justified only when stage N needs cross-item context from *all* of stage N-1 —
not merely to flatten/map/filter (do that inside a stage) or because the stages feel separate.

**Canonical pattern — review each dimension, adversarially verify each finding as soon as it's found:**

```javascript
const results = await pipeline(
  DIMENSIONS,
  d => agent(d.prompt, { label: `review:${d.key}`, phase: 'Review', schema: FINDINGS_SCHEMA }),
  review => parallel(review.findings.map(f => () =>
    agent(`Adversarially verify, default to refuted if uncertain: ${f.title}`,
          { label: `verify:${f.file}`, phase: 'Verify', schema: VERDICT_SCHEMA })
      .then(v => ({ ...f, verdict: v }))))
)
const confirmed = results.flat().filter(Boolean).filter(f => f.verdict?.isReal)
return confirmed
```

**Constraints to respect when editing:**

- Plain **JavaScript, not TypeScript** — no type annotations/interfaces/generics.
- **No `Date.now()` / `Math.random()` / argless `new Date()`** (they'd break resume) — pass
  timestamps via `args`, vary randomness by index. No filesystem/Node APIs.
- Concurrency cap **min(16, cores−2)**; lifetime cap **1,000 agents/run**. You can still pass 100s
  of items to `pipeline`/`parallel` — excess queue.

**Resume / iterate:** every run persists its script under `~/.claude/projects/<session>/`. Edit
that file and relaunch with `{ scriptPath, resumeFromRunId }` — the longest unchanged prefix of
`agent()` calls returns cached results instantly; the first changed call onward runs live. Same
script + same args → 100% cache hit.

## Cost control

A run spawns many agents, so it can use **meaningfully more tokens** than doing the same work
conversationally; it counts toward plan usage and rate limits.

- **Scope small first** — one directory, not the whole repo; a narrow question, not a broad one.
  The `/workflows` view shows per-agent token usage live, and you can stop without losing completed
  work.
- Every agent uses **your session's model** unless the script routes a stage elsewhere. Check
  `/model` before a large run, and ask Claude to use a smaller model for stages that don't need the
  strongest one.

## Turning workflows off

`/config` toggle · `"disableWorkflows": true` in `~/.claude/settings.json` ·
`CLAUDE_CODE_DISABLE_WORKFLOWS=1` (read at startup). Org-wide: `"disableWorkflows": true` in
managed settings. When off, bundled workflow commands are unavailable and `ultracode` no longer
triggers a run or appears in `/effort`.

## Gotchas

- **Subagents run `acceptEdits` regardless of session mode** — the single most surprising
  behavior. A "read-only" expectation doesn't hold; file edits are auto-approved.
- **No mid-run steering** — you can pause/save/stop, but can't redirect agents while they work
  ("skip Module C"). If the task needs frequent human judgment calls, use plain subagents.
- **Execution state is session-bound** — resume works *within* the session (completed agents return
  cached results); **exit Claude Code and the run restarts fresh** next session. The saved *script*
  persists; the *execution state* does not.
- **Not for small tasks** — without ~3+ cross-verifiable subtasks, a workflow is slower and pricier
  than a conversation.
- **`ultracode` needs an `xhigh`-capable model** (Opus 4.8 / 4.7); the `/effort` menu hides it
  otherwise.
- **Proof point:** Bun's Zig→Rust port used dynamic workflows — ~750k lines of Rust, 99.8% of the
  test suite passing, in ~11 days, via lifetime-mapping → parallel file conversion with two
  independent reviewers per file → an overnight copy-elimination pass. (Anthropic's figures;
  research-preview, pre-production.)
