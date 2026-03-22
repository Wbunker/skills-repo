# Gradle Plugins

Plugins extend the Gradle build model by adding tasks, configurations, conventions, and extensions to a project. They are the primary mechanism for reusing build logic.

## Core / Built-in Plugins

Core plugins ship with Gradle and require no version declaration. They are applied by their short ID.

| Plugin ID | Purpose | Key Tasks Added |
|---|---|---|
| `java` | Compile Java source, run tests, create JAR | `compileJava`, `processResources`, `classes`, `test`, `jar` |
| `java-library` | Library with `api`/`implementation` separation | all of `java` plus `javadocJar`, `sourcesJar` (with `java.withJavadocJar()`) |
| `application` | Executable JVM app with start scripts and distributions | `run`, `startScripts`, `distZip`, `distTar`, `installDist` |
| `kotlin("jvm")` | Kotlin JVM compilation | `compileKotlin`, `compileTestKotlin` |
| `maven-publish` | Publish artifacts to Maven repositories | `publish`, `publishToMavenLocal`, `generatePomFileFor*` |
| `signing` | GPG-sign artifacts for Maven Central | `sign`, `signMavenJavaPublication` |
| `jacoco` | JaCoCo code coverage reports | `jacocoTestReport`, `jacocoTestCoverageVerification` |
| `java-test-fixtures` | Shared test fixtures accessible from other projects | `testFixturesJar` |
| `groovy` | Groovy compilation (alongside or instead of Java) | `compileGroovy`, `compileTestGroovy` |
| `scala` | Scala compilation | `compileScala`, `compileTestScala` |
| `distribution` | Package project outputs into zip/tar archives | `distZip`, `distTar`, `installDist`, `assembleDist` |
| `war` | Build a WAR file for servlet containers | `war` |
| `ear` | Build an EAR file for Java EE containers | `ear` |
| `checkstyle` | Checkstyle static analysis | `checkstyleMain`, `checkstyleTest` |
| `pmd` | PMD static analysis | `pmdMain`, `pmdTest` |
| `base` | Lifecycle tasks only (`assemble`, `check`, `build`, `clean`) | `assemble`, `check`, `build`, `clean` |
| `version-catalog` | Generate and publish a version catalog | `generateCatalogAsToml` |

## Plugin Application

Always use the `plugins {}` block at the top of the build file. It is evaluated before the rest of the build script and enables static type-safe accessors for extensions and tasks.

```kotlin
// build.gradle.kts

plugins {
    // Core plugins: no version, no quotes needed (or backtick for hyphenated names)
    java
    `java-library`
    `maven-publish`
    signing
    jacoco

    // Kotlin shorthand for org.jetbrains.kotlin.jvm
    kotlin("jvm") version "2.0.0"
    kotlin("plugin.spring") version "2.0.0"    // makes Spring @Configuration classes open
    kotlin("plugin.jpa") version "2.0.0"       // makes JPA entity classes open

    // Community plugins by full ID
    id("org.springframework.boot") version "3.2.0"
    id("io.spring.dependency-management") version "1.1.4"

    // From version catalog (preferred for multi-project builds)
    alias(libs.plugins.spotless)
    alias(libs.plugins.shadow)
}
```

Backtick notation is required for any plugin accessor whose name contains a hyphen (`java-library`, `maven-publish`, etc.).

Legacy application style — avoid for new code:

```kotlin
// Old style — loses type-safe accessors
apply(plugin = "java")
apply(plugin = "maven-publish")
```

## Community Plugins

### Shadow (Fat JAR / Uber JAR)

Packages the project and all its runtime dependencies into a single self-contained JAR. Essential for AWS Lambda, CLI tools, and deployments without a dependency management layer.

```kotlin
plugins {
    id("com.gradleup.shadow") version "9.0.0"
}

tasks.shadowJar {
    archiveClassifier = ""          // replace the standard jar as the primary artifact
    mergeServiceFiles()             // merge META-INF/services/* for ServiceLoader
    manifest {
        attributes["Main-Class"] = "com.example.MainKt"
    }
    // Relocate a dependency to avoid classpath conflicts
    relocate("com.google.common", "shadow.com.google.common")
}

// Ensure shadowJar is built as part of assemble
tasks.assemble { dependsOn(tasks.shadowJar) }
```

Build and run:

```bash
./gradlew shadowJar
java -jar build/libs/myapp-1.0.0.jar
```

### Spotless (Code Formatting)

Enforces consistent code style across the project. Run `spotlessApply` to auto-format; `spotlessCheck` in CI to fail on unformatted code.

```kotlin
plugins {
    id("com.diffplug.spotless") version "6.25.0"
}

spotless {
    kotlin {
        ktlint("1.2.1")
        // ktfmt("0.46")  // alternative: Google style via ktfmt
        trimTrailingWhitespace()
        endWithNewline()
        targetExclude("build/**/*.kt")
    }
    java {
        googleJavaFormat("1.19.2")
        importOrder()
        removeUnusedImports()
        trimTrailingWhitespace()
        endWithNewline()
    }
    kotlinGradle {
        ktlint("1.2.1")
    }
    // Format JSON, YAML, XML, etc.
    format("misc") {
        target("**/*.md", "**/*.yaml", "**/*.yml")
        trimTrailingWhitespace()
        endWithNewline()
    }
}
```

Integrate with CI:

```bash
./gradlew spotlessApply    # auto-format all files (run locally before committing)
./gradlew spotlessCheck    # check formatting without modifying (use in CI)
```

### Versions (Dependency Updates)

Reports which dependencies have newer versions available.

```kotlin
plugins {
    id("com.github.ben-manes.versions") version "0.51.0"
}

// Optional: filter to stable releases only
fun isStable(version: String): Boolean {
    val stableKeyword = listOf("RELEASE", "FINAL", "GA").any { version.uppercase().contains(it) }
    val regex = "^[0-9,.v-]+(-r)?$".toRegex()
    return stableKeyword || regex.matches(version)
}

tasks.dependencyUpdates {
    rejectVersionIf { !isStable(candidate.version) }
}
```

```bash
./gradlew dependencyUpdates
./gradlew dependencyUpdates -Drevision=release  # stable releases only
```

### SonarQube / SonarCloud

Static analysis, code smell detection, security vulnerability scanning, and coverage reporting.

```kotlin
plugins {
    id("org.sonarqube") version "5.0.0.4638"
    jacoco
}

sonar {
    properties {
        property("sonar.projectKey", "my-org_my-project")
        property("sonar.organization", "my-org")             // SonarCloud only
        property("sonar.host.url", "https://sonarcloud.io") // or self-hosted URL
        property("sonar.coverage.jacoco.xmlReportPaths",
            "${layout.buildDirectory.get()}/reports/jacoco/test/jacocoTestReport.xml")
        property("sonar.qualitygate.wait", "true")           // block until quality gate passes
    }
}

// Ensure coverage report is generated before sonar analysis
tasks.sonar { dependsOn(tasks.jacocoTestReport) }
```

```bash
./gradlew sonar -Dsonar.token=$SONAR_TOKEN
```

### Test Retry

Automatically retries flaky tests before marking them as failed. Reduces false build failures from intermittent infrastructure issues.

```kotlin
plugins {
    id("org.gradle.test-retry") version "1.5.9"
}

tasks.test {
    retry {
        maxRetries = 2              // retry each failing test up to 2 times
        maxFailures = 5             // give up if more than 5 total failures
        failOnPassedAfterRetry = false  // treat a pass-on-retry as success
    }
}
```

### Kotlin Spring and JPA Plugins

Spring requires open classes (Kotlin classes are `final` by default). The Kotlin Spring and JPA plugins automatically open annotated classes at compile time.

```kotlin
plugins {
    kotlin("jvm") version "2.0.0"
    kotlin("plugin.spring") version "2.0.0"   // opens @Component, @Service, @Repository, @Controller, @Configuration
    kotlin("plugin.jpa") version "2.0.0"      // opens @Entity, @MappedSuperclass, @Embeddable; adds no-arg constructors
}
```

### OWASP Dependency Check (Security Vulnerability Scanning)

```kotlin
plugins {
    id("org.owasp.dependencycheck") version "10.0.3"
}

dependencyCheck {
    failBuildOnCVSS = 7.0f          // fail build on HIGH or CRITICAL vulnerabilities
    suppressionFile = "owasp-suppressions.xml"
    nvd {
        apiKey = System.getenv("NVD_API_KEY") ?: ""
    }
}
```

```bash
./gradlew dependencyCheckAnalyze
```

### CycloneDX SBOM

Generates a Software Bill of Materials in CycloneDX format.

```kotlin
plugins {
    id("org.cyclonedx.bom") version "1.10.0"
}

tasks.cyclonedxBom {
    setProjectType("library")       // or "application", "firmware", "container"
    setSchemaVersion("1.5")
    setIncludeLicenseText(true)
}
```

```bash
./gradlew cyclonedxBom
# Output: build/reports/bom.json and build/reports/bom.xml
```

## Custom Tasks

Custom task classes define reusable, incremental units of build logic with declared inputs and outputs. Gradle uses these declarations to determine whether the task is up-to-date or can be loaded from cache.

```kotlin
// Can be defined in build.gradle.kts directly, or in buildSrc/

abstract class GenerateVersionFile : DefaultTask() {
    @get:Input
    abstract val version: Property<String>

    @get:Input
    abstract val buildTimestamp: Property<String>

    @get:OutputFile
    abstract val outputFile: RegularFileProperty

    @TaskAction
    fun generate() {
        val file = outputFile.get().asFile
        file.parentFile.mkdirs()
        file.writeText(
            """
            version=${version.get()}
            build.timestamp=${buildTimestamp.get()}
            """.trimIndent()
        )
    }
}

tasks.register<GenerateVersionFile>("generateVersion") {
    version = project.version.toString()
    buildTimestamp = providers.systemProperty("build.timestamp").orElse("unknown")
    outputFile = layout.buildDirectory.file("generated/version.properties")
}

// Wire to processResources so the file is included in the JAR
tasks.processResources {
    from(tasks.named("generateVersion"))
}
```

Key annotations for incremental task support:

| Annotation | Meaning |
|---|---|
| `@Input` | Scalar input value (String, Int, Boolean, etc.) |
| `@InputFile` | Single input file; task reruns if file changes |
| `@InputFiles` | Collection of input files |
| `@InputDirectory` | Input directory; task reruns if any file inside changes |
| `@OutputFile` | Single output file |
| `@OutputDirectory` | Output directory |
| `@OutputFiles` | Map of output files |
| `@Internal` | Property that does not affect up-to-date checks |
| `@CacheableTask` | Marks task outputs as eligible for the build cache |
| `@Incremental` | Combined with `@InputFiles`; lets task process only changed files |

## Custom Plugin in `buildSrc`

`buildSrc` is a special Gradle project whose compiled output is automatically available on the build classpath of all subprojects. Use it for shared build logic.

Class-based plugin (more powerful, IDE-friendly):

```kotlin
// buildSrc/src/main/kotlin/com/example/MyConventionPlugin.kt

package com.example

import org.gradle.api.Plugin
import org.gradle.api.Project
import org.gradle.api.tasks.testing.Test
import org.gradle.kotlin.dsl.*

class MyConventionPlugin : Plugin<Project> {
    override fun apply(project: Project) {
        project.plugins.apply("java")
        project.plugins.apply("jacoco")

        project.dependencies {
            add("testImplementation", "org.junit.jupiter:junit-jupiter:5.10.0")
            add("testRuntimeOnly", "org.junit.platform:junit-platform-launcher")
        }

        project.tasks.withType<Test>().configureEach {
            useJUnitPlatform()
            maxHeapSize = "1g"
        }
    }
}
```

Precompiled script plugin (simpler; recommended for most convention plugins):

```kotlin
// buildSrc/src/main/kotlin/my-java-conventions.gradle.kts
// Applied with: id("my-java-conventions")

plugins {
    java
    jacoco
}

java {
    toolchain {
        languageVersion = JavaLanguageVersion.of(21)
    }
    withSourcesJar()
}

tasks.test {
    useJUnitPlatform()
    maxHeapSize = "1g"
}

tasks.jacocoTestReport {
    dependsOn(tasks.test)
    reports {
        xml.required = true
        html.required = true
    }
}
```

Apply in subprojects:

```kotlin
// app/build.gradle.kts
plugins {
    id("my-java-conventions")  // picks up buildSrc/src/main/kotlin/my-java-conventions.gradle.kts
}
```

`buildSrc` setup:

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
    // Add plugins used inside convention plugins here
    implementation("com.diffplug.spotless:spotless-plugin-gradle:6.25.0")
}
```

## Plugin Resolution and Version Management

Centralize plugin versions in `settings.gradle.kts` using `pluginManagement`. This keeps version declarations out of individual subproject build files:

```kotlin
// settings.gradle.kts
pluginManagement {
    // Declare plugin versions here; subprojects apply without specifying a version
    plugins {
        id("org.springframework.boot") version "3.2.0"
        id("com.diffplug.spotless") version "6.25.0"
        id("com.github.ben-manes.versions") version "0.51.0"
    }

    repositories {
        gradlePluginPortal()    // default plugin repository
        mavenCentral()          // needed if plugins are published only to Central
        google()                // required for Android plugin
    }

    // Resolve plugin IDs to Maven coordinates (useful for non-standard plugins)
    resolutionStrategy {
        eachPlugin {
            if (requested.id.namespace == "com.example") {
                useModule("com.example:gradle-plugins:${requested.version}")
            }
        }
    }
}
```

Subprojects then apply without a version:

```kotlin
// lib/build.gradle.kts
plugins {
    id("org.springframework.boot")  // version comes from pluginManagement
}
```

Or use a version catalog (the preferred modern approach):

```kotlin
// settings.gradle.kts
plugins {
    alias(libs.plugins.kotlin.jvm)   // version catalog controls the version
}
```

## Important Patterns and Constraints

- The `plugins {}` block must be the first declaration in a build file (before any `import` statements and before all other build logic).
- Plugin versions belong in `pluginManagement {}` in `settings.gradle.kts` or in `gradle/libs.versions.toml`, not scattered across individual subproject build files.
- `buildSrc` changes invalidate the configuration cache for every project in the build — keep `buildSrc` lean and avoid frequent changes to it. For large multi-project builds, consider migrating `buildSrc` to a separate included build (`includeBuild("build-logic")`).
- Prefer precompiled script plugins (`.gradle.kts` files in `buildSrc/src/main/kotlin/`) over class-based plugins for convention logic — they are simpler, IDE-friendly, and do not require explicit plugin registration.
- Always use `configureEach {}` rather than `all {}` when configuring tasks to preserve configuration avoidance (lazy evaluation); `all {}` forces eager configuration of every matching task.
- The `kotlin("jvm")` shorthand in `plugins {}` is equivalent to `id("org.jetbrains.kotlin.jvm")`.
