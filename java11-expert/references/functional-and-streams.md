# Java 11 Functional Programming and Streams
## Lambdas, var in Lambdas, Method References, java.util.function, Stream API, Optional, Collectors

---

## Lambda Expressions

A lambda is a concise inline implementation of a **functional interface** (single abstract method).

### Syntax Forms

```java
// Full form
(String s) -> { return s.toUpperCase(); }

// Inferred parameter type
(s) -> { return s.toUpperCase(); }

// Single parameter — parentheses optional
s -> { return s.toUpperCase(); }

// Single expression — braces and return optional
s -> s.toUpperCase()

// No parameters
() -> System.out.println("hello")

// Multiple parameters
(a, b) -> a + b
```

### Scope Rules

- Lambdas can capture **effectively final** local variables (assigned once, never changed)
- `this` refers to the **enclosing class** instance (not the lambda itself)
- Cannot shadow local variables from the enclosing scope

```java
int multiplier = 3;  // effectively final
Function<Integer, Integer> triple = x -> x * multiplier;
// multiplier = 4;  // would break the lambda — won't compile
```

### `var` in Lambda Parameters (JEP 323, Java 11)

The main use case for `var` in lambda params is **annotations**:

```java
// Bare lambda (no annotation possible)
list.stream().map(s -> s.trim());

// var lambda — enables annotation
list.stream().map((@NonNull var s) -> s.trim());
list.stream().map((@Deprecated var s) -> s.trim());

// All params must be var or all bare — cannot mix:
(var x, var y) -> x + y      // OK
(x, y) -> x + y              // OK
(var x, y) -> x + y          // COMPILE ERROR — must be consistent
```

---

## `java.util.function` — Standard Functional Interfaces

| Interface | Method | Input → Output | Use Case |
|-----------|--------|---------------|----------|
| `Function<T,R>` | `R apply(T t)` | T → R | Transform |
| `BiFunction<T,U,R>` | `R apply(T t, U u)` | T,U → R | Transform two inputs |
| `UnaryOperator<T>` | `T apply(T t)` | T → T | Transform same type |
| `BinaryOperator<T>` | `T apply(T t1, T t2)` | T,T → T | Combine same type |
| `Predicate<T>` | `boolean test(T t)` | T → boolean | Filter/test |
| `BiPredicate<T,U>` | `boolean test(T,U)` | T,U → boolean | Test two inputs |
| `Consumer<T>` | `void accept(T t)` | T → void | Side effect |
| `BiConsumer<T,U>` | `void accept(T,U)` | T,U → void | Side effect two inputs |
| `Supplier<T>` | `T get()` | () → T | Provide value |

### Primitive Specializations (Avoid Boxing)

```java
IntFunction<R>     // int → R
ToIntFunction<T>   // T → int
IntUnaryOperator   // int → int
IntBinaryOperator  // int, int → int
IntPredicate       // int → boolean
IntConsumer        // int → void
IntSupplier        // () → int
// Also Long*, Double* variants
```

### Composition

```java
Function<String, String> trim = String::strip;
Function<String, String> upper = String::toUpperCase;

Function<String, String> trimThenUpper = trim.andThen(upper);
Function<String, String> upperThenTrim = trim.compose(upper);  // upper applied first

Predicate<String> notBlank = s -> !s.isBlank();
Predicate<String> short_  = s -> s.length() < 10;
Predicate<String> both = notBlank.and(short_);
Predicate<String> either = notBlank.or(short_);
Predicate<String> blank = notBlank.negate();
```

---

## Method References

Method references are shorthand for lambdas that simply call a method.

| Type | Syntax | Equivalent Lambda |
|------|--------|------------------|
| Static | `ClassName::staticMethod` | `(args) -> ClassName.staticMethod(args)` |
| Bound instance | `instance::method` | `(args) -> instance.method(args)` |
| Unbound instance | `ClassName::instanceMethod` | `(obj, args) -> obj.method(args)` |
| Constructor | `ClassName::new` | `(args) -> new ClassName(args)` |

```java
// Static
Function<String, Integer> parseInt = Integer::parseInt;

// Bound instance
String prefix = "Hello, ";
Function<String, String> greet = prefix::concat;

// Unbound instance — first arg is the target
Function<String, String> upper = String::toUpperCase;
BiFunction<String, String, Boolean> startsWith = String::startsWith;

// Constructor
Supplier<ArrayList<String>> listMaker = ArrayList::new;
Function<Integer, int[]> arrayMaker = int[]::new;
```

---

## Optional<T>

`Optional` avoids `null` returns. Use it as a **return type** only — not for fields or method parameters.

```java
Optional<String> empty  = Optional.empty();
Optional<String> of     = Optional.of("hello");     // NPE if null
Optional<String> safe   = Optional.ofNullable(maybeNull);

// Query
safe.isPresent()        // true/false
safe.isEmpty()          // Java 11+ — opposite of isPresent()
safe.get()              // value or NoSuchElementException

// Safe extraction
safe.orElse("default")                  // value or default
safe.orElseGet(() -> computeDefault())  // value or lazy default
safe.orElseThrow()                      // value or NoSuchElementException (Java 10+)
safe.orElseThrow(IllegalStateException::new)  // value or custom exception

// Transform
safe.map(String::toUpperCase)           // Optional<String>
safe.flatMap(s -> Optional.of(s.trim())) // avoids Optional<Optional<T>>
safe.filter(s -> s.length() > 3)        // Optional or empty

// Side effects
safe.ifPresent(System.out::println)
safe.ifPresentOrElse(                    // Java 9+
    System.out::println,
    () -> System.out.println("empty"));

// Chain
safe.stream()  // Java 9+ — Stream of 0 or 1 element
```

---

## Stream API

Streams process sequences of elements lazily. A stream pipeline: **source → intermediate ops → terminal op**.

### Stream Sources

```java
List<String> list = List.of("a", "b", "c");
list.stream()                           // from collection
Stream.of("x", "y", "z")              // from varargs
Stream.empty()                          // empty stream
Arrays.stream(new int[]{1,2,3})        // from array
"a,b,c".chars()                        // IntStream of chars
IntStream.range(0, 10)                 // [0, 10)
IntStream.rangeClosed(1, 10)           // [1, 10]
Stream.generate(Math::random)           // infinite stream
Stream.iterate(0, n -> n + 2)          // infinite: 0, 2, 4, ...
Stream.iterate(0, n -> n < 100, n -> n + 1)  // Java 9+ bounded iterate
Files.lines(path)                       // lines of a file
```

### Intermediate Operations (Lazy)

```java
.filter(Predicate)          // keep matching elements
.map(Function)              // transform each element
.mapToInt(ToIntFunction)    // transform to IntStream
.flatMap(Function<T, Stream<R>>)   // flatten nested streams
.flatMapToInt(...)
.sorted()                   // natural order
.sorted(Comparator)         // custom order
.distinct()                 // remove duplicates (by equals)
.limit(long n)              // take first n elements
.skip(long n)               // skip first n elements
.peek(Consumer)             // debug — side effect, passes through
.takeWhile(Predicate)       // Java 9+ — take while predicate true
.dropWhile(Predicate)       // Java 9+ — drop while predicate true
```

### Terminal Operations

```java
// Reduction
.count()                    // long
.sum()                      // IntStream/LongStream/DoubleStream
.min(Comparator) → Optional
.max(Comparator) → Optional
.reduce(identity, BinaryOperator)
.reduce(BinaryOperator) → Optional

// Collection
.collect(Collectors.toList())
.collect(Collectors.toUnmodifiableList())  // Java 10+
.collect(Collectors.toSet())
.collect(Collectors.toMap(keyFn, valueFn))
.toArray()
.toArray(String[]::new)     // Java 11 — typed array

// Short-circuit
.findFirst() → Optional
.findAny() → Optional        // may differ in parallel
.anyMatch(Predicate)         // true if any match
.allMatch(Predicate)         // true if all match
.noneMatch(Predicate)        // true if none match

// Side effects
.forEach(Consumer)
.forEachOrdered(Consumer)    // preserves encounter order in parallel
```

### Collectors

```java
import java.util.stream.Collectors;

// Basic
Collectors.toList()
Collectors.toUnmodifiableList()
Collectors.toSet()
Collectors.toMap(Student::getId, Student::getName)
Collectors.toMap(k, v, (existing, newVal) -> existing)  // merge fn

// Joining
Collectors.joining()                          // concat
Collectors.joining(", ")                      // with delimiter
Collectors.joining(", ", "[", "]")           // with prefix/suffix

// Grouping
Collectors.groupingBy(Student::getGrade)      // Map<Grade, List<Student>>
Collectors.groupingBy(Student::getGrade, Collectors.counting())  // Map<Grade, Long>
Collectors.partitioningBy(s -> s.getGpa() >= 3.0)  // Map<Boolean, List<Student>>

// Statistics
Collectors.counting()
Collectors.summingInt(Student::getCredits)
Collectors.averagingDouble(Student::getGpa)
Collectors.summarizingInt(...)    // IntSummaryStatistics

// Downstream collectors
Collectors.groupingBy(Department::getName,
    Collectors.mapping(Employee::getName, Collectors.toList()))
```

### Primitive Streams

Use `IntStream`, `LongStream`, `DoubleStream` to avoid boxing overhead:

```java
IntStream.of(1, 2, 3).sum()          // 6
IntStream.range(1, 6).average()       // OptionalDouble(3.0)
int[] arr = IntStream.rangeClosed(1, 5).toArray();

// Box to object stream
IntStream.of(1, 2, 3).boxed()         // Stream<Integer>
// Convert object stream to primitive
list.stream().mapToInt(String::length)  // IntStream
```

### Parallel Streams

```java
list.parallelStream()                  // parallel from collection
stream.parallel()                      // convert existing stream

// Rules:
// - Operations must be stateless and non-interfering
// - Avoid shared mutable state
// - forEach order not guaranteed — use forEachOrdered if needed
// - Not always faster — measure before using
```

---

## Common Stream Patterns

```java
// Filter + map + collect
List<String> names = employees.stream()
    .filter(e -> e.getDept().equals("Engineering"))
    .map(Employee::getName)
    .sorted()
    .collect(Collectors.toList());

// FlatMap — flatten list of lists
List<String> allSkills = employees.stream()
    .flatMap(e -> e.getSkills().stream())
    .distinct()
    .collect(Collectors.toList());

// GroupBy with count
Map<String, Long> byDept = employees.stream()
    .collect(Collectors.groupingBy(
        Employee::getDept,
        Collectors.counting()));

// Reduce to sum
int totalAge = employees.stream()
    .mapToInt(Employee::getAge)
    .sum();

// First match
Optional<Employee> first = employees.stream()
    .filter(e -> e.getSalary() > 100_000)
    .findFirst();
```

---

## Stream Pitfalls

| Pitfall | Fix |
|---------|-----|
| Reusing a stream | Create new stream — streams are single-use |
| `peek()` for non-debug logic | Use `map()` + `filter()` instead |
| Stateful lambdas in parallel streams | Use stateless operations only |
| `collect(toList())` then `stream()` again | Chain operations instead |
| Calling `get()` on Optional without `isPresent()` | Use `orElse`/`orElseThrow` |
