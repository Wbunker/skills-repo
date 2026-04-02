# Rule Authoring Guide

Detailed guidance for writing CLAUDE.md files and rules that Claude reliably follows.

## Table of Contents
1. [Structure and organization](#structure-and-organization)
2. [Specificity patterns](#specificity-patterns)
3. [Size management](#size-management)
4. [Progressive disclosure with imports](#progressive-disclosure-with-imports)
5. [What to include vs exclude](#what-to-include-vs-exclude)
6. [Personal vs project rules](#personal-vs-project-rules)
7. [Conflict and precedence](#conflict-and-precedence)
8. [Templates](#templates)

---

## Structure and Organization

Use markdown headers and bullets to group related instructions. Claude follows organized,
scannable rules more reliably than dense paragraphs.

```markdown
# Project: Auth Service

## Build & test              ← Group by workflow
- ...

## Code conventions          ← Group by concern
- ...

## Architecture constraints  ← Group by concern
- ...
```

Order matters: put the most important, most frequently relevant instructions first.
Claude reads the whole file but earlier content has more weight.

---

## Specificity Patterns

Rules work when they're specific enough that both you and Claude can verify compliance.

### The verification test
Ask: "Could I look at Claude's output and know for certain whether it followed this?"

| Fails the test | Passes the test |
|----------------|-----------------|
| "Write clean code" | "Functions must not exceed 30 lines; extract helpers when needed" |
| "Handle errors properly" | "Every async function must have try/catch; log errors with `logger.error(err, context)`" |
| "Follow the project structure" | "New services go in `src/services/`, interfaces in `src/types/`" |
| "Document your changes" | "Add a JSDoc comment to every exported function" |

### Constraint vs instruction
Constraints ("don't X") are easier to verify than instructions ("do X well").
Mix both:
```markdown
- NEVER import directly from `src/internal/` — use the public API in `src/api/`
- Use `zod` for all input validation — no manual `typeof` checks
- New database queries must go through the repository layer, not called directly from handlers
```

### Giving Claude the "why"
When a rule exists for a non-obvious reason, include it. Claude uses context to apply rules
sensibly in edge cases:

```markdown
- Do not modify files in `generated/` — these are auto-generated from the schema and will
  be overwritten on next build
- Use `Date.now()` not `new Date()` for timestamps — the codebase normalizes on ms integers
  and mixing formats has caused bugs
```

---

## Size Management

**Guideline:** Under 200 lines per CLAUDE.md, under 500 lines per rules file.

Beyond these limits, adherence degrades — Claude has limited attention for very long
instructions files, and the most important rules get diluted.

### Signs your CLAUDE.md is too long
- It includes content that applies to only one part of the codebase
- It restates things Claude already knows (e.g., "write tests for your code")
- It duplicates content from your README or existing docs

### Strategies for trimming
1. **Delete obvious rules** — if Claude would do it anyway, don't say it
2. **Replace with @imports** — link to existing docs instead of copying content
3. **Move to path-scoped rules** — frontend rules don't need to load for backend work
4. **Move to skills** — if instructions only apply to a specific workflow, use a skill

---

## Progressive Disclosure with Imports

The `@path/to/file` syntax lets you reference external docs inline. Claude receives
the imported content as if it were written directly in CLAUDE.md.

### Best uses for @imports

**Import your README** instead of duplicating its overview:
```markdown
# Project context
@README.md
```

**Import existing runbooks** so you maintain them in one place:
```markdown
## Deployment process
@docs/deployment-runbook.md
```

**Share rules across projects** from your personal files:
```markdown
@~/.claude/shared/git-conventions.md
```

**Layer personal overrides** on top of team rules:
```markdown
# Team rules (below)
@.claude/team-rules.md

# My local overrides (not committed — in CLAUDE.local.md)
@~/.claude/personal-preferences.md
```

### Import resolution
- Relative paths resolve relative to the importing file
- `~` expands to the home directory
- Supports up to 5 hops of recursive imports
- Circular imports are detected and stopped

---

## What to Include vs Exclude

### High-value content

**Project-specific commands** that Claude can't guess:
```markdown
- Run tests: `./scripts/test.sh --coverage` (not `npm test` — we use a wrapper)
- Lint: `make lint` (runs eslint + prettier + type-check together)
```

**Non-obvious constraints**:
```markdown
- Do not use `fetch` directly — use the wrapper in `src/lib/http.ts` which handles auth tokens
- All feature flags must be declared in `src/config/flags.ts` before use
```

**Architectural decisions**:
```markdown
- This is a hexagonal architecture — domain logic in `src/domain/`, adapters in `src/adapters/`
- Database models and API schemas are kept intentionally separate (we've been bitten by coupling)
```

**Workspace conventions**:
```markdown
- Monorepo: each package under `packages/` has its own `tsconfig.json` and `package.json`
- Cross-package imports must go through published interfaces in `packages/shared/`
```

### Low-value content (omit)

- Generic advice: "write readable code", "add error handling"
- Things Claude already knows: "functions should have a single responsibility"
- Content duplicated from README — import instead: `@README`
- Linting rules — enforce via a linter tool, not instructions
- Credentials, API keys, or secrets of any kind
- Session-specific context that changes frequently

---

## Personal vs Project Rules

### Personal rules (`~/.claude/CLAUDE.md`, `~/.claude/rules/`)
Good for preferences that apply across all your work:
```markdown
# My preferences
- Always show me a summary of changes before making them when the scope is large
- Prefer explicit types over inference in TypeScript
- Use `const` by default; explain when you choose `let`
```

### Project rules (`./CLAUDE.md`, `./.claude/rules/`)
Good for project-specific constraints that the whole team benefits from:
```markdown
# Project conventions
- This project targets ES2020 — no optional chaining (?.) in runtime code
- We use Prisma for all DB access — raw SQL queries need a review comment explaining why
```

### Personal project overrides (`./CLAUDE.local.md`)
Auto-gitignored. Use for your personal preferences within a specific project:
```markdown
# My local overrides for this project
- Don't ask me to confirm before running tests — just run them
- I prefer shorter variable names here; the team style guide is overly verbose
```

---

## Conflict and Precedence

When multiple files have conflicting instructions, later-loaded files take precedence:

1. Org-wide managed CLAUDE.md (highest authority, cannot be excluded)
2. Personal rules (`~/.claude/rules/`)
3. Project rules (`.claude/rules/`)
4. Project CLAUDE.md (`./.claude/CLAUDE.md` or `./CLAUDE.md`)
5. Ancestor CLAUDE.md files (walked up from working directory)
6. Subdirectory CLAUDE.md files (loaded on demand)

**Tip:** If you find yourself writing "override the personal rule about X", that's a signal
the personal rule is too broad. Narrow it with a path-scoped rule instead.

---

## Templates

### Minimal project CLAUDE.md
```markdown
# [Project Name]

## Build & test
- Tests: `[command]`
- Lint: `[command]`
- Dev server: `[command]`

## Conventions
- [Key naming/file placement rule]
- [Key dependency or library rule]

## Non-obvious gotchas
- [Thing that would surprise someone new to this codebase]
```

### Personal CLAUDE.md
```markdown
# My Claude preferences

## Communication style
- [Verbosity preferences, summary behavior, etc.]

## Code style defaults
- [Language-specific preferences that apply everywhere]

## Workflow preferences
- [How I like to work — confirm before large changes, etc.]
```

### Team CLAUDE.md for a monorepo
```markdown
# [Company] / [Repo]

## Getting around
- Each service is under `services/[name]/`; each has its own README
- Shared libraries in `libs/` — see @libs/README.md

## Build system
@docs/build-system.md

## Contributing
@CONTRIBUTING.md

## Conventions
- [Cross-cutting conventions that apply repo-wide]
```
