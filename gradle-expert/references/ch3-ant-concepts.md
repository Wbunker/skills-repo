# Ch.3 — Ant and Gradle

> **Note:** Ant interoperability is primarily concept-based. There is no separate CLI file for Ant
> integration — all interaction happens through the `AntBuilder` object and `ant.importBuild` within
> Gradle build scripts. The CLI surface is Gradle's own (`./gradlew <task>`).

---

## Why Ant Interop?

- Many legacy projects have existing Ant builds; Gradle can call Ant tasks directly without
  rewriting them first
- Gradle embeds a full Ant runtime; the `ant` object (`AntBuilder`) is always available in any
  build script without adding a dependency
- Provides a migration path: run Ant targets from Gradle while incrementally replacing them with
  native Gradle tasks
- Enables reuse of custom Ant tasks (e.g., proprietary code-generation tasks) that have no
  Gradle equivalent

---

## The AntBuilder Object

Every Gradle build script exposes an `ant` property of type `AntBuilder`. This is a live,
embedded Ant instance — not a separate process.

```kotlin
// Adjust the verbosity of Ant's internal logging
ant.lifecycleLogLevel = AntBuilder.AntMessagePriority.INFO

// Create a directory using the Ant <mkdir> task
ant.mkdir(mapOf("dir" to "${buildDir}/generated"))

// Copy files using Ant <copy> with a nested <fileset>
ant.copy(mapOf("todir" to "$buildDir/output")) {
    ant.fileset(mapOf("dir" to "src/resources", "includes" to "**/*.xml"))
}

// Print a message via Ant <echo>
ant.echo(mapOf("message" to "Hello from Ant within Gradle"))
```

Ant task names map directly to method names on `AntBuilder`. Attributes become map entries.
Nested elements are expressed as nested lambdas or method calls within the outer block.

---

## Importing Custom Ant Tasks (Berglund Ch.3)

Custom Ant tasks distributed as JARs must be defined with `<taskdef>` before use. In Gradle
this is done through `ant.taskdef`.

```kotlin
// Add the Checkstyle JAR to a configuration so Gradle can resolve it
configurations {
    create("checkstyle")
}
dependencies {
    "checkstyle"("com.puppycrawl.tools:checkstyle:10.14.2")
}

// Register the custom Ant task with the embedded Ant runtime
ant.taskdef(
    mapOf(
        "name"      to "checkstyle",
        "classname" to "com.puppycrawl.tools.checkstyle.CheckStyleTask",
        "classpath" to configurations["checkstyle"].asPath
    )
)

// Invoke the custom Ant task
ant.invokeMethod(
    "checkstyle",
    mapOf(
        "config"          to "checkstyle.xml",
        "failOnViolation" to true
    )
)
```

`ant.invokeMethod` is the fallback for tasks whose name conflicts with a Kotlin reserved word or
where Gradle cannot generate a typed accessor.

---

## Importing an Entire Ant Build File (Berglund Ch.3)

`ant.importBuild` reads a `build.xml` and registers every Ant target as a Gradle task. This is
the core tool for phased Ant → Gradle migration.

```kotlin
// Import all targets from build.xml; rename each to avoid collisions with Gradle tasks
ant.importBuild("build.xml") { antTargetName: String ->
    "ant-$antTargetName"   // e.g., Ant target "compile" becomes Gradle task "ant-compile"
}
```

After this call:

```bash
# Run the imported Ant target as if it were a Gradle task
./gradlew ant-compile

# List all imported targets (they appear alongside native Gradle tasks)
./gradlew tasks --all | grep "^ant-"
```

The rename lambda receives the original Ant target name and must return a unique Gradle task name.
Returning `antTargetName` (identity) is only safe if no Gradle task with that name exists.

---

## Ant Target ↔ Gradle Task Dependencies (Berglund Ch.3)

Once imported, Ant targets behave like Gradle tasks for the purposes of `dependsOn` ordering.

```kotlin
// Make a native Gradle task wait for an imported Ant target to complete first
tasks.named("myGradleTask") {
    dependsOn("ant-prepare")   // "ant-prepare" is the renamed Ant target
}

// Make an imported Ant target depend on a native Gradle task
// (useful when the Ant target needs generated sources produced by Gradle)
tasks.named("ant-compile") {
    dependsOn("generateSources")
}

// Chain: generateSources → ant-prepare → myGradleTask
tasks.named("myGradleTask") {
    dependsOn("ant-prepare")
}
tasks.named("ant-prepare") {
    dependsOn("generateSources")
}
```

Gradle respects these dependency edges in its task graph. The ordering guarantee is that
`dependsOn` tasks complete before the dependent task begins.

---

## Complex Ant Configuration

### Ant Properties

Ant properties are key–value strings. Use `ant.properties` to read or write them from Gradle,
bridging Gradle values into the Ant world.

```kotlin
// Pass Gradle project version into Ant
ant.properties["my.version"] = version.toString()

// Pass a computed value
ant.properties["build.timestamp"] = java.time.Instant.now().toString()

// Read back a property set by an Ant target (after the Ant task has run)
val antResult = ant.properties["my.result.property"] as String?
```

### Ant References

For passing complex objects (classpaths, filesets) into Ant tasks:

```kotlin
// Expose a Gradle configuration as an Ant path reference
ant.references["my.classpath"] = configurations["runtimeClasspath"].asFileTree

// Use the reference in a subsequent Ant task
ant.java(mapOf("classname" to "com.example.Main", "classpathref" to "my.classpath"))
```

### Ant Conditions

```kotlin
// Set an Ant property conditionally — equivalent to Ant's <condition>
ant.condition(mapOf("property" to "isWindows")) {
    ant.os(mapOf("family" to "windows"))
}

// Use the condition result in a subsequent Ant task
ant.echo(mapOf("message" to "Running on Windows: ${ant.properties["isWindows"]}"))
```

### Ant FileSet and Path

```kotlin
// Build an Ant fileset for use in copy/zip/etc.
ant.copy(mapOf("todir" to "$buildDir/dist")) {
    ant.fileset(mapOf("dir" to "src/main/resources")) {
        ant.include(mapOf("name" to "**/*.properties"))
        ant.exclude(mapOf("name" to "**/*-local.properties"))
    }
}

// Create a named Ant path
ant.path(mapOf("id" to "compile.path")) {
    ant.pathelement(mapOf("path" to configurations["compileClasspath"].asPath))
}
```

---

## When to Use Ant Integration vs Native Gradle

| Scenario | Recommendation |
|---|---|
| Custom Ant task with no Gradle equivalent, rarely changes | Use `AntBuilder` inline in a `doLast` block |
| Large Ant project, incremental migration planned | Use `ant.importBuild` with renamed targets |
| Ant task needs to run as part of Gradle lifecycle | Wrap in a custom `Exec` task or `AntBuilder` call inside a task action |
| Ant task available as Gradle plugin | Replace with native Gradle plugin — don't use Ant |
| CI pipeline, build caching enabled | Replace Ant tasks — they don't participate in Gradle's build cache |

---

## Important Patterns & Constraints

- **Configuration cache incompatibility**: `ant.importBuild` is not compatible with Gradle's
  configuration cache (introduced in Gradle 7, enforced by default in Gradle 9). Builds using
  `importBuild` cannot enable `org.gradle.configuration-cache=true`. This is the strongest
  reason to complete Ant migration before upgrading to Gradle 9.

- **Execution phase only**: Ant tasks run at execution time. Never call `ant.*` at configuration
  time (top-level script body). Place Ant calls inside task actions (`doFirst`/`doLast`) or
  within a task's `actions` block.

  ```kotlin
  tasks.register("runAntTask") {
      doLast {
          ant.echo(mapOf("message" to "This is correct — runs at execution time"))
      }
  }
  ```

- **No incremental build**: Gradle cannot track inputs/outputs of Ant tasks. They always run
  when their Gradle wrapper task runs (they are never `UP-TO-DATE` based on their own logic).
  Declare `inputs` and `outputs` on the wrapping Gradle task to get incremental behavior.

- **Thread safety**: `AntBuilder` is not thread-safe. Don't invoke Ant tasks from parallel
  task execution workers. Use `--no-parallel` if Ant tasks must run, or isolate them in a
  single-threaded task.

- **`ant.properties` is a live map**: Reading a property before the Ant target that sets it
  has run will return `null`. Order matters; use `dependsOn` to enforce it.

- **Classpath isolation**: Custom Ant tasks loaded via `taskdef` are added to the Ant classloader,
  not Gradle's build classloader. Avoid using the same class from both contexts without
  careful classloader management.
