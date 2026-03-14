# Scala Tools and Libraries

Reference for sbt, testing frameworks, Java interop, annotations, and the Scala ecosystem.

## Table of Contents
- [sbt In Depth](#sbt-in-depth)
- [Testing](#testing)
- [Java Interoperability](#java-interoperability)
- [Annotations](#annotations)
- [Key Libraries](#key-libraries)

## sbt In Depth

### Project Configuration
```scala
// build.sbt
ThisBuild / scalaVersion := "3.3.1"
ThisBuild / organization := "com.example"
ThisBuild / version      := "0.1.0-SNAPSHOT"

lazy val root = project
  .in(file("."))
  .settings(
    name := "my-app",
    libraryDependencies ++= Seq(
      "org.typelevel" %% "cats-core"   % "2.10.0",
      "org.typelevel" %% "cats-effect" % "3.5.2",
      "org.scalameta" %% "munit"       % "0.7.29" % Test,
    ),
    scalacOptions ++= Seq(
      "-Wunused:all",
      "-deprecation",
      "-feature",
    ),
  )
```

### Multi-Module Projects
```scala
lazy val core = project
  .in(file("core"))
  .settings(
    libraryDependencies += "org.typelevel" %% "cats-core" % "2.10.0"
  )

lazy val api = project
  .in(file("api"))
  .dependsOn(core)
  .settings(
    libraryDependencies += "com.softwaremill.sttp.tapir" %% "tapir-core" % "1.9.0"
  )

lazy val root = project
  .in(file("."))
  .aggregate(core, api)
```

### sbt Commands
```bash
sbt compile          # Compile main sources
sbt test             # Run all tests
sbt "testOnly *MySpec"  # Run specific test
sbt run              # Run default main class
sbt "runMain com.example.Main"  # Run specific main
sbt console          # REPL with project classpath
sbt ~compile         # Watch mode
sbt clean            # Clean build artifacts
sbt assembly         # Create fat JAR (with sbt-assembly plugin)
sbt publishLocal     # Publish to local Ivy repo
sbt dependencyTree   # Show dependency tree (with sbt-dependency-graph)
```

### Useful Plugins
```scala
// project/plugins.sbt
addSbtPlugin("com.eed3si9n"   % "sbt-assembly"  % "2.1.4")   // fat JARs
addSbtPlugin("org.scalameta"  % "sbt-scalafmt"   % "2.5.2")   // formatting
addSbtPlugin("ch.epfl.scala"  % "sbt-scalafix"   % "0.11.1")  // linting/refactoring
addSbtPlugin("org.scoverage"  % "sbt-scoverage"  % "2.0.9")   // code coverage
addSbtPlugin("com.github.sbt" % "sbt-native-packager" % "1.9.16") // Docker/native
```

## Testing

### MUnit
```scala
// Modern, lightweight testing framework
class MySuite extends munit.FunSuite:

  test("addition works") {
    val result = 1 + 1
    assertEquals(result, 2)
  }

  test("string operations") {
    assert("hello".startsWith("he"))
    assertNotEquals("hello", "world")
  }

  test("exception handling") {
    intercept[ArithmeticException] {
      1 / 0
    }
  }

  test("async test".tag(Slow)) {
    Future { Thread.sleep(100); 42 }.map(assertEquals(_, 42))
  }

  // Fixtures
  val tempFile = FunFixture[java.io.File](
    setup = _ => java.io.File.createTempFile("test", ".tmp"),
    teardown = f => f.delete()
  )
  tempFile.test("file operations") { file =>
    assert(file.exists())
  }
```

### ScalaTest
```scala
// Most popular Scala testing framework
import org.scalatest.flatspec.AnyFlatSpec
import org.scalatest.matchers.should.Matchers

class CalculatorSpec extends AnyFlatSpec with Matchers:
  "A Calculator" should "add numbers" in {
    Calculator.add(1, 2) should be(3)
  }

  it should "handle negative numbers" in {
    Calculator.add(-1, 1) should be(0)
  }

  it should "not divide by zero" in {
    a [ArithmeticException] should be thrownBy {
      Calculator.divide(1, 0)
    }
  }

// FunSuite style
class CalculatorSuite extends AnyFunSuite:
  test("addition") {
    assert(Calculator.add(1, 2) == 3)
  }
```

### ScalaCheck (Property-Based Testing)
```scala
import org.scalacheck.Properties
import org.scalacheck.Prop.forAll

object StringSpec extends Properties("String"):
  property("startsWith") = forAll { (a: String, b: String) =>
    (a + b).startsWith(a)
  }

  property("concatenation length") = forAll { (a: String, b: String) =>
    (a + b).length >= a.length
  }

  property("reverse reverse is identity") = forAll { (s: String) =>
    s.reverse.reverse == s
  }

// With MUnit integration
class MyPropertySuite extends munit.ScalaCheckSuite:
  property("sort is idempotent") {
    forAll { (xs: List[Int]) =>
      xs.sorted == xs.sorted.sorted
    }
  }
```

## Java Interoperability

### Calling Java from Scala
```scala
// Java classes work directly
import java.util.{ArrayList, HashMap}
import java.time.{LocalDate, LocalDateTime}

val list = ArrayList[String]()
list.add("hello")
val date = LocalDate.now()

// Java collections ↔ Scala collections
import scala.jdk.CollectionConverters.*

val javaList: java.util.List[Int] = List(1, 2, 3).asJava
val scalaList: List[Int] = javaList.asScala.toList

val javaMap: java.util.Map[String, Int] = Map("a" -> 1).asJava
val scalaMap: Map[String, Int] = javaMap.asScala.toMap
```

### Calling Scala from Java
```scala
// Scala objects become Java static-like singletons
object Utils:
  def helper(s: String): String = s.toUpperCase
// Java: Utils$.MODULE$.helper("hello")
// Or with @JvmStatic:

object Utils:
  @JvmStatic def helper(s: String): String = s.toUpperCase
// Java: Utils.helper("hello")

// @JvmOverloads for default parameters
class Config @JvmOverloads() (
  val host: String = "localhost",
  val port: Int = 8080
)
// Java: new Config(), new Config("host"), new Config("host", 9090)

// @JvmField to expose fields directly
class Data:
  @JvmField val name = "hello"
// Java: data.name (instead of data.name())

// @throws for checked exceptions
@throws(classOf[java.io.IOException])
def readFile(path: String): String = ???
```

### Handling Java Nulls
```scala
// Wrap nullable Java returns
val result: Option[String] = Option(javaMethod())  // None if null

// Avoid .nn (Scala 3 explicit nulls helper)
// Use Option() or null checks when interacting with Java APIs
```

## Annotations

### Common Annotations
```scala
@deprecated("Use newMethod instead", "2.0")
def oldMethod(): Unit = ???

@tailrec
def factorial(n: Int, acc: Int = 1): Int =
  if n <= 1 then acc else factorial(n - 1, n * acc)

@main def hello(): Unit = println("Hello!")

@throws(classOf[Exception])
def riskyMethod(): Unit = ???

@volatile var flag: Boolean = false  // JVM volatile

@transient val cache: Map[String, Int] = Map()  // not serialized

@inline def fastAdd(a: Int, b: Int): Int = a + b

@unchecked // suppress exhaustiveness warnings
(x: @unchecked) match { case i: Int => i }

import scala.annotation.unused
def method(@unused hint: String): Unit = ???  // suppress unused warning
```

## Key Libraries

### Ecosystem Overview
| Category | Library | Description |
|----------|---------|-------------|
| **FP** | Cats | Type classes, data types, FP abstractions |
| **Effects** | Cats Effect | IO monad, concurrent primitives |
| **Effects** | ZIO | Effect system with environment, error handling |
| **HTTP** | http4s | Functional HTTP server/client |
| **HTTP** | Tapir | Type-safe API descriptions |
| **HTTP** | sttp | HTTP client |
| **JSON** | Circe | Functional JSON library |
| **JSON** | uPickle | Simple JSON/MessagePack |
| **Database** | Doobie | Functional JDBC |
| **Database** | Skunk | Functional PostgreSQL |
| **Database** | Slick | Functional-relational mapping |
| **Streaming** | fs2 | Functional streaming |
| **Streaming** | Akka Streams | Reactive streams |
| **Actors** | Akka | Actor model, clustering |
| **Config** | PureConfig | Typesafe config loading |
| **Logging** | scribe | Scala-native logging |
| **CLI** | decline | Functional argument parsing |
| **Testing** | MUnit | Lightweight test framework |
| **Testing** | ScalaTest | Full-featured test framework |
| **Testing** | ScalaCheck | Property-based testing |
