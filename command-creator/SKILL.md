---
name: command-creator
description: >
  Create or update Claude Code slash commands (also called skills). Use when the user wants to
  create a new /command, add a command file to .claude/commands/ or .claude/skills/, define
  command frontmatter, set up handoffs, configure allowed-tools, use $ARGUMENTS, add context
  injection, or design a multi-step command workflow. Triggers on: "create a command",
  "add a slash command", "new command", "write a command for", "make a /command".
---

# Command Creator

Commands and skills are the same format. A file at `.claude/commands/deploy.md` and a skill
at `.claude/skills/deploy/SKILL.md` both create `/deploy` and work identically.

**Full frontmatter reference**: See [references/frontmatter.md](references/frontmatter.md)
**Command patterns with examples**: See [references/patterns.md](references/patterns.md)

## Workflow

1. **Clarify intent** — determine command purpose, arguments, tools needed, and whether it should be user-invoked only or auto-triggered by Claude
2. **Choose the right pattern** — pick from the patterns in `references/patterns.md` that best matches the use case
3. **Select where to put it**:
   - `.claude/commands/<name>.md` — standalone command (simple, no bundled resources)
   - `.claude/skills/<name>/SKILL.md` — skill with bundled scripts/references/assets
4. **Write frontmatter** — use `references/frontmatter.md`; add only the fields needed
5. **Write the body** — imperative instructions; reference `$ARGUMENTS` and body variables as needed
6. **Validate** — the `description` field is the primary auto-trigger signal; make sure it clearly states when the command should load

## Key Decisions

**`disable-model-invocation: true`** — any command with side effects (deploys, commits, pushes, deletions). Forces explicit `/name` invocation; Claude won't auto-trigger it.

**`context: fork`** — command runs isolated from conversation history. Good for research tasks, long analysis, or commands that dispatch many subagents.

**`handoffs`** — multi-step workflows where the user should be offered a next step after the command completes. Each handoff becomes a clickable button in the UI.

**`allowed-tools`** — restrict tools available without prompting. Use `Read, Grep, Glob` for read-only commands; `Agent` for orchestrators that only dispatch.

## Body Template

```markdown
---
description: <what it does and when to use it>
argument-hint: [optional-arg-hint]
---

## User Input

\`\`\`text
$ARGUMENTS
\`\`\`

You MUST consider the user input before proceeding (if not empty).

## Steps

1. ...
2. ...
```

## Variable Quick Reference

| Variable | Value |
|---|---|
| `$ARGUMENTS` | Everything typed after `/command-name` |
| `$0`, `$1`, `$2` | Individual space-separated args (0-indexed) |
| `$ARGUMENTS[N]` | Same as `$N` |
| `${CLAUDE_SESSION_ID}` | Current session ID |
| `${CLAUDE_SKILL_DIR}` | Absolute path to the skill's directory |
| `` !`shell cmd` `` | Shell output injected before Claude sees the prompt (preprocessing) |
