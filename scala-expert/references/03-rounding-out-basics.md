# Rounding Out the Basics

Reference for operator overloading, enums, string interpolation, conditionals, error handling, and lazy vals.

## Table of Contents
- [Operator Overloading](#operator-overloading)
- [Enumerations](#enumerations)
- [Conditionals and Loops](#conditionals-and-loops)
- [Error Handling](#error-handling)
- [Lazy Values](#lazy-values)
- [Named and Default Parameters](#named-and-default-parameters)

## Operator Overloading

### Operators Are Methods
```scala
// In Scala, operators are just methods
1 + 2         // same as 1.+(2)
"ab" * 3      // same as "ab".*(3)  →  "ababab"

// Define your own
case class Vec(x: Double, y: Double):
  def +(other: Vec): Vec = Vec(x + other.x, y + other.y)
  def *(scalar: Double): Vec = Vec(x * scalar, y * scalar)
  def unary_- : Vec = Vec(-x, -y)  // prefix operator

val v1 = Vec(1, 2)
val v2 = Vec(3, 4)
val v3 = v1 + v2      // Vec(4.0, 6.0)
val v4 = v1 * 2.0     // Vec(2.0, 4.0)
val v5 = -v1           // Vec(-1.0, -2.0)
```

### Infix Notation
```scala
// Methods with one parameter can be called infix
// Scala 3: requires `infix` modifier or backticks for alphanumeric names
infix def max(other: Int): Int = if this > other then this else other

// Right-associative operators end with ':'
1 :: 2 :: 3 :: Nil   // same as Nil.::(3).::(2).::(1)
// Result: List(1, 2, 3)
```

### Precedence
```
Highest → Lowest:
  (all other special characters)
  * / %
  + -
  :
  < >
  = !
  &
  ^
  |
  (all letters, including _)
  (assignment operators like +=, -=)
```

## Enumerations

### Scala 3 Enums
```scala
// Simple enum
enum Color:
  case Red, Green, Blue

val c = Color.Red
c.ordinal   // 0
Color.valueOf("Red")   // Color.Red
Color.values           // Array(Red, Green, Blue)

// Parameterized enum
enum Planet(val mass: Double, val radius: Double):
  def surfaceGravity: Double = Planet.G * mass / (radius * radius)
  case Mercury extends Planet(3.303e+23, 2.4397e6)
  case Earth   extends Planet(5.976e+24, 6.37814e6)

object Planet:
  private val G = 6.67300e-11

// ADT enum (algebraic data type)
enum Expr:
  case Literal(value: Double)
  case Add(left: Expr, right: Expr)
  case Multiply(left: Expr, right: Expr)
  case Variable(name: String)

def eval(expr: Expr, env: Map[String, Double]): Double = expr match
  case Expr.Literal(v)    => v
  case Expr.Add(l, r)     => eval(l, env) + eval(r, env)
  case Expr.Multiply(l, r) => eval(l, env) * eval(r, env)
  case Expr.Variable(n)   => env(n)

// Enum with methods and type parameters
enum Option[+A]:
  case Some(value: A)
  case None
  def map[B](f: A => B): Option[B] = this match
    case Some(v) => Some(f(v))
    case None    => None
```

## Conditionals and Loops

### If Expressions
```scala
// if is an expression (returns a value)
val max = if a > b then a else b

// Multi-line (Scala 3 indentation syntax)
val result =
  if x < 0 then
    "negative"
  else if x == 0 then
    "zero"
  else
    "positive"
```

### For Expressions
```scala
// Generator
for i <- 1 to 10 do println(i)

// With yield (produces a value)
val doubled = for i <- 1 to 5 yield i * 2
// Vector(2, 4, 6, 8, 10)

// Multiple generators
val pairs = for
  x <- 1 to 3
  y <- 1 to 3
  if x != y           // guard (filter)
yield (x, y)

// With definitions
for
  line <- io.Source.fromFile("data.txt").getLines()
  trimmed = line.trim
  if trimmed.nonEmpty
yield trimmed
```

### While Loops
```scala
// While (Scala 3 syntax)
var i = 0
while i < 10 do
  println(i)
  i += 1

// Note: prefer recursion or collection operations over while loops
```

### Match Expressions
```scala
// Match is an expression
val description = x match
  case 1 => "one"
  case 2 => "two"
  case n if n > 0 => s"positive: $n"
  case _ => "other"
```

## Error Handling

### Try / Catch / Finally
```scala
import scala.util.{Try, Success, Failure}

// Traditional try/catch
try
  val result = riskyOperation()
  process(result)
catch
  case e: FileNotFoundException =>
    println(s"File not found: ${e.getMessage}")
  case e: IOException =>
    println(s"IO error: ${e.getMessage}")
  case e: Exception =>
    println(s"Unexpected: ${e.getMessage}")
finally
  cleanup()
```

### Try Monad
```scala
// Try[A] = Success[A] | Failure[Throwable]
val result: Try[Int] = Try("42".toInt)  // Success(42)
val bad: Try[Int] = Try("abc".toInt)    // Failure(NumberFormatException)

// map / flatMap / recover
result.map(_ * 2)                // Success(84)
bad.map(_ * 2)                   // Failure(...)
bad.getOrElse(0)                 // 0
bad.recover { case _: NumberFormatException => -1 }  // Success(-1)

// Chain with flatMap
def parseInt(s: String): Try[Int] = Try(s.toInt)
def divide(a: Int, b: Int): Try[Int] = Try(a / b)

val computation = for
  a <- parseInt("10")
  b <- parseInt("3")
  result <- divide(a, b)
yield result
// Success(3)
```

### Either
```scala
// Either[L, R] — Right is success by convention
def divide(a: Int, b: Int): Either[String, Int] =
  if b == 0 then Left("Division by zero")
  else Right(a / b)

divide(10, 3)  // Right(3)
divide(10, 0)  // Left("Division by zero")

// map / flatMap work on Right
divide(10, 3).map(_ * 2)  // Right(6)

// For comprehension
val result = for
  x <- divide(10, 2)
  y <- divide(x, 3)
yield y
```

## Lazy Values

### Lazy Evaluation
```scala
// lazy val: computed once, on first access
lazy val expensiveResult =
  println("Computing...")
  heavyComputation()

// Not computed until accessed:
println("Before access")
val r = expensiveResult  // prints "Computing..." then computes
val r2 = expensiveResult // uses cached value, no recomputation

// Use cases:
// - Expensive initialization deferred until needed
// - Breaking circular dependencies
// - Infinite/deferred streams
```

### Call-by-Name Parameters
```scala
// => T means evaluated each time it's used (not just once)
def logging(enabled: Boolean, msg: => String): Unit =
  if enabled then println(msg)  // msg only evaluated if enabled

logging(false, expensiveStringBuild())  // expensiveStringBuild NOT called

// Compare:
// def f(x: Int)      — call-by-value (evaluated once at call site)
// def f(x: => Int)   — call-by-name (evaluated each time x is used)
```

## Named and Default Parameters

### Named Arguments
```scala
def createUser(name: String, age: Int, email: String): User = ???

// Call with named arguments (any order)
createUser(email = "alice@example.com", name = "Alice", age = 30)
```

### Default Values
```scala
def connect(
  host: String = "localhost",
  port: Int = 5432,
  ssl: Boolean = false
): Connection = ???

connect()                          // all defaults
connect("db.example.com")         // override host only
connect(port = 3306)              // override port only
connect("db.example.com", ssl = true)  // mix positional + named
```

### Copy with Named Parameters
```scala
case class Config(host: String, port: Int, ssl: Boolean)

val default = Config("localhost", 5432, false)
val production = default.copy(host = "db.prod.com", ssl = true)
// Config("db.prod.com", 5432, true)
```
