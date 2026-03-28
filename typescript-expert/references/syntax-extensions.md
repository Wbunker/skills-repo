# Syntax Extensions
## Chapter 14: Syntax Extensions

TypeScript adds a small set of syntax constructs beyond standard JavaScript. These compile away to JavaScript but provide additional expressiveness or performance at compile time.

---

## Decorators

Decorators are a **stage 3 TC39 proposal** (and a TypeScript experimental feature) that add annotations and meta-programming to class declarations and members.

### Enabling Decorators

```json
// tsconfig.json
{
  "compilerOptions": {
    "experimentalDecorators": true,   // legacy TypeScript decorators
    "emitDecoratorMetadata": true     // emit reflect-metadata (for DI frameworks)
  }
}
```

TypeScript 5.0+ supports the TC39 stage 3 decorator proposal natively (no flag needed). The two systems are incompatible; check which your framework uses.

### Class Decorator

Applied to the class constructor:

```typescript
function sealed(constructor: Function): void {
  Object.seal(constructor)
  Object.seal(constructor.prototype)
}

@sealed
class BugReport {
  type = "report"
  title: string
  constructor(t: string) { this.title = t }
}
```

### Method Decorator

Applied to a class method:

```typescript
function log(target: any, key: string, descriptor: PropertyDescriptor) {
  const original = descriptor.value
  descriptor.value = function (...args: any[]) {
    console.log(`Calling ${key} with`, args)
    return original.apply(this, args)
  }
  return descriptor
}

class Calc {
  @log
  add(a: number, b: number): number { return a + b }
}
```

### Property and Parameter Decorators

Also available for class properties and constructor/method parameters. Used heavily by frameworks like Angular, NestJS, and TypeORM for dependency injection and ORM mapping.

### When Decorators Are Used

- **NestJS**: `@Controller()`, `@Get()`, `@Injectable()`, `@Body()`
- **Angular**: `@Component()`, `@Injectable()`, `@Input()`, `@Output()`
- **TypeORM**: `@Entity()`, `@Column()`, `@PrimaryGeneratedColumn()`
- **class-validator**: `@IsEmail()`, `@IsNotEmpty()`, `@Min()`

---

## Enums

TypeScript enums define a set of named constants. They are one of the few TypeScript constructs that produce runtime JavaScript output.

### Numeric Enums (default)

```typescript
enum Direction {
  North,   // 0
  South,   // 1
  East,    // 2
  West,    // 3
}

const dir: Direction = Direction.North
console.log(dir)         // 0
console.log(Direction[0]) // "North" (reverse mapping)
```

Values auto-increment from 0, or from a specified start:

```typescript
enum Status {
  Pending = 1,
  Active,    // 2
  Closed,    // 3
}
```

### String Enums

```typescript
enum Color {
  Red   = "RED",
  Green = "GREEN",
  Blue  = "BLUE",
}

const c: Color = Color.Red
console.log(c)   // "RED"
```

String enums are **more debuggable** (values are human-readable) and do not produce reverse mappings.

### Const Enums

`const enum` is fully erased at compile time — each usage is replaced inline with the literal value. No runtime object is created.

```typescript
const enum Direction {
  North = "N",
  South = "S",
}

const d = Direction.North   // compiled to: const d = "N"
```

**Caveats**:
- Cannot be used with `--isolatedModules` (used by Babel, esbuild, etc.)
- Cannot be imported across module boundaries without declaration files
- Prefer string union types or regular enums if using a non-tsc transpiler

### Enum vs. Union of String Literals

For most cases, **a union of string literals is simpler** than an enum:

```typescript
// Enum
enum Direction { North = "N", South = "S", East = "E", West = "W" }

// Union type (preferred for most use cases)
type Direction = "N" | "S" | "E" | "W"
```

Use enums when:
- You want a runtime object with named members
- You need to iterate over members at runtime
- You are matching the idiom of a framework that uses enums

Use string literal unions when:
- You only need compile-time type safety
- You want to avoid the runtime overhead and complexity of enums
- You are using a non-tsc transpiler (Babel, esbuild, swc)

---

## Namespaces (Legacy)

Namespaces are TypeScript's pre-module way to organize code. They predate the ECMAScript module system and are largely **legacy** in modern TypeScript.

```typescript
namespace Validation {
  export interface StringValidator {
    isAcceptable(s: string): boolean
  }

  export class LettersOnlyValidator implements StringValidator {
    isAcceptable(s: string): boolean {
      return /^[A-Za-z]+$/.test(s)
    }
  }
}

const v = new Validation.LettersOnlyValidator()
```

### When Namespaces Are Still Used

- Augmenting global library types (e.g., extending `jQuery.fn`)
- Declaration files for scripts (not modules) that pollute the global scope
- Organizing declaration files for very large global APIs

**Modern replacement**: Use ES modules (`import`/`export`) for code organization. Use `declare module` for module augmentation. Avoid namespaces in new code.

---

## Class Field Declarations

TypeScript supports the TC39 class fields proposal, which gives class properties block-scoped semantics and private-by-default with `#`:

```typescript
class Counter {
  count = 0           // public field
  #secret = "hidden"  // private field (runtime enforcement)

  increment(): void {
    this.count++
    console.log(this.#secret)  // accessible inside class only
  }
}
```

### Class Fields vs TypeScript's Property Declarations

| Feature | TypeScript `private` | JavaScript `#private` |
|---------|---------------------|----------------------|
| Compile-time only | Yes | No |
| Runtime enforcement | No | Yes |
| Inherited class access | No | No |
| Structurally compatible | Yes (across class bodies) | No |

Use `#private` when you need true runtime privacy. Use TypeScript `private` for compile-time documentation.

### Accessor (get/set)

TypeScript fully supports JavaScript getters and setters with type annotations:

```typescript
class Temperature {
  private _celsius: number = 0

  get fahrenheit(): number {
    return this._celsius * 9/5 + 32
  }

  set fahrenheit(value: number) {
    this._celsius = (value - 32) * 5/9
  }
}
```
