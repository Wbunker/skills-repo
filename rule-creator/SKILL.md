---
name: rule-creator
description: >
  Create or improve Claude Code rules and CLAUDE.md files. Use when the user wants
  to write a CLAUDE.md, add rules to a project, set up the .claude/rules/ directory,
  create path-scoped rules that only activate for certain files, write personal or
  global rules, use @import syntax to split large instruction files, debug why
  Claude isn't following instructions, or understand what belongs in rules vs skills
  vs agents. Also use when the user asks about "memory files", "project instructions",
  "how to tell Claude to always do X", or "how to make Claude remember my preferences".
  Covers all scopes (project, personal, org-wide), path frontmatter, glob patterns,
  import syntax, best practices for specificity and size, and what to include vs exclude.
---

# Rule Creator

Claude Code rules are Markdown files that give Claude persistent instructions — loaded
at the start of every session (or on demand for path-scoped files). They're the right
tool when you want Claude to always follow certain conventions, workflows, or constraints
without having to repeat them in every prompt.

## Quick Reference

| Goal | Go to |
|------|-------|
| Write a CLAUDE.md for a project | [File placement](#file-placement) + [Authoring guide](references/authoring-guide.md) |
| Set up `.claude/rules/` for modular rules | [Rules directory](references/rules-directory.md) |
| Create rules that only apply to certain files | [Path-scoped rules](references/rules-directory.md#path-scoped-rules) |
| Import external docs into CLAUDE.md | [Import syntax](#import-syntax) |
| Know what to put in rules vs skills vs agents | [Rules vs other tools](#rules-vs-other-tools) |
| Debug why Claude isn't following a rule | Run `/memory` in the session to see what loaded |

## Decision Tree

```
What does the user need?
│
├── "Tell Claude to always follow X in this project"
│   → Write/update ./CLAUDE.md or ./.claude/CLAUDE.md
│   → See: Authoring guide
│
├── "My CLAUDE.md is getting long / hard to manage"
│   → Split into .claude/rules/ files by topic
│   → Or use @import to reference external docs
│   → See: Rules directory
│
├── "Rules should only apply to certain files (e.g., frontend vs backend)"
│   → Use path-scoped rules with paths: frontmatter
│   → See: Path-scoped rules
│
├── "My preferences across all projects"
│   → Write ~/.claude/CLAUDE.md (personal) or ~/.claude/rules/
│   → See: File placement
│
├── "Claude isn't following a rule I wrote"
│   → Run /memory to confirm the file loaded
│   → Check: is the rule specific enough to verify?
│   → See: Writing effective rules
│
└── "Instructions only needed for one task, not every session"
    → Use a skill instead (skills load on demand, not always)
    → See: Rules vs other tools
```

## File Placement

| Scope | Path | Notes |
|-------|------|-------|
| Project (team) | `./CLAUDE.md` or `./.claude/CLAUDE.md` | Commit to git; shared with team |
| Project (personal) | `./CLAUDE.local.md` | Auto-gitignored; your local overrides |
| Personal (all projects) | `~/.claude/CLAUDE.md` | Applies everywhere |
| Modular project rules | `.claude/rules/*.md` | Split by topic; supports path scoping |
| Personal modular rules | `~/.claude/rules/*.md` | Applies everywhere |
| Org-wide (IT managed) | `/etc/claude-code/CLAUDE.md` (Linux) | Cannot be excluded by users |

**Loading order:** Claude walks up the directory tree from the current working directory,
collecting all CLAUDE.md files. More specific (deeper) locations load after broader ones,
so project rules override personal rules when there's a conflict.

## Import Syntax

Use `@path/to/file` in any CLAUDE.md to include another file inline. Keeps the main file
lean while referencing detailed docs that already exist.

```markdown
# Project Instructions
See @README for project overview and architecture.

# Build process
@docs/build-instructions.md

# Personal preferences (not committed)
@~/.claude/my-preferences.md
```

- Relative paths resolve relative to the importing file
- Supports up to 5 hops of recursive imports
- Good for: importing README, pulling in existing runbooks, sharing rule fragments

## Writing Effective Rules

**The test for a good rule:** Could you verify Claude followed it by looking at the output?

| Vague (hard to follow) | Specific (verifiable) |
|------------------------|----------------------|
| "Format code properly" | "Use 2-space indentation; no trailing whitespace" |
| "Test your changes" | "Run `npm test` before marking anything done" |
| "Keep files organized" | "New API handlers go in `src/api/handlers/`" |

**Size guidelines:**
- Under 200 lines per CLAUDE.md (adherence degrades past this)
- Under 500 lines per rules file
- If growing large: split with `.claude/rules/` or use `@` imports

**What to include:**
- Build, test, and lint commands for this project
- Non-obvious architectural decisions and constraints
- File structure conventions Claude can't infer from the code
- Project-specific tool or API patterns
- Things that surprised you when you first worked on the project

**What to leave out:**
- Generic best practices Claude already knows
- Sensitive credentials or API keys
- Instructions only relevant for one specific session (use a skill instead)
- Content already in README — import it with `@README` instead
- Style enforcement — use a linter + hook rather than a rule (more reliable)

## Rules vs Other Tools

| Use | When |
|-----|------|
| **CLAUDE.md / rules** | Conventions that apply to most/all sessions — code style, build commands, architectural constraints |
| **Skill** | Task-specific workflows that only matter sometimes — loaded on demand, not always in context |
| **Agent** | Isolated, self-contained work in its own context window — background tasks, restricted tool access |
| **permissions.deny in settings** | Hard enforcement — blocking specific tools or commands regardless of Claude's judgment |

Rules are context, not enforcement. For hard blocks on tools or file paths, use
`permissions.deny` in `.claude/settings.json` instead.

## Common Patterns

### Minimal project CLAUDE.md

```markdown
# Project: My API Service

## Build & test
- Run tests: `npm test`
- Lint: `npm run lint`
- Start dev server: `npm run dev`

## Conventions
- All API handlers live in `src/handlers/`
- Use `zod` for input validation at every API boundary
- Return errors as `{ error: string, code: string }`

## Non-obvious gotchas
- The `config/` directory is generated at runtime — don't edit it
- Integration tests require `docker-compose up` first
```

### Splitting a large CLAUDE.md

Instead of one large file, break by concern:
```
.claude/rules/
├── testing.md        # Test commands, coverage requirements, patterns
├── code-style.md     # Naming, formatting, linting
├── architecture.md   # Layer boundaries, module constraints
└── api/
    ├── rest.md       # REST conventions
    └── graphql.md    # GraphQL patterns
```

### Path-scoped rule (frontend only)

```yaml
---
paths:
  - "src/components/**/*.tsx"
  - "src/pages/**/*.tsx"
---

# Frontend conventions
- Use Tailwind for all styling — no inline styles
- Components must have a named export (not default)
- Use React.FC<Props> with explicit Props interface
```

For full path-scoped rule syntax and glob patterns, see [rules directory reference](references/rules-directory.md).

## Debugging

Run `/memory` in any Claude Code session to see exactly which CLAUDE.md and rules
files were loaded. Use this when Claude seems to be ignoring an instruction — it
confirms whether the file loaded and shows the full content Claude received.
