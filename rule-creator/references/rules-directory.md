# Rules Directory Reference

The `.claude/rules/` directory (available since Claude Code v2.0.64) lets you split
instructions across focused markdown files rather than maintaining one large CLAUDE.md.

## Table of Contents
1. [Directory structure](#directory-structure)
2. [Path-scoped rules](#path-scoped-rules)
3. [Glob pattern reference](#glob-pattern-reference)
4. [Loading behavior](#loading-behavior)
5. [Symlink support](#symlink-support)
6. [Excluding rules in monorepos](#excluding-rules-in-monorepos)
7. [Debugging](#debugging)

---

## Directory Structure

```
your-project/
├── CLAUDE.md               # Main project instructions (still valid)
└── .claude/
    ├── CLAUDE.md           # Alternative location for main instructions
    └── rules/
        ├── code-style.md   # Unconditional — loads at startup
        ├── testing.md      # Unconditional — loads at startup
        ├── security.md     # Unconditional — loads at startup
        ├── frontend/
        │   ├── react.md    # Path-scoped — loads for matching files
        │   └── styles.md   # Path-scoped — loads for matching files
        └── backend/
            ├── api.md      # Path-scoped — loads for matching files
            └── database.md # Path-scoped — loads for matching files
```

All `.md` files under `.claude/rules/` are discovered recursively. Subdirectory
organization is for your own clarity — Claude treats all files the same way.

**Personal rules** at `~/.claude/rules/` apply to every project and load first
(project rules load after and therefore take precedence).

---

## Path-Scoped Rules

Rules with a `paths:` frontmatter field only load when Claude reads files matching
those glob patterns. This keeps context lean — frontend rules don't pollute backend
work, and vice versa.

### Frontmatter syntax

Single pattern:
```yaml
---
paths: "src/api/**/*.ts"
---
```

Multiple patterns (recommended form):
```yaml
---
paths:
  - "src/api/**/*.ts"
  - "src/handlers/**/*.ts"
---
```

With brace expansion:
```yaml
---
paths:
  - "src/**/*.{ts,tsx}"
  - "{src,lib}/**/*.ts"
  - "tests/**/*.test.ts"
---
```

**Important:** Patterns that start with `*` or `{` must be quoted — unquoted patterns
starting with these characters are invalid YAML and will cause the rule to be ignored.

### When path rules trigger
Path-scoped rules load when Claude reads a matching file via the Read tool. They are
**not** triggered by Write operations (known limitation as of current versions). This
means path rules are best used for read-oriented workflows like code review, exploration,
and analysis.

---

## Glob Pattern Reference

| Pattern | Matches | Example match |
|---------|---------|---------------|
| `**/*.ts` | All `.ts` files in any directory | `src/auth/user.ts` |
| `src/**/*` | All files under `src/` | `src/api/routes.ts` |
| `*.md` | Markdown files in project root only | `README.md` |
| `src/components/*.tsx` | Direct `.tsx` children of `src/components/` | `src/components/Button.tsx` |
| `src/components/**/*.tsx` | All `.tsx` files under `src/components/` | `src/components/ui/Card.tsx` |
| `**/*.{ts,tsx}` | All TypeScript files | `src/app.ts`, `src/App.tsx` |
| `{src,lib}/**/*.ts` | All `.ts` in `src/` or `lib/` | `lib/utils.ts` |
| `tests/**/*.test.ts` | Test files anywhere under `tests/` | `tests/unit/auth.test.ts` |

**Patterns are matched against relative paths from the project root.**

---

## Loading Behavior

### Unconditional rules (no `paths:` field)
Load at session startup alongside `CLAUDE.md`. Claude has them in context for the
entire session. Use for project-wide conventions.

### Path-scoped rules
Load on demand when Claude reads a matching file. Not in context otherwise.
Use for area-specific conventions (language-specific, layer-specific, etc.).

### Load order
1. Personal rules at `~/.claude/rules/` (load first)
2. Project rules at `.claude/rules/` (load after; higher effective priority)
3. Both before any CLAUDE.md files

Later-loaded content has higher effective priority when instructions conflict.

---

## Organizing Rules by Domain

### By code layer
```
.claude/rules/
├── api.md          paths: src/api/**
├── domain.md       paths: src/domain/**
├── database.md     paths: src/db/**
└── frontend.md     paths: src/ui/**
```

### By file type
```
.claude/rules/
├── typescript.md   paths: **/*.{ts,tsx}
├── python.md       paths: **/*.py
├── sql.md          paths: **/*.sql
└── tests.md        paths: **/*.test.*
```

### Mixed unconditional + path-scoped
```
.claude/rules/
├── global.md       (no paths — always loaded)
├── security.md     (no paths — security applies everywhere)
├── react.md        paths: src/components/**/*.tsx
└── migrations.md   paths: db/migrations/**/*.sql
```

---

## Symlink Support

`.claude/rules/` supports symlinks for sharing rules across projects:

```bash
# Share a rules directory from a central location
ln -s ~/company-standards/claude-rules .claude/rules/shared

# Share a single rule file
ln -s ~/shared-rules/security.md .claude/rules/security.md
```

Circular symlinks are detected and handled gracefully.

---

## Excluding Rules in Monorepos

Use `claudeMdExcludes` in `.claude/settings.local.json` to skip specific CLAUDE.md
or rules files when they're not relevant to the current working directory:

```json
{
  "claudeMdExcludes": [
    "**/other-team/.claude/rules/**",
    "/home/user/monorepo/legacy-service/CLAUDE.md"
  ]
}
```

- Patterns match against absolute paths
- Settings live in `settings.local.json` (gitignored) for personal exclusions,
  or `settings.json` (committed) for team-wide exclusions
- Org-managed CLAUDE.md files cannot be excluded

---

## Debugging

### Check what loaded
Run `/memory` in any Claude Code session. This shows:
- Every CLAUDE.md file that was loaded
- Every rules file that was loaded
- The full content Claude received from each

### Common issues

**Rule not loading:**
- Check the `paths:` glob pattern with a glob tester
- Confirm the file was actually read via the Read tool (not just written to)
- Verify YAML frontmatter is valid — unquoted `*` or `{` patterns will silently fail

**Rule loading but not followed:**
- Make the instruction more specific and verifiable
- Move it earlier in the file (first is highest attention)
- Check for conflicting instructions in other loaded files
- Consider whether it belongs in settings `permissions.deny` for hard enforcement

**Too many rules loading:**
- Add `paths:` frontmatter to restrict context-specific rules
- Use `claudeMdExcludes` to suppress irrelevant ancestor files
