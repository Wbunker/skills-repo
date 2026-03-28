# Type Operations
## Chapter 15: Type Operations

Advanced TypeScript type constructs that let you create new types from existing ones programmatically.

---

## Mapped Types

A **mapped type** creates a new object type by iterating over the keys of an existing type and transforming each property:

```typescript
type Readonly<T> = {
  readonly [K in keyof T]: T[K]
}

type Optional<T> = {
  [K in keyof T]?: T[K]
}

type Nullable<T> = {
  [K in keyof T]: T[K] | null
}
```

### Mapped Type Syntax

```typescript
type MyMapped<T> = {
  [K in keyof T]: NewType
}
```

- `K in keyof T` — iterate over all keys of `T`
- `T[K]` — index access: get the type of property `K` on `T`
- Add `readonly` or `?` to make properties readonly/optional
- Prefix with `-` to *remove* modifiers: `-readonly`, `-?`

```typescript
// Remove optionality from all properties
type Required<T> = {
  [K in keyof T]-?: T[K]
}

// Remove readonly from all properties
type Mutable<T> = {
  -readonly [K in keyof T]: T[K]
}
```

### Mapping to a Different Value Type

```typescript
type Stringify<T> = {
  [K in keyof T]: string
}

type Getters<T> = {
  [K in keyof T as `get${Capitalize<string & K>}`]: () => T[K]
}
// { getName: () => string; getAge: () => number; ... }
```

### Key Remapping with as

TypeScript 4.1+ supports remapping keys in mapped types using `as`:

```typescript
type Prefixed<T> = {
  [K in keyof T as `prefix_${string & K}`]: T[K]
}
```

---

## Conditional Types

A **conditional type** branches on whether a type satisfies a constraint:

```typescript
type IsString<T> = T extends string ? true : false

type A = IsString<string>   // true
type B = IsString<number>   // false
```

Syntax: `T extends U ? TrueType : FalseType`

### Practical Conditional Types

```typescript
// Extract the element type from an array
type ElementType<T> = T extends (infer E)[] ? E : never

type A = ElementType<string[]>   // string
type B = ElementType<number[]>   // number
type C = ElementType<string>     // never

// NonNullable — remove null and undefined
type NonNullable<T> = T extends null | undefined ? never : T
```

### infer Keyword

`infer` introduces a type variable within a conditional type branch, capturing part of a type:

```typescript
// Extract return type of a function
type ReturnType<T> = T extends (...args: any[]) => infer R ? R : never

type R1 = ReturnType<() => string>           // string
type R2 = ReturnType<(x: number) => boolean> // boolean

// Extract parameter types
type Parameters<T> = T extends (...args: infer P) => any ? P : never

type P1 = Parameters<(a: string, b: number) => void>  // [string, number]
```

### Distributive Conditional Types

When a conditional type receives a **union type** for `T`, it **distributes** over each member:

```typescript
type ToArray<T> = T extends any ? T[] : never

type A = ToArray<string | number>   // string[] | number[]
// NOT: (string | number)[] — it distributes!
```

To prevent distribution, wrap in a tuple:

```typescript
type ToArrayNonDist<T> = [T] extends [any] ? T[] : never

type B = ToArrayNonDist<string | number>   // (string | number)[]
```

---

## Template Literal Types

TypeScript 4.1+ supports string template literal types:

```typescript
type Greeting = `Hello, ${string}`
type EventName = `on${Capitalize<string>}`

type Direction = "north" | "south" | "east" | "west"
type DirectionMessage = `Moving ${Direction}`
// "Moving north" | "Moving south" | "Moving east" | "Moving west"
```

### Template Literal with Union Distribution

Template literals distribute over unions automatically:

```typescript
type Suit = "hearts" | "diamonds" | "clubs" | "spades"
type Rank = "ace" | "king" | "queen" | "jack"
type Card = `${Rank} of ${Suit}`
// "ace of hearts" | "ace of diamonds" | ... (16 combinations)
```

### String Manipulation Types

Built-in utility types for string literal transformation:

| Type | Effect |
|------|--------|
| `Uppercase<S>` | `"hello"` → `"HELLO"` |
| `Lowercase<S>` | `"HELLO"` → `"hello"` |
| `Capitalize<S>` | `"hello"` → `"Hello"` |
| `Uncapitalize<S>` | `"Hello"` → `"hello"` |

---

## Built-in Utility Types

TypeScript ships with a library of utility types for common type transformations:

### Object Utilities

| Utility | Effect |
|---------|--------|
| `Partial<T>` | All properties of `T` become optional |
| `Required<T>` | All properties of `T` become required |
| `Readonly<T>` | All properties of `T` become readonly |
| `Record<K, V>` | Object with keys of type `K` and values of type `V` |
| `Pick<T, K>` | New type with only the specified keys from `T` |
| `Omit<T, K>` | New type without the specified keys from `T` |

```typescript
type User = { id: number; name: string; email: string }

type CreateUser = Omit<User, "id">              // { name: string; email: string }
type UserPreview = Pick<User, "id" | "name">    // { id: number; name: string }
type PartialUser = Partial<User>                // all optional
type StringMap = Record<string, string>         // { [key: string]: string }
```

### Union Utilities

| Utility | Effect |
|---------|--------|
| `Exclude<T, U>` | Remove from union `T` all members assignable to `U` |
| `Extract<T, U>` | Keep only union members assignable to `U` |
| `NonNullable<T>` | Remove `null` and `undefined` from `T` |

```typescript
type T = string | number | boolean
type NoNumbers = Exclude<T, number>   // string | boolean
type OnlyStrings = Extract<T, string> // string

type MaybeString = string | null | undefined
type DefiniteString = NonNullable<MaybeString>  // string
```

### Function Utilities

| Utility | Effect |
|---------|--------|
| `ReturnType<T>` | Extract return type of function type `T` |
| `Parameters<T>` | Extract parameter types as a tuple |
| `ConstructorParameters<T>` | Extract constructor parameter types |
| `InstanceType<T>` | Extract the instance type of a class constructor |
| `Awaited<T>` | Unwrap a `Promise<T>` (or nested promises) to `T` |

```typescript
function fetchUser(id: string): Promise<User> { ... }

type FetchReturn = Awaited<ReturnType<typeof fetchUser>>  // User
type FetchParams = Parameters<typeof fetchUser>           // [string]
```

---

## Index Access Types

Access the type of a property by indexing into another type:

```typescript
type User = { name: string; age: number; address: { city: string } }

type Name    = User["name"]          // string
type Age     = User["age"]           // number
type City    = User["address"]["city"] // string

type UserVals = User[keyof User]     // string | number | { city: string }
```

---

## Combining Techniques: Real Examples

### Making All Properties Deeply Optional

```typescript
type DeepPartial<T> = {
  [K in keyof T]?: T[K] extends object ? DeepPartial<T[K]> : T[K]
}
```

### Picking by Value Type

```typescript
type PickByValue<T, V> = {
  [K in keyof T as T[K] extends V ? K : never]: T[K]
}

type User = { name: string; age: number; active: boolean }
type Strings = PickByValue<User, string>   // { name: string }
```

### Event Map to Handler Map

```typescript
type EventMap = { click: MouseEvent; keydown: KeyboardEvent }
type Handlers = { [K in keyof EventMap]: (event: EventMap[K]) => void }
// { click: (event: MouseEvent) => void; keydown: (event: KeyboardEvent) => void }
```
