# CLAUDE.md Design

Sources: Anthropic official documentation (code.claude.com/docs/en/memory, /hooks-guide); Alireza Rezvani, production experience running Claude Code across 7-engineer team for 1 year; HumanLayer research

## Table of Contents

- [What CLAUDE.md Actually Is](#what-claudemd-actually-is) — advisory not deterministic; delivered as user message
- [Size Limit](#size-limit) — 200-line official ceiling; adherence math
- [The Scope System](#the-scope-system) — root / subdirectory / user-global / local
- [.claude/rules/ — Path-Scoped Rules](#clauderules--path-scoped-rules) — globs syntax; known parser bugs; token budget math
- [Rules by Domain](#rules-by-domain) — per-subdirectory rule files
- [@Import Syntax](#import-syntax)
- [HTML Comments for Maintainer Notes](#html-comments-for-maintainer-notes)
- [Commands](#commands) — slash command definitions
- [The Three Sections That Actually Matter](#the-three-sections-that-actually-matter) — must-do / never-do / context
- [Writing Rules That Work](#writing-rules-that-work) — positive instructions; specificity; verification
- [Hooks](#hooks) → [hooks.md](hooks.md) — exit codes, updatedInput, hook types, CI caveats
- [CLAUDE.md vs. Auto-Memory](#claudemd-vs-auto-memory) — memory hierarchy; 200-line ceiling; worktree fragmentation; CI disable
- [AGENTS.md Interoperability](#agentsmd-interoperability)
- [The Compounding Maintenance Pattern](#the-compounding-maintenance-pattern)
- [What Does Not Work](#what-does-not-work)

---

## What CLAUDE.md Actually Is

Claude Code is stateless. Every session starts from zero. Whatever corrections you made Tuesday, whatever architectural context you explained Monday — gone. CLAUDE.md is the only mechanism that bridges sessions: it loads automatically at the start of every conversation, before you type a single word.

**Technically**: CLAUDE.md content is delivered as a **user message** after the system prompt, not as part of the system prompt itself. Claude reads it and tries to follow it, but there is no guarantee of strict compliance — especially for vague or conflicting instructions.

The critical nuance most teams miss: **CLAUDE.md is advisory, not deterministic.**

Implication: every unnecessary line dilutes the ones that matter. For instructions that *must* happen without exception, use hooks (see [Hooks vs. CLAUDE.md](#hooks-vs-claude-md)).

> "CLAUDE.md is not documentation. It is not a README for the AI. It is the only persistent control layer you have over Claude Code's behavior — a production configuration that determines whether Claude Code operates as a disciplined engineer or an expensive autocomplete."

## Size Limit

**Official Anthropic guidance: keep each CLAUDE.md file under 200 lines.** Files over 200 lines consume more context and may reduce adherence.

An 800-line CLAUDE.md does not give Claude more guidance — it gives Claude more noise to filter through. A 90-line root with targeted subdirectory files consistently outperforms a 600-line root.

If your file is growing large: split using `@path` imports or `.claude/rules/` files. See the scope system below.

## The Scope System

CLAUDE.md files can live in several locations, each with a different scope. More specific locations take precedence over broader ones.

| Scope | Location | Shared with | Use for |
|---|---|---|---|
| **Managed policy** | macOS: `/Library/Application Support/ClaudeCode/CLAUDE.md`<br>Linux: `/etc/claude-code/CLAUDE.md` | All users in org | Company coding standards, security policies, compliance — cannot be excluded |
| **Project** | `./CLAUDE.md` or `./.claude/CLAUDE.md` | Team via source control | Project architecture, coding standards, build commands |
| **User** | `~/.claude/CLAUDE.md` | Just you (all projects) | Personal preferences for all projects |
| **Local** | `./CLAUDE.local.md` | Just you (current project) | Your sandbox URLs, local database config — add to `.gitignore` |
| **Rules** | `.claude/rules/*.md` | Team via source control | Domain-specific rules scoped to file paths |

**Loading behavior**:
- Project and user CLAUDE.md files in the directory hierarchy *above* the working directory are loaded in full at launch
- Files in subdirectories load **on demand** when Claude reads files in those directories — not at launch
- All discovered files are concatenated; `CLAUDE.local.md` is appended after `CLAUDE.md` at each level
- CLAUDE.md survives `/compact` — re-read from disk and re-injected fresh after compaction

**Monorepos**: use `claudeMdExcludes` in `.claude/settings.local.json` to skip other teams' CLAUDE.md files:
```json
{
  "claudeMdExcludes": [
    "**/other-team/CLAUDE.md",
    "/home/user/monorepo/other-team/.claude/rules/**"
  ]
}
```

## `.claude/rules/` — Path-Scoped Rules

For larger projects, organize instructions into multiple files in `.claude/rules/`. Each file should cover one topic (`testing.md`, `api-design.md`, `security.md`). Files are discovered recursively; organize into subdirectories if needed.

Rules without a frontmatter `globs` field load at session start. Rules with `globs` load **only when Claude works with matching files**.

### The `globs:` vs `paths:` parser bug

**Use `globs:`, not `paths:`**. The official docs show `paths:` but the underlying parser is a CSV reader that breaks when YAML hands it an array object. Several formats fail silently:

```yaml
# BROKEN — YAML array format, silently ignored (GitHub #17204)
---
paths:
  - "src/api/**/*.ts"
---

# BROKEN — quoted single value
---
paths: "src/api/**/*.ts"
---

# WORKS — unquoted single value
---
paths: src/api/**/*.ts
---

# WORKS RELIABLY — use globs: with comma-separated values
---
globs: src/api/**/*.ts, tests/**/*.test.ts
---
```

For any rule that should be path-conditional, use `globs:` with comma-separated patterns. Silent failures are the worst kind — the rule appears to be configured but has no effect.

**Diagnosis**: the community tool [claude-rules-doctor](https://github.com/nulone/claude-rules-doctor) scans `.claude/rules/` and flags rules whose globs match zero files in the current repo — catches both parser issues and refactoring drift where paths were renamed.

### Other known limitations (as of 2026)

- **Load globally despite scoping** (issue #16299, open): path-scoped rules sometimes load at session start regardless of glob matching — up to 28 rules loading when ~5 should. Scoping reduces context waste but is not a reliable exclusion mechanism.
- **User-level `~/.claude/rules/` ignores `paths:` entirely** (issue #21858): glob scoping only works for project-level rules. User-level rules always load globally.
- **`Write` tool doesn't trigger path-scoped rules** (issue #23478): rules only activate when Claude reads a matching file, not when it creates one. A rule for `src/api/**/*.ts` won't fire when Claude creates a new API file from scratch.
- **Breaks with git worktrees** (issue #23569): path-conditional rules may fail to activate in worktree-based parallel agent workflows.

### Token budget mathematics

Frontier LLMs reliably follow roughly 150–200 instructions total. Claude's system prompt consumes ~50 before CLAUDE.md ever loads. Every low-priority rule in an unscoped rules file degrades compliance on high-priority rules.

This makes scoped rules a functional requirement, not just organization:

- **Always-loaded rules** (no `globs:`): security constraints, standards that must hold everywhere — keep these under ~50 lines total
- **Scoped rules** (`globs:`): domain-specific context loaded only when relevant — no token cost outside their scope

The test for each rule: "when must this constraint apply?" If the answer is "only in certain directories," it belongs in a scoped file. If the answer is "everywhere, always," it belongs in the always-loaded set.

### CLAUDE.md as explicit rule dispatch table

Given the loading bugs above, don't rely entirely on automatic path-triggered rule loading. Add an explicit dispatch table in CLAUDE.md that tells Claude which rule file to consult for which kind of work:

```markdown
## Rules by domain
- API endpoints (`src/api/`): see .claude/rules/api-standards.md
- Tests (`**/*.test.ts`): see .claude/rules/testing.md  
- Database migrations (`src/db/`): see .claude/rules/migrations.md
- Auth/security paths: see .claude/rules/security.md
```

This primes Claude's planning phase before rule evaluation — Claude reads the relevant rule file explicitly rather than waiting for path-based auto-loading to fire (which may not, given the bugs).

### Multi-tool sharing

Claude Code ignores unknown frontmatter fields, which means rule files can carry fields for other tools (Cursor's `alwaysApply`, Gemini CLI fields) without breaking. Three patterns for sharing rules across AI coding tools:

- **Symlink**: `.claude/rules` → `.cursor/rules` — same files, each tool reads its own directory
- **Neutral location**: `.ai/rules/` with symlinks into each tool's expected directory
- **[rulesync](https://dev.to/dyoshikawatech/rulesync-published-a-tool-to-unify-management-of-rules-for-claude-code-gemini-cli-and-cursor-390f)**: write rules once in `.rulesync/*.md` with a `targets:` field; generates platform-specific files for Claude Code, Cursor, Gemini CLI, Cline, GitHub Copilot, and Roo Code

**User-level rules** at `~/.claude/rules/` apply to every project on your machine (loaded before project rules, giving project rules higher priority). Note: `globs:` scoping does not work at the user level — these always load globally.

**Share rules across projects**: `.claude/rules/` supports symlinks — maintain a shared rules directory and link it into multiple projects.

## @Import Syntax

CLAUDE.md files can import additional files using `@path/to/file` syntax. Imported files are expanded and loaded into context at launch:

```markdown
See @README for project overview and @package.json for available commands.

# Additional Instructions
- Git workflow: @docs/git-instructions.md
```

- Both relative and absolute paths are supported
- Relative paths resolve relative to the file containing the import, not the working directory
- Imported files can recursively import other files (maximum depth: 5 hops)
- First time external imports are encountered, Claude shows an approval dialog

**Sharing personal instructions across worktrees** (gitignored `CLAUDE.local.md` only exists in one worktree):
```markdown
# Individual Preferences
- @~/.claude/my-project-instructions.md
```

## HTML Comments for Maintainer Notes

`<!-- HTML comments -->` in CLAUDE.md are stripped before injection into Claude's context. Use them to leave notes for human maintainers without spending context tokens:

```markdown
<!-- Last reviewed: 2026-03-15. Remove the pnpm rule if we migrate to bun. -->
## Commands
- Install: pnpm install (NEVER npm install)
```

Comments inside code blocks are preserved. When you open the file directly with the Read tool, comments remain visible.

## The Three Sections That Actually Matter

### 1. Build and Test Commands

The mistake: including the primary command but omitting flags, environment requirements, and the differences between commands.

**Before:**
```
Test: pnpm test
```

**After:**
```markdown
## Commands
- Install: pnpm install (NEVER npm install or yarn install)
- Build: pnpm build (requires DATABASE_URL env var — will fail silently without it)
- Test (unit only): pnpm test:unit (fast, no external dependencies)
- Test (e2e): pnpm test:e2e (requires Redis on port 6380 and PostgreSQL on port 5433)
- Lint: pnpm lint --fix
- Typecheck: pnpm typecheck
```

`pnpm test` runs the full suite including e2e, which times out without external services. Claude reports test failures that are actually environment failures. One line in CLAUDE.md fixes that permanently.

### 2. The Never List

Negative constraints are often more powerful than positive guidance. The Never List encodes anti-patterns specific to your codebase — not generic best practices, but your specific failure modes.

**Every item on the Never List should come from something Claude actually did wrong.** Not theoretical risk — observed failure. Each item represents a correction made at least twice before being encoded permanently.

Example:
```markdown
## Never Do
- Import from relative paths — always use the @/ alias
- Create new DTO types without checking src/shared/types first
- Use `any` type — if you need escape hatches, use `unknown` with a type guard
- Add console.log statements to production code
- Bypass Zod validation on any external API response
- Run database migrations directly — always use scripts/db/migrate.sh
```

### 3. Architecture Notes

Not your full architecture document — one paragraph maximum per concern that is **non-obvious**.

Claude can infer a lot from the codebase. It cannot infer decisions made three years ago and the reasons behind them. Non-obvious decisions — the ones where a new engineer would ask "why is it done this way?" — belong here. Obvious decisions don't.

## Writing Rules That Work

**Rules without examples are unreliable.** "Use descriptive variable names" is useless. "Name variables after what they contain, not what type they are — `userEmail` not `emailString`" is actionable.

**Use `IMPORTANT:` or `YOU MUST` for critical rules.** Since CLAUDE.md is advisory, emphasis signals unconditional applicability.

**Write rules as positive instructions where possible.** "Use the `@/` import alias" outperforms "Don't use relative imports."

**Verify your files are loading.** Run `/memory` in a session — it lists all CLAUDE.md, CLAUDE.local.md, and rules files loaded in the current session. If a file isn't listed, Claude can't see it.

## Hooks

CLAUDE.md is advisory; hooks are deterministic. For enforcement details — exit code semantics, `updatedInput`, hook types, CI caveats — see **[hooks.md](hooks.md)**.

Quick reference:
- `PreToolUse` — block or transform before tool executes; fires in headless/CI mode
- `PostToolUse` — react after tool runs; cannot block
- `PermissionRequest` — intercept permission prompts; does **not** fire in headless mode (use `PreToolUse` for CI)
- Exit 2 = blocking (stderr → Claude); exit 0 + JSON = structured response; any other = non-blocking

## CLAUDE.md vs. Auto-Memory

| | CLAUDE.md | Auto-memory (MEMORY.md) |
|---|---|---|
| Written by | Humans | Claude |
| Shared | Committed to git, team-wide | Local to each developer's machine |
| Purpose | Project rules, conventions, build commands | Claude's own learned observations |
| Worktree scope | Per project | Per git repo — all worktrees of same repo share one |

**Memory hierarchy** (loading order, most specific wins):
1. Organization managed policy
2. Project `CLAUDE.md` (committed to git, team-wide)
3. User `~/.claude/CLAUDE.md` (personal, all projects)
4. `MEMORY.md` — first 200 lines loaded at session start; beyond that, Claude creates topic files (`debugging.md`, `patterns.md`, etc.) in the same directory, loaded on demand

**Auto-memory location**: `~/.claude/projects/<project-path>/memory/MEMORY.md`. Each repository gets its own directory — no cross-contamination between projects or clients. To review across all projects: `cat ~/.claude/projects/*/memory/MEMORY.md`.

**The 200-line ceiling**: only the first 200 lines of MEMORY.md load at session start. For projects that accumulate more, Claude creates additional topic-specific files in the same directory and loads them when relevant. In practice, auto-memory tends to be sparse — commands, paths, and patterns rather than architectural reasoning. The "why" belongs in CLAUDE.md, written by humans; the "what" accumulates in MEMORY.md.

**Worktree fragmentation**: git worktrees get separate memory directories. If you're running parallel sessions across multiple worktrees, each session starts with slightly different auto-memory context. This is a known limitation — mitigation is ensuring the important team context lives in shared CLAUDE.md rather than individual auto-memory.

**The promotion pattern**: let auto-memory accumulate individual session learnings (which port your database runs on, which env var your build needs). Periodically review and promote recurring patterns into the shared CLAUDE.md so the whole team benefits.

**This is partially schedulable**: the discovery step — scanning MEMORY.md for patterns that have appeared across multiple sessions — can run as a scheduled Claude Code task that reads the file and proposes additions to CLAUDE.md. The decision step (which ones to actually promote) requires human judgment, so the full workflow is: scheduled scan surfaces candidates → developer reviews and commits the ones worth sharing.

A minimal entropy agent for this:
```markdown
---
name: memory-promotion-scan
description: Scan MEMORY.md for team-worthy patterns
---

Read ~/.claude/projects/*/memory/MEMORY.md and the current project's CLAUDE.md.
Identify entries in MEMORY.md that:
1. Apply to all team members, not just personal preferences
2. Are not already in CLAUDE.md
3. Have appeared in multiple sessions (repeated corrections are the strongest signal)

List up to 5 candidates with the proposed CLAUDE.md addition for each.
Do not make changes — output candidates for human review.
```

**Disabling auto-memory in CI** — critical: automated Claude Code runs (CI pipelines, headless PR review, staging workflows) will accumulate CI noise in MEMORY.md that then pollutes every local developer session. Prevent this with one environment variable:

```bash
# In your CI config (GitHub Actions, Jenkins, etc.)
export CLAUDE_CODE_DISABLE_AUTO_MEMORY=1
```

This takes precedence over the `/memory` toggle and any `settings.json` configuration. Add it to every non-local Claude Code invocation — CI, staging, automated review, any headless run.

## AGENTS.md Interoperability

Claude Code reads `CLAUDE.md`, not `AGENTS.md`. If your repository uses `AGENTS.md` for other coding agents, create a `CLAUDE.md` that imports it:

```markdown
@AGENTS.md

## Claude Code
Use plan mode for changes under `src/billing/`.
```

Claude loads the imported file at session start, then appends the rest.

## The Compounding Maintenance Pattern

> "Boris Cherny, who leads Claude Code at Anthropic, calls this 'compounding engineering.' Every correction you encode makes every future session smarter."

**The single habit**: every time Claude does something wrong, ask — is this a missing rule, or a one-time mistake? If it is a missing rule, the correction goes into CLAUDE.md, not just the chat. Corrections in chat disappear at session end; corrections in CLAUDE.md compound across every future session and every engineer on the team.

**Team practice**: weekly 10-minute review of Claude Code sessions for corrections that belong in the file.

**Monthly pruning**: for each line, ask — is Claude already doing this correctly without being told? If yes, the line is noise. Remove it. CLAUDE.md grows naturally; rules rarely get removed. Prune intentionally to keep adherence high.

**Official Anthropic recommendation**: review your CLAUDE.md files, nested subdirectory files, and `.claude/rules/` periodically to remove outdated or conflicting instructions.

## What Does Not Work

**Everything in the root file**: Claude consistently ignores ~60% of an 800-line root CLAUDE.md. Fix: lean root + domain-specific subdirectory files.

**CLAUDE.md as a substitute for feedback loops**: CLAUDE.md is advisory; hooks are deterministic. If a rule must happen without exception, build a hook.

**Rules without examples**: specific, concrete, example-backed rules are followed; vague rules are ignored.

**Personal preferences in the shared file**: personal preferences go in `~/.claude/CLAUDE.md` (all projects) or `CLAUDE.local.md` (current project only). Mixing them creates noise and causes shared rules to compete for attention with individual preferences.
