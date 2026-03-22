# Ch.1 — Gradle CLI Reference

*Companion concepts reference: [ch1-fundamentals-concepts.md](ch1-fundamentals-concepts.md)*

---

## Wrapper Setup

```bash
# Generate wrapper targeting a specific Gradle version (requires local Gradle install)
gradle wrapper --gradle-version 8.11 --distribution-type bin

# Generate wrapper with full distribution (includes Gradle sources — useful for IDE navigation)
gradle wrapper --gradle-version 8.11 --distribution-type all

# Update an existing wrapper to a newer version using the current wrapper
./gradlew wrapper --gradle-version 9.2.1

# Verify the active Gradle version (downloads if needed)
./gradlew --version

# Sample output:
# ------------------------------------------------------------
# Gradle 8.11
# ------------------------------------------------------------
# Build time:    2024-11-20 16:56:46 UTC
# Revision:      ...
# Kotlin:        1.9.24
# Groovy:        3.0.22
# Ant:           Apache Ant(TM) version 1.10.14
# Launcher JVM:  21.0.1 (Eclipse Adoptium 21.0.1+12)
# Daemon JVM:    /Library/Java/JavaVirtualMachines/temurin-21.jdk/...
# OS:            Mac OS X 14.1.1 aarch64
```

### Wrapper Property: Pin a SHA-256 Checksum

Add this to `gradle/wrapper/gradle-wrapper.properties` to verify the downloaded distribution:
```properties
distributionSha256Sum=5c76a3e174a3369a62ba3b75ea41e5bbc7d3cdb0e37038f0e3edd8e88ca57702
```

Obtain the checksum from `https://services.gradle.org/distributions/` (each `.zip` has a companion `.zip.sha256` file).

---

## gradle init

```bash
# Launch interactive project scaffolding wizard
gradle init

# Non-interactive: Java application with Kotlin DSL and JUnit Jupiter
gradle init \
  --type java-application \
  --dsl kotlin \
  --test-framework junit-jupiter \
  --project-name my-app \
  --package com.example \
  --java-version 17 \
  --no-incubating

# Non-interactive: Java library
gradle init \
  --type java-library \
  --dsl kotlin \
  --test-framework junit-jupiter \
  --project-name my-lib \
  --package com.example.lib

# Kotlin application
gradle init \
  --type kotlin-application \
  --dsl kotlin \
  --test-framework kotlin-test \
  --project-name my-kotlin-app \
  --package com.example

# Basic project (wrapper + settings only, no source)
gradle init --type basic --dsl kotlin --project-name my-project
```

### Available `--type` Values

| Value | Plugin Applied | Description |
|---|---|---|
| `basic` | none | Wrapper + settings only |
| `java-application` | `application` | Executable Java app with `run` task |
| `java-library` | `java-library` | Reusable Java library |
| `kotlin-application` | `org.jetbrains.kotlin.jvm` + `application` | Executable Kotlin app |
| `kotlin-library` | `org.jetbrains.kotlin.jvm` | Reusable Kotlin library |
| `scala-library` | `scala` | Scala library |
| `groovy-application` | `application` + `groovy` | Groovy application |
| `groovy-library` | `groovy` | Groovy library |
| `cpp-application` | `cpp-application` | C++ application (incubating) |
| `cpp-library` | `cpp-library` | C++ library (incubating) |

### Available `--test-framework` Values

| Value | Framework | Notes |
|---|---|---|
| `junit-jupiter` | JUnit 5 | Default; requires `useJUnitPlatform()` |
| `junit` | JUnit 4 | Legacy |
| `testng` | TestNG | Requires `useTestNG()` |
| `spock` | Spock | Groovy-based; works with Java and Kotlin projects |
| `kotlin-test` | kotlin.test | For Kotlin projects |

---

## Running Tasks

```bash
# The three most common lifecycle tasks
./gradlew build      # compileJava + processResources + classes + jar + test + check
./gradlew assemble   # compileJava + processResources + classes + jar (no tests)
./gradlew check      # all verification: test + any lint/analysis tasks

# Clean outputs
./gradlew clean                  # delete the build/ directory
./gradlew clean build            # clean first, then full build

# Run the application (requires the `application` plugin)
./gradlew run
./gradlew run --args="--port 8080 --verbose"   # pass arguments to main()

# List available tasks
./gradlew tasks                          # lifecycle, build setup, help tasks
./gradlew tasks --all                    # include all tasks with their dependents
./gradlew tasks --group verification     # filter by group name
./gradlew tasks --group "build"

# Get help on a specific task
./gradlew help --task build
./gradlew help --task compileJava
./gradlew help --task test

# Run multiple tasks in one invocation (Gradle executes in correct dependency order)
./gradlew clean assemble test

# Run a specific subproject's task (multi-project builds)
./gradlew :app:build
./gradlew :lib:jar
```

---

## Output Verbosity

Gradle has five logging levels. Default is LIFECYCLE (shows task names and outcomes).

```bash
./gradlew build -q          # QUIET  — only errors and output explicitly logged at QUIET
./gradlew build             # LIFECYCLE (default) — task names, outcomes, and warnings
./gradlew build -w          # WARN   — lifecycle + warnings
./gradlew build -i          # INFO   — verbose; shows task inputs/outputs, skipped reasons
./gradlew build -d          # DEBUG  — extremely verbose; internal Gradle decisions, classpath details

# Surface all deprecation warnings (essential when upgrading Gradle versions)
./gradlew build --warning-mode=all

# Suppress all warnings
./gradlew build --warning-mode=none

# Show rich (colored, animated) console output (default on interactive TTY)
./gradlew build --console=rich
# Plain output (good for CI systems that capture stdout/stderr)
./gradlew build --console=plain
# Verbose output: show the task name before its output
./gradlew build --console=verbose
```

### Interpreting Task Outcome Labels

| Label | Meaning |
|---|---|
| (none) | Task executed successfully |
| `UP-TO-DATE` | Inputs/outputs unchanged; task skipped |
| `FROM-CACHE` | Outputs restored from build cache; task not re-executed |
| `SKIPPED` | Task was excluded (`-x`) or `onlyIf` condition was false |
| `NO-SOURCE` | Task had no source files to process |
| `FAILED` | Task threw an exception |

---

## Incremental Build Control

```bash
# Force re-run ALL tasks regardless of up-to-date status
./gradlew build --rerun-tasks

# Force re-run only a specific task (Gradle 7.6+)
./gradlew test --rerun

# Exclude a task from execution
./gradlew build -x test          # skip the test task (and tasks that only test depends on)
./gradlew build -x javadoc -x test

# Skip the build cache for this run (still writes outputs to cache)
./gradlew build --no-build-cache

# Continue execution after a task failure (default: stop on first failure)
./gradlew test --continue

# Show what tasks would run without executing them
./gradlew build --dry-run
# Output example:
# :compileJava SKIPPED
# :processResources SKIPPED
# :classes SKIPPED
# :jar SKIPPED
# :test SKIPPED
# :check SKIPPED
# :build SKIPPED
```

---

## Build Scans

Build scans provide a shareable, web-based view of a build's performance, task timeline, test results, and dependency tree. Hosted at `scans.gradle.com` (free) or Gradle Enterprise (self-hosted).

```bash
# Publish a build scan (prompts for Terms of Service acceptance on first run)
./gradlew build --scan

# Suppress the build scan prompt entirely
./gradlew build --no-scan

# Always publish scans without the prompt: add to gradle.properties
# org.gradle.scan.background-upload=true
```

After a scan-enabled build completes, Gradle prints:
```
Publishing build scan...
https://scans.gradle.com/s/abc123xyz456
```

A build scan shows:
- Timeline of every task with duration
- Up-to-date status for each task
- All test results (pass/fail/skip with output)
- Full dependency tree
- Switch details (which flags were passed)
- Environment info (JVM, OS, Gradle version)
- Performance suggestions

---

## Daemon

The Gradle daemon is a long-lived JVM process that persists between builds. It eliminates JVM startup overhead and keeps the class-loading cache warm. On most developer machines, the daemon cuts build time by 2–5 seconds per build.

```bash
# List all Gradle daemons and their status
./gradlew --status
# Output:
#   PID STATUS   INFO
#   12345 IDLE     8.11
#   12346 BUSY     8.11

# Stop all daemons
./gradlew --stop
# (also: gradle --stop)

# Run this build without using a daemon (useful for debugging daemon issues or CI)
./gradlew build --no-daemon

# Force foreground execution (same as --no-daemon but more explicit)
./gradlew build --foreground
```

### Daemon Configuration in gradle.properties

```properties
# Enable the daemon (default: true since Gradle 3.0)
org.gradle.daemon=true

# Daemon JVM memory
org.gradle.jvmargs=-Xmx2g -XX:+UseG1GC

# Idle timeout before daemon self-terminates (in milliseconds; default: 3 hours = 10800000)
org.gradle.daemon.idletimeout=7200000
```

### When to Disable the Daemon

- **CI environments**: most CI systems run builds in ephemeral containers; the daemon provides no benefit and wastes memory. Use `./gradlew --no-daemon` or set `org.gradle.daemon=false` in CI-specific environment configuration.
- **Debugging classpath issues**: a fresh JVM process ensures no stale class-loading state.
- **Memory-constrained environments**: each daemon takes ~256 MB–2 GB depending on `jvmargs`.

---

## Project Properties

Project properties let you pass values from the CLI into your `build.gradle.kts` (accessible via `project.findProperty()` or the `by project` delegate).

```bash
# Pass a project property
./gradlew build -PmyProp=value
./gradlew build -Prelease=true
./gradlew build -Pversion=2.0.0

# Pass a JVM system property (to the Gradle daemon's JVM)
./gradlew build -Dorg.gradle.parallel=true
./gradlew build -Dfile.encoding=UTF-8

# List all project properties and their values
./gradlew properties

# List all properties filtered to a pattern
./gradlew properties | grep version
```

### Using Properties in build.gradle.kts

```kotlin
// Access with a default (safe — returns null if not set)
val myProp: String? = project.findProperty("myProp") as String?

// Access with by project delegate (throws if not set)
val release: String by project

// Access with default value
val buildNumber: String = (project.findProperty("buildNumber") as String?) ?: "SNAPSHOT"
```

---

## Gradle User Home and Cache

Gradle stores downloaded distributions, dependency caches, and build scan data in the **Gradle User Home** directory.

```bash
# Default location
# Linux/macOS: ~/.gradle/
# Windows:     %USERPROFILE%\.gradle\

# Override for a specific build (useful in CI to use a shared cache volume)
GRADLE_USER_HOME=/opt/gradle-cache ./gradlew build

# Or set persistently in your shell profile:
export GRADLE_USER_HOME=/opt/gradle-cache
```

### Cache Directory Layout

```
~/.gradle/
├── caches/
│   ├── modules-2/               ← Downloaded dependency JARs and metadata
│   ├── build-cache-1/           ← Local build cache (task output cache)
│   └── <gradle-version>/        ← Gradle version-specific caches
├── wrapper/
│   └── dists/                   ← Downloaded Gradle distributions
├── daemon/
│   └── <version>/               ← Daemon logs and registry
├── init.d/                      ← Init scripts applied to ALL builds on this machine
│   └── enterprisePlugin.gradle
└── gradle.properties            ← User-level properties (credentials, memory overrides)
```

### Clearing Caches (Use Sparingly)

```bash
# Stop all daemons before clearing caches
./gradlew --stop

# Delete dependency cache (forces re-download of all dependencies)
rm -rf ~/.gradle/caches/modules-2/

# Delete local build cache (forces re-execution of all cached tasks)
rm -rf ~/.gradle/caches/build-cache-1/

# Delete a specific Gradle version distribution
rm -rf ~/.gradle/wrapper/dists/gradle-8.11-bin/

# Delete everything (nuclear option — forces full re-download of distributions + deps)
rm -rf ~/.gradle/caches/
```

---

## Init Scripts

Init scripts (`~/.gradle/init.d/*.gradle.kts`) are applied to every Gradle build on the machine, before any project-level configuration. They are useful for applying enterprise-wide conventions (e.g., repository mirrors, Gradle Enterprise plugin, signing certificates).

```kotlin
// ~/.gradle/init.d/enterprise.gradle.kts
beforeSettings {
    apply(plugin = "com.gradle.enterprise")
    configure<com.gradle.enterprise.gradleplugin.GradleEnterpriseExtension> {
        buildScan {
            server = "https://ge.example.com"
            publishAlways()
        }
    }
}
```

---

## Useful One-Liners

```bash
# Full clean build with build scan (typical pre-release check)
./gradlew clean build --scan

# List all dependencies in the runtimeClasspath configuration
./gradlew dependencies --configuration runtimeClasspath

# Check for dependency updates (requires the ben-manes/versions plugin)
./gradlew dependencyUpdates

# Show which dependency version was selected and why
./gradlew dependencyInsight --dependency guava --configuration compileClasspath

# Run only tests matching a pattern (JUnit 5)
./gradlew test --tests "com.example.*"
./gradlew test --tests "com.example.FooTest.testBar"

# Run in continuous mode: re-execute on file changes
./gradlew test --continuous

# Generate an HTML dependency report in build/reports/project/dependencies/
./gradlew htmlDependencyReport

# Print the project structure
./gradlew projects

# Show Gradle environment info
./gradlew --version
./gradlew properties | grep -E "^(group|version|name):"
```
