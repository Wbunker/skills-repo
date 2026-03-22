# Dependency Management

See also: [Dependency Management CLI](dependency-management-cli.md)

## Configurations

Gradle dependencies are assigned to named *configurations* that control which classpaths they appear on. The `java` and `java-library` plugins add the standard configurations:

```kotlin
dependencies {
    implementation("org.springframework:spring-core:6.1.0")  // compile + runtime, NOT exported
    api("com.google.guava:guava:33.0.0-jre")                 // compile + runtime, EXPORTED (java-library only)
    compileOnly("org.projectlombok:lombok:1.18.30")          // compile only, NOT in runtime
    runtimeOnly("org.postgresql:postgresql:42.7.0")          // runtime only, NOT compile classpath
    testImplementation("org.junit.jupiter:junit-jupiter:5.10.0")
    testRuntimeOnly("org.junit.platform:junit-platform-launcher")
    annotationProcessor("org.projectlombok:lombok:1.18.30")
}
```

## `api` vs `implementation` (java-library plugin)

The `java-library` plugin adds the `api` configuration, which controls whether a dependency leaks onto the compile classpath of downstream consumers.

| Configuration | Compile classpath | Runtime classpath | Exported to consumers |
|---|---|---|---|
| `api` | yes | yes | yes — leaks to dependents' compile classpath |
| `implementation` | yes | yes | no — hidden from dependents' compile classpath |
| `compileOnly` | yes | no | no |
| `runtimeOnly` | no | yes | no |
| `testImplementation` | yes (test only) | yes (test only) | no |
| `testRuntimeOnly` | no | yes (test only) | no |

**Rule**: Use `api` only when the type appears in the public API of your library — in method signatures, field types, or class inheritance. Use `implementation` for everything internal. Leaking implementation dependencies via `api` forces your consumers to recompile whenever those transitive dependencies change, increasing build times across the dependency graph.

Apply the `java-library` plugin instead of `java` when publishing a library intended for consumption:

```kotlin
plugins {
    `java-library`
}
```

## Version Catalogs (`libs.versions.toml`) — Modern Standard

Version catalogs centralize all dependency coordinates and versions in a single TOML file. All subprojects share the same catalog automatically; no per-project version declarations needed.

```toml
# gradle/libs.versions.toml

[versions]
kotlin = "2.0.0"
junit = "5.10.0"
guava = "33.0.0-jre"
spring-boot = "3.2.0"
testcontainers = "1.19.0"
jackson = "2.16.1"
mockk = "1.13.10"

[libraries]
guava = { group = "com.google.guava", name = "guava", version.ref = "guava" }
junit-jupiter = { group = "org.junit.jupiter", name = "junit-jupiter", version.ref = "junit" }
junit-launcher = { group = "org.junit.platform", name = "junit-platform-launcher" }
spring-boot-starter-web = { group = "org.springframework.boot", name = "spring-boot-starter-web", version.ref = "spring-boot" }
spring-boot-starter-data-jpa = { group = "org.springframework.boot", name = "spring-boot-starter-data-jpa", version.ref = "spring-boot" }
spring-boot-starter-test = { group = "org.springframework.boot", name = "spring-boot-starter-test", version.ref = "spring-boot" }
testcontainers-junit = { group = "org.testcontainers", name = "junit-jupiter", version.ref = "testcontainers" }
testcontainers-postgresql = { group = "org.testcontainers", name = "postgresql", version.ref = "testcontainers" }
jackson-databind = { group = "com.fasterxml.jackson.core", name = "jackson-databind", version.ref = "jackson" }
mockk = { group = "io.mockk", name = "mockk", version.ref = "mockk" }

[bundles]
junit = ["junit-jupiter", "junit-launcher"]
testcontainers = ["testcontainers-junit", "testcontainers-postgresql"]
spring-web = ["spring-boot-starter-web", "spring-boot-starter-data-jpa"]

[plugins]
kotlin-jvm = { id = "org.jetbrains.kotlin.jvm", version.ref = "kotlin" }
spring-boot = { id = "org.springframework.boot", version.ref = "spring-boot" }
spring-dependency-management = { id = "io.spring.dependency-management", version = "1.1.4" }
```

Reference the catalog in build files using the `libs` accessor:

```kotlin
// build.gradle.kts
plugins {
    alias(libs.plugins.kotlin.jvm)
    alias(libs.plugins.spring.boot)
    alias(libs.plugins.spring.dependency.management)
}

dependencies {
    implementation(libs.guava)
    implementation(libs.jackson.databind)
    implementation(libs.bundles.spring.web)
    testImplementation(libs.bundles.junit)
    testImplementation(libs.bundles.testcontainers)
    testImplementation(libs.mockk)
}
```

Catalog accessor names: hyphens in library aliases become dots in Kotlin (`spring-boot-starter-web` → `libs.spring.boot.starter.web`). Underscores are also valid separators in the TOML and map to dots in the accessor.

## BOM (Bill of Materials) Import

A BOM is a special POM that declares compatible versions for a family of dependencies. Importing a BOM lets you omit version numbers for all artifacts it covers.

```kotlin
dependencies {
    // Import BOM — sets versions for all Spring Boot managed dependencies
    implementation(platform("org.springframework.boot:spring-boot-dependencies:3.2.0"))

    // No version needed; BOM controls it
    implementation("org.springframework.boot:spring-boot-starter-web")
    implementation("org.springframework.boot:spring-boot-starter-data-jpa")
    implementation("org.springframework.boot:spring-boot-starter-actuator")
    testImplementation("org.springframework.boot:spring-boot-starter-test")

    // Enforce BOM versions even if a transitive dependency requests a different version
    implementation(enforcedPlatform("org.springframework.boot:spring-boot-dependencies:3.2.0"))
}
```

`platform()` recommends versions (can be overridden by explicit declarations). `enforcedPlatform()` forces them (overrides everything). Prefer `platform()` in libraries; `enforcedPlatform()` is appropriate in application builds.

Common BOMs:
- `org.springframework.boot:spring-boot-dependencies` — Spring Boot managed dependencies
- `org.springframework.cloud:spring-cloud-dependencies` — Spring Cloud
- `io.quarkus.platform:quarkus-bom` — Quarkus
- `software.amazon.awssdk:bom` — AWS SDK v2
- `com.fasterxml.jackson:jackson-bom` — Jackson

## Repositories

Declare repositories in `settings.gradle.kts` using `dependencyResolutionManagement` to apply them to all subprojects from one place. Setting `FAIL_ON_PROJECT_REPOS` prevents subprojects from declaring their own repositories, which enforces consistency:

```kotlin
// settings.gradle.kts
dependencyResolutionManagement {
    repositoriesMode.set(RepositoriesMode.FAIL_ON_PROJECT_REPOS)
    repositories {
        mavenCentral()                    // https://repo.maven.apache.org/maven2/
        google()                          // https://dl.google.com/dl/android/maven2/ — required for Android
        gradlePluginPortal()              // https://plugins.gradle.org/m2/ — for plugins used in subprojects

        // JitPack — builds from GitHub sources
        maven("https://jitpack.io")

        // Custom Maven repo (no auth)
        maven("https://repo.example.com/releases")

        // Custom Maven repo with credentials
        maven {
            name = "CorporateNexus"
            url = uri("https://nexus.example.com/repository/maven-public/")
            credentials {
                username = providers.environmentVariable("NEXUS_USER").orElse("").get()
                password = providers.environmentVariable("NEXUS_PASS").orElse("").get()
            }
        }

        // S3-backed repo (AWS CodeArtifact)
        maven {
            url = uri("s3://my-bucket/releases")
            authentication { create<AwsImAuthentication>("awsIm") }
        }

        // mavenLocal() — reads ~/.m2/repository — AVOID in production and CI
        // mavenLocal()
    }
}
```

`mavenLocal()` is non-reproducible (local state can differ between machines) and should be omitted from CI builds. Use a Nexus or Artifactory proxy to cache and proxy Maven Central instead.

## Resolution Strategies

Resolution strategies let you override Gradle's default dependency resolution behavior — useful for forcing a specific version, resolving conflicts, or substituting one module for another:

```kotlin
configurations.all {
    resolutionStrategy {
        // Force a specific version regardless of what is requested
        force("com.fasterxml.jackson.core:jackson-databind:2.16.1")
        force("org.yaml:snakeyaml:2.2")

        // Fail the build if any version conflict is found (strict mode)
        // failOnVersionConflict()

        // Substitute one module for another (migration, relocation)
        dependencySubstitution {
            // Replace the vulnerable Log4j 1.x with Log4j 2.x
            substitute(module("log4j:log4j"))
                .using(module("org.apache.logging.log4j:log4j-core:2.22.1"))

            // Replace a published artifact with a local project during development
            substitute(module("com.example:shared-lib"))
                .using(project(":shared-lib"))
        }

        // Disable caching of dynamic version resolution (e.g., "1.+")
        cacheDynamicVersionsFor(0, "seconds")

        // Disable caching of SNAPSHOT resolution
        cacheChangingModulesFor(0, "seconds")

        // Prefer the project's own modules over external ones in version conflict
        preferProjectModules()

        // Sort conflict resolution: Gradle defaults to highest version wins
        // eachDependency lets you inspect and override per-dependency
        eachDependency {
            if (requested.group == "org.bouncycastle") {
                useVersion("1.77")
                because("Security: CVE-2023-33201 fix in 1.77")
            }
        }
    }
}
```

## Dependency Locking (Reproducibility)

Dependency locking records the exact resolved versions for every configuration into lock files committed to VCS. This guarantees that every build — local, CI, Docker — resolves identical versions even if new versions are published.

Enable locking:

```kotlin
// build.gradle.kts
dependencyLocking {
    lockAllConfigurations()
    // lockMode.set(LockMode.LENIENT)  // advisory: warns rather than fails on drift
}
```

Generate lock files:

```bash
# Write locks for all configurations
./gradlew dependencies --write-locks

# Creates files like:
# gradle/dependency-locks/compileClasspath.lockfile
# gradle/dependency-locks/runtimeClasspath.lockfile
# gradle/dependency-locks/testCompileClasspath.lockfile
# ...
```

Lock file format (committed to VCS):

```
# This is a Gradle generated file for dependency locking.
# Manual edits can break the build and are not advised.
# This file is expected to be part of source control.
com.fasterxml.jackson.core:jackson-annotations:2.16.1=compileClasspath,runtimeClasspath
com.fasterxml.jackson.core:jackson-core:2.16.1=compileClasspath,runtimeClasspath
com.fasterxml.jackson.core:jackson-databind:2.16.1=compileClasspath,runtimeClasspath
```

Update locks when upgrading dependencies:

```bash
# Update all locks
./gradlew dependencies --write-locks

# Update locks for a specific dependency only
./gradlew dependencies --update-locks com.google.guava:guava

# Update locks for multiple dependencies
./gradlew dependencies --update-locks com.google.guava:guava,com.fasterxml.jackson.core:jackson-databind
```

## Dependency Exclusions

Exclude a transitive dependency from a specific dependency declaration:

```kotlin
dependencies {
    implementation("org.springframework:spring-core:6.1.0") {
        exclude(group = "commons-logging", module = "commons-logging")
    }

    // Exclude just by group (removes all modules from that group)
    implementation("org.hibernate:hibernate-core:6.4.0") {
        exclude(group = "org.jboss.logging")
    }
}
```

Exclude from all configurations (global exclusion):

```kotlin
configurations.all {
    exclude(group = "commons-logging", module = "commons-logging")
}
```

Replace an excluded dependency with a substitute (common pattern: replace commons-logging with slf4j-jcl-bridge):

```kotlin
configurations.all {
    resolutionStrategy.dependencySubstitution {
        substitute(module("commons-logging:commons-logging"))
            .using(module("org.slf4j:jcl-over-slf4j:2.0.12"))
    }
}
```

## Dynamic Versions (Avoid in Production)

Dynamic version selectors are supported but produce non-reproducible builds:

```kotlin
// AVOID in production — resolves to whatever is latest at build time
implementation("com.example:lib:1.+")            // latest 1.x
implementation("com.example:lib:latest.release") // latest non-snapshot
implementation("com.example:lib:+")              // latest of any version

// PREFER — pin exact versions
implementation("com.example:lib:1.2.3")

// If dynamic versions are required, combine with dependency locking
// to restore reproducibility
```

Dynamic version results are cached for 24 hours by default. Use `cacheDynamicVersionsFor(0, "seconds")` in `resolutionStrategy` to force fresh resolution on every build.

## Dependency Verification (Security)

Dependency verification records cryptographic checksums for every resolved artifact. Gradle verifies checksums on every build and fails if any artifact does not match — detecting supply-chain attacks and corrupted downloads.

Generate verification metadata:

```bash
# Generate SHA-256 and MD5 checksums for all resolved artifacts
./gradlew --write-verification-metadata sha256,md5 help

# Creates: gradle/verification-metadata.xml
```

Sample `verification-metadata.xml`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<verification-metadata
    xmlns="https://schema.gradle.org/dependency-verification"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xsi:schemaLocation="https://schema.gradle.org/dependency-verification
        https://schema.gradle.org/dependency-verification/dependency-verification-1.3.xsd">
   <configuration>
      <verify-metadata>true</verify-metadata>
      <verify-signatures>false</verify-signatures>
   </configuration>
   <components>
      <component group="com.google.guava" name="guava" version="33.0.0-jre">
         <artifact name="guava-33.0.0-jre.jar">
            <sha256 value="a2f3a...c9d4" origin="Generated by Gradle"/>
         </artifact>
      </component>
   </components>
</verification-metadata>
```

Enable GPG signature verification for stronger guarantees:

```bash
./gradlew --write-verification-metadata sha256 --export-keys help
```

Update verification metadata after upgrading dependencies:

```bash
./gradlew --write-verification-metadata sha256 dependencies
```

## Strict, Required, and Preferred Version Declarations

Rich version declarations give fine-grained control over version resolution:

```kotlin
dependencies {
    implementation("com.example:lib") {
        version {
            require("1.2.3")          // minimum version (default behavior)
            strictly("1.2.3")         // exact version; build fails if another version selected
            prefer("1.2.3")           // soft preference; overridden by other constraints
            reject("1.2.0", "1.2.1")  // these specific versions are unacceptable
        }
    }
}
```

`strictly` is useful for security-sensitive libraries where you must control the exact version. It causes a build failure if dependency resolution would select any other version, forcing you to explicitly acknowledge version changes.

## Important Patterns and Constraints

- Use `implementation` (not the removed `compile` configuration) for most dependencies. `compile` was removed in Gradle 7.
- Version catalog `libs.versions.toml` is shared automatically across all subprojects without any additional configuration.
- Avoid `mavenLocal()` in CI; use a Nexus or Artifactory repository proxy instead to get reproducible, cached resolution.
- Run `./gradlew dependencyInsight --dependency NAME` to trace exactly why a particular version was selected (which dependency requested it, what resolution rules applied).
- Run `./gradlew dependencies --configuration compileClasspath` to see the full resolved dependency tree for a specific classpath.
- Commit lock files (`gradle/dependency-locks/`) and verification metadata (`gradle/verification-metadata.xml`) to VCS.
- `enforcedPlatform()` overrides all version constraints including `strictly()`; use it only in application modules, not in published libraries.
- The `annotationProcessor` configuration is separate from `implementation` and must be declared independently (unlike Maven where annotation processors on the compile classpath are automatically detected).
