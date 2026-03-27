# Documentation Types and the Diataxis Framework
## What to Write, For Whom, and Why

---

## The Diataxis Framework

Diataxis (developed by Daniele Procida; adopted by Ubuntu, Django, and many others) organizes documentation into four types on two axes:

```
                    ACTION-ORIENTED
                          │
              Tutorials   │   How-to Guides
              (learning)  │   (working)
                          │
ACQUISITION ──────────────┼────────────────── APPLICATION
(studying)                │                   (working)
                          │
              Explanation │   Reference
              (learning)  │   (working)
                          │
                   COGNITION-ORIENTED
```

**The core insight**: each piece of documentation should serve exactly one purpose. Mixing types is the root cause of most confusing documentation.

---

## The Four Types

### 1. Tutorials (Learning-Oriented)

**Purpose**: Help a newcomer learn by doing. The student follows a guided lesson and accomplishes something meaningful under your supervision.

**Characteristics:**
- You are in control; the learner follows your lead
- The task exists to teach, not to accomplish something in the real world
- Success is the learner completing it and feeling capable
- Analogy: a cooking class where the teacher guides you to make a dish

**What to include:**
- A clear, achievable goal stated up front
- Every step spelled out, even the obvious ones (beginners trip on the "obvious")
- Expected output at each stage so learners know they're on track
- No digressions into explanation — keep momentum

**What to avoid:**
- Offering alternatives or options ("you could also...") — this interrupts the guided flow
- Embedding reference material or deep explanation

**Example**: "Build your first REST API with Spring Boot" — a 30-minute guided project for someone who has never used Spring Boot.

---

### 2. How-to Guides (Problem-Oriented)

**Purpose**: Help a competent practitioner accomplish a specific goal. The reader knows what they want to do; your job is to show them how.

**Characteristics:**
- The reader is in control; they have a real task to accomplish
- Assume competence — no need to explain foundational concepts
- Structured as a series of steps
- Analogy: a recipe (not a cooking class) — you have the skills, just need the instructions

**What to include:**
- A clear problem statement in the title ("How to configure OAuth with Okta")
- Steps that achieve the goal, no more
- Brief notes on prerequisites
- Warnings about non-obvious pitfalls

**What to avoid:**
- Explaining why unless it's critical to doing the task correctly
- Background information or conceptual discussion (put that in Explanation)
- Covering every edge case (put those in Reference)

**Example**: "How to add a custom domain to your Vercel deployment" — assumes the reader knows what Vercel is and why they'd want a custom domain.

---

### 3. Reference (Information-Oriented)

**Purpose**: Provide a neutral, complete, authoritative description of the machinery. Structured for lookup, not for reading cover-to-cover.

**Characteristics:**
- Describes the system as it is, not as you wish it were
- No narrative arc; structured consistently for predictable lookup
- Completeness and accuracy are more important than readability
- Analogy: an encyclopedia entry or a man page

**What to include:**
- Every option, parameter, field, and flag
- Data types, default values, valid ranges
- Return values and error codes
- Version notes and deprecations

**What to avoid:**
- Step-by-step instructions (put those in How-to or Tutorial)
- Explanation of trade-offs or background (put that in Explanation)
- Getting-started guidance

**Example**: REST API reference documentation listing every endpoint, HTTP method, query parameters, request/response schemas, and status codes.

---

### 4. Explanation (Understanding-Oriented)

**Purpose**: Deepen understanding. Discuss the topic from multiple angles, provide context, explain trade-offs, and answer "why does it work this way?"

**Characteristics:**
- The reader is studying, not working on a task
- May challenge assumptions or discuss alternatives
- Does not need to tell the reader what to do
- Analogy: an essay or a chapter in a textbook

**What to include:**
- Background and history
- Rationale for design decisions
- Alternative approaches and why they were or weren't chosen
- Conceptual models and mental frameworks
- Links to ADRs for deep-dive decision rationale

**What to avoid:**
- Step-by-step instructions
- Comprehensive reference listings

**Example**: "Why we use event sourcing instead of CRUD" — explains the trade-offs, the team's reasoning, and what problems the approach solves.

---

## Complete Document Type Inventory

### Always Required

| Document | Purpose | Audience |
|----------|---------|---------|
| **README.md** | Entry point; orients every visitor | Everyone |
| **LICENSE** | Legal right to use the code | Everyone |

### Required for Open Source / Public Repos

| Document | Purpose | Audience |
|----------|---------|---------|
| **CONTRIBUTING.md** | How to submit issues and PRs | Contributors |
| **CODE_OF_CONDUCT.md** | Community standards | Community |
| **SECURITY.md** | How to report vulnerabilities privately | Security reporters |
| **CHANGELOG.md** | Release history | Users, operators |

### Required If Using AI Coding Tools

| Document | Purpose | Audience |
|----------|---------|---------|
| **CLAUDE.md** | Context for Claude Code | Claude |
| **AGENTS.md** | Universal AI agent context | All AI tools |
| **Subdirectory CLAUDE.md** | Domain-specific context | Claude (scoped) |

### Required for Production / Team Projects

| Document | Purpose | Audience |
|----------|---------|---------|
| **ARCHITECTURE.md** | System component map | Developers, new joiners |
| **ADRs** (docs/decisions/) | Why key decisions were made | Developers, future maintainers |
| **API Reference** | Interface contracts | API consumers |
| **Runbook** | Deploy, monitor, recover | Operators, on-call |
| **Onboarding Guide** | Get new engineers productive fast | New team members |
| **Glossary** | Project-specific terminology | All audiences |

### Optional / Progressive

| Document | Purpose | When to Add |
|----------|---------|------------|
| **Tutorials** | Learning-oriented guided projects | When users are new to the domain |
| **How-to Guides** | Solving specific problems | When users report confusion on specific tasks |
| **Explanation docs** | Deep background | When "why" questions recur in issues/PRs |
| **.github/ISSUE_TEMPLATE/** | Structured issue creation | When issues lack context |
| **.github/PULL_REQUEST_TEMPLATE.md** | Structured PR descriptions | When PRs lack context |
| **CODEOWNERS** | Automatic reviewer assignment | When you have area ownership |

---

## Documentation Priority by Project Phase

### Phase 1: Prototype / Exploration
Minimum viable documentation:
- README.md (what it is, how to run it)
- LICENSE

### Phase 2: Sharing / Open Source Launch
Add:
- CONTRIBUTING.md
- CODE_OF_CONDUCT.md
- SECURITY.md
- CHANGELOG.md
- .github/ISSUE_TEMPLATE/

### Phase 3: Production System
Add:
- ARCHITECTURE.md
- ADRs for all significant decisions
- Runbook
- Onboarding guide
- API reference docs
- CI-tested code examples

### Phase 4: Developer Platform / API Product
Add:
- Tutorials (getting started)
- How-to guides for common tasks
- Full API reference with OpenAPI spec
- SDK documentation
- Error reference

---

## Architecture Decision Records (ADRs)

ADRs are short documents recording a significant architectural decision: the context, the decision made, and the consequences.

### Why ADRs Matter for AI Tools

ADRs prevent AI from "improving" code by removing deliberately chosen constraints. When Claude sees `@Singleton` on a class, it might remove it for "simplicity" — unless an ADR explains the thread-safety requirement that made it necessary.

### ADR Format (Lightweight)

```markdown
# ADR-0001: Use event sourcing for order state

**Status**: Accepted
**Date**: 2024-03-15
**Deciders**: @alice, @bob

## Context
Our order system requires full audit history for compliance.
CRUD updates lose the intermediate states regulators require.

## Decision
Use event sourcing: persist events (OrderPlaced, OrderShipped, etc.)
and derive current state by replaying them.

## Consequences
- Positive: Complete audit trail; easy temporal queries; decoupled consumers
- Negative: Increased complexity; eventual consistency; event schema migration is hard
- Rejected alternatives: CRUD with audit log table (insufficient for replay)
```

### ADR Storage Conventions

Common locations: `docs/decisions/`, `docs/adr/`, `architecture/decisions/`
Naming: `0001-use-event-sourcing.md` (padded numbers for sort order)
Tools: `adr-tools` CLI, `log4brains` (web UI for browsing ADRs)

---

## Common Anti-Patterns

| Anti-Pattern | Problem | Fix |
|-------------|---------|-----|
| **Type mixing** | Tutorial + explanation in one page confuses both learner and practitioner | One Diataxis type per document |
| **Wall of text** | No headings, no lists → can't scan, AI can't extract facts | Add structure: headings, tables, bullets, code blocks |
| **Outdated docs left in place** | Stale content misleads AI and human readers equally | Archive or delete; enforce doc updates in PR process |
| **No error documentation** | Users hit errors with no guidance | Document common errors, causes, and fixes |
| **Broken code examples** | Examples that don't run erode trust and mislead AI | Test examples in CI |
| **README as dumping ground** | 5,000-word README nobody reads | Use README as navigation hub; move detail to `docs/` |
| **"Why" without "how"** | Explanation without actionable guidance | Pair explanation docs with how-to guides |
| **No ownership** | Documentation without an owner becomes outdated | CODEOWNERS for `docs/`; doc updates required in PR template |
