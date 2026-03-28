# Templates and Checklists
## Documentation Authoring Templates and Codebase Analysis Output Templates

---

## README.md Template

```markdown
# Project Name

One-sentence description: what this does and for whom.

[![Build](https://github.com/org/repo/actions/workflows/ci.yml/badge.svg)](https://github.com/org/repo/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

<!-- Screenshot or GIF here for UI projects -->

## Why

What problem does this solve? 2–4 sentences on the motivation and who benefits.
Skip for internal tools where the audience already knows the context.

## Quickstart

The minimum to get something working:

```bash
# 1. Install
npm install my-project

# 2. Configure
cp .env.example .env
# Edit .env: set REQUIRED_API_KEY

# 3. Run
npm start
# → Server running at http://localhost:3000
```

## Installation

More detailed setup if the quickstart isn't sufficient.

### Prerequisites

- Node.js 18+
- PostgreSQL 15+
- [Any other requirements]

### Setup

```bash
git clone https://github.com/org/repo
cd repo
npm install
npm run db:migrate
```

## Usage

Concrete examples showing the most common use cases.

```javascript
const client = new MyClient({ apiKey: process.env.API_KEY });

const result = await client.processOrder({
  customerId: 'cust-123',
  items: [{ sku: 'WIDGET-A', quantity: 2 }]
});

console.log(result.orderId);  // "ord-456"
```

## Configuration

| Variable | Required | Default | Description |
|----------|---------|---------|-------------|
| `API_KEY` | Yes | — | Your API key from the dashboard |
| `DATABASE_URL` | Yes | — | PostgreSQL connection string |
| `LOG_LEVEL` | No | `info` | Logging level: debug, info, warn, error |
| `PORT` | No | `3000` | HTTP server port |

## Documentation

- [Architecture overview](docs/ARCHITECTURE.md)
- [API reference](docs/api/reference.md)
- [Deployment guide](docs/guides/deployment.md)
- [Contributing guide](CONTRIBUTING.md)

## License

[MIT](LICENSE) — Copyright (c) 2024 [Your Name / Organization]
```

---

## CLAUDE.md Template

Use this as a starting point. Keep it under 150 lines. Delete any section that doesn't apply.

```markdown
# Project: [Name]

## Stack
- Language/runtime: [e.g., Python 3.11, Node.js 20, Java 17]
- Framework: [e.g., FastAPI, Express, Spring Boot]
- Key dependencies: [list 3–5 most important]
- Infrastructure: [e.g., AWS Lambda + DynamoDB + API Gateway]

## Commands

```bash
# Install
npm install          # or: pip install -e ".[dev]"  /  mvn install

# Build
npm run build        # or: mvn package  /  gradle build

# Test
npm test             # or: pytest  /  mvn test
npm run test:watch   # optional: watch mode

# Lint / type check
npm run lint         # or: ruff check . && mypy src/  /  mvn checkstyle:check

# Run locally
npm start            # or: uvicorn app.main:app --reload
```

## Structure

```
src/           # Application source
  [domain]/    # Domain-specific modules
tests/         # Tests (mirror structure of src/)
docs/          # Documentation
  decisions/   # ADRs
infra/         # Infrastructure as Code
scripts/       # Developer tooling (not deployed)
```

## Key conventions

- [Only list things that deviate from standard practice for this language/framework]
- [e.g., "All DB writes use conditional expressions — see ADR-0003"]
- [e.g., "Integration tests require TEST_DATABASE_URL env var set"]

## Git workflow

- Branch: `feat/`, `fix/`, `chore/` prefix
- Commit: [conventional commits / describe your format]
- PRs: [describe review requirements]

## Non-obvious constraints

- [e.g., "Never use --force on git commands"]
- [e.g., "DynamoDB table names must use the TABLE_NAME env var, not hardcoded"]

## Related docs

- Architecture: @docs/ARCHITECTURE.md
- ADRs: @docs/decisions/
- API reference: @docs/api/openapi.yaml
```

---

## AGENTS.md Template (Cross-Tool Universal)

```markdown
# [Project Name]

## Overview
[1–2 sentences: what this project does]

## Stack
- Language/runtime: ...
- Framework: ...
- Infrastructure: ...

## Commands

Install: `[command]`
Build: `[command]`
Test: `[command]`
Lint: `[command]`
Run locally: `[command]`

## Repository structure

```
[directory]/   [description]
[directory]/   [description]
```

## Architecture
[2–4 sentences on the main components and how they relate]
See docs/ARCHITECTURE.md for the full component diagram.

## Key conventions
- [Non-obvious convention 1]
- [Non-obvious convention 2]

## Constraints
- [Thing that would cause problems if violated]
- [Reference to ADR if applicable]
```

---

## ADR Template

Save as `docs/decisions/NNNN-title-using-hyphens.md`

```markdown
# ADR-[NUMBER]: [Short decision title]

**Status**: [Proposed | Accepted | Deprecated | Superseded by ADR-NNNN]
**Date**: YYYY-MM-DD
**Deciders**: @handle, @handle

## Context

What is the situation that requires a decision?
What forces are at play (technical, organizational, constraints)?
Keep this factual and neutral.

## Decision

What decision was made?
State it clearly and directly.

## Consequences

**Positive:**
- [Benefit 1]
- [Benefit 2]

**Negative / trade-offs:**
- [Trade-off 1]
- [Trade-off 2]

**Alternatives rejected:**
- [Alternative 1]: [Why it was rejected]
- [Alternative 2]: [Why it was rejected]
```

---

## CONTRIBUTING.md Template

```markdown
# Contributing to [Project Name]

Thank you for your interest in contributing!

## How to report a bug

Before filing an issue, check if it already exists in [Issues](https://github.com/org/repo/issues).

When filing a bug report, please include:
- What you did
- What you expected to happen
- What actually happened
- Your environment (OS, language version, project version)

## How to suggest a feature

Open an issue describing:
- The problem you're trying to solve
- Your proposed solution
- Alternatives you've considered

## Development setup

1. Fork the repo and clone your fork
2. Install dependencies: `[command]`
3. Run the test suite: `[command]` — all tests should pass
4. Create a branch: `git checkout -b feat/your-feature`

## Making changes

- Write tests for new functionality
- Update documentation if you change public behavior
- Update CHANGELOG.md for user-facing changes

## Submitting a pull request

1. Ensure all tests pass: `[command]`
2. Ensure linting passes: `[command]`
3. Open a PR against `main`
4. Describe what changed and why
5. Reference any related issues with `Fixes #123`

## Code review

- We aim to review PRs within [2 business days]
- We may request changes; this is normal and not a rejection
- PRs are merged by [maintainers] after approval

## Commit message format

[Describe your convention, e.g., Conventional Commits]

```
feat(orders): add retry logic for transient failures

Implements exponential backoff with jitter for DynamoDB write failures.
Max retries: 3. Permanent failures are routed to the DLQ.

Fixes #42
```

## License

By contributing, you agree that your contributions will be licensed under the [MIT License](LICENSE).
```

---

## Pull Request Template

Save as `.github/PULL_REQUEST_TEMPLATE.md`

```markdown
## Summary

<!-- What does this PR do? Why? Link to issue if applicable (Fixes #123) -->

## Changes

<!-- Brief list of what changed -->

-
-

## Testing

<!-- How was this tested? -->

- [ ] Unit tests added/updated
- [ ] Integration tests pass
- [ ] Manual testing steps documented below (if applicable)

<details>
<summary>Manual testing steps</summary>

1. ...

</details>

## Documentation

- [ ] CHANGELOG.md updated (if user-facing change)
- [ ] Docs updated (if behavior or API changed)
- [ ] New ADR added (if significant architectural decision)

## Screenshots / recordings

<!-- For UI changes. Delete section if not applicable. -->
```

---

## ARCHITECTURE.md Template

```markdown
# Architecture

## Overview
[2-3 sentences: what the system does, its primary architectural style,
and the key quality attributes it optimizes for]

## System Context

[C4 Level 1 Mermaid diagram]

[Brief description of users and external systems]

## Container Architecture

[C4 Level 2 Mermaid diagram]

| Container | Technology | Purpose |
|-----------|-----------|---------|
| [name] | [tech] | [responsibility] |

## Key Components

[For each major container, a brief component summary with diagram]

## Data Flow

[Mermaid diagram showing primary data flows]

## Key Decisions

| Decision | Rationale | Alternatives Considered |
|----------|-----------|------------------------|
| [what] | [why] | [what else was considered] |

## External Dependencies

| Dependency | Purpose | Failure Impact |
|-----------|---------|----------------|
| [name] | [why we use it] | [what happens if it's down] |

## Development

### Directory Structure
[Tree with annotations]

### Key Conventions
[Non-obvious patterns a developer should know]

### Extension Points
[Where and how to add new functionality]

## Out of Scope
[What this system deliberately does NOT handle and where those concerns live]
```

---

## New Project Documentation Checklist

Use this when starting a new project:

### Immediate (Day 1)
- [ ] README.md with what/why/quickstart
- [ ] LICENSE file
- [ ] CLAUDE.md or AGENTS.md with commands and stack

### Before First External Contributor
- [ ] CONTRIBUTING.md
- [ ] CODE_OF_CONDUCT.md
- [ ] SECURITY.md
- [ ] .github/ISSUE_TEMPLATE/ (bug + feature request)
- [ ] .github/PULL_REQUEST_TEMPLATE.md

### Before Production Deployment
- [ ] ARCHITECTURE.md
- [ ] ADRs for all significant non-obvious design decisions
- [ ] CHANGELOG.md
- [ ] Runbook (docs/runbook.md)
- [ ] API reference (if public API)
- [ ] Onboarding guide for new engineers

### CI/CD Pipeline
- [ ] Link checker on all Markdown files
- [ ] Code example tests (doctest or equivalent)
- [ ] Vale or other documentation linter
- [ ] CODEOWNERS configured
- [ ] Doc update requirement in PR template

---

## Documentation Review Checklist (for Existing Projects)

Use this to audit documentation health:

### Coverage
- [ ] Can a new engineer get the project running from the README alone?
- [ ] Is the architecture documented with a current diagram?
- [ ] Are ADRs written for all major non-obvious decisions?
- [ ] Are all public APIs documented?
- [ ] Are error messages documented with their causes and fixes?

### Quality
- [ ] Are all code examples runnable and tested?
- [ ] Are there any obviously stale sections (references to removed features, old commands)?
- [ ] Does each document have a single clear purpose (Diataxis)?
- [ ] Are there broken links? (Run a link checker)

### AI-Readiness
- [ ] Does CLAUDE.md/AGENTS.md have all build/test/lint commands?
- [ ] Is CLAUDE.md under 150 lines?
- [ ] Do all public functions have type annotations?
- [ ] Do files have module-level docstrings?
- [ ] Are significant constraints explained in ADRs and referenced from CLAUDE.md?

---

# Analysis Output Templates

Templates for documentation artifacts produced by codebase analysis.
Fill in brackets with actual values from the analysis.

---

## System Overview

One-page summary for anyone encountering the system for the first time.

```markdown
# [System Name] — System Overview

## What It Does
[1-2 sentences: what problem does this system solve and for whom]

## Tech Stack
| Layer | Technology |
|-------|-----------|
| Language | [e.g., TypeScript 5.x] |
| Framework | [e.g., Next.js 14] |
| Database | [e.g., PostgreSQL 16] |
| Cache | [e.g., Redis 7] |
| Message Broker | [e.g., RabbitMQ] |
| Infrastructure | [e.g., AWS ECS, Terraform] |

## System Context

[C4 Level 1 Mermaid diagram here]

## Key Entry Points
| Entry Point | Location | Purpose |
|-------------|----------|---------|
| [e.g., API routes] | [file path] | [what it handles] |

## Directory Structure
[Top-level directory tree with one-line purpose per directory]

## How to Run
[Build/run commands from package manifest or README]
```

---

## Container Diagram

For systems with multiple services, databases, or separately-deployed units.

```markdown
# [System Name] — Container Diagram

[C4 Level 2 Mermaid diagram]

## Container Inventory

| Container | Technology | Responsibility | Port/Protocol |
|-----------|-----------|---------------|---------------|
| [name] | [tech] | [one sentence] | [e.g., :8080/HTTP] |

## Communication Flows

| From | To | Protocol | Purpose |
|------|-----|----------|---------|
| [source] | [target] | [HTTP/gRPC/AMQP/SQL] | [what data flows] |
```

---

## Component Analysis

For documenting the internals of a single container or major module.

```markdown
# [Container/Module Name] — Component Analysis

## Overview
[1-2 sentences: what this container does and its architectural style]

## Component Map

[C4 Level 3 Mermaid diagram or module dependency diagram]

## Components

### [Component Name]
- **Responsibility**: [what it does]
- **Location**: [directory/file path]
- **Public interface**: [key exported functions/classes]
- **Dependencies**: [what it imports from other components]
- **Key patterns**: [e.g., repository pattern, strategy, middleware chain]

[Repeat for each component]

## Layer Structure
[If applicable: diagram showing layers and dependency direction]

## Internal Data Flow
[Mermaid flowchart showing how data moves between components]
```

---

## Request Flow Trace

Documents a single end-to-end flow through the system.

```markdown
# Flow: [Flow Name]

## Summary
[One sentence: what this flow accomplishes]

## Trigger
[What initiates this flow: HTTP request, event, cron job, etc.]

## Sequence

[Mermaid sequence diagram]

## Step-by-Step

| Step | Component | Action | File:Line |
|------|-----------|--------|-----------|
| 1 | [component] | [what happens] | [path:line] |
| 2 | [component] | [what happens] | [path:line] |

## Data Transformations
[How the request/data shape changes at each step]

## Error Paths
| Error Condition | Where Caught | Response |
|----------------|-------------|----------|
| [condition] | [file:line] | [what happens] |

## Side Effects
[Events emitted, logs written, metrics recorded, external calls made]
```

---

## Interface Catalog

Documents the contract for a key interface or module boundary.

```markdown
# Interface: [Interface Name]

## Location
[File path and line number]

## Purpose
[One sentence: what this interface represents]

## Provided Resources

### [Method/Function Name]
- **Signature**: `[full signature]`
- **Purpose**: [what it does]
- **Parameters**: [name, type, constraints for each]
- **Returns**: [type and meaning]
- **Preconditions**: [what must be true before calling]
- **Postconditions**: [what is guaranteed after success]
- **Side effects**: [state changes, events, external calls]
- **Error conditions**: [what can go wrong, error types thrown]

[Repeat for each method]

## Required Dependencies
[What the implementing module needs from its environment]

## Usage Example
[Minimal code example showing correct usage]

## Invariants
[Rules that must always hold for implementations of this interface]
```

---

## Inferred ADR

For architectural decisions reverse-engineered from code.

```markdown
# ADR-[N]: [Decision Title]

**Status**: Inferred from code (not explicitly documented)
**Date**: [Approximate from git history, or "unknown"]
**Confidence**: [High|Medium|Low — how certain is this inference]

## Context
[Forces and constraints that likely drove this decision.
State as facts observed in the code, not speculation.]

## Decision
[What was decided. State as "The system uses X" or "The team chose X over Y".]

## Evidence
- [Code location 1 that supports this inference]
- [Code location 2]
- [Git history evidence if applicable]

## Consequences
### Positive
- [Benefit observed in the codebase]

### Negative
- [Trade-off or limitation observed]

### Neutral
- [Side effect that is neither good nor bad]
```

---

## Integration Point Inventory

Catalogs every external dependency with its failure characteristics.

```markdown
# Integration Point Inventory

## Summary
[N] external integration points identified. [M] have explicit failure protection.

## Inventory

### [Integration Point Name]
- **Type**: [HTTP API | Database | Message Queue | File System | External Service]
- **Location**: [file paths where this integration is used]
- **Protocol**: [HTTP/gRPC/AMQP/SQL/etc.]
- **Authentication**: [API key | OAuth | mTLS | none]
- **Failure modes**:
  - Timeout: [configured? value? fallback?]
  - Unavailable: [circuit breaker? retry? degraded mode?]
  - Slow response: [timeout configured? queue depth limit?]
  - Error response: [error handling? retry on specific codes?]
- **Stability patterns in place**:
  - [ ] Timeout configured
  - [ ] Circuit breaker
  - [ ] Retry with backoff
  - [ ] Bulkhead (isolated pool)
  - [ ] Fallback/degraded mode
  - [ ] Rate limiting
- **Monitoring**: [metrics? alerts? dashboard?]

[Repeat for each integration point]

## Coverage Matrix

| Integration Point | Timeout | Circuit Breaker | Retry | Bulkhead | Fallback |
|-------------------|---------|-----------------|-------|----------|----------|
| [name] | [Y/N] | [Y/N] | [Y/N] | [Y/N] | [Y/N] |
```

---

## Where to Look Guide

Quick-reference for developers working in the codebase.

```markdown
# Where to Look

## "I need to..."

| Task | Start Here | Key Files |
|------|-----------|-----------|
| Add a new API endpoint | [directory] | [key files] |
| Add a new database table | [directory] | [migration path, model path] |
| Modify business logic for X | [directory] | [service/use case files] |
| Add a new background job | [directory] | [worker/job files] |
| Change authentication | [directory] | [auth middleware files] |
| Update external API integration | [directory] | [client/adapter files] |
| Add a new event/notification | [directory] | [event handler files] |
| Fix a failing test | [directory] | [test config, fixtures] |
| Update deployment config | [directory] | [IaC files, CI config] |

## Common Patterns in This Codebase

### [Pattern Name]
**Where**: [directory/file pattern]
**How it works**: [1-2 sentences]
**Example**: [one concrete instance with file path]

[Repeat for 3-5 key patterns]

## Gotchas
[Non-obvious things that trip people up — ordered by how frequently they bite]

| Gotcha | Why It Happens | What to Do |
|--------|---------------|------------|
| [surprise] | [root cause] | [correct approach] |
```

---

## Complexity Hotspot Report

For risk and maintainability assessments.

```markdown
# Complexity Hotspot Report

## Summary
[N] hotspots identified. Top concerns: [1-2 sentence summary].

## Hotspots (by severity)

### 1. [Hotspot Name/Area]
- **Location**: [file paths]
- **Indicators**: [what makes this complex — high churn, deep nesting, many dependencies, etc.]
- **Cognitive load**: [High|Medium] — [why this is hard to understand]
- **Risk**: [what could go wrong when modifying this area]
- **Recommendation**: [refactor suggestion or documentation needed]

[Repeat, ordered by severity]

## Churn Analysis
| File | Changes (last 6mo) | Last Modified | Complexity Indicator |
|------|-------------------|---------------|---------------------|
| [path] | [count] | [date] | [what makes it complex] |

## Dependency Hotspots
[Files/modules with highest fan-in or fan-out]

| Module | Fan-In | Fan-Out | Risk |
|--------|--------|---------|------|
| [name] | [count] | [count] | [assessment] |
```
