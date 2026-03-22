# Dependency Management CLI

See also: [Dependency Management Concepts](dependency-management-concepts.md)

```bash
# ── Viewing Dependencies ─────────────────────────────────────────────────────

# Show all dependencies for the root project across all configurations
./gradlew dependencies

# Show dependencies for a specific configuration
./gradlew dependencies --configuration compileClasspath
./gradlew dependencies --configuration runtimeClasspath
./gradlew dependencies --configuration testCompileClasspath
./gradlew dependencies --configuration testRuntimeClasspath
./gradlew dependencies --configuration annotationProcessor

# Show dependencies for a specific subproject
./gradlew :lib:dependencies
./gradlew :app:dependencies --configuration runtimeClasspath

# Show all configurations with their dependency trees
./gradlew dependencies --all

# ── Dependency Insight ───────────────────────────────────────────────────────

# Why is a specific dependency included, and which version was selected?
./gradlew dependencyInsight --dependency guava
./gradlew dependencyInsight --dependency jackson-databind
./gradlew dependencyInsight --dependency jackson-databind --configuration compileClasspath

# Insight for a subproject
./gradlew :lib:dependencyInsight --dependency slf4j-api --configuration runtimeClasspath

# Understand why a transitive dep was upgraded (look for "by conflict resolution")
./gradlew dependencyInsight --dependency snakeyaml

# ── Dependency Updates (ben-manes.versions plugin) ───────────────────────────

# Check for newer available versions of all dependencies
./gradlew dependencyUpdates

# Restrict results to stable releases only (exclude alphas, betas, RCs, snapshots)
./gradlew dependencyUpdates -Drevision=release

# Include milestone releases
./gradlew dependencyUpdates -Drevision=milestone

# Output report as JSON
./gradlew dependencyUpdates --report-format json
# Report location: build/dependencyUpdates/report.json

# ── Dependency Locking ───────────────────────────────────────────────────────

# Write lock files for all configurations (generates gradle/dependency-locks/*.lockfile)
./gradlew dependencies --write-locks

# Write lock files for a specific subproject
./gradlew :lib:dependencies --write-locks

# Update lock file for one specific dependency (leaves all others locked)
./gradlew dependencies --update-locks com.google.guava:guava

# Update lock files for multiple specific dependencies
./gradlew dependencies --update-locks com.google.guava:guava,org.slf4j:slf4j-api

# Update all lock files (equivalent to --write-locks; regenerates from current resolution)
./gradlew dependencies --update-locks '*'

# ── Dependency Verification ──────────────────────────────────────────────────

# Generate SHA-256 verification metadata (creates gradle/verification-metadata.xml)
./gradlew --write-verification-metadata sha256 help

# Generate SHA-256 and MD5 verification metadata
./gradlew --write-verification-metadata sha256,md5 help

# Generate verification metadata AND export trusted GPG keys
./gradlew --write-verification-metadata sha256 --export-keys help

# Update verification metadata after upgrading dependencies
./gradlew --write-verification-metadata sha256 dependencies

# Verification happens automatically on every build; this forces it explicitly
./gradlew build  # fails with checksum error if any artifact is tampered

# ── Resolution and Classpath Diagnostics ─────────────────────────────────────

# Print the full resolved classpath for a configuration (useful for debugging)
./gradlew :printClasspath  # requires a custom task (see below)

# Show all configurations for a project
./gradlew outgoingVariants
./gradlew resolvableConfigurations

# Find version conflicts in the dependency tree (look for -> lines)
./gradlew dependencies --configuration compileClasspath 2>&1 | grep " -> "

# Show all dependency substitutions that were applied
./gradlew dependencies --configuration runtimeClasspath --info 2>&1 | grep "Substitut"

# ── Publishing / Local ───────────────────────────────────────────────────────

# Publish to local Maven repository (~/.m2) for testing
./gradlew publishToMavenLocal

# Publish a specific publication to local Maven
./gradlew publishMavenJavaPublicationToMavenLocal

# List all available publish tasks
./gradlew tasks --group publishing

# ── Utility ──────────────────────────────────────────────────────────────────

# Show the build script classpath (plugins and their dependencies)
./gradlew buildEnvironment

# Show buildscript dependencies for a subproject
./gradlew :app:buildEnvironment

# Force re-download all dependencies (delete cached artifacts)
./gradlew --refresh-dependencies build

# Quiet mode (suppress progress, show only dependency tree)
./gradlew dependencies -q

# Custom task to print compile classpath (add to build.gradle.kts for debugging)
# tasks.register("printClasspath") {
#     doLast {
#         configurations.compileClasspath.get().forEach { println(it) }
#     }
# }
```
