# Type System Design for Agent Harnesses

Source: OpenAI harness engineering (Feb 2026)

## Table of Contents

- [Types as a Harness Property](#types-as-a-harness-property)
- [Semantic Type Names](#semantic-type-names) — UserId, WorkspaceSlug over string
- [End-to-End Type Coverage](#end-to-end-type-coverage) — TypeScript strict, OpenAPI clients, Postgres+Kysely, third-party wrapping
- [Automatic Enforcement](#automatic-enforcement) — CI type checks; branded types
- [Connection to Other Harness Principles](#connection-to-other-harness-principles)

---

## Types as a Harness Property

Types are not just a code quality concern in agent-maintained codebases — they are a harness mechanism.

> "Entire categories of illegal states and transitions can be eliminated. And types shrink the search space of possible actions the model can take, while doubling as source-of-truth documentation describing exactly what kind of data flows through each layer."

Two distinct benefits:

**Degrees-of-freedom reduction**: the agent cannot construct an illegal state if the type system rejects it. Every constraint encoded in the type system is one less decision the agent can get wrong. This compounds: a fully typed codebase eliminates an entire class of errors before the agent has a chance to make them.

**In-context documentation**: types are machine-readable documentation that is guaranteed to be current — unlike comments or docstrings, which can drift. When the agent reads a function signature, the types tell it exactly what each argument is and what the return value will be. It doesn't have to infer this from variable names or comments.

## Semantic Type Names

Generic names are appropriate for self-contained generic algorithms. Inside a business system, they communicate nothing.

| Generic | Semantic |
|---|---|
| `string` | `UserId`, `WorkspaceSlug`, `EmailAddress` |
| `string` | `SignedWebhookPayload`, `JwtToken` |
| `number` | `UnixTimestampMs`, `CentAmount` |
| `object` | `InvoiceLineItem`, `AuditLogEntry` |

> "When you're working with agents, good semantic names are an amplifier. If the model sees a type like `UserId`, `WorkspaceSlug`, or `SignedWebhookPayload`, it can immediately understand what kind of thing it is dealing with. It can also search for that thing easily."

**Searchability matters**: an agent looking for all places a `UserId` is used can grep for `UserId`. An agent looking for all places a raw `string` is used cannot narrow that search to user IDs. Semantic names create a vocabulary the agent can query.

**Preventing accidental interchange**: branded types prevent the agent from accidentally passing a `WorkspaceId` where a `UserId` is expected — two values that are both strings, but not interchangeable. The type system catches this; naming conventions alone do not.

## End-to-End Type Coverage

The goal is to eliminate untyped boundaries — points where typed data becomes `any`, `unknown`, or an unvalidated raw string that the agent has to probe to understand.

### TypeScript Application Layer

- Use TypeScript with strict mode (`strict: true`)
- Represent every domain concept as a named type, not a primitive
- Push semantic meaning into type names — the type name should answer "what is this?" at a glance
- Avoid `any` — it is a context hole; the agent can't reason about values typed `any`

### API Layer: OpenAPI + Generated Clients

Generate typed clients from OpenAPI specs rather than writing HTTP calls by hand:

```typescript
// Generated from OpenAPI spec — agent knows exact shapes
const response = await client.billing.invoices.create({
  workspaceId,     // WorkspaceId — type-checked
  lineItems,       // InvoiceLineItem[] — type-checked
  currency,        // CurrencyCode — type-checked
});
// response: CreateInvoiceResponse — agent knows what came back
```

Benefits:
- Frontend and backend are guaranteed to agree on request/response shapes
- The agent doesn't need to look up API documentation — the types are the documentation
- Breaking API changes surface as type errors before they reach production

### Database Layer: Typed Clients + Constraints

Use the database type system to enforce invariants:
- Column types constrain what values can be stored
- `CHECK` constraints enforce domain rules (`amount > 0`, `status IN ('pending', 'paid', 'void')`)
- `NOT NULL` constraints prevent null-ambiguity that confuses agents
- Triggers enforce multi-column invariants that column types can't express

Generate typed TypeScript clients from the schema (Kysely, Prisma, Drizzle):

```typescript
// Kysely example — fully typed queries
const invoice = await db
  .selectFrom('invoices')
  .where('workspace_id', '=', workspaceId)  // WorkspaceId — type-checked
  .where('status', '=', 'pending')           // only valid statuses
  .select(['id', 'amount_cents', 'currency'])
  .executeTakeFirstOrThrow();
// invoice: { id: InvoiceId; amount_cents: number; currency: CurrencyCode }
```

**Why this matters for agents**: if an agent tries to write invalid data, the database complains clearly and loudly — with an error the agent can read and act on. Invalid states are rejected at the boundary rather than silently stored and discovered later.

### Third-Party Clients

For external dependencies:
- Prefer clients that provide good TypeScript types
- When a client provides poor types or none: **wrap it**

```typescript
// Wrap poorly-typed clients to give them good types
function sendSlackMessage(
  channel: SlackChannelId,
  text: string,
  options?: SlackMessageOptions
): Promise<SlackMessageId> {
  // internal call to slack-sdk with `any` types
  // the wrapper gives the rest of the codebase good types
}
```

The wrapper is the boundary where `any` is contained. Everything outside the wrapper is typed; the agent interacts with the typed wrapper, not the opaque client. This is the "validate at boundaries" golden principle applied to third-party dependencies.

## Automatic Enforcement

Types require tooling enforcement to be load-bearing:

- **TypeScript compiler in strict mode** — CI fails on type errors; the agent cannot ship code that violates types
- **Linters** — ESLint with TypeScript rules; catch `any` usage, implicit `any`, unsafe type assertions
- **Auto-applied on task completion**: configure linters and formatters to apply automatically when the agent finishes a task or before each commit — don't rely on the agent to remember to run them

> "Make those as strict as possible and configured to automatically apply fixes whenever the LLM finishes a task or is about to commit."

This turns type checking into a feedback loop: the agent writes code, types are checked, errors surface, the agent fixes them. The tighter this loop, the faster the agent can work without accumulating type debt.

## Connection to Other Harness Principles

**Degrees-of-freedom removal**: types are the most pervasive form of constraint in the codebase — they apply to every value in every function. More constrained = more productive agent (see [context-engineering.md](context-engineering.md) → "Architectural Constraints").

**Validate at boundaries, not YOLO**: the database layer enforcement and API client generation are the technical implementation of OpenAI's golden principle "don't probe data YOLO-style — validate boundaries or rely on typed SDKs."

**Dependency selection**: typed dependencies are higher harnessability choices. When evaluating a new library, the presence of good TypeScript types is a first-class criterion (see [context-engineering.md](context-engineering.md) → "Dependency Selection as a Harness Decision").

**Searchability**: semantic type names are part of the filesystem-as-interface principle applied to types — the agent can navigate the type system by searching, just as it navigates the codebase by reading file paths (see [context-engineering.md](context-engineering.md) → "The Filesystem as Navigation Interface").
