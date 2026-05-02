# TypeScript / JavaScript Value Objects

## Approach Selection

| Use case | Approach |
|---|---|
| Full domain VO with behavior + methods | Class with `private constructor` + `static create()` |
| Type-safe primitive without runtime overhead | Branded type |
| API boundary validation + type safety in one step | Zod with `.brand<T>()` |
| Two primitives that form one concept | Class VO (always — branded types can't group fields) |

---

## Pattern 1: Class VO with Private Constructor (primary pattern)

```typescript
export class EmailAddress {
  private constructor(private readonly value: string) {}

  static create(raw: string): EmailAddress {
    const normalized = raw.trim().toLowerCase();
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(normalized)) {
      throw new Error(`Invalid email address: "${raw}"`);
    }
    return new EmailAddress(normalized);
  }

  equals(other: EmailAddress): boolean {
    return this.value === other.value;
  }

  toString(): string {
    return this.value;
  }

  getDomain(): string {
    return this.value.split('@')[1];
  }
}

// Usage:
const email = EmailAddress.create('User@Example.COM');
// email.value = 'other'   ← TypeScript compile error (readonly)
// new EmailAddress('bad') ← TypeScript compile error (private constructor)
```

**Key patterns:**
- `private constructor` — forces factory method; prevents bypassing validation with `new`
- `readonly` — TypeScript compile-time immutability
- `static create()` / `static fromString()` — named factory expresses intent; can have multiple factories
- `equals(other)` — explicit structural equality (no `==` override in TS)
- `Object.freeze(this)` — optional; adds runtime immutability on top of TypeScript's compile-time check

### Multi-field VO

```typescript
export class Money {
  private constructor(
    public readonly amount: number,
    public readonly currency: string
  ) {}

  static of(amount: number, currency: string): Money {
    if (amount < 0) throw new Error('amount must be non-negative');
    const c = currency.trim().toUpperCase();
    if (c.length !== 3) throw new Error('currency must be 3-letter ISO code');
    return new Money(Math.round(amount * 100) / 100, c);
  }

  add(other: Money): Money {
    if (this.currency !== other.currency) {
      throw new Error(`Currency mismatch: ${this.currency} vs ${other.currency}`);
    }
    return Money.of(this.amount + other.amount, this.currency);
  }

  equals(other: Money): boolean {
    return this.amount === other.amount && this.currency === other.currency;
  }

  toString(): string {
    return `${this.amount} ${this.currency}`;
  }
}
```

---

## Pattern 2: Branded Types (zero runtime overhead)

Use when you need type safety at compile time but don't need methods or runtime validation.

```typescript
// Generic Brand utility
type Brand<Base, Tag> = Base & { readonly __brand: Tag };

type EmailAddress = Brand<string, 'EmailAddress'>;
type UserId       = Brand<number, 'UserId'>;
type CustomerId   = Brand<number, 'CustomerId'>;

// Factory — only way to get a branded value (validation here)
function createEmail(raw: string): EmailAddress {
  const normalized = raw.trim().toLowerCase();
  if (!normalized.includes('@')) throw new Error('Invalid email');
  return normalized as EmailAddress;
}

// TypeScript prevents confusion between same-primitive types:
function findCustomer(id: CustomerId): Customer { ... }
// findCustomer(userId)  ← TS error: UserId is not assignable to CustomerId
```

**`__brand` is never assigned at runtime** — it only exists in the type system. Zero overhead.

### Unique symbol branding (strictest, avoids tag string collision)

```typescript
declare const __brand: unique symbol;
type Brand<T, B> = T & { [__brand]: B };

type Percentage = Brand<number, 'Percentage'>;
type Quantity   = Brand<number, 'Quantity'>;
// Percentage and Quantity are incompatible even though both wrap number
```

---

## Pattern 3: Zod with `.brand<T>()` (API boundary + domain type)

```typescript
import { z } from 'zod';

const EmailSchema = z.string()
  .email()
  .transform(s => s.toLowerCase().trim())
  .brand<'EmailAddress'>();

type EmailAddress = z.infer<typeof EmailSchema>;

// Parse = validate + transform + get branded type in one step:
const email = EmailSchema.parse('USER@EXAMPLE.COM'); // 'user@example.com' as EmailAddress
// const bad: EmailAddress = 'raw@string' as EmailAddress; ← TS error (can't assign without parse)

// Compose schemas into a complex VO:
const MoneySchema = z.object({
  amount: z.number().nonnegative().transform(n => Math.round(n * 100) / 100),
  currency: z.string().length(3).transform(s => s.toUpperCase()),
}).brand<'Money'>();
```

---

## Result Type Pattern (avoid throw in factories)

For functional codebases that prefer `Result<T, E>` over exceptions:

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

// Or use a library like neverthrow, true-myth, or fp-ts Either
```

---

## Serialization

```typescript
// Class VO: implement toJSON for JSON.stringify support
export class Money {
  toJSON() {
    return { amount: this.amount, currency: this.currency };
  }

  static fromJSON(data: { amount: number; currency: string }): Money {
    return Money.of(data.amount, data.currency);
  }
}

// Branded type: already a primitive — serializes transparently
const email: EmailAddress = createEmail('user@example.com');
JSON.stringify({ email }); // '{"email":"user@example.com"}'
```

---

## Common Gotchas

| Gotcha | Fix |
|---|---|
| `readonly` is compile-time only | Add `Object.freeze(this)` in constructor for runtime immutability |
| Class VOs don't serialize nicely by default | Implement `toJSON()` |
| Branded type can be cast with `as` | Factory is the only safe entry point — use `eslint-plugin-no-restricted-syntax` to ban `as BrandedType` |
| `===` compares identity on class instances | Always implement `equals(other)` method; never use `===` for class VO equality |
| Private constructor prevents JSON deserialization | Add a `static fromJSON()` factory or a `protected` constructor |
