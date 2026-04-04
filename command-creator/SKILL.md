---
name: command-creator
description: Create or update Claude Code custom commands (slash commands / skills). Use when the user wants to build a new /command, write a SKILL.md file, add frontmatter to a command, understand what frontmatter fields are available, or author a step-by-step workflow that runs as a slash command. Covers file placement, all frontmatter options, argument passing, dynamic context injection, invocation control, subagent forking, and tool restrictions.
---

# Command Creator

Claude Code commands are markdown files that become `/slash-commands`. A file at `.claude/commands/deploy.md` or `.claude/skills/deploy/SKILL.md` both create `/deploy` and work identically. Skills (directory form) are preferred because they support supporting files.

## File placement

| Scope | Path | Available to |
|---|---|---|
| Personal | `~/.claude/skills/<name>/SKILL.md` | All your projects |
| Project | `.claude/skills/<name>/SKILL.md` | This project only |
| Legacy command | `.claude/commands/<name>.md` | This project only |

The directory name becomes the slash-command name unless overridden by the `name` frontmatter field.

## Anatomy of a command file

```
my-command/
├── SKILL.md        # Required — frontmatter + instructions
├── reference.md    # Optional supporting docs (load on demand)
└── scripts/
    └── helper.py   # Optional scripts Claude can run
```

## Frontmatter reference

YAML between `---` markers at the top of `SKILL.md`. All fields are optional; `description` is strongly recommended.

```yaml
---
name: my-command
description: What this does and when to use it
argument-hint: "[issue-number]"
disable-model-invocation: true
user-invocable: true
allowed-tools: Read, Grep, Bash(gh *)
model: claude-opus-4-6
context: fork
agent: Explore
hooks:
  Stop:
    - type: command
      command: echo "done"
---
```

| Field | Default | Purpose |
|---|---|---|
| `name` | directory name | Slash-command name. Lowercase letters, numbers, hyphens. Max 64 chars. |
| `description` | first paragraph | What it does + when to use it. Claude uses this to decide when to auto-invoke. Put all trigger context here — not in the body. |
| `argument-hint` | — | Autocomplete hint shown in the `/` menu. E.g. `[filename] [format]`. |
| `disable-model-invocation` | `false` | `true` = only you can invoke; Claude never auto-triggers. Use for side-effect commands like `/deploy`, `/commit`. |
| `user-invocable` | `true` | `false` = hidden from `/` menu; Claude auto-invokes only. Use for background knowledge. |
| `allowed-tools` | — | Tools Claude may use without approval when this command runs. E.g. `Read, Grep, Glob` or `Bash(npm *)`. |
| `model` | session default | Override the model for this command's execution. |
| `context` | — | Set `fork` to run in an isolated subagent. Command body becomes the subagent task. No access to conversation history. |
| `agent` | `general-purpose` | Subagent type when `context: fork`. Options: `Explore`, `Plan`, `general-purpose`, or any `.claude/agents/` custom agent. |
| `background` | `false` | `true` = run the forked subagent in the background (non-blocking). Requires `context: fork`. Any tool not in `allowed-tools` will **silently fail** — no prompt. Enumerate every needed tool upfront. |
| `hooks` | — | Lifecycle hooks scoped to this command. |

### Invocation control matrix

| Frontmatter | User can invoke | Claude auto-invokes | Description in context |
|---|---|---|---|
| (default) | Yes | Yes | Always |
| `disable-model-invocation: true` | Yes | No | Never |
| `user-invocable: false` | No | Yes | Always |

## Passing arguments

Use `$ARGUMENTS` in the body — replaced with whatever the user types after the command name.

```yaml
---
name: fix-issue
description: Fix a GitHub issue by number
disable-model-invocation: true
argument-hint: "[issue-number]"
---

Fix GitHub issue $ARGUMENTS following our coding standards.
1. Read the issue
2. Implement the fix
3. Write a test
4. Commit with message "Fix #$ARGUMENTS: <description>"
```

Running `/fix-issue 42` replaces `$ARGUMENTS` with `42`.

### Positional arguments

```yaml
---
name: migrate-component
---

Migrate the $0 component from $1 to $2.
```

`/migrate-component SearchBar React Vue` → `$0=SearchBar`, `$1=React`, `$2=Vue`.

| Variable | Description |
|---|---|
| `$ARGUMENTS` | All arguments as a single string |
| `$ARGUMENTS[N]` or `$N` | Argument at 0-based index |
| `${CLAUDE_SESSION_ID}` | Current session ID |
| `${CLAUDE_SKILL_DIR}` | Absolute path to the command's directory (use to ref bundled scripts) |

## Dynamic context injection

Place an exclamation mark followed by a command wrapped in backticks to run shell commands **before** Claude sees the prompt. The output replaces the placeholder in-place.

Syntax: `!` immediately followed by a backtick-wrapped shell command.

Example command file (pr-summary):

```yaml
---
name: pr-summary
context: fork
agent: Explore
allowed-tools: Bash(gh *)
---
```

In the body of that command file, you would write lines like:

    ## Pull request context
    - Diff: (! followed by backtick-wrapped: gh pr diff)
    - Comments: (! followed by backtick-wrapped: gh pr view --comments)
    - Changed files: (! followed by backtick-wrapped: gh pr diff --name-only)

    Summarize this pull request for a reviewer.

**Note**: The actual syntax cannot be shown in a SKILL.md example because it would be executed during skill loading. When writing your own command files, place `!` directly before a backtick-wrapped command with no space.

The shell commands execute first; Claude only sees the rendered output.

## Subagent fork pattern

Use `context: fork` when the command should run in isolation (no conversation history, clean context):

```yaml
---
name: deep-research
description: Research a topic thoroughly in isolation
context: fork
agent: Explore
---

Research $ARGUMENTS thoroughly:
1. Find relevant files using Glob and Grep
2. Read and analyze the code
3. Return findings with specific file references
```

Results are summarized back into the main conversation.

### Background subagent pattern

Add `background: true` to run without blocking the main conversation.

> **Do not use `context: fork` on a command whose job is to orchestrate other agents.** `context: fork` makes the command itself a subagent, and subagents cannot use the Agent tool — any agent dispatch will silently fail. Orchestrating commands must run in the main conversation (no `context: fork`).

```yaml
---
name: deploy-prod
description: Deploy to production
context: fork
agent: general-purpose
background: true
disable-model-invocation: true
allowed-tools: Bash(npm *), Bash(git *), Bash(gh *)
---

Deploy to production:
1. Run tests
2. Build
3. Push to deployment target
4. Report result
```

**Critical gotchas for background subagents:**
- Every tool the subagent needs must be in `allowed-tools` — missing tools silently fail (no user prompt)
- The subagent has no access to conversation history — inject all context explicitly via dynamic context injection (the `!` + backtick syntax described above)
- If a background subagent is failing silently, remove `background: true` to debug with interactive prompts

### Loop patterns

**Option 1 — repeat the whole command on an interval** using `/loop`:
```
/loop 5m /my-command
```
Each invocation spawns a fresh subagent (if `context: fork` is set).

**Option 2 — write loop logic inside the skill body:**
```yaml
---
name: monitor-build
context: fork
agent: general-purpose
allowed-tools: Bash(npm *)
---

Monitor the build:
1. Run `npm run build`
2. If exit code non-zero, wait 30s and retry up to 3 times
3. Report final status
```

The agent follows the loop instructions autonomously.

## Writing effective descriptions

The `description` field is the only thing Claude reads to decide whether to auto-invoke your command. Make it count:

- State what it does **and** specific trigger phrases
- Include examples of what users would say
- Bad: `"Deploy the app"`
- Good: `"Deploy the application to production. Use when user says 'deploy', 'ship it', 'push to prod', or asks to release the current branch."`

Commands with `disable-model-invocation: true` don't need trigger language — only you invoke them.

## Quick examples

### Reference-only command (auto-invoked by Claude)
```yaml
---
name: api-conventions
description: API design patterns for this codebase. Use when writing or reviewing API endpoints, routes, or controllers.
user-invocable: false
---

When writing API endpoints:
- Use RESTful naming
- Return consistent error formats: `{ error: string, code: string }`
- Validate all inputs at the boundary
```

### Manual-only workflow command
```yaml
---
name: deploy
description: Deploy to production
disable-model-invocation: true
allowed-tools: Bash(npm *), Bash(git *), Bash(gh *)
---

Deploy $ARGUMENTS to production:
1. Run `npm test`
2. Run `npm run build`
3. Push to origin
4. Verify deployment via `gh run list --limit 1`
```

### Forked research command
```yaml
---
name: audit-deps
description: Audit npm dependencies for security issues
context: fork
agent: general-purpose
allowed-tools: Bash(npm *), Read, Glob
---

Audit the project's npm dependencies:
1. Run `npm audit`
2. Read package.json and package-lock.json
3. Identify high/critical severity issues
4. Suggest remediation steps
```

## Supporting files

Keep `SKILL.md` under 500 lines. Move detailed reference material to separate files and link them:

```markdown
## Resources
- For API schema details, see [api-schema.md](api-schema.md)
- For example outputs, see [examples.md](examples.md)
```

Reference files in `${CLAUDE_SKILL_DIR}` are loaded on demand — not at startup.
