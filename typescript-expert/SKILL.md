---
name: typescript-expert
description: TypeScript expertise covering the type system, unions and literals, objects, functions, arrays, interfaces, classes, type modifiers, generics, configuration, declaration files, syntax extensions, and advanced type operations. Use when writing TypeScript code, debugging type errors, designing type-safe APIs, configuring tsconfig.json, working with generics, understanding structural typing, or using advanced type operations like mapped types and conditional types. Based on "Learning TypeScript" by Josh Goldberg (O'Reilly, 2022).
---

# TypeScript Expert

Based on: *Learning TypeScript* by Josh Goldberg (O'Reilly, 2022).

TypeScript is a typed superset of JavaScript that compiles to plain JavaScript. Its structural type system catches errors at compile time while preserving JavaScript's flexibility.

## TypeScript Type System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                      TYPESCRIPT TYPE UNIVERSE                        │
│                                                                     │
│  TOP TYPES ──────────────────────────────────────────────────────── │
│  ┌──────────┐  ┌──────────────────────────────────────────────────┐ │
│  │   any    │  │  unknown  (must narrow before use)               │ │
│  └────┬─────┘  └───────────────────────┬──────────────────────────┘ │
│       │ (opt-out of type checking)     │ (safe top type)            │
│       ▼                                ▼                            │
│  ┌─────────────────────────────────────────────────────────────────┐│
│  │                  OBJECT / STRUCTURAL TYPES                      ││
│  │   interfaces · type aliases · classes · arrays · tuples         ││
│  │   { prop: T }  ·  A & B  ·  A | B                              ││
│  └────────────────────────────┬────────────────────────────────────┘│
│                               │                                     │
│  ┌─────────────────────────────────────────────────────────────────┐│
│  │                     PRIMITIVE TYPES                             ││
│  │    string  ·  number  ·  boolean  ·  bigint  ·  symbol          ││
│  │    null  ·  undefined                                           ││
│  └────────────────────────────┬────────────────────────────────────┘│
│                               │                                     │
│  BOTTOM TYPE ─────────────────▼──────────────────────────────────── │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │  never  (no valid value; assignable to everything)           │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  KEY RELATIONSHIPS                                                  │
│  Structural (duck typing): shape compatibility, not nominal identity│
│  Union   (A | B): value is A or B — narrowing resolves which        │
│  Intersection (A & B): value satisfies both A and B                │
│  Narrowing: control-flow refines union types to specific branches   │
└─────────────────────────────────────────────────────────────────────┘
```

## Quick Reference

| Task | Reference |
|------|-----------|
| TypeScript basics, tsc, type inference, type errors, unions, literals, narrowing | [type-system-basics.md](references/type-system-basics.md) |
| Object types, structural typing, discriminated unions, intersection types, interfaces, index signatures | [objects-and-interfaces.md](references/objects-and-interfaces.md) |
| Function parameters, return types, overloads, void/never, rest/optional/default params | [functions.md](references/functions.md) |
| Array types, tuples, readonly arrays, spreads and rests | [arrays-and-tuples.md](references/arrays-and-tuples.md) |
| Classes, constructors, visibility, abstract, implements, static, override | [classes.md](references/classes.md) |
| any/unknown, type predicates (is), keyof, typeof, type assertions (as), non-null assertions | [type-modifiers.md](references/type-modifiers.md) |
| Generic functions, generic interfaces/classes, constraints, defaults, Promise<T> | [generics.md](references/generics.md) |
| .d.ts files, DefinitelyTyped, declare, module declarations, tsconfig.json, IDE features | [configuration-and-declarations.md](references/configuration-and-declarations.md) |
| Decorators, enums, const enums, namespaces | [syntax-extensions.md](references/syntax-extensions.md) |
| Mapped types, conditional types, template literal types, infer, utility types | [type-operations.md](references/type-operations.md) |

## Reference Files

| File | Chapters | Key Topics |
|------|----------|-----------|
| `type-system-basics.md` | 1–3 | JS→TS, tsc, type inference, type annotations, type errors vs syntax errors, assignability, union types, literal types, narrowing, strictness |
| `objects-and-interfaces.md` | 4, 7 | Object types, optional properties, structural typing, discriminated unions, intersection types (&), interfaces, readonly, call signatures, index signatures, interface merging |
| `functions.md` | 5 | Parameter types, return types, optional/default/rest params, function types, overloads, void vs never vs undefined |
| `arrays-and-tuples.md` | 6 | Typed arrays, array members, spreads and rests, tuples, readonly arrays |
| `classes.md` | 8 | Class properties, constructors, member visibility (public/protected/private/#), readonly, abstract classes, implements, static, override |
| `type-modifiers.md` | 9 | Top types (any, unknown), type predicates (is), keyof, typeof, type assertions (as), non-null assertion (!), const assertions |
| `generics.md` | 10 | Generic functions, generic interfaces, generic classes, generic type aliases, constrained generics, generic defaults, Promise<T> |
| `configuration-and-declarations.md` | 11–13 | .d.ts files, DefinitelyTyped (@types/), declare keyword, module declarations, tsconfig.json options, strictness flags, module/target settings, IDE features |
| `syntax-extensions.md` | 14 | Decorators, enum types, const enums, namespaces (legacy context), class field declarations |
| `type-operations.md` | 15 | Mapped types, conditional types, template literal types, infer keyword, distributive conditionals, built-in utility types |

## Core Decision Trees

### How Do I Type This Value?

```
What is the value?
├── Primitive (string, number, boolean, bigint, symbol)
│   ├── Exact value known at compile time → literal type ("hello", 42, true)
│   └── Any value of that primitive → primitive type (string, number, boolean)
├── Object with known shape
│   ├── Inline, single use → object type literal { name: string; age: number }
│   ├── Reusable, extendable, class-like → interface
│   └── Reusable with union/intersection/mapped shape → type alias
├── Function → see functions.md
├── Array
│   ├── All elements same type → T[] or Array<T>
│   └── Fixed length, mixed types → tuple [string, number, boolean]
├── Could be one of several types → union (A | B | C)
├── Must satisfy multiple shapes → intersection (A & B)
├── Comes from outside / shape unknown
│   ├── Will narrow before use → unknown (safe, preferred)
│   └── Bypass checking entirely → any (avoid unless necessary)
└── Should never actually occur → never
```

### Type Error: What's Wrong?

```
What does the error say?
├── "Type X is not assignable to type Y"
│   ├── Wrong type assigned → fix value or widen annotation
│   ├── Union type not narrowed → add type guard before use
│   └── Structural mismatch → check property names and types
├── "Property X does not exist on type Y"
│   ├── Typo → fix spelling
│   ├── Optional property accessed without check → narrow first
│   └── Type is a union → narrow to the branch that has the property
├── "Argument of type X is not assignable to parameter of type Y"
│   ├── Wrong argument type → fix call site
│   └── Excess properties (object literal) → extract to variable first
├── "Object is possibly null or undefined"
│   └── Use ?. / ?? / explicit null check / non-null assertion (!)
└── "Type X has no properties in common with type Y"
    └── Union with no overlap → check discriminant field or types
```

### Interface vs Type Alias?

```
Do you need...
├── Declaration merging (augmenting the type from multiple files)?
│   └── interface  (only interfaces merge)
├── A union, intersection, or mapped/conditional shape?
│   └── type alias  (interfaces cannot express these directly)
├── Aliasing a primitive, tuple, or template literal type?
│   └── type alias
├── A class-like hierarchy with extends?
│   └── interface  (conventional; slightly better error messages)
└── A reusable object shape with no special requirements?
    └── either — pick one and be consistent
```

### Narrowing: Which Guard to Use?

```
What are you narrowing?
├── Primitive type → typeof x === "string" | "number" | "boolean" | "symbol" | "bigint"
├── null or undefined → x !== null  /  x != null (covers both)  /  x?.prop
├── Class instance → x instanceof MyClass
├── Object with a discriminant field → x.kind === "circle"
├── Custom multi-step logic → type predicate: (val: unknown): val is X { ... }
└── Exhaustiveness (all cases must be handled)
    └── function assertNever(x: never): never { throw new Error("Unexpected: " + x) }
```

## Key Concepts

### Structural Typing (Duck Typing)
TypeScript checks **shape compatibility**, not nominal identity. If a value has all required properties with compatible types, it satisfies the type — regardless of its declared class or origin.

```typescript
interface Named { name: string }
function greet(n: Named) { console.log(n.name) }

const user = { name: "Alice", age: 30 }
greet(user) // OK — user has all of Named's properties
```

### Type Inference
TypeScript infers types from usage. Explicit annotations are needed only when inference is wrong, insufficient, or for documentation at API boundaries.

```typescript
let count = 0         // inferred: number
const label = "open"  // inferred: "open" (narrower literal type)
```

### Assignability Rule
Type `S` is assignable to type `T` when:
- `S` is the same type as `T`
- `S` is a structural subtype of `T` (has all of `T`'s required properties, possibly more)
- `T` is `any` or `unknown` (accepts everything)
- `S` is `never` (assignable to everything)
- `S` is a member of a union that includes `T`

### The Narrowing Mental Model
TypeScript maintains a **type at every point in the control flow**. Each check (typeof, instanceof, property access, truthiness) narrows the type inside that branch. After the branch, the type reverts to its prior state (or is the union of all exit paths).
