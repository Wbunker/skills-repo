# CLAUDE.md, Rules & Memory

How to give Claude Code persistent instructions and let it accumulate learnings. Two
complementary systems, both loaded at the **start of every conversation**:

- **CLAUDE.md files** + **`.claude/rules/`** — instructions *you* write.
- **Auto memory** — notes *Claude* writes itself from your corrections and discoveries.

**Critical framing:** both are *context, not enforced configuration*. Claude reads them and tries
to follow, but compliance is not guaranteed (CLAUDE.md is delivered as a user message after the
system prompt). To make something happen regardless of what Claude decides, use a
[hook](claude-code.md) (PreToolUse/Stop) — not a rule. Specific, concise instructions are followed
more reliably than vague or conflicting ones.

Docs: https://code.claude.com/docs/en/memory · https://code.claude.com/docs/en/best-practices

## Table of Contents

- [CLAUDE.md locations & load order](#claudemd-locations--load-order)
- [Writing effective instructions](#writing-effective-instructions)
- [Imports (`@path`) and AGENTS.md](#imports-path-and-agentsmd)
- [`.claude/rules/` (modular & path-scoped rules)](#clauderules-modular--path-scoped-rules)
- [Auto memory](#auto-memory)
- [`/memory`, `/init`, and the `#` shortcut](#memory-init-and-the--shortcut)
- [Enforcement vs. guidance](#enforcement-vs-guidance)
- [Org-wide & monorepo controls](#org-wide--monorepo-controls)
- [Gotchas](#gotchas)

## CLAUDE.md locations & load order

Listed broadest → most specific; later entries appear after earlier ones in context, so the
narrowest scope is read last.

| Scope | Location | Shared with |
|---|---|---|
| **Managed policy** | macOS `/Library/Application Support/ClaudeCode/CLAUDE.md` · Linux/WSL `/etc/claude-code/CLAUDE.md` · Windows `C:\Program Files\ClaudeCode\CLAUDE.md` | All users (IT-deployed, cannot be excluded) |
| **User** | `~/.claude/CLAUDE.md` | Just you, all projects |
| **Project** | `./CLAUDE.md` or `./.claude/CLAUDE.md` | Team, via git |
| **Local** | `./CLAUDE.local.md` (gitignore it) | Just you, this project |

**Directory-hierarchy walk:** Claude walks up from the working directory; every `CLAUDE.md` /
`CLAUDE.local.md` in ancestor directories is concatenated (not overridden), ordered filesystem
root → cwd, with `CLAUDE.local.md` appended after `CLAUDE.md` at each level. Files in
**subdirectories** below cwd are *not* loaded at launch — they load on demand when Claude reads a
file in that subdirectory.

Run `/init` to bootstrap a project CLAUDE.md (analyzes the codebase; suggests improvements if one
exists rather than overwriting). `CLAUDE_CODE_NEW_INIT=1` enables an interactive multi-phase flow
that also offers to set up skills and hooks.

## Writing effective instructions

CLAUDE.md is loaded **in full every session**, consuming tokens alongside the conversation, so
phrasing drives adherence.

- **Size:** target **under 200 lines** per file. Bloat reduces adherence — "if your CLAUDE.md is
  too long, Claude ignores half of it because important rules get lost in the noise."
- **The pruning test:** for each line ask *"Would removing this cause Claude to make mistakes?"*
  If not, cut it. Treat CLAUDE.md like code — review, prune, and test by observing whether
  behavior actually shifts.
- **Structure:** group with markdown headers and bullets, not dense paragraphs.
- **Specificity (concrete enough to verify):**
  - "Use 2-space indentation" — not "Format code properly"
  - "Run `npm test` before committing" — not "Test your changes"
  - "API handlers live in `src/api/handlers/`" — not "Keep files organized"
- **Emphasis:** add `IMPORTANT` or `YOU MUST` to tune adherence on rules Claude keeps ignoring.
- **Consistency:** contradictory rules → Claude picks arbitrarily. Prune conflicts periodically.
- **When to add a rule:** Claude makes the same mistake twice; a review catches something it
  should have known; you re-type the same correction; a new teammate would need the same context.
- **What to move elsewhere:** multi-step procedures or context that only matters sometimes →
  [skills](claude-code.md) (load on demand). Instructions that apply only to certain files →
  [path-scoped rules](#clauderules--modular--path-scoped-rules).

| ✅ Include | ❌ Exclude |
|---|---|
| Bash commands Claude can't guess | Anything Claude can infer from the code |
| Code style that differs from defaults | Standard language conventions |
| Testing instructions / preferred runners | Detailed API docs (link instead) |
| Repository etiquette (branch naming, PRs) | Info that changes frequently |
| Project-specific architectural decisions | Long explanations or tutorials |
| Dev-environment quirks (required env vars) | File-by-file codebase descriptions |
| Common gotchas / non-obvious behaviors | Self-evident advice ("write clean code") |

> On Opus 4.7+, NEVER/ALWAYS rules became *sharper*, not softer — don't water them down; instead
> write out their scope and exceptions explicitly. See [opus-47-migration.md](opus-47-migration.md).

A minimal, effective example:

```markdown
# Code style
- Use ES modules (import/export), not CommonJS (require)
- Destructure imports when possible (e.g. import { foo } from 'bar')

# Workflow
- Typecheck after a series of code changes
- Prefer running single tests, not the whole suite, for performance
```

## Imports (`@path`) and AGENTS.md

CLAUDE.md can pull in other files with `@path/to/import` (anywhere in the file):

```text
See @README.md for project overview and @package.json for npm commands.

# Additional Instructions
- Git workflow: @docs/git-instructions.md
- Personal overrides (shared across worktrees): @~/.claude/my-project-instructions.md
```

- Relative (resolved against the importing file, not cwd) **and** absolute / `~` paths allowed.
- Imports recurse, **max depth 4 hops**.
- **Imports do NOT save context** — imported files expand and load at launch. Use them for
  *organization*, use `.claude/rules/` path-scoping for *context savings*.
- First time a project uses *external* imports, Claude shows a one-time approval dialog; decline
  and they stay disabled.
- Worktree note: a gitignored `CLAUDE.local.md` exists only in the worktree it was created in —
  import from `~/.claude/...` to share personal notes across worktrees.

**AGENTS.md:** Claude reads `CLAUDE.md`, not `AGENTS.md`. To reuse an existing `AGENTS.md`, make a
`CLAUDE.md` that does `@AGENTS.md` (then add Claude-specific notes below), or symlink it
(`ln -s AGENTS.md CLAUDE.md`). `/init` also incorporates `AGENTS.md`, `.cursorrules`,
`.windsurfrules` when present.

## `.claude/rules/` (modular & path-scoped rules)

Split instructions into topic files under `.claude/rules/`. Files **without** `paths` frontmatter
load at launch (same priority as `.claude/CLAUDE.md`); files **with** a `paths` glob load only when
Claude touches matching files — the main lever for cutting always-on context.

→ Full reference (layout, glob table, trigger semantics, precedence, symlinks, user-level rules,
rules-vs-CLAUDE.md-vs-skills-vs-hooks): [claude-rules.md](claude-rules.md)

## Auto memory

Claude writes its own notes across sessions — build commands, debugging insights, architecture
notes, preferences — deciding what's worth keeping (it doesn't save every session). On by default
(requires Claude Code **v2.1.59+**).

- **Storage:** `~/.claude/projects/<project>/memory/` — a `MEMORY.md` index plus topic files
  (`debugging.md`, etc.). Per-git-repo; shared across that repo's worktrees; **machine-local**
  (not synced across machines or cloud).
- **Loading:** first **200 lines or 25KB** of `MEMORY.md` (whichever first) loads every session;
  topic files load on demand. (This 200-line limit is for `MEMORY.md`; CLAUDE.md always loads in
  full.)
- **Toggle:** `/memory` toggle, `autoMemoryEnabled: false` in settings, or
  `CLAUDE_CODE_DISABLE_AUTO_MEMORY=1`. Relocate with `autoMemoryDirectory` (absolute or `~/`).
- All files are plain markdown — audit/edit/delete freely via `/memory`.

## `/memory`, `/init`, and the `#` shortcut

- `/memory` — lists every CLAUDE.md, CLAUDE.local.md, and rules file loaded this session; toggles
  auto memory; opens any file in your editor. First stop when an instruction "isn't working."
- `/init` — bootstrap or improve a project CLAUDE.md.
- **Routing what you say:** "remember that the API tests need a local Redis" → saved to **auto
  memory**. "Add this to CLAUDE.md" → written to **CLAUDE.md**. Be explicit about which you want.

## Enforcement vs. guidance

CLAUDE.md, rules, and memory shape behavior but are advisory. When something *must* happen:

| Need | Use |
|---|---|
| Run/block at a fixed lifecycle point (before commit, after edit) | [Hook](claude-code.md) (PreToolUse/Stop) — deterministic |
| Block specific tools/commands/paths | Managed settings `permissions.deny` |
| System-prompt-level instruction | `--append-system-prompt` (must pass every invocation; for scripts) |
| Reusable, on-demand workflow/knowledge | [Skill](claude-code.md) |

## Org-wide & monorepo controls

- **Managed CLAUDE.md** (policy location above) applies to every session on the machine and
  **cannot be excluded**; or put content inline via the `claudeMd` key in `managed-settings.json`.
  Loads before user/project. Honored in managed/policy settings only.
- **`claudeMdExcludes`** (glob, any settings layer; arrays merge) skips ancestor CLAUDE.md / rules
  files irrelevant to your work in a monorepo — except managed-policy files. Keep it local:

  ```json
  { "claudeMdExcludes": ["**/monorepo/CLAUDE.md", "/abs/path/other-team/.claude/rules/**"] }
  ```

## Gotchas

- **Advisory, not enforced** — if a rule must hold every time, it belongs in a hook, not CLAUDE.md.
- **Bloat backfires** — over-long CLAUDE.md makes Claude ignore rules. Prune ruthlessly; convert
  "must always" rules to hooks.
- **`@path` imports don't reduce context** — only path-scoped `.claude/rules/` or trimming do.
- **Subdirectory CLAUDE.md isn't re-injected after `/compact`** — only project-root CLAUDE.md is
  re-read from disk and re-injected; nested files reload next time Claude reads a file there.
  Conversation-only instructions vanish on compaction — add them to CLAUDE.md to persist.
- **HTML block comments (`<!-- ... -->`) are stripped** before injection (free maintainer notes);
  comments *inside code blocks* are preserved.
- **Conflicting rules → arbitrary choice.** Audit across the hierarchy + `.claude/rules/` + auto
  memory periodically.
- **Debug loading** with the `InstructionsLoaded` hook (logs which files loaded, when, why).
