# Ch.5 — Testing with Gradle

See also: [Ch.5 Testing CLI Reference](ch5-testing-cli.md)

---

## JUnit 5 (Jupiter) — Primary Framework

JUnit 5 is the recommended test framework for new Gradle projects. It requires explicit opt-in via `useJUnitPlatform()`.

```kotlin
// build.gradle.kts
plugins { id("java") }

dependencies {
    testImplementation("org.junit.jupiter:junit-jupiter:5.10.0")
    testRuntimeOnly("org.junit.platform:junit-platform-launcher")
}

tasks.test {
    useJUnitPlatform()
    // Optional: enable JUnit 5 parallel execution
    systemProperty("junit.jupiter.execution.parallel.enabled", "true")
    systemProperty("junit.jupiter.execution.parallel.mode.default", "concurrent")
    maxParallelForks = (Runtime.getRuntime().availableProcessors() / 2).coerceAtLeast(1)
}
```

### JUnit 5 Features Relevant to Gradle

- `@Test` — marks a test method
- `@ParameterizedTest` — runs a test multiple times with different arguments (requires `junit-jupiter-params`)
- `@RepeatedTest(n)` — runs a test n times
- `@TestFactory` — dynamic test generation; returns a stream/collection of `DynamicTest`
- `@Tag("integration")` — attaches a tag; filter with `includeTags` / `excludeTags` in the `test` task or via `--tests`
- `@Disabled` — skips the test; appears as skipped (not failed) in the HTML and XML reports
- `@ExtendWith` — JUnit 5 extension model; used by Mockito (`MockitoExtension`), Spring (`SpringExtension`), Testcontainers, etc.
- `@Nested` — groups related tests; supports `@BeforeEach` scoping per nested class
- `@TempDir` — injects a temporary directory for file I/O tests; cleaned up after each test

---

## JUnit 4 (Legacy)

JUnit 4 is still encountered in existing codebases. No `useJUnitPlatform()` call is needed — Gradle uses the JUnit 4 runner by default when `junit:junit` is on the classpath.

```kotlin
dependencies {
    testImplementation("junit:junit:4.13.2")
}

tasks.test {
    useJUnit()  // explicit; also the default without useJUnitPlatform()
}
```

JUnit 4 test filtering via Gradle still works with `--tests`, but tag-based filtering uses `@Category` annotations rather than `@Tag`.

---

## TestNG

TestNG is configured with `useTestNG()` and supports XML suite files, listener hooks, and group-based filtering.

```kotlin
dependencies {
    testImplementation("org.testng:testng:7.9.0")
}

tasks.test {
    useTestNG()
    options {
        suites("src/test/resources/testng.xml")         // optional XML suite file
        listeners("com.example.MyTestNGListener")        // register listeners
        groups(mapOf("include" to listOf("unit")))       // run only "unit" group
        // groups(mapOf("exclude" to listOf("slow")))    // exclude a group
    }
}
```

TestNG groups map roughly to JUnit 5 tags. The `suites()` method accepts one or more XML files that declare test classes, groups, and ordering.

---

## Spock Framework — Groovy-Based BDD

Spock is a Groovy-based specification framework that produces highly readable test reports. Spock 2.x runs on the JUnit Platform (requires `useJUnitPlatform()`).

```kotlin
plugins {
    id("groovy")
}

dependencies {
    testImplementation("org.spockframework:spock-core:2.4-groovy-4.0")
    testImplementation("org.codehaus.groovy:groovy:4.0.15")
}

tasks.test { useJUnitPlatform() }  // Spock 2.x runs on JUnit Platform
```

### Example Spock Specification

```groovy
import spock.lang.Specification

class CalculatorSpec extends Specification {

    def "should add two numbers"() {
        expect:
        1 + 1 == 2
    }

    def "should multiply correctly"() {
        expect:
        a * b == result

        where:
        a | b | result
        2 | 3 | 6
        4 | 5 | 20
    }

    def "should throw on divide by zero"() {
        when:
        10 / 0

        then:
        thrown(ArithmeticException)
    }

    def "should interact with collaborator"() {
        given:
        def publisher = new Publisher()
        def subscriber = Mock(Subscriber)
        publisher.subscribers << subscriber

        when:
        publisher.publish("hello")

        then:
        1 * subscriber.receive("hello")
    }
}
```

Spock blocks: `given` (setup), `when` (stimulus), `then` (verification), `expect` (combined condition), `where` (data table), `cleanup` (teardown). Reports show the block labels in failure messages.

---

## Test Suites DSL (Gradle 7.6+) — Modern Approach

The `testing` extension provides a typed, declarative API for defining test suites. It replaces manual `sourceSets` + `Test` task wiring for integration and functional test configurations.

```kotlin
// build.gradle.kts
testing {
    suites {
        // Default unit test suite — always exists; configure it here
        val test by getting(JvmTestSuite::class) {
            useJUnitJupiter("5.10.0")
        }

        // Integration test suite with Testcontainers
        val integrationTest by registering(JvmTestSuite::class) {
            useJUnitJupiter()

            dependencies {
                implementation(project())                                         // production classes
                implementation("org.testcontainers:testcontainers:1.19.0")
                implementation("org.testcontainers:junit-jupiter:1.19.0")
            }

            targets {
                all {
                    testTask.configure {
                        shouldRunAfter(test)
                        maxParallelForks = 2
                        timeout.set(java.time.Duration.ofMinutes(15))
                    }
                }
            }
        }

        // Functional/end-to-end test suite
        val functionalTest by registering(JvmTestSuite::class) {
            useJUnitJupiter()
            dependencies {
                implementation(project())
            }
            targets {
                all {
                    testTask.configure {
                        shouldRunAfter(integrationTest)
                    }
                }
            }
        }
    }
}

// Ensure check runs all suites
tasks.named("check") {
    dependsOn(testing.suites.named("integrationTest"))
    dependsOn(testing.suites.named("functionalTest"))
}
```

Running:
```bash
./gradlew integrationTest
./gradlew functionalTest
./gradlew check   # runs all three suites
```

The Test Suites DSL automatically creates a source set, compile task, and test task for each suite. Source code lives in `src/<suiteName>/java` (or `kotlin`, `groovy`).

---

## Parallel Test Execution

Two independent levels of parallelism can be combined for maximum throughput.

### Level 1: Gradle-Level (Multiple JVMs)

Gradle forks multiple JVM processes. Each fork handles a subset of test classes. Isolation is strong; memory overhead is proportional to fork count.

```kotlin
tasks.test {
    maxParallelForks = (Runtime.getRuntime().availableProcessors() / 2).coerceAtLeast(1)
    forkEvery = 100  // restart each JVM after 100 tests to prevent memory/static-state leaks
}
```

- `maxParallelForks` — number of concurrent JVM processes (default: 1)
- `forkEvery` — restart the JVM after this many tests; useful when tests leak static state or native resources; expensive due to JVM startup cost — only use when needed

### Level 2: JUnit 5-Level (Within a Single JVM, Multiple Threads)

JUnit 5 parallel execution runs test methods or test classes concurrently on a thread pool within one JVM. Tests must be thread-safe.

```kotlin
tasks.test {
    systemProperty("junit.jupiter.execution.parallel.enabled", "true")
    systemProperty("junit.jupiter.execution.parallel.mode.default", "concurrent")
    systemProperty("junit.jupiter.execution.parallel.mode.classes.default", "concurrent")
}
```

Alternatively, configure via `src/test/resources/junit-platform.properties`:

```properties
junit.jupiter.execution.parallel.enabled=true
junit.jupiter.execution.parallel.config.strategy=dynamic
junit.jupiter.execution.parallel.config.dynamic.factor=2
```

Available strategies:
- `fixed` — fixed thread pool size; set `junit.jupiter.execution.parallel.config.fixed.parallelism`
- `dynamic` — pool size = `availableProcessors * factor` (default factor: 1.0)
- `custom` — implement `ParallelExecutionConfigurationStrategy`

To opt a specific test class out of parallelism: `@Execution(ExecutionMode.SAME_THREAD)`.

---

## Test Filtering

### In build.gradle.kts

```kotlin
tasks.test {
    filter {
        includeTestsMatching("com.example.*")
        includeTestsMatching("*IntegrationTest")
        excludeTestsMatching("*SlowTest")
    }

    // Tag-based filtering (JUnit 5):
    includeTags("unit")
    excludeTags("slow", "integration")
}
```

### Dynamic Filtering at the Command Line

```bash
./gradlew test --tests "com.example.MyTest"
./gradlew test --tests "com.example.MyTest.shouldDoSomething"
./gradlew test --tests "com.example.*IntegrationTest"
```

Note: `--tests` is ANDed with any `filter {}` block declared in the build file.

### Combining Tags and Patterns

```kotlin
tasks.test {
    includeTags("fast")
    filter {
        includeTestsMatching("com.example.unit.*")
    }
}
```

---

## JaCoCo Code Coverage

The `jacoco` plugin instruments bytecode to measure which lines, branches, and methods are executed during tests.

```kotlin
plugins {
    java
    jacoco
}

tasks.jacocoTestReport {
    dependsOn(tasks.test)   // always run tests before generating report
    reports {
        xml.required = true    // consumed by CI tools (SonarQube, Codecov, etc.)
        html.required = true   // human-readable report
        csv.required = false
    }
}

// Wire into the check lifecycle
tasks.check { dependsOn(tasks.jacocoTestReport) }

// Fail the build if coverage drops below threshold
tasks.jacocoTestCoverageVerification {
    violationRules {
        rule {
            limit {
                minimum = "0.80".toBigDecimal()   // 80% line coverage required
            }
        }
        rule {
            element = "CLASS"
            limit {
                counter = "BRANCH"
                value = "COVEREDRATIO"
                minimum = "0.70".toBigDecimal()   // 70% branch coverage per class
            }
            excludes = listOf("com.example.generated.*")
        }
    }
}

tasks.check { dependsOn(tasks.jacocoTestCoverageVerification) }
```

Report locations:
- HTML: `build/reports/jacoco/test/html/index.html`
- XML: `build/reports/jacoco/test/jacocoTestReport.xml`

For multi-project builds, use the `JacocoMerge` task or the `JacocoReport` task with multiple `executionData` files to produce an aggregate coverage report:

```kotlin
// root build.gradle.kts
tasks.register<JacocoReport>("jacocoAggregateReport") {
    dependsOn(subprojects.map { it.tasks.withType<Test>() })
    executionData(fileTree(rootDir) { include("**/build/jacoco/*.exec") })
    sourceDirectories.from(subprojects.map { it.file("src/main/java") })
    classDirectories.from(subprojects.map { it.file("build/classes/java/main") })
    reports {
        xml.required = true
        html.required = true
    }
}
```

---

## Test Reports

Gradle generates two types of reports automatically after a `test` task run.

| Report Type | Location | Format |
|---|---|---|
| HTML (human-readable) | `build/reports/tests/test/index.html` | HTML with pass/fail/skip counts |
| JUnit XML (CI-compatible) | `build/test-results/test/*.xml` | One XML file per test class |

```kotlin
tasks.test {
    reports {
        html.required = true
        junitXml.required = true   // consumed by Jenkins, GitHub Actions, GitLab CI, etc.
    }
}
```

For integration test suites, the paths include the suite name:
- HTML: `build/reports/tests/integrationTest/index.html`
- XML: `build/test-results/integrationTest/*.xml`

---

## Test Logging (Console Output)

By default, Gradle only prints a summary. Enable detailed output for debugging:

```kotlin
tasks.test {
    testLogging {
        events("passed", "skipped", "failed")  // also: "started", "standardOut", "standardError"
        showExceptions = true
        showCauses = true
        showStackTraces = true
        exceptionFormat = org.gradle.api.tasks.testing.logging.TestExceptionFormat.FULL
        showStandardStreams = false   // set true to see System.out/System.err from tests
    }
}
```

For CI environments, `events("passed", "skipped", "failed")` combined with `exceptionFormat = FULL` is a practical default — it surfaces all failures with full stack traces without flooding the log with passing test noise.

---

## Test Environment Control

```kotlin
tasks.test {
    // JVM tuning
    jvmArgs("-Xmx512m", "-XX:+HeapDumpOnOutOfMemoryError", "-Dfile.encoding=UTF-8")

    // Environment variables visible to the test process
    environment("MY_ENV_VAR", "test-value")
    environment("DATABASE_URL", "jdbc:h2:mem:testdb")

    // System properties (accessible via System.getProperty())
    systemProperty("spring.profiles.active", "test")
    systemProperty("logback.configurationFile", "src/test/resources/logback-test.xml")

    // Working directory for the test JVM (default: project dir)
    workingDir(project.rootDir)

    // Kill the test JVM if tests take longer than this
    timeout.set(java.time.Duration.ofMinutes(10))

    // Fail on first test failure; skip remaining tests
    failFast = true
}
```

Passing all project properties into system properties (useful for CI parameter injection):

```kotlin
tasks.test {
    project.properties.forEach { (key, value) ->
        if (value is String) systemProperty(key, value)
    }
}
```

---

## Geb and EasyB (Legacy — Berglund Ch.5)

**Geb** is a Groovy-based browser automation library built on Selenium WebDriver. It integrates with Spock or JUnit via modules:

```kotlin
dependencies {
    testImplementation("org.gebish:geb-spock:7.0")          // Spock integration
    testImplementation("org.seleniumhq.selenium:selenium-firefox-driver:4.18.1")
}
tasks.test { useJUnitPlatform() }   // Geb+Spock 2.x runs on JUnit Platform
```

Geb is now rarely chosen for greenfield projects; Playwright (via `playwright-java`) and Selenium directly are more common.

**EasyB** was a Groovy BDD framework with `given`/`when`/`then` story syntax. It is largely unmaintained and has been superseded by Spock for Groovy-based BDD. Both Geb and EasyB use `useJUnit()` or `useTestNG()` as the underlying runner depending on the version.

---

## Important Patterns and Constraints

- `testImplementation` does not leak into `implementation` — test dependencies are invisible to production code consumers. Use `testImplementation` for all test-only deps.
- Gradle caches test results. If source files, test classes, and the classpath are unchanged since the last run, the `test` task is marked `UP-TO-DATE` and skipped. Use `--rerun` to force re-execution or `--rerun-tasks` globally.
- `forkEvery` is expensive due to JVM startup cost. Only enable it when tests have global static state leaks or native library conflicts.
- JUnit 5 thread-level parallelism is NOT automatic. Tests must be annotated with `@Execution(ExecutionMode.CONCURRENT)` or configured via `junit-platform.properties`. Parallel execution is unsafe for tests that share mutable static state.
- The `test` task only covers the `test` source set. Integration tests require either the Test Suites DSL or manual source set + task configuration.
- Skipped tests (`@Disabled`, `assumeTrue()` failures) appear in the HTML report with a yellow indicator and are counted separately from failures. They do not fail the build.
- JaCoCo and test tasks must be coordinated: `jacocoTestReport` must `dependsOn(tasks.test)`, and `jacocoTestCoverageVerification` should run after the report is generated.
