---
name: primitive-obsession
description: Detects and fixes the "primitive obsession" code smell from Domain-Driven Design. Use when a user asks to find or fix primitive obsession, value objects, or the primitive obsession code smell (Vlad Khononov's Learning Domain-Driven Design, Martin Fowler's Refactoring). Also use when reviewing code that uses raw string/int/float for domain concepts like email, money, phone number, address, status, color, SKU, coordinates, or other named domain types — and when the user asks to refactor those primitives into proper Value Objects in Python, TypeScript, JavaScript, Java, C#, Go, Rust, or Ruby.
---

# Primitive Obsession → Value Objects

**Primitive obsession**: using raw `string`/`int`/`float`/`bool` to represent domain concepts that deserve their own type with validation, equality, and behavior.

**Value Object** (DDD): immutable, equality by value (not identity), self-validating constructor, no ID field, domain behavior co-located.

---

## Detection Checklist

Scan code for these signals and call out each by file + line:

| Signal | Example (smell → concept) |
|---|---|
| Domain-named primitive field/param | `email: str` → `EmailAddress`, `amount: float` → `Money`, `status: str` → `OrderStatus` |
| Paired primitives forming one concept | `(amount, currency)` → `Money`; `(street, city, zip)` → `Address`; `(lat, lng)` → `Coordinates` |
| Duplicated validation across services | `if '@' not in email` repeated in 3 service methods → belongs in `EmailAddress.__init__` |
| Utility class with domain logic | `EmailUtils.isValid()`, `PhoneUtils.normalize()` → methods on the VO itself |
| Magic string/int state constants | `STATUS_PENDING = "PENDING"` → `OrderStatus` enum or VO |
| Primitive-typed collection with domain rules | `List<string> tags` with uniqueness rules → `TagSet` VO |

**Common domain-concept keywords to flag**: `email`, `phone`, `price`, `amount`, `currency`, `money`, `zip`, `postal`, `address`, `street`, `city`, `color`, `status`, `code`, `sku`, `id` (typed as raw string), `lat`/`lng`, `percentage`, `url`, `username`, `password`.

---

## Value Object Correctness Checklist

A correctly implemented VO must satisfy all of these:

- [ ] **Immutable** — no public setters; "mutation" returns a new instance
- [ ] **Structural equality** — `a == b` when all attributes match; no identity/pointer comparison
- [ ] **Consistent hash** — `a == b` implies `hash(a) == hash(b)` (required for sets/dicts/maps)
- [ ] **Self-validating constructor** — throws/raises on invalid input; holding an instance guarantees validity
- [ ] **No ID field** — if it has an `id`, it's an Entity, not a VO
- [ ] **Behavior co-located** — `email.getDomain()`, `money.add(other)`, not `EmailUtils.getDomain(email)`

---

## Universal Refactoring Steps

1. **Identify** — find a primitive field/param whose name implies a domain concept
2. **Shell first** — create the new type wrapping the primitive (no validation yet); get callers to compile
3. **Push validation in** — move all scattered `if`/regex/range checks into the constructor; delete duplicates
4. **Move behavior in** — migrate utility methods as instance methods on the new type
5. **Update callers** — use IDE rename to migrate construction sites one file at a time
6. **Audit persistence** — add ORM converters/serializers (JPA `@AttributeConverter`, EF Core `ComplexProperty`, Pydantic serializer)

---

## When NOT to Create a VO

- Primitive used in only one place and never validated
- Simple CRUD app with no complex domain rules
- Validation is a single annotation (`@NotNull`, `@Min`) with no behavior needed
- Configuration/settings objects (DTOs usually suffice)
- Collection VOs with 500+ items (replacing the whole collection is expensive)

---

## Language Reference Files

Load the appropriate file when working in that language:

| Language | File | Load when... |
|---|---|---|
| Python | [references/python-value-objects.md](references/python-value-objects.md) | `@dataclass`, Pydantic, attrs, NewType |
| TypeScript / JS | [references/typescript-value-objects.md](references/typescript-value-objects.md) | branded types, class VOs, Zod |
| Java | [references/java-value-objects.md](references/java-value-objects.md) | records, Lombok, JPA mapping |
| C# | [references/csharp-value-objects.md](references/csharp-value-objects.md) | record structs, EF Core, ValueObject base class |
| Go | [references/go-value-objects.md](references/go-value-objects.md) | unexported fields, value receivers |
| Rust | [references/rust-value-objects.md](references/rust-value-objects.md) | newtype, TryFrom, nutype macro |
| Ruby | [references/ruby-value-objects.md](references/ruby-value-objects.md) | Data.define, Struct, dry-struct |

If no language is specified, ask which language the user is working in before loading a reference file.
