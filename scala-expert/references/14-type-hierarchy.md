# The Scala Type Hierarchy

Reference for Any, AnyVal, AnyRef, Nothing, Null, value classes, and union/intersection types.

## Table of Contents
- [Type Hierarchy](#type-hierarchy)
- [Any, AnyVal, AnyRef](#any-anyval-anyref)
- [Nothing and Null](#nothing-and-null)
- [Value Types and Value Classes](#value-types-and-value-classes)
- [Union Types](#union-types)
- [Intersection Types](#intersection-types)
- [Type Aliases](#type-aliases)

## Type Hierarchy

### The Complete Hierarchy
```
                    Any
                   /   \
              AnyVal   AnyRef (= java.lang.Object)
             /  |  \      |    \
          Int Double Boolean  String  List  YourClass
           |    |     |        |       |       |
         (value types)     (reference types)
                               |
                             Null (subtype of all AnyRef)
                               \
                              Nothing (subtype of everything)
```

## Any, AnyVal, AnyRef

### Any — The Top Type
```scala
// Every type extends Any
val x: Any = 42
val y: Any = "hello"
val z: Any = List(1, 2)

// Any methods (available on all types):
x.toString     // "42"
x.hashCode     // hash value
x.equals(42)   // true
x.##           // null-safe hashCode
x.isInstanceOf[Int]  // true
x.asInstanceOf[Int]  // 42 (unsafe cast)
```

### AnyVal — Value Types
```scala
// AnyVal is the parent of all value types
// These map to JVM primitives (no heap allocation):
// Int, Long, Float, Double, Boolean, Byte, Short, Char, Unit

val i: AnyVal = 42       // boxed when stored as AnyVal
val b: AnyVal = true
val u: AnyVal = ()        // Unit

// Unit — like void, but is an actual value
def sideEffect(): Unit = println("effect")
val result: Unit = ()     // the only Unit value
```

### AnyRef — Reference Types
```scala
// AnyRef = java.lang.Object
// All non-value types extend AnyRef
val s: AnyRef = "hello"
val l: AnyRef = List(1)
val p: AnyRef = Person("Alice")

// AnyRef methods:
s eq s        // true (reference equality)
s ne "other"  // true (reference inequality)
s.synchronized { /* critical section */ }
```

## Nothing and Null

### Nothing — The Bottom Type
```scala
// Nothing is a subtype of every type
// No instances of Nothing exist
// Used for:

// 1. Expressions that never return
def fail(msg: String): Nothing = throw RuntimeException(msg)

// 2. Empty collections
val empty: List[Int] = Nil  // Nil: List[Nothing], subtype of List[Int]

// 3. Covariant type parameter in "empty" case
enum Option[+A]:
  case Some(value: A)
  case None  // None: Option[Nothing], subtype of Option[A] for any A

// 4. Type inference for impossible branches
val x: Int = if true then 42 else throw Exception()
// throw returns Nothing, which is subtype of Int
```

### Null
```scala
// Null is a subtype of all AnyRef types
// null is the only instance of Null
val s: String = null  // compiles (but avoid!)

// Scala 3 explicit nulls (experimental)
// With -Yexplicit-nulls, null is NOT assignable to reference types
// val s: String = null  // ERROR
// val s: String | Null = null  // OK

// Best practice: use Option instead of null
val name: Option[String] = None  // instead of null
```

## Value Types and Value Classes

### Value Classes (Scala 2 / limited in 3)
```scala
// Wrapper that avoids heap allocation in many cases
class Meters(val value: Double) extends AnyVal:
  def +(other: Meters): Meters = Meters(value + other.value)
  def *(factor: Double): Meters = Meters(value * factor)

// At runtime, Meters(5.0) is just the Double 5.0 (no wrapper)
// Allocation happens when:
// - Assigned to Any or AnyVal
// - Used as array element
// - Pattern matched
```

### Opaque Types (Scala 3 — Preferred)
```scala
// Zero-cost always (never allocates)
object Units:
  opaque type Meters = Double
  object Meters:
    def apply(d: Double): Meters = d
    extension (m: Meters)
      def +(other: Meters): Meters = m + other
      def value: Double = m
```

## Union Types

### Union Types (Scala 3)
```scala
// A | B — value can be A or B
type StringOrInt = String | Int

def show(x: StringOrInt): String = x match
  case s: String => s"String: $s"
  case i: Int    => s"Int: $i"

show("hello")  // "String: hello"
show(42)       // "Int: 42"

// Common use: error handling
type Result = Success | Failure
def parse(s: String): Int | String =
  try s.toInt
  catch case _: Exception => s"Cannot parse: $s"

// Union of multiple types
type Primitive = Int | Long | Float | Double | Boolean | Char
```

### Union vs Either
```scala
// Union type: compile-time only, no wrapper at runtime
val x: Int | String = 42  // no boxing

// Either: runtime wrapper, methods (map, flatMap)
val y: Either[String, Int] = Right(42)  // Either object allocated

// Use union types for:
//   - Simple "this or that" without operations
//   - Avoiding wrapper allocation
// Use Either for:
//   - Monadic composition (for comprehensions)
//   - Error handling with map/flatMap
```

## Intersection Types

### Intersection Types (Scala 3)
```scala
// A & B — value has both A and B
trait Printable:
  def print(): Unit

trait Serializable:
  def serialize(): Array[Byte]

def process(x: Printable & Serializable): Unit =
  x.print()
  val bytes = x.serialize()

// Intersection types for parameter requirements
trait HasName { def name: String }
trait HasAge { def age: Int }

def greet(person: HasName & HasAge): String =
  s"Hello ${person.name}, age ${person.age}"
```

### Intersection vs with (Scala 2)
```scala
// Scala 2: A with B (compound type)
// Scala 3: A & B (intersection type)
// They are similar but & is commutative: A & B == B & A
```

## Type Aliases

### Simple Aliases
```scala
// type creates an alias (not a new type)
type UserName = String
type UserId = Int
type UserMap = Map[UserId, UserName]

val users: UserMap = Map(1 -> "Alice", 2 -> "Bob")

// Parameterized alias
type Result[A] = Either[String, A]
type Callback[A] = A => Unit
```

### Opaque Type Aliases
```scala
// For truly distinct types, use opaque
object Domain:
  opaque type UserId = Long
  opaque type OrderId = Long
  // UserId and OrderId are different types (cannot be mixed up)
  // But at runtime, both are just Long (zero cost)
```
