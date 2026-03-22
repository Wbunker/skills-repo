# Ch.2 — Gradle Tasks

*Companion CLI reference: [ch2-tasks-cli.md](ch2-tasks-cli.md)*

---

## Task Basics

A **task** is the fundamental unit of work in Gradle. Every build is a set of tasks that Gradle executes in dependency order. Each task has:
- A **name** (e.g., `compileJava`, `test`, `jar`)
- Zero or more **actions** (`doFirst {}` / `doLast {}` / `@TaskAction`)
- Zero or more **dependencies** (other tasks that must run first)
- A set of **inputs** and **outputs** (used for up-to-date checks and caching)
- Optional **description** and **group** (surfaced in `./gradlew tasks`)

### Ad-Hoc Task (Simplest Form)

```kotlin
// build.gradle.kts

// Register an ad-hoc task with a single action
tasks.register("hello") {
    description = "Prints a greeting"
    group = "demo"
    doLast {
        println("Hello, Gradle!")
    }
}
```

```bash
./gradlew hello
# > Task :hello
# Hello, Gradle!
```

### Lazy Registration vs Eager Creation

| Method | Evaluation | Recommended? |
|---|---|---|
| `tasks.register("name") {}` | Lazy — only configured if task is in the execution graph | Yes — always prefer this |
| `tasks.create("name") {}` | Eager — configured at configuration time for every build | Avoid |
| `tasks.named("name") {}` | Lazy — configure an existing task by name | Yes |
| `tasks.getByName("name") {}` | Eager — immediately resolves and configures | Avoid |
| `tasks["name"]` | Eager | Avoid |

**Why it matters**: with `register()`, Gradle only configures a task when that task will actually run. This speeds up configuration time — especially in large multi-project builds where most tasks are irrelevant to the requested command.

---

## Task Actions: doFirst and doLast

A task can have multiple actions, which are executed sequentially when the task runs. `doFirst` prepends an action to the front of the action list; `doLast` appends to the end.

```kotlin
// Configuring an existing task (the `build` lifecycle task)
tasks.named("build") {
    doFirst {
        println("== Build starting ==")
    }
    doLast {
        println("== Build complete ==")
    }
}
```

Multiple `doFirst` and `doLast` calls accumulate:
```kotlin
tasks.register("multiAction") {
    doFirst { println("First action (added last with doFirst)") }
    doFirst { println("First action (added first with doFirst — runs BEFORE the above)") }
    doLast  { println("Second action") }
    doLast  { println("Third action") }
}
// Execution order:
// "First action (added first...)"   ← doFirst is a stack; last-registered runs first
// "First action (added last...)"
// "Second action"
// "Third action"
```

**Important**: `doFirst` / `doLast` are **execution-time** actions. They only run when the task is in the execution graph. Code inside the task's configuration block (but outside `doFirst`/`doLast`) runs at **configuration time**.

---

## Task Configuration vs Execution Time

This is the most common source of bugs in Gradle build files. Understanding the distinction is essential.

```kotlin
tasks.register("example") {
    // === CONFIGURATION TIME ===
    // This println runs when Gradle evaluates this build file,
    // regardless of which task was requested.
    println("Configuring example task")  // ← runs even during `./gradlew help`

    val outputFile = layout.buildDirectory.file("output.txt")  // lazy path — OK here

    // === EXECUTION TIME ===
    // doLast runs only when `example` is actually in the execution graph.
    doLast {
        println("Executing example task")
        outputFile.get().asFile.writeText("done")
    }
}
```

### Common Mistake: File I/O at Configuration Time

```kotlin
// BAD: reads a file for every build, even ones that never run this task
tasks.register("processConfig") {
    val config = file("config.json").readText()  // ← configuration-time I/O
    doLast { println(config) }
}

// GOOD: defer the read to execution time using Provider API
tasks.register("processConfig") {
    val configProvider = layout.projectDirectory.file("config.json")
    doLast {
        val config = configProvider.get().asFile.readText()  // ← execution-time I/O
        println(config)
    }
}
```

---

## Task Dependencies

### dependsOn

`dependsOn` declares that one task requires another to run first. Gradle adds both tasks to the execution graph and ensures correct ordering.

```kotlin
tasks.register("compileAll") {
    dependsOn("compileJava", "compileKotlin")
}

// Using a lazy task reference (preferred — avoids resolving the task eagerly)
tasks.register("generateAndPackage") {
    dependsOn(tasks.named("generateSources"))
    dependsOn(tasks.named("jar"))
}

// Depending on a task from another subproject
tasks.register("integrationTest") {
    dependsOn(":lib:jar")   // fully-qualified task path
}
```

### mustRunAfter (Ordering Without Dependency)

`mustRunAfter` controls execution order when both tasks are in the graph, without forcing either task to run. It does **not** add a dependency — if only one task is requested, the other is not added.

```kotlin
tasks.named("test") {
    mustRunAfter("cleanTestResults")  // if both run, cleanTestResults goes first
}
```

### shouldRunAfter (Weak Ordering Hint)

`shouldRunAfter` is a weaker version of `mustRunAfter`. Gradle may ignore it in parallel builds when it would create a cycle.

```kotlin
tasks.named("integrationTest") {
    shouldRunAfter("test")  // prefer test before integrationTest, but not required
}
```

### finalizedBy (Always-Run Finalizer)

`finalizedBy` registers a **finalizer** task that runs after the primary task completes — even if the primary task fails. Use for cleanup operations, reporting, or archiving.

```kotlin
tasks.register("integrationTest") {
    finalizedBy("stopTestServer")  // stopTestServer runs even if integrationTest fails
}

tasks.register("stopTestServer") {
    doLast { println("Stopping test server") }
}
```

### onlyIf (Conditional Execution)

```kotlin
tasks.register("deploy") {
    onlyIf {
        // Only run deploy if the `release` project property is set to `true`
        project.findProperty("release") == "true"
    }
    doLast { println("Deploying...") }
}

// Multiple onlyIf conditions are ANDed together
tasks.named("publish") {
    onlyIf { !version.toString().endsWith("-SNAPSHOT") }
    onlyIf { System.getenv("CI") == "true" }
}
```

---

## Task Properties

### description and group

```kotlin
tasks.register("generateDocs") {
    description = "Generates Javadoc for all public APIs"
    group = "documentation"
    // `group` controls which section of `./gradlew tasks` output the task appears in.
    // Well-known groups: "build", "verification", "publishing", "help", "other"
}
```

### enabled

```kotlin
tasks.named("javadoc") {
    enabled = !version.toString().endsWith("-SNAPSHOT")
    // When disabled, the task is shown as SKIPPED in output but is still part of the graph.
    // Contrast with onlyIf: both achieve skipping, but `enabled` is set at configuration time.
}
```

### didWork

`didWork` is a boolean set by Gradle after the task executes. It indicates whether the task actually performed work (as opposed to being UP-TO-DATE). Custom tasks can set it:

```kotlin
@TaskAction
fun execute() {
    if (outputFile.get().asFile.exists()) {
        didWork = false  // nothing changed
        return
    }
    outputFile.get().asFile.writeText("generated content")
    didWork = true
}
```

### path and name

```kotlin
// Read-only properties available in any task
tasks.register("showPath") {
    doLast {
        println("Task name: $name")   // e.g., "showPath"
        println("Task path: $path")   // e.g., ":showPath" or ":app:showPath"
    }
}
```

---

## Built-in Task Types

Gradle ships with many ready-to-use task types. The most common:

| Task Type | Purpose | Key Properties |
|---|---|---|
| `Copy` | Copy files, optionally transforming them | `from`, `into`, `include`, `exclude`, `rename`, `filter`, `expand` |
| `Jar` | Assemble a JAR archive | `archiveBaseName`, `archiveVersion`, `manifest`, `from` |
| `JavaExec` | Execute a Java main class | `mainClass`, `classpath`, `args`, `jvmArgs`, `systemProperties` |
| `Exec` | Execute an arbitrary command | `commandLine`, `args`, `workingDir`, `environment`, `executable` |
| `Delete` | Delete files or directories | `delete` (file collection or path) |
| `Zip` | Create a ZIP archive | `from`, `into`, `archiveBaseName`, `archiveVersion` |
| `Tar` | Create a TAR archive | Same as Zip plus `compression` (`GZIP`, `BZIP2`, `XZ`) |
| `Sync` | Copy files to a destination, deleting anything not in source | `from`, `into`, `preserve` |
| `WriteProperties` | Write a `.properties` file with consistent ordering | `outputFile`, `property(key, value)`, `properties(map)` |
| `GradleBuild` | Run another Gradle build | `dir`, `tasks` |

### Copy Task Example

```kotlin
tasks.register<Copy>("copyDocs") {
    description = "Copies Markdown docs to the build directory"
    group = "documentation"

    from("src/docs")
    into(layout.buildDirectory.dir("docs"))

    // Include/exclude filters (Ant-style patterns)
    include("**/*.md")
    exclude("**/draft-*.md")

    // Rename files: captures regex groups
    rename("(.*)-v\\d+\\.md", "$1.md")

    // Filter: transform each line of each file
    filter { line -> line.replace("%%VERSION%%", project.version.toString()) }

    // Expand: replace tokens using a map (like Ant's `filter` with `tokens`)
    expand(mapOf("appName" to project.name, "version" to project.version))
}
```

### Exec Task Example

```kotlin
tasks.register<Exec>("startDatabase") {
    description = "Starts the test database container"
    group = "verification"

    executable = "docker"
    args("run", "--rm", "-d",
         "--name", "test-db",
         "-p", "5432:5432",
         "-e", "POSTGRES_PASSWORD=test",
         "postgres:16")

    // Capture stdout to a ByteArrayOutputStream for further processing
    val output = org.apache.tools.ant.util.TeeOutputStream(System.out, java.io.ByteArrayOutputStream())
    standardOutput = output
}

tasks.register<Exec>("runMigrations") {
    dependsOn("startDatabase")
    commandLine("./scripts/run-migrations.sh")
    workingDir(project.rootDir)
    environment("DB_URL", "jdbc:postgresql://localhost:5432/testdb")
    environment("DB_PASSWORD", "test")
    // Fail the build if the script exits non-zero (default: true)
    isIgnoreExitValue = false
}
```

### JavaExec Task Example

```kotlin
tasks.register<JavaExec>("runCodeGenerator") {
    description = "Generates source code from the schema"
    group = "build"

    classpath = configurations.runtimeClasspath.get()
    mainClass = "com.example.codegen.Main"
    args("--schema", "schema.json", "--output", layout.buildDirectory.dir("generated-sources").get())
    jvmArgs("-Xmx512m", "-Dfile.encoding=UTF-8")
    systemProperties["codegen.strict"] = "true"
}
```

---

## Custom Task Types

For reusable task logic, define a custom task class. This is the correct approach when you want the same task type used in multiple places, or when you need proper up-to-date checking and build cache support.

### Minimal Custom Task (buildSrc or build.gradle.kts)

```kotlin
// In buildSrc/src/main/kotlin/GenerateReport.kt
// OR inline in build.gradle.kts (for single-project use)

abstract class GenerateReport : DefaultTask() {

    @get:Input
    abstract val reportTitle: Property<String>

    @get:InputDirectory
    abstract val sourceDir: DirectoryProperty

    @get:OutputFile
    abstract val reportFile: RegularFileProperty

    init {
        description = "Generates a Markdown report from source files"
        group = "reporting"
    }

    @TaskAction
    fun generate() {
        val sources = sourceDir.asFileTree.filter { it.extension == "java" }
        val output = reportFile.get().asFile
        output.parentFile.mkdirs()
        output.bufferedWriter().use { writer ->
            writer.write("# ${reportTitle.get()}\n\n")
            writer.write("Source files processed: ${sources.files.size}\n\n")
            sources.files.sortedBy { it.name }.forEach { file ->
                writer.write("- `${file.relativeTo(sourceDir.get().asFile)}`\n")
            }
        }
        logger.lifecycle("Report written to ${output.path}")
    }
}
```

### Registering and Configuring a Custom Task

```kotlin
// build.gradle.kts

tasks.register<GenerateReport>("generateReport") {
    reportTitle = "Source File Report"
    sourceDir = layout.projectDirectory.dir("src/main/java")
    reportFile = layout.buildDirectory.file("reports/source-report.md")
}

// Wire output of one task to input of another (lazy wiring — no value resolved at config time)
val compileTask = tasks.named<JavaCompile>("compileJava")
tasks.register<GenerateReport>("generateCompiledReport") {
    reportTitle = "Compiled Sources Report"
    sourceDir = compileTask.flatMap { it.destinationDirectory }
    reportFile = layout.buildDirectory.file("reports/compiled-report.md")
}
```

### Custom Task with Incremental File Processing

For tasks that process a large set of files, use `InputChanges` to implement incremental processing — only process files that changed since the last execution.

```kotlin
abstract class IncrementalProcessor : DefaultTask() {

    @get:InputDirectory
    @get:SkipWhenEmpty
    abstract val inputDir: DirectoryProperty

    @get:OutputDirectory
    abstract val outputDir: DirectoryProperty

    @TaskAction
    fun process(inputChanges: InputChanges) {
        if (inputChanges.isIncremental) {
            logger.lifecycle("Running incrementally")
        } else {
            logger.lifecycle("Running non-incrementally (full rebuild)")
            outputDir.get().asFile.deleteRecursively()
        }

        inputChanges.getFileChanges(inputDir).forEach { change ->
            val outputFile = outputDir.get().file(change.normalizedPath).asFile
            when (change.changeType) {
                ChangeType.ADDED, ChangeType.MODIFIED -> {
                    outputFile.parentFile.mkdirs()
                    outputFile.writeText(change.file.readText().uppercase())
                }
                ChangeType.REMOVED -> outputFile.delete()
            }
        }
    }
}
```

---

## Provider API (Lazy Configuration)

The Provider API is Gradle's mechanism for lazy evaluation of values. Instead of resolving a value immediately at configuration time, Providers represent a value that will be resolved later (at execution time, or when explicitly queried).

### Core Types

| Type | Writable? | Description |
|---|---|---|
| `Provider<T>` | No | Read-only lazy value; can be derived from other Providers |
| `Property<T>` | Yes | Writable lazy value; extends `Provider<T>` |
| `RegularFileProperty` | Yes | Lazy reference to a file; extends `Property<RegularFile>` |
| `DirectoryProperty` | Yes | Lazy reference to a directory; extends `Property<Directory>` |
| `ListProperty<T>` | Yes | Lazy list; has `add()`, `addAll()` |
| `MapProperty<K, V>` | Yes | Lazy map |
| `ConfigurableFileCollection` | Yes | Lazy file collection; use `files()` to add entries |

### Creating and Wiring Providers

```kotlin
// In a custom task class, abstract properties are created by Gradle's object factory:
abstract class MyTask : DefaultTask() {
    @get:Input abstract val inputText: Property<String>
    @get:OutputFile abstract val outputFile: RegularFileProperty

    @TaskAction fun run() {
        outputFile.get().asFile.writeText(inputText.get())
    }
}

// In build.gradle.kts, wire task outputs to inputs of other tasks:
val producerTask = tasks.register<MyTask>("producer") {
    inputText = "Hello, world"
    outputFile = layout.buildDirectory.file("intermediate/text.txt")
}

// `flatMap` wires the output of producer to the input of consumer.
// If producer's outputFile changes, consumer automatically becomes out of date.
tasks.register<MyTask>("consumer") {
    inputText = producerTask.flatMap { it.outputFile }.map { it.asFile.readText() }
    outputFile = layout.buildDirectory.file("final/text.txt")
}
```

### layout API

`layout` is available in any task or build script and provides `Provider`-based paths relative to the project:

```kotlin
layout.buildDirectory                  // Provider<Directory> pointing to build/
layout.buildDirectory.dir("reports")   // Provider<Directory> pointing to build/reports/
layout.buildDirectory.file("out.jar")  // Provider<RegularFile> pointing to build/out.jar
layout.projectDirectory                // Directory pointing to the project root
layout.projectDirectory.dir("src")     // Directory pointing to src/
layout.projectDirectory.file("config.json")  // RegularFile pointing to config.json
```

---

## Incremental Builds and Up-to-Date Checks

Gradle's up-to-date mechanism compares a **fingerprint** of all task inputs and outputs between the current build and the previous one. If nothing has changed, the task is marked `UP-TO-DATE` and skipped.

### Input/Output Annotations

Apply these annotations to properties in custom task classes:

| Annotation | Description |
|---|---|
| `@Input` | A scalar input value: `String`, `Int`, `Boolean`, `Enum`, etc. Serialized and hashed. |
| `@InputFile` | A single input file. Hashed by content (not path or timestamp). |
| `@InputFiles` | A collection of input files. |
| `@InputDirectory` | An input directory. All files within are hashed. |
| `@OutputFile` | A single output file produced by this task. |
| `@OutputFiles` | A collection of output files. |
| `@OutputDirectory` | An output directory. |
| `@Classpath` | A classpath input: like `@InputFiles` but order-insensitive and filtered for junk JARs. |
| `@CompileClasspath` | Classpath that ignores non-ABI changes (method body changes that don't affect the public API). |
| `@Internal` | Exclude from up-to-date checks entirely. Use for logging helpers, counters. |
| `@Console` | Like `@Internal` but specifically for properties that affect console output only. |
| `@Nested` | The annotated property is itself an object with annotated input/output properties. |
| `@Optional` | The input or output is allowed to be absent (null or missing file). |
| `@SkipWhenEmpty` | Skip the task (mark as NO-SOURCE) when the annotated `@InputFiles`/`@InputDirectory` is empty. |

### Runtime API (for ad-hoc tasks)

When you cannot annotate a class (e.g., ad-hoc tasks registered with `tasks.register`), declare inputs and outputs using the runtime API:

```kotlin
tasks.register("processTemplates") {
    // Declare inputs
    inputs.dir("src/templates")
        .withPropertyName("templates")
        .withPathSensitivity(PathSensitivity.RELATIVE)
    inputs.property("version", project.version)

    // Declare outputs
    outputs.dir(layout.buildDirectory.dir("processed-templates"))
        .withPropertyName("processedTemplates")

    doLast {
        // ... processing logic
    }
}
```

### Build Cache

When the build cache is enabled (`org.gradle.caching=true`), a task that has been run before (even on a different machine, if using a remote cache) can have its outputs restored from cache (`FROM-CACHE`) instead of being re-executed.

Requirements for a task to be cacheable:
1. Annotate the task class with `@CacheableTask`
2. All inputs must be annotated and deterministic
3. All outputs must be annotated

```kotlin
@CacheableTask
abstract class GenerateReport : DefaultTask() {
    @get:Input abstract val title: Property<String>
    @get:InputDirectory @get:PathSensitive(PathSensitivity.RELATIVE) abstract val srcDir: DirectoryProperty
    @get:OutputFile abstract val reportFile: RegularFileProperty

    @TaskAction fun generate() { /* ... */ }
}
```

---

## Dynamic (Extra) Properties

Tasks (and projects) support **extra properties** — arbitrary key/value pairs added at runtime. These are accessed via the `extra` extension. Use sparingly; prefer typed `@Input` properties on custom task classes.

```kotlin
tasks.register("myTask") {
    // Set an extra property at configuration time
    extra["buildTimestamp"] = System.currentTimeMillis()

    doLast {
        // Read it back at execution time
        println("Build started at: ${extra["buildTimestamp"]}")
    }
}

// Access extra properties on the project
extra["releaseMode"] = true
val releaseMode: Boolean by extra

// In another task or build script:
println(project.extra["releaseMode"])
```

---

## Task Ordering Summary

| Mechanism | Forces execution of both tasks? | Use case |
|---|---|---|
| `dependsOn(other)` | Yes — `other` always runs if `this` runs | `other` produces output that `this` consumes |
| `mustRunAfter(other)` | No — only orders if both are in graph | Ordering without creating a dependency |
| `shouldRunAfter(other)` | No — weak hint, may be ignored | Suggested ordering; OK to violate |
| `finalizedBy(other)` | `other` always runs after `this` | Cleanup, report generation after test |

---

## Important Patterns and Constraints

- **Never call `tasks.create()` inside a task action** (`doLast {}`). Tasks must be declared at configuration time; dynamic task creation during execution is unsupported and will be an error in Gradle 9.
- **Use `tasks.register()` (lazy) over `tasks.create()` (eager)** at all times for any task you define.
- **Use `tasks.named()` (lazy) over `tasks.getByName()` (eager)** when configuring existing tasks.
- **Task outputs must go under `layout.buildDirectory`** — never use hardcoded strings like `"build/foo"`. The `buildDirectory` property can be relocated with `layout.buildDirectory.set(...)`.
- **Avoid `project.exec {}` in a doLast** — use an `Exec` task type instead; it participates in up-to-date checks.
- **Gradle 9 deprecates configuration-time task access**: accessing a task via `tasks["name"]` or `tasks.getByName("name")` triggers deprecation warnings. Migrate to `tasks.named("name")`.
- **The `inputs.files()` / `outputs.files()` runtime API does not support build cache** — use annotated custom task classes for cacheable tasks.
- **`@Internal` is not the same as no annotation**: un-annotated properties trigger a validation warning in Gradle 7+ and will be an error in Gradle 9. Always annotate every property of a custom task class.
