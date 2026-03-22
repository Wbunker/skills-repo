# Ch.4 — Maven and Gradle

> **Note:** The publishing CLI surface lives in the `maven-publish` plugin. This file covers
> conceptual mapping, configuration patterns, and the `maven-publish` DSL. For task invocations
> see the tasks section below and the CLI reference file if present.

---

## Maven POM ↔ Gradle Mapping (Berglund Ch.4)

| Maven POM Element | Gradle Kotlin DSL | Notes |
|---|---|---|
| `<groupId>` | `group = "com.example"` | Top-level project property |
| `<artifactId>` | `rootProject.name` in `settings.gradle.kts`; or `tasks.jar { archiveBaseName = "..." }` | Settings file controls the primary artifact name |
| `<version>` | `version = "1.0.0"` | Top-level project property |
| `<packaging>jar</packaging>` | Default when `java` plugin applied | Change via `tasks.jar` |
| `<packaging>war</packaging>` | `war` plugin | Produces `.war` file |
| `<dependencies>` | `dependencies { }` block | |
| `<scope>compile</scope>` (leaks API) | `api(...)` | Requires `java-library` plugin; leaked to consumers |
| `<scope>compile</scope>` (no leak) | `implementation(...)` | Not visible to consumers; preferred default |
| `<scope>test</scope>` | `testImplementation(...)` | |
| `<scope>provided</scope>` | `compileOnly(...)` | On compile classpath, not runtime |
| `<scope>runtime</scope>` | `runtimeOnly(...)` | On runtime classpath, not compile |
| `<scope>system</scope>` | `files(...)` local file dependency | Avoid; use a repository instead |
| `<build><plugins>` | `plugins { }` block | Declarative; preferred |
| `<build><pluginManagement>` | `plugins { }` in root with `apply false` | Declare version centrally, apply in subprojects |
| `<properties>` | `gradle.properties` or `extra { }` in script | `gradle.properties` for key–value; `extra` for computed |
| `<parent>` | Convention plugins in `buildSrc` or included builds | No single "parent POM" concept; use composition |
| `<modules>` | `include(":module-a", ":module-b")` in `settings.gradle.kts` | |
| `<dependencyManagement>` | `platform(...)` BOM import or version catalogs | |
| `<profiles>` | Gradle properties + `if/else` in script, or separate source sets | No first-class profile support; use properties |
| `<distributionManagement>` | `publishing { repositories { } }` | |
| `<repositories>` | `dependencyResolutionManagement { repositories { } }` in settings | |
| `<reporting>` | Plugin-specific DSL (e.g., `jacoco`, `checkstyle`) | No single reporting block |

---

## Maven Goals ↔ Gradle Tasks (Berglund Ch.4)

| Maven Goal | Gradle Task | Notes |
|---|---|---|
| `mvn compile` | `./gradlew compileJava` | Compiles `src/main/java` |
| `mvn test-compile` | `./gradlew compileTestJava` | Compiles `src/test/java` |
| `mvn test` | `./gradlew test` | Runs all tests |
| `mvn package` | `./gradlew jar` or `./gradlew assemble` | `assemble` builds all archive artifacts |
| `mvn install` | `./gradlew publishToMavenLocal` | Installs to `~/.m2/repository` |
| `mvn deploy` | `./gradlew publish` | Publishes to all configured remote repositories |
| `mvn clean` | `./gradlew clean` | Deletes `build/` directory |
| `mvn verify` | `./gradlew check` | Runs all verification tasks (tests, lint, etc.) |
| `mvn validate` | `./gradlew help` (no direct equivalent) | Gradle validates at configuration time |
| `mvn dependency:tree` | `./gradlew dependencies` | Prints full dependency tree |
| `mvn dependency:resolve` | `./gradlew dependencies --configuration runtimeClasspath` | Resolves a specific configuration |
| `mvn dependency:analyze` | No built-in; use `nebula.lint` plugin | |
| `mvn versions:display-dependency-updates` | `./gradlew dependencyUpdates` (Ben Manes plugin) | |
| `mvn site` | No direct equivalent; use `dokka` or custom tasks | |
| `mvn enforcer:enforce` | Gradle's built-in dependency constraints + `resolutionStrategy` | |
| `mvn release:prepare` | `./gradlew release` (researchgate/gradle-release plugin) | |

---

## The Legacy `maven` Plugin (Berglund Ch.4)

The old `apply plugin: 'maven'` (Groovy: `maven` plugin) is deprecated and removed in Gradle 7.
Berglund's book covers the transitional period. The replacement is `maven-publish`.

**Do not use:**
```kotlin
// DEPRECATED — removed in Gradle 7
apply(plugin = "maven")   // No longer available
```

---

## maven-publish Plugin (Modern)

The `maven-publish` plugin is the current standard for publishing artifacts to Maven repositories.

### Minimal Setup — Library

```kotlin
// build.gradle.kts
plugins {
    id("java-library")
    id("maven-publish")
}

group = "com.example"
version = "1.0.0"

publishing {
    publications {
        create<MavenPublication>("mavenJava") {
            from(components["java"])   // includes jar + sources jar + javadoc jar if configured
        }
    }
    repositories {
        maven {
            name = "GitHubPackages"
            url = uri("https://maven.pkg.github.com/example/my-library")
            credentials {
                username = System.getenv("GITHUB_ACTOR")
                password = System.getenv("GITHUB_TOKEN")
            }
        }
    }
}
```

### Full Setup — With POM Metadata

```kotlin
plugins {
    id("java-library")
    id("maven-publish")
    id("signing")   // required for Maven Central
}

java {
    withJavadocJar()   // attaches javadoc artifact to publication
    withSourcesJar()   // attaches sources artifact to publication
}

publishing {
    publications {
        create<MavenPublication>("mavenJava") {
            from(components["java"])

            // Explicit coordinate overrides (optional if group/version set at project level)
            groupId = "com.example"
            artifactId = "my-library"
            version = "1.0.0"

            // Attach additional artifacts
            artifact(tasks.named("customJar"))

            pom {
                name = "My Library"
                description = "A concise description of what this library does"
                url = "https://github.com/example/my-library"
                inceptionYear = "2024"

                licenses {
                    license {
                        name = "Apache License 2.0"
                        url = "https://www.apache.org/licenses/LICENSE-2.0"
                        distribution = "repo"
                    }
                }

                developers {
                    developer {
                        id = "tim"
                        name = "Tim Berglund"
                        email = "tim@example.com"
                        organization = "Gradle"
                        organizationUrl = "https://gradle.com"
                    }
                }

                scm {
                    connection = "scm:git:git://github.com/example/my-library.git"
                    developerConnection = "scm:git:ssh://github.com/example/my-library.git"
                    url = "https://github.com/example/my-library/tree/main"
                    tag = "v1.0.0"
                }

                issueManagement {
                    system = "GitHub Issues"
                    url = "https://github.com/example/my-library/issues"
                }

                ciManagement {
                    system = "GitHub Actions"
                    url = "https://github.com/example/my-library/actions"
                }
            }

            // Modify generated POM programmatically (e.g., remove test dependencies)
            pom.withXml {
                val deps = asNode().get("dependencies") as groovy.util.NodeList
                deps.forEach { dep ->
                    val node = dep as groovy.util.Node
                    if ((node.get("scope") as groovy.util.NodeList).text() == "test") {
                        node.parent().remove(node)
                    }
                }
            }
        }
    }

    repositories {
        // Sonatype OSSRH / Maven Central
        maven {
            name = "OSSRH"
            url = uri(
                if (version.toString().endsWith("SNAPSHOT"))
                    "https://s01.oss.sonatype.org/content/repositories/snapshots/"
                else
                    "https://s01.oss.sonatype.org/service/local/staging/deploy/maven2/"
            )
            credentials {
                username = System.getenv("OSSRH_USERNAME")
                password = System.getenv("OSSRH_TOKEN")
            }
        }

        // GitHub Packages
        maven {
            name = "GitHubPackages"
            url = uri("https://maven.pkg.github.com/example/my-library")
            credentials {
                username = System.getenv("GITHUB_ACTOR")
                password = System.getenv("GITHUB_TOKEN")
            }
        }

        // Internal Nexus / Artifactory
        maven {
            name = "Internal"
            url = uri("https://nexus.internal.example.com/repository/maven-releases/")
            isAllowInsecureProtocol = false
            credentials(HttpHeaderCredentials::class) {
                name = "Authorization"
                value = "Bearer ${System.getenv("NEXUS_TOKEN")}"
            }
            authentication {
                create<HttpHeaderAuthentication>("header")
            }
        }
    }
}

// Sign all publications (required for Maven Central)
signing {
    val signingKey: String? by project
    val signingPassword: String? by project
    useInMemoryPgpKeys(signingKey, signingPassword)
    sign(publishing.publications["mavenJava"])
}
```

---

## Install to Local Maven Repository (Berglund Ch.4)

Applying `maven-publish` automatically adds a `publishToMavenLocal` task. No extra configuration
is needed unless you want to customize what gets installed.

```kotlin
plugins {
    `java-library`
    `maven-publish`
}

publishing {
    publications {
        create<MavenPublication>("mavenJava") {
            from(components["java"])
        }
    }
    // No repositories block needed for publishToMavenLocal
}
```

```bash
# Install to ~/.m2/repository/com/example/my-library/1.0.0/
./gradlew publishToMavenLocal

# Verify
ls ~/.m2/repository/com/example/my-library/1.0.0/
```

---

## Using Maven Repositories as Dependency Sources (Berglund Ch.4)

Gradle resolves dependencies from repositories. Configure them in `settings.gradle.kts` (Gradle 7+
preferred) or in each `build.gradle.kts`.

```kotlin
// settings.gradle.kts — preferred; applies to all projects in the build
dependencyResolutionManagement {
    repositoriesMode.set(RepositoriesMode.FAIL_ON_PROJECT_REPOS)  // enforce no per-project repos
    repositories {
        mavenCentral()                              // https://repo1.maven.org/maven2/
        google()                                    // https://maven.google.com/
        maven("https://jitpack.io")                 // JitPack for GitHub-hosted libraries
        maven {
            name = "Internal"
            url = uri("https://nexus.internal.example.com/repository/maven-public/")
            credentials {
                username = providers.gradleProperty("nexusUser").orNull
                password = providers.gradleProperty("nexusPassword").orNull
            }
        }
        // mavenLocal() — use only for testing locally-built snapshots; never in CI
    }
}
```

```kotlin
// Per-project (older style, still valid when needed)
// build.gradle.kts
repositories {
    mavenCentral()
    maven("https://oss.sonatype.org/content/repositories/snapshots/") {
        mavenContent {
            snapshotsOnly()   // only resolve snapshots from this repo
        }
    }
}
```

---

## Importing a Maven BOM (Bill of Materials) (Berglund Ch.4)

A BOM (equivalent to Maven's `<dependencyManagement>`) aligns versions across a group of related
artifacts without specifying versions on each dependency individually.

```kotlin
dependencies {
    // Import BOM — versions from the BOM apply to all matching dependencies
    implementation(platform("org.springframework.boot:spring-boot-dependencies:3.2.0"))
    implementation(platform("com.fasterxml.jackson:jackson-bom:2.16.0"))

    // No version needed — resolved from the BOM
    implementation("org.springframework.boot:spring-boot-starter-web")
    implementation("org.springframework.boot:spring-boot-starter-data-jpa")
    implementation("com.fasterxml.jackson.core:jackson-databind")

    testImplementation("org.springframework.boot:spring-boot-starter-test")
}
```

Use `enforcedPlatform(...)` to make BOM versions override any transitive version conflicts
(equivalent to Maven's `<scope>import</scope>` with forced versions). Use sparingly.

```kotlin
dependencies {
    implementation(enforcedPlatform("io.micrometer:micrometer-bom:1.12.0"))
}
```

---

## Version Catalogs — Modern Alternative to BOM-Only Management

```toml
# gradle/libs.versions.toml
[versions]
spring-boot = "3.2.0"
jackson = "2.16.0"

[libraries]
spring-boot-starter-web = { module = "org.springframework.boot:spring-boot-starter-web", version.ref = "spring-boot" }
jackson-databind = { module = "com.fasterxml.jackson.core:jackson-databind", version.ref = "jackson" }

[plugins]
spring-boot = { id = "org.springframework.boot", version.ref = "spring-boot" }
```

```kotlin
// build.gradle.kts
dependencies {
    implementation(libs.spring.boot.starter.web)
    implementation(libs.jackson.databind)
}
```

---

## Maven2Gradle Converter (Berglund Ch.4)

The `gradle init` command detects a `pom.xml` in the project directory and offers to convert it.

```bash
# Navigate to the Maven project root (where pom.xml lives)
cd /path/to/maven/project

# Gradle detects pom.xml and offers POM-based initialization
gradle init

# Alternatively, explicitly specify a Java application/library:
gradle init --type java-application --dsl kotlin
gradle init --type java-library --dsl kotlin
```

The converter handles:
- Basic `<dependencies>` with scope mapping
- `<parent>` to multi-project structure suggestion
- `<modules>` to `include()` in settings
- Common plugins (compiler, surefire, etc.)

What the converter does **not** handle well:
- Custom Maven plugins with complex configurations
- Multi-module builds with cross-module dependency cycles
- Maven profiles (must be manually converted to Gradle properties)
- `<build><sourceDirectory>` overrides beyond the standard layout

After conversion, inspect and clean up the generated files. The output is a starting point,
not a production-ready build.

---

## Dependency Scopes — Complete Mapping

For projects using the `java` plugin (applications):

| Maven Scope | Gradle Configuration | Included in JAR? | On compile CP? | On runtime CP? | Exported to consumers? |
|---|---|---|---|---|---|
| `compile` | `implementation` | No (as dep) | Yes | Yes | No |
| `compile` (API) | `api` | No (as dep) | Yes | Yes | Yes |
| `test` | `testImplementation` | No | Test only | Test only | No |
| `provided` | `compileOnly` | No | Yes | No | No |
| `runtime` | `runtimeOnly` | No | No | Yes | No |
| `system` | Local `files(...)` | No | Yes | Configurable | Avoid |

For projects using `java-library` plugin, `api` becomes meaningful. For plain `java` plugin,
use `implementation` for everything that was `compile`.

---

## Important Patterns & Constraints

- **Never use `mavenLocal()` in CI.** Local Maven repositories are not reproducible across
  machines. Use a shared remote repository (Nexus, Artifactory, GitHub Packages) for artifacts
  that need to be shared between CI jobs.

- **`api` requires `java-library` plugin**, not `java`. Adding an `api(...)` dependency with
  only the `java` plugin applied will produce a build error in Gradle 7+.

- **Don't publish SNAPSHOTs to Maven Central.** Maven Central (`OSSRH`) does not allow snapshot
  versions in the release repository. Snapshots go to the OSSRH snapshot repository only.

- **Dynamic versions break reproducibility.** Gradle supports `1.+`, `latest.release`, and
  `[1.0,2.0)` Maven-style ranges, but these resolve differently over time. Prefer exact versions
  and use dependency locking for reproducibility:

  ```bash
  ./gradlew dependencies --write-locks
  ```

  With lock files committed, Gradle will resolve the exact same versions on all machines.

- **`pom.withXml` is a last resort.** Prefer typed DSL (`pom { scm { } }`) over XML manipulation.
  `withXml` breaks IDE support and type safety.

- **`publishToMavenLocal` does not sign** unless you explicitly add the signing configuration.
  This is intentional — signing is only required for remote repositories.

- **Component variants**: `from(components["java"])` includes the main jar variant. For
  multi-variant publications (e.g., different target JVM versions), use the Gradle Module
  Metadata features and declare additional variants via `AdhocComponentWithVariants`.

- **Gradle Module Metadata (GMM)**: When publishing with `maven-publish`, Gradle also publishes
  a `.module` file alongside the POM. This file carries richer variant and dependency information
  that Gradle consumers use. Maven consumers fall back to the POM. Do not disable GMM unless
  you have a specific reason.
