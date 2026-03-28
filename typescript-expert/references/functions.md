# Functions
## Chapter 5: Functions

---

## Parameter Types

Annotate each parameter with its type. TypeScript does not infer parameter types from usage (unlike return types).

```typescript
function add(a: number, b: number): number {
  return a + b
}
```

Without an annotation, parameters default to `any` (or an error under `noImplicitAny`).

## Return Types

TypeScript infers return types from the function body. You can add an explicit annotation for documentation and to catch mismatches:

```typescript
function greet(name: string): string {
  return `Hello, ${name}`
}
```

If the return type is inferred as `string | undefined` but you declared `: string`, TypeScript will report an error on any branch that might return `undefined`.

## Optional Parameters

Add `?` after the parameter name to make it optional. Its type becomes `T | undefined`.

```typescript
function greet(name: string, greeting?: string): string {
  return `${greeting ?? "Hello"}, ${name}`
}

greet("Alice")           // OK
greet("Alice", "Hi")     // OK
```

Optional parameters must come *after* required parameters.

## Default Parameters

Default parameters are always optional at the call site. Their type is inferred from the default value (no annotation needed, though you can add one).

```typescript
function greet(name: string, greeting = "Hello"): string {
  return `${greeting}, ${name}`
}

greet("Alice")           // OK — greeting = "Hello"
greet("Alice", "Hi")     // OK
greet("Alice", undefined)// OK — uses default
```

Default parameters are the idiomatic way to handle optional-with-a-default in TypeScript.

## Rest Parameters

A rest parameter collects remaining arguments into an array:

```typescript
function sum(...numbers: number[]): number {
  return numbers.reduce((a, b) => a + b, 0)
}

sum(1, 2, 3)    // 6
```

Rest parameters must be the last parameter and can only appear once.

## Function Types

A function type describes the signature of a function value:

```typescript
type Transformer = (value: string) => string

const upper: Transformer = (s) => s.toUpperCase()

function apply(values: string[], fn: Transformer): string[] {
  return values.map(fn)
}
```

### Arrow Functions

```typescript
const double = (n: number): number => n * 2
```

TypeScript infers parameter types from a typed function variable or parameter context (contextual typing):

```typescript
const nums = [1, 2, 3]
nums.map(n => n * 2)   // n inferred as number from Array<number>.map
```

## void

`void` is the return type of functions that do not return a meaningful value (they `return` nothing, or `return undefined`):

```typescript
function log(message: string): void {
  console.log(message)
  // no return value
}
```

A variable of type `void` can only be assigned `undefined`. `void` signals "callers should not use the return value."

## never

`never` is the return type of functions that **never return** — they always throw or have an infinite loop:

```typescript
function fail(message: string): never {
  throw new Error(message)
}

function forever(): never {
  while (true) {}
}
```

`never` is also the type of a value in an unreachable branch after narrowing:

```typescript
function assertNever(x: never): never {
  throw new Error("Unexpected value: " + x)
}
```

Use `assertNever` at the end of an exhaustive `switch` to get a compile-time error if a new union member is added but not handled.

### void vs. never vs. undefined

| Type | Meaning | Return statement |
|------|---------|-----------------|
| `void` | Returns nothing meaningful | `return` / `return undefined` / no return |
| `never` | Never returns at all | Throws or infinite loops |
| `undefined` | Explicitly returns the value `undefined` | `return undefined` |

## Function Overloads

TypeScript supports **overload signatures** to describe multiple valid call signatures for a single function:

```typescript
function createDate(timestamp: number): Date
function createDate(month: number, day: number, year: number): Date
function createDate(monthOrTimestamp: number, day?: number, year?: number): Date {
  // implementation signature — not callable directly
  if (day === undefined || year === undefined) {
    return new Date(monthOrTimestamp)
  }
  return new Date(year, monthOrTimestamp, day)
}

createDate(1234567890)       // uses overload 1
createDate(3, 15, 2024)      // uses overload 2
createDate(3, 15)            // Error — neither overload matches
```

Rules:
- Overload signatures appear before the implementation signature
- The implementation signature is not callable directly — only the overload signatures are visible to callers
- The implementation signature must be compatible with all overload signatures
- Prefer union-typed parameters over overloads when possible — overloads add complexity

## this Parameter

TypeScript can type-check `this` inside a method or function using a special `this` parameter (it is not a real parameter — it's erased at compile time):

```typescript
interface User { name: string; greet(this: User): string }

const user: User = {
  name: "Alice",
  greet() { return `Hello, ${this.name}` }
}
```

## Contextual Typing

When a function is assigned to a typed variable or passed as a typed argument, TypeScript infers parameter types from the context:

```typescript
type Predicate = (value: number) => boolean

const isEven: Predicate = (n) => n % 2 === 0   // n inferred as number
```

## Parameter Destructuring

Type the destructured parameter as an object:

```typescript
function greet({ name, age }: { name: string; age: number }): string {
  return `${name} is ${age}`
}
```

Or use a named type/interface:

```typescript
type User = { name: string; age: number }
function greet({ name, age }: User): string { ... }
```
