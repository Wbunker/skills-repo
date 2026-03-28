# TypeScript Type System Basics
## Chapters 1–3: From JavaScript to TypeScript, The Type System, Unions and Literals

---

## Chapter 1: From JavaScript to TypeScript

### Why TypeScript?

JavaScript has no built-in type checking. TypeScript adds a **static type layer** that:
- Catches type mismatches and typos at compile time
- Documents function signatures and object shapes
- Powers IDE autocomplete, rename, and go-to-definition
- Compiles away entirely — output is plain JavaScript

### TypeScript Is a Superset

All valid JavaScript is valid TypeScript. TypeScript adds:
- Type annotations (`: string`, `: number`)
- Type-only constructs (interfaces, generics, enums, decorators)
- Compile-time error checking

### The TypeScript Compiler: `tsc`

```bash
npm install --save-dev typescript    # install locally
npx tsc --version                    # verify

npx tsc index.ts                     # compile a single file
npx tsc                              # compile using tsconfig.json
npx tsc --init                       # create a starter tsconfig.json
```

`tsc` produces `.js` output. It reports errors but (by default) still emits JavaScript.

### TypeScript's Role in the Toolchain

```
.ts source files
     │
     ▼
  tsc (type checker + transpiler)
     │
     ▼
.js output  ──▶  Node / browser / bundler
```

TypeScript does **not** run at runtime. All types are erased during compilation.

### Freedom and Strictness

TypeScript can be configured from lenient (permissive) to strict. The `strict` flag in `tsconfig.json` enables the recommended set of checks. New projects should start with `"strict": true`.

---

## Chapter 2: The Type System

### What Is a Type?

A **type** is the set of values a variable can hold, along with the operations valid on it. TypeScript infers types and checks that all operations are valid for the inferred (or declared) type.

### Type Inference

TypeScript infers the type of most values automatically:

```typescript
let name = "Alice"       // TypeScript infers: string
let age = 30             // TypeScript infers: number
let active = true        // TypeScript infers: boolean
```

You can always add explicit annotations, but inference usually suffices for local variables.

### Type Annotations

Use `: Type` to explicitly declare the type of a variable, parameter, or return value:

```typescript
let name: string = "Alice"
let age: number
age = 30

function greet(name: string): string {
  return `Hello, ${name}`
}
```

### Type Errors vs Syntax Errors

| Error Kind | When Detected | Blocks Compilation? |
|------------|---------------|---------------------|
| **Syntax error** | Parse time | Yes — invalid JS/TS |
| **Type error** | Type-check time | By default no; use `noEmitOnError: true` |

TypeScript reports type errors but (by default) still emits JavaScript output. Use `"noEmitOnError": true` in `tsconfig.json` to block emit when errors exist.

### Assignability

TypeScript checks whether a value is **assignable** to a target type. A value is assignable when it is of the same type or a structural subtype.

```typescript
let value: number
value = 42        // OK
value = "hello"   // Error: Type 'string' is not assignable to type 'number'
```

### Type Shapes

TypeScript understands the **shape** of objects — which properties exist and their types. Accessing a property not in the declared type is an error.

```typescript
let user = { name: "Alice", age: 30 }
console.log(user.name)   // OK
console.log(user.email)  // Error: Property 'email' does not exist
```

### Modules

TypeScript files with at least one `import` or `export` are **modules** (isolated scope). Files without imports/exports are **scripts** (global scope). Always use modules for real projects.

```typescript
// math.ts
export function add(a: number, b: number): number { return a + b }

// main.ts
import { add } from "./math"
```

---

## Chapter 3: Unions and Literals

### Union Types

A **union type** allows a value to be one of several types, separated by `|`:

```typescript
let id: string | number
id = "abc"    // OK
id = 123      // OK
id = true     // Error
```

### Narrowing

TypeScript uses **control flow analysis** to narrow a union type to a more specific type inside a branch:

```typescript
function printId(id: string | number) {
  if (typeof id === "string") {
    console.log(id.toUpperCase())  // TypeScript knows id is string here
  } else {
    console.log(id.toFixed(2))     // TypeScript knows id is number here
  }
}
```

Common narrowing techniques:

| Technique | Syntax | Use For |
|-----------|--------|---------|
| `typeof` check | `typeof x === "string"` | Primitives |
| Truthiness | `if (x)` | null, undefined, 0, "" |
| Equality | `x === "circle"` | Literal types / discriminants |
| `instanceof` | `x instanceof Date` | Class instances |
| `in` operator | `"prop" in x` | Optional property presence |
| Type predicate | `(x): x is T => ...` | Custom logic |

### Literal Types

A **literal type** is a type that represents exactly one specific value:

```typescript
let direction: "north" | "south" | "east" | "west"
direction = "north"   // OK
direction = "up"      // Error

type Status = "pending" | "active" | "closed"
```

Literal types are most useful in union types to create a constrained set of allowed values (similar to an enum but lighter weight).

### Type Widening

When assigned to a `let`, TypeScript infers the wider type (e.g., `string`). When assigned to a `const`, TypeScript infers the narrower literal type (e.g., `"north"`):

```typescript
let direction = "north"   // inferred: string (let — may be reassigned)
const direction = "north" // inferred: "north" (const — will never change)
```

Use `as const` to force a literal type on a `let` or object.

### Strictness

The `strict` compiler option enables several checks:

| Flag | What It Checks |
|------|---------------|
| `strictNullChecks` | `null` and `undefined` are not assignable to other types |
| `noImplicitAny` | Variables must have inferrable or explicit types |
| `strictFunctionTypes` | Stricter checking for function parameter types |
| `strictPropertyInitialization` | Class properties must be initialized in constructor |
| `strictBindCallApply` | Stricter types for `.bind`, `.call`, `.apply` |

**Always use `"strict": true`** in new projects. It catches the most bugs.

### null and undefined

With `strictNullChecks` enabled (included in `strict`):
- `null` and `undefined` are **distinct types** — not assignable to `string` or `number`
- You must explicitly include them in union types when a value might be absent:

```typescript
let name: string | null = null
name = "Alice"        // OK
name = null           // OK
name.toUpperCase()    // Error: Object is possibly null

if (name !== null) {
  name.toUpperCase()  // OK — narrowed to string
}
```

### Undefined vs. Optional

- `undefined`: a value that is explicitly undefined
- Optional property (`?:`): may be omitted entirely (its type is `T | undefined`)

```typescript
interface User {
  name: string
  nickname?: string       // type is string | undefined; may be omitted
  bio: string | undefined // must be present, but value may be undefined
}
```
