# `.claude/rules/` — Project Rules

A directory of modular, topic-scoped instruction files for Claude Code. Each file holds one
topic's rules; **path-scoped** rules load into context only when Claude touches matching files,
which is the main lever for keeping always-on context small in a large project.

This is distinct from CLAUDE.md: CLAUDE.md is one (or a few) always-loaded files; `.claude/rules/`
is a set of files, some always-on and some conditional. Both are *advisory context, not
enforcement* — for anything that must happen every time, use a hook. See
[claude-memory.md](claude-memory.md) for CLAUDE.md, imports, and auto memory.

Docs: https://code.claude.com/docs/en/memory#organize-rules-with-claude%2Frules%2F

## Table of Contents

- [Directory layout](#directory-layout)
- [Always-on vs path-scoped rules](#always-on-vs-path-scoped-rules)
- [`paths` glob patterns](#paths-glob-patterns)
- [Precedence & load order](#precedence--load-order)
- [Sharing rules with symlinks](#sharing-rules-with-symlinks)
- [User-level rules](#user-level-rules)
- [Additional dirs, excludes, debugging](#additional-dirs-excludes-debugging)
- [When to use rules vs CLAUDE.md vs skills vs hooks](#when-to-use-rules-vs-claudemd-vs-skills-vs-hooks)
- [Gotchas](#gotchas)

## Directory layout

Place markdown files under `.claude/rules/`. One topic per file, descriptive filename. All `.md`
files are discovered **recursively**, so you can nest by area:

```text
your-project/
└── .claude/
    ├── CLAUDE.md            # main always-on project instructions
    └── rules/
        ├── code-style.md
        ├── testing.md
        ├── security.md
        ├── frontend/
        │   └── components.md
        └── backend/
            └── api-design.md
```

## Always-on vs path-scoped rules

A rule file is one of two kinds, decided solely by whether it has a `paths` frontmatter field:

**Always-on** (no frontmatter, or frontmatter without `paths`): loaded at launch, applies to all
files, **same priority as `.claude/CLAUDE.md`**. Use for project-wide standards you'd otherwise
put in CLAUDE.md but want kept in their own file for maintainability.

```markdown
# Testing conventions
- Co-locate tests as `*.test.ts` next to the source file
- Use the project's `test` helper factory, never instantiate fixtures inline
```

**Path-scoped** (`paths` frontmatter): conditional — only enters context when Claude reads/works
with a file matching one of the globs. This is how you keep instructions out of context until
they're relevant.

```markdown
---
paths:
  - "src/api/**/*.ts"
---

# API Development Rules

- All API endpoints must include input validation
- Use the standard error response format
- Include OpenAPI documentation comments
```

> `paths` is the only supported rule frontmatter field. (Don't confuse rules with skills —
> fields like `name`/`description`/`disable-model-invocation` belong to `SKILL.md`, not rules.)

## `paths` glob patterns

| Pattern | Matches |
|---|---|
| `**/*.ts` | All TypeScript files in any directory |
| `src/**/*` | All files under `src/` |
| `*.md` | Markdown files in the project root only |
| `src/components/*.tsx` | React components in that specific directory |

List multiple patterns, and use brace expansion for multiple extensions in one:

```markdown
---
paths:
  - "src/**/*.{ts,tsx}"
  - "lib/**/*.ts"
  - "tests/**/*.test.ts"
---
```

**Trigger semantics:** path-scoped rules trigger when Claude **reads a file matching the
pattern** — not on every tool use. So a rule scoped to `src/api/**` won't be in context while
Claude works in `src/ui/`, and arrives the moment it opens an API file.

## Precedence & load order

- Always-on rules load at launch with the **same priority as `.claude/CLAUDE.md`**.
- **User-level rules load before project rules**, so project rules take higher priority on
  conflict (most-specific-wins, consistent with CLAUDE.md hierarchy ordering).
- Contradictions across rules/CLAUDE.md/auto-memory resolve arbitrarily — audit periodically.

## Sharing rules with symlinks

`.claude/rules/` resolves symlinks, so you can keep one canonical rule set and link it into many
repos. Circular symlinks are detected and handled gracefully.

```bash
# Link a shared directory of rules
ln -s ~/shared-claude-rules .claude/rules/shared
# Link a single shared rule file
ln -s ~/company-standards/security.md .claude/rules/security.md
```

## User-level rules

Personal rules that apply to **every project** on your machine go in `~/.claude/rules/`:

```text
~/.claude/rules/
├── preferences.md    # personal coding preferences
└── workflows.md      # preferred workflows
```

Loaded before project rules (project wins). Path-scoped frontmatter works here too.

## Additional dirs, excludes, debugging

- **`--add-dir`:** rules from extra directories are *not* loaded by default. Set
  `CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD=1` to also load `CLAUDE.md`, `.claude/CLAUDE.md`,
  `.claude/rules/*.md`, and `CLAUDE.local.md` from them.
- **Exclude in monorepos:** `claudeMdExcludes` (glob, any settings layer, arrays merge) skips
  ancestor rules dirs that aren't relevant — e.g. `"/abs/other-team/.claude/rules/**"`. Keep it in
  `.claude/settings.local.json`. Managed-policy files can't be excluded.
- **Verify loading:** `/memory` lists every CLAUDE.md, CLAUDE.local.md, and rules file loaded this
  session. The `InstructionsLoaded` hook logs exactly which files load, when, and why — the best
  tool for debugging path-scoped rules that aren't firing.

## When to use rules vs CLAUDE.md vs skills vs hooks

| Need | Use |
|---|---|
| Project-wide standard, always relevant | `.claude/CLAUDE.md` (or an always-on rule file) |
| Standard relevant only to certain files/areas | **Path-scoped `.claude/rules/`** (saves context) |
| Multi-step procedure / knowledge needed only sometimes | Skill (loads on demand / on invocation) |
| Must happen every time, deterministically (e.g. lint before commit) | Hook (PreToolUse/Stop) |
| Personal cross-project preferences | `~/.claude/rules/` or `~/.claude/CLAUDE.md` |

Mental model: **rules without `paths` ≈ a tidier CLAUDE.md; rules with `paths` ≈ context that
pays for itself only when relevant.** If it's a workflow you trigger, it's a skill; if it must be
enforced, it's a hook.

## Gotchas

- **Advisory, not enforced** — a path-scoped rule is still just context Claude *tries* to follow.
- **`paths` is the only frontmatter field** — invented fields are silently ignored.
- **Path-scoped rules trigger on file read, not on every turn** — a rule that never fires usually
  means no matching file was opened, or the glob is wrong. Confirm with `InstructionsLoaded`.
- **User rules load before project rules** — if a personal rule seems overridden, a project rule
  of higher priority is winning by design.
- **Always-on rules still cost context every session** — only `paths`-scoped rules save context.
  Don't move bloat from CLAUDE.md into a dozen always-on rule files and expect savings.
