# Type Less, Do More

Reference for type inference, literals, tuples, Option, sealed types, and organizing code.

## Table of Contents
- [Type Inference](#type-inference)
- [Literals](#literals)
- [Tuples](#tuples)
- [Option Type](#option-type)
- [Sealed Hierarchies](#sealed-hierarchies)
- [Organizing Code](#organizing-code)

## Type Inference

### How Inference Works
```scala
// The compiler infers types from context
val x = 42                        // Int
val name = "Scala"                // String
val pi = 3.14                     // Double
val flag = true                   // Boolean
val xs = List(1, 2, 3)           // List[Int]
val pair = (1, "hello")          // (Int, String)

// Method return types are inferred
def add(a: Int, b: Int) = a + b  // returns Int

// Recursive methods MUST have explicit return type
def factorial(n: Int): Long =
  if n <= 1 then 1L else n * factorial(n - 1)

// When to annotate explicitly:
// - Public API methods (good practice)
// - Recursive methods (required)
// - When inference gives unexpected type
// - Implicit/given definitions (required in Scala 3)
```

### Type Ascription
```scala
// Force a specific type
val x: Long = 42           // Int promoted to Long
val xs: Seq[Int] = List(1) // List widened to Seq
val any: Any = "hello"     // String widened to Any

// Useful for overloaded methods
println(42: Long)           // calls println(Long)
```

## Literals

### Numeric Literals
```scala
val dec = 42               // Int (decimal)
val hex = 0xFF             // Int (hexadecimal) = 255
val long = 42L             // Long
val float = 3.14f          // Float
val double = 3.14          // Double
val bigInt = BigInt("123456789012345678901234567890")
val bigDec = BigDecimal("3.14159265358979323846")

// Underscores for readability (Scala 2.13+)
val million = 1_000_000
val hex2 = 0xFF_FF_FF
```

### String Literals
```scala
// Regular strings
val s = "Hello, World"

// Raw strings (triple-quoted, preserves whitespace)
val raw = """This is a
  |multi-line string
  |with leading pipes stripped""".stripMargin

// String interpolation
val name = "Scala"
val s1 = s"Hello, $name"              // s-interpolator
val s2 = s"1 + 1 = ${1 + 1}"         // expressions in ${}
val s3 = f"Pi is $pi%.2f"             // f-interpolator (printf-style)
val s4 = raw"No escape: \n stays \n"  // raw-interpolator

// Custom interpolators (via extension methods on StringContext)
```

### Symbol and Char Literals
```scala
val c: Char = 'A'
val tab: Char = '\t'
val unicode: Char = '\u0041'  // 'A'
```

## Tuples

### Tuple Basics
```scala
// Tuples are typed, fixed-size collections
val pair = (1, "hello")          // (Int, String)
val triple = (1, "hello", 3.14) // (Int, String, Double)

// Access by index (1-based)
pair._1   // 1
pair._2   // "hello"

// Destructuring
val (num, str) = pair
// num: Int = 1
// str: String = "hello"

// Named fields (Scala 3)
val t = (name = "Alice", age = 30)
t.name  // "Alice"
t.age   // 30
```

### Tuple Operations
```scala
// Scala 3: tuples are more powerful
val t1 = (1, "a")
val t2 = (true, 3.14)

// Concatenation
val t3 = t1 ++ t2  // (1, "a", true, 3.14)

// Convert to/from list
val list = t1.toList  // List(1, "a"): List[Int | String]

// Map over tuple elements (Scala 3)
val t = (1, 2, 3)
t.map([T] => (x: T) => x.toString)  // ("1", "2", "3")
```

## Option Type

### Avoiding Null
```scala
// Option[A] = Some[A] | None
def findUser(id: Int): Option[String] =
  if id == 1 then Some("Alice")
  else None

// Safe access
findUser(1).getOrElse("unknown")  // "Alice"
findUser(2).getOrElse("unknown")  // "unknown"

// Pattern matching
findUser(1) match
  case Some(name) => println(s"Found: $name")
  case None       => println("Not found")

// map / flatMap / filter
findUser(1).map(_.toUpperCase)           // Some("ALICE")
findUser(2).map(_.toUpperCase)           // None
findUser(1).filter(_.startsWith("A"))    // Some("Alice")
findUser(1).filter(_.startsWith("B"))    // None

// flatMap for chaining
def findEmail(name: String): Option[String] =
  if name == "Alice" then Some("alice@example.com") else None

findUser(1).flatMap(findEmail)  // Some("alice@example.com")
findUser(2).flatMap(findEmail)  // None

// For comprehension
val email = for
  name  <- findUser(1)
  email <- findEmail(name)
yield email
// Some("alice@example.com")
```

### Option Best Practices
```scala
// DON'T: Use .get (throws NoSuchElementException on None)
// option.get  // AVOID

// DO: Use safe alternatives
option.getOrElse(default)
option.fold(default)(transform)
option.map(transform)
option.foreach(sideEffect)
option.exists(predicate)
option.contains(value)
option.orElse(fallback)

// Convert from nullable Java APIs
Option(javaMethod())  // None if null, Some(value) otherwise
```

## Sealed Hierarchies

### Sealed Traits and Classes
```scala
// Sealed: all subtypes must be in the same file
// Enables exhaustive pattern matching
sealed trait Shape
case class Circle(radius: Double) extends Shape
case class Rectangle(width: Double, height: Double) extends Shape
case class Triangle(base: Double, height: Double) extends Shape

def area(s: Shape): Double = s match
  case Circle(r)       => Math.PI * r * r
  case Rectangle(w, h) => w * h
  case Triangle(b, h)  => 0.5 * b * h
// Compiler warns if a case is missing

// Scala 3 enum (preferred for ADTs)
enum Shape:
  case Circle(radius: Double)
  case Rectangle(width: Double, height: Double)
  case Triangle(base: Double, height: Double)
```

## Organizing Code

### Packages and Imports
```scala
// Package declaration
package com.example.myapp

// Import
import scala.collection.mutable
import scala.collection.mutable.{ArrayBuffer, ListBuffer}
import scala.collection.mutable as m  // rename (Scala 3)
import scala.collection.mutable.{Map as _, *}  // import all except Map

// Package objects (Scala 2, deprecated in 3)
// Use top-level definitions in Scala 3 instead
package com.example
val DefaultTimeout = 30  // top-level definition
def helper(): Unit = ???
```

### Exports (Scala 3)
```scala
// Re-export members from another object
class Logger:
  def info(msg: String): Unit = println(s"INFO: $msg")
  def warn(msg: String): Unit = println(s"WARN: $msg")

class Service:
  private val logger = Logger()
  export logger.*  // Service now has info() and warn() methods
```
