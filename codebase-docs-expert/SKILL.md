---
name: codebase-docs-expert
description: Expert in software project and GitHub repository documentation. Use this skill whenever the user asks about README files, CLAUDE.md or AGENTS.md setup, architecture documentation, ADRs (architecture decision records), API docs, documentation-as-code, making a codebase understandable to AI tools, or auditing what documentation a project is missing. Also trigger for questions like "what docs do I need", "how should I document my repo", "how do I make my codebase AI-friendly", "help me write a CLAUDE.md", "document this project", or "what's missing from my documentation". Based on the Diataxis framework, GitHub documentation standards, and current AI-coding-assistant best practices.
---

# Codebase Documentation Expert

Covers the full documentation ecosystem for software projects: what to write, for whom, in what format, and how to make it useful to both humans and AI coding assistants.

Key frameworks: **Diataxis** (four documentation types), **docs-as-code** (version-control and CI everything), **AI-context files** (CLAUDE.md / AGENTS.md).

## Documentation Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                    DOCUMENTATION ECOSYSTEM                          │
│                                                                     │
│  FOR HUMANS                          FOR AI AGENTS                  │
│  ──────────────────────              ──────────────────────         │
│  README.md        (entry point)      CLAUDE.md / AGENTS.md          │
│  CONTRIBUTING.md  (contributors)     Subdirectory CLAUDE.md files   │
│  CHANGELOG.md     (users/ops)        Type annotations (code)        │
│  SECURITY.md      (reporters)        Module docstrings              │
│  CODE_OF_CONDUCT  (community)        Named constants                │
│  docs/ directory  (deep reference)   .claude/skills/               │
│                                                                     │
│  DIATAXIS FOUR TYPES (both audiences)                               │
│  ──────────────────────────────────────────────────────────────     │
│  TUTORIALS          HOW-TO GUIDES     REFERENCE       EXPLANATION   │
│  (learning)         (working)         (working)       (learning)    │
│  Student follows    Solve real        Neutral facts   Conceptual    │
│  guided lesson      world problem     and specs       background    │
│                                                                     │
│  GITHUB SURFACES AUTOMATICALLY                                      │
│  ──────────────────────────────                                     │
│  README.md → repo homepage    CONTRIBUTING.md → new PR/issue flow   │
│  SECURITY.md → Security tab   CODEOWNERS → auto reviewer assignment │
│  LICENSE → prominently shown  .github/ISSUE_TEMPLATE/ → new issues  │
└─────────────────────────────────────────────────────────────────────┘
```

## Quick Reference

| Task | Reference |
|------|-----------|
| What documentation types exist? What should every project have? | [diataxis-and-doc-types.md](references/diataxis-and-doc-types.md) |
| Writing CLAUDE.md, AGENTS.md, or other AI context files | [ai-context-files.md](references/ai-context-files.md) |
| GitHub repo standards, README anatomy, community health files | [github-standards.md](references/github-standards.md) |
| Tooling, automation, CI/CD for docs, docs-as-code practices | [documentation-as-code.md](references/documentation-as-code.md) |
| Making code and architecture understandable to AI coding tools | [ai-readable-codebase.md](references/ai-readable-codebase.md) |
| Diagram types (C4, Mermaid, sequence, ERD, state, ASCII) — which to use and how to write AI-readable diagrams | [diagrams.md](references/diagrams.md) |
| Templates and checklists (README, ADR, CLAUDE.md, PR template) | [templates.md](references/templates.md) |

## Reference Files

| File | Key Topics |
|------|-----------|
| `diataxis-and-doc-types.md` | Diataxis (tutorials/how-to/reference/explanation), all doc types per project phase, priority matrix, common anti-patterns |
| `ai-context-files.md` | CLAUDE.md/AGENTS.md best practices, what to include/exclude, multi-tool ecosystem, size constraints, import syntax, skills |
| `github-standards.md` | README anatomy, files GitHub auto-surfaces, wikis vs. docs/, community health files, CODEOWNERS, issue templates |
| `documentation-as-code.md` | Docs in version control, PR-based review, CI link-checking/linting, automated API doc generation, Vale, Repomix |
| `ai-readable-codebase.md` | Context window design, directory structure, docstrings, type annotations, architecture docs for AI, test infrastructure as docs |
| `diagrams.md` | Text-based vs. image diagrams, C4 model (L1/L2/L3), Mermaid types (sequence/ERD/state/class/C4), ASCII art, AI-readable diagram rules |
| `templates.md` | Ready-to-use templates: README, CLAUDE.md, ADR, PR description template, CONTRIBUTING.md outline |

## Core Decision Trees

### What Documentation Does This Project Need?

```
What stage is this project at?
├── Brand new / prototype
│   ├── README.md (what it is + how to run it)
│   ├── LICENSE
│   └── CLAUDE.md / AGENTS.md (if using AI tools)
├── Open source / accepting contributors
│   ├── All of the above, plus:
│   ├── CONTRIBUTING.md
│   ├── CODE_OF_CONDUCT.md
│   ├── SECURITY.md
│   ├── CHANGELOG.md
│   └── .github/ (issue templates, PR template)
└── Production system / team product
    ├── All of the above, plus:
    ├── Architecture doc (ARCHITECTURE.md or docs/architecture/)
    ├── ADRs (docs/decisions/)
    ├── API reference (OpenAPI, generated from code)
    ├── Runbook / operations guide
    └── Onboarding guide for new engineers
```

### Which Documentation Type Should I Write?

```
Who is the reader and what are they trying to do?
├── Wants to learn by doing → Tutorial
│   └── Guide them through a task; outcome matters more than explanation
├── Knows the system, solving a specific problem → How-to Guide
│   └── Step-by-step; assume competence; don't explain why
├── Looking up a fact, option, or spec → Reference
│   └── Neutral, complete, consistent structure; no narrative
└── Wants to understand the system deeply → Explanation
    └── Background, rationale, trade-offs, "why it works this way"

CRITICAL: Each document should be exactly ONE of these types.
Mixing types (e.g., tutorial with embedded explanation) is the #1 cause of confusing docs.
```

### Is My CLAUDE.md / AGENTS.md the Right Length?

```
How many lines is your AI context file?
├── Under 100 lines → Good target for most projects
├── 100–300 lines → Acceptable for large/complex repos; review for bloat
└── Over 300 lines → Too long; AI will ignore parts of it
    └── Audit each line: "Would Claude make a mistake without this?"
        ├── No → Delete it
        ├── Yes, but Claude already knows this convention → Delete it
        └── Yes, and it's non-obvious → Keep it

Signs of a bloated CLAUDE.md:
- Restating standard language conventions (PEP 8, etc.)
- Generic platitudes ("write clean code", "be helpful")
- Detailed API docs that should live in reference files
- Content that changes frequently
- Rules without a positive alternative
```

### How Should I Structure Docs for AI vs. Human Readers?

```
Is this documentation primarily for AI coding assistants?
├── Yes (CLAUDE.md, AGENTS.md, subdirectory context files)
│   ├── Lead with build/test/lint commands (highest signal)
│   ├── Use imperative bullet points, not prose paragraphs
│   ├── Be explicit about non-obvious conventions only
│   ├── Reference longer docs with @path/to/file instead of embedding
│   └── Test it: if Claude makes a mistake, add the rule; otherwise don't
└── No (README, architecture docs, tutorials)
    ├── Structure with Diataxis (pick one type per document)
    ├── Use headings, tables, code blocks — not walls of prose
    ├── Put the most important information first (inverted pyramid)
    ├── Include runnable examples that are tested in CI
    └── Link to deeper content rather than embedding everything
```

### Which Diagram Type Should I Use?

```
What question are you trying to answer?
├── What does the system do and who uses it? → C4 Level 1 Context
├── What services/apps make up the system? → C4 Level 2 Container
├── What calls what, in what order? → Sequence diagram
├── What fields/tables exist and how are they related? → ERD
├── What states can an object be in? → State machine diagram
├── How do classes relate (OOP)? → Class diagram
├── How does data flow step-by-step? → Flowchart
└── Need to embed in CLAUDE.md, ADR, or code comment? → ASCII art

Format rule: AI tools can READ text-based diagrams (Mermaid, ASCII).
They CANNOT reliably read PNG/SVG image files.
Use Mermaid in ```mermaid code blocks for AI-readable diagrams.
See diagrams.md for full reference with examples.
```

### Do I Have an Architecture Documentation Problem?

```
Can a new engineer understand the system from your docs?
├── Can they name the 5–10 major components and what each does? → Architecture doc
├── Do they know why key design decisions were made? → ADRs
├── Can they deploy and operate the system? → Runbook
└── Can they get their dev environment working in < 1 hour? → Onboarding guide

For AI tools specifically:
├── Would Claude reinvent a deliberate constraint? → Add an ADR explaining why
├── Does Claude generate code for the wrong architecture? → Add ARCHITECTURE.md
└── Does Claude use wrong commands? → Check CLAUDE.md has exact build/test invocations
```

## Key Concepts at a Glance

### The Diataxis Four (one sentence each)

| Type | One-sentence rule |
|------|------------------|
| Tutorial | Take the learner by the hand through a meaningful, achievable task |
| How-to Guide | A series of steps to achieve a specific goal — assume competence, skip backstory |
| Reference | Describe the machinery, neutrally and completely, structured for lookup not reading |
| Explanation | Discuss the topic from multiple angles, give context, explain trade-offs and history |

### Documentation Priority Matrix

| Document | Audience | Priority | Format |
|----------|---------|---------|--------|
| README.md | Everyone | Critical | Markdown |
| LICENSE | Everyone | Critical | Plain text |
| CLAUDE.md / AGENTS.md | AI agents | Critical if using AI tools | Markdown |
| CONTRIBUTING.md | Contributors | Critical for OSS | Markdown |
| SECURITY.md | Security reporters | Critical | Markdown |
| CHANGELOG.md | Users, operators | High | Markdown |
| Architecture doc | Developers | High | Markdown + diagrams |
| ADRs | Developers, future maintainers | High | Markdown |
| API reference | API consumers | High | OpenAPI / generated |
| Code docstrings | AI agents, developers | High | Language-native |
| Runbook | Operators | High for deployed systems | Markdown |
| How-to guides | Users, developers | Medium-High | Markdown |
| Tutorials | New users | Medium | Markdown |
| Onboarding guide | New team members | Medium | Markdown |
| CODE_OF_CONDUCT.md | Community | Medium for OSS | Markdown |

### Anti-Patterns Quick List

- **Wall of text**: no structure, can't scan → use headings, tables, bullets
- **Type mixing**: tutorial + explanation in one page → one Diataxis type per doc
- **Stale docs left in place**: outdated content actively misleads AI → archive or delete
- **Broken examples**: code snippets that don't run → treat examples as tests
- **CLAUDE.md bloat**: too many rules → AI ignores them; ruthlessly prune
- **Docs divorced from code**: separate repo drifts → colocate; update together in PRs
- **README as dumping ground**: 5,000-word README → hub with links to `docs/`
- **No error documentation**: silent failures → document common errors and fixes
