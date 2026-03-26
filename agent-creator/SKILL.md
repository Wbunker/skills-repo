---
name: agent-creator
description: >
  Create or update Claude Code agents (subagents). Use when the user wants to create a new
  agent file in .claude/agents/, define agent frontmatter, write an agent system prompt,
  configure agent tools/model/permissions, set up background agents, add worktree isolation,
  or design an agent that gets dispatched by a command or orchestrator. Triggers on: "create
  an agent", "new agent", "add an agent", "write an agent for", "make an agent that".
---

# Agent Creator

Agents are specialized, isolated AI workers defined as `.md` files in `.claude/agents/`.
They differ from skills/commands in one key way: **the body is a system prompt** running in
its own context window, not instructions added to the main conversation.

**Full frontmatter reference**: See [references/frontmatter.md](references/frontmatter.md)
**Agent patterns with examples**: See [references/patterns.md](references/patterns.md)

## Agent vs Command — Choose the Right Tool

| Need | Use |
|---|---|
| Isolated worker Claude dispatches automatically | **Agent** in `.claude/agents/` |
| Reusable task that runs in main context | **Command** in `.claude/commands/` |
| Side-effect action user triggers explicitly | **Command** with `disable-model-invocation: true` |
| Background parallel worker | **Agent** with `background: true` |
| One-off task in isolated context | **Command** with `context: fork` |

## File Location and Format

```
.claude/agents/<name>.md          ← project agent (version-controlled, team-shared)
~/.claude/agents/<name>.md        ← user agent (personal, all projects)
```

Single flat `.md` file — no directory needed (unlike skills).

```markdown
---
name: my-agent
description: When Claude should delegate to this agent (auto-trigger signal)
tools: Read, Grep, Glob, Bash
model: sonnet
permissionMode: acceptEdits
---

You are a specialized assistant for...

## Your task

When invoked:
1. ...
2. ...
```

## Workflow

1. **Clarify purpose** — what specific task does this agent own? What's its input/output contract?
2. **Decide scope** — project (`.claude/agents/`) or personal (`~/.claude/agents/`)?
3. **Choose tools** — list only what the agent needs; omit `Agent` unless it spawns subagents
4. **Choose model** — `haiku` for simple/fast tasks, `sonnet` for most work, `opus` for complex reasoning
5. **Set permission mode** — `acceptEdits` if it writes files without asking; `default` otherwise
6. **Write the system prompt** (body) — concise role definition + numbered steps + output format
7. **Decide invocation** — auto-triggered by description match, or called explicitly from a command

## Key Decisions

**`background: true`** — agent runs concurrently without blocking the main conversation. Use for agents dispatched in bulk by an orchestrator command. Claude pre-approves permissions upfront.

**`permissionMode: acceptEdits`** — agent applies file edits without per-file confirmation. Use when the agent's whole job is making edits (linting fixers, CSS squashers, codemods).

**`isolation: worktree`** — agent runs in a temporary git worktree. Use when parallel agents might conflict on the same files.

**`skills: [name]`** — preloads full skill content into the agent's context at startup. Use when the agent needs domain knowledge from a skill (e.g., `css-bug-squashing` for a CSS fixer agent). Note: agents do NOT inherit skills from the parent conversation.

**`maxTurns`** — cap the agent's agentic loop. Use when the agent could run indefinitely on large inputs (e.g., `maxTurns: 20` for a file-by-file processor).

## System Prompt Body Guidelines

- Open with a one-sentence role definition: "You are a [role] for [context]."
- Define the input format the agent expects (e.g., a file path, a task description)
- Use numbered steps for the workflow
- Define the output format precisely — especially for background agents that report to an orchestrator
- Keep it focused on one job; resist adding "also handle X" scope creep
