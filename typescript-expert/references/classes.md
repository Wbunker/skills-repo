# Classes
## Chapter 8: Classes

---

## Class Basics

TypeScript classes build on JavaScript classes with added type annotations and compile-time checks:

```typescript
class User {
  name: string
  age: number

  constructor(name: string, age: number) {
    this.name = name
    this.age = age
  }

  greet(): string {
    return `Hello, ${this.name}`
  }
}

const user = new User("Alice", 30)
```

## Property Declarations

Class properties must be declared in the class body (not just assigned in the constructor) when using TypeScript's class syntax. Under `strictPropertyInitialization`, all declared properties must be initialized in the constructor or with a default value.

```typescript
class Counter {
  count: number = 0    // declared and initialized

  increment(): void {
    this.count++
  }
}
```

### Definite Assignment Assertion

If a property is initialized indirectly (e.g., via a method called from the constructor), use `!` to assert it will be defined:

```typescript
class DataLoader {
  data!: string[]    // I guarantee this will be set before use

  constructor() {
    this.initialize()
  }

  private initialize(): void {
    this.data = []
  }
}
```

Use sparingly — it disables a useful safety check.

## Readonly Properties

Class properties can be `readonly`. They may only be assigned in the declaration or in the constructor:

```typescript
class Config {
  readonly host: string
  readonly port: number

  constructor(host: string, port: number) {
    this.host = host
    this.port = port
  }
}
```

## Member Visibility

TypeScript has three visibility modifiers:

| Modifier | Accessible From |
|----------|----------------|
| `public` (default) | Anywhere |
| `protected` | Class and subclasses |
| `private` | Class only (compile-time) |
| `#name` (JS private) | Class only (runtime enforcement) |

```typescript
class BankAccount {
  public owner: string
  private balance: number
  protected accountNumber: string

  constructor(owner: string, balance: number, accountNumber: string) {
    this.owner = owner
    this.balance = balance
    this.accountNumber = accountNumber
  }

  deposit(amount: number): void {
    this.balance += amount
  }
}
```

### TypeScript `private` vs JavaScript `#`

- `private`: compile-time only — the property is still accessible at runtime via JavaScript (or type assertions)
- `#name`: JavaScript private field — truly inaccessible at runtime (even via `(obj as any)["#name"]`)

Use `#name` when you need actual runtime privacy. Use `private` for compile-time documentation and checking.

## Parameter Properties (Shorthand)

TypeScript allows declaring and initializing properties directly in the constructor parameters:

```typescript
class User {
  constructor(
    public readonly name: string,
    private age: number
  ) {}
  // Equivalent to:
  // public readonly name: string
  // private age: number
  // this.name = name; this.age = age
}
```

## Implementing Interfaces

A class can `implement` one or more interfaces, guaranteeing it satisfies those shapes:

```typescript
interface Serializable {
  serialize(): string
}

interface Loggable {
  log(): void
}

class Event implements Serializable, Loggable {
  constructor(public readonly name: string) {}

  serialize(): string { return JSON.stringify({ name: this.name }) }
  log(): void { console.log(this.name) }
}
```

`implements` is a compile-time check only — it doesn't add any runtime behavior.

## Extending Classes

```typescript
class Animal {
  constructor(public name: string) {}
  speak(): string { return `${this.name} makes a noise.` }
}

class Dog extends Animal {
  constructor(name: string, public breed: string) {
    super(name)    // must call super() before accessing this
  }

  override speak(): string {    // 'override' keyword ensures parent has this method
    return `${this.name} barks.`
  }
}
```

### override Keyword

The `override` keyword (requires `noImplicitOverride: true` in tsconfig) ensures:
- The method exists in the parent class
- You get an error if you accidentally override a method that doesn't exist in the base

## Abstract Classes

An `abstract` class cannot be instantiated directly. It provides a partial implementation and declares abstract methods that subclasses must implement:

```typescript
abstract class Shape {
  abstract area(): number     // subclasses must implement this

  toString(): string {
    return `Area: ${this.area()}`   // can use abstract methods here
  }
}

class Circle extends Shape {
  constructor(public radius: number) { super() }
  area(): number { return Math.PI * this.radius ** 2 }
}

const shape = new Shape()   // Error: Cannot create an instance of an abstract class
const circle = new Circle(5)  // OK
```

## Classes as Types

A class name serves as a type representing an *instance* of the class:

```typescript
class User { name: string = "" }

function greet(user: User): string { return user.name }  // User is used as a type
```

To type a **constructor** (the class itself, not an instance), use `typeof ClassName` or a construct signature:

```typescript
function createInstance<T>(Ctor: new () => T): T {
  return new Ctor()
}
```

## Static Members

Static properties and methods belong to the class itself, not instances:

```typescript
class IdGenerator {
  private static nextId = 1

  static generate(): number {
    return IdGenerator.nextId++
  }
}

const id1 = IdGenerator.generate()   // 1
const id2 = IdGenerator.generate()   // 2
```

## Classes and Structural Typing

TypeScript uses structural typing for classes. Two classes with the same shape are interchangeable, even if unrelated:

```typescript
class Cat { meow(): void {} }
class Dog { meow(): void {} }

const animal: Cat = new Dog()   // OK — structural match
```

Private and protected members *are* considered in structural checks: two classes with the same private property names but from different class declarations are *not* compatible.
