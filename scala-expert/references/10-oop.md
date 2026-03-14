# Object-Oriented Programming in Scala

Reference for classes, objects, companions, constructors, case classes, apply/unapply, and OOP patterns.

## Table of Contents
- [Classes](#classes)
- [Objects and Companions](#objects-and-companions)
- [Constructors](#constructors)
- [Case Classes and Objects](#case-classes-and-objects)
- [Apply and Unapply](#apply-and-unapply)
- [Abstract Classes](#abstract-classes)

## Classes

### Basic Class Definition
```scala
// Scala 3 indentation syntax
class Person(val name: String, var age: Int):
  def greet(): String = s"Hello, I'm $name"
  override def toString: String = s"Person($name, $age)"

val p = Person("Alice", 30)
p.name   // "Alice" (accessible — val)
p.age    // 30 (accessible and mutable — var)
p.age = 31
```

### Access Modifiers on Parameters
```scala
class Example(
  val public: Int,       // public getter
  var mutable: Int,      // public getter + setter
  private val priv: Int, // private
  internal: Int          // private (no val/var = constructor-only, unless used in body)
):
  def sum: Int = public + mutable + priv + internal
```

### Fields and Methods
```scala
class Counter:
  private var count = 0

  def increment(): Unit = count += 1
  def decrement(): Unit = count -= 1
  def current: Int = count  // parentheses-less = property access style

val c = Counter()
c.increment()
c.current  // 1 (no parens — property style)
```

### Open vs Closed Classes (Scala 3)
```scala
// By default, classes can be extended
// Use `final` to prevent extension
final class Singleton  // cannot be extended

// Use `open` to explicitly mark as extensible (with -source:future)
open class Base:
  def method: String = "base"

class Derived extends Base:
  override def method: String = "derived"

// sealed: can only be extended in same file
sealed class Shape
```

## Objects and Companions

### Singleton Objects
```scala
// `object` creates a singleton (one instance)
object Logger:
  private var level = "INFO"
  def info(msg: String): Unit = println(s"[$level] $msg")
  def setLevel(l: String): Unit = level = l

Logger.info("Starting")  // no need to create instance

// Object as entry point
object Main:
  def main(args: Array[String]): Unit =
    println("Hello!")

// Or with @main annotation (Scala 3)
@main def run(): Unit = println("Hello!")
```

### Companion Objects
```scala
// A class and object with the same name in the same file
class Circle private (val radius: Double):
  def area: Double = Circle.Pi * radius * radius

object Circle:
  private val Pi = 3.14159
  def apply(radius: Double): Circle =
    require(radius > 0, "Radius must be positive")
    new Circle(radius)

val c = Circle(5.0)  // calls Circle.apply — no `new` needed
c.area
```

### Companion Object Patterns
```scala
// Factory methods
object User:
  def fromEmail(email: String): User = ???
  def anonymous: User = User("anonymous", 0)

// Implicit/given instances
class Money(val amount: BigDecimal)
object Money:
  given Ordering[Money] = Ordering.by(_.amount)
  // Automatically found for Ordering[Money]

// Extractors
object Money:
  def unapply(m: Money): Option[BigDecimal] = Some(m.amount)
```

## Constructors

### Primary Constructor
```scala
// Parameters in class definition ARE the primary constructor
class Person(val name: String, val age: Int)
// Compiled to: constructor + fields + getters
```

### Auxiliary Constructors
```scala
class Person(val name: String, val age: Int):
  // Auxiliary constructors must call primary constructor
  def this(name: String) = this(name, 0)
  def this() = this("Unknown", 0)

// Better approach: use default parameters
class Person(val name: String = "Unknown", val age: Int = 0)

// Or factory methods in companion
object Person:
  def apply(name: String): Person = Person(name, 0)
  def unknown: Person = Person("Unknown", 0)
```

### Constructor Parameters and val/var
```scala
class A(x: Int)           // x is private, only in scope if used in methods
class B(val x: Int)       // x has a public getter
class C(var x: Int)       // x has public getter and setter
class D(private val x: Int)  // x has private getter
```

## Case Classes and Objects

### Case Class Features
```scala
case class Point(x: Double, y: Double)

// Auto-generated:
// 1. apply: Point(1.0, 2.0) — no `new`
// 2. unapply: pattern matching
// 3. copy: p.copy(x = 3.0)
// 4. equals/hashCode: structural equality
// 5. toString: "Point(1.0,2.0)"
// 6. Serializable
// 7. Product methods: productArity, productElement

val p1 = Point(1.0, 2.0)
val p2 = Point(1.0, 2.0)
p1 == p2       // true (structural equality)
p1.toString    // "Point(1.0,2.0)"
p1.copy(x = 3) // Point(3.0, 2.0)

// Pattern matching
p1 match
  case Point(x, y) => s"($x, $y)"

// Case class parameters are val by default (immutable)
// p1.x = 5  // ERROR: val cannot be reassigned
```

### Case Objects
```scala
// Singleton with case class features
case object Nothing extends Option[Nothing]

// Useful for enumeration values and sentinels
sealed trait Command
case class Move(x: Int, y: Int) extends Command
case object Stop extends Command
case object Reset extends Command
```

### Copy Method
```scala
case class Config(host: String, port: Int, ssl: Boolean)

val dev = Config("localhost", 8080, false)
val prod = dev.copy(host = "prod.example.com", ssl = true)
// Config("prod.example.com", 8080, true)

// Useful for "immutable update" pattern
case class State(count: Int, items: List[String]):
  def addItem(item: String): State =
    copy(count = count + 1, items = item :: items)
```

## Apply and Unapply

### Apply Method
```scala
// apply makes an object callable like a function
class Multiplier(factor: Int):
  def apply(x: Int): Int = x * factor

val double = Multiplier(2)
double(5)     // calls double.apply(5) → 10
double.apply(5)  // same thing, explicit

// Common pattern: companion apply as factory
object Temperature:
  def apply(celsius: Double): Temperature = new Temperature(celsius)
  def fromFahrenheit(f: Double): Temperature = Temperature((f - 32) * 5 / 9)
```

### Unapply Method
```scala
// unapply enables pattern matching (extraction)
object Email:
  def unapply(s: String): Option[(String, String)] =
    val parts = s.split("@")
    if parts.length == 2 then Some((parts(0), parts(1)))
    else None

"alice@example.com" match
  case Email(user, domain) => s"$user at $domain"  // uses unapply
  case _                   => "not an email"
```

## Abstract Classes

### Abstract vs Trait
```scala
// Abstract class: can have constructor parameters, single inheritance
abstract class Animal(val name: String):
  def speak: String  // abstract method
  def info: String = s"$name says ${speak}"  // concrete method

class Dog(name: String) extends Animal(name):
  def speak: String = "Woof!"

// When to use abstract class vs trait:
// Abstract class:
//   - Has constructor parameters (though Scala 3 traits can too)
//   - Interop with Java (Java doesn't have traits)
//   - Performance-critical (slightly faster dispatch)
// Trait:
//   - Mixin composition (a class can extend multiple traits)
//   - Interface-like behavior
//   - Default choice in Scala
```
