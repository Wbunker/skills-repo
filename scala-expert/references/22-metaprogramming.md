# Metaprogramming: Macros and Reflection

Reference for inline, compiletime, macros, reflection, TASTy, and code generation in Scala 3.

## Table of Contents
- [Inline](#inline)
- [Compiletime Operations](#compiletime-operations)
- [Macros](#macros)
- [TASTy Reflection](#tasty-reflection)
- [Common Macro Patterns](#common-macro-patterns)

## Inline

### Inline Methods
```scala
// inline: evaluated at compile time when possible
inline def debug(inline msg: String): Unit =
  println(s"[DEBUG] $msg")

// Compiler inlines the call, no method overhead
debug("hello")
// Becomes: println("[DEBUG] hello")

// inline if: branch is resolved at compile time
inline def choose(inline cond: Boolean): String =
  inline if cond then "yes" else "no"

val result = choose(true)   // compile-time: "yes"
```

### Inline Val
```scala
// inline val: compile-time constant
inline val MaxSize = 1024
inline val AppName = "MyApp"

// Can be used in type positions
val arr: Array[Byte] = new Array[Byte](MaxSize)
```

### Inline Parameters
```scala
// inline parameters must be known at compile time
inline def repeat(inline n: Int)(inline action: => Unit): Unit =
  inline if n > 0 then
    action
    repeat(n - 1)(action)

repeat(3)(println("hello"))
// Unrolled at compile time to:
// println("hello")
// println("hello")
// println("hello")
```

### Transparent Inline
```scala
// transparent inline: return type is refined at call site
transparent inline def parse(s: String): Any =
  inline s match
    case "true"  => true    // Boolean
    case "false" => false   // Boolean
    case _       => s       // String

val x = parse("true")   // x: Boolean = true (not Any!)
val y = parse("hello")  // y: String = "hello"
```

## Compiletime Operations

### scala.compiletime Package
```scala
import scala.compiletime.*

// constValue: extract a literal type's value
inline def name[T]: String = constValue[T]
// name["hello"] → "hello"

// constValueTuple: extract tuple of literal types
inline def names[T <: Tuple]: T = constValueTuple[T]
// names[("a", "b", "c")] → ("a", "b", "c")

// erasedValue: create a phantom value for type matching
inline def typeSize[T]: Int = inline erasedValue[T] match
  case _: Byte    => 1
  case _: Short   => 2
  case _: Int     => 4
  case _: Long    => 8
  case _: Float   => 4
  case _: Double  => 8
  case _: Boolean => 1
  case _: Char    => 2

typeSize[Int]     // 4 (computed at compile time)
typeSize[Double]  // 8

// summonInline: summon given at compile time
inline def show[T](value: T): String =
  val s = summonInline[Show[T]]
  s.show(value)

// error: compile-time error
inline def restricted[T]: Unit =
  inline erasedValue[T] match
    case _: Int    => ()
    case _: String => ()
    case _ => error("Only Int and String are supported")
```

### Compile-Time Arithmetic
```scala
import scala.compiletime.ops.int.*

// Type-level arithmetic
type Three = 1 + 2        // 3
type Six = Three * 2       // 6
type IsPositive = 5 > 0   // true

// Use in type constraints
def takePair[N <: Int](using N > 1 =:= true): Unit = ???
```

## Macros

### Macro Basics
```scala
import scala.quoted.*

// A macro is a method that runs at compile time
// It takes Expr[T] (AST nodes) and produces Expr[T]

// Macro entry point (inline method)
inline def inspect(inline x: Any): String = ${ inspectImpl('x) }

// Macro implementation (runs at compile time)
def inspectImpl(x: Expr[Any])(using Quotes): Expr[String] =
  import quotes.reflect.*
  val tree = x.asTerm
  Expr(s"Expression: ${x.show}, Type: ${tree.tpe.show}")

// Usage:
inspect(1 + 2)
// "Expression: 1.+(2), Type: Int"
```

### Quoting and Splicing
```scala
// ' (quote): turn code into AST (Expr)
// $ (splice): turn AST back into code

// In macro implementation:
def makeDouble(x: Expr[Int])(using Quotes): Expr[Int] =
  '{ $x * 2 }  // $x splices the expression, ' quotes new code

// Quoting blocks
def logging(msg: Expr[String])(using Quotes): Expr[Unit] =
  '{
    println(s"LOG: ${$msg}")
    println(s"Time: ${System.currentTimeMillis()}")
  }

inline def log(inline msg: String): Unit = ${ logging('msg) }
```

### Examining Types at Compile Time
```scala
import scala.quoted.*

inline def typeName[T]: String = ${ typeNameImpl[T] }

def typeNameImpl[T: Type](using Quotes): Expr[String] =
  import quotes.reflect.*
  val name = TypeRepr.of[T].show
  Expr(name)

typeName[List[Int]]  // "scala.collection.immutable.List[scala.Int]"
```

### Pattern Matching on ASTs
```scala
def optimize(expr: Expr[Int])(using Quotes): Expr[Int] =
  expr match
    case '{ 0 + $x }       => x         // 0 + x → x
    case '{ $x + 0 }       => x         // x + 0 → x
    case '{ 1 * $x }       => x         // 1 * x → x
    case '{ $x * 1 }       => x         // x * 1 → x
    case '{ $x * 0 }       => '{ 0 }    // x * 0 → 0
    case other              => other     // no optimization
```

## TASTy Reflection

### Reflection API
```scala
import scala.quoted.*

def inspectClass[T: Type](using Quotes): Expr[String] =
  import quotes.reflect.*

  val tpe = TypeRepr.of[T]
  val symbol = tpe.typeSymbol

  val fields = symbol.caseFields.map { field =>
    s"${field.name}: ${field.tree.asInstanceOf[ValDef].tpt.tpe.show}"
  }

  val methods = symbol.memberMethods.map(_.name)

  Expr(s"Class: ${symbol.name}, Fields: ${fields.mkString(", ")}")

// TASTy (Typed Abstract Syntax Trees) is Scala 3's IR format
// Macros can inspect and generate TASTy
```

### Mirror-Based Derivation
```scala
import scala.deriving.Mirror

// Derive a type class using Mirror (compile-time reflection)
inline def derived[T](using m: Mirror.Of[T]): MyTypeClass[T] =
  inline m match
    case p: Mirror.ProductOf[T] =>
      // Case class: access field types, labels
      val labels = constValueTuple[p.MirroredElemLabels]
      val instances = summonAll[p.MirroredElemTypes]
      // Build instance from field information
      ???
    case s: Mirror.SumOf[T] =>
      // Enum/sealed trait: access variant types
      val instances = summonAll[s.MirroredElemTypes]
      ???
```

## Common Macro Patterns

### JSON Codec Derivation
```scala
// Derive JSON encoder at compile time
inline given derived[T](using Mirror.ProductOf[T]): JsonEncoder[T] =
  ${ deriveEncoder[T] }

def deriveEncoder[T: Type](using Quotes): Expr[JsonEncoder[T]] =
  // Use reflection to get field names and types
  // Generate encoding logic at compile time
  // No runtime reflection overhead
  ???
```

### Compile-Time Validation
```scala
// Validate at compile time
inline def regex(inline pattern: String): scala.util.matching.Regex =
  ${ regexImpl('pattern) }

def regexImpl(pattern: Expr[String])(using Quotes): Expr[scala.util.matching.Regex] =
  import quotes.reflect.*
  pattern.value match
    case Some(p) =>
      try
        java.util.regex.Pattern.compile(p)  // validate at compile time
        '{ new scala.util.matching.Regex($pattern) }
      catch
        case e: java.util.regex.PatternSyntaxException =>
          report.error(s"Invalid regex: ${e.getMessage}")
          '{ ??? }
    case None =>
      report.error("Regex pattern must be a literal string")
      '{ ??? }

// Usage:
val r = regex("[a-z]+")     // OK
// val bad = regex("[a-z")  // Compile error: Invalid regex
```

### Source Location
```scala
// Capture call-site source location
case class SourceLocation(file: String, line: Int)

object SourceLocation:
  inline given generate: SourceLocation =
    ${ generateImpl }

  def generateImpl(using Quotes): Expr[SourceLocation] =
    import quotes.reflect.*
    val pos = Position.ofMacroExpansion
    val file = Expr(pos.sourceFile.name)
    val line = Expr(pos.startLine + 1)
    '{ SourceLocation($file, $line) }

def log(msg: String)(using loc: SourceLocation): Unit =
  println(s"[${loc.file}:${loc.line}] $msg")

log("hello")  // [Main.scala:42] hello
```
