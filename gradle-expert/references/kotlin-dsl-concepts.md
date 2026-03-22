# Kotlin DSL — Gradle Build Scripts

---

## Why Kotlin DSL?

- **Statically typed**: IntelliJ IDEA and Android Studio provide full autocomplete, parameter
  hints, and navigation to source for every Gradle API symbol — no more guessing configuration
  block names
- **Compile-time error detection**: type mismatches and missing methods are caught when the
  script is compiled, not at execution time as with Groovy DSL
- **Default since Gradle 8.2**: `gradle init` generates `.gradle.kts` files by default; new
  projects should start with Kotlin DSL
- **Refactoring support**: IDE rename, find usages, and extract refactorings work correctly
  because types are known statically
- **Same Gradle API**: Kotlin DSL is purely syntactic — it calls the same `Project`, `Task`,
  `Configuration`, and extension objects as Groovy DSL. No capabilities are lost.
- **Consistent language**: if your project is already Kotlin, build scripts use the same
  language, toolchain, and idioms

---

## Syntax Comparison Table (Groovy vs Kotlin DSL)

| Feature | Groovy DSL | Kotlin DSL |
|---|---|---|
| File name | `build.gradle` | `build.gradle.kts` |
| Settings file | `settings.gradle` | `settings.gradle.kts` |
| String quotes | `'single'` or `"double"` | `"double"` only (Kotlin `String`) |
| Core plugin | `id 'java'` | `java` (unquoted accessor) |
| Hyphenated core plugin | `id 'java-library'` | `` `java-library` `` (backtick) |
| Community plugin | `id 'com.example.plugin' version '1.0'` | `id("com.example.plugin") version "1.0"` |
| Kotlin plugin | `id 'org.jetbrains.kotlin.jvm' version '2.0'` | `kotlin("jvm") version "2.0"` |
| Apply legacy | `apply plugin: 'java'` | `apply(plugin = "java")` — avoid; use `plugins {}` |
| Dependency | `implementation 'group:name:version'` | `implementation("group:name:version")` |
| Dependency (map) | `implementation group: 'g', name: 'n', version: 'v'` | `implementation(group = "g", name = "n", version = "v")` |
| Map literal | `[key: 'value']` | `mapOf("key" to "value")` |
| List literal | `['a', 'b']` | `listOf("a", "b")` |
| Property assignment | `sourceCompatibility = '11'` | `sourceCompatibility = JavaVersion.VERSION_11` |
| Boolean property | `buildTypes.release.minifyEnabled = true` | `buildTypes.getByName("release").isMinifyEnabled = true` |
| Task registration | `task myTask { ... }` | `tasks.register("myTask") { ... }` |
| Task by name | `tasks.myTask { ... }` | `tasks.named("myTask") { ... }` |
| Task by name + type | `tasks.test { ... }` | `tasks.named<Test>("test") { ... }` |
| Extra property (set) | `ext.myProp = 'value'` | `val myProp by extra("value")` |
| Extra property (read) | `myProp` | `val myProp: String by extra` |
| Closure | `{ ... }` | `{ ... }` (Kotlin lambda — same syntax, different type) |
| Named argument in map | `copy(from: 'src', into: 'dest')` | `copy { from("src"); into("dest") }` |
| Version catalog plugin | `alias(libs.plugins.spotless)` | `alias(libs.plugins.spotless)` (same) |

---

## plugins {} Block

The `plugins {}` block is the preferred way to apply plugins. It runs before the rest of the
script, enabling type-safe accessors to be generated.

```kotlin
plugins {
    // Core plugins — no quotes, no version
    java
    `java-library`                                     // backtick required for hyphenated names
    application
    `kotlin-dsl`                                       // for buildSrc

    // Community plugins — id + version
    id("org.springframework.boot") version "3.2.0"
    id("io.spring.dependency-management") version "1.1.4"
    id("com.github.ben-manes.versions") version "0.51.0"
    id("com.diffplug.spotless") version "6.25.0"

    // Kotlin plugins — shorthand
    kotlin("jvm") version "2.0.0"
    kotlin("plugin.spring") version "2.0.0"
    kotlin("plugin.serialization") version "2.0.0"

    // Version catalog alias
    alias(libs.plugins.spotless)

    // Declare version in root, apply in subprojects (don't apply in root)
    id("org.sonarqube") version "4.4.1.3373" apply false
}
```

Rules of the `plugins {}` block:
- Only `id(...)`, `kotlin(...)`, `alias(...)`, and core plugin accessors are allowed
- No variables, conditionals, or arbitrary Kotlin code (it must be statically analyzable)
- To apply a plugin conditionally, use `apply(plugin = "...")` outside the block after evaluation

---

## Type-Safe Accessors

When a plugin is applied in the `plugins {}` block, Gradle generates type-safe Kotlin accessors
for that plugin's contributions: configurations, extensions, and tasks.

```kotlin
// java plugin adds: java { }, compileJava, processResources, etc.
java {
    sourceCompatibility = JavaVersion.VERSION_17
    targetCompatibility = JavaVersion.VERSION_17
    withSourcesJar()
    withJavadocJar()
    toolchain {
        languageVersion = JavaLanguageVersion.of(17)
    }
}

// java-library plugin adds: api(...), implementation(...) configurations as typed methods
dependencies {
    api("com.google.guava:guava:32.1.3-jre")
    implementation("org.apache.commons:commons-lang3:3.14.0")
}

// testing plugin (Gradle 7.3+)
testing {
    suites {
        val test by getting(JvmTestSuite::class) {
            useJUnitJupiter("5.10.1")
        }
        val integrationTest by registering(JvmTestSuite::class) {
            dependencies {
                implementation(project())
            }
        }
    }
}

// application plugin
application {
    mainClass = "com.example.MainKt"
}
```

### Accessing Extensions When Accessors Are Not Generated

If a plugin is applied dynamically (via `apply(plugin = "...")` or from a condition), type-safe
accessors are not generated. Use these fallbacks:

```kotlin
// Access an extension by type
configure<com.diffplug.gradle.spotless.SpotlessExtension> {
    kotlin {
        target("**/*.kt")
        ktlint("1.1.0")
    }
}

// Get a reference without configuring
val spotless = the<com.diffplug.gradle.spotless.SpotlessExtension>()

// Access a task by type without an accessor
tasks.withType<JavaCompile>().configureEach {
    options.encoding = "UTF-8"
    options.compilerArgs.add("-Xlint:all")
}
```

---

## Lazy Task Configuration

Lazy configuration is critical for performance. Eagerly resolving tasks forces configuration of
all tasks even when only one is requested. Always prefer `tasks.named` over `tasks.getByName`
and `tasks.register` over `tasks.create`.

```kotlin
// CORRECT — lazy: the lambda only runs if "test" is in the task graph
tasks.named<Test>("test") {
    useJUnitPlatform()
    maxHeapSize = "512m"
    jvmArgs("-XX:+EnableDynamicAgentLoading")
    testLogging {
        events("passed", "skipped", "failed")
        showStandardStreams = false
    }
    systemProperty("spring.profiles.active", "test")
}

// CORRECT — lazy registration of a new task
tasks.register<Copy>("copyArtifacts") {
    from(tasks.named<Jar>("jar").map { it.archiveFile })
    into(layout.buildDirectory.dir("dist"))
    rename { "app.jar" }
}

// CORRECT — configure all tasks of a type lazily
tasks.withType<JavaCompile>().configureEach {
    options.encoding = "UTF-8"
    options.release = 17
}

// INCORRECT — eager: forces configuration of "test" even if not running it
tasks.getByName<Test>("test") {        // resolves immediately
    useJUnitPlatform()
}

// INCORRECT — eager task creation
tasks.create<Copy>("copyArtifacts") {  // always configured
    // ...
}
```

### Task Wiring with Lazy Providers

```kotlin
// Wire task outputs to task inputs without forcing resolution
val generateSources = tasks.register<JavaExec>("generateSources") {
    mainClass = "com.example.Generator"
    classpath = configurations["generatorClasspath"]
    outputs.dir(layout.buildDirectory.dir("generated/sources"))
}

tasks.named<JavaCompile>("compileJava") {
    // dependsOn is inferred from the input wiring — no explicit dependsOn needed
    source(generateSources.map { it.outputs.files })
}
```

---

## Extra Properties

Extra properties attach arbitrary data to Gradle objects (`Project`, `Task`, etc.).

```kotlin
// Declare and initialize in build.gradle.kts
val myVersion: String by extra("1.2.3")
val isRelease: Boolean by extra { !version.toString().endsWith("SNAPSHOT") }

// Read a property defined in gradle.properties (type-safe)
val javaVersion: String by project   // reads from gradle.properties: javaVersion=17

// Read with a default if not set
val ciMode: String = project.findProperty("ci")?.toString() ?: "false"

// Set on a sub-object
tasks.named("jar") {
    extra["buildTime"] = java.time.Instant.now().toString()
}
```

```properties
# gradle.properties
javaVersion=17
myVersion=1.2.3
org.gradle.jvmargs=-Xmx2g -XX:+HeapDumpOnOutOfMemoryError
org.gradle.parallel=true
org.gradle.caching=true
```

---

## buildSrc and Precompiled Script Plugins

`buildSrc` is a special directory that Gradle compiles before the main build. It is the standard
place for shared build logic (convention plugins) in single-repo builds.

### Directory Layout

```
buildSrc/
├── build.gradle.kts                              ← must apply kotlin-dsl
├── settings.gradle.kts                           ← optional but recommended
└── src/
    └── main/
        └── kotlin/
            ├── my-java-conventions.gradle.kts    ← convention plugin
            ├── my-kotlin-conventions.gradle.kts
            └── my-publish-conventions.gradle.kts
```

### buildSrc/build.gradle.kts

```kotlin
plugins {
    `kotlin-dsl`
}

repositories {
    mavenCentral()
}

// Add dependencies needed by convention plugins
dependencies {
    implementation("com.diffplug.spotless:spotless-plugin-gradle:6.25.0")
}
```

### buildSrc/settings.gradle.kts

```kotlin
rootProject.name = "buildSrc"

dependencyResolutionManagement {
    repositories {
        mavenCentral()
    }
}
```

### Convention Plugin — Java Conventions

```kotlin
// buildSrc/src/main/kotlin/my-java-conventions.gradle.kts
plugins {
    java
}

java {
    toolchain {
        languageVersion = JavaLanguageVersion.of(17)
    }
    withSourcesJar()
}

tasks.named<Test>("test") {
    useJUnitPlatform()
    maxHeapSize = "512m"
}

tasks.withType<JavaCompile>().configureEach {
    options.encoding = "UTF-8"
    options.compilerArgs.addAll(listOf("-Xlint:unchecked", "-Xlint:deprecation"))
}
```

### Convention Plugin — Kotlin Conventions

```kotlin
// buildSrc/src/main/kotlin/my-kotlin-conventions.gradle.kts
plugins {
    id("my-java-conventions")   // compose convention plugins
    kotlin("jvm")
}

kotlin {
    jvmToolchain(17)
    compilerOptions {
        freeCompilerArgs.addAll("-Xjsr305=strict", "-opt-in=kotlin.RequiresOptIn")
        apiVersion = org.jetbrains.kotlin.gradle.dsl.KotlinVersion.KOTLIN_2_0
    }
}
```

### Convention Plugin — Publish Conventions

```kotlin
// buildSrc/src/main/kotlin/my-publish-conventions.gradle.kts
plugins {
    `maven-publish`
    signing
}

publishing {
    publications {
        create<MavenPublication>("mavenJava") {
            from(components["java"])
        }
    }
    repositories {
        maven {
            name = "GitHubPackages"
            url = uri("https://maven.pkg.github.com/${System.getenv("GITHUB_REPOSITORY") ?: "owner/repo"}")
            credentials {
                username = System.getenv("GITHUB_ACTOR")
                password = System.getenv("GITHUB_TOKEN")
            }
        }
    }
}

signing {
    val signingKey: String? by project
    val signingPassword: String? by project
    if (signingKey != null) {
        useInMemoryPgpKeys(signingKey, signingPassword)
        sign(publishing.publications["mavenJava"])
    }
}
```

### Applying Convention Plugins in Subprojects

```kotlin
// subproject-a/build.gradle.kts
plugins {
    id("my-java-conventions")
    id("my-publish-conventions")
}

dependencies {
    implementation("org.apache.commons:commons-lang3:3.14.0")
}
```

---

## Settings DSL in Kotlin

```kotlin
// settings.gradle.kts
rootProject.name = "my-app"

// Include subprojects
include(":app")
include(":lib")
include(":lib:core")       // nested subproject

// Rename a subproject directory (if dir name differs from project name)
project(":lib:core").projectDir = file("libraries/core")

// Plugin management (where Gradle looks for plugins)
pluginManagement {
    repositories {
        gradlePluginPortal()
        mavenCentral()
        google()
    }
    // Pin a plugin version for all subprojects
    plugins {
        id("org.springframework.boot") version "3.2.0"
    }
}

// Dependency resolution management (where Gradle looks for libraries)
dependencyResolutionManagement {
    repositoriesMode.set(RepositoriesMode.FAIL_ON_PROJECT_REPOS)
    repositories {
        mavenCentral()
        google()
    }
    // Enable version catalog
    versionCatalogs {
        create("libs") {
            from(files("gradle/libs.versions.toml"))
        }
    }
}

// Feature preview flags
enableFeaturePreview("TYPESAFE_PROJECT_ACCESSORS")  // enables projects.app, projects.lib
```

---

## Multi-Project Build Structure

```kotlin
// root build.gradle.kts
plugins {
    // Declare versions of plugins used in subprojects (don't apply here)
    id("org.springframework.boot") version "3.2.0" apply false
    kotlin("jvm") version "2.0.0" apply false
}

// Configuration shared across ALL subprojects
allprojects {
    group = "com.example"
    version = "1.0.0"
}

// Configuration for subprojects only (excludes root)
subprojects {
    apply(plugin = "my-java-conventions")  // or use convention plugins per subproject
    repositories {
        mavenCentral()
    }
}

// Target a specific subproject from the root
project(":lib") {
    dependencies {
        // dependencies for lib
    }
}
```

---

## Dependency Configuration DSL

```kotlin
dependencies {
    // Standard scopes
    implementation("org.apache.commons:commons-lang3:3.14.0")
    api("com.google.guava:guava:32.1.3-jre")                  // java-library only
    compileOnly("org.projectlombok:lombok:1.18.30")
    annotationProcessor("org.projectlombok:lombok:1.18.30")
    runtimeOnly("org.postgresql:postgresql:42.7.1")
    testImplementation("org.junit.jupiter:junit-jupiter:5.10.1")
    testRuntimeOnly("org.junit.platform:junit-platform-launcher")

    // BOM import
    implementation(platform("org.springframework.boot:spring-boot-dependencies:3.2.0"))

    // Local project dependency
    implementation(project(":lib"))
    implementation(project(":lib:core"))

    // File dependency (avoid; use a repository)
    implementation(files("libs/proprietary.jar"))
    implementation(fileTree("libs") { include("*.jar") })

    // Dependency with exclusion
    implementation("org.springframework:spring-core:6.1.0") {
        exclude(group = "commons-logging", module = "commons-logging")
    }

    // Force a version (override transitive)
    implementation("com.fasterxml.jackson.core:jackson-databind:2.16.0") {
        isForce = true
    }

    // Dependency constraints (preferred over force)
    constraints {
        implementation("commons-codec:commons-codec:1.16.0") {
            because("earlier versions have a known security vulnerability")
        }
    }
}
```

---

## Repository DSL

```kotlin
repositories {
    mavenCentral()
    google()

    // Custom Maven repo
    maven {
        url = uri("https://repo.example.com/maven2")
        credentials {
            username = providers.gradleProperty("repoUser").get()
            password = providers.gradleProperty("repoPassword").get()
        }
        // Content filtering — only use this repo for specific groups
        content {
            includeGroup("com.example")
            includeGroupByRegex("com\\.example\\..*")
        }
        // Only resolve releases (not snapshots)
        mavenContent {
            releasesOnly()
        }
    }

    // Ivy repo
    ivy {
        url = uri("https://repo.example.com/ivy")
        layout("pattern") {
            artifact("[organisation]/[module]/[revision]/[artifact]-[revision].[ext]")
        }
    }
}
```

---

## Task DSL Patterns

```kotlin
// Register a new task with a type
tasks.register<Zip>("packageDist") {
    group = "distribution"
    description = "Packages the distribution as a ZIP file"
    archiveFileName = "app-${project.version}.zip"
    destinationDirectory = layout.buildDirectory.dir("distributions")
    from(tasks.named<Jar>("jar"))
    from("scripts") { into("bin") }
    into("lib") { from(configurations.runtimeClasspath) }
}

// Configure an existing task (from plugin)
tasks.named<Jar>("jar") {
    manifest {
        attributes(
            "Main-Class" to "com.example.MainKt",
            "Implementation-Version" to project.version,
            "Built-By" to System.getProperty("user.name"),
            "Build-Jdk" to System.getProperty("java.version")
        )
    }
    // Fat JAR: include all runtime dependencies
    from(configurations.runtimeClasspath.get().map { if (it.isDirectory) it else zipTree(it) })
    duplicatesStrategy = DuplicatesStrategy.EXCLUDE
}

// Custom task class defined in buildSrc
tasks.register<com.example.build.GenerateTask>("generateCode") {
    inputDir = layout.projectDirectory.dir("src/main/templates")
    outputDir = layout.buildDirectory.dir("generated/sources")
}

// Task ordering without dependency
tasks.named("test") {
    mustRunAfter("spotlessCheck")    // if both run, test runs after spotlessCheck
    shouldRunAfter("integrationTest")  // soft ordering
}

// Lifecycle task dependencies
tasks.named("check") {
    dependsOn(tasks.named("integrationTest"))
}
```

---

## Source Sets

```kotlin
sourceSets {
    main {
        java {
            srcDir("src/main/java")
            srcDir(layout.buildDirectory.dir("generated/sources"))
        }
        resources {
            srcDir("src/main/resources")
        }
    }
    test {
        java { srcDir("src/test/java") }
    }
    // Custom source set
    create("integrationTest") {
        java { srcDir("src/integrationTest/java") }
        resources { srcDir("src/integrationTest/resources") }
        compileClasspath += sourceSets["main"].output + configurations["testRuntimeClasspath"]
        runtimeClasspath += output + compileClasspath
    }
}

// Register integration test task for the custom source set
val integrationTest = tasks.register<Test>("integrationTest") {
    description = "Runs integration tests"
    group = "verification"
    testClassesDirs = sourceSets["integrationTest"].output.classesDirs
    classpath = sourceSets["integrationTest"].runtimeClasspath
    shouldRunAfter("test")
    useJUnitPlatform()
}

tasks.named("check") { dependsOn(integrationTest) }
```

---

## Migrating from Groovy to Kotlin DSL

Follow these steps in order. Fix compile errors after each rename before proceeding.

**Step 1: Rename files**
```bash
mv settings.gradle settings.gradle.kts
mv build.gradle build.gradle.kts
# For each subproject:
mv subproject/build.gradle subproject/build.gradle.kts
```

**Step 2: Fix string quotes**
- Change all `'single-quoted strings'` to `"double-quoted strings"`
- `'org.springframework.boot'` → `"org.springframework.boot"`

**Step 3: Fix plugin declarations**
```kotlin
// Before (Groovy)
plugins {
    id 'java'
    id 'org.springframework.boot' version '3.2.0'
}

// After (Kotlin)
plugins {
    java
    id("org.springframework.boot") version "3.2.0"
}
```

**Step 4: Fix `apply plugin` calls** (if outside `plugins {}`)
```kotlin
// Before
apply plugin: 'checkstyle'
// After
apply(plugin = "checkstyle")
// Better: move into plugins { } block if possible
```

**Step 5: Fix property assignments**
```kotlin
// Before
sourceCompatibility = '17'
group = 'com.example'
// After
java { sourceCompatibility = JavaVersion.VERSION_17 }
group = "com.example"
```

**Step 6: Fix dependency configurations**
```kotlin
// Before (Groovy — old API)
compile 'com.google.guava:guava:32.0.0'
testCompile 'junit:junit:4.13.2'
// After (Kotlin — current API)
implementation("com.google.guava:guava:32.0.0")
testImplementation("junit:junit:4.13.2")
```

**Step 7: Fix task definitions**
```kotlin
// Before (Groovy)
task myTask(type: Copy) {
    from 'src'
    into 'dest'
}
// After (Kotlin)
tasks.register<Copy>("myTask") {
    from("src")
    into("dest")
}
```

**Step 8: Fix closures and named parameters**
```kotlin
// Before (Groovy)
jar { manifest { attributes 'Main-Class': 'com.example.Main' } }
// After (Kotlin)
tasks.named<Jar>("jar") {
    manifest { attributes("Main-Class" to "com.example.Main") }
}
```

**Step 9: Fix `ext` properties**
```kotlin
// Before (Groovy)
ext { myVersion = '1.0' }
println myVersion
// After (Kotlin)
val myVersion by extra("1.0")
println(myVersion)
```

---

## Common Kotlin DSL Gotchas

### No `GString` interpolation in identifiers

Kotlin strings use `$variable` or `${expression}` syntax, same as Groovy. The difference is
there are no GStrings — everything is a plain Kotlin `String`:

```kotlin
val version = "1.0.0"
val artifact = "my-app-$version.jar"          // correct
val dir = "${layout.buildDirectory.get()}/dist"  // correct
```

### Boolean properties have `is` prefix

Gradle model properties that are Booleans often follow JavaBean naming: `isMinifyEnabled`,
`isTransitive`, `isForce`. Access them with the prefix:

```kotlin
dependencies {
    implementation("com.example:lib:1.0") {
        isTransitive = false   // not: transitive = false
        isForce = true
    }
}
```

### `String` vs `Provider<String>`

Gradle uses lazy `Provider<T>` types for many properties. Don't call `.get()` at configuration
time if you can avoid it — keep values lazy:

```kotlin
// Lazy — preferred
val outputDir = layout.buildDirectory.dir("generated")  // Provider<Directory>

// Eager — forces resolution at configuration time
val outputDirPath = layout.buildDirectory.dir("generated").get().asFile.path  // String
```

### Configuration cache — avoid capturing `project` in task actions

```kotlin
// WRONG — captures `project` reference; breaks configuration cache
tasks.register("myTask") {
    doLast {
        println(project.version)   // project is not serializable
    }
}

// CORRECT — capture only the value
val ver = project.version.toString()
tasks.register("myTask") {
    doLast {
        println(ver)
    }
}
```

### `plugins {}` block restrictions

```kotlin
// WRONG — variables not allowed in plugins block
val springVersion = "3.2.0"
plugins {
    id("org.springframework.boot") version springVersion  // compile error
}

// CORRECT — use version catalog or literal version
plugins {
    alias(libs.plugins.springBoot)       // version catalog
    id("org.springframework.boot") version "3.2.0"  // literal
}
```

### `buildDir` is deprecated — use `layout.buildDirectory`

```kotlin
// DEPRECATED
val outputDir = File(buildDir, "generated")

// CORRECT
val outputDir = layout.buildDirectory.dir("generated")
```

### IDE shows errors but build succeeds

This usually means the IDE hasn't indexed the generated type-safe accessors. Fix:
1. Run `./gradlew --rerun-tasks help` to force script compilation
2. In IntelliJ: **File → Sync Gradle Project** (or **Reload All Gradle Projects**)
3. If using buildSrc: ensure `buildSrc/build.gradle.kts` has `kotlin-dsl` plugin and repositories

### `classpath` in `buildscript {}` (legacy)

Some older patterns use `buildscript {}` to add to the script classpath. With the `plugins {}`
block this is unnecessary for plugins. For non-plugin dependencies in build scripts, it remains:

```kotlin
buildscript {
    repositories { mavenCentral() }
    dependencies {
        classpath("com.example:build-helper:1.0")  // available in the script itself
    }
}
```

Avoid `buildscript {}` for anything that can be moved to `buildSrc` or a convention plugin.
