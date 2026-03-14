# Variance Behavior and Equality

Reference for covariance, contravariance, invariance, universal equality, multiversal equality, and CanEqual.

## Table of Contents
- [Variance](#variance)
- [Covariance](#covariance)
- [Contravariance](#contravariance)
- [Invariance](#invariance)
- [Variance Positions](#variance-positions)
- [Equality](#equality)

## Variance

### What Variance Means
```
Given: Dog extends Animal

Covariant (+A):     List[Dog] is a subtype of List[Animal]
Contravariant (-A): Handler[Animal] is a subtype of Handler[Dog]
Invariant (A):      Mutable[Dog] is NOT related to Mutable[Animal]
```

### Declaring Variance
```scala
class Producer[+A]      // covariant
class Consumer[-A]      // contravariant
class Container[A]      // invariant (default)
```

## Covariance

### When to Use Covariance (+A)
```scala
// Covariant: produces A values, doesn't consume them
// "If Dog is an Animal, then Box[Dog] is a Box[Animal]"

class Box[+A](val value: A)

val dogBox: Box[Dog] = Box(Dog("Rex"))
val animalBox: Box[Animal] = dogBox  // OK — covariant

// Built-in covariant types:
// List[+A], Option[+A], Vector[+A], Set[+A], Map[+K, +V] (in value)
// Function return type: Function1[-A, +B]

val dogs: List[Dog] = List(Dog("Rex"), Dog("Fido"))
val animals: List[Animal] = dogs  // OK
```

### Covariance Restriction
```scala
// Covariant type parameter CANNOT appear in method input position
class Box[+A]:
  // def put(a: A): Unit  // ERROR: covariant A in contravariant position

  // Solution: use lower bound
  def put[B >: A](b: B): Box[B] = Box(b)

// This is why List is immutable:
// :: returns List[B] where B >: A
val animals: List[Animal] = Dog("Rex") :: List[Animal]()
```

## Contravariance

### When to Use Contravariance (-A)
```scala
// Contravariant: consumes A values, doesn't produce them
// "If Dog is an Animal, then Vet[Animal] is a Vet[Dog]"
// (A vet that handles any animal can certainly handle dogs)

trait Vet[-A]:
  def treat(animal: A): Unit

val animalVet: Vet[Animal] = new Vet[Animal]:
  def treat(a: Animal): Unit = println(s"Treating ${a}")

val dogVet: Vet[Dog] = animalVet  // OK — contravariant

// Built-in contravariant positions:
// Function input: Function1[-A, +B]
// Ordering[-A], Equiv[-A], CanEqual[-L, -R]

val animalOrd: Ordering[Animal] = Ordering.by(_.name)
val dogOrd: Ordering[Dog] = animalOrd  // OK
```

## Invariance

### When Types Are Invariant
```scala
// Mutable containers must be invariant
class MutableBox[A](var value: A)

val dogBox: MutableBox[Dog] = MutableBox(Dog("Rex"))
// val animalBox: MutableBox[Animal] = dogBox  // ERROR — invariant

// Why? If allowed:
// animalBox.value = Cat("Whiskers")  // puts a Cat in a Dog box!
// dogBox.value  // would return a Cat typed as Dog — unsound!

// Array is invariant (it's mutable)
val dogs: Array[Dog] = Array(Dog("Rex"))
// val animals: Array[Animal] = dogs  // ERROR
```

## Variance Positions

### Position Rules
```scala
// A type parameter's position determines allowed variance:
trait Example[+A, -B]:
  def produce: A           // +A in return (covariant) position: OK
  def consume(b: B): Unit  // -B in parameter (contravariant) position: OK
  // def bad(a: A): Unit   // +A in parameter position: ERROR
  // def bad2: B            // -B in return position: ERROR

// Nested positions flip:
trait Callback[+A]:
  // Function parameter flips the position
  def onResult(handler: A => Unit): Unit  // A appears in "flipped" position
  // ERROR: +A in contravariant position (input of handler)

  // Fix with lower bound
  def onResult[B >: A](handler: B => Unit): Unit  // OK
```

### Summary Table
| Position | Covariant (+A) | Contravariant (-A) | Invariant (A) |
|----------|---------------|-------------------|--------------|
| Method return type | OK | Error | OK |
| Method parameter | Error | OK | OK |
| val field type | OK | Error | OK |
| var field type | Error | Error | OK |

## Equality

### Universal Equality (==)
```scala
// By default, any two values can be compared
42 == "hello"  // false (but compiles — potentially a bug!)
List(1) == "abc"  // false (compiles, almost certainly a bug)

// == calls .equals (structural equality)
// eq/ne test reference equality
val a = List(1, 2)
val b = List(1, 2)
a == b   // true (structural: same contents)
a eq b   // false (referential: different objects)

// Case classes get structural equals automatically
case class Point(x: Int, y: Int)
Point(1, 2) == Point(1, 2)  // true
```

### Multiversal Equality (Scala 3)
```scala
// Scala 3 can restrict which types can be compared
import scala.language.strictEquality

// With strict equality, you must declare what can be compared
case class Celsius(value: Double) derives CanEqual
case class Fahrenheit(value: Double) derives CanEqual

Celsius(100) == Celsius(100)      // OK
// Celsius(100) == Fahrenheit(212) // ERROR: cannot compare

// Allow cross-type comparison explicitly
given CanEqual[Celsius, Fahrenheit] = CanEqual.derived
Celsius(100) == Fahrenheit(212)    // OK now (compiles, false at runtime)
```

### CanEqual Type Class
```scala
// CanEqual[L, R] — evidence that L and R can be compared
trait CanEqual[-L, -R]

// Auto-derived for case classes with `derives CanEqual`
case class UserId(value: Long) derives CanEqual

// Custom equality for a hierarchy
sealed trait Shape derives CanEqual
case class Circle(r: Double) extends Shape
case class Square(s: Double) extends Shape
Circle(1) == Square(1)  // OK — same hierarchy

// With strict equality enabled:
// - Same type: always allowed
// - Different types: need CanEqual instance
// - Subtype: allowed if parent has CanEqual
```

### Best Practices
```scala
// 1. Enable strict equality in new projects
scalacOptions += "-language:strictEquality"

// 2. Use derives CanEqual on sealed hierarchies
// 3. Override equals/hashCode together (or use case classes)
// 4. Use == for comparison (not .equals — handles null)
// 5. Use eq only when reference identity matters
```
