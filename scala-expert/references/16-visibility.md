# Visibility Rules

Reference for public, private, protected, package-level, companion access, and sealed.

## Table of Contents
- [Access Modifiers](#access-modifiers)
- [Private](#private)
- [Protected](#protected)
- [Package-Level Access](#package-level-access)
- [Companion Object Access](#companion-object-access)

## Access Modifiers

### Overview
| Modifier | Accessible From |
|----------|----------------|
| (none) | Everywhere (public) |
| `private` | Same class/object only |
| `private[this]` | Same instance only |
| `private[pkg]` | Same package |
| `private[EnclosingClass]` | Enclosing class and its companions |
| `protected` | Same class + subclasses |
| `protected[pkg]` | Same class + subclasses + package |

### Scala 3 Default Is Public
```scala
class Example:
  def publicMethod: String = "visible everywhere"
  val publicField: Int = 42
  // No keyword needed for public — this is the default
```

## Private

### private
```scala
class Account:
  private var balance: Double = 0.0

  def deposit(amount: Double): Unit =
    balance += amount  // OK — same class

  def transfer(other: Account, amount: Double): Unit =
    balance -= amount
    other.balance += amount  // OK — same class, different instance
```

### private[this]
```scala
class Account:
  private[this] var balance: Double = 0.0

  def deposit(amount: Double): Unit =
    balance += amount  // OK — same instance

  def transfer(other: Account, amount: Double): Unit =
    balance -= amount
    // other.balance += amount  // ERROR — different instance!
    other.deposit(amount)       // OK — using public method
```

### Private in Nested Scopes
```scala
class Outer:
  private val x = 1

  class Inner:
    def getX: Int = x  // OK — inner class can access outer's private

  private class Secret  // private class

object Outer:
  private val y = 2    // accessible to Outer class and object
```

## Protected

### protected
```scala
class Animal:
  protected def speak: String = "..."

class Dog extends Animal:
  override def speak: String = "Woof"  // OK — subclass
  def bark: String = speak              // OK — same class (subclass)

val d = Dog()
// d.speak  // ERROR — protected, not accessible from outside
d.bark     // OK — bark is public
```

### protected vs Java protected
```scala
// Scala protected: same class + subclasses only
// Java protected: same class + subclasses + same package
// Scala is MORE restrictive

// To match Java protected behavior:
class Example:
  protected[mypackage] def method: String = "accessible in package too"
```

## Package-Level Access

### Qualified Private/Protected
```scala
package com.example.app

class Service:
  private[app] def internal(): Unit = ???     // visible in com.example.app
  private[example] def broader(): Unit = ???  // visible in com.example
  private[com] def widest(): Unit = ???       // visible in com

// Useful for:
// - Testing (make internals visible to test package)
// - Module boundaries (package-private APIs)
```

## Companion Object Access

### Shared Private Access
```scala
class Person private (val name: String, val age: Int)
// Primary constructor is private

object Person:
  def apply(name: String, age: Int): Person =
    require(age >= 0)
    new Person(name, age)  // OK — companion can access private constructor

  def fromString(s: String): Option[Person] =
    s.split(",") match
      case Array(name, ageStr) => Some(new Person(name.trim, ageStr.trim.toInt))
      case _ => None

// val p = new Person("Alice", 30)  // ERROR — private constructor
val p = Person("Alice", 30)         // OK — factory method
```

### Class and Companion Share Private
```scala
class MyClass:
  private val secret = 42

object MyClass:
  def reveal(m: MyClass): Int = m.secret  // OK — companion access

// This works both ways:
object MyObject:
  private val data = "private"

class MyObject:
  def getData: String = MyObject.data  // OK — companion access
```
