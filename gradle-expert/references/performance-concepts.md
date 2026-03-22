# Performance — Daemon, Caching, Configuration Cache

See also: [Performance CLI Reference](performance-cli.md)

## Gradle Daemon

The Gradle daemon is a long-lived JVM background process that eliminates the overhead of JVM startup and class loading on every build invocation. Without the daemon, each `./gradlew` call starts a fresh JVM, loads Gradle internals, and then executes. With the daemon, all of that warm-up work is paid once and the daemon stays alive to serve subsequent builds.

```properties
# gradle.properties
org.gradle.daemon=true              # enabled by default; keep it on
org.gradle.jvmargs=-Xmx2g -XX:+HeapDumpOnOutOfMemoryError -XX:MaxMetaspaceSize=512m
```

Daemon lifecycle:

- Started on the first build that needs it; reused for all subsequent builds on the same machine that use the same Gradle version and the same JVM arguments.
- Idle timeout: 3 hours by default; the daemon exits gracefully after this period with no build activity.
- If a daemon is busy, Gradle starts a new one; multiple daemons can run concurrently.
- Gradle 9: the daemon itself is provisioned using the project's JVM toolchain configuration, so it runs on the same JDK version as your code. You no longer need to set `JAVA_HOME` to match the build JDK.

Daemon identity is based on two things: the Gradle version and the `org.gradle.jvmargs` value. Changing heap size in `gradle.properties` starts a new daemon. Keep JVM args stable across your team by committing `gradle.properties` to VCS.

## Build Cache

The build cache saves task *outputs* (compiled classes, test results, processed resources, etc.) keyed by a hash of all task *inputs* (source files, compiler flags, dependency versions, etc.). When inputs are unchanged — even across machines or CI agents — Gradle restores the cached outputs instead of re-executing the task. A restored task is logged as `FROM-CACHE`.

Enable globally:

```properties
# gradle.properties
org.gradle.caching=true
```

Local cache is stored at `~/.gradle/caches/build-cache/`. It is always enabled by default when `org.gradle.caching=true`.

Remote cache for team-wide sharing:

```kotlin
// settings.gradle.kts
buildCache {
    local {
        isEnabled = true
        removeUnusedEntriesAfterDays = 30
    }
    remote<HttpBuildCache> {
        url = uri("https://build-cache.example.com/cache/")
        credentials {
            username = providers.environmentVariable("CACHE_USER").get()
            password = providers.environmentVariable("CACHE_KEY").get()
        }
        // Only CI agents push to the remote cache; developers only pull
        isPush = System.getenv("CI") != null
    }
}
```

For a task to participate in the build cache it must:

1. Declare all inputs with `@Input`, `@InputFile`, `@InputFiles`, or `@InputDirectory`.
2. Declare all outputs with `@OutputFile`, `@OutputDirectory`, or `@OutputFiles`.
3. Be annotated with `@CacheableTask`.
4. Produce *deterministic* outputs: the same inputs must always produce byte-for-byte identical outputs. Tasks that embed timestamps or random values in their output cannot be cached.

```kotlin
@CacheableTask
abstract class GenerateReport : DefaultTask() {
    @get:PathSensitive(PathSensitivity.RELATIVE)
    @get:InputFiles
    abstract val sources: ConfigurableFileCollection

    @get:Input
    abstract val reportTitle: Property<String>

    @get:OutputDirectory
    abstract val outputDir: DirectoryProperty

    @TaskAction
    fun generate() {
        // deterministic report generation
    }
}
```

`@PathSensitive(PathSensitivity.RELATIVE)` tells Gradle that the absolute paths of input files do not affect the output — only their contents and relative paths matter. This is required for cache hits across machines with different checkout directories.

## Configuration Cache

The configuration cache serializes the entire task graph — all configured tasks and their parameters — after the configuration phase completes. On subsequent builds, if nothing in the build scripts, settings, or inputs has changed, Gradle skips the configuration phase entirely and deserializes the task graph directly. This can eliminate seconds or minutes of configuration time on large builds.

```properties
# gradle.properties
org.gradle.configuration-cache=true
org.gradle.configuration-cache.problems=warn  # warn (lenient) or fail (strict)
```

Gradle 9: configuration cache is enabled by default for new projects; "preferred mode" in Gradle 9.0.

### What triggers a configuration cache miss

- Changes to any `build.gradle.kts`, `settings.gradle.kts`, or `gradle.properties` file.
- Changes to files read at configuration time (e.g., version files loaded with `file("version.txt").readText()`).
- Changes to system properties or environment variables read at configuration time.
- Changes in buildSrc or included builds.

### Configuration cache compatibility requirements

Build logic must not capture mutable state that cannot be serialized:

```kotlin
// WRONG: captures Project reference, which is not serializable
tasks.register("bad") {
    val projectName = project.name  // project object captured in closure
    doLast { println(projectName) }
}

// CORRECT: capture the value, not the object
tasks.register("good") {
    val projectName = project.name  // primitive String captured — fine
    inputs.property("projectName", projectName)
    doLast { println(projectName) }
}
```

External processes (e.g., `exec {}` blocks) called at configuration time will not re-run on a configuration cache hit — move them to task actions.

```bash
# Check compatibility without enabling globally
./gradlew build --configuration-cache
./gradlew build --configuration-cache-problems=warn

# HTML compatibility report
open build/reports/configuration-cache/*/configuration-cache-report.html

# Gradle 9.1: read-only mode for CI (never writes, only reads from shared store)
./gradlew build --configuration-cache --read-only-configuration-cache-store
```

## Incremental Compilation

Gradle tracks which source files changed and recompiles only the affected classes and their dependents, rather than the entire source set.

Java incremental compilation is enabled by default. The Java compiler daemon avoids JVM startup on each compile:

```kotlin
tasks.withType<JavaCompile>().configureEach {
    options.isIncremental = true        // default; explicit for clarity
    options.isFork = true               // compile in a separate compiler daemon process
    options.forkOptions.memoryMaximumSize = "1g"
}
```

Kotlin incremental compilation:

```properties
# gradle.properties
kotlin.incremental=true       # default; recompile only changed Kotlin files and dependents
kotlin.daemon.jvm.options=-Xmx2g  # heap for the Kotlin compiler daemon
```

The Kotlin incremental daemon maintains a cache of compiled output and dependency relations between classes. It can detect ABI changes and limit recompilation to directly affected classes.

## Parallel Execution

Independent tasks across subprojects run concurrently when parallel execution is enabled:

```properties
# gradle.properties
org.gradle.parallel=true
org.gradle.workers.max=8    # default: number of CPU cores
```

Parallel execution requires that tasks declare their dependencies correctly (via `dependsOn`, `mustRunAfter`, or input/output wiring). Tasks with undeclared dependencies can produce flaky builds under parallel execution.

The Worker API allows tasks to execute work items concurrently within a single task:

```kotlin
abstract class ProcessFiles : DefaultTask() {
    @get:Inject
    abstract val workerExecutor: WorkerExecutor

    @TaskAction
    fun process() {
        val workQueue = workerExecutor.noIsolation()
        project.fileTree("src").forEach { file ->
            workQueue.submit(ProcessFileAction::class) {
                this.inputFile = file
            }
        }
    }
}
```

Parallel execution across subprojects is different from parallel test execution (configured per test task with `maxParallelForks`).

## `gradle.properties` Performance Tuning

A comprehensive `gradle.properties` for a large project:

```properties
# ── Daemon ───────────────────────────────────────────────────────────────────
org.gradle.daemon=true
org.gradle.jvmargs=-Xmx4g -XX:+HeapDumpOnOutOfMemoryError -XX:MaxMetaspaceSize=512m -XX:+UseParallelGC -Dfile.encoding=UTF-8

# ── Execution ─────────────────────────────────────────────────────────────────
org.gradle.parallel=true
org.gradle.workers.max=8
org.gradle.vfs.watch=true       # file system watching: persist FS state between builds

# ── Caching ──────────────────────────────────────────────────────────────────
org.gradle.caching=true
org.gradle.configuration-cache=true
org.gradle.configuration-cache.problems=warn

# ── Kotlin ───────────────────────────────────────────────────────────────────
kotlin.incremental=true
kotlin.daemon.jvm.options=-Xmx2g
kotlin.build.report.output=file   # build reports: build/reports/kotlin-build/
```

For developer machines, you can put performance flags in `~/.gradle/gradle.properties` so they apply to all projects without committing team-specific settings.

## File System Watching

File system watching keeps a hot model of the file system state between builds. Without it, Gradle must scan the entire project tree at the start of each build to detect changes. With watching enabled, the OS notifies Gradle of changes in real time, reducing the file system scanning overhead of incremental builds.

```properties
# gradle.properties (enabled by default on macOS and Linux since Gradle 7)
org.gradle.vfs.watch=true
```

```bash
# Verbose watching events (useful for debugging)
./gradlew build -Dorg.gradle.vfs.verbose=true
```

## Build Scan Analysis

Build scans are the primary tool for diagnosing slow builds. They provide a detailed timeline and breakdown of every aspect of the build:

```bash
./gradlew build --scan
# Publishes to scans.gradle.com (free for open source and individual use)
# Develocity on-premise for enterprise use
```

A build scan shows:

- **Timeline**: wall clock gantt chart of all tasks; reveals parallelism gaps and serial bottlenecks.
- **Performance tab**: total build time split into startup, configuration, dependency resolution, and task execution time.
- **Task execution**: breakdown of `UP-TO-DATE`, `FROM-CACHE`, `EXECUTED`, `SKIPPED` for every task.
- **Test results**: pass/fail/skip counts, duration per test, test output.
- **Dependency resolution**: what was resolved, from which repository, and how long it took.
- **Configuration cache**: compatibility status and problems.
- **Performance suggestions**: automatically identified issues (e.g., too many `resolve` calls at configuration time).

## JVM Toolchains (Java Version Management)

Java toolchains let Gradle automatically download and use the correct JDK for compilation, regardless of what is installed on the machine or set as `JAVA_HOME`.

```kotlin
// build.gradle.kts
java {
    toolchain {
        languageVersion = JavaLanguageVersion.of(21)
        vendor = JvmVendorSpec.AMAZON        // ADOPTIUM, AZUL, BELLSOFT, IBM, ORACLE, etc.
        implementation = JvmImplementation.VENDOR_SPECIFIC
    }
}
```

Gradle downloads the JDK to `~/.gradle/jdks/` if it is not already present. Auto-provisioning uses Foojay Disco API by default.

```kotlin
// settings.gradle.kts — configure toolchain auto-provisioning
plugins {
    id("org.gradle.toolchains.foojay-resolver-convention") version "0.8.0"
}
```

Gradle 9: the daemon itself is started using the toolchain JVM. Previously the daemon used the system JDK; now it matches the project's declared toolchain.

Per-task toolchain override (e.g., compile with JDK 21 but test with JDK 17):

```kotlin
tasks.withType<Test>().configureEach {
    javaLauncher = javaToolchains.launcherFor {
        languageVersion = JavaLanguageVersion.of(17)
    }
}
```

## Common Performance Problems

| Symptom | Likely Cause | Fix |
|---|---|---|
| First build always slow even with caching | Configuration cache miss on every run | Check the configuration cache report for incompatible plugins or configuration-time side effects |
| `buildSrc` change invalidates every project | Any modification to `buildSrc` invalidates all cached configuration | Migrate `buildSrc` to a separate included build (`includeBuild("build-logic")`) |
| Tests always re-run even without source changes | Test task output is non-deterministic (timestamps, random ports, etc.) | Fix the non-determinism; or exclude specific tests from caching with `outputs.cacheIf { false }` |
| Slow dependency resolution | Dynamic versions (`1.+`, `latest.release`) force network round-trips | Pin versions; or use dependency locking to cache resolved versions |
| `compileKotlin` re-runs unnecessarily | Kotlin incremental cache invalidated by annotation processor changes | Separate annotation processing into its own source set; check Kotlin incremental compatibility |
| Large daemon heap consuming memory on developer machines | `-Xmx` set too high for local use | Put a lower `org.gradle.jvmargs` in `~/.gradle/gradle.properties` (overrides project `gradle.properties`) |
| Remote build cache has very low hit rate | Cache key varies between CI agents | Ensure file paths are normalized with `@PathSensitive`; check for absolute path references in task inputs |
