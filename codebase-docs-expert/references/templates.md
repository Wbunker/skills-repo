# Documentation Templates and Checklists
## Ready-to-Use Templates for README, CLAUDE.md, ADR, CONTRIBUTING.md, and More

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

[2–4 sentences describing the system: what it does, what scale it operates at,
and what its key characteristics are (e.g., event-driven, microservices, etc.)]

## Components

| Component | Technology | Responsibility |
|-----------|-----------|---------------|
| [name] | [tech] | [what it does] |
| [name] | [tech] | [what it does] |

## Data Flow

```
[ASCII or Mermaid diagram showing how data moves through the system]

Client → [component] → [component]
              ↓
         [storage]
```

## External Dependencies

| Service | Purpose | Access Method |
|---------|---------|--------------|
| [service] | [what it's used for] | [SDK / REST / credentials in Secrets Manager] |

## Infrastructure

[Brief description: cloud provider, deployment model, environments]

See `infra/` for Terraform/CDK/CloudFormation definitions.

## Significant Design Decisions

| Decision | ADR |
|----------|-----|
| [Why we use X instead of Y] | [ADR-0001](decisions/0001-title.md) |
| [Why we don't do Z] | [ADR-0003](decisions/0003-title.md) |

## What Is Out of Scope

[Explicitly state what this system does NOT do, to prevent scope creep
and misguided "improvements" by contributors or AI tools]
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
