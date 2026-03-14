# Type Classes and Extension Methods

Reference for type classes, extension methods, given instances, exports, and opaque types in Scala 3.

## Table of Contents
- [Type Classes](#type-classes)
- [Extension Methods](#extension-methods)
- [Given Instances](#given-instances)
- [Opaque Types](#opaque-types)
- [Exports](#exports)

## Type Classes

### What Type Classes Are
```scala
// A type class defines behavior that can be added to types retroactively
// Three components:
// 1. Trait (the type class)
// 2. Given instances (implementations for specific types)
// 3. Using clauses (require an instance)

// 1. Define the type class
trait Show[A]:
  extension (a: A) def show: String

// 2. Provide instances
given Show[Int] with
  extension (i: Int) def show: String = i.toString

given Show[String] with
  extension (s: String) def show: String = s"\"$s\""

given [A](using sa: Show[A]): Show[List[A]] with
  extension (xs: List[A]) def show: String =
    xs.map(_.show).mkString("[", ", ", "]")

// 3. Use the type class
def printAll[A](xs: List[A])(using Show[A]): Unit =
  xs.foreach(x => println(x.show))

printAll(List(1, 2, 3))          // prints 1, 2, 3
printAll(List("a", "b"))         // prints "a", "b"
```

### Standard Type Classes
```scala
// Ordering
given Ordering[Person] with
  def compare(a: Person, b: Person): Int =
    a.name.compareTo(b.name)

List(Person("Bob"), Person("Alice")).sorted
// List(Person("Alice"), Person("Bob"))

// Numeric
def sum[A](xs: List[A])(using num: Numeric[A]): A =
  xs.foldLeft(num.zero)(num.plus)

// Equiv (equality)
given Equiv[Person] with
  def equiv(a: Person, b: Person): Boolean = a.name == b.name
```

### Deriving Type Classes
```scala
// Automatic derivation (Scala 3)
case class Point(x: Double, y: Double) derives CanEqual

// For custom type classes, implement a given Mirror
// or use libraries like Magnolia/Shapeless for automatic derivation
```

## Extension Methods

### Basic Extension Methods
```scala
// Add methods to existing types
extension (s: String)
  def words: List[String] = s.split("\\s+").toList
  def isBlank: Boolean = s.trim.isEmpty

"hello world".words  // List("hello", "world")
"  ".isBlank         // true

// Extension with type parameter
extension [A](xs: List[A])
  def second: Option[A] = xs.drop(1).headOption
  def penultimate: Option[A] = xs.dropRight(1).lastOption

List(1, 2, 3).second       // Some(2)
List(1, 2, 3).penultimate  // Some(2)
```

### Extension Methods with Using Clauses
```scala
extension [A](xs: List[A])
  def sortedBy[B](f: A => B)(using ord: Ordering[B]): List[A] =
    xs.sortBy(f)

case class Person(name: String, age: Int)
List(Person("Bob", 30), Person("Alice", 25)).sortedBy(_.name)
```

### Generic Extensions
```scala
extension [A](a: A)
  def |>[B](f: A => B): B = f(a)  // pipe operator
  def tap(f: A => Unit): A = { f(a); a }  // side-effect and return

42 |> (_ * 2) |> (_.toString)  // "84"

List(1, 2, 3)
  .tap(xs => println(s"Before: $xs"))
  .map(_ * 2)
  .tap(xs => println(s"After: $xs"))
```

### Replacing Implicit Classes (Migration)
```scala
// Scala 2 implicit class:
implicit class RichInt(val n: Int) extends AnyVal {
  def isEven: Boolean = n % 2 == 0
}

// Scala 3 extension method:
extension (n: Int)
  def isEven: Boolean = n % 2 == 0
```

## Given Instances

### Defining Given Instances
```scala
// Named given
given intOrdering: Ordering[Int] = Ordering.Int

// Anonymous given
given Ordering[String] = Ordering.String

// Given with body
given personOrdering: Ordering[Person] with
  def compare(a: Person, b: Person): Int =
    a.name.compare(b.name)

// Conditional given (depends on other givens)
given [A](using ord: Ordering[A]): Ordering[List[A]] with
  def compare(a: List[A], b: List[A]): Int =
    a.zip(b).map((x, y) => ord.compare(x, y))
      .find(_ != 0).getOrElse(a.length - b.length)

// Given alias (re-export from another scope)
given Ordering[Int] = summon[Ordering[Int]].reverse
```

### Importing Givens
```scala
// Regular import does NOT import givens
import mypackage.*

// Explicitly import givens
import mypackage.given              // all givens
import mypackage.{given Ordering[?]} // specific type
import mypackage.{myGiven}          // by name

// Import everything including givens
import mypackage.{given, *}
```

### summon
```scala
// summon retrieves a given instance (replaces implicitly)
val ord = summon[Ordering[Int]]  // get the Ordering[Int] in scope

// Useful for debugging: what instance is being used?
println(summon[Ordering[String]])
```

## Opaque Types

### Defining Opaque Types
```scala
// Opaque types provide zero-cost abstractions
// Outside the defining scope, the type is opaque (no access to underlying type)
// Inside the defining scope, it's transparent

object Types:
  opaque type UserId = Long
  opaque type Email = String
  opaque type Meters = Double

  object UserId:
    def apply(id: Long): UserId = id
    extension (id: UserId)
      def value: Long = id

  object Email:
    def apply(s: String): Either[String, Email] =
      if s.contains("@") then Right(s)
      else Left("Invalid email")
    extension (e: Email)
      def value: String = e
      def domain: String = e.split("@")(1)

  object Meters:
    def apply(d: Double): Meters = d
    extension (m: Meters)
      def +(other: Meters): Meters = m + other
      def value: Double = m

// Usage:
import Types.*

val id = UserId(42)
// id + 1  // ERROR: UserId is not Long outside Types
id.value + 1  // OK: 43

val email = Email("alice@example.com")  // Right(alice@example.com)
```

### Opaque Types vs Value Classes
```scala
// Value class (Scala 2 approach) — sometimes allocates
case class UserId(value: Long) extends AnyVal

// Opaque type (Scala 3) — never allocates, true zero-cost
opaque type UserId = Long
// At runtime, UserId IS Long (no wrapper object)
```

## Exports

### Export Clauses
```scala
// Re-export members from a field
class Database:
  def query(sql: String): List[Row] = ???
  def execute(sql: String): Int = ???
  def close(): Unit = ???

class Repository:
  private val db = Database()
  export db.{query, execute}  // selectively export

  // Repository now has query() and execute() but NOT close()

// Export all
class Facade:
  private val service = Service()
  export service.*  // export everything

// Export with rename
class Adapter:
  private val legacy = LegacySystem()
  export legacy.{oldMethod as newMethod}
```
