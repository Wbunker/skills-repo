# Agent Patterns

## Pattern 1: Simple auto-delegated agent

The most common pattern. A command or conversation calls the Agent tool without `subagent_type`; Claude matches the prompt to the best available agent by description.

```markdown
---
name: repo-analyzer
description: Analyzes a single GitHub repo and writes a brief to repo-briefs/<repo-name>.md. Use when analyzing any repo in the org.
tools: Bash, Read, Write, Glob, Grep
model: sonnet
permissionMode: acceptEdits
---

You are a repo analyst. Input is a repo name.
1. Clone the repo
2. Read key files
3. Write repo-briefs/<repo-name>.md with findings
4. Output: DONE: <repo> — <summary>
```

**Dispatch from command:**
```markdown
For each repo:
- Use the Agent tool with prompt: "Analyze repo: <repo-name>"
  (Claude routes to repo-analyzer based on description match)
```

---

## Pattern 2: Background agent with pre-approved permissions

For fire-and-forget parallel work. The agent cannot ask questions or request permissions mid-run — all permissions must be pre-approved.

```markdown
---
name: data-processor
description: Processes a single data file and writes output. Use when batch-processing files.
tools: Bash, Read, Write
model: haiku
permissionMode: acceptEdits   # REQUIRED for background agents that write files
background: true
---
```

**Key rules for background agents:**
- Always set `permissionMode: acceptEdits` or `bypassPermissions`
- Write all output to files, not stdout (background agents' stdout is not shown)
- Return a structured completion line the orchestrator can parse (e.g. `DONE: <item> — <summary>`)
- Do not prompt for user input — the agent runs unattended

---

## Pattern 3: Worktree-isolated agent

Gives the agent its own clean git checkout. Safe for agents that make experimental changes. Auto-cleaned if no changes committed.

```markdown
---
name: refactoring-agent
description: Experimental refactoring agent. Runs in an isolated git worktree.
tools: Read, Edit, Bash, Write
model: sonnet
isolation: worktree
permissionMode: acceptEdits
---
```

The worktree path and branch are returned if the agent commits changes; otherwise the worktree is auto-deleted.

---

## Pattern 4: Orchestrator agent (main thread only)

**Only works when the agent is launched as the main thread via `claude --agent my-orchestrator`.** Not usable from commands or when dispatched as a subagent.

```markdown
---
name: my-orchestrator
description: Orchestrates parallel worker agents.
tools: Agent(worker-a, worker-b), Read, Bash
model: sonnet
---

Dispatch worker-a and worker-b in parallel for each item in the list.
```

The `Agent(worker-a, worker-b)` tools syntax restricts which named agents this orchestrator can spawn. Without it, the agent can spawn any available agent.

**Experimental parallel dispatch:** Set `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` for true parallel named-agent dispatch from an orchestrator.

---

## Pattern 5: Command-based parallel orchestration (TaskCreate)

The correct pattern when a **command** (not an agent) needs to dispatch work to multiple agents in parallel. Since subagents cannot spawn subagents, commands own all dispatch.

```markdown
# In the command:

### 5. Dispatch agents in batches of 8

For each batch of repos:
1. Use TaskCreate to track each unit of work
2. Dispatch via Agent tool (auto-delegation — no subagent_type):
   ```
   Agent(prompt="Analyze repo billing/<repo-name> and write pass-2 report")
   ```
   Pass `run_in_background: true` for parallel execution
3. Wait for all agents in the batch to complete
4. Parse result lines (DONE/SKIP/ERROR)
5. Use TaskUpdate to mark each complete
6. Commit progress tracking file
```

**Why batches?** Running all agents simultaneously can exhaust context. Batches of 8 balance parallelism and stability.

---

## Pattern 6: Agent with persistent memory

Use for agents that should accumulate domain knowledge across sessions.

```markdown
---
name: debugging-specialist
description: Expert debugger. Use proactively when errors, test failures, or unexpected behavior occur.
tools: Read, Edit, Bash, Grep, Glob
model: sonnet
memory: project   # stored in .claude/agent-memory/debugging-specialist/
---

Check your memory for known patterns before starting.
After fixing: update your memory with root cause and fix pattern.
```

Memory scopes:
- `user` — `~/.claude/agent-memory/<name>/` — shared across all projects
- `project` — `.claude/agent-memory/<name>/` — project-specific, git-committable
- `local` — `.claude/agent-memory-local/<name>/` — project-specific, not committed

---

## Pattern 7: Skills preloading

Agents do NOT inherit skills from the parent conversation. Explicitly list skills to inject at startup.

```markdown
---
name: billing-analyst
description: Analyzes billing domain repos.
skills:
  - domain-context-builder   # full SKILL.md injected at agent startup
  - curantis-codebase
---
```

The full skill content is injected — not just made available for invocation. Keep preloaded skills concise to avoid bloating the agent's context window.

---

## Common mistakes

| Mistake | Fix |
|---------|-----|
| `subagent_type: "my-agent"` | Remove `subagent_type`; rely on description matching |
| Subagent tries to spawn subagents | Move all dispatch up to the command/orchestrator |
| `Agent(worker)` in a dispatched agent | Only valid for main-thread agents (`claude --agent`) |
| Background agent asks for permissions | Set `permissionMode: acceptEdits` or `bypassPermissions` |
| Agent inherits parent skills | List skills explicitly in `skills:` frontmatter |
| Forgetting branch protection | Agents writing to repos must push a branch and open a PR, not push to main |
