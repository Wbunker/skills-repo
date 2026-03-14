# Instance Initialization and Method Resolution

Reference for initialization order, early definitions, linearization, method resolution, and super calls.

## Table of Contents
- [Initialization Order](#initialization-order)
- [Linearization](#linearization)
- [Method Resolution](#method-resolution)
- [Super Calls](#super-calls)

## Initialization Order

### Constructor Execution Order
```scala
class Animal(val name: String):
  println(s"Animal($name)")

trait Furry:
  println("Furry")

trait HasLegs:
  println("HasLegs")

class Cat(name: String) extends Animal(name), Furry, HasLegs:
  println(s"Cat($name)")

Cat("Tom")
// Output:
// Animal(Tom)      — superclass first
// Furry            — traits left to right
// HasLegs
// Cat(Tom)         — class body last
```

### Val Initialization Trap
```scala
trait Greet:
  val name: String
  val greeting = s"Hello, $name"  // DANGER: name is null during trait init!

class Person extends Greet:
  val name = "Alice"

Person().greeting  // "Hello, null" — name not yet initialized!

// Solutions:
// 1. Use lazy val
trait Greet:
  val name: String
  lazy val greeting = s"Hello, $name"  // computed on first access

// 2. Use def
trait Greet:
  def name: String
  def greeting = s"Hello, $name"  // computed each time

// 3. Early definitions (Scala 2 only, removed in Scala 3)
// Use lazy val or def in Scala 3 instead
```

### Lazy Val Thread Safety
```scala
// lazy val is thread-safe (uses double-checked locking)
// But beware of deadlocks with circular lazy vals
class A:
  lazy val x: Int = B.y + 1

class B:
  lazy val y: Int = A.x + 1  // DEADLOCK if accessed from different threads
```

## Linearization

### How Linearization Works
```scala
// Linearization determines the order of initialization and method resolution
// Algorithm: depth-first, right-to-left, remove duplicates (keep last)

trait A:
  def method: String = "A"
trait B extends A:
  override def method: String = "B"
trait C extends A:
  override def method: String = "C"
class D extends B, C

// Linearization of D:
// Start: D
// Add C's linearization: C → A
// Add B's linearization: B → A (A already seen, remove)
// Result: D → C → B → A
// Method call D().method → "C" (first in chain after D)
```

### Linearization Examples
```scala
trait Base { def method: String = "Base" }
trait T1 extends Base { override def method: String = s"T1(${super.method})" }
trait T2 extends Base { override def method: String = s"T2(${super.method})" }
trait T3 extends Base { override def method: String = s"T3(${super.method})" }

class C extends T1, T2, T3
C().method  // "T3(T2(T1(Base)))"
// Linearization: C → T3 → T2 → T1 → Base
// super.method in T3 → T2.method
// super.method in T2 → T1.method
// super.method in T1 → Base.method
```

### Viewing Linearization
```scala
// At runtime, check with getClass
val c = C()
// Use reflection or debug output to see linearization

// Compile with -Xprint:mixin to see compiler's linearization
```

## Method Resolution

### Override Rules
```scala
// override keyword required when overriding concrete methods
trait Animal:
  def speak: String = "..."

class Dog extends Animal:
  override def speak: String = "Woof"  // override required

// abstract override: override an abstract method with a call to super
trait Logged extends Animal:
  abstract override def speak: String =
    println(s"Speaking: ${super.speak}")
    super.speak

class LoggedDog extends Dog, Logged
LoggedDog().speak
// prints "Speaking: Woof"
// returns "Woof"
```

### Diamond Problem Resolution
```scala
trait A:
  def greet: String = "A"

trait B extends A:
  override def greet: String = "B"

trait C extends A:
  override def greet: String = "C"

// Diamond: D extends B and C, both extend A
class D extends B, C
D().greet  // "C" — rightmost trait wins (linearization: D → C → B → A)

// If you need to call a specific parent's method:
class D extends B, C:
  override def greet: String = super[B].greet  // explicitly "B"
```

## Super Calls

### super Keyword
```scala
// super refers to the next type in the linearization chain
class D extends B, C:
  override def method: String = super.method
  // super → C (next in linearization after D)
```

### Qualified super
```scala
// super[TraitName] — call a specific parent trait's method
trait A:
  def method: String = "A"

trait B extends A:
  override def method: String = "B"

trait C extends A:
  override def method: String = "C"

class D extends B, C:
  def fromB: String = super[B].method  // "B"
  def fromC: String = super[C].method  // "C"
  override def method: String = s"D(${super[B].method},${super[C].method})"
```

### super in Stackable Traits
```scala
// super follows the linearization chain, enabling stackable behavior
trait IntTransform:
  def transform(x: Int): Int = x

trait Double extends IntTransform:
  override def transform(x: Int): Int = super.transform(x * 2)

trait AddOne extends IntTransform:
  override def transform(x: Int): Int = super.transform(x + 1)

// Order matters:
(new IntTransform with Double with AddOne {}).transform(3)
// AddOne: super.transform(3 + 1) = super.transform(4)
// Double: super.transform(4 * 2) = super.transform(8)
// IntTransform: 8
// Result: 8

(new IntTransform with AddOne with Double {}).transform(3)
// Double: super.transform(3 * 2) = super.transform(6)
// AddOne: super.transform(6 + 1) = super.transform(7)
// IntTransform: 7
// Result: 7
```
