# Advanced Functional Programming

Reference for category theory concepts, functors, monads, applicatives, algebraic data types, and effects.

## Table of Contents
- [Category Theory Basics](#category-theory-basics)
- [Functors](#functors)
- [Monads](#monads)
- [Applicatives](#applicatives)
- [Effect Systems](#effect-systems)
- [Algebraic Data Types](#algebraic-data-types)

## Category Theory Basics

### Why Category Theory in Scala
- Provides mathematical foundations for composition patterns
- Functors, monads, applicatives are category theory concepts
- Libraries like Cats and ZIO formalize these patterns
- Understanding them helps write more composable, generic code

### Key Concepts
```
Functor:     "thing you can map over"        F[A].map(A => B): F[B]
Applicative: "functor you can combine"       (F[A], F[B]).mapN((A,B) => C): F[C]
Monad:       "functor you can flatMap over"  F[A].flatMap(A => F[B]): F[B]

Hierarchy:  Monad extends Applicative extends Functor
```

## Functors

### The Functor Pattern
```scala
// A functor provides map: F[A] => (A => B) => F[B]
// Laws:
//   1. Identity:    fa.map(identity) == fa
//   2. Composition: fa.map(f).map(g) == fa.map(f andThen g)

// Built-in functors:
List(1, 2, 3).map(_ * 2)       // List functor
Option(42).map(_ + 1)          // Option functor
Future(42).map(_ + 1)          // Future functor
Right(42).map(_ + 1)           // Either functor (right-biased)
Try(42).map(_ + 1)             // Try functor
```

### Defining a Functor Type Class
```scala
trait Functor[F[_]]:
  extension [A](fa: F[A])
    def map[B](f: A => B): F[B]

// Instance for Option
given Functor[Option] with
  extension [A](fa: Option[A])
    def map[B](f: A => B): Option[B] = fa match
      case Some(a) => Some(f(a))
      case None    => None

// Instance for List
given Functor[List] with
  extension [A](fa: List[A])
    def map[B](f: A => B): List[B] = fa.map(f)

// Generic function using Functor
def doubleAll[F[_]: Functor](fa: F[Int]): F[Int] =
  fa.map(_ * 2)

doubleAll(List(1, 2, 3))   // List(2, 4, 6)
doubleAll(Option(21))       // Some(42)
```

## Monads

### The Monad Pattern
```scala
// A monad provides flatMap: F[A] => (A => F[B]) => F[B]
// Plus pure/unit: A => F[A]
// Laws:
//   1. Left identity:  pure(a).flatMap(f) == f(a)
//   2. Right identity: fa.flatMap(pure) == fa
//   3. Associativity:  fa.flatMap(f).flatMap(g) == fa.flatMap(a => f(a).flatMap(g))

trait Monad[F[_]] extends Functor[F]:
  def pure[A](a: A): F[A]
  extension [A](fa: F[A])
    def flatMap[B](f: A => F[B]): F[B]
    def map[B](f: A => B): F[B] = fa.flatMap(a => pure(f(a)))
```

### Common Monads
```scala
// Option monad: represents optional values
// flatMap short-circuits on None
Some(42).flatMap(x => if x > 0 then Some(x) else None)  // Some(42)
None.flatMap(x => Some(x))                                // None

// Either monad: represents success or failure
// flatMap short-circuits on Left
Right(42).flatMap(x => if x > 0 then Right(x) else Left("negative"))

// List monad: represents non-determinism
List(1, 2).flatMap(x => List(x, x * 10))  // List(1, 10, 2, 20)

// Future monad: represents async computation
Future(42).flatMap(x => Future(x + 1))

// IO monad (from Cats Effect / ZIO): represents side effects
// IO(println("hello")).flatMap(_ => IO(println("world")))
```

### Monad Transformers
```scala
// Problem: nested monads don't compose well
// Future[Option[A]] — you need nested flatMap/map

// Solution: monad transformers (from Cats library)
import cats.data.OptionT
import cats.instances.future.*

def findUser(id: Int): Future[Option[User]] = ???
def findAddress(user: User): Future[Option[Address]] = ???

// With OptionT:
val result: OptionT[Future, Address] = for
  user    <- OptionT(findUser(42))
  address <- OptionT(findAddress(user))
yield address

result.value  // Future[Option[Address]]

// Common transformers:
// OptionT[F, A]  — F[Option[A]]
// EitherT[F, E, A] — F[Either[E, A]]
// StateT[F, S, A] — S => F[(S, A)]
```

## Applicatives

### The Applicative Pattern
```scala
// Applicative: combine independent effects
// Unlike Monad, effects don't depend on previous results

// Applicative can combine failures:
// Monad (flatMap): short-circuits on first error
// Applicative: accumulates all errors

// With Cats Validated:
import cats.data.Validated
import cats.data.Validated.{Valid, Invalid}
import cats.syntax.all.*

case class Person(name: String, age: Int, email: String)

def validateName(s: String): Validated[List[String], String] =
  if s.nonEmpty then Valid(s) else Invalid(List("Name required"))

def validateAge(n: Int): Validated[List[String], Int] =
  if n > 0 && n < 150 then Valid(n) else Invalid(List("Invalid age"))

def validateEmail(s: String): Validated[List[String], String] =
  if s.contains("@") then Valid(s) else Invalid(List("Invalid email"))

// Combine all validations (accumulates ALL errors)
val person = (
  validateName(""),
  validateAge(-1),
  validateEmail("bad")
).mapN(Person.apply)
// Invalid(List("Name required", "Invalid age", "Invalid email"))
```

## Effect Systems

### Cats Effect (IO)
```scala
import cats.effect.IO

// IO[A] represents a side-effectful computation
val program: IO[Unit] = for
  _    <- IO.println("What's your name?")
  name <- IO.readLine
  _    <- IO.println(s"Hello, $name!")
yield ()

// IO is lazy — nothing happens until run
// program.unsafeRunSync()  // actually executes

// Composition
def readFile(path: String): IO[String] = IO(scala.io.Source.fromFile(path).mkString)
def writeFile(path: String, data: String): IO[Unit] = IO(java.nio.file.Files.writeString(java.nio.file.Path.of(path), data))

val copy: IO[Unit] = for
  data <- readFile("input.txt")
  _    <- writeFile("output.txt", data)
yield ()
```

### ZIO
```scala
import zio.*

// ZIO[R, E, A] — R = environment, E = error, A = value
val program: ZIO[Any, IOException, Unit] = for
  _    <- Console.printLine("What's your name?")
  name <- Console.readLine
  _    <- Console.printLine(s"Hello, $name!")
yield ()

// ZIO layers for dependency injection
trait Database:
  def query(sql: String): Task[List[Row]]

val live: ZLayer[Any, Nothing, Database] =
  ZLayer.succeed(new Database { def query(sql: String) = ??? })
```

## Algebraic Data Types

### Sum Types and Product Types
```scala
// Product type: AND (all fields present)
case class User(name: String, age: Int, email: String)
// A User has a name AND an age AND an email

// Sum type: OR (one of several variants)
enum Result[+A]:
  case Success(value: A)
  case Failure(error: String)
// A Result is a Success OR a Failure

// Combining sum and product types
enum Shape:
  case Circle(center: Point, radius: Double)       // product
  case Rectangle(topLeft: Point, bottomRight: Point) // product
// Shape is Circle OR Rectangle (sum of products)
```

### Recursive ADTs
```scala
enum Expr:
  case Num(value: Double)
  case Var(name: String)
  case BinOp(op: String, left: Expr, right: Expr)
  case UnaryOp(op: String, operand: Expr)

def eval(expr: Expr, env: Map[String, Double]): Double = expr match
  case Expr.Num(v)          => v
  case Expr.Var(n)          => env(n)
  case Expr.BinOp("+", l, r) => eval(l, env) + eval(r, env)
  case Expr.BinOp("*", l, r) => eval(l, env) * eval(r, env)
  case Expr.UnaryOp("-", e)  => -eval(e, env)
  case _                     => throw RuntimeException("Unknown op")

// Free monads (advanced pattern — from Cats)
// Represent programs as data, then interpret them
// Useful for building DSLs and testable side-effecting code
```

### GADTs (Generalized Algebraic Data Types)
```scala
// Scala 3 supports GADTs
enum Expr[A]:
  case IntLit(value: Int) extends Expr[Int]
  case BoolLit(value: Boolean) extends Expr[Boolean]
  case Add(left: Expr[Int], right: Expr[Int]) extends Expr[Int]
  case IfThenElse[T](cond: Expr[Boolean], thenE: Expr[T], elseE: Expr[T]) extends Expr[T]

def eval[A](expr: Expr[A]): A = expr match
  case Expr.IntLit(v)  => v        // compiler knows A = Int here
  case Expr.BoolLit(v) => v        // compiler knows A = Boolean here
  case Expr.Add(l, r)  => eval(l) + eval(r)
  case Expr.IfThenElse(c, t, e) => if eval(c) then eval(t) else eval(e)
```
