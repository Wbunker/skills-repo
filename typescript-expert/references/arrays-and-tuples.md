# Arrays and Tuples
## Chapter 6: Arrays

---

## Array Types

Two equivalent syntaxes for typed arrays:

```typescript
let names: string[]         // preferred — concise
let names: Array<string>    // generic form — useful in complex types
```

TypeScript infers the element type from the initial value:

```typescript
const nums = [1, 2, 3]        // inferred: number[]
const mixed = [1, "hello"]    // inferred: (number | string)[]
```

## Array Members

TypeScript knows the type of elements accessed by index:

```typescript
const names: string[] = ["Alice", "Bob"]
const first = names[0]   // inferred: string

names.push(42)           // Error: Argument of type 'number' is not assignable to 'string'
```

### Caution: Out-of-Bounds Access

By default, TypeScript treats array index access as returning the element type (not `T | undefined`), even when the index may be out of bounds. Enable `noUncheckedIndexedAccess` in `tsconfig.json` to get `T | undefined` from index access, which forces you to check:

```typescript
// with noUncheckedIndexedAccess: true
const el = names[0]   // type: string | undefined
if (el !== undefined) { console.log(el.toUpperCase()) }
```

## Spreads and Rests

### Spreading Arrays

```typescript
const first  = [1, 2, 3]
const second = [4, 5, 6]
const all    = [...first, ...second]   // number[]
```

### Spreading into a Tuple

Spread preserves tuple structure when using `as const` or typed tuples:

```typescript
function logArgs(...args: [string, number]): void {
  console.log(args[0], args[1])
}
```

### Rest Elements in Tuples

```typescript
type StringNumberBooleans = [string, number, ...boolean[]]
// first: string, second: number, rest: any number of booleans
```

## Readonly Arrays

Use `readonly T[]` or `ReadonlyArray<T>` to prevent mutation:

```typescript
function sum(numbers: readonly number[]): number {
  return numbers.reduce((a, b) => a + b, 0)
  // numbers.push(1)  // Error — readonly array
}
```

A mutable `T[]` is assignable to `readonly T[]` (widening), but not vice versa.

---

## Tuples

A **tuple** is an array with a fixed number of elements of specific types at specific positions:

```typescript
let point: [number, number]
point = [10, 20]    // OK
point = [10]        // Error: Source has 1 element(s) but target requires 2
point = [10, 20, 30]// Error: Source has 3 element(s) but target allows only 2
```

### Named Tuple Members

TypeScript supports labels in tuple types for documentation (they don't affect behavior):

```typescript
type Range = [start: number, end: number]
```

### Tuples as Function Return Types

Tuples are the TypeScript idiom for returning multiple values:

```typescript
function minMax(numbers: number[]): [number, number] {
  return [Math.min(...numbers), Math.max(...numbers)]
}

const [min, max] = minMax([1, 2, 3, 4, 5])
```

### Optional Tuple Elements

```typescript
type Point = [number, number, number?]   // 2D or 3D point
```

Optional elements must appear at the end of the tuple.

### Readonly Tuples

```typescript
const config: readonly [string, number] = ["localhost", 3000]
// config[0] = "remote"  // Error — readonly tuple
```

### const Assertions on Array Literals

Use `as const` to infer a tuple type (and literal types for each element) from an array literal:

```typescript
const point = [10, 20] as const     // type: readonly [10, 20]
const palette = ["red", "green"] as const  // type: readonly ["red", "green"]
```

Without `as const`, `[10, 20]` is inferred as `number[]`.

## Array Type Inference Summary

| Declaration | Inferred Type |
|------------|--------------|
| `const a = [1, 2, 3]` | `number[]` |
| `const a = [1, "x"]` | `(number \| string)[]` |
| `const a = [1, 2, 3] as const` | `readonly [1, 2, 3]` |
| `let a: [number, string] = [1, "x"]` | `[number, string]` (tuple) |

## Common Array Pitfalls

### Inferring `never[]`

An empty array literal without annotation infers `never[]`, which can't have elements pushed to it:

```typescript
const items = []          // inferred: never[] — usually wrong
const items: string[] = [] // OK — explicit annotation
```

### Mutable vs. Readonly Covariance

```typescript
const mutable: string[]         = ["a"]
const readonly: readonly string[] = mutable   // OK — widening

const readonly2: readonly string[] = ["a"]
const mutable2: string[]          = readonly2  // Error — can't narrow readonly
```
