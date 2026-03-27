# AI Context Files: CLAUDE.md, AGENTS.md, and the Full Ecosystem
## Writing AI-Readable Instructions for Coding Assistants

---

## Why AI Context Files Exist

AI coding assistants have no persistent memory between sessions. Every session starts from zero — the assistant has no knowledge of your conventions, commands, constraints, or architecture unless you provide it. AI context files are the mechanism for loading that project knowledge at the start of every session.

**The core design constraint**: context files compete with code and conversation for the AI's limited context window. Every line you add costs something. The information density must be high.

---

## The Multi-Tool Ecosystem

Every major AI coding tool reads a project-level context file. They differ in name, location, and behavior:

| File | Tool(s) | Notes |
|------|---------|-------|
| `CLAUDE.md` | Claude Code | Hierarchical: `~/.claude/CLAUDE.md` (global), project root, subdirectories. Supports `@path/to/file` imports |
| `AGENTS.md` | OpenAI Codex, GitHub Copilot, Cursor, Gemini CLI, Windsurf, Aider, Claude Code | Cross-tool universal standard; stewarded by Agentic AI Foundation under Linux Foundation |
| `.github/copilot-instructions.md` | GitHub Copilot | Scoped by glob patterns |
| `GEMINI.md` | Gemini CLI | Merges from multiple directory levels |
| `.cursor/rules/` | Cursor | Activation modes: Always On, Auto Attached, Manual |
| `.windsurfrules` | Windsurf | 6,000 char per file / 12,000 char combined limit |

### Recommended Layered Strategy

```
your-project/
├── AGENTS.md                        ← Universal instructions (primary, all tools read this)
├── CLAUDE.md                        ← Claude-specific additions only (or just use AGENTS.md)
├── .github/copilot-instructions.md  ← If you use Copilot
└── backend/
    └── CLAUDE.md                    ← Backend-specific conventions (loaded only in backend context)
```

If you only use Claude Code, one `CLAUDE.md` at the root is sufficient. If your team uses multiple AI tools, maintain `AGENTS.md` as the primary and use tool-specific files only for tool-specific features.

---

## CLAUDE.md: What to Include

### Must-Have Content (High Signal)

**1. Build, test, lint, and run commands** — the highest-value content. Exact commands, not descriptions.

```markdown
## Commands
- Build: `mvn package -DskipTests`
- Test: `mvn test`
- Test single: `mvn test -Dtest=OrderHandlerTest`
- Lint: `mvn checkstyle:check`
- Local run: `sam local invoke OrderFunction --event events/test.json`
```

**2. Tech stack with versions** — explicit, not inferred.

```markdown
## Stack
- Java 11 (Corretto), Maven 3.8
- AWS Lambda + API Gateway + DynamoDB
- JUnit 5, Mockito 4, Jackson 2.13
```

**3. Directory layout** — especially important for monorepos.

```markdown
## Structure
- `order-function/` — order processing Lambda (deploys independently)
- `payment-function/` — payment Lambda
- `shared/` — shared models and utilities (not deployed directly)
- `template.yaml` — SAM/CloudFormation template for all functions
```

**4. Critical non-obvious conventions** — things that deviate from standard defaults.

```markdown
## Conventions
- All DynamoDB writes MUST use conditional expressions (see ADR-0003)
- Never use `--force` on any git operation
- Integration tests (`*IT.java`) require `AWS_PROFILE=test` set
```

**5. Repository etiquette** — branch naming, commit format, PR process.

```markdown
## Git
- Branch: `feat/`, `fix/`, `chore/` prefix
- Commit: conventional commits (`feat(orders): add retry logic`)
- PRs require one approval + passing CI
```

---

## CLAUDE.md: What to Exclude

**Already-known conventions**: Don't tell Claude to "use PEP 8" or "write clean code" — it already knows. Only document deviations from widely-known standards.

**Generic platitudes**: "Be helpful", "write readable code", "add comments" — these cost context and add no value.

**API documentation**: Link to it instead. `See @docs/api-reference.md for endpoint details.` The AI can load it when needed.

**Frequently-changing content**: Configuration values, dependency versions, environment-specific settings — these go in actual config files, not CLAUDE.md.

**Anything Claude gets right without it**: Test empirically. If Claude writes your DynamoDB queries correctly without an explicit rule, don't add the rule.

**Rules without alternatives**: "Never use X" is worse than "Never use X; use Y instead."

---

## Size and Adherence Constraints

- **Target under 150 lines** for most projects; absolute maximum ~300 lines
- Research shows frontier LLMs can reliably follow ~150–200 instructions total. Claude Code's system prompt already uses ~50 slots.
- **The bloat penalty is real**: when CLAUDE.md is too long, Claude ignores parts of it. The middle and end of a long context file are followed less reliably than the beginning.
- **Production example**: HumanLayer's production CLAUDE.md is under 60 lines.
- Test your CLAUDE.md: if Claude still makes a mistake after you added a rule, either the file is too long or the phrasing is ambiguous.

### The Audit Test

For each line in your CLAUDE.md, ask: *"Would Claude make a specific, demonstrable mistake if I deleted this line?"*

- No → Delete it
- Yes, but it's a standard convention Claude already knows → Delete it
- Yes, and it's non-obvious to someone who hasn't read the codebase → Keep it

---

## Progressive Disclosure: Imports and Skills

CLAUDE.md supports two mechanisms for loading additional context on demand rather than always:

### @path imports

```markdown
## Architecture
See @docs/ARCHITECTURE.md for the system component map.

## API Reference
See @docs/api/orders.md for the orders API spec.
```

Claude loads the referenced file when working on related tasks. This avoids bloating every session with content that's only relevant to specific tasks.

### Skills (`.claude/skills/`)

For domain knowledge that requires detailed reference material (e.g., how to write Kinesis event handlers, how to use a specific internal library), create a skill:

```
.claude/skills/
  kinesis-patterns/
    SKILL.md            ← loaded when relevant
    references/
      event-handling.md ← loaded on demand
```

Skills appear in Claude's available_skills list and are consulted only when the task requires them. They are the right mechanism for content that's too long for CLAUDE.md but too specialized to load every session.

---

## Hierarchical CLAUDE.md (Subdirectory Files)

Claude Code reads CLAUDE.md files at multiple levels and merges them:

```
~/.claude/CLAUDE.md          ← Global defaults (your preferences across all projects)
your-project/CLAUDE.md       ← Project-level rules
your-project/backend/CLAUDE.md  ← Backend-specific rules (loaded when in backend context)
your-project/frontend/CLAUDE.md ← Frontend-specific rules
```

**Good uses for subdirectory CLAUDE.md files:**
- Backend: database conventions, service layer patterns, auth requirements
- Frontend: component structure, state management patterns, CSS conventions
- Infrastructure: deployment conventions, IaC patterns, security requirements
- Scripts: scripting conventions, required env vars, testing approach

---

## AGENTS.md: Cross-Tool Best Practices

AGENTS.md follows the same content rules as CLAUDE.md. Additional considerations:

- Use common Markdown that renders correctly in all tools
- Avoid Claude-specific syntax (`@path/to/file` is Claude-only; other tools ignore it)
- Keep it tool-agnostic: describe *what* to do, not *how Claude specifically* should behave
- Test with each tool your team actually uses

### AGENTS.md minimal template

```markdown
# Project: My Project

## Stack
- Language/framework: ...
- Key dependencies: ...

## Commands
- Install: ...
- Build: ...
- Test: ...
- Lint: ...

## Architecture
Brief description of main components and how they relate.
See docs/ARCHITECTURE.md for the full system diagram.

## Conventions
- [List only non-obvious deviations from standard practice]

## Important Constraints
- [List only things that would cause real problems if violated]
```

---

## Global vs. Project Context

### `~/.claude/CLAUDE.md` (Global)

Preferences that apply across all your projects:

```markdown
## My defaults
- I prefer concise responses without trailing summaries
- For Python: always use type hints
- For shell scripts: always use `set -euo pipefail`
- My preferred test frameworks: pytest (Python), JUnit 5 (Java), Jest (JS)
```

### Project CLAUDE.md

Project-specific context only. Don't duplicate global defaults.

---

## Diagnosing Broken AI Behavior

When Claude consistently makes a mistake despite CLAUDE.md instructions, the root cause is usually one of:

| Symptom | Likely Cause | Fix |
|---------|-------------|-----|
| Ignores a specific rule | Rule is buried in a long file | Move it to the top; trim file |
| Gets commands wrong | Commands described, not quoted | Use exact `` `command` `` syntax |
| Uses wrong architecture | Architecture not documented | Add ARCHITECTURE.md + @import |
| Removes deliberate constraints | No ADR explaining the "why" | Write an ADR; reference it from CLAUDE.md |
| Makes mistakes Claude.md doesn't cover | Missing rule | Add the rule with the positive alternative |
| Still makes mistakes after adding rule | File too long | Audit and prune; add emphasis (`IMPORTANT:`) sparingly |
