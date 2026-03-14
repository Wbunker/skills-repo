# The Scala Collections Library

Reference for List, Vector, Map, Set, Array, immutable vs mutable, performance characteristics, and LazyList.

## Table of Contents
- [Collections Overview](#collections-overview)
- [Sequences](#sequences)
- [Maps](#maps)
- [Sets](#sets)
- [Arrays and Strings](#arrays-and-strings)
- [Performance Characteristics](#performance-characteristics)
- [Collection Operations](#collection-operations)
- [LazyList and Views](#lazylist-and-views)
- [Mutable Collections](#mutable-collections)

## Collections Overview

### Hierarchy
```
                Iterable
               /   |    \
            Seq   Map   Set
           /   \
     IndexedSeq  LinearSeq
       |    |      |    |
    Vector Array  List  LazyList
```

### Immutable vs Mutable
```scala
// Immutable (default — import scala.collection.immutable._)
val xs = List(1, 2, 3)        // linked list
val vs = Vector(1, 2, 3)      // indexed sequence
val m = Map("a" -> 1)         // hash trie
val s = Set(1, 2, 3)          // hash set

// Mutable (explicit import)
import scala.collection.mutable
val buf = mutable.ArrayBuffer(1, 2, 3)
val mm = mutable.HashMap("a" -> 1)
val ms = mutable.HashSet(1, 2, 3)
```

## Sequences

### List (Linked List)
```scala
val xs = List(1, 2, 3)
val ys = 0 :: xs              // prepend: O(1)
val zs = xs :+ 4              // append: O(n) — avoid for large lists
val head = xs.head             // 1
val tail = xs.tail             // List(2, 3)
val empty = Nil                // empty list

// Pattern matching
xs match
  case Nil          => "empty"
  case head :: tail => s"$head :: $tail"

// Construction
val range = (1 to 5).toList    // List(1, 2, 3, 4, 5)
val filled = List.fill(3)("x") // List("x", "x", "x")
val tabulated = List.tabulate(5)(i => i * i) // List(0, 1, 4, 9, 16)
```

### Vector (Indexed Sequence)
```scala
val v = Vector(1, 2, 3)
v(0)                           // O(~1) indexed access
v :+ 4                         // O(~1) append
0 +: v                         // O(~1) prepend
v.updated(1, 99)              // O(~1) update at index

// Preferred over List when:
// - Random access needed
// - Appending frequently
// - Large collections (better cache locality)
```

### Range
```scala
1 to 10         // 1, 2, ..., 10 (inclusive)
1 until 10      // 1, 2, ..., 9 (exclusive)
1 to 10 by 2    // 1, 3, 5, 7, 9
10 to 1 by -1   // 10, 9, ..., 1
```

## Maps

### Immutable Map
```scala
val m = Map("a" -> 1, "b" -> 2, "c" -> 3)

// Access
m("a")                   // 1 (throws if missing)
m.get("a")               // Some(1)
m.get("z")               // None
m.getOrElse("z", 0)      // 0
m.contains("a")          // true

// Update (returns new map)
m + ("d" -> 4)           // add/update
m - "a"                  // remove
m ++ Map("d" -> 4, "e" -> 5)  // merge

// Iteration
m.foreach((k, v) => println(s"$k=$v"))
m.keys                   // Iterable("a", "b", "c")
m.values                 // Iterable(1, 2, 3)
m.map((k, v) => (k.toUpperCase, v * 10))

// Transform
m.view.mapValues(_ * 2).toMap  // Map("a" -> 2, "b" -> 4, "c" -> 6)
m.filter((_, v) => v > 1)      // Map("b" -> 2, "c" -> 3)
```

### SortedMap
```scala
import scala.collection.immutable.SortedMap
val sm = SortedMap("c" -> 3, "a" -> 1, "b" -> 2)
sm.keys  // TreeSet("a", "b", "c") — sorted
```

## Sets

### Immutable Set
```scala
val s = Set(1, 2, 3, 2, 1)  // Set(1, 2, 3) — duplicates removed

s + 4            // Set(1, 2, 3, 4)
s - 2            // Set(1, 3)
s ++ Set(4, 5)   // Set(1, 2, 3, 4, 5)
s.contains(2)    // true
s(2)             // true (same as contains)

// Set operations
val a = Set(1, 2, 3)
val b = Set(2, 3, 4)
a & b            // Set(2, 3) — intersection
a | b            // Set(1, 2, 3, 4) — union
a &~ b           // Set(1) — difference
a diff b         // Set(1)
```

## Arrays and Strings

### Array
```scala
// Array is mutable, maps to Java array
val arr = Array(1, 2, 3)
arr(0) = 10             // mutable update
arr.length              // 3

// Creation
Array.fill(5)(0)        // Array(0, 0, 0, 0, 0)
Array.ofDim[Int](3, 4)  // 3x4 matrix
Array.range(0, 10)      // Array(0, 1, ..., 9)

// Conversion
arr.toList              // List(10, 2, 3)
List(1, 2).toArray      // Array(1, 2)

// Array has all Seq methods via implicit conversion to ArraySeq
arr.map(_ * 2)          // Array(20, 4, 6)
arr.filter(_ > 2)       // Array(3)
```

### String as Collection
```scala
// String has collection methods via implicit conversion
"hello".map(_.toUpper)       // "HELLO"
"hello".filter(_ != 'l')     // "heo"
"hello".take(3)              // "hel"
"hello world".split(" ")     // Array("hello", "world")
"hello".zip("world")         // Vector(('h','w'), ('e','o'), ('l','r'), ('l','l'), ('o','d'))
```

## Performance Characteristics

### Time Complexity
| Operation | List | Vector | ArrayBuffer | Array |
|-----------|------|--------|-------------|-------|
| head | O(1) | O(1) | O(1) | O(1) |
| tail | O(1) | O(~1) | O(n) | O(n) |
| apply(i) | O(i) | O(~1) | O(1) | O(1) |
| prepend | O(1) | O(~1) | O(n) | O(n) |
| append | O(n) | O(~1) | O(1)* | O(n) |
| update(i) | O(i) | O(~1) | O(1) | O(1) |

*amortized

### Choosing the Right Collection
```scala
// Default choice: Vector (good all-around performance)
// Prepend-heavy: List
// Random access + mutation: ArrayBuffer
// Key-value: Map (HashMap for unordered, TreeMap for sorted)
// Unique elements: Set
// Interop with Java: Array
```

## Collection Operations

### Common Transformations
```scala
val xs = List(1, 2, 3, 4, 5)

xs.map(_ * 2)              // List(2, 4, 6, 8, 10)
xs.filter(_ > 3)           // List(4, 5)
xs.flatMap(x => List(x, -x)) // List(1, -1, 2, -2, ...)
xs.collect { case x if x % 2 == 0 => x * 10 }  // List(20, 40)
xs.zip(List("a", "b"))    // List((1,"a"), (2,"b"))
xs.zipWithIndex            // List((1,0), (2,1), (3,2), ...)
xs.grouped(2).toList       // List(List(1,2), List(3,4), List(5))
xs.sliding(3).toList       // List(List(1,2,3), List(2,3,4), List(3,4,5))
xs.distinct                // remove duplicates
xs.sorted                  // sort
xs.sortBy(x => -x)        // sort descending
```

### Folding and Reducing
```scala
xs.foldLeft(0)(_ + _)       // 15 (left to right)
xs.foldRight(0)(_ + _)      // 15 (right to left)
xs.reduce(_ + _)             // 15 (no initial value)
xs.scan(0)(_ + _)            // List(0, 1, 3, 6, 10, 15) (running total)

// foldLeft processes: ((((0+1)+2)+3)+4)+5
// foldRight processes: 1+(2+(3+(4+(5+0))))
```

## LazyList and Views

### LazyList (Lazy Sequences)
```scala
// Elements computed on demand, memoized
val naturals: LazyList[Int] = LazyList.from(1)
naturals.take(5).toList  // List(1, 2, 3, 4, 5)

// Fibonacci
val fibs: LazyList[Int] = 0 #:: 1 #:: fibs.zip(fibs.tail).map(_ + _)
fibs.take(10).toList  // List(0, 1, 1, 2, 3, 5, 8, 13, 21, 34)

// Useful for:
// - Infinite sequences
// - Expensive computations (only compute what's needed)
// - Avoiding intermediate collections
```

### Views
```scala
// Views defer transformations (no intermediate collections)
val result = (1 to 1_000_000)
  .view
  .map(_ * 2)
  .filter(_ % 3 == 0)
  .take(10)
  .toList
// Only processes elements until 10 results found
```

## Mutable Collections

### When to Use Mutable
```scala
import scala.collection.mutable

// ArrayBuffer — dynamic array (like ArrayList)
val buf = mutable.ArrayBuffer(1, 2, 3)
buf += 4                    // append
buf.prepend(0)              // prepend
buf.insert(2, 99)           // insert at index
buf.remove(2)               // remove at index

// HashMap
val m = mutable.HashMap("a" -> 1)
m("b") = 2                  // add
m += ("c" -> 3)             // add
m -= "a"                    // remove
m.getOrElseUpdate("d", computeDefault())  // atomic get-or-set

// Best practice: use mutable internally, return immutable
def buildMap(data: List[(String, Int)]): Map[String, Int] =
  val m = mutable.HashMap[String, Int]()
  data.foreach((k, v) => m(k) = v)
  m.toMap  // return immutable
```
