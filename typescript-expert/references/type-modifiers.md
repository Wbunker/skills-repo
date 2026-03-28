# Type Modifiers
## Chapter 9: Type Modifiers

---

## Top Types: any and unknown

TypeScript has two top types that can hold any value.

### any

`any` disables type checking entirely for a value. It is assignable to and from any type:

```typescript
let value: any = "hello"
value = 42          // OK
value = { x: 1 }   // OK
value.foo.bar.baz   // OK at compile time — no error, even if wrong at runtime
```

**Avoid `any`.** It is a full opt-out from TypeScript's safety guarantees. It exists for:
- Migrating JavaScript code incrementally
- Typing third-party code that has no type definitions
- Rare dynamic patterns where the shape is genuinely unknowable

### unknown

`unknown` is the **safe top type** — it accepts any value, but you cannot use it without narrowing first:

```typescript
let value: unknown = "hello"
value.toUpperCase()             // Error: Object is of type 'unknown'

if (typeof value === "string") {
  value.toUpperCase()           // OK — narrowed to string
}
```

**Prefer `unknown` over `any`** when you must accept a value of unknown type (e.g., from `JSON.parse`, external APIs, catch blocks). It forces you to check before using.

### Comparison

| | `any` | `unknown` |
|---|-------|---------|
| Assignable from | Everything | Everything |
| Assignable to | Everything | Only `any` and `unknown` |
| Operations allowed without narrowing | All (unsafe) | None |
| When to use | Legacy migration, dynamic escape hatch | Inputs of unknown shape that require validation |

---

## Type Predicates (User-Defined Type Guards)

A **type predicate** is a function whose return type asserts that a parameter is a specific type:

```typescript
function isString(value: unknown): value is string {
  return typeof value === "string"
}

function process(value: unknown): void {
  if (isString(value)) {
    value.toUpperCase()    // TypeScript knows value is string here
  }
}
```

Syntax: `(param: T): param is SpecificType`

Type predicates are useful when:
- The narrowing logic is complex and you want to reuse it
- You're working with `unknown` or `any` input

**Caution**: TypeScript trusts the predicate implementation — a wrong predicate silently breaks type safety.

---

## keyof

`keyof T` produces a union of the string (or number) keys of type `T`:

```typescript
interface User { name: string; age: number; email: string }

type UserKey = keyof User   // "name" | "age" | "email"

function getProperty<T, K extends keyof T>(obj: T, key: K): T[K] {
  return obj[key]
}

const user: User = { name: "Alice", age: 30, email: "a@b.com" }
const name = getProperty(user, "name")    // type: string
const age  = getProperty(user, "age")     // type: number
```

`keyof` is fundamental for creating generic utility functions that operate on object keys type-safely.

---

## typeof

`typeof` has two distinct uses in TypeScript:

### 1. Runtime typeof (JavaScript)
Used in expressions and type narrowing:

```typescript
if (typeof value === "string") { ... }
```

### 2. Type-level typeof

Used in type positions to get the *type* of a value:

```typescript
const config = { host: "localhost", port: 3000 }
type Config = typeof config   // { host: string; port: number }
```

Useful for:
- Getting the type of a value without manually declaring it
- Getting the type of a function or class constructor

```typescript
function add(a: number, b: number): number { return a + b }
type AddFn = typeof add   // (a: number, b: number) => number
```

---

## Type Assertions (as)

A **type assertion** tells TypeScript to treat a value as a specific type, bypassing type checking:

```typescript
const value: unknown = "hello"
const str = value as string     // assert to string
str.toUpperCase()               // OK
```

### When to Use Type Assertions

- Narrowing `unknown` when you are certain of the type
- Working with DOM APIs that return `Element | null`
- When TypeScript can't infer what you know from context

```typescript
const canvas = document.getElementById("canvas") as HTMLCanvasElement
```

### Limits of as

You can only assert between related types (TypeScript blocks "impossible" assertions):

```typescript
const n = 42 as string   // Error: Conversion of type 'number' to type 'string' may be a mistake
```

To force any assertion (escape hatch):

```typescript
const n = 42 as unknown as string   // double assertion — use with extreme caution
```

### as const

`as const` asserts the widest possible narrowing — every value becomes its literal type, and the object/array becomes `readonly`:

```typescript
const config = {
  host: "localhost",
  port: 3000,
} as const
// type: { readonly host: "localhost"; readonly port: 3000 }
```

Useful for:
- Preventing accidental mutation of configuration objects
- Getting literal types from object/array values for use in discriminated unions

---

## Non-Null Assertion Operator (!)

The `!` suffix operator asserts that a value is not `null` or `undefined`:

```typescript
function getTitle(el: HTMLElement | null): string {
  return el!.title    // assert el is not null
}
```

TypeScript removes `null | undefined` from the type. The assertion is compile-time only — if the value is actually `null` at runtime, you'll get a runtime error.

**Use sparingly.** Prefer explicit null checks or optional chaining (`?.`) where possible.

---

## Satisfies Operator

The `satisfies` operator (TypeScript 4.9+) checks that a value matches a type without widening the inferred type:

```typescript
type Colors = "red" | "green" | "blue"
type ColorMap = Record<Colors, string>

const palette = {
  red: "#ff0000",
  green: "#00ff00",
  blue: "#0000ff",
} satisfies ColorMap
// palette.red is still inferred as "#ff0000" (literal), not string
```

`satisfies` is useful when you want type safety without losing the narrower inferred type.

---

## Summary: When to Use Each

| Mechanism | Use When |
|-----------|---------|
| `unknown` | Accepting input of unknown type — force narrowing before use |
| `any` | Migrating JS code or truly dynamic patterns (avoid otherwise) |
| Type predicate (`is`) | Reusable complex narrowing logic |
| `keyof` | Accessing object properties type-safely in generic functions |
| `typeof` (type position) | Deriving a type from an existing value |
| `as` assertion | You know the type and TypeScript doesn't; or DOM API return types |
| `as const` | Lock down object/array to literal types and readonly |
| `!` | You're certain a value is non-null and can't express it via narrowing |
| `satisfies` | Validate shape while preserving the narrow inferred type |
