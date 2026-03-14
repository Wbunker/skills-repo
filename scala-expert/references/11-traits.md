# Traits

Reference for traits, mixins, stackable modifications, diamond problem, self types, and trait parameters.

## Table of Contents
- [Trait Basics](#trait-basics)
- [Mixin Composition](#mixin-composition)
- [Stackable Modifications](#stackable-modifications)
- [Self Types](#self-types)
- [Trait Parameters](#trait-parameters)
- [Sealed Traits](#sealed-traits)

## Trait Basics

### Defining Traits
```scala
// Traits define interfaces with optional implementations
trait Greeter:
  def greet(name: String): String  // abstract
  def hello(name: String): String = s"Hello, $name"  // concrete

trait Logger:
  def log(msg: String): Unit = println(s"LOG: $msg")

// Class extends one or more traits
class Service extends Greeter, Logger:
  def greet(name: String): String =
    log(s"Greeting $name")
    hello(name)
```

### Traits with Fields
```scala
trait Named:
  val name: String  // abstract field

trait HasId:
  val id: Int = 0  // concrete field with default

class User(val name: String) extends Named, HasId
```

### Traits with Type Parameters
```scala
trait Container[A]:
  def get: A
  def map[B](f: A => B): Container[B]

class Box[A](value: A) extends Container[A]:
  def get: A = value
  def map[B](f: A => B): Container[B] = Box(f(value))
```

## Mixin Composition

### Extending Multiple Traits
```scala
trait Flying:
  def fly(): String = "I can fly!"

trait Swimming:
  def swim(): String = "I can swim!"

trait Walking:
  def walk(): String = "I can walk!"

// Mixin multiple traits
class Duck extends Flying, Swimming, Walking

val duck = Duck()
duck.fly()   // "I can fly!"
duck.swim()  // "I can swim!"
duck.walk()  // "I can walk!"

// Mix in at instantiation time
val swimmer = new Animal with Swimming
```

### Override in Mixins
```scala
trait Base:
  def method: String = "base"

trait A extends Base:
  override def method: String = "A:" + super.method

trait B extends Base:
  override def method: String = "B:" + super.method

class C extends A, B

C().method  // "B:A:base" (linearization order: C → B → A → Base)
```

## Stackable Modifications

### The Pattern
```scala
// Stack behaviors using trait mixins with super calls
trait IntQueue:
  def put(x: Int): Unit
  def get(): Int

class BasicIntQueue extends IntQueue:
  private val buf = scala.collection.mutable.ArrayBuffer[Int]()
  def put(x: Int): Unit = buf += x
  def get(): Int = buf.remove(0)

// Stackable modification traits
trait Doubling extends IntQueue:
  abstract override def put(x: Int): Unit = super.put(x * 2)

trait Incrementing extends IntQueue:
  abstract override def put(x: Int): Unit = super.put(x + 1)

trait Filtering extends IntQueue:
  abstract override def put(x: Int): Unit =
    if x >= 0 then super.put(x)

// Mix and match behaviors
val q1 = new BasicIntQueue with Doubling with Incrementing
q1.put(5)   // Incrementing(5+1=6) → Doubling(6*2=12) → BasicIntQueue.put(12)
q1.get()    // 12

val q2 = new BasicIntQueue with Incrementing with Doubling
q2.put(5)   // Doubling(5*2=10) → Incrementing(10+1=11) → BasicIntQueue.put(11)
q2.get()    // 11
```

### Linearization Order
```
For: class C extends T1, T2, T3
Linearization: C → T3 → T2 → T1 → (base classes)
super calls follow this right-to-left chain
```

## Self Types

### Self Type Annotations
```scala
// Require that a trait can only be mixed into specific types
trait DatabaseAccess:
  self: Configurable =>  // self type: must also be Configurable
  def query(sql: String): List[Row] =
    val url = self.getConfig("db.url")  // can use Configurable methods
    // ...

trait Configurable:
  def getConfig(key: String): String

// This works:
class AppService extends DatabaseAccess, Configurable:
  def getConfig(key: String): String = ???

// This fails at compile time:
// class BadService extends DatabaseAccess  // ERROR: does not extend Configurable
```

### Self Types vs Inheritance
```scala
// Self type: declares a dependency (composition)
trait A:
  self: B =>  // A requires B, but doesn't extend B

// Inheritance: IS-A relationship
trait A extends B  // A is a B

// Self types are used for:
// - Dependency injection (cake pattern)
// - Breaking circular dependencies
// - Requiring a specific mix of traits
```

### Cake Pattern
```scala
// Layered architecture using self types
trait UserRepository:
  def findUser(id: Int): Option[User]

trait UserService:
  self: UserRepository =>  // requires UserRepository
  def getUser(id: Int): User =
    findUser(id).getOrElse(throw Exception("Not found"))

trait EmailService:
  self: UserRepository =>  // also requires UserRepository
  def sendEmail(userId: Int, msg: String): Unit =
    findUser(userId).foreach(u => /* send email */)

// Wire everything together
object ProductionApp extends UserService, EmailService, UserRepository:
  def findUser(id: Int): Option[User] = ??? // real implementation

object TestApp extends UserService, EmailService, UserRepository:
  def findUser(id: Int): Option[User] = Some(User("test", id)) // test stub
```

## Trait Parameters

### Scala 3 Trait Parameters
```scala
// Scala 3: traits can have parameters
trait Greeting(val greeting: String):
  def greet(name: String): String = s"$greeting, $name!"

// Class extending parameterized trait must provide argument
class EnglishGreeter extends Greeting("Hello")
class FrenchGreeter extends Greeting("Bonjour")

EnglishGreeter().greet("Alice")  // "Hello, Alice!"
FrenchGreeter().greet("Alice")   // "Bonjour, Alice!"

// Only the first class/trait in the chain provides the parameter
trait Formal extends Greeting("Good day")
class FormalGreeter extends Formal  // gets "Good day" from Formal
```

## Sealed Traits

### Sealed Hierarchies
```scala
// sealed: all implementations must be in the same file
sealed trait Result[+A]
case class Success[A](value: A) extends Result[A]
case class Failure(error: String) extends Result[Nothing]

// Compiler checks exhaustiveness
def handle[A](r: Result[A]): String = r match
  case Success(v) => s"OK: $v"
  case Failure(e) => s"Error: $e"
// No warning — all cases covered

// Scala 3 enum (preferred)
enum Result[+A]:
  case Success(value: A)
  case Failure(error: String)
```

### Transparent Traits
```scala
// transparent trait: doesn't affect inferred type
transparent trait Serializable
transparent trait Product

case class Point(x: Int, y: Int) extends Serializable
// Inferred type is Point, not Point & Serializable
```
