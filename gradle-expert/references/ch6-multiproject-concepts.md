# Ch.6 — Multi-Project Builds

See also: [Ch.6 Multi-Project CLI Reference](ch6-multiproject-cli.md)

---

## Multi-Project Structure

A multi-project Gradle build has one root directory containing a `settings.gradle.kts` that declares all subprojects. Each subproject has its own `build.gradle.kts`.

```
my-app/
├── settings.gradle.kts        ← declares all subprojects; required
├── build.gradle.kts           ← root build (optional shared config)
├── gradle/
│   └── libs.versions.toml    ← shared version catalog (available to all subprojects)
├── app/
│   └── build.gradle.kts      ← application subproject
├── lib/
│   └── build.gradle.kts      ← library subproject
└── api/
    └── build.gradle.kts      ← API/contract subproject
```

Gradle always starts from the root directory (where `settings.gradle.kts` lives), regardless of which directory `./gradlew` is invoked from.

---

## settings.gradle.kts — Root Configuration

The settings file is the entry point for every build. It must declare the root project name and all subprojects.

```kotlin
rootProject.name = "my-app"   // determines root artifact name; set explicitly

pluginManagement {
    repositories {
        gradlePluginPortal()
        mavenCentral()
    }
    // Optional: pin plugin versions centrally
    plugins {
        id("org.springframework.boot") version "3.2.0"
    }
}

dependencyResolutionManagement {
    // FAIL_ON_PROJECT_REPOS: subprojects cannot declare their own repositories
    // PREFER_SETTINGS: subproject repos used as fallback
    repositoriesMode.set(RepositoriesMode.FAIL_ON_PROJECT_REPOS)
    repositories {
        mavenCentral()
        google()
    }
}

include(":app", ":lib", ":api")

// Optional: place subprojects in non-default directories
project(":api").projectDir = file("modules/api")
project(":lib").projectDir = file("modules/lib")
```

`include()` uses colon-prefixed paths that map to directory names by default. Nested subprojects use deeper paths: `include(":platform:core", ":platform:util")`.

---

## Project Dependencies (Cross-Project)

Subprojects declare dependencies on each other using `project()`. Gradle resolves these as source-level dependencies — it compiles the depended-on project before the depending project.

```kotlin
// app/build.gradle.kts
dependencies {
    implementation(project(":lib"))      // compile + runtime dependency
    implementation(project(":api"))
    testImplementation(project(":lib"))  // can also be test-scoped
}
```

When `:app` depends on `:lib`, running `./gradlew :app:build` automatically builds `:lib` first. Circular dependencies (`:lib` depending on `:app`) are detected at configuration time and cause a build error.

`java-library` subprojects expose two configurations:
- `api` — transitive; consumers see these deps on their compile classpath
- `implementation` — non-transitive; hidden from consumers

---

## One Master Build File (allprojects / subprojects)

The root `build.gradle.kts` can configure all subprojects from a single place using `subprojects {}` or `allprojects {}`.

```kotlin
// root build.gradle.kts
allprojects {
    group = "com.example"
    version = "1.0.0"
}

subprojects {
    apply(plugin = "java")

    java {
        toolchain {
            languageVersion = JavaLanguageVersion.of(17)
        }
    }

    repositories {
        mavenCentral()
    }

    dependencies {
        "testImplementation"("org.junit.jupiter:junit-jupiter:5.10.0")
        "testRuntimeOnly"("org.junit.platform:junit-platform-launcher")
    }

    tasks.withType<Test> {
        useJUnitPlatform()
    }
}
```

String-based dependency notation (`"testImplementation"(...)`) is required in `subprojects {}` because the typed `testImplementation(...)` accessor is only generated for projects that have applied the `java` plugin before the DSL is evaluated.

> **Modern alternative**: Convention plugins (see below) are preferred over `subprojects {}` for new projects because they are more explicit, composable, and compatible with the configuration cache.

---

## Project-Specific Build Files

Each subproject has its own `build.gradle.kts` applying only the plugins and dependencies it needs.

```kotlin
// lib/build.gradle.kts
plugins {
    id("java-library")
}

dependencies {
    api("com.google.guava:guava:33.0.0-jre")            // exposed to consumers
    implementation("org.slf4j:slf4j-api:2.0.12")         // hidden from consumers
}
```

```kotlin
// app/build.gradle.kts
plugins {
    id("application")
}

application {
    mainClass = "com.example.app.Main"
}

dependencies {
    implementation(project(":lib"))
    implementation(project(":api"))
}
```

```kotlin
// api/build.gradle.kts
plugins {
    id("java-library")
}
// API module: pure interfaces, no implementation deps
```

---

## Convention Plugins — Modern Best Practice

Convention plugins are reusable build scripts stored in `buildSrc` (or an included build). Subprojects opt in by applying the convention plugin by ID. This is the recommended approach for sharing build logic in new multi-project builds.

### buildSrc Layout

```
buildSrc/
├── build.gradle.kts                           ← declares the Kotlin DSL plugin
└── src/main/kotlin/
    ├── java-library-conventions.gradle.kts   ← convention for library modules
    └── kotlin-app-conventions.gradle.kts     ← convention for application modules
```

```kotlin
// buildSrc/build.gradle.kts
plugins {
    `kotlin-dsl`
}

repositories {
    gradlePluginPortal()
    mavenCentral()
}

dependencies {
    // If convention plugins need to apply external plugins, declare them here
    implementation("org.jetbrains.kotlin:kotlin-gradle-plugin:2.0.0")
}
```

```kotlin
// buildSrc/src/main/kotlin/java-library-conventions.gradle.kts
plugins {
    `java-library`
    `maven-publish`
    jacoco
}

java {
    toolchain {
        languageVersion = JavaLanguageVersion.of(17)
    }
}

testing {
    suites {
        val test by getting(JvmTestSuite::class) {
            useJUnitJupiter("5.10.0")
        }
    }
}

tasks.jacocoTestReport {
    dependsOn(tasks.test)
    reports {
        xml.required = true
        html.required = true
    }
}

publishing {
    publications {
        create<MavenPublication>("mavenJava") {
            from(components["java"])
        }
    }
}
```

```kotlin
// buildSrc/src/main/kotlin/kotlin-app-conventions.gradle.kts
plugins {
    id("org.jetbrains.kotlin.jvm")
    application
}

kotlin {
    jvmToolchain(17)
}

testing {
    suites {
        val test by getting(JvmTestSuite::class) {
            useJUnitJupiter("5.10.0")
        }
    }
}
```

### Thin Subproject Build Files

Once convention plugins exist, individual subproject build files become minimal:

```kotlin
// lib/build.gradle.kts
plugins {
    id("java-library-conventions")   // all common config inherited
}

dependencies {
    api(libs.guava)                  // only project-specific deps
}
```

```kotlin
// app/build.gradle.kts
plugins {
    id("kotlin-app-conventions")
}

application {
    mainClass = "com.example.MainKt"
}

dependencies {
    implementation(project(":lib"))
    implementation(project(":api"))
    implementation(libs.logback.classic)
}
```

---

## allprojects vs subprojects vs Convention Plugins

| Approach | When to Use | Drawbacks |
|---|---|---|
| `allprojects {}` | Apply to root AND all subprojects | Affects root project unexpectedly; configuration cache unfriendly |
| `subprojects {}` | Apply to all subprojects at once from root | Applies to ALL subprojects including unrelated ones; configuration cache unfriendly |
| Convention plugins | Projects opt in by applying the plugin | Requires `buildSrc` or included build setup |
| **Convention plugins** | **Recommended for all new multi-project builds** | More initial setup |

**Configuration cache compatibility**: `subprojects {}` and `allprojects {}` blocks that cross-configure projects (accessing another project's tasks or extensions) break the configuration cache. Convention plugins do not have this problem.

---

## Multi-Project Task Execution

Gradle resolves task names relative to the current project. When run from the root, unqualified task names execute in all projects that define that task.

```bash
./gradlew test          # runs :app:test, :lib:test, :api:test
./gradlew build         # runs build in all subprojects
./gradlew :lib:test     # runs only lib's test task
./gradlew :app:run      # runs only app's run task
```

Gradle respects task dependencies across projects. When `:app:compileJava` depends on `:lib`, Gradle builds `:lib:jar` before `:app:compileJava`.

---

## allprojects and subprojects Blocks

```kotlin
// root build.gradle.kts
allprojects {
    group = "com.example"
    version = "1.0.0"

    // Apply to every project including root
    tasks.register("printVersion") {
        doLast { println("${project.name}: ${project.version}") }
    }
}

subprojects {
    repositories {
        mavenCentral()
    }

    tasks.register("hello") {
        doLast { println("Hello from ${project.name}") }
    }
}
```

---

## Cross-Project Task Dependencies

Explicit cross-project task dependencies are possible but generally discouraged. Prefer `project()` dependency declarations (which Gradle resolves automatically) over manual `dependsOn` with cross-project references.

```kotlin
// Explicit cross-project task dependency (use sparingly)
tasks.named("test") {
    dependsOn(project(":lib").tasks.named("jar"))
}
```

When `:app` has `implementation(project(":lib"))` in its dependencies, Gradle already ensures `:lib:jar` runs before `:app:compileJava` — no manual `dependsOn` needed.

---

## Composite Builds (includeBuild)

Composite builds allow treating a separate Gradle build as if it were a subproject. The primary use case is developing a library and its consumer simultaneously, with Gradle substituting the locally-checked-out source for the published artifact.

```kotlin
// settings.gradle.kts
includeBuild("../my-library") {
    dependencySubstitution {
        substitute(module("com.example:my-library"))
            .using(project(":"))
    }
}
```

Now, any dependency on `com.example:my-library` in the consumer project resolves to the local `../my-library` source, with full IDE support and incremental compilation.

Composite builds are also an alternative to `buildSrc` for convention plugins in large teams: a separate `build-logic` build can be included and cached more aggressively than `buildSrc`.

```kotlin
// settings.gradle.kts — build-logic as included build
includeBuild("build-logic")

// build-logic/settings.gradle.kts
rootProject.name = "build-logic"

// build-logic/build.gradle.kts
plugins { `kotlin-dsl` }
repositories { gradlePluginPortal() }
```

---

## Version Catalog — Sharing Dependencies Across Subprojects

`gradle/libs.versions.toml` is automatically available in all subprojects with no import or additional configuration.

```toml
# gradle/libs.versions.toml
[versions]
kotlin = "2.0.0"
junit = "5.10.0"
guava = "33.0.0-jre"
spring-boot = "3.2.0"
testcontainers = "1.19.0"

[libraries]
junit-jupiter        = { group = "org.junit.jupiter",   name = "junit-jupiter",         version.ref = "junit" }
junit-launcher       = { group = "org.junit.platform",  name = "junit-platform-launcher", version.ref = "junit" }
guava                = { group = "com.google.guava",    name = "guava",                 version.ref = "guava" }
testcontainers-core  = { group = "org.testcontainers",  name = "testcontainers",         version.ref = "testcontainers" }
testcontainers-junit = { group = "org.testcontainers",  name = "junit-jupiter",          version.ref = "testcontainers" }

[bundles]
testing = ["junit-jupiter", "junit-launcher"]

[plugins]
kotlin-jvm   = { id = "org.jetbrains.kotlin.jvm",   version.ref = "kotlin" }
spring-boot  = { id = "org.springframework.boot",   version.ref = "spring-boot" }
```

```kotlin
// Any subproject build.gradle.kts
dependencies {
    testImplementation(libs.junit.jupiter)
    testRuntimeOnly(libs.junit.launcher)
    implementation(libs.guava)
    testImplementation(libs.bundles.testing)   // bundle = multiple libs at once
}

plugins {
    alias(libs.plugins.kotlin.jvm)
}
```

---

## Multi-Project Performance

### Parallel Execution

```bash
./gradlew build --parallel
```

Gradle runs tasks from independent subprojects concurrently. Tasks within a single project still run sequentially (unless they are configuration-cache–compatible and have no ordering constraints).

### Configuration Cache

The configuration cache serializes the task graph after the first run. Subsequent runs skip the configuration phase entirely when inputs are unchanged.

```bash
./gradlew build --configuration-cache
```

Requirements for configuration cache compatibility:
- Avoid `subprojects {}` / `allprojects {}` that cross-reference other projects' tasks
- Avoid reading system properties or environment variables at configuration time
- Use `providers.systemProperty()` and `providers.environmentVariable()` instead

### Project Isolation

```bash
./gradlew build --project-isolation
```

Project isolation enforces that each subproject is configured independently. Prevents cross-project configuration from `subprojects {}` blocks. Required for full parallel configuration (future Gradle feature).

### Build Caching

```bash
./gradlew build --build-cache
```

Tasks with cacheable outputs (e.g., `compileJava`, `test`) can restore outputs from a local or remote cache rather than re-executing.

---

## Important Patterns and Constraints

- **Circular project dependencies** — not allowed. `:lib` depending on `:app` while `:app` depends on `:lib` is detected at configuration time with a clear error.
- **`buildSrc` invalidation** — any change to `buildSrc` invalidates the configuration cache for all projects because `buildSrc` classes are on Gradle's classpath. For large teams, prefer an included build (`build-logic`) for better cache granularity.
- **`rootProject.name`** — must be set explicitly in `settings.gradle.kts`. Without it, the directory name is used, which can vary across developer machines and break artifact names.
- **`dependencyResolutionManagement` repositories** — centralizing repositories in `settings.gradle.kts` with `FAIL_ON_PROJECT_REPOS` prevents subprojects from silently adding custom repositories and improves security and reproducibility.
- **`gradle/libs.versions.toml`** — available to all subprojects automatically. No import or `apply` needed. The `libs` accessor is generated by Gradle at configuration time.
- **Task ordering vs dependency** — `shouldRunAfter` and `mustRunAfter` control ordering only; they do not imply a dependency. If task A `shouldRunAfter` task B, running only A does not trigger B. Use `dependsOn` for true dependencies.
- **`project()` dependency resolution** — when `:app` depends on `project(":lib")`, Gradle uses the artifact configuration appropriate for the dependency scope. For `java-library` projects, `api` dependencies are transitive through `project()` references just as they would be through published artifacts.
