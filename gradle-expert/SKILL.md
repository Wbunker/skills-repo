---
name: gradle-expert
description: >
  Deep Gradle expertise for building, testing, and publishing JVM projects. Organized around
  Tim Berglund's "Building and Testing with Gradle" (O'Reilly) chapter structure, extended with
  modern Gradle 8/9 features. Use when the user asks about: writing build.gradle.kts or
  build.gradle files, declaring tasks and plugins, configuring dependencies and repositories,
  testing with JUnit 5 / TestNG / Spock, multi-project builds, the Gradle wrapper, Kotlin DSL
  vs Groovy DSL, version catalogs (libs.versions.toml), the build lifecycle (initialization /
  configuration / execution), custom tasks or plugins, the build cache, configuration cache,
  Gradle daemon, publishing to Maven Central or Artifactory, Ant/Maven interoperability,
  dependency resolution strategies, or any Gradle CLI command (./gradlew). Also use for
  "gradle init" scaffolding, build scan analysis, and Gradle 9 migration guidance.
---

# Gradle Expert

*Based on "Building and Testing with Gradle" by Tim Berglund & Matthew McCullough (O'Reilly, 2011), extended with Gradle 8/9 (2025) best practices.*

## Core Approach

1. **Identify the concern** — which chapter/domain does the question touch? (Tasks, Testing, Multi-project, Dependencies, Performance, Publishing?)
2. **Default to Kotlin DSL** for new code (`.gradle.kts`); show Groovy DSL equivalent only when explicitly asked or the project already uses it
3. **Prefer declarative over imperative** — use plugins, configurations, and Provider API rather than raw imperative task logic
4. **Incremental first** — annotate task inputs/outputs; use build cache; enable configuration cache
5. **Check Gradle version** — Gradle 9 (Java 17 minimum, config cache preferred); Gradle 8 (widely deployed); Gradle 7 (legacy)

## Kotlin DSL Default

All code examples use **Kotlin DSL** (`build.gradle.kts`) unless the user's project clearly uses Groovy. Key Kotlin DSL differences:
- String quotes: `"double"` only (no single quotes)
- Plugin blocks: `kotlin("jvm")` not `id 'org.jetbrains.kotlin.jvm'`
- `tasks.named<TaskType>("name") { }` for lazy task configuration
- `val` / `by` for property delegation: `val greeting: String by project`

## Reference Files

Reference files use a **2-tier system** mirroring the book's chapter structure. Load the chapter reference when the question touches that domain.

**Tier 1 — Chapter Indexes** (load to navigate to the right topic):

| Reference | Load when... |
|---|---|
| [ch1-fundamentals-concepts.md](references/ch1-fundamentals-concepts.md) | Gradle installation, the build file, `./gradlew`, wrapper setup, build lifecycle phases, `gradle init`, project structure |
| [ch1-fundamentals-cli.md](references/ch1-fundamentals-cli.md) | CLI flags (`--info`, `--debug`, `--scan`, `--rerun-tasks`), wrapper commands, `gradle init` scaffolding |
| [ch2-tasks-concepts.md](references/ch2-tasks-concepts.md) | Task declaration, `doFirst`/`doLast`, `dependsOn`, task types (Copy/Jar/Exec), custom task classes, Provider API, `@Input`/`@OutputFile` |
| [ch2-tasks-cli.md](references/ch2-tasks-cli.md) | `./gradlew tasks`, running tasks, task filtering, `--rerun`, `--dry-run`, `--continuous` |
| [ch3-ant-concepts.md](references/ch3-ant-concepts.md) | Ant interop, `AntBuilder`, importing Ant tasks/build files, Ant target ↔ Gradle task dependencies |
| [ch4-maven-concepts.md](references/ch4-maven-concepts.md) | Maven POM ↔ Gradle mapping, `maven-publish` plugin, `pom {}` DSL, local Maven repo install |
| [ch5-testing-concepts.md](references/ch5-testing-concepts.md) | JUnit 5 setup, TestNG, Spock, test suites DSL, parallel execution, `maxParallelForks`, test filtering, coverage with JaCoCo |
| [ch5-testing-cli.md](references/ch5-testing-cli.md) | `--tests` filter, `--fail-fast`, test dry-run, test report paths, rerunning failed tests |
| [ch6-multiproject-concepts.md](references/ch6-multiproject-concepts.md) | `settings.gradle.kts`, `include()`, project dependencies, `allprojects`/`subprojects`, convention plugins, composite builds (`includeBuild`) |
| [ch6-multiproject-cli.md](references/ch6-multiproject-cli.md) | Running tasks in subprojects, `--project-dir`, `:subproject:task` syntax, dependency insights across projects |
| [kotlin-dsl-concepts.md](references/kotlin-dsl-concepts.md) | Kotlin DSL vs Groovy DSL, type-safe accessors, precompiled script plugins, IDE setup, migrating from Groovy |
| [dependency-management-concepts.md](references/dependency-management-concepts.md) | Version catalogs (`libs.versions.toml`), configurations (`implementation`/`api`/`compileOnly`), resolution strategies, dependency locking, BOM imports |
| [dependency-management-cli.md](references/dependency-management-cli.md) | `dependencies` task, `dependencyInsight`, `--write-locks`, `./gradlew dependencies --configuration` |
| [plugins-concepts.md](references/plugins-concepts.md) | Core plugins (java, application, kotlin), community plugins (shadow, spotless), custom tasks and plugins, `buildSrc`, precompiled script plugins |
| [performance-concepts.md](references/performance-concepts.md) | Gradle daemon, build cache, configuration cache, incremental compilation, `gradle.properties` tuning, parallel execution |
| [performance-cli.md](references/performance-cli.md) | `--build-cache`, `--configuration-cache`, `--parallel`, `--scan`, profiling with `--profile` |
| [publishing-concepts.md](references/publishing-concepts.md) | `maven-publish` plugin, signing plugin, Maven Central (Sonatype), Artifactory publishing, SBOM generation |

## Build Lifecycle Quick Reference

| Phase | What Happens | Key File |
|---|---|---|
| **Initialization** | `settings.gradle.kts` evaluated; project list determined | `settings.gradle.kts` |
| **Configuration** | All `build.gradle.kts` files evaluated; task graph assembled | `build.gradle.kts` |
| **Execution** | Selected tasks run in dependency order | Tasks with `@TaskAction` / `doLast {}` |

> Configuration cache skips the Configuration phase on incremental builds when nothing has changed.

## Common Patterns

**Standard Java project:**
```kotlin
plugins { id("java") }
java { toolchain { languageVersion = JavaLanguageVersion.of(17) } }
dependencies { testImplementation("org.junit.jupiter:junit-jupiter:5.10.0") }
tasks.test { useJUnitPlatform() }
```

**Multi-project root settings:**
```kotlin
rootProject.name = "my-app"
include(":app", ":lib", ":api")
```

**Version catalog dependency:**
```kotlin
// build.gradle.kts
dependencies { implementation(libs.guava) }
// gradle/libs.versions.toml: [libraries] guava = { group = "com.google.guava", name = "guava", version = "33.0.0-jre" }
```
