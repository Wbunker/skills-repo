# Publishing with Gradle

Publishing artifacts to Maven repositories is handled by the `maven-publish` plugin. The key concepts are: what you publish (publications), where you publish it (repositories), and how you sign it (the `signing` plugin).

## `maven-publish` Plugin — Full Setup

The following is a complete, production-ready publishing configuration for a library targeting Maven Central. It includes sources JAR, Javadoc JAR, full POM metadata, and GPG signing.

```kotlin
// build.gradle.kts

plugins {
    id("java-library")
    id("maven-publish")
    id("signing")
}

// Generate sources and Javadoc JARs (required by Maven Central)
java {
    withSourcesJar()
    withJavadocJar()
}

publishing {
    publications {
        create<MavenPublication>("mavenJava") {
            // Attach the compiled jar, sources jar, javadoc jar, and POM
            from(components["java"])

            // Override artifact coordinates if they differ from project defaults
            groupId = "com.example"
            artifactId = "my-library"
            // version is inherited from project.version

            pom {
                name = "My Library"
                description = "A comprehensive library for doing things reliably"
                url = "https://github.com/example/my-library"
                inceptionYear = "2024"

                licenses {
                    license {
                        name = "The Apache License, Version 2.0"
                        url = "https://www.apache.org/licenses/LICENSE-2.0.txt"
                        distribution = "repo"
                    }
                }

                developers {
                    developer {
                        id = "tberglund"
                        name = "Tim Berglund"
                        email = "tim@example.com"
                        organization = "Example Corp"
                        organizationUrl = "https://example.com"
                    }
                }

                scm {
                    connection = "scm:git:git://github.com/example/my-library.git"
                    developerConnection = "scm:git:ssh://github.com/example/my-library.git"
                    url = "https://github.com/example/my-library/tree/main"
                    tag = "HEAD"
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
        }
    }

    repositories {
        // Maven Central via OSSRH (legacy Nexus staging)
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
                    ?: providers.gradleProperty("ossrhUsername").orNull
                password = System.getenv("OSSRH_TOKEN")
                    ?: providers.gradleProperty("ossrhToken").orNull
            }
        }

        // GitHub Packages
        maven {
            name = "GitHubPackages"
            url = uri("https://maven.pkg.github.com/OWNER/REPOSITORY")
            credentials {
                username = System.getenv("GITHUB_ACTOR")
                password = System.getenv("GITHUB_TOKEN")
            }
        }

        // Local file-system repo (useful for testing publication output)
        maven {
            name = "LocalFile"
            url = uri(layout.buildDirectory.dir("local-repo"))
        }
    }
}
```

## Signing Plugin

Signing is required for publication to Maven Central. It is optional for GitHub Packages and Artifactory/Nexus.

```kotlin
// build.gradle.kts
signing {
    // Option 1: Use the system gpg agent (interactive; works locally with a GPG key in the keyring)
    useGpgCmd()

    // Option 2: In-memory ASCII-armored key (preferred for CI)
    // Pass via: ORG_GRADLE_PROJECT_signingKey and ORG_GRADLE_PROJECT_signingPassword env vars
    val signingKey: String? by project
    val signingPassword: String? by project
    useInMemoryPgpKeys(signingKey, signingPassword)

    sign(publishing.publications["mavenJava"])

    // Only sign non-SNAPSHOT releases, and only when actually publishing
    setRequired {
        !version.toString().endsWith("SNAPSHOT") &&
            gradle.taskGraph.hasTask("publish")
    }
}
```

Properties-based signing (for local development without environment variables):

```properties
# ~/.gradle/gradle.properties  (never commit this file)
signing.keyId=ABCDEF01            # last 8 hex chars of the GPG key ID
signing.password=my-passphrase
signing.secretKeyRingFile=/Users/me/.gnupg/secring.gpg
```

Export an ASCII-armored private key for CI:

```bash
# Export the private key as ASCII armor
gpg --armor --export-secret-keys ABCDEF01 > private-key.asc

# Store the contents of private-key.asc as a CI secret named GPG_PRIVATE_KEY
# Store your passphrase as GPG_PASSPHRASE
```

GitHub Actions workflow:

```yaml
- name: Publish to Maven Central
  env:
    OSSRH_USERNAME: ${{ secrets.OSSRH_USERNAME }}
    OSSRH_TOKEN: ${{ secrets.OSSRH_TOKEN }}
    ORG_GRADLE_PROJECT_signingKey: ${{ secrets.GPG_PRIVATE_KEY }}
    ORG_GRADLE_PROJECT_signingPassword: ${{ secrets.GPG_PASSPHRASE }}
  run: ./gradlew publish --no-daemon
```

## Maven Central via Central Portal (2024+)

Sonatype replaced OSSRH in 2024 with the Central Portal (`central.sonatype.com`). New namespaces must use the portal. The `nmcp` plugin (New Maven Central Publishing) provides Gradle integration:

```kotlin
plugins {
    id("maven-publish")
    id("signing")
    id("com.gradleup.nmcp") version "0.1.3"
}

nmcp {
    publishAllPublicationsToCentralPortal {
        username = System.getenv("CENTRAL_USERNAME") ?: ""
        password = System.getenv("CENTRAL_PASSWORD") ?: ""
        // AUTOMATIC: Gradle releases to Central automatically after validation
        // USER_MANAGED: artifacts go to a staging area; you manually release
        publishingType = "AUTOMATIC"
    }
}
```

```bash
./gradlew publishAllPublicationsToCentralPortal
```

## Publishing to Artifactory / Nexus

```kotlin
repositories {
    // JFrog Artifactory
    maven {
        name = "Artifactory"
        url = uri(
            if (version.toString().endsWith("SNAPSHOT"))
                "https://artifactory.example.com/artifactory/libs-snapshot"
            else
                "https://artifactory.example.com/artifactory/libs-release"
        )
        credentials {
            username = System.getenv("ARTIFACTORY_USER")
            password = System.getenv("ARTIFACTORY_API_KEY")  // use an API key, not a password
        }
    }

    // Sonatype Nexus OSS
    maven {
        name = "Nexus"
        url = uri(
            if (version.toString().endsWith("SNAPSHOT"))
                "https://nexus.example.com/repository/maven-snapshots/"
            else
                "https://nexus.example.com/repository/maven-releases/"
        )
        credentials {
            username = System.getenv("NEXUS_USER")
            password = System.getenv("NEXUS_PASSWORD")
        }
    }
}
```

## SBOM Generation

```kotlin
plugins {
    id("org.cyclonedx.bom") version "1.10.0"
}

tasks.cyclonedxBom {
    setProjectType("library")           // "application", "library", "firmware", "container"
    setSchemaVersion("1.5")
    setIncludeLicenseText(true)
    setIncludeBomSerialNumber(true)
    destination = project.file("build/reports")
    outputName = "bom"
}
```

```bash
./gradlew cyclonedxBom
# Outputs: build/reports/bom.json  and  build/reports/bom.xml
```

Attach the SBOM as an additional artifact in the Maven publication:

```kotlin
publishing {
    publications {
        named<MavenPublication>("mavenJava") {
            artifact(tasks.cyclonedxBom.get().outputs.files.singleFile) {
                classifier = "cyclonedx"
                extension = "json"
            }
        }
    }
}
tasks.named("generateMetadataFileForMavenJavaPublication") {
    dependsOn(tasks.cyclonedxBom)
}
```

## Version Naming and Automation

Standard Maven version conventions:

- Release: `1.2.3`
- Snapshot: `1.2.3-SNAPSHOT`
- Release candidate: `1.2.3-RC1`
- Milestone: `1.2.3-M2`

Snapshots are published to the snapshot repository and can be overwritten without a version bump. Releases are immutable — once published to Maven Central, a version cannot be replaced.

Auto-derive version from Git tags in CI:

```kotlin
// build.gradle.kts — version from CI environment or git tags
version = System.getenv("RELEASE_VERSION")
    ?: runCatching {
        providers.exec {
            commandLine("git", "describe", "--tags", "--exact-match")
        }.standardOutput.asText.get().trim().removePrefix("v")
    }.getOrElse("0.0.1-SNAPSHOT")
```

For multi-project builds, set the version once in the root build:

```kotlin
// root build.gradle.kts
allprojects {
    version = System.getenv("RELEASE_VERSION") ?: "0.0.1-SNAPSHOT"
    group = "com.example"
}
```

## Publish to Local Maven Repository (Testing)

```bash
# Install to ~/.m2/repository/GROUP/ARTIFACT/VERSION/
./gradlew publishToMavenLocal

# Install a specific publication
./gradlew publishMavenJavaPublicationToMavenLocal

# Verify what was published
ls ~/.m2/repository/com/example/my-library/
```

After `publishToMavenLocal`, test consumption in another project by adding `mavenLocal()` to its repositories. Remove `mavenLocal()` before committing — it is not reproducible in CI.

## Available Publishing Tasks

The `maven-publish` plugin generates tasks following a naming pattern:

| Task | Effect |
|---|---|
| `publish` | Publish all publications to all configured repositories |
| `publishToMavenLocal` | Install all publications to `~/.m2/repository` |
| `publishMavenJavaPublicationToOSSRHRepository` | One publication to one named repository |
| `publishMavenJavaPublicationToMavenLocal` | One publication to local Maven |
| `generatePomFileForMavenJavaPublication` | Write the POM XML without publishing |
| `signMavenJavaPublication` | Sign the publication (requires `signing` plugin) |

List all available publishing tasks:

```bash
./gradlew tasks --group publishing
```

## Multi-Project Publishing

Apply publishing configuration via a convention plugin so it does not need to be repeated in every subproject:

```kotlin
// buildSrc/src/main/kotlin/publish-conventions.gradle.kts

plugins {
    id("java-library")
    id("maven-publish")
    id("signing")
}

java {
    withSourcesJar()
    withJavadocJar()
}

publishing {
    publications {
        create<MavenPublication>("mavenJava") {
            from(components["java"])
            pom {
                url = "https://github.com/example/my-project"
                licenses {
                    license {
                        name = "Apache License 2.0"
                        url = "https://www.apache.org/licenses/LICENSE-2.0"
                    }
                }
                scm {
                    connection = "scm:git:git://github.com/example/my-project.git"
                    url = "https://github.com/example/my-project"
                }
            }
        }
    }
    repositories {
        maven {
            name = "OSSRH"
            url = uri(
                if (version.toString().endsWith("SNAPSHOT"))
                    "https://s01.oss.sonatype.org/content/repositories/snapshots/"
                else
                    "https://s01.oss.sonatype.org/service/local/staging/deploy/maven2/"
            )
            credentials {
                username = System.getenv("OSSRH_USERNAME") ?: ""
                password = System.getenv("OSSRH_TOKEN") ?: ""
            }
        }
    }
}

signing {
    val signingKey: String? by project
    val signingPassword: String? by project
    useInMemoryPgpKeys(signingKey, signingPassword)
    sign(publishing.publications["mavenJava"])
    setRequired { !version.toString().endsWith("SNAPSHOT") }
}
```

Each publishable subproject simply applies the convention:

```kotlin
// lib/build.gradle.kts
plugins {
    id("publish-conventions")
}
```

## Important Patterns and Constraints

- Maven Central requires all four of: POM with name/description/url/license/developer/SCM, sources JAR, Javadoc JAR, and GPG signature. Missing any one will cause the publication to be rejected.
- Signing is required for Maven Central; it is optional for GitHub Packages and corporate Artifactory/Nexus deployments.
- Snapshot versions (`-SNAPSHOT`) must be published to the snapshot repository URL; attempting to publish a snapshot to the release URL will be rejected.
- After staging to OSSRH, you must manually log in to `s01.oss.sonatype.org` and release the staging repository (or use the Central Portal API to close and release programmatically).
- Gradle 8.8 and later: the `publishing {}` block is configuration-cache compatible.
- Never hardcode credentials in build files. Use environment variables (`System.getenv()`) or project properties sourced from `~/.gradle/gradle.properties` (`providers.gradleProperty()`).
- `publishToMavenLocal` is for local testing only and bypasses POM validation checks. Do not rely on it to verify Maven Central compatibility.
- The `ORG_GRADLE_PROJECT_` prefix on environment variables makes them available as Gradle project properties (e.g., `ORG_GRADLE_PROJECT_signingKey` is read by `val signingKey: String? by project`).
