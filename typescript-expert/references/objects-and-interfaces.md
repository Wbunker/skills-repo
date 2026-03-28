# Objects and Interfaces
## Chapters 4, 7: Objects, Interfaces

---

## Chapter 4: Objects

### Object Types

TypeScript uses **structural typing**: an object satisfies a type if it has all required properties with compatible types. The type is the *shape*, not the declared name.

```typescript
let user: { name: string; age: number }
user = { name: "Alice", age: 30 }   // OK
user = { name: "Bob" }              // Error: missing age
```

### Type Aliases for Object Shapes

Use `type` to give a reusable name to an object shape:

```typescript
type User = {
  name: string
  age: number
}

function greet(user: User): string {
  return `Hello, ${user.name}`
}
```

### Optional Properties

Add `?` to mark a property as optional. Its type becomes `T | undefined`.

```typescript
type Post = {
  title: string
  content: string
  publishedAt?: Date    // may be omitted; type is Date | undefined
}
```

### Readonly Properties (on Object Types)

Mark a property `readonly` to prevent reassignment after initialization:

```typescript
type Config = {
  readonly host: string
  readonly port: number
}

const cfg: Config = { host: "localhost", port: 3000 }
cfg.host = "remote"  // Error: Cannot assign to 'host' because it is a read-only property
```

`readonly` is a compile-time check only — it does not affect runtime behavior.

### Structural Typing in Practice

TypeScript allows objects with **extra properties** to satisfy a type, as long as they have all required ones — *except* when the object is an object literal passed directly:

```typescript
type Named = { name: string }

const user = { name: "Alice", age: 30 }
const named: Named = user   // OK — variable assignment checks structurally

const named2: Named = { name: "Alice", age: 30 }  // Error — excess property check on object literals
```

The excess property check fires only when an object literal is directly assigned. Extract to a variable to bypass it (when intentional).

### Discriminated Unions (Tagged Unions)

A discriminated union is a union of object types where each member has a **common literal property** (the discriminant) with a unique value. This enables exhaustive narrowing.

```typescript
type Circle  = { kind: "circle";  radius: number }
type Square  = { kind: "square";  side: number }
type Shape   = Circle | Square

function area(shape: Shape): number {
  switch (shape.kind) {
    case "circle": return Math.PI * shape.radius ** 2
    case "square": return shape.side ** 2
  }
}
```

Design discriminated unions so that:
- The discriminant is a string literal
- Every member has the discriminant
- `switch`/`if` on the discriminant narrows to a specific member

### Intersection Types

An **intersection type** (`A & B`) produces a type that must satisfy *both* A and B simultaneously:

```typescript
type Named     = { name: string }
type Timestamped = { createdAt: Date }

type NamedRecord = Named & Timestamped
// equivalent to: { name: string; createdAt: Date }

const record: NamedRecord = { name: "Alice", createdAt: new Date() }
```

Intersections are useful for combining multiple type aliases or mixing in shared properties.

---

## Chapter 7: Interfaces

### Declaring an Interface

An `interface` names an object type and can be extended, implemented, and merged:

```typescript
interface User {
  name: string
  age: number
}
```

### Interface vs. Type Alias

| Feature | `interface` | `type` |
|---------|------------|--------|
| Object shapes | Yes | Yes |
| Unions / intersections | No (directly) | Yes |
| Declaration merging | Yes | No |
| Extending | `extends` keyword | `&` intersection |
| Implementing in a class | Yes | Yes (for object shapes) |

**Rule of thumb**: prefer `interface` for public API shapes and class-like hierarchies. Use `type` when you need unions, intersections, or complex computed types.

### Extending Interfaces

An interface can extend one or more other interfaces, inheriting all their properties:

```typescript
interface Animal {
  name: string
}

interface Dog extends Animal {
  breed: string
}

const dog: Dog = { name: "Rex", breed: "Labrador" }
```

A `type` achieves the same with intersection: `type Dog = Animal & { breed: string }`.

### Optional and Readonly Interface Properties

```typescript
interface Config {
  readonly host: string     // cannot be reassigned
  port: number
  timeout?: number          // optional; type is number | undefined
}
```

### Method Signatures

Two ways to declare methods in an interface:

```typescript
interface Formatter {
  format(value: string): string           // method signature
  format: (value: string) => string       // property of function type
}
```

The method signature form is slightly more permissive with variance; the property function type is stricter. Prefer the method signature form for most interfaces.

### Call Signatures

An interface can describe a function that is also an object (with properties):

```typescript
interface Greeter {
  (name: string): string    // call signature
  language: string          // also has a property
}

const greet: Greeter = (name) => `Hello, ${name}`
greet.language = "English"
```

### Index Signatures

An index signature allows arbitrary keys of a given type:

```typescript
interface StringMap {
  [key: string]: string
}

const headers: StringMap = { "Content-Type": "application/json" }
```

Caveats:
- All *named* properties must be compatible with the index signature's value type
- Prefer `Record<string, string>` (see type-operations.md) for simple cases
- Index signatures allow access to any key without error, which can hide typos

### Interface Merging (Declaration Merging)

If two `interface` declarations share the same name in the same scope, TypeScript **merges** them into one:

```typescript
interface Window { myPlugin: () => void }
interface Window { title: string }
// Both declarations merge — Window now has both myPlugin and title
```

This is how DefinitelyTyped packages augment third-party types. You cannot merge `type` aliases.

### Augmenting Module Interfaces

To add properties to an existing interface from a third-party library:

```typescript
// global.d.ts
declare module "express" {
  interface Request {
    user?: { id: string; name: string }
  }
}
```

This uses declaration merging to extend `express.Request` without modifying the library.
