# For Comprehensions in Depth

Reference for generators, guards, yield, desugaring to flatMap/map/withFilter, and monadic composition.

## Table of Contents
- [For Comprehension Syntax](#for-comprehension-syntax)
- [Desugaring Rules](#desugaring-rules)
- [Working with Options](#working-with-options)
- [Working with Either and Try](#working-with-either-and-try)
- [Working with Futures](#working-with-futures)
- [Custom Types in For Comprehensions](#custom-types-in-for-comprehensions)

## For Comprehension Syntax

### Generators, Guards, and Yield
```scala
// Generator: x <- collection
for x <- List(1, 2, 3) yield x * 2
// List(2, 4, 6)

// Multiple generators (nested iteration)
for
  x <- List(1, 2)
  y <- List("a", "b")
yield (x, y)
// List((1,a), (1,b), (2,a), (2,b))

// Guard (filter)
for
  x <- 1 to 20
  if x % 3 == 0
  if x % 5 == 0
yield x
// Vector(15)

// Value definition
for
  line <- io.Source.fromFile("data.txt").getLines()
  trimmed = line.trim       // intermediate value (not a generator)
  if trimmed.nonEmpty
yield trimmed

// Side effects (no yield — returns Unit)
for
  x <- List(1, 2, 3)
do println(x)
```

### Nested For Comprehensions
```scala
// Dependent generators
for
  xs <- List(List(1, 2), List(3, 4))
  x  <- xs
yield x * 10
// List(10, 20, 30, 40)

// Pattern matching in generators
val pairs = List(("a", 1), ("b", 2), ("c", 3))
for (key, value) <- pairs yield s"$key=$value"
// List("a=1", "b=2", "c=3")

// With case (filters non-matching)
val mixed: List[Any] = List(1, "two", 3, "four")
for case i: Int <- mixed yield i * 2
// List(2, 6)
```

## Desugaring Rules

### How the Compiler Translates For Expressions
```scala
// Rule 1: Single generator with yield → map
for x <- xs yield f(x)
// becomes:
xs.map(x => f(x))

// Rule 2: Multiple generators with yield → flatMap + map
for
  x <- xs
  y <- ys
yield (x, y)
// becomes:
xs.flatMap(x => ys.map(y => (x, y)))

// Rule 3: Guard → withFilter
for
  x <- xs
  if p(x)
yield f(x)
// becomes:
xs.withFilter(x => p(x)).map(x => f(x))

// Rule 4: Value definition → map in intermediate position
for
  x <- xs
  y = f(x)
yield g(x, y)
// becomes:
xs.map(x => (x, f(x))).map((x, y) => g(x, y))

// Rule 5: No yield → foreach
for x <- xs do f(x)
// becomes:
xs.foreach(x => f(x))
```

### Full Desugaring Example
```scala
// This for comprehension:
for
  x <- List(1, 2, 3)
  if x > 1
  y <- List(x, x * 10)
yield y + 1

// Desugars to:
List(1, 2, 3)
  .withFilter(x => x > 1)
  .flatMap(x => List(x, x * 10).map(y => y + 1))
// List(3, 21, 4, 31)
```

## Working with Options

### Option Chaining
```scala
case class User(name: String, addressId: Option[Int])
case class Address(id: Int, city: String, zip: Option[String])

def findUser(name: String): Option[User] = ???
def findAddress(id: Int): Option[Address] = ???

// Chaining with for comprehension
val zipCode: Option[String] = for
  user    <- findUser("Alice")
  addrId  <- user.addressId
  address <- findAddress(addrId)
  zip     <- address.zip
yield zip

// Equivalent to:
findUser("Alice")
  .flatMap(_.addressId)
  .flatMap(findAddress)
  .flatMap(_.zip)
```

## Working with Either and Try

### Either Composition
```scala
def parseInt(s: String): Either[String, Int] =
  try Right(s.toInt)
  catch case _: NumberFormatException => Left(s"Not an int: $s")

def divide(a: Int, b: Int): Either[String, Int] =
  if b == 0 then Left("Division by zero")
  else Right(a / b)

// For comprehension with Either (short-circuits on Left)
val result: Either[String, Int] = for
  a <- parseInt("10")
  b <- parseInt("3")
  c <- divide(a, b)
yield c
// Right(3)

val bad: Either[String, Int] = for
  a <- parseInt("abc")   // Left("Not an int: abc")
  b <- parseInt("3")     // skipped
  c <- divide(a, b)      // skipped
yield c
// Left("Not an int: abc")
```

### Try Composition
```scala
import scala.util.{Try, Success, Failure}

val result: Try[Int] = for
  a <- Try("10".toInt)
  b <- Try("3".toInt)
  c <- Try(a / b)
yield c
// Success(3)
```

## Working with Futures

### Async Composition
```scala
import scala.concurrent.{Future, ExecutionContext}
import scala.concurrent.ExecutionContext.Implicits.global

def fetchUser(id: Int): Future[User] = ???
def fetchOrders(userId: Int): Future[List[Order]] = ???
def fetchProducts(orderId: Int): Future[List[Product]] = ???

// Sequential composition (each depends on previous)
val result: Future[List[Product]] = for
  user     <- fetchUser(42)
  orders   <- fetchOrders(user.id)
  products <- fetchProducts(orders.head.id)
yield products

// Parallel execution: start futures BEFORE the for comprehension
val userF = fetchUser(42)
val settingsF = fetchSettings(42)

val result = for
  user     <- userF      // already running
  settings <- settingsF  // already running
yield (user, settings)
```

## Custom Types in For Comprehensions

### Required Methods
```scala
// To work in for comprehensions, a type needs:
// - map[B](f: A => B): F[B]              (for yield)
// - flatMap[B](f: A => F[B]): F[B]       (for multiple generators)
// - withFilter(p: A => Boolean): F[A]     (for guards)
// - foreach(f: A => Unit): Unit           (for do)

// Example: custom container
case class Box[A](value: A):
  def map[B](f: A => B): Box[B] = Box(f(value))
  def flatMap[B](f: A => Box[B]): Box[B] = f(value)
  def withFilter(p: A => Boolean): Box[A] =
    if p(value) then this else throw MatchError(value)

// Now works in for comprehensions:
val result = for
  x <- Box(10)
  y <- Box(20)
yield x + y
// Box(30)
```

### Monadic Laws
```scala
// Any type used in for comprehensions should satisfy:

// 1. Left identity: unit(a).flatMap(f) == f(a)
Some(42).flatMap(x => Some(x + 1))  ==  Some(43)

// 2. Right identity: m.flatMap(unit) == m
Some(42).flatMap(Some(_))  ==  Some(42)

// 3. Associativity: m.flatMap(f).flatMap(g) == m.flatMap(x => f(x).flatMap(g))
Some(42).flatMap(x => Some(x + 1)).flatMap(y => Some(y * 2))  ==
Some(42).flatMap(x => Some(x + 1).flatMap(y => Some(y * 2)))
```
