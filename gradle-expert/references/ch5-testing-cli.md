# Ch.5 — Testing CLI Reference

See also: [Ch.5 Testing Concepts](ch5-testing-concepts.md)

---

## Running Tests

```bash
# Run all tests in the project
./gradlew test

# Run a specific test class (fully qualified)
./gradlew test --tests "com.example.MyTest"

# Run a specific test method
./gradlew test --tests "com.example.MyTest.shouldDoSomething"

# Run tests matching a wildcard pattern
./gradlew test --tests "com.example.*IntegrationTest"
./gradlew test --tests "*Service*"

# Run multiple patterns (each --tests flag is ORed)
./gradlew test --tests "com.example.FooTest" --tests "com.example.BarTest"

# Run all tests in a package (recursive)
./gradlew test --tests "com.example.service.*"
```

---

## Controlling Test Execution

```bash
# Fail fast — stop the test run on the first failure
./gradlew test --fail-fast

# Force re-run even if Gradle considers the task UP-TO-DATE
./gradlew test --rerun

# Force re-run all tasks (not just test)
./gradlew test --rerun-tasks

# Skip tests entirely (run assemble/build without test phase)
./gradlew build -x test
./gradlew assemble          # assembles without running any tests

# Dry run — show which tasks would execute without running them
./gradlew test --dry-run
```

---

## Console Verbosity

```bash
# Show INFO-level log output (includes test events from testLogging config)
./gradlew test --info
./gradlew test -i

# Show DEBUG-level log output (very verbose; Gradle internals)
./gradlew test --debug
./gradlew test -d

# Quiet mode — suppress all output except errors
./gradlew test --quiet
./gradlew test -q
```

---

## Continuous Testing (Watch Mode)

```bash
# Re-run tests automatically whenever source files change
./gradlew test --continuous
./gradlew test -t
```

Gradle watches the inputs of the `test` task (compiled classes, resources). Any change triggers a re-run. Press `Ctrl+D` to stop.

---

## Test Reports

```bash
# Open the HTML test report (macOS)
open build/reports/tests/test/index.html

# Open the HTML test report (Linux)
xdg-open build/reports/tests/test/index.html

# XML results directory (consumed by CI systems: Jenkins, GitHub Actions, GitLab CI)
ls build/test-results/test/

# Generate JaCoCo coverage report after running tests
./gradlew test jacocoTestReport

# Open the JaCoCo HTML coverage report (macOS)
open build/reports/jacoco/test/html/index.html

# Verify coverage meets thresholds (fails build if below minimum)
./gradlew test jacocoTestCoverageVerification
```

---

## Tag-Based Filtering (JUnit 5)

```bash
# Run only tests tagged "unit"
./gradlew test -Dgroups="unit"

# Run only tests tagged "integration"
./gradlew test -Dgroups="integration"

# Exclude tests tagged "slow"
./gradlew test -DexcludeGroups="slow"

# Combine: include "unit" AND exclude "slow"
./gradlew test -Dgroups="unit" -DexcludeGroups="slow"
```

For TestNG, the same `-Dgroups` / `-DexcludeGroups` flags apply.

---

## Test Suites (Gradle 7.6+)

```bash
# Run only the integration test suite (if defined in testing {} block)
./gradlew integrationTest

# Run only the functional test suite
./gradlew functionalTest

# Run all suites (unit + integration + functional), if wired into check
./gradlew check

# Run integration tests in a specific subproject
./gradlew :app:integrationTest

# Open the integration test report
open build/reports/tests/integrationTest/index.html
```

---

## Subproject Test Execution

```bash
# Run tests only in the :lib subproject
./gradlew :lib:test

# Run tests only in the :app subproject
./gradlew :app:test

# Run from within the subproject directory (equivalent to :lib:test)
cd lib && ../gradlew test

# Run tests in parallel across all subprojects
./gradlew test --parallel

# Skip tests in a specific subproject while building everything else
./gradlew build -x :lib:test
```

---

## Diagnostics and Debugging

```bash
# List all test tasks across the build
./gradlew tasks --all | grep -i test

# Show task inputs and outputs (useful for understanding UP-TO-DATE checks)
./gradlew help --task test
./gradlew help --task :lib:test

# Print the test classpath (DEBUG level)
./gradlew test --debug 2>&1 | grep "test classpath"

# Run with a specific JVM argument (e.g., remote debug on port 5005)
./gradlew test --debug-jvm
# Then attach your IDE's remote debugger to localhost:5005

# Show full stack traces for build failures (not test failures)
./gradlew test --stacktrace
./gradlew test -s

# Show full stack traces including cause chains
./gradlew test --full-stacktrace
./gradlew test -S
```

---

## Lifecycle Integration

```bash
# Run tests as part of the standard build lifecycle
./gradlew build       # compileJava → processResources → classes → compileTestJava → test → jar → ...

# Run only the check lifecycle (test + any additional verification tasks)
./gradlew check

# Run tests then generate JaCoCo report in one command
./gradlew test jacocoTestReport

# Run tests then verify coverage threshold in one command
./gradlew test jacocoTestReport jacocoTestCoverageVerification
```

---

## Common Flags Summary

| Flag | Effect |
|---|---|
| `--tests "<pattern>"` | Run only tests matching the pattern |
| `--fail-fast` | Stop on first test failure |
| `--rerun` | Force re-run the test task |
| `--rerun-tasks` | Force re-run all tasks |
| `-x test` | Exclude the test task |
| `--parallel` | Run tasks in parallel across subprojects |
| `--continuous` / `-t` | Re-run on file change |
| `--info` / `-i` | Show INFO log (test events) |
| `--debug-jvm` | Suspend test JVM; attach remote debugger on port 5005 |
| `--stacktrace` / `-s` | Print full stack trace for build errors |
