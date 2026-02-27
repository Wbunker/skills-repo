# Anatomy of a Healthy Node

What goes in a CLAUDE.md or AGENTS.md file, and why.

---

## Table of Contents

1. [The Six Core Areas](#the-six-core-areas)
2. [What to Include vs Exclude](#what-to-include-vs-exclude)
3. [Node Structure Templates](#node-structure-templates)
4. [Target Lengths](#target-lengths)
5. [Downlinks and @imports](#downlinks-and-imports)
6. [Examples of Good Nodes](#examples-of-good-nodes)

---

## The Six Core Areas

A healthy node touches one or more of these:

### 1. Commands
Executable commands with flags and options. Agent references these constantly.

```markdown
## Commands

# Type check a single file
npm run tsc --noEmit path/to/file.tsx

# Run single test file
npm run vitest run path/to/file.test.tsx

# Full build (use sparingly)
yarn build:app
```

### 2. Testing
How to run tests, what patterns to use, test file locations.

```markdown
## Testing

Tests live alongside source files as `*.test.ts`.
Use `vi.mock()` for mocking—never manual mocks.
Run `pnpm test:unit <path>` for single file.
E2E tests require `docker compose up` first.
```

### 3. Project Structure
What lives where. Especially important in monorepos.

```markdown
## Structure

apps/web — Next.js frontend
apps/api — Express backend
packages/shared — Shared types and utilities
packages/ui — Component library
```

### 4. Code Style
Patterns and conventions via examples, not prose.

```markdown
## Code Style

- Avoid class-based components like `Admin.tsx`
- Prefer functional components like `Projects.tsx`
- Forms: copy `app/components/DashForm.tsx`
- HTTP: use `app/api/client.ts`—never fetch directly
```

### 5. Git Workflow
Branch naming, merge vs rebase, commit conventions.

```markdown
## Git Workflow

Branch naming: `feature/JIRA-123-description`
Always rebase on main before merging.
Squash commits in PR.
Never push directly to main.
```

### 6. Boundaries
What should never be touched.

```markdown
## Boundaries

- Never commit secrets or .env files
- Don't modify `vendor/` or `node_modules/`
- Production configs in `deploy/` are off-limits
- Don't touch `legacy/` unless explicitly asked
```

---

## What to Include vs Exclude

The question isn't "what could Claude benefit from knowing?" It's "what can Claude NOT infer from code alone?"

### Include

| Content Type | Example |
|--------------|---------|
| Project context | "Next.js e-commerce app with Stripe integration" |
| Commands with flags | `npm run tsc --noEmit path/to/file.tsx` |
| Patterns diverging from conventions | "We use repository pattern, not direct ORM calls" |
| Critical invariants | "Never bypass rate limiter—protects fragile downstream" |
| Gotchas | "Auth module has weird retry logic due to OAuth bug" |
| Why behind patterns | "48-hour reconciliation window due to Q3 2021 incident" |

### Exclude

| Content Type | Why |
|--------------|-----|
| Generic best practices | Model already knows |
| Linter-enforced rules | Tooling handles it |
| Standard conventions | Model's training covers it |
| Detailed explanations of code | Code speaks for itself |
| Task-specific guidance | Belongs in sub-folder nodes |

---

## Node Structure Templates

### Root Node (~50 lines)

```markdown
[One-liner describing the project and stack]

## Commands

[Most-used commands with full flags]

## Architecture

[High-level structure—what lives where]
[Key patterns that apply everywhere]

## Critical Invariants

[3-5 things that must NEVER be violated]

## Navigation

- API patterns: `api/CLAUDE.md`
- Frontend: `frontend/CLAUDE.md`
- Scripts: `scripts/CLAUDE.md`
```

### Subsystem Node (~80-150 lines)

```markdown
## Purpose

[What this area owns. What it explicitly doesn't own.]

## Entry Points

[Main APIs, jobs, CLI commands]

## Patterns

[How to add new X. Canonical examples to follow.]
[Code snippets under 20 lines]

## Anti-patterns

[What NEVER to do here]

## Invariants

[Contracts with other systems]
[Things that must always be true]

## Pitfalls

[Common mistakes agents or humans make]
[Gotchas that aren't obvious from code]

## Dependencies

[What this depends on]
[What depends on this]

## Related Context

- [Downlink to child node]
- [Downlink to related node outside hierarchy]
```

### Leaf Node (~60-100 lines)

```markdown
## Purpose

[Specific responsibility of this module]

## Usage

[How to use this correctly. Example code.]

## Constraints

[Hard rules specific to this area]

## Historical Context

[Why it's this way. Incidents. Decisions.]
```

---

## Target Lengths

| Node Level | Ideal Lines | Max Lines | Tokens |
|------------|-------------|-----------|--------|
| Root | 50 | 300 | ~400-2500 |
| Subsystem | 100 | 200 | ~800-1600 |
| Leaf | 60 | 100 | ~500-800 |

If your root is longer than 300 lines, it's almost certainly full of content that should live elsewhere.

**Rule of thumb:** If you can't write 30+ lines specific to a directory, you don't need a node there. Let parent cover it.

---

## Downlinks and @imports

### Downlinks

Point to related context outside the ancestor chain:

```markdown
## Related Context

- Payment validation rules: `./validators/CLAUDE.md`
- Settlement engine: `./settlement/CLAUDE.md`
- Why eventual consistency: `/docs/adrs/004-eventual-consistency.md`
```

### @imports

Pull in content from other files:

```markdown
See @README.md for project overview
See @docs/api-patterns.md for API conventions
See @package.json for available npm scripts
```

**Pattern:** Essentials in CLAUDE.md, detailed topic-specific guidance in separate files via @imports.

---

## Examples of Good Nodes

### Good Root Node

```markdown
React 18 + Node 20 + PostgreSQL 15. Monorepo with `apps/web` and `apps/api`.

## Commands

- `pnpm dev` — Start both services
- `pnpm test:unit <path>` — Run single test file
- `pnpm db:migrate` — Run pending migrations

## Architecture

API follows vertical slice: each feature in `apps/api/src/features/{name}/`
contains router, service, repository, and tests together.

Auth uses JWT with refresh tokens. All protected routes use `requireAuth`
middleware from `apps/api/src/middleware/auth.ts`.

## Critical Invariants

- Never bypass `requireAuth`—audit logs depend on `req.user`
- All database writes go through repositories for soft-delete handling
- Feature flags via `apps/api/src/lib/flags.ts`, not env vars directly
```

### Good Subsystem Node

```markdown
## Purpose

Payment processing: authorization, capture, refunds. Does NOT handle settlement
(see `../settlement/`).

## Entry Points

- `POST /api/payments/authorize` — Main entry for new payments
- `PaymentProcessor.process()` — Core processing logic
- `RefundJob` — Nightly refund batch processing

## Patterns

New payment types follow `src/processors/CreditCardProcessor.ts`.
All processors implement `PaymentProcessor` interface.

## Anti-patterns

- Never call gateway directly—always through `GatewayClient`
- Never store raw card numbers—use tokenization service

## Invariants

- Idempotency key required on all mutations
- Gateway calls must be wrapped in circuit breaker
- All amounts in cents (integer), never decimals

## Pitfalls

- `PaymentStatus.PENDING` can mean two things—check `isAwaitingCapture`
- Test cards only work in staging, never production config

## Historical Context

The 3-retry pattern exists because Gateway X has 15% timeout rate
during peak hours. See incident INC-2341.
```

---

## The Quality Test

For each line in your node, ask:

1. **Is this project-specific?** If it applies to any project, delete it.
2. **Would an agent go wrong without this?** If not, it's optional.
3. **Does the code already show this?** If yes, don't repeat it.
4. **Will this rot?** If yes, phrase it more abstractly or link to source.
5. **Is this the right level?** Root = everywhere. Subsystem = here and children. Leaf = here only.

The goal: **maximum signal per token.**
