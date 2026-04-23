# Getting Started with Spring Boot

Chapters 1–2 of *Spring Boot Up & Running* — Spring Boot philosophy, auto-configuration internals, starters, Spring Initializr, project structure.

---

## What Spring Boot Does

Spring Boot is **opinionated convention over configuration**. It removes boilerplate by:

1. **Auto-configuration** — detects what's on the classpath and wires sensible defaults automatically
2. **Starter POMs** — curated dependency sets that pull in everything needed for a capability
3. **Embedded server** — ships Tomcat (or Jetty/Netty) inside the JAR; no external container required
4. **Production-ready defaults** — health checks, metrics, externalized config out of the box

```
Traditional Spring App         Spring Boot App
─────────────────────         ───────────────
web.xml                       (gone)
applicationContext.xml        @SpringBootApplication
spring-mvc-servlet.xml        (auto-configured)
server installation           embedded Tomcat in JAR
manual DataSource bean        auto-configured from spring.datasource.*
```

---

## Spring Initializr

The fastest way to start: **https://start.spring.io**

| Field | Guidance |
|-------|---------|
| Project | Maven (wider tooling support) or Gradle (faster builds, Kotlin DSL) |
| Language | Java, Kotlin, or Groovy |
| Spring Boot version | Use latest GA release (not SNAPSHOT or M-release) |
| Group/Artifact | Follow reverse-DNS convention: `com.example` / `myapp` |
| Dependencies | Add starters upfront; easy to add more to pom.xml later |

CLI equivalent:
```bash
spring init --dependencies=web,data-jpa,h2,security myapp
```

---

## Project Structure

```
myapp/
├── src/
│   ├── main/
│   │   ├── java/com/example/myapp/
│   │   │   ├── MyappApplication.java   ← entry point (@SpringBootApplication)
│   │   │   ├── controller/
│   │   │   ├── service/
│   │   │   ├── repository/
│   │   │   └── model/
│   │   └── resources/
│   │       ├── application.properties  ← primary config
│   │       ├── application-dev.yml     ← profile-specific config
│   │       └── static/                 ← static web assets
│   │       └── templates/              ← Thymeleaf templates
│   └── test/
│       └── java/com/example/myapp/
│           └── MyappApplicationTests.java
├── pom.xml  (or build.gradle)
└── .mvn/ (or gradlew)
```

---

## @SpringBootApplication

```java
@SpringBootApplication
public class MyappApplication {
    public static void main(String[] args) {
        SpringApplication.run(MyappApplication.class, args);
    }
}
```

`@SpringBootApplication` is shorthand for three annotations:

| Annotation | Effect |
|-----------|--------|
| `@Configuration` | Marks the class as a source of bean definitions |
| `@EnableAutoConfiguration` | Triggers Spring Boot's auto-configuration machinery |
| `@ComponentScan` | Scans the current package and sub-packages for components |

**Place it in the root package** (e.g., `com.example.myapp`) so the component scan reaches all sub-packages.

---

## Auto-Configuration Internals

Spring Boot scans for auto-configuration classes registered in:
- **Spring Boot 2.x**: `META-INF/spring.factories` under `EnableAutoConfiguration`
- **Spring Boot 3.x**: `META-INF/spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports`

Each auto-configuration class uses `@ConditionalOn*` annotations to apply only when its conditions are met:

| Condition | When it applies |
|-----------|----------------|
| `@ConditionalOnClass(DataSource.class)` | Only if DataSource is on the classpath |
| `@ConditionalOnMissingBean(DataSource.class)` | Only if user hasn't defined their own DataSource |
| `@ConditionalOnProperty("spring.datasource.url")` | Only if the property is set |
| `@ConditionalOnWebApplication` | Only in a web application context |

### Debugging Auto-Configuration

```bash
# Print full auto-config report at startup
java -jar myapp.jar --debug

# Or in application.properties
debug=true
```

The report shows three sections:
- **Positive matches** — what was auto-configured and why
- **Negative matches** — what was skipped and the failing condition
- **Exclusions** — what you explicitly excluded

### Excluding Auto-Configuration

```java
@SpringBootApplication(exclude = {DataSourceAutoConfiguration.class})
```

Or via properties:
```properties
spring.autoconfigure.exclude=org.springframework.boot.autoconfigure.jdbc.DataSourceAutoConfiguration
```

---

## Starters

Starters are Maven/Gradle dependency descriptors that bring in all required dependencies for a feature. You never import Spring jars individually.

```xml
<!-- pom.xml parent — manages all Spring Boot dependency versions -->
<parent>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-parent</artifactId>
    <version>3.2.0</version>
</parent>

<!-- No version needed — managed by parent -->
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-web</artifactId>
</dependency>
```

| Starter | What it includes |
|---------|-----------------|
| `spring-boot-starter` | Core: logging, yaml, spring-core |
| `spring-boot-starter-web` | Spring MVC, Tomcat, Jackson (JSON) |
| `spring-boot-starter-webflux` | Spring WebFlux, Netty, Reactor |
| `spring-boot-starter-data-jpa` | Hibernate, Spring Data JPA, JDBC |
| `spring-boot-starter-security` | Spring Security, BCrypt |
| `spring-boot-starter-test` | JUnit 5, Mockito, AssertJ, Hamcrest |
| `spring-boot-starter-actuator` | Health, info, metrics endpoints |
| `spring-boot-starter-thymeleaf` | Thymeleaf template engine |

---

## SpringApplication Customization

```java
// Programmatic customization before context refresh
SpringApplication app = new SpringApplication(MyappApplication.class);
app.setBannerMode(Banner.Mode.OFF);
app.setWebApplicationType(WebApplicationType.NONE); // non-web app
app.run(args);

// Fluent API alternative
new SpringApplicationBuilder()
    .sources(MyappApplication.class)
    .bannerMode(Banner.Mode.OFF)
    .run(args);
```

---

## Running the Application

```bash
# Via Maven wrapper
./mvnw spring-boot:run

# Via Gradle wrapper
./gradlew bootRun

# Run the executable JAR
java -jar target/myapp-0.0.1-SNAPSHOT.jar

# With a specific profile
java -jar myapp.jar --spring.profiles.active=dev

# Passing property overrides
java -jar myapp.jar --server.port=9090
```

---

## Spring Boot Versions — Key Differences

| Version | Java Baseline | Notable Changes |
|---------|--------------|----------------|
| 2.7.x | Java 8+ | Last 2.x release; uses `spring.factories` |
| 3.0.x | Java 17+ | Jakarta EE 9 namespace (`javax` → `jakarta`), `AutoConfiguration.imports` |
| 3.1.x | Java 17+ | Docker Compose support, service connections |
| 3.2.x | Java 17+ | Virtual threads (Project Loom) support, improved observability |

**Migration note (2.x → 3.x)**: Replace all `javax.*` imports with `jakarta.*`.
