# Ch.2 — Tasks CLI Reference

*Companion concepts reference: [ch2-tasks-concepts.md](ch2-tasks-concepts.md)*

---

## Discovering Tasks

### List All Tasks

```bash
# List tasks organized by group (excludes tasks with no group by default)
./gradlew tasks

# Include all tasks — even those without a group or not normally visible
./gradlew tasks --all

# Filter to a specific group
./gradlew tasks --group verification
./gradlew tasks --group build
./gradlew tasks --group "custom tasks"
./gradlew tasks --group help

# Sample output of ./gradlew tasks --group verification:
# Verification tasks
# ------------------
# check - Runs all checks.
# test - Runs the test suite.
```

### Get Detailed Help for a Task

```bash
# Show a task's description, group, type, options, inputs, and outputs
./gradlew help --task build
./gradlew help --task compileJava
./gradlew help --task test
./gradlew help --task jar

# Sample output:
# > Task :help
# Detailed task information for build
#
# Paths
#      :build
#
# Type
#      Task (org.gradle.api.Task)
#
# Description
#      Assembles and tests this project.
#
# Group
#      build
```

### List Tasks Across All Subprojects

```bash
# In a multi-project build, list tasks for a specific subproject
./gradlew :app:tasks
./gradlew :lib:tasks --all

# List tasks for all subprojects simultaneously (run from the root project)
./gradlew tasks --all
```

---

## Running Specific Tasks

### Single-Project

```bash
# Run a task by name
./gradlew myTask
./gradlew generateReport
./gradlew compileJava

# Run multiple tasks in one invocation (Gradle determines execution order from the task graph)
./gradlew clean build
./gradlew test jacocoTestReport
./gradlew assemble generateDocs publishToMavenLocal
```

### Multi-Project: Fully Qualified Task Paths

```bash
# Run a task in a specific subproject using its fully-qualified path
./gradlew :app:build
./gradlew :lib:jar
./gradlew :api:test

# Run the same task in ALL subprojects that define it
./gradlew build       # runs :app:build, :lib:build, :api:build etc. from the root
./gradlew test        # runs test in every subproject that has a test task

# Run from a subproject directory (path becomes relative to that subproject)
cd app/
./gradlew build       # equivalent to ./gradlew :app:build from root
cd ..

# Alternatively, use --project-dir without changing directories
./gradlew --project-dir app build
```

---

## Excluding Tasks

```bash
# Exclude a task using -x (short form of --exclude-task)
./gradlew build -x test            # run the full build lifecycle but skip tests
./gradlew build -x javadoc         # skip Javadoc generation
./gradlew build -x test -x javadoc # skip multiple tasks

# Note: -x excludes the named task AND any tasks that are exclusively required by it.
# If another task also depends on the excluded task, the excluded task still runs.
# Use --dry-run first to verify what will execute.
```

---

## Forcing Re-Execution

By default, Gradle skips tasks that are UP-TO-DATE. These flags override that behavior.

```bash
# Force ALL tasks in this build to re-run, ignoring up-to-date status and build cache
./gradlew build --rerun-tasks

# Force a SPECIFIC task to re-run (Gradle 7.6+)
# Only that task is forced; its dependencies still honor UP-TO-DATE checks
./gradlew test --rerun
./gradlew compileJava --rerun

# Disable the build cache for this run (tasks will still write to cache, but not read from it)
./gradlew build --no-build-cache

# Disable build cache reads AND writes entirely for this run
./gradlew build -Dorg.gradle.caching=false
```

### When to Force Re-Execution

| Scenario | Command |
|---|---|
| Stale outputs from external change (e.g., changed environment variable not declared as `@Input`) | `./gradlew build --rerun-tasks` |
| Flaky test that might pass on a fresh run | `./gradlew test --rerun` |
| Suspecting a build cache poisoning issue | `./gradlew build --no-build-cache` |
| CI pipeline configured to always produce fresh artifacts | `./gradlew clean assemble` |

---

## Dry Run

The `--dry-run` flag (short: `-m`) shows the full task execution plan — which tasks would run and in which order — without actually executing any task actions.

```bash
./gradlew build --dry-run
./gradlew build -m

# Sample output:
# :compileJava SKIPPED
# :processResources SKIPPED
# :classes SKIPPED
# :jar SKIPPED
# :startScripts SKIPPED
# :distTar SKIPPED
# :distZip SKIPPED
# :assemble SKIPPED
# :compileTestJava SKIPPED
# :processTestResources SKIPPED
# :testClasses SKIPPED
# :test SKIPPED
# :check SKIPPED
# :build SKIPPED

# In a multi-project build:
./gradlew :app:build --dry-run
```

**Use dry run when**:
- You want to understand what `./gradlew build` will actually do before running it
- You're debugging unexpected task ordering
- You want to verify that `-x test` correctly removes the test task from the graph

---

## Continuous Build (Watch Mode)

```bash
# Re-execute the task automatically whenever source files change
./gradlew test --continuous
./gradlew test -t        # short form

# Also works with other tasks
./gradlew compileJava --continuous
./gradlew generateDocs --continuous

# Combine with a specific test filter (see also ch5-testing-cli.md)
./gradlew test --continuous --tests "com.example.*"
```

**How it works**: Gradle watches the declared inputs of the executed tasks using the file system watching API. When a change is detected, it re-runs the requested tasks from the earliest affected task in the graph. Press `CTRL+C` to stop.

**Requirements**:
- Task inputs must be properly declared via `@InputFiles`, `@InputDirectory`, or the runtime API (otherwise changes are not detected)
- The Gradle daemon must be running (`--continuous` does not work with `--no-daemon`)
- File system watching must be enabled (default since Gradle 7.0; override with `--no-watch-fs` if causing issues)

---

## Task Output Logging

```bash
# See why a task was UP-TO-DATE or not (--info level required)
./gradlew test --info 2>&1 | grep -A 10 "Task :test"

# Verbose output for the full build
./gradlew build --info
./gradlew build -i

# Full debug output (extremely verbose — includes internal Gradle decisions, classpath details)
./gradlew build --debug
./gradlew build -d

# Redirect all output to a file for offline analysis
./gradlew build --info > build.log 2>&1

# Show all deprecation warnings (essential during Gradle upgrades)
./gradlew build --warning-mode=all
```

### Task Outcome Labels

| Label | Meaning |
|---|---|
| (none) | Task executed and did work |
| `UP-TO-DATE` | Inputs/outputs unchanged since last run; task skipped |
| `FROM-CACHE` | Outputs restored from build cache; task not re-executed |
| `SKIPPED` | Task was excluded (`-x`), `onlyIf` condition was false, or `enabled = false` |
| `NO-SOURCE` | Task had no source files (annotated with `@SkipWhenEmpty`) |
| `FAILED` | Task threw an exception; build stops (unless `--continue` is set) |

### Understanding UP-TO-DATE Reasoning (--info Mode)

When a task is NOT up-to-date, `--info` explains why:

```
Task ':test' is not up-to-date because:
  Input property 'classpath' file /path/to/app.jar has changed.

Task ':compileJava' is not up-to-date because:
  Input property 'source' file src/main/java/App.java has changed.
```

---

## Parallel Task Execution

```bash
# Run independent tasks in parallel
./gradlew build --parallel

# Set the maximum number of parallel workers (default: number of CPU cores)
./gradlew build --parallel --max-workers=4
./gradlew build --parallel --max-workers=8

# Disable parallel execution for debugging
./gradlew build --no-parallel
```

**Persist in `gradle.properties`:**
```properties
org.gradle.parallel=true
org.gradle.workers.max=4
```

**Parallel safety rules**:
- Tasks that write to the same output directory must be ordered with `dependsOn` or `mustRunAfter`
- Core Gradle plugins (`java`, `kotlin`, `application`) are parallel-safe
- Custom `@TaskAction` methods must avoid shared mutable state

---

## Profiling and Performance Diagnostics

```bash
# Generate an HTML build profile report in build/reports/profile/
./gradlew build --profile

# Open the generated profile (macOS)
open build/reports/profile/*.html

# Publish a build scan (far more detailed than --profile; hosted at scans.gradle.com)
./gradlew build --scan

# Check if configuration cache is being used (reduces configuration phase overhead)
./gradlew build --configuration-cache
# Output will include:
# "Configuration cache entry stored."   (first run — config phase ran and was cached)
# "Configuration cache entry reused."   (subsequent run — config phase skipped entirely)

# Measure the benefit of the build cache
./gradlew clean build           # first run: populates cache
./gradlew clean build           # second run: should show FROM-CACHE for many tasks
```

---

## Dependency-Related Task Commands

These show task inputs from the dependency graph perspective:

```bash
# Show the full dependency tree for a configuration
./gradlew dependencies
./gradlew dependencies --configuration compileClasspath
./gradlew dependencies --configuration runtimeClasspath
./gradlew dependencies --configuration testRuntimeClasspath

# Explain why a specific dependency is present and which version was selected
./gradlew dependencyInsight --dependency guava
./gradlew dependencyInsight --dependency guava --configuration compileClasspath

# In a specific subproject
./gradlew :app:dependencies --configuration runtimeClasspath
./gradlew :lib:dependencyInsight --dependency jackson-databind

# Check for outdated dependencies (requires the com.github.ben-manes.versions plugin)
./gradlew dependencyUpdates
./gradlew dependencyUpdates -Drevision=release   # only stable releases
```

---

## Task Graph Visualization

Gradle does not ship a built-in task graph visualizer, but these approaches help:

```bash
# Dry run shows execution order without running anything
./gradlew build --dry-run

# Build scan provides a full interactive task timeline at scans.gradle.com
./gradlew build --scan

# Third-party plugin: gradle-task-tree (barfuin/gradle-task-tree)
# After applying the plugin to build.gradle.kts:
./gradlew build taskTree
./gradlew test taskTree --task-depth 3    # limit depth of dependency tree shown
```

---

## Useful Task-Related One-Liners

```bash
# Full clean build with build scan (typical pre-release verification)
./gradlew clean build --scan

# Run only compileJava (without running its dependents)
./gradlew compileJava

# List all dependencies in runtimeClasspath
./gradlew dependencies --configuration runtimeClasspath

# Show what tasks are triggered by `build` (via dry run)
./gradlew build --dry-run

# Re-run tests even when UP-TO-DATE (e.g., when a database changed externally)
./gradlew test --rerun

# Run tests and generate a coverage report
./gradlew test jacocoTestReport

# Run all verification checks (tests + static analysis)
./gradlew check

# Run tests in watch mode (re-runs on every source change)
./gradlew test --continuous

# Reset the local build cache and run a full build to repopulate it
./gradlew --stop && rm -rf ~/.gradle/caches/build-cache-1/ && ./gradlew build

# Check if a task is configuration-cache compatible
./gradlew build --configuration-cache --info 2>&1 | grep -i "incompatible\|not compatible"

# Show all project properties (useful for debugging -P flags)
./gradlew properties

# Show the Gradle version used by the wrapper
./gradlew --version
```
