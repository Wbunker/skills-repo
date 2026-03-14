# Scala's Type System

Reference for path-dependent types, type projections, structural types, type lambdas, match types, and singleton types.

## Table of Contents
- [Path-Dependent Types](#path-dependent-types)
- [Structural Types](#structural-types)
- [Type Lambdas](#type-lambdas)
- [Match Types](#match-types)
- [Singleton Types](#singleton-types)
- [Higher-Kinded Types](#higher-kinded-types)
- [Type Bounds](#type-bounds)
- [Abstract Type Members](#abstract-type-members)

## Path-Dependent Types

### Types That Depend on Values
```scala
class Outer:
  class Inner:
    def whoAmI: String = "inner"

val a = Outer()
val b = Outer()

val ai: a.Inner = a.Inner()  // type is a.Inner
val bi: b.Inner = b.Inner()  // type is b.Inner
// ai and bi have DIFFERENT types

// a.Inner != b.Inner (path-dependent)
// Outer#Inner is the general type (any Outer's Inner)

def processAny(inner: Outer#Inner): Unit = ???  // accepts any Outer's Inner
def processSpecific(outer: Outer)(inner: outer.Inner): Unit = ???  // specific
```

### Dependent Method Types
```scala
trait Key:
  type Value

object StringKey extends Key:
  type Value = String

object IntKey extends Key:
  type Value = Int

def get(key: Key): key.Value = ???  // return type depends on argument
get(StringKey)  // String
get(IntKey)     // Int
```

## Structural Types

### Structural Types (Duck Typing)
```scala
// Define a type by its structure (methods it has)
type Closeable = { def close(): Unit }

def withResource(r: Closeable)(f: => Unit): Unit =
  try f finally r.close()

// Works with any object that has close()
class MyResource:
  def close(): Unit = println("closed")

withResource(MyResource()) {
  println("using resource")
}

// Scala 3: uses Selectable trait for better performance
import scala.reflect.Selectable.reflectiveSelectable

type HasName = { val name: String }
def greet(x: HasName): String = s"Hello, ${x.name}"
```

### Refinement Types
```scala
// Narrow a type with additional members
trait Animal:
  def name: String

type NamedAnimal = Animal { def nickname: String }

// Only accepts Animals that also have a nickname method
def call(a: NamedAnimal): String = a.nickname
```

## Type Lambdas

### Scala 3 Type Lambdas
```scala
// Type-level functions: [X] =>> F[X]
type StringMap = [V] =>> Map[String, V]
// StringMap[Int] = Map[String, Int]

// Useful for partially applying type constructors
type Result = [A] =>> Either[String, A]
// Result[Int] = Either[String, Int]

// With higher-kinded types
def mapValues[F[_], A, B](fa: F[A])(f: A => B)(using Functor[F]): F[B] =
  fa.map(f)

// Apply to partially applied type
// mapValues[Result, Int, String](Right(42))(_.toString)
```

### Kind Projector (Scala 2 equivalent)
```scala
// Scala 2 needed compiler plugin or type lambdas with structural types
// Scala 3 type lambdas are built-in
```

## Match Types

### Compile-Time Type Matching
```scala
// Match types compute types based on other types
type Elem[X] = X match
  case String      => Char
  case Array[t]    => t
  case Iterable[t] => t

// Usage:
val x: Elem[String] = 'a'         // Char
val y: Elem[Array[Int]] = 42      // Int
val z: Elem[List[String]] = "hi"  // String

// Recursive match type
type Flatten[X] = X match
  case Array[Array[t]] => Flatten[Array[t]]
  case Array[t]        => Array[t]
  case t               => t

// Flatten[Array[Array[Array[Int]]]] = Array[Int]
```

### Match Types with Inline
```scala
inline def typeName[T]: String = inline erasedValue[T] match
  case _: Int    => "Int"
  case _: String => "String"
  case _: List[?] => "List"
  case _         => "Other"

typeName[Int]     // "Int" (computed at compile time)
typeName[String]  // "String"
```

## Singleton Types

### Literal Types
```scala
// Scala 3: literal values have singleton types
val x: 42 = 42          // type is literally 42
val s: "hello" = "hello" // type is literally "hello"
val b: true = true       // type is literally true

// Useful for type-level programming
type Zero = 0
type One = 1

// Singleton types in method signatures
def handle(code: 200 | 404 | 500): String = code match
  case 200 => "OK"
  case 404 => "Not Found"
  case 500 => "Server Error"
```

## Higher-Kinded Types

### Types That Take Type Parameters
```scala
// F[_] — a type constructor (takes one type parameter)
trait Functor[F[_]]:
  extension [A](fa: F[A])
    def map[B](f: A => B): F[B]

// F[_, _] — takes two type parameters
trait BiFunctor[F[_, _]]:
  extension [A, B](fab: F[A, B])
    def bimap[C, D](f: A => C, g: B => D): F[C, D]

// Kind: * → * (Functor takes a type and produces a type)
// Kind: * → * → * (BiFunctor takes two types)

// Instances
given Functor[List] with
  extension [A](fa: List[A])
    def map[B](f: A => B): List[B] = fa.map(f)

given Functor[Option] with
  extension [A](fa: Option[A])
    def map[B](f: A => B): Option[B] = fa.map(f)

given BiFunctor[Either] with
  extension [A, B](fab: Either[A, B])
    def bimap[C, D](f: A => C, g: B => D): Either[C, D] = fab match
      case Left(a)  => Left(f(a))
      case Right(b) => Right(g(b))
```

## Type Bounds

### Upper and Lower Bounds
```scala
// Upper bound: A must be a subtype of Comparable
def max[A <: Comparable[A]](a: A, b: A): A =
  if a.compareTo(b) >= 0 then a else b

// Lower bound: B must be a supertype of A
def prepend[A, B >: A](xs: List[A], elem: B): List[B] = elem :: xs

// Context bound: requires a given instance
def sorted[A: Ordering](xs: List[A]): List[A] = xs.sorted

// Combined bounds
def process[A >: Nothing <: AnyRef : Ordering](xs: List[A]): List[A] = xs.sorted
```

## Abstract Type Members

### Type Members vs Type Parameters
```scala
// Type parameter
trait Container[A]:
  def get: A

// Type member (abstract type)
trait Container:
  type Elem
  def get: Elem

class IntContainer extends Container:
  type Elem = Int
  def get: Int = 42

// Type members are useful for:
// - Avoiding long type parameter lists
// - Path-dependent typing
// - When the type is determined by the implementation

// Type member with bounds
trait Collection:
  type Elem <: Comparable[Elem]
  def elements: List[Elem]
  def sorted: List[Elem] = elements.sorted
```
