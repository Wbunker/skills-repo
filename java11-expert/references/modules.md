# Java 11 Module System (JPMS)
## module-info.java, requires/exports/opens, jlink, Removed Modules, Migration

---

## Overview

The Java Platform Module System (JPMS) was introduced in Java 9 (Project Jigsaw, JEP 261) and is fully production-ready in Java 11. It provides:
- **Reliable configuration**: explicit dependency declarations replace classpath scanning
- **Strong encapsulation**: packages must be explicitly exported; internal APIs are hidden
- **Scalable platform**: `jlink` creates minimal custom runtimes

---

## Module Concepts

### Types of Modules

| Type | Description | module-info.java? |
|------|-------------|-------------------|
| **Named module** | Has a `module-info.java`; on the module path | Yes |
| **Unnamed module** | On the classpath (legacy code); reads all named modules | No |
| **Automatic module** | JAR on module path without `module-info.java`; name from MANIFEST or filename | No (auto) |

### Module Path vs. Class Path

```bash
# Class path (legacy)
java -cp myapp.jar:libs/* com.example.Main

# Module path
java --module-path mods --module com.example/com.example.Main
```

Code on the classpath belongs to the **unnamed module**, which can read all named modules but cannot be read by them.

---

## `module-info.java`

Placed in the root of the module source tree:

```java
module com.example.myapp {
    // Dependencies
    requires java.base;               // implicit in all modules
    requires java.sql;                // depend on java.sql module
    requires transitive java.logging; // re-export: consumers of this module also get java.logging
    requires static java.annotation;  // compile-time only (optional at runtime)

    // Export packages for use by other modules
    exports com.example.myapp.api;                    // all modules
    exports com.example.myapp.internal to com.example.tools;  // qualified export

    // Open packages for reflection (frameworks, DI, serialization)
    opens com.example.myapp.model;                    // all modules
    opens com.example.myapp.config to com.fasterxml.jackson.databind;  // qualified

    // Service declarations
    uses com.example.spi.Plugin;                      // service consumer
    provides com.example.spi.Plugin                   // service provider
        with com.example.myapp.impl.DefaultPlugin;
}
```

---

## Directive Reference

### `requires`

| Directive | Meaning |
|-----------|---------|
| `requires M` | Depends on module M at compile and runtime |
| `requires transitive M` | Depends on M; anyone who requires this module also implicitly reads M |
| `requires static M` | Compile-time dependency; optional at runtime |

### `exports`

Makes a package's `public` (and `protected`) types accessible to other modules.

```java
exports com.example.api;                  // to all modules
exports com.example.internal to com.example.tools;  // only to specific module
```

Non-exported packages are **encapsulated** — inaccessible even via reflection by default.

### `opens`

Allows **reflection** access to a package (even private members):

```java
opens com.example.model;                  // all modules can reflect
opens com.example.model to spring.core;   // only spring.core can reflect
```

`opens` is required for:
- Dependency injection frameworks (Spring, CDI)
- Serialization (Jackson, GSON)
- Testing frameworks (JUnit, Mockito) inspecting private fields
- `--add-opens` flag can open packages from the command line

### `uses` and `provides`

Service provider interface pattern (replaces `META-INF/services`):

```java
// Consumer module
uses com.example.spi.DataFormatter;

// Provider module
provides com.example.spi.DataFormatter with com.example.impl.CsvFormatter;
```

```java
// Runtime — load services
ServiceLoader<DataFormatter> loader = ServiceLoader.load(DataFormatter.class);
loader.stream()
    .map(ServiceLoader.Provider::get)
    .forEach(f -> System.out.println(f.format(data)));
```

---

## JDK Modules Structure

Key platform modules in Java 11:

| Module | Contents |
|--------|---------|
| `java.base` | Core Java: `java.lang`, `java.util`, `java.io`, `java.nio`, `java.math`, `java.net` |
| `java.sql` | JDBC API |
| `java.net.http` | HTTP Client API (new in Java 11) |
| `java.logging` | `java.util.logging` |
| `java.xml` | XML processing, DOM, SAX, StAX |
| `java.desktop` | AWT, Swing |
| `java.management` | JMX |
| `java.compiler` | `javax.tools.JavaCompiler` |
| `jdk.jfr` | Java Flight Recorder |
| `jdk.jlink` | `jlink` tool |

---

## Removed Modules (JEP 320, Java 11)

These Java EE and CORBA modules were deprecated in Java 9 and **removed in Java 11**:

| Removed Module | Contains | Replacement |
|----------------|---------|-------------|
| `java.xml.ws` | JAX-WS (SOAP web services) | Use `jakarta.xml.ws` from Maven |
| `java.xml.bind` | JAXB (XML ↔ Java binding) | `jakarta.xml.bind-api` + impl |
| `java.activation` | JAF (JavaBeans Activation Framework) | `jakarta.activation` |
| `java.xml.ws.annotation` | Common annotations | `jakarta.annotation` |
| `java.corba` | CORBA/IIOP | No standard replacement |
| `java.transaction` | JTA (Java Transaction API) | `jakarta.transaction` |
| `java.se.ee` | Aggregator for EE modules | Replaced by individual Maven deps |

**Migration**: Add Maven/Gradle dependencies:

```xml
<!-- JAXB replacement (Java 11+) -->
<dependency>
    <groupId>jakarta.xml.bind</groupId>
    <artifactId>jakarta.xml.bind-api</artifactId>
    <version>3.0.1</version>
</dependency>
<dependency>
    <groupId>com.sun.xml.bind</groupId>
    <artifactId>jaxb-impl</artifactId>
    <version>3.0.2</version>
</dependency>
```

---

## `jlink` — Custom Runtime Images

Java 11 no longer ships a separate JRE. Use `jlink` to build minimal runtime images:

```bash
jlink \
  --module-path $JAVA_HOME/jmods \
  --add-modules com.example.myapp,java.sql,java.net.http \
  --output dist/myapp-runtime \
  --launcher myapp=com.example.myapp/com.example.myapp.Main \
  --strip-debug \
  --compress=2 \
  --no-header-files \
  --no-man-pages
```

Result: `dist/myapp-runtime/` is a self-contained runtime for the app, often 30–60 MB vs. full JDK at 200+ MB.

### `jdeps` — Dependency Analysis

```bash
# Show module dependencies of a JAR
jdeps --module-path mods myapp.jar

# Check for use of JDK internal APIs
jdeps --jdk-internals myapp.jar

# Generate module-info.java for an automatic module
jdeps --generate-module-info . myapp.jar

# Summary view
jdeps -summary myapp.jar
```

---

## Migration Strategies

### Strategy 1: Unnamed Module (No Changes)

Keep everything on the classpath. Code runs in the unnamed module. Easiest, but no strong encapsulation benefits.

```bash
java -cp app.jar:libs/* com.example.Main
```

### Strategy 2: Automatic Modules

Move JARs to the module path without `module-info.java`. Each becomes an automatic module:
- Name derived from JAR filename or `Automatic-Module-Name` in MANIFEST.MF
- Can read all other modules; exports all packages

```bash
java --module-path app.jar:libs/* -m com.example/com.example.Main
```

### Strategy 3: Named Modules (Full Migration)

Add `module-info.java` to your code. Requires:
1. Declaring all `requires` dependencies
2. Ensuring all dependencies are either named or automatic modules
3. Opening packages needed by reflection-based frameworks

### Common Migration Issues

| Issue | Cause | Fix |
|-------|-------|-----|
| `InaccessibleObjectException` | Reflective access to unexported package | Add `opens` or `--add-opens` flag |
| `ClassNotFoundException` | Dependency not on module path | Add JAR to `--module-path` |
| Split package | Same package in two modules | Consolidate or rename |
| `NoClassDefFoundError` for `javax.xml.bind.*` | Removed Java EE module | Add Jakarta XML Bind Maven dep |

### Command-Line Escape Hatches

```bash
# Open a package for reflection without module-info changes
--add-opens java.base/java.lang=ALL-UNNAMED

# Export internal package
--add-exports java.base/sun.security.util=ALL-UNNAMED

# Add dependency
--add-reads com.example.myapp=java.sql
```

These are stopgaps — add `module-info.java` properly for production code.

---

## Module System Quick Check

```java
// Runtime introspection
Module module = String.class.getModule();
module.getName();               // "java.base"
module.isNamed();               // true
module.getDescriptor();         // ModuleDescriptor

// Check if package is exported
module.isExported("java.lang");           // true
module.isOpen("java.lang");               // false (not opened)
```
