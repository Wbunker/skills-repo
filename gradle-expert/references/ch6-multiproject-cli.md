# Chapter 6 — Multi-project Builds: CLI Reference

## Running Tasks in Subprojects

```bash
# Run in a specific subproject
./gradlew :app:build
./gradlew :lib:test

# Run in all subprojects (from root)
./gradlew build            # respects dependsOn across projects
./gradlew subprojects:test # NOT valid syntax

# Run same task in all subprojects that have it
./gradlew test             # runs :app:test :lib:test etc. in dependency order
```

## Project Listing

```bash
# List all projects in the build
./gradlew projects

# Show project dependencies
./gradlew :app:dependencies
./gradlew :app:dependencies --configuration runtimeClasspath
```

## Dependency Insights Across Projects

```bash
# Which project provides a dependency
./gradlew :app:dependencyInsight --dependency guava --configuration compileClasspath
```

## Selective Subproject Execution

```bash
# Only execute in a specific project dir
./gradlew build --project-dir app/

# Focus build on a subproject without running its dependents
./gradlew :lib:build
```

## Composite Builds

```bash
# Substitute local build for a published dependency (ad-hoc)
./gradlew build --include-build ../my-utils

# Or declared in settings.gradle.kts:
# includeBuild("../my-utils")
```

## Task Filtering

```bash
# Run all tasks matching a pattern across subprojects
./gradlew test -p app       # only in :app
./gradlew -p lib clean build
```

## Parallel Multi-project

```bash
# Gradle can run independent subproject tasks in parallel
./gradlew build --parallel
```

Projects with no inter-dependencies execute concurrently. Declare inter-project dependencies with `implementation(project(":lib"))` so Gradle respects ordering.

## Build Validation

```bash
# Check the full settings structure
./gradlew :help --task projects

# Verify composite build substitutions
./gradlew :app:dependencies | grep my-utils
```
