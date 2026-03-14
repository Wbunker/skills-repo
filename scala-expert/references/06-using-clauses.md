# Using Clauses

Reference for context parameters, implicit conversions, context bounds, given imports, and type class derivation.

## Table of Contents
- [Using Clauses (Context Parameters)](#using-clauses-context-parameters)
- [Context Bounds](#context-bounds)
- [Implicit Conversions](#implicit-conversions)
- [Given Imports and Scope](#given-imports-and-scope)
- [Type Class Derivation](#type-class-derivation)
- [Migration from Scala 2 Implicits](#migration-from-scala-2-implicits)

## Using Clauses (Context Parameters)

### Basic Using Clauses
```scala
// `using` parameters are filled in automatically from scope
def sorted[A](xs: List[A])(using ord: Ordering[A]): List[A] =
  xs.sorted(using ord)

// Given instance in scope
given Ordering[Int] = Ordering.Int

sorted(List(3, 1, 2))  // List(1, 2, 3) — ord filled in automatically
sorted(List(3, 1, 2))(using Ordering.Int.reverse)  // explicit override

// Anonymous using parameter
def max[A](a: A, b: A)(using Ordering[A]): A =
  if summon[Ordering[A]].compare(a, b) >= 0 then a else b
```

### Multiple Using Clauses
```scala
def process[A](xs: List[A])(using ord: Ordering[A], show: Show[A]): String =
  xs.sorted.map(_.show).mkString(", ")

// Using clause lists can be separate
def f[A](x: A)(using Ordering[A])(using Show[A]): String = ???
```

### Passing Context Through
```scala
// Context parameters are automatically passed to inner calls
def outerSort[A](xs: List[A])(using Ordering[A]): List[A] =
  innerSort(xs)  // Ordering[A] automatically passed

def innerSort[A](xs: List[A])(using Ordering[A]): List[A] =
  xs.sorted
```

## Context Bounds

### Syntactic Sugar
```scala
// Context bound is shorthand for using clause
def sorted[A: Ordering](xs: List[A]): List[A] =
  xs.sorted

// Equivalent to:
def sorted[A](xs: List[A])(using Ordering[A]): List[A] =
  xs.sorted

// Multiple context bounds
def process[A: Ordering: Show](xs: List[A]): String =
  xs.sorted.map(_.show).mkString(", ")

// Equivalent to:
def process[A](xs: List[A])(using Ordering[A], Show[A]): String =
  xs.sorted.map(_.show).mkString(", ")

// Access the instance with summon
def max[A: Ordering](a: A, b: A): A =
  if summon[Ordering[A]].compare(a, b) >= 0 then a else b
```

## Implicit Conversions

### Scala 3 Conversions
```scala
// Scala 3: explicit Conversion type class
given Conversion[Int, Double] = _.toDouble
given Conversion[String, Int] = _.toInt

// Must import scala.language.implicitConversions
import scala.language.implicitConversions

val d: Double = 42     // Int auto-converted to Double
val i: Int = "42"      // String auto-converted to Int

// Custom conversion
case class Meters(value: Double)
case class Feet(value: Double)

given Conversion[Feet, Meters] = f => Meters(f.value * 0.3048)

def run(distance: Meters): Unit = println(s"${distance.value}m")
run(Feet(100))  // auto-converted to Meters(30.48)
```

### When Conversions Are Applied
```
1. Expression type doesn't match expected type
2. Member selection: x.method where x has no 'method'
   → compiler looks for conversion to a type that has 'method'
3. Argument type doesn't match parameter type
```

### Best Practices
```scala
// AVOID implicit conversions in most cases
// They make code harder to understand and debug

// PREFER:
// - Extension methods (add functionality)
// - Explicit conversion methods
// - Type classes

// ACCEPTABLE uses:
// - DSLs (domain-specific languages)
// - Interop wrappers (Java ↔ Scala)
// - Well-known numeric promotions
```

## Given Imports and Scope

### Where Givens Are Found
```scala
// 1. Current scope
given Ordering[Int] = Ordering.Int

// 2. Imported scope
import mypackage.given

// 3. Companion objects of involved types
// (This is the most important for type classes!)
case class Person(name: String)
object Person:
  given Ordering[Person] = Ordering.by(_.name)
  // Automatically found when Ordering[Person] is needed

// 4. Companion objects of type arguments
trait JsonEncoder[A]:
  def encode(a: A): String
object JsonEncoder:
  given JsonEncoder[Int] with
    def encode(i: Int): String = i.toString
  // Found when JsonEncoder[Int] is needed
```

### Import Specificity
```scala
import mypackage.given              // all givens from mypackage
import mypackage.{given Ordering[?]} // only Ordering givens
import mypackage.{given Show[?]}    // only Show givens
import mypackage.{myOrdering}       // import by name

// Wildcard import does NOT include givens
import mypackage.*  // no givens!

// Import both
import mypackage.{given, *}
```

### Ambiguity Resolution
```scala
// If multiple givens match, the compiler uses specificity rules:
// 1. More specific type wins (List[Int] beats List[?])
// 2. Non-parameterized beats parameterized
// 3. In same scope: error (ambiguous)
// 4. Inner scope shadows outer scope

// Resolve ambiguity by importing or defining a more specific given
given defaultOrd: Ordering[Person] = Ordering.by(_.name)
given ageOrd: Ordering[Person] = Ordering.by(_.age)
// ERROR: ambiguous

// Fix: use one explicitly
people.sorted(using ageOrd)
```

## Type Class Derivation

### derives Clause
```scala
// Scala 3 can automatically derive type class instances
case class Point(x: Double, y: Double) derives CanEqual

// For custom type classes, define a derived method in companion
trait JsonCodec[A]:
  def encode(a: A): String
  def decode(s: String): A

object JsonCodec:
  // inline given derived uses Mirrors for compile-time derivation
  inline given derived[A](using m: scala.deriving.Mirror.Of[A]): JsonCodec[A] =
    ??? // implementation using Mirror

// Then:
case class Person(name: String, age: Int) derives JsonCodec
```

### Mirror-Based Derivation
```scala
import scala.deriving.Mirror

// Mirror provides compile-time information about types
// Mirror.ProductOf[A] — case classes, tuples
// Mirror.SumOf[A]     — enums, sealed traits

inline def nameOf[A](using m: Mirror.Of[A]): String =
  constValue[m.MirroredLabel]

nameOf[Person]  // "Person" (at compile time)
```

## Migration from Scala 2 Implicits

### Mapping Table
| Scala 2 | Scala 3 |
|---------|---------|
| `implicit val` | `given` |
| `implicit def` (conversion) | `given Conversion[A, B]` |
| `implicit def` (derivation) | `given ... with` |
| `implicit class` | `extension` methods |
| `implicitly[T]` | `summon[T]` |
| `implicit parameter` | `using` clause |
| `(implicit x: T)` | `(using x: T)` |

### Examples
```scala
// Scala 2:
implicit val ord: Ordering[Person] = Ordering.by(_.name)
def sorted[A](xs: List[A])(implicit ord: Ordering[A]): List[A] = xs.sorted
implicit class RichString(s: String) { def words: List[String] = s.split(" ").toList }

// Scala 3:
given ord: Ordering[Person] = Ordering.by(_.name)
def sorted[A](xs: List[A])(using ord: Ordering[A]): List[A] = xs.sorted
extension (s: String) def words: List[String] = s.split(" ").toList
```
