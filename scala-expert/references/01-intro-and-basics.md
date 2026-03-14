# Introducing Scala

Reference for Scala origins, why Scala, Scala 3, REPL, sbt, and getting started.

## Table of Contents
- [Why Scala](#why-scala)
- [Scala 3](#scala-3)
- [Getting Started](#getting-started)
- [A Taste of Scala](#a-taste-of-scala)

## Why Scala

### The Appeal
- **Scalability** — from scripts to distributed systems
- **Functional + Object-Oriented** — true hybrid language
- **JVM-based** — runs on Java Virtual Machine, interoperates with Java
- **Type safety** — powerful static type system with inference
- **Concise** — significantly less boilerplate than Java
- **Ecosystem** — Akka, Play, Spark, Kafka, Cats, ZIO

### Scala vs Java
| Feature | Java | Scala |
|---------|------|-------|
| Type inference | Limited (`var` since 11) | Pervasive |
| Functions | Lambda since 8 | First-class citizens |
| Pattern matching | Switch (limited) | Full algebraic matching |
| Immutability | Verbose (`final`, records) | Default (`val`, case classes) |
| Null safety | Optional (added) | Option built-in |
| Collections | Mutable by default | Immutable by default |
| Concurrency | Threads, CompletableFuture | Futures, actors, effects |

## Scala 3

### Key Changes from Scala 2
```scala
// New syntax: optional braces (indentation-based)
def hello(name: String): String =
  val greeting = s"Hello, $name"
  greeting  // last expression is return value

// New syntax: quieter control structures
if x > 0 then
  println("positive")
else
  println("non-positive")

for i <- 1 to 10 do
  println(i)

while running do
  process()

// enum (replaces sealed trait + case objects pattern)
enum Color:
  case Red, Green, Blue

// enum with parameters
enum Planet(mass: Double, radius: Double):
  case Mercury extends Planet(3.303e+23, 2.4397e6)
  case Venus   extends Planet(4.869e+24, 6.0518e6)
  case Earth   extends Planet(5.976e+24, 6.37814e6)

// Union types
def handle(input: String | Int): String = input match
  case s: String => s"String: $s"
  case i: Int    => s"Int: $i"

// Intersection types
trait Resettable:
  def reset(): Unit
trait Growable[A]:
  def add(a: A): Unit
def f(x: Resettable & Growable[String]): Unit =
  x.reset()
  x.add("hello")

// Export clauses
class BitSet:
  export implementation.*  // re-export members

// given / using replaces implicit
given ordering: Ordering[Int] = Ordering.Int
def sort[A](xs: List[A])(using ord: Ordering[A]): List[A] = ???
```

### Migration from Scala 2
```bash
# Use the Scala 3 migration tool
# Add to build.sbt:
scalacOptions ++= Seq("-source:3.0-migration", "-rewrite")

# Cross-building
crossScalaVersions := Seq("2.13.12", "3.3.1")

# Key migration items:
# - implicit → given/using
# - implicit class → extension methods
# - sealed trait + case object → enum
# - Procedure syntax removed (def f() { } → def f(): Unit = { })
```

## Getting Started

### Installing Scala
```bash
# Install via Coursier (recommended)
curl -fL https://github.com/coursier/launchers/raw/master/cs-x86_64-pc-linux.gz | gzip -d > cs
chmod +x cs && ./cs setup

# Or via SDKMAN
sdk install scala

# Or via Homebrew (macOS)
brew install scala

# Verify
scala -version
```

### The REPL
```bash
# Start Scala 3 REPL
scala

# REPL commands:
# :help    — show help
# :quit    — exit
# :type    — show type of expression
# :load    — load a file
# :paste   — enter multi-line code
# :reset   — clear all definitions
```

```scala
scala> val x = 42
val x: Int = 42

scala> :type x
Int

scala> List(1, 2, 3).map(_ * 2)
val res0: List[Int] = List(2, 4, 6)
```

### sbt (Scala Build Tool)
```bash
# Create new project
sbt new scala/scala3.g8

# Project structure:
# build.sbt
# project/
#   build.properties
#   plugins.sbt
# src/
#   main/scala/
#   test/scala/
```

```scala
// build.sbt
val scala3Version = "3.3.1"

lazy val root = project
  .in(file("."))
  .settings(
    name := "my-project",
    version := "0.1.0",
    scalaVersion := scala3Version,
    libraryDependencies += "org.scalameta" %% "munit" % "0.7.29" % Test
  )
```

```bash
# Common sbt commands
sbt compile        # Compile
sbt run            # Run main class
sbt test           # Run tests
sbt console        # Start REPL with project classpath
sbt "runMain com.example.Main"  # Run specific main class
sbt ~compile       # Watch mode (recompile on change)
sbt clean          # Clean build artifacts
```

## A Taste of Scala

### Hello World
```scala
// Scala 3 top-level definition (no object wrapper needed)
@main def hello(): Unit =
  println("Hello, Scala 3!")

// Or traditional App trait
object Hello extends App:
  println("Hello, Scala!")

// Or traditional main method
object Hello:
  def main(args: Array[String]): Unit =
    println("Hello, Scala!")
```

### Key Concepts Preview
```scala
// Immutable by default
val name = "Scala"          // immutable (like final)
var count = 0               // mutable (avoid when possible)

// Type inference
val x = 42                  // Int inferred
val xs = List(1, 2, 3)     // List[Int] inferred
val m = Map("a" -> 1)      // Map[String, Int] inferred

// Functions are values
val double = (x: Int) => x * 2
val nums = List(1, 2, 3).map(double)  // List(2, 4, 6)

// Pattern matching
val result = x match
  case 0          => "zero"
  case n if n > 0 => "positive"
  case _          => "negative"

// Case classes (immutable data)
case class Person(name: String, age: Int)
val p = Person("Alice", 30)
val older = p.copy(age = 31)

// Option instead of null
def find(id: Int): Option[String] =
  if id == 1 then Some("found") else None

find(1).getOrElse("not found")  // "found"
find(2).getOrElse("not found")  // "not found"

// For comprehension
val pairs = for
  x <- List(1, 2, 3)
  y <- List("a", "b")
yield (x, y)
// List((1,a), (1,b), (2,a), (2,b), (3,a), (3,b))
```
