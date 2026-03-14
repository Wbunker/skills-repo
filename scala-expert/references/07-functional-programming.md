# Functional Programming in Scala

Reference for FP principles, pure functions, higher-order functions, closures, recursion, tail calls, currying, and partial functions.

## Table of Contents
- [FP Principles](#fp-principles)
- [Functions as Values](#functions-as-values)
- [Higher-Order Functions](#higher-order-functions)
- [Closures](#closures)
- [Recursion and Tail Calls](#recursion-and-tail-calls)
- [Currying and Partial Application](#currying-and-partial-application)
- [Partial Functions](#partial-functions)
- [Functional Data Structures](#functional-data-structures)

## FP Principles

### Core Ideas
- **Immutability** — prefer `val` over `var`, immutable collections
- **Pure functions** — same inputs → same outputs, no side effects
- **First-class functions** — functions are values (pass, return, store)
- **Referential transparency** — expression can be replaced by its value
- **Composition** — build complex behavior from simple functions

### Pure vs Impure
```scala
// Pure: no side effects, deterministic
def add(a: Int, b: Int): Int = a + b
def factorial(n: Int): Long = if n <= 1 then 1L else n * factorial(n - 1)

// Impure: side effects (I/O, mutation, randomness)
def printResult(x: Int): Unit = println(x)    // I/O
var counter = 0; def inc(): Int = { counter += 1; counter }  // mutation
def random(): Double = Math.random()           // non-deterministic
```

## Functions as Values

### Function Literals (Lambdas)
```scala
// Full syntax
val add: (Int, Int) => Int = (a: Int, b: Int) => a + b

// Type-inferred
val double = (x: Int) => x * 2

// Placeholder syntax
val triple: Int => Int = _ * 3
val sum: (Int, Int) => Int = _ + _

// Multi-line
val process = (s: String) =>
  val trimmed = s.trim
  val upper = trimmed.toUpperCase
  upper
```

### Function Types
```scala
// Function0 through Function22
val f0: () => Int = () => 42
val f1: Int => String = _.toString
val f2: (Int, Int) => Int = _ + _

// SAM (Single Abstract Method) conversion
trait Processor:
  def process(s: String): String

val p: Processor = s => s.toUpperCase  // lambda as SAM

// Method references
def isEven(n: Int): Boolean = n % 2 == 0
val f: Int => Boolean = isEven  // method → function (eta expansion)
```

## Higher-Order Functions

### Functions That Take Functions
```scala
// map: transform each element
List(1, 2, 3).map(_ * 2)           // List(2, 4, 6)

// filter: keep matching elements
List(1, 2, 3, 4).filter(_ % 2 == 0) // List(2, 4)

// flatMap: transform and flatten
List(1, 2, 3).flatMap(n => List(n, n * 10))  // List(1, 10, 2, 20, 3, 30)

// fold: accumulate a result
List(1, 2, 3, 4).foldLeft(0)(_ + _)  // 10
List("a", "b", "c").foldLeft("")(_ + _)  // "abc"

// reduce: fold without initial value
List(1, 2, 3).reduce(_ + _)  // 6

// foreach: side effect on each element
List(1, 2, 3).foreach(println)

// collect: partial function filter + map
List(1, "two", 3, "four").collect { case i: Int => i * 2 }
// List(2, 6)

// groupBy: partition into map
List("apple", "banana", "avocado").groupBy(_.head)
// Map('a' -> List("apple", "avocado"), 'b' -> List("banana"))

// partition: split into (match, no-match)
List(1, 2, 3, 4).partition(_ % 2 == 0)
// (List(2, 4), List(1, 3))
```

### Returning Functions
```scala
def multiplier(factor: Int): Int => Int =
  (x: Int) => x * factor

val double = multiplier(2)
val triple = multiplier(3)
double(5)  // 10
triple(5)  // 15
```

## Closures

### Closing Over Variables
```scala
// A closure captures variables from its enclosing scope
var total = 0
val addToTotal = (x: Int) => { total += x; total }

addToTotal(10)  // total = 10
addToTotal(20)  // total = 30

// Closure over immutable val (safer)
def makeGreeter(greeting: String): String => String =
  (name: String) => s"$greeting, $name!"

val hello = makeGreeter("Hello")
val hi = makeGreeter("Hi")
hello("Alice")  // "Hello, Alice!"
hi("Bob")       // "Hi, Bob!"
```

## Recursion and Tail Calls

### Basic Recursion
```scala
def factorial(n: Long): Long =
  if n <= 1 then 1L
  else n * factorial(n - 1)  // NOT tail-recursive (multiplies after recursive call)
```

### Tail-Call Optimization
```scala
import scala.annotation.tailrec

// Tail-recursive: recursive call is the LAST operation
@tailrec
def factorial(n: Long, acc: Long = 1L): Long =
  if n <= 1 then acc
  else factorial(n - 1, n * acc)  // tail position — optimized to loop

// @tailrec annotation verifies tail recursion at compile time
// If the method is NOT tail-recursive, compilation fails

// Tail-recursive list operations
@tailrec
def sum(xs: List[Int], acc: Int = 0): Int = xs match
  case Nil     => acc
  case x :: rest => sum(rest, acc + x)  // tail position

// Trampoline for mutual recursion
import scala.util.control.TailCalls.*

def isEven(n: Long): TailRec[Boolean] =
  if n == 0 then done(true) else tailcall(isOdd(n - 1))

def isOdd(n: Long): TailRec[Boolean] =
  if n == 0 then done(false) else tailcall(isEven(n - 1))

isEven(1_000_000).result  // true (no stack overflow)
```

## Currying and Partial Application

### Curried Functions
```scala
// Multiple parameter lists
def add(a: Int)(b: Int): Int = a + b

add(1)(2)  // 3

// Partially apply
val addOne: Int => Int = add(1)
addOne(5)  // 6

// Curried function literal
val addCurried: Int => Int => Int = a => b => a + b
```

### Converting Between Forms
```scala
// Uncurried to curried
def add(a: Int, b: Int): Int = a + b
val addCurried = (add _).curried  // Int => Int => Int

// Curried to uncurried
val addUncurried = Function.uncurried(addCurried)  // (Int, Int) => Int
```

### Why Multiple Parameter Lists
```scala
// 1. Partial application
def log(level: String)(msg: String): Unit = println(s"[$level] $msg")
val info = log("INFO")
val error = log("ERROR")
info("Starting")   // [INFO] Starting
error("Failed")    // [ERROR] Failed

// 2. Type inference (left-to-right)
def map[A, B](xs: List[A])(f: A => B): List[B] = xs.map(f)
map(List(1, 2, 3))(_ * 2)  // B inferred from A

// 3. Using clauses
def sorted[A](xs: List[A])(using Ordering[A]): List[A] = xs.sorted

// 4. Imitation of control structures
def withResource[A](r: Resource)(f: Resource => A): A =
  try f(r) finally r.close()

withResource(openFile("data.txt")) { file =>
  file.readAll()
}
```

## Partial Functions

### PartialFunction[A, B]
```scala
// A function defined only for certain inputs
val reciprocal: PartialFunction[Int, Double] =
  case n if n != 0 => 1.0 / n

reciprocal.isDefinedAt(0)  // false
reciprocal.isDefinedAt(5)  // true
reciprocal(5)              // 0.2
// reciprocal(0)           // throws MatchError

// Use with collect (safe — skips undefined inputs)
List(-1, 0, 1, 2).collect(reciprocal)  // List(-1.0, 1.0, 0.5)

// Chaining partial functions
val handler: PartialFunction[String, String] =
  val handleInt: PartialFunction[String, String] =
    case s if s.toIntOption.isDefined => s"Int: ${s.toInt}"
  val handleBool: PartialFunction[String, String] =
    case "true" | "false" => s"Bool: $s"
  val handleOther: PartialFunction[String, String] =
    case s => s"String: $s"

  handleInt orElse handleBool orElse handleOther
```

## Functional Data Structures

### Immutable by Default
```scala
// Scala's default collections are immutable
val xs = List(1, 2, 3)
val ys = 0 :: xs     // List(0, 1, 2, 3) — xs unchanged
val zs = xs :+ 4     // List(1, 2, 3, 4) — xs unchanged

val m = Map("a" -> 1)
val m2 = m + ("b" -> 2)  // Map("a" -> 1, "b" -> 2) — m unchanged

// Structural sharing: ys shares most of xs's structure
// No copying of entire data structure
```

### Algebraic Data Types (ADTs)
```scala
// Sum type (one of several variants)
enum Shape:
  case Circle(radius: Double)
  case Rectangle(width: Double, height: Double)

// Product type (combination of values)
case class Point(x: Double, y: Double)

// Recursive ADT
enum Tree[+A]:
  case Leaf(value: A)
  case Branch(left: Tree[A], right: Tree[A])

def size[A](tree: Tree[A]): Int = tree match
  case Tree.Leaf(_)      => 1
  case Tree.Branch(l, r) => size(l) + size(r)
```
