# Pattern Matching

Reference for match expressions, case classes, guards, extractors, regex patterns, and sealed hierarchies.

## Table of Contents
- [Match Expressions](#match-expressions)
- [Pattern Types](#pattern-types)
- [Case Classes and Pattern Matching](#case-classes-and-pattern-matching)
- [Guards](#guards)
- [Extractors](#extractors)
- [Regex Patterns](#regex-patterns)
- [Sealed Hierarchies](#sealed-hierarchies)

## Match Expressions

### Basic Syntax
```scala
// Match is an expression that returns a value
val result = x match
  case 0 => "zero"
  case 1 => "one"
  case _ => "other"  // wildcard (default)

// Match on type
def describe(x: Any): String = x match
  case i: Int    => s"Int: $i"
  case s: String => s"String: $s"
  case _: Double => "some double"
  case _         => "unknown"

// Match on collections
val list = List(1, 2, 3)
list match
  case Nil             => "empty"
  case head :: Nil     => s"single: $head"
  case head :: tail    => s"head=$head, tail=$tail"

// Tuple matching
(1, "a") match
  case (1, s) => s"one and $s"
  case (n, _) => s"$n and something"
```

## Pattern Types

### Literal Patterns
```scala
x match
  case 42      => "forty-two"
  case "hello" => "greeting"
  case true    => "yes"
  case null    => "null!"
```

### Variable Patterns
```scala
x match
  case value => s"matched: $value"  // binds x to 'value'

// IMPORTANT: lowercase names are variable patterns
// Uppercase names or backticked names are stable identifiers
val Pi = 3.14
x match
  case Pi    => "pi"          // matches the value of Pi (constant)
  case other => s"not pi: $other"

// Use backticks for lowercase constants
val expected = 42
x match
  case `expected` => "matched"  // matches value of expected
  case _          => "not matched"
```

### Typed Patterns
```scala
x match
  case s: String       => s.length
  case i: Int          => i * 2
  case xs: List[?]     => xs.size  // ? for erased type parameter
  case m: Map[?, ?]    => m.size

// WARNING: generic types are erased at runtime
// This does NOT work as expected:
// case xs: List[Int] => ...  // compiler warning: type erasure
// Use List[?] and check elements instead
```

### Constructor Patterns (Case Classes)
```scala
case class Person(name: String, age: Int)

person match
  case Person("Alice", age)     => s"Alice is $age"
  case Person(name, age) if age > 18 => s"$name is adult"
  case Person(name, _)          => s"$name (any age)"
```

### Nested Patterns
```scala
case class Address(city: String, state: String)
case class Person(name: String, address: Address)

person match
  case Person(name, Address("NYC", _)) => s"$name from NYC"
  case Person(_, Address(city, "CA"))  => s"Someone from $city, CA"
  case _ => "other"
```

## Case Classes and Pattern Matching

### How Case Classes Enable Matching
```scala
// case class auto-generates:
// - unapply method (for pattern matching / extraction)
// - apply method (for construction without new)
// - equals, hashCode, toString
// - copy method
// - Product trait implementation

case class Email(user: String, domain: String)

val email = Email("alice", "example.com")  // apply

email match
  case Email(u, d) => println(s"User: $u, Domain: $d")  // unapply

val updated = email.copy(domain = "newdomain.com")  // copy
```

## Guards

### Pattern Guards
```scala
x match
  case n: Int if n > 0 && n < 100 => "small positive"
  case n: Int if n >= 100          => "large positive"
  case n: Int if n < 0             => "negative"
  case 0                           => "zero"

// Guards in for comprehensions
for
  person <- people
  if person.age >= 18
yield person.name
```

### Combining Patterns with `|`
```scala
x match
  case 0 | 1 | 2 => "small"
  case _          => "other"

day match
  case "Saturday" | "Sunday" => "weekend"
  case _                     => "weekday"
```

## Extractors

### Custom Extractors (unapply)
```scala
// Extractor with unapply returning Option
object Email:
  def unapply(s: String): Option[(String, String)] =
    s.split("@") match
      case Array(user, domain) => Some((user, domain))
      case _                   => None

"alice@example.com" match
  case Email(user, domain) => println(s"$user at $domain")
  case _                   => println("not an email")
```

### Boolean Extractors
```scala
// unapply returning Boolean (test only, no extraction)
object Even:
  def unapply(n: Int): Boolean = n % 2 == 0

42 match
  case Even() => "even"  // note the empty parens
  case _      => "odd"
```

### Sequence Extractors (unapplySeq)
```scala
object Words:
  def unapplySeq(s: String): Option[Seq[String]] =
    Some(s.trim.split("\\s+").toSeq)

"hello world foo" match
  case Words(first, second, rest*) =>
    println(s"first=$first, second=$second, rest=$rest")
  // first=hello, second=world, rest=List(foo)
```

### Product Extractors (Scala 3)
```scala
// Case classes automatically work as extractors
// Scala 3 also supports name-based extractors
class FullName(val first: String, val last: String)

object FullName:
  def unapply(n: FullName): (String, String) = (n.first, n.last)
  // In Scala 3: non-Option return types work for irrefutable patterns
```

## Regex Patterns

### Regex Matching
```scala
val datePattern = """(\d{4})-(\d{2})-(\d{2})""".r

"2024-01-15" match
  case datePattern(year, month, day) =>
    println(s"$year/$month/$day")
  case _ =>
    println("not a date")

// Regex groups become extractors via unapplySeq
val email = """(\w+)@([\w.]+)""".r
"alice@example.com" match
  case email(user, domain) => s"$user at $domain"

// Find all matches
val numbers = """\d+""".r
numbers.findAllIn("abc 123 def 456").toList  // List("123", "456")
```

## Sealed Hierarchies

### Exhaustive Matching
```scala
// Sealed = all subtypes defined in same file
// Compiler checks exhaustiveness
sealed trait Result
case class Success(value: Int) extends Result
case class Error(message: String) extends Result

def handle(r: Result): String = r match
  case Success(v) => s"OK: $v"
  case Error(m)   => s"Error: $m"
// If you miss a case, compiler warns:
// "match may not be exhaustive. It would fail on: Error(_)"

// Scala 3 enum as sealed hierarchy
enum Json:
  case JNull
  case JBool(value: Boolean)
  case JNum(value: Double)
  case JStr(value: String)
  case JArr(items: List[Json])
  case JObj(fields: Map[String, Json])

def stringify(json: Json): String = json match
  case Json.JNull      => "null"
  case Json.JBool(b)   => b.toString
  case Json.JNum(n)    => n.toString
  case Json.JStr(s)    => s"\"$s\""
  case Json.JArr(items) => items.map(stringify).mkString("[", ",", "]")
  case Json.JObj(fields) =>
    fields.map((k, v) => s"\"$k\":${stringify(v)}").mkString("{", ",", "}")
```

### @unchecked Annotation
```scala
// Suppress exhaustiveness warning (use sparingly)
(x: @unchecked) match
  case i: Int => i * 2
  // No warning about missing cases
```
