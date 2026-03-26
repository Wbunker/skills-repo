# Command Patterns

Common command archetypes with real examples from this project.

## Pattern 1: Simple Workflow Command

For step-by-step tasks with no side effects. Auto-triggered by Claude is fine.

```markdown
---
description: <what it does and when to use it>
---

## User Input

\`\`\`text
$ARGUMENTS
\`\`\`

## Steps

1. ...
2. ...
```

**Example**: `next-issue.md` — grabs the oldest open GitHub issue and triages it.

---

## Pattern 2: Side-Effect Command (User-Invoked Only)

For commands that commit, push, deploy, delete, or modify external state. Always add
`disable-model-invocation: true` so Claude never runs it automatically.

```markdown
---
description: <what it does>
disable-model-invocation: true
allowed-tools: Bash, Read
---

1. Run `git status` to check...
2. If on main, stop and tell the user...
3. ...
```

**Example**: `ship-it.md` — commits, pushes, gets Vercel URL, labels GitHub issue.

---

## Pattern 3: Argument-Driven Command

For commands that take a meaningful argument affecting behavior. Use `argument-hint` and
read `$ARGUMENTS` explicitly at the start.

```markdown
---
description: <what it does>
argument-hint: [value1|value2|all]
disable-model-invocation: true
allowed-tools: Glob, Grep, Agent, Read
---

## Step 1 — Parse argument

Read `$ARGUMENTS`. Valid values: `value1`, `value2`, `all`.
If empty or unrecognized, default to `all`.
Store as TARGET.

## Step 2 — ...
```

**Example**: `squash-css.md` — takes `[colors|inputs|buttons|spacing|all]`.

---

## Pattern 4: Orchestrator Command

Dispatches multiple background agents, collects results. Keeps the orchestrator from
touching files directly — it delegates exclusively.

```markdown
---
description: <what it does>
disable-model-invocation: true
allowed-tools: Glob, Grep, Agent, Read
---

## Step 1 — Discover targets

Find all files matching `app/**/*.tsx`.

## Step 2 — Print task list

Output the full list before dispatching:
\`\`\`
Found <N> files:
  [ ] path/to/file.tsx
  ...
Dispatching <N> background agents...
\`\`\`

## Step 3 — Dispatch one agent per file

For each file, spawn a `<agent-name>` agent in the background with this prompt:
> Do X to `<FILE>`. Report back ONLY: `DONE: <FILE> — <N> fixes`

Dispatch all agents before waiting for any.

## Step 4 — Collect results

Wait for all agents. Output final summary when done.

## Constraints

- Never fix files yourself. Delegate everything.
- Only request the single DONE: line from agents — preserve context window.
```

**Example**: `squash-css.md` — dispatches one `css-bug-squasher` per tsx file.

---

## Pattern 5: Multi-Step Workflow with Handoffs

For commands that are part of a sequence. `handoffs` add clickable next-step buttons
after the command finishes.

```markdown
---
description: <what this step does>
handoffs:
  - label: Next Step Name
    agent: namespace.next-command
    prompt: Pre-filled prompt for next step
  - label: Alternative Step
    agent: namespace.alt-command
    prompt: Pre-filled prompt
    send: true   # auto-send without user confirmation
---

## User Input

\`\`\`text
$ARGUMENTS
\`\`\`

## Outline

1. ...
2. ...
```

**Example**: `speckit/specify.md` → handoffs to `speckit.plan` or `speckit.clarify`.

---

## Pattern 6: Forked / Isolated Command

Runs in an isolated subagent context with no conversation history. Good for research or
analysis that could bloat the main context.

```markdown
---
description: <what it does>
context: fork
agent: Explore
allowed-tools: Bash(gh *)
---

## Context (injected before Claude runs)

- Current diff: !`gh pr diff`
- Recent commits: !`git log --oneline -10`

## Your task

Analyze the above and...
```

**Use `!` backtick syntax** to inject shell output at load time — Claude sees the final
values, not the shell commands.

---

## Pattern 7: Nested / Namespaced Command

For grouping related commands under a namespace. Create a subdirectory:

```
.claude/commands/
  speckit/
    specify.md     → /speckit:specify
    plan.md        → /speckit:plan
    tasks.md       → /speckit:tasks
```

Or with skills:
```
.claude/skills/
  speckit:specify/
    SKILL.md       → /speckit:specify
```

Namespace separator is `:` in the slash command, `/` in the file path.

---

## Anti-Patterns to Avoid

- **No `disable-model-invocation` on side-effect commands** — Claude may auto-run `/deploy` at the wrong time
- **Vague description** — "Does stuff" won't trigger or not trigger correctly; be specific about when to use it
- **Putting the body content before frontmatter is parsed** — body is loaded after trigger; "When to Use" sections in the body are useless for triggering
- **Overcrowded `allowed-tools`** — list only what the command actually needs; extra tools add permission surface
- **Forgetting `$ARGUMENTS` handling** — if the command takes args, always read them at step 1 and handle empty/invalid gracefully
