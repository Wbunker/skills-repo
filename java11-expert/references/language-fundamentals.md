# Java 11 Language Fundamentals
## var, String API, Single-File Launch, Primitives, Operators, Switch

---

## `var` — Local Variable Type Inference (JEP 286, Java 10; JEP 323 lambda extension in Java 11)

`var` tells the compiler to infer the type from the initializer. It is **not** dynamic typing — the type is fixed at compile time.

### Valid Uses

```java
// Local variables in methods
var list    = new ArrayList<String>();   // inferred: ArrayList<String>
var map     = new HashMap<String, Integer>();
var path    = Path.of("/tmp/data.txt");  // inferred: Path
var entry   = map.entrySet().iterator(); // inferred: Iterator<Map.Entry<String,Integer>>

// For-each loop variables
for (var item : list) { /* item is String */ }

// Try-with-resources
try (var stream = Files.newInputStream(path)) { ... }

// Lambda parameters — Java 11 JEP 323 (enables annotations)
list.stream()
    .map((@Nonnull var s) -> s.toUpperCase())
    .forEach(System.out::println);
```

### Invalid Uses

```java
var x;                          // no initializer — compiler error
var x = null;                   // cannot infer from null alone
var x = {1, 2, 3};             // array initializer without type — error
private var field = "hello";    // instance fields — NOT allowed
public var method() { }         // return types — NOT allowed
void process(var x) { }         // method parameters — NOT allowed
```

### Why `var` in Lambda Params?

The only reason to use `var` in lambda params (vs. leaving them untyped) is to add annotations:
```java
// These are equivalent without annotations:
list.stream().map(s -> s.trim());
list.stream().map((var s) -> s.trim());

// But var enables annotations (impossible with bare `s ->`)
list.stream().map((@NonNull var s) -> s.trim());
```

---

## New String Methods (Java 11)

Java 11 adds six new instance methods to `java.lang.String`.

### `strip()` Family — Unicode-Aware Whitespace

```java
String s = "  hello  ";
s.strip()          // "hello"       — removes leading and trailing whitespace
s.stripLeading()   // "hello  "     — removes leading only
s.stripTrailing()  // "  hello"     — removes trailing only
```

**`strip()` vs `trim()`**: `trim()` only removes ASCII control characters (`<= '\u0020'`). `strip()` uses `Character.isWhitespace()` which covers Unicode whitespace (e.g., `\u2003` em space). Prefer `strip()` in new code.

### `isBlank()` — Empty or Whitespace

```java
"".isBlank()          // true
"   ".isBlank()       // true  (Unicode whitespace counts)
"   ".isEmpty()       // false (not zero-length)
" a ".isBlank()       // false
```

### `lines()` — Split into Stream

```java
"line1\nline2\nline3".lines()
// Stream<String> → ["line1", "line2", "line3"]

// Useful for processing multi-line strings
Files.readString(path).lines()
    .filter(l -> !l.startsWith("#"))
    .forEach(System.out::println);
```

Handles `\n`, `\r`, and `\r\n` line endings.

### `repeat(int)` — Repeat String

```java
"ab".repeat(3)    // "ababab"
"-".repeat(40)    // "----------------------------------------"
"x".repeat(0)     // ""
```

Throws `IllegalArgumentException` if count < 0.

---

## Single-File Source-Code Programs (JEP 330)

Java 11 allows launching a single `.java` file directly without explicit compilation:

```bash
# Before Java 11 (two steps)
javac Hello.java
java Hello

# Java 11+ (one step)
java Hello.java
```

### Rules

- Only works when the **first class** in the file contains `main(String[] args)`
- The file is compiled in memory; no `.class` file is produced on disk
- All classes must be in the same file (no imports from other `.java` files in project)
- Can add JVM flags and classpath entries: `java -cp lib.jar Hello.java arg1`
- Useful for scripting, quick prototypes, and shebang scripts on Unix:

```java
#!/usr/bin/java --source 11
// Hello.java
public class Hello {
    public static void main(String[] args) {
        System.out.println("Hello, " + args[0]);
    }
}
```

---

## Primitive Types and Wrappers

| Primitive | Wrapper | Size | Range |
|-----------|---------|------|-------|
| `boolean` | `Boolean` | 1 bit (JVM-dependent) | `true`/`false` |
| `byte` | `Byte` | 8-bit signed | -128 to 127 |
| `short` | `Short` | 16-bit signed | -32,768 to 32,767 |
| `char` | `Character` | 16-bit unsigned | `'\u0000'` to `'\uffff'` |
| `int` | `Integer` | 32-bit signed | -2^31 to 2^31-1 |
| `long` | `Long` | 64-bit signed | -2^63 to 2^63-1 |
| `float` | `Float` | 32-bit IEEE 754 | ~±3.4e38, 7 digits |
| `double` | `Double` | 64-bit IEEE 754 | ~±1.7e308, 15 digits |

### Autoboxing / Unboxing

```java
Integer i = 42;          // autoboxing: int → Integer
int x = i;               // unboxing: Integer → int
Integer a = 127, b = 127;
a == b;   // true  (cached -128 to 127)
Integer c = 128, d = 128;
c == d;   // false (different objects — use equals())
```

### Numeric Literals

```java
int million   = 1_000_000;       // underscores for readability
long bigNum   = 123_456L;        // L suffix for long
double sci    = 1.5e10;          // scientific notation
int hex       = 0xFF;            // hexadecimal
int binary    = 0b1010_1010;     // binary literal
```

---

## Type Casting and Promotion

### Widening (implicit, safe)
```
byte → short → int → long → float → double
                char → int
```

### Narrowing (explicit, may lose data)
```java
double d = 9.99;
int i = (int) d;   // 9 — truncates, does not round
```

### Numeric Promotion in Expressions
- Operands smaller than `int` are promoted to `int` before arithmetic
- If either operand is `long`/`float`/`double`, both promote to that type

---

## Switch Statement (Java 11 Classic Form)

Java 11 has the traditional switch statement. Switch expressions with `->` syntax arrive in Java 14 (standard).

```java
switch (day) {
    case MONDAY:
    case TUESDAY:
        System.out.println("Weekday");
        break;
    case SATURDAY:
    case SUNDAY:
        System.out.println("Weekend");
        break;
    default:
        System.out.println("Other");
}
```

**Fall-through**: Without `break`, execution continues into the next case.

Switch works on: `byte`, `short`, `char`, `int`, `String`, enums, and their wrapper types.

---

## Operators

### Equality
- `==` on objects: reference equality (same object in memory)
- `.equals()`: logical/content equality (override in your classes)

### Conditional / Ternary
```java
String result = score >= 60 ? "Pass" : "Fail";
```

### Instanceof
```java
Object obj = "hello";
if (obj instanceof String) {
    String s = (String) obj;
    System.out.println(s.length());
}
```

Pattern matching for `instanceof` (`obj instanceof String s`) arrives in Java 16 standard — **not in Java 11**.

### Bitwise and Shift
| Operator | Meaning |
|----------|---------|
| `&` | bitwise AND |
| `\|` | bitwise OR |
| `^` | bitwise XOR |
| `~` | bitwise complement |
| `<<` | left shift |
| `>>` | arithmetic right shift (sign-extends) |
| `>>>` | unsigned right shift (zero-fills) |
