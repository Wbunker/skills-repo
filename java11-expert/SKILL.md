---
name: java11-expert
description: Java 11 (LTS) expertise covering language features, OOP, generics, functional programming, streams, JPMS modules, concurrency, I/O and NIO.2, HTTP Client API, security, JDBC, date/time, and JVM tooling. Use when writing or reviewing Java 11 code, migrating from older Java versions, preparing for OCP 1Z0-819 certification, or designing Java 11 applications. Based on Java SE 11 official documentation (docs.oracle.com/en/java/javase/11/) and OCP Java 11 exam syllabus.
---

# Java 11 Expert

Based on: Oracle Java SE 11 official documentation, JEP specifications, and OCP Java SE 11 Developer (1Z0-819) syllabus.
Java 11 is an LTS release. Key additions over Java 8: JPMS modules, HTTP Client, `var`, new String/Files methods, ZGC, Epsilon GC, Java Flight Recorder.

## Java 11 Platform Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                      JAVA 11 PLATFORM                            │
│                                                                  │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │  LANGUAGE   │  │  LIBRARIES  │  │     JVM      │             │
│  │─────────────│  │─────────────│  │─────────────│             │
│  │ var (local) │  │ java.base   │  │ G1GC (default│             │
│  │ var lambdas │  │ java.net.http│  │ ZGC (exp)   │             │
│  │ single-file │  │ java.time   │  │ Epsilon GC  │             │
│  │ launch      │  │ java.nio    │  │ JFR (open)  │             │
│  └─────────────┘  │ java.util   │  │ JMC         │             │
│                   │ java.sql    │  └─────────────┘             │
│  ┌─────────────┐  └─────────────┘                               │
│  │   MODULES   │                    ┌─────────────┐             │
│  │─────────────│  ┌─────────────┐  │  SECURITY   │             │
│  │ module-info │  │ FUNCTIONAL  │  │─────────────│             │
│  │ requires    │  │─────────────│  │ TLS 1.3     │             │
│  │ exports     │  │ Lambdas     │  │ ChaCha20    │             │
│  │ opens       │  │ Streams     │  │ Curve25519  │             │
│  │ provides    │  │ Optional    │  │ AES-GCM     │             │
│  │ jlink       │  │ CompletablF │  └─────────────┘             │
│  └─────────────┘  └─────────────┘                               │
└──────────────────────────────────────────────────────────────────┘
```

## Quick Reference

| Task | Reference |
|------|-----------|
| `var`, String new methods, single-file launch, switch, primitives | [language-fundamentals.md](references/language-fundamentals.md) |
| Classes, interfaces, inheritance, enums, nested classes, nest-access | [oop.md](references/oop.md) |
| Generics, wildcards, List/Set/Map, factory methods, Comparator | [generics-and-collections.md](references/generics-and-collections.md) |
| Lambdas, method references, Streams, Optional, functional interfaces | [functional-and-streams.md](references/functional-and-streams.md) |
| JPMS, module-info.java, requires/exports/opens, jlink, migration | [modules.md](references/modules.md) |
| Threads, ExecutorService, synchronization, CompletableFuture | [concurrency.md](references/concurrency.md) |
| InputStream/Writer, NIO.2 Path/Files, serialization, Files.readString | [io-and-nio2.md](references/io-and-nio2.md) |
| HttpClient, HttpRequest, HttpResponse, async, WebSocket, HTTP/2 | [http-client.md](references/http-client.md) |
| TLS 1.3, ChaCha20, Curve25519, JSSE, cryptographic APIs | [security.md](references/security.md) |
| JDBC, Connection, PreparedStatement, ResultSet, transactions | [jdbc.md](references/jdbc.md) |
| java.time, LocalDate/ZonedDateTime, Locale, ResourceBundle, DateTimeFormatter | [date-time-and-localization.md](references/date-time-and-localization.md) |
| GC tuning, ZGC, Epsilon, JFR, jlink, jdeps, jmod, jcmd | [jvm-and-tooling.md](references/jvm-and-tooling.md) |

## Reference Files

| File | Topic Area | Key Topics |
|------|-----------|------------|
| `language-fundamentals.md` | Language Core | `var` type inference, String API (strip/isBlank/lines/repeat), single-file launch (JEP 330), switch, operators, casting |
| `oop.md` | OOP | Classes, interfaces (private methods), abstract classes, enums, polymorphism, nested classes, nest-based access (JEP 181) |
| `generics-and-collections.md` | Generics & Collections | Type parameters, bounded wildcards, List/Set/Map/Queue implementations, `List.of()`, `toArray(IntFunction)` |
| `functional-and-streams.md` | Functional Programming | Lambda syntax, `var` in lambdas (JEP 323), method references, `java.util.function`, Stream API, `Optional`, collectors, parallel streams |
| `modules.md` | JPMS | `module-info.java`, requires/exports/opens/uses/provides, unnamed/automatic modules, `jlink`, removed Java EE modules (JEP 320) |
| `concurrency.md` | Concurrency | `Thread`, `ExecutorService`, `Future`, `CompletableFuture`, locks, atomic classes, concurrent collections, Fork/Join |
| `io-and-nio2.md` | I/O & NIO.2 | Classic I/O streams, serialization, NIO.2 `Path`/`Files`, `Files.readString`/`writeString`/`Path.of` (Java 11), directory traversal |
| `http-client.md` | HTTP Client | `HttpClient` builder, `HttpRequest`/`HttpResponse`, sync/async, `BodyPublishers`/`BodyHandlers`, HTTP/2, WebSocket (JEP 321) |
| `security.md` | Security | TLS 1.3 (JEP 332), ChaCha20-Poly1305 (JEP 329), Curve25519/448 (JEP 324), JSSE, `java.security` |
| `jdbc.md` | Database | JDBC driver types, `Connection`, `PreparedStatement`, `ResultSet`, transactions, `DataSource`, `RowSet` |
| `date-time-and-localization.md` | Date/Time & i18n | `LocalDate`, `ZonedDateTime`, `Duration`/`Period`, `DateTimeFormatter`, `Locale`, `ResourceBundle`, `NumberFormat` |
| `jvm-and-tooling.md` | JVM & Tools | G1GC, ZGC (JEP 333), Epsilon GC (JEP 318), JFR (JEP 328), `jlink`, `jdeps`, `jmod`, `jcmd`, heap profiling (JEP 331) |

## Core Decision Trees

### Which Java 11 API to Use?

```
What are you trying to do?
├── Make an HTTP request
│   └── Use java.net.http.HttpClient (NOT HttpURLConnection)
│       ├── Synchronous → client.send(request, bodyHandler)
│       └── Asynchronous → client.sendAsync(...) → CompletableFuture
├── Read/write a file
│   ├── Small text file → Files.readString(path) / Files.writeString(path, text)
│   ├── Large file / streaming → BufferedReader / InputStream
│   └── Walk directory → Files.walk(path) or Files.find()
├── Work with text/strings
│   ├── Unicode-aware whitespace trim → strip() NOT trim()
│   ├── Blank check → isBlank() NOT isEmpty()
│   ├── Split into lines → lines() (returns Stream<String>)
│   └── Repeat n times → repeat(n)
├── Omit explicit type → var (local variables and lambda params only)
├── Run without compiling → java MyFile.java (single-file JEP 330)
└── Custom runtime image → jlink --add-modules ...
```

### Concurrency: Which Abstraction?

```
Concurrency need?
├── Simple background task → Runnable / Thread
├── Task with return value → Callable + ExecutorService.submit()
├── Compose async operations → CompletableFuture
│   ├── Transform result → thenApply()
│   ├── Chain async task → thenCompose()
│   ├── Combine two futures → thenCombine()
│   └── Handle errors → exceptionally() / handle()
├── Parallel data processing → parallel stream (stateless ops only)
├── Divide-and-conquer → ForkJoinPool / RecursiveTask
└── Shared mutable state
    ├── Single variable → AtomicInteger / AtomicReference
    ├── Critical section → synchronized / ReentrantLock
    └── Shared map → ConcurrentHashMap
```

### Module System: What Directive?

```
What access do you need?
├── Depend on another module → requires <module>
│   ├── And re-export it → requires transitive <module>
│   └── Only at compile time → requires static <module>
├── Let others use your packages
│   ├── Normal API access → exports <package>
│   └── Restricted to specific module → exports <package> to <module>
├── Allow reflection access (frameworks, DI)
│   ├── Full reflection → opens <package>
│   └── Restricted reflection → opens <package> to <module>
├── Use a service → uses <ServiceInterface>
└── Provide a service → provides <Interface> with <Implementation>
```

### Lambda vs. Method Reference?

```
Lambda body
├── Single method call on parameter → method reference
│   ├── Static method: (x) -> Foo.bar(x) → Foo::bar
│   ├── Instance method on param: (x) -> x.toString() → Object::toString
│   ├── Instance method on specific obj: () -> obj.get() → obj::get
│   └── Constructor: () -> new Foo() → Foo::new
└── Multiple operations or logic → keep as lambda
```

## Java 11 vs Java 8: Key Differences

| Feature | Java 8 | Java 11 |
|---------|--------|---------|
| Type inference | None in lambdas | `var` in lambda params (JEP 323) |
| HTTP client | `HttpURLConnection` (clunky) | `java.net.http.HttpClient` (JEP 321) |
| Modules | Not available | JPMS (from Java 9, mature in 11) |
| String utilities | `trim()`, `isEmpty()` | `strip()`, `isBlank()`, `lines()`, `repeat()` |
| File I/O shortcuts | None | `Files.readString()`, `Files.writeString()`, `Path.of()` |
| GC options | G1GC, CMS | G1GC (default), ZGC (exp), Epsilon GC |
| JFR | Commercial only | Open source, in JDK |
| JRE distribution | Separate JRE download | Use `jlink` for custom runtime |
| Java EE modules | Available | Removed (JEP 320) |
| Nashorn JS engine | Available | Deprecated (JEP 335) |
| Single-file programs | Must compile first | `java File.java` directly (JEP 330) |
| Nest access | Synthetic bridge methods | Direct private access (JEP 181) |

## Key Concepts at a Glance

### `var` — Local Variable Type Inference

```java
// Valid uses (Java 11)
var list = new ArrayList<String>();       // local variable
var path = Path.of("/tmp/data.txt");      // local variable
list.stream()
    .map((@Nonnull var s) -> s.trim())    // lambda param (JEP 323, Java 11)
    .forEach(System.out::println);

// NOT valid
var field = "hello";    // instance/static field — NO
var x;                  // no initializer — NO
var m() { }             // return type — NO
```

### New String Methods (Java 11)

```java
"  hello  ".strip()         // "hello"  (Unicode-aware, unlike trim())
"  hello  ".stripLeading()  // "hello  "
"  hello  ".stripTrailing() // "  hello"
"   ".isBlank()             // true  (Unicode whitespace)
"   ".isEmpty()             // false (not empty, just whitespace)
"line1\nline2".lines()      // Stream<String> → ["line1", "line2"]
"ha".repeat(3)              // "hahaha"
```

### New Files/Path Methods (Java 11)

```java
Path p = Path.of("/tmp/data.txt");               // replaces Paths.get()
String content = Files.readString(p);            // read entire file as String
Files.writeString(p, "hello", StandardOpenOption.CREATE);
```

### HTTP Client (Java 11)

```java
HttpClient client = HttpClient.newHttpClient();
HttpRequest request = HttpRequest.newBuilder()
    .uri(URI.create("https://example.com/api"))
    .GET()
    .build();

// Synchronous
HttpResponse<String> response =
    client.send(request, HttpResponse.BodyHandlers.ofString());

// Asynchronous
client.sendAsync(request, HttpResponse.BodyHandlers.ofString())
    .thenApply(HttpResponse::body)
    .thenAccept(System.out::println);
```
