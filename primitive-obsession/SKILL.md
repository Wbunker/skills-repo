---
name: primitive-obsession
description: Detects and fixes the "primitive obsession" code smell (Domain-Driven Design). Use when a user asks to find or fix primitive obsession, value objects, or branded types in TypeScript. Also use when reviewing TypeScript code that uses raw string/number for domain concepts like userId, teamId, email, money, phone, address, status, orderId, SKU, or other named domain identifiers — and when the user asks to refactor those primitives into branded types or class-based Value Objects.
---

# Primitive Obsession → Value Objects (TypeScript)

**Primitive obsession**: using raw `string`/`number`/`boolean` to represent domain concepts that deserve their own type.

**Value Object** (DDD): immutable, equality by value (not identity), self-validating, no ID field, behavior co-located.

---

## Detection Checklist

Scan code for these signals and call out each by file + line:

| Signal | Example (smell → concept) |
|---|---|
| Domain-named primitive field/param | `email: string` → `EmailAddress`, `amount: number` → `Money`, `status: string` → `OrderStatus` |
| Same-primitive IDs that can be confused | `userId: number`, `teamId: number` both passed to `fn(a, b)` → `UserId`, `TeamId` |
| Paired primitives forming one concept | `(amount, currency)` → `Money`; `(lat, lng)` → `Coordinates` |
| Duplicated validation across functions | `if (!email.includes("@"))` in 3 places → belongs in `EmailAddress` factory |
| Utility functions with domain logic | `isValidEmail(s)`, `normalizePhone(s)` → methods/factories on the VO itself |
| Magic string/number constants | `const STATUS_PENDING = "pending"` → `OrderStatus` enum or branded string |
| Collection with domain uniqueness rules | `string[]` tags with deduplication logic → `TagSet` VO |

**Common keywords to flag**: `email`, `phone`, `price`, `amount`, `currency`, `zip`, `address`, `color`, `status`, `code`, `sku`, `id` (typed as raw `string`/`number`), `lat`/`lng`, `percentage`, `url`, `username`, `password`.

---

## Value Object Correctness Checklist

- [ ] **Immutable** — `readonly` fields; "mutation" returns a new instance
- [ ] **Structural equality** — explicit `equals(other)` method; never `===` on class instances
- [ ] **Self-validating** — factory throws on invalid input; holding an instance guarantees validity
- [ ] **No ID field** — if it has an `id`, it is an Entity, not a VO
- [ ] **Behavior co-located** — `email.getDomain()`, `money.add(other)`, not utility functions

---

## Refactoring Steps (TypeScript)

1. **Identify** — find a primitive field/param whose name implies a domain concept
2. **Shell first** — create the new type (branded or class); get existing callers to compile
3. **Push validation in** — move scattered `if`/regex/range checks into the factory; delete duplicates
4. **Move behavior in** — migrate utility functions as methods/factories on the new type
5. **Update callers** — fix construction sites (where `number`/`string` must become the branded type); reads/comparisons usually need no change since branded types are subtypes
6. **Audit API boundary** — brand raw API/form values at entry points (hooks, API handlers); trust branded types downstream without re-casting

---

## When NOT to Create a VO

- Primitive used in only one place and never validated
- No cross-domain confusion risk (only one `id: number` in the entire call chain)
- Validation is a single non-reused check at one boundary
- Configuration/DTO objects that never flow into domain logic

---

## TypeScript Patterns

Load [references/typescript-value-objects.md](references/typescript-value-objects.md) for full implementation:
- Branded types (zero runtime — preferred for IDs and simple domain primitives)
- Class VOs with `private constructor` (multi-field concepts or rich behavior)
- Zod `.brand()` (API boundary validation + branding in one step)
- Type predicates and assertion functions
- ESLint guard against `as BrandedType` bypasses
- Serialization patterns

