# TypeScript Value Objects

## Approach Selection

| Use case | Approach |
|---|---|
| ID types / simple domain primitives | Branded type (zero runtime overhead) |
| Multi-field concept (money, address, coordinates) | Class VO with `private constructor` |
| API boundary: validate + brand in one step | Zod `.brand()` |
| Domain string/number with behavior | Class VO |

---

## Pattern 1: Branded Types (preferred for IDs and simple primitives)

Zero runtime overhead — the brand exists only in the type system.

```typescript
// Generic Brand utility (unique symbol prevents tag-string collisions)
declare const __brand: unique symbol;
type Brand<T, B> = T & { readonly [__brand]: B };

type UserId    = Brand<number, "UserId">;
type TeamId    = Brand<number, "TeamId">;
type EmailAddress = Brand<string, "EmailAddress">;

// Factory functions — the ONLY safe construction boundary
export function asUserId(n: number): UserId     { return n as UserId; }
export function asTeamId(n: number): TeamId     { return n as TeamId; }

// TypeScript prevents confusion between same-primitive types:
function findTeam(id: TeamId): Team { ... }
// findTeam(userId)  ← TS error: UserId is not assignable to TeamId

// Branded types are subtypes — downstream reads need no changes:
const url = `/teams/${team.id}`;    // fine: TeamId extends number/string
const map = new Map<TeamId, Team>(); // fine as map key
```

**`__brand` is never assigned at runtime** — zero overhead, zero serialization impact.

### Type predicates (runtime narrowing)

```typescript
function isUserId(n: number): n is UserId {
  return Number.isInteger(n) && n > 0;
}

// Usage:
if (isUserId(rawId)) {
  findUser(rawId); // rawId is UserId inside the block
}
```

### Assertion functions (imperative narrowing)

```typescript
function assertUserId(n: number): asserts n is UserId {
  if (!Number.isInteger(n) || n <= 0) throw new Error(`Invalid UserId: ${n}`);
}

assertUserId(rawId); // throws or narrows
findUser(rawId);     // UserId from here on
```

---

## Pattern 2: Class VO with Private Constructor

Use for multi-field concepts or when you need rich domain behavior.

```typescript
export class Money {
  private constructor(
    public readonly amount: number,
    public readonly currency: string
  ) {}

  static of(amount: number, currency: string): Money {
    if (amount < 0) throw new Error("amount must be non-negative");
    const c = currency.trim().toUpperCase();
    if (c.length !== 3) throw new Error("currency must be 3-letter ISO code");
    return new Money(Math.round(amount * 100) / 100, c);
  }

  add(other: Money): Money {
    if (this.currency !== other.currency) throw new Error("Currency mismatch");
    return Money.of(this.amount + other.amount, this.currency);
  }

  equals(other: Money): boolean {
    return this.amount === other.amount && this.currency === other.currency;
  }

  toString(): string { return `${this.amount} ${this.currency}`; }

  toJSON() { return { amount: this.amount, currency: this.currency }; }
  static fromJSON(d: { amount: number; currency: string }) { return Money.of(d.amount, d.currency); }
}
```

**Key rules:**
- `private constructor` — forces factory; prevents bypassing validation with `new`
- Always implement `equals()` — never use `===` for class instance equality
- Implement `toJSON()` + `static fromJSON()` — class VOs do not serialize transparently
- `Object.freeze(this)` — optional runtime immutability on top of TypeScript readonly

---

## Pattern 3: Zod `.brand()` (API boundary validation + type safety)

Ideal when you already use Zod for request/response parsing.

```typescript
import { z } from "zod";

const UserIdSchema = z.number().int().positive().brand<"UserId">();
const EmailSchema  = z.string().email().transform(s => s.toLowerCase().trim()).brand<"EmailAddress">();

type UserId       = z.infer<typeof UserIdSchema>;
type EmailAddress = z.infer<typeof EmailSchema>;

// Parse = validate + transform + brand in one step:
const userId = UserIdSchema.parse(req.params.id);
const email  = EmailSchema.parse(formData.email);
```

---

## API Boundary Normalization Pattern

Brand raw API responses at the hook/handler boundary. Trust branded types downstream — no re-casting.

```typescript
// In a fetch hook (e.g., use-team-detail.ts):
import { asTeamId, asUserId } from "@/lib/types";

function normalizeTeam(raw: ApiTeam): Team {
  return {
    ...raw,
    id:              asTeamId(raw.id),
    organization_id: raw.organization_id != null ? asTeamId(raw.organization_id) : null,
    creator: {
      ...raw.creator,
      id: asUserId(raw.creator.id),
    },
  };
}

// Downstream components receive Team with branded fields — no casting needed.
```

**Rule**: `as BrandedType` is only valid inside factory/normalization functions. Everywhere else it is a smell — add the normalization one level up.

---

## ESLint: Prevent `as BrandedType` Bypasses

Branded type safety collapses if callers cast directly. Enforce via `no-restricted-syntax`:

```json
// .eslintrc or eslint.config.js
{
  "rules": {
    "no-restricted-syntax": [
      "error",
      {
        "selector": "TSTypeAssertion[typeAnnotation.typeName.name=/Id$/]",
        "message": "Use asXxxId() factory instead of direct `as XxxId` casts."
      }
    ]
  }
}
```

---

## Result Type Pattern (prefer over throwing in public APIs)

```typescript
type Result<T, E = Error> =
  | { ok: true; value: T }
  | { ok: false; error: E };

export class EmailAddress {
  private constructor(private readonly value: string) {}

  static parse(raw: string): Result<EmailAddress> {
    const normalized = raw.trim().toLowerCase();
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(normalized)) {
      return { ok: false, error: new Error(`Invalid email: "${raw}"`) };
    }
    return { ok: true, value: new EmailAddress(normalized) };
  }
}
```

---

## Common Gotchas

| Gotcha | Fix |
|---|---|
| `readonly` is compile-time only | Add `Object.freeze(this)` for runtime immutability |
| Class VOs do not serialize by default | Implement `toJSON()` + `static fromJSON()` |
| `as BrandedType` bypasses all safety | Factory functions only; add ESLint rule above |
| `===` compares class instance identity | Always implement `equals(other)`; never `===` |
| Branded type on `null`-able field | Use `TeamId \| null`, not `TeamId \| undefined` — match API shape |
| Optimistic / temp IDs | Use factory: `asDayPlanColumnId(-Date.now())` — negative IDs are valid branded values |

---

## Future: Native Opaque Types

TypeScript has open issues (#202, #28515) for native nominal/opaque type support. The branded-type workaround is the current community consensus. If native opaque types land, factory functions will remain the right construction pattern — only the `Brand<T, B>` utility definition will change.

