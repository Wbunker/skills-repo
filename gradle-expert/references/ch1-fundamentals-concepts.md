# Ch.1 — Gradle Fundamentals & Build Files

*Companion CLI reference: [ch1-fundamentals-cli.md](ch1-fundamentals-cli.md)*

---

## What is Gradle?

Gradle is a build automation tool for JVM projects (and increasingly for Android, C/C++, Swift, and other ecosystems). It uses a Groovy or Kotlin DSL to express build logic as a directed acyclic graph (DAG) of tasks. Key properties:

- **Convention over configuration**: the `java` plugin establishes `src/main/java`, `src/test/java`, standard task names (`compileJava`, `test`, `jar`), and standard configurations (`implementation`, `testImplementation`) without requiring any explicit configuration
- **Incremental by default**: tasks declare inputs and outputs; Gradle skips a task if nothing has changed since the last run
- **Extensible**: every piece of build logic is a task or plugin; Gradle's API is fully open
- **Three build phases**: every Gradle build goes through Initialization → Configuration → Execution in that order; understanding this prevents many common mistakes

### Everything is a Project; Projects Have Tasks; Tasks Have Actions

- A **project** corresponds to a `build.gradle.kts` file. A single-project build has one; a multi-project build has many.
- A **task** is a unit of work (compile sources, run tests, produce a JAR).
- A **task action** is a block of code that executes when the task runs — added via `doFirst {}`, `doLast {}`, or `@TaskAction` in a custom task class.

---

## Installation

### Recommended: Gradle Wrapper (no local Gradle install required)

The Gradle Wrapper (`gradlew` / `gradlew.bat`) is the canonical way to use Gradle in any project. It downloads and caches the correct Gradle version automatically. Always commit the wrapper files.

```
gradle/wrapper/gradle-wrapper.jar
gradle/wrapper/gradle-wrapper.properties
gradlew
gradlew.bat
```

### Manual Installation Options

| Method | Command | Notes |
|---|---|---|
| SDKMAN (recommended on macOS/Linux) | `sdk install gradle 8.11` | Supports multiple versions |
| Homebrew (macOS) | `brew install gradle` | Installs latest stable |
| Scoop (Windows) | `scoop install gradle` | Windows package manager |
| Direct download | Download ZIP from gradle.org | Extract and add `bin/` to `PATH` |

**Verify installation:**
```bash
gradle --version
# or, from a project with a wrapper:
./gradlew --version
```

---

## Gradle Wrapper

The wrapper is Berglund's first recommendation: ship your build tool with your project. The wrapper ensures every developer and every CI server uses the identical Gradle version, eliminating "works on my machine" build failures caused by Gradle version drift.

### Wrapper Files

```
gradle/
└── wrapper/
    ├── gradle-wrapper.jar        ← The wrapper bootstrap code (binary, commit this)
    └── gradle-wrapper.properties ← Version configuration
gradlew                           ← Unix shell script (commit this, chmod +x)
gradlew.bat                       ← Windows batch script (commit this)
```

### gradle-wrapper.properties

```properties
# gradle/wrapper/gradle-wrapper.properties
distributionBase=GRADLE_USER_HOME
distributionPath=wrapper/dists
distributionUrl=https\://services.gradle.org/distributions/gradle-8.11-bin.zip
networkTimeout=10000
validateDistributionUrl=true
zipStoreBase=GRADLE_USER_HOME
zipStorePath=wrapper/dists
```

Key property: `distributionUrl`. Use `-bin.zip` (binaries only) rather than `-all.zip` (binaries + sources + docs) for faster CI downloads. Use `-all.zip` in local development if you want Gradle source navigation in IntelliJ IDEA.

### Generating or Updating the Wrapper

```bash
# Generate wrapper from scratch (requires a local Gradle install)
gradle wrapper --gradle-version 8.11 --distribution-type bin

# Update an existing wrapper (uses the current wrapper to download the new one)
./gradlew wrapper --gradle-version 9.2.1

# Pin to a specific distribution type
./gradlew wrapper --gradle-version 9.2.1 --distribution-type all
```

### Wrapper Security: Checksum Verification (Gradle 7.2+)

```properties
# Add to gradle-wrapper.properties to verify the downloaded ZIP
distributionSha256Sum=e6e9f7395f48f7d4fda6e4e636e31fd47ad2e32f72085fca5a66b77
```

Generate the SHA-256: `sha256sum gradle-8.11-bin.zip` (Linux) or `Get-FileHash` (PowerShell).

---

## Project Structure

### Minimal Single-Project Java Application

```
my-project/
├── gradlew                              ← Unix wrapper (chmod +x)
├── gradlew.bat                          ← Windows wrapper
├── gradle/
│   ├── wrapper/
│   │   ├── gradle-wrapper.jar
│   │   └── gradle-wrapper.properties
│   └── libs.versions.toml               ← Version catalog (Gradle 7.4+, standard since 8.2)
├── settings.gradle.kts                  ← Initialization phase: project name + subproject list
├── build.gradle.kts                     ← Configuration phase: plugins, dependencies, tasks
└── src/
    ├── main/
    │   ├── java/
    │   │   └── com/example/App.java
    │   └── resources/
    │       └── application.properties
    └── test/
        ├── java/
        │   └── com/example/AppTest.java
        └── resources/
```

### Multi-Project Layout

```
my-app/
├── gradlew / gradlew.bat
├── gradle/
│   ├── wrapper/...
│   └── libs.versions.toml
├── settings.gradle.kts        ← Lists all subprojects
├── build.gradle.kts           ← Root build file (often thin or empty)
├── app/
│   └── build.gradle.kts       ← Application subproject
├── lib/
│   └── build.gradle.kts       ← Library subproject
└── api/
    └── build.gradle.kts       ← API contract subproject
```

---

## settings.gradle.kts (Initialization Phase)

`settings.gradle.kts` is evaluated during the **Initialization** phase, before any `build.gradle.kts`. Its responsibilities:
1. Set `rootProject.name`
2. Declare which subprojects exist with `include()`
3. Configure plugin repositories (`pluginManagement {}`)
4. Configure dependency repositories for all projects (`dependencyResolutionManagement {}`)

### Complete Modern settings.gradle.kts

```kotlin
// settings.gradle.kts

rootProject.name = "my-app"

// Configure where Gradle finds plugins (applied in build.gradle.kts `plugins {}` blocks)
pluginManagement {
    repositories {
        gradlePluginPortal()   // Gradle's official plugin portal (plugins.gradle.org)
        mavenCentral()
        google()               // Needed for Android/Kotlin Multiplatform plugins
    }
    // Pin a plugin version globally (optional — avoids repeating in every subproject)
    // plugins {
    //     id("com.diffplug.spotless") version "6.25.0"
    // }
}

// Configure where Gradle finds dependencies (libraries) for all subprojects
// FAIL_ON_PROJECT_REPOS prevents subprojects from adding their own repositories
// (which is good practice; centralise repository management here)
dependencyResolutionManagement {
    repositoriesMode.set(RepositoriesMode.FAIL_ON_PROJECT_REPOS)
    repositories {
        mavenCentral()
        google()
        // Internal Artifactory or Nexus:
        // maven { url = uri("https://artifactory.example.com/libs-release") }
    }
}

// Declare subprojects
include(":app")
include(":lib")
include(":api")

// Include a composite build (an external project treated as a local dependency)
// includeBuild("../my-shared-lib")
```

### Enabling Feature Previews (settings.gradle.kts)

```kotlin
// Enable experimental Gradle features
enableFeaturePreview("TYPESAFE_PROJECT_ACCESSORS")  // enables projects.app.lib etc.
enableFeaturePreview("STABLE_CONFIGURATION_CACHE")  // Gradle 8.x; stable in 9
```

---

## build.gradle.kts (Configuration Phase)

Every `build.gradle.kts` is evaluated during the **Configuration** phase. Gradle evaluates ALL build files even if you only run one task — this is why expensive logic should never appear at configuration time without lazy evaluation.

### Full Single-Project Java Application

```kotlin
// build.gradle.kts

plugins {
    // Core plugins (no version required — they ship with Gradle)
    id("java")
    // Or for an executable application:
    // id("application")

    // Community plugins (version required when not in pluginManagement)
    id("com.diffplug.spotless") version "6.25.0"
}

// Project coordinates (used in published artifacts and dependency declarations)
group = "com.example"
version = "1.0.0"

// Java toolchain: tells Gradle which JDK to use to compile and test
// Gradle will auto-provision the JDK if it's not installed (with Toolchain Provisioning)
java {
    toolchain {
        languageVersion = JavaLanguageVersion.of(17)
        // Optional: pin vendor
        // vendor = JvmVendorSpec.ADOPTIUM
    }
    // Generate sources and javadoc JARs automatically (useful for library publishing)
    withSourcesJar()
    withJavadocJar()
}

// For the `application` plugin: set the main class
// application {
//     mainClass = "com.example.App"
// }

// Dependency configurations
dependencies {
    // implementation: on compile classpath and runtime classpath, NOT exposed to consumers
    implementation("com.google.guava:guava:33.0.0-jre")

    // api: on compile classpath AND exposed to consumers (requires java-library plugin)
    // api("org.slf4j:slf4j-api:2.0.9")

    // compileOnly: compile classpath only (like 'provided' in Maven)
    compileOnly("org.projectlombok:lombok:1.18.30")
    annotationProcessor("org.projectlombok:lombok:1.18.30")

    // runtimeOnly: runtime classpath only (not needed to compile against)
    runtimeOnly("ch.qos.logback:logback-classic:1.4.14")

    // Test dependencies
    testImplementation("org.junit.jupiter:junit-jupiter:5.10.0")
    testRuntimeOnly("org.junit.platform:junit-platform-launcher")
    testCompileOnly("org.projectlombok:lombok:1.18.30")
    testAnnotationProcessor("org.projectlombok:lombok:1.18.30")
}

// Configure the test task to use JUnit Platform (required for JUnit 5)
tasks.test {
    useJUnitPlatform()
    // Show test output in console
    testLogging {
        events("passed", "skipped", "failed")
    }
}

// Configure Spotless code formatter
spotless {
    java {
        googleJavaFormat("1.18.1")
        removeUnusedImports()
    }
}
```

### Groovy DSL Equivalent (build.gradle)

For reference when working on a Groovy-DSL project:

```groovy
// build.gradle (Groovy DSL)
plugins {
    id 'java'
    id 'com.diffplug.spotless' version '6.25.0'
}

group = 'com.example'
version = '1.0.0'

java {
    toolchain {
        languageVersion = JavaLanguageVersion.of(17)
    }
}

dependencies {
    implementation 'com.google.guava:guava:33.0.0-jre'
    testImplementation 'org.junit.jupiter:junit-jupiter:5.10.0'
    testRuntimeOnly 'org.junit.platform:junit-platform-launcher'
}

test {
    useJUnitPlatform()
}
```

Key Groovy/Kotlin DSL differences:
- Groovy uses single OR double quotes; Kotlin requires double quotes
- Groovy method calls don't need parentheses in many places; Kotlin requires `()` consistently
- Groovy `test { }` vs Kotlin `tasks.test { }` (Kotlin requires explicit task access)
- Groovy `id 'plugin'` vs Kotlin `id("plugin")`

---

## gradle init Scaffolding

`gradle init` is the official way to create a new Gradle project from scratch. It generates a complete, working project with the wrapper, settings file, build file, source directories, and a sample test.

### Interactive Mode

```bash
gradle init
```

Gradle asks a series of questions:
1. Project type (see below)
2. Build script DSL: Kotlin (default since 8.2) or Groovy
3. Test framework: JUnit Jupiter (default), TestNG, Spock
4. Project name (defaults to directory name)
5. Source package (e.g., `com.example`)
6. Java version (defaults to current JVM)
7. Whether to generate a version catalog (`libs.versions.toml`)

### Non-Interactive Mode (CI / Scripting)

```bash
gradle init \
  --type java-application \
  --dsl kotlin \
  --test-framework junit-jupiter \
  --project-name my-app \
  --package com.example \
  --java-version 17 \
  --no-incubating
```

### Project Types

| `--type` | Description |
|---|---|
| `basic` | Empty project with wrapper only |
| `java-application` | `application` plugin, main class, JUnit |
| `java-library` | `java-library` plugin, `api` configuration |
| `kotlin-application` | Kotlin JVM application |
| `kotlin-library` | Kotlin JVM library |
| `scala-library` | Scala library |
| `groovy-application` | Groovy application |
| `groovy-library` | Groovy library |
| `cpp-application` | C++ application (experimental) |
| `cpp-library` | C++ library (experimental) |

---

## Build Lifecycle Deep Dive

### Phase 1: Initialization

**What runs**: Gradle finds and evaluates `settings.gradle.kts`. This determines which projects exist and their directory locations.

**Files evaluated**: `settings.gradle.kts` (and `init.gradle.kts` from `GRADLE_USER_HOME/init.d/` if present)

**What Gradle does**:
- Evaluates `pluginManagement {}` block to know where to find plugins
- Evaluates `dependencyResolutionManagement {}` to configure repositories
- Creates a `Project` object for each `include()`d subproject

### Phase 2: Configuration

**What runs**: Every `build.gradle.kts` in the project tree is evaluated, top to bottom, even if only a single task was requested.

**Files evaluated**: `build.gradle.kts` for root project and all subprojects

**What Gradle does**:
- Applies plugins (which register new tasks and configurations)
- Evaluates dependency declarations
- Creates task objects and wires up `dependsOn` relationships
- Builds the **task execution graph**

**Critical rule**: code outside `doFirst {}`, `doLast {}`, or `@TaskAction` runs at **configuration time**. Heavy computation, file I/O, or network calls here slow every single build, even builds that don't need that work.

```kotlin
// BAD: runs at configuration time for every build
tasks.register("myTask") {
    val result = File("big-file.txt").readText()  // ← configuration-time I/O!
    doLast { println(result) }
}

// GOOD: use lazy Provider API; resolved only at execution time
tasks.register("myTask") {
    val inputFile = layout.projectDirectory.file("big-file.txt")
    doLast {
        val result = inputFile.get().asFile.readText()  // ← execution-time I/O
        println(result)
    }
}
```

### Phase 3: Execution

**What runs**: Gradle executes the tasks in the execution graph, in dependency order.

**Up-to-date checking**: before running each task, Gradle checks whether its inputs and outputs have changed since the last run. If nothing changed, the task is marked `UP-TO-DATE` and skipped.

**Build cache**: if `--build-cache` is enabled and a task with matching inputs was run in a previous build (or on another machine), Gradle restores outputs from cache (`FROM-CACHE`) instead of re-executing.

### Configuration Cache

Introduced in Gradle 6.6, stable in Gradle 8.1, and the default mode in Gradle 9.

The configuration cache serializes the result of the Configuration phase to disk. On subsequent builds where nothing in `settings.gradle.kts`, `build.gradle.kts`, or any plugin has changed, Gradle **skips the Configuration phase entirely** and goes directly to Execution.

Enable in `gradle.properties`:
```properties
org.gradle.configuration-cache=true
```

Or per-run:
```bash
./gradlew build --configuration-cache
```

---

## gradle.properties

`gradle.properties` configures the Gradle build environment. It lives either in the project root (checked into version control; project-specific) or in `~/.gradle/gradle.properties` (user-level; applies to all projects).

### Recommended Project-Level gradle.properties

```properties
# gradle.properties

# --- Performance ---
# Keep the Gradle daemon running between builds (almost always true)
org.gradle.daemon=true

# Run independent tasks in parallel (safe for well-structured builds)
org.gradle.parallel=true

# Enable the build cache (reuse outputs from previous builds)
org.gradle.caching=true

# Enable configuration cache (skip re-configuration on unchanged builds)
# Stable since Gradle 8.1; default in Gradle 9
org.gradle.configuration-cache=true

# JVM memory for the Gradle daemon
# -XX:+HeapDumpOnOutOfMemoryError: write a heap dump on OOM for diagnosis
# -XX:HeapDumpPath: where to write it
org.gradle.jvmargs=-Xmx2g -XX:+HeapDumpOnOutOfMemoryError -XX:HeapDumpPath=/tmp/gradle-heap.hprof

# --- Logging ---
# Emit all deprecation warnings (important during Gradle version upgrades)
org.gradle.warning.mode=all

# --- Kotlin DSL ---
# Faster Kotlin DSL script compilation (experimental pre-compiled scripts cache)
# kotlin.incremental=true

# --- Android (if applicable) ---
# android.useAndroidX=true
# android.enableJetifier=false
```

### User-Level gradle.properties (~/.gradle/gradle.properties)

```properties
# Personal settings that should not be committed to version control

# Publish credentials (prefer environment variables over this file in CI)
# mavenCentralUsername=your-username
# mavenCentralPassword=your-token

# Override daemon memory for this machine
org.gradle.jvmargs=-Xmx4g

# Enable build scans by default
# org.gradle.scan.background-upload=true
```

---

## .gitignore for Gradle Projects

```gitignore
# Gradle build outputs
build/
.gradle/

# Do NOT ignore (commit these):
# gradle/wrapper/gradle-wrapper.jar
# gradle/wrapper/gradle-wrapper.properties
# gradlew
# gradlew.bat

# IntelliJ IDEA
.idea/
*.iml
*.iws
out/

# Eclipse
.classpath
.project
.settings/

# OS
.DS_Store
Thumbs.db
```

---

## Important Patterns and Constraints

- **Always commit the Gradle wrapper** including `gradle-wrapper.jar` (it's a binary but it's tiny and necessary for CI bootstrap without a Gradle pre-install)
- **Never commit `.gradle/`** — this is the per-project cache directory
- **`buildSrc/`** is a special Gradle subproject that is compiled before the main build; use it for shared task types, plugins, and convention plugins; it has full IDE support but slows configuration if large
- **`gradle/libs.versions.toml`** is the standard location for version catalogs since Gradle 8.2; prefer it over hardcoded version strings
- **Gradle 9.0 requires Java 17** to *run* Gradle (the daemon JVM); this is separate from the Java *toolchain* version used to compile your code
- **Plugin versions in `plugins {}` block**: when using `pluginManagement {}` in `settings.gradle.kts`, you can omit the version from `plugins {}` blocks in subproject build files — the version is resolved from `pluginManagement`
- **Avoid `allprojects {}` and `subprojects {}`** for applying plugins — prefer convention plugins in `buildSrc` or an included build; `allprojects` cross-configures every project at configuration time and prevents project isolation
