---
name: codebase-docs-expert
description: >
  Expert in software project documentation — both analyzing existing codebases and
  producing documentation. Provides multiple viewpoints and methodologies for reasoning
  about software systems. Use when asked to: analyze a codebase, document an existing
  system, reverse-engineer architecture from code, create an architecture overview,
  map dependencies, understand how a system works, produce onboarding documentation,
  generate ARCHITECTURE.md, identify system boundaries, document data flows, catalog
  integration points, write README files, set up CLAUDE.md or AGENTS.md, create ADRs,
  audit documentation gaps, make a codebase AI-friendly, or answer "how does this
  codebase work" or "what docs do I need". Works with any language or framework.
  Synthesizes SEI Views and Beyond, C4 Model, Rozanski & Woods viewpoints/perspectives,
  Ousterhout's cognitive load analysis, Diátaxis framework, ADRs, Release It! stability
  patterns, and docs-as-code practices.
---

# Codebase Documentation Expert

Provides multiple viewpoints and methodologies for reasoning about, analyzing, and
documenting software systems. Two complementary modes:

- **Analyze** — Read an existing codebase and produce structured documentation
- **Author** — Write documentation following established frameworks and standards

## Quick Reference

| Goal | Reference |
|------|-----------|
| **Analyzing an existing codebase** | |
| Parallelized full-codebase analysis (16 agents, 5 waves → site-context skill) | [codebase-analysis-orchestration.md](references/codebase-analysis-orchestration.md) |
| Manual 7-phase analysis workflow (single-agent, step-by-step) | [analysis-workflow.md](references/analysis-workflow.md) |
| Viewtype catalog: what to analyze and what questions each view answers | [viewtypes-and-perspectives.md](references/viewtypes-and-perspectives.md) |
| What to prioritize: cognitive load, depth heuristics, ROI | [prioritization-guide.md](references/prioritization-guide.md) |
| **Writing documentation** | |
| Documentation types (Diátaxis) and what every project needs | [diataxis-and-doc-types.md](references/diataxis-and-doc-types.md) |
| Writing CLAUDE.md, AGENTS.md, or other AI context files | [ai-context-files.md](references/ai-context-files.md) |
| GitHub repo standards, README anatomy, community health files | [github-standards.md](references/github-standards.md) |
| Making code and architecture understandable to AI coding tools | [ai-readable-codebase.md](references/ai-readable-codebase.md) |
| Tooling, automation, CI/CD for docs, docs-as-code practices | [documentation-as-code.md](references/documentation-as-code.md) |
| **Both modes** | |
| Which diagram type to use and when (selection guide) | [diagram-selection-guide.md](references/diagram-selection-guide.md) |
| All 13 diagram types: full syntax, examples, and best practices | [diagrams.md](references/diagrams.md) |
| All templates: analysis outputs, doc scaffolds, checklists | [templates.md](references/templates.md) |

## Decision Tree: What Does the User Need?

```
What is the user trying to accomplish?
│
├── ANALYZE an existing codebase
│   ├── "How does this system work?" (full onboarding)
│   │   → Run analysis phases 1-7 → see analysis-workflow.md
│   │   → Produce: System Overview, Container Map, Component Analysis
│   │
│   ├── "I need to fix a bug in X" (targeted understanding)
│   │   → Orient (phase 1), then Trace Runtime (phase 3) focused on X
│   │   → Produce: Sequence diagram of the relevant flow, interface docs
│   │
│   ├── "I need to add a feature" (extension point analysis)
│   │   → Orient, Map Structure (phase 2), Surface Contracts (phase 4)
│   │   → Produce: Component analysis of target area, dependency map
│   │
│   ├── "Where are the risks?" (risk/complexity audit)
│   │   → Orient, Assess Risk (phase 6)
│   │   → Produce: Integration point inventory, complexity hotspot map
│   │
│   └── "Generate an ARCHITECTURE.md" (specific artifact)
│       → Phases 1-3, then produce ARCHITECTURE.md template
│
├── AUTHOR documentation
│   ├── "What docs do I need?" → diataxis-and-doc-types.md § project phases
│   ├── "Help me write a README" → github-standards.md § README anatomy
│   ├── "Set up CLAUDE.md / AGENTS.md" → ai-context-files.md
│   ├── "Write an ADR" → templates.md § ADR template
│   ├── "Make this codebase AI-friendly" → ai-readable-codebase.md
│   ├── "Set up docs CI/CD" → documentation-as-code.md
│   └── "Which diagram type?" → diagrams.md § quick reference
│
└── BOTH (comprehensive documentation effort)
    → Analyze first (phases 1-6), then author using analysis outputs
    → Use templates.md for all output formats
```

## Core Methodological Framework

This skill synthesizes six complementary methodologies. Each provides a different
lens for reasoning about software:

### 1. Viewtype Discipline (SEI Views and Beyond)
Every question maps to a viewtype. Never mix viewtypes in one artifact:
- **Module views** → How is code organized? What depends on what?
- **Runtime views** → What runs, what connects, how does data flow?
- **Allocation views** → Where does code deploy? Who owns what?

### 2. Zoom Levels (C4 Model)
Work top-down through four levels of abstraction:
- **L1 Context** → System boundary, users, external systems
- **L2 Container** → Separately-running processes and data stores
- **L3 Component** → Major functional groupings within a container
- **L4 Code** → Only when specific detail is needed

### 3. Cross-Cutting Perspectives (Rozanski & Woods)
Quality concerns that apply as lenses across all views:
Security, Performance, Availability, Evolution, Scalability,
Observability, Operability, Testability, Data Integrity, Compliance

### 4. Cognitive Load Priority (Ousterhout)
Document what creates the most cognitive load first:
- Deep modules → document the interface, skip internals
- Shallow modules → document everything (they leak complexity)
- Cross-module dependencies → document every non-obvious coupling
- Unknown unknowns → highest priority targets

### 5. Documentation Types (Diátaxis)
Each document serves exactly one purpose:
- **Tutorial** → Learning by doing (guided lesson)
- **How-to** → Solving a specific problem (assume competence)
- **Reference** → Neutral, complete, structured for lookup
- **Explanation** → Background, rationale, "why it works this way"

### 6. Stability Patterns (Release It!)
Every integration point needs failure mode documentation:
Timeout, Circuit Breaker, Retry, Bulkhead, Fallback, Rate Limiting

## Analysis Workflow Summary

```
1. ORIENT        → Tech stack, entry points, project shape
2. MAP STRUCTURE → Modules, layers, dependencies (Module viewtype)
3. TRACE RUNTIME → Request flows, data flow, communication patterns (C&C viewtype)
4. SURFACE CONTRACTS → Interfaces, boundaries, invariants
5. EXCAVATE DECISIONS → Reverse-engineer the "why" (inferred ADRs)
6. ASSESS RISK  → Integration points, failure modes, complexity hotspots
7. PRODUCE ARTIFACTS → Assemble deliverables using templates
```

Full procedures in [analysis-workflow.md](references/analysis-workflow.md).

## Documentation Ecosystem Overview

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
│  ARCHITECTURE VIEWS (both audiences)                                │
│  ──────────────────────────────────────────────────────────────     │
│  Module views          C&C views           Allocation views         │
│  (code structure)      (runtime behavior)  (deployment/teams)       │
│                                                                     │
│  DIAGRAM TYPES (always use Mermaid for AI readability)              │
│  ──────────────────────────────────────────────────────────────     │
│  C4 (L1-L3)   Sequence    ERD    State    Control Flow   Class      │
└─────────────────────────────────────────────────────────────────────┘
```

## Diagram Type Selection

```
What question are you trying to answer?
├── What is inside vs outside the system? → Context diagram (C4 L1)
├── What are the major parts? → Component diagram (C4 L2/L3)
├── What calls what, in what order? → Sequence diagram
├── What states can this object be in? → State diagram
├── How is the data organized? → ERD
├── What does this function do step by step? → Control flow (flowchart)
├── Where does this code execute? → Deployment diagram
├── Why does this software exist? → Use case diagram / actor-goal table
├── What exact rules drive this behavior? → Decision table
├── What meaningful events happen? → Event catalog / flow timeline
├── What breaks if I change this? → Dependency analysis
├── Which service can change this data? → CRUD matrix
├── How do these classes relate (OOP)? → Class diagram
└── Need to embed in CLAUDE.md or code comment? → ASCII art

For detailed guidance on which diagrams to use for your specific goal,
audience, and system type, see diagram-selection-guide.md.
Format rule: Use Mermaid in ```mermaid blocks for AI-readable diagrams.
See diagrams.md for full syntax, examples, and best practices.
```

## Automated Codebase Analysis

This skill includes an installable orchestrator command and worker agent that
automate the full analysis workflow, producing a `site-context` skill in the
target repository.

### Install

```bash
bash ${CLAUDE_SKILL_DIR}/scripts/install.sh
```

This copies to the target project:
- `.claude/commands/analyze-codebase.md` — orchestrator command (invoke with `/analyze-codebase`)
- `.claude/agents/codebase-analyzer.md` — background worker agent

### Run

```
/analyze-codebase
```

Launches 16 agents across 5 waves, producing `.claude/skills/site-context/` with
14 reference files covering all 13 analysis types. See
[codebase-analysis-orchestration.md](references/codebase-analysis-orchestration.md)
for the full wave execution plan and diagram inventory.

## Anti-Patterns

- **Boiling the ocean**: Documenting everything at once → Let user needs guide depth
- **Describing the obvious**: Restating what code says → Focus on the "why"
- **Wrong abstraction level**: Code detail before understanding containers → Follow C4 top-down
- **Mixing viewtypes**: Structure + behavior in one diagram → One viewtype per artifact
- **Type mixing**: Tutorial + explanation in one page → One Diátaxis type per doc
- **CLAUDE.md bloat**: Too many rules → AI ignores them; ruthlessly prune
- **Ignoring failure modes**: Only the happy path → Every integration point gets failure docs
- **Stale docs left in place**: Outdated content misleads → Archive or delete
- **Snapshot without rationale**: Pure structure, no "why" → Always include inferred decisions
