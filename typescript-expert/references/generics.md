# Generics
## Chapter 10: Generics

---

## What Are Generics?

Generics let you write functions, interfaces, and classes that work with **any type** while still being type-safe. Instead of accepting `any`, a generic accepts a **type parameter** (`T`) that is inferred or specified at the call site.

```typescript
// Without generics — loses type information
function identity(value: any): any { return value }

// With generics — type is preserved
function identity<T>(value: T): T { return value }

const str = identity("hello")   // T inferred as string; returns string
const num = identity(42)        // T inferred as number; returns number
```

---

## Generic Functions

Declare type parameters in angle brackets before the parameter list:

```typescript
function firstElement<T>(array: T[]): T | undefined {
  return array[0]
}

const first = firstElement([1, 2, 3])      // T inferred as number
const name  = firstElement(["a", "b"])     // T inferred as string
```

### Multiple Type Parameters

```typescript
function pair<T, U>(first: T, second: U): [T, U] {
  return [first, second]
}

const p = pair("hello", 42)   // [string, number]
```

### Explicit Type Arguments

TypeScript infers type arguments in most cases. You can provide them explicitly when inference fails:

```typescript
const empty = firstElement<string>([])   // T explicitly set to string
```

---

## Generic Interfaces

```typescript
interface Box<T> {
  value: T
  transform: (value: T) => T
}

const strBox: Box<string> = {
  value: "hello",
  transform: (s) => s.toUpperCase(),
}
```

### Generic Interface as a Container Pattern

```typescript
interface ApiResponse<T> {
  data: T
  status: number
  message: string
}

async function fetchUser(): Promise<ApiResponse<User>> { ... }
```

---

## Generic Classes

```typescript
class Stack<T> {
  private items: T[] = []

  push(item: T): void { this.items.push(item) }
  pop(): T | undefined { return this.items.pop() }
  peek(): T | undefined { return this.items[this.items.length - 1] }
  get size(): number { return this.items.length }
}

const numStack = new Stack<number>()
numStack.push(1)
numStack.push(2)
const top = numStack.pop()    // type: number | undefined
```

TypeScript infers the type argument from the first `push` call if not specified explicitly.

---

## Generic Type Aliases

```typescript
type Nullable<T> = T | null
type Maybe<T> = T | null | undefined

type Result<T, E = Error> = { ok: true; value: T } | { ok: false; error: E }

function divide(a: number, b: number): Result<number, string> {
  if (b === 0) return { ok: false, error: "Division by zero" }
  return { ok: true, value: a / b }
}
```

---

## Generic Constraints (extends)

Use `extends` to constrain a type parameter to a subset of types:

```typescript
function getProperty<T, K extends keyof T>(obj: T, key: K): T[K] {
  return obj[key]
}

const user = { name: "Alice", age: 30 }
getProperty(user, "name")    // OK — "name" is a key of user
getProperty(user, "email")   // Error — "email" is not a key of user
```

### Constraining to a Shape

```typescript
function logName<T extends { name: string }>(item: T): void {
  console.log(item.name)   // safe — T guaranteed to have name: string
}

logName({ name: "Alice", age: 30 })  // OK
logName({ age: 30 })                 // Error — missing name
```

### Constraining to a Class

```typescript
function create<T>(Ctor: new () => T): T {
  return new Ctor()
}
```

---

## Generic Defaults

Type parameters can have default types, making them optional when specified explicitly:

```typescript
interface Paginated<T, Cursor = string> {
  items: T[]
  nextCursor: Cursor | null
}

type UserPage = Paginated<User>              // Cursor defaults to string
type NumPage  = Paginated<number, number>   // Cursor explicitly number
```

---

## Promise<T>

`Promise<T>` is the built-in generic for asynchronous operations that resolve to type `T`:

```typescript
async function fetchUser(id: string): Promise<User> {
  const response = await fetch(`/users/${id}`)
  return response.json() as Promise<User>
}

const user: User = await fetchUser("123")
```

`async` functions always return a `Promise<T>` where `T` is the return type of the function body.

---

## Common Generic Patterns

### Identity / Passthrough

```typescript
function identity<T>(value: T): T { return value }
```

### Mapping Array Elements

```typescript
function map<T, U>(array: T[], transform: (item: T) => U): U[] {
  return array.map(transform)
}
```

### Optional Return

```typescript
function find<T>(array: T[], predicate: (item: T) => boolean): T | undefined {
  return array.find(predicate)
}
```

### Narrowing with Generics

```typescript
function filterNullish<T>(array: (T | null | undefined)[]): T[] {
  return array.filter((item): item is T => item !== null && item !== undefined)
}
```

---

## Generics vs. any vs. Union Types

| Approach | Type safety | Flexibility |
|----------|------------|------------|
| `any` | None — disables checking | Maximum |
| Union (`string \| number`) | Full — but only for listed types | Fixed set |
| Generic `<T>` | Full — type is tracked end-to-end | Maximum |

Use generics when you need flexibility *and* type safety — when the type depends on the call site, not the definition site.

---

## Type Parameter Naming Conventions

| Name | Convention |
|------|-----------|
| `T` | General "type" (most common) |
| `K` | Key (usually `extends keyof T`) |
| `V` | Value |
| `E` | Element or Error |
| `R` | Return type |
| Descriptive names | `TInput`, `TOutput` — preferred in complex generics |
