# Spring Boot 2.3 — Version-Specific Features

## What's New in 2.3

Spring Boot 2.3.0 (released May 2020) introduced:

1. **Graceful shutdown** (`server.shutdown=graceful`)
2. **Liveness and readiness probes** (Kubernetes-native)
3. **Docker/OCI image building** (`spring-boot:build-image` via Cloud Native Buildpacks)
4. **Layered JARs** for optimized Docker image layering
5. **`spring-boot-starter-validation` separated** from `spring-boot-starter-web`
6. **R2DBC GA** support (`spring-boot-starter-data-r2dbc`)
7. **WebClient auto-configuration** improvements
8. Spring Framework 5.2.x, Java 14 support

---

## 1. Graceful Shutdown

Previously, the embedded server shut down abruptly. In 2.3, graceful shutdown is supported for all embedded servers (Tomcat, Jetty, Undertow, Reactor Netty).

```properties
server.shutdown=graceful

# Max wait time for in-flight requests to complete (default: 30s)
spring.lifecycle.timeout-per-shutdown-task=30s
```

**Behavior:**
1. Application receives shutdown signal (SIGTERM / `SpringApplication.exit()`)
2. Server stops accepting new requests immediately (returns 503)
3. Waits up to `timeout-per-shutdown-task` for in-flight requests to complete
4. Then closes connections and shuts down

**For Kubernetes** — combine with a preStop hook to avoid traffic being routed after SIGTERM but before endpoints are deregistered:

```yaml
spec:
  containers:
  - name: myapp
    image: myapp:latest
    lifecycle:
      preStop:
        exec:
          command: ["sh", "-c", "sleep 10"]
    readinessProbe:
      httpGet:
        path: /actuator/health/readiness
        port: 8080
    livenessProbe:
      httpGet:
        path: /actuator/health/liveness
        port: 8080
```

```java
// Triggered by POST /actuator/shutdown (if enabled)
// Or by JVM shutdown hook:
SpringApplication.exit(SpringApplication.run(MyApp.class, args));

// Or signal the application is not ready for traffic:
AvailabilityChangeEvent.publish(eventPublisher, new RefusingTrafficEvent(), ReadinessState.REFUSING_TRAFFIC);
```

---

## 2. Liveness and Readiness Probes

Spring Boot 2.3 introduces first-class support for Kubernetes pod probes via the `ApplicationAvailability` API.

### Availability States

**LivenessState:**
- `CORRECT` — application is functioning normally
- `BROKEN` — application is in a broken state; infrastructure should restart the pod

**ReadinessState:**
- `ACCEPTING_TRAFFIC` — application is ready to receive requests
- `REFUSING_TRAFFIC` — application is not ready (e.g., still initializing, or temporarily overloaded)

### Lifecycle

```
startup:
  ApplicationStartingEvent
  ...
  ApplicationStartedEvent → LivenessState.CORRECT published
  AvailabilityChangeEvent(LivenessState.CORRECT)
  CommandLineRunner/ApplicationRunner executed
  ApplicationReadyEvent → ReadinessState.ACCEPTING_TRAFFIC published
  AvailabilityChangeEvent(ReadinessState.ACCEPTING_TRAFFIC)

shutdown (graceful):
  ReadinessState → REFUSING_TRAFFIC (stop routing)
  Wait for in-flight requests...
  Shutdown complete
```

### Actuator health groups (auto-configured in K8s environments)

```properties
# Enabled automatically when running on Kubernetes
management.endpoint.health.probes.enabled=true

# Manual enable (non-K8s environments or testing)
management.endpoint.health.probes.enabled=true
```

Endpoints:
- `GET /actuator/health/liveness` — LivenessStateHealthIndicator
- `GET /actuator/health/readiness` — ReadinessStateHealthIndicator

### Programmatic state management

```java
// Inject ApplicationAvailability to read state
@Component
public class HealthMonitor {

    private final ApplicationAvailability availability;

    public HealthMonitor(ApplicationAvailability availability) {
        this.availability = availability;
    }

    public boolean isLive() {
        return availability.getLivenessState() == LivenessState.CORRECT;
    }

    public boolean isReady() {
        return availability.getReadinessState() == ReadinessState.ACCEPTING_TRAFFIC;
    }
}

// Publish state changes
@Component
public class CacheVerifier {

    private final ApplicationEventPublisher publisher;

    public CacheVerifier(ApplicationEventPublisher publisher) {
        this.publisher = publisher;
    }

    public void markBroken(Exception ex) {
        AvailabilityChangeEvent.publish(publisher, ex, LivenessState.BROKEN);
    }

    public void markNotReady() {
        AvailabilityChangeEvent.publish(publisher, new Object(), ReadinessState.REFUSING_TRAFFIC);
    }

    public void markReady() {
        AvailabilityChangeEvent.publish(publisher, new Object(), ReadinessState.ACCEPTING_TRAFFIC);
    }
}

// Listen for availability changes
@Component
public class AvailabilityListener {

    @EventListener
    public void onLivenessChange(AvailabilityChangeEvent<LivenessState> event) {
        switch (event.getState()) {
            case CORRECT: log.info("App is live"); break;
            case BROKEN: log.error("App is broken"); break;
        }
    }

    @EventListener
    public void onReadinessChange(AvailabilityChangeEvent<ReadinessState> event) {
        switch (event.getState()) {
            case ACCEPTING_TRAFFIC: log.info("App is ready"); break;
            case REFUSING_TRAFFIC: log.warn("App refusing traffic"); break;
        }
    }
}
```

### Customizing readiness group

```properties
management.endpoint.health.group.readiness.include=readinessState,db,redis
management.endpoint.health.group.readiness.show-details=always
```

---

## 3. Docker/OCI Image Building (spring-boot:build-image)

Spring Boot 2.3 integrates with **Cloud Native Buildpacks** (CNB) to build OCI-compatible container images without writing a Dockerfile.

### Maven

```bash
# Build and push to local Docker daemon
mvn spring-boot:build-image

# Custom image name
mvn spring-boot:build-image -Dspring-boot.build-image.imageName=myregistry/myapp:1.0
```

```xml
<plugin>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-maven-plugin</artifactId>
    <configuration>
        <image>
            <!-- Default builder: gcr.io/paketo-buildpacks/builder:base-platform-api-0.3 -->
            <name>myregistry/myapp:${project.version}</name>
            <env>
                <BP_JVM_VERSION>11.*</BP_JVM_VERSION>
            </env>
            <cleanCache>false</cleanCache>
            <verboseLogging>false</verboseLogging>
        </image>
        <!-- Ensure layered JAR is enabled for efficient builds -->
        <layers>
            <enabled>true</enabled>
        </layers>
    </configuration>
</plugin>
```

### Gradle

```bash
./gradlew bootBuildImage
./gradlew bootBuildImage --imageName=myregistry/myapp:latest
```

```gradle
bootBuildImage {
    imageName = "myregistry/${project.name}:${project.version}"
    environment = ["BP_JVM_VERSION": "11.*"]
}
```

### Builder environment variables (Paketo buildpack)

| Variable | Description |
|----------|-------------|
| `BP_JVM_VERSION` | JVM version (e.g., `11.*`, `15.*`) |
| `BP_JAVA_INSTALL_NODE` | Install Node.js |
| `BPL_JVM_HEAD_ROOM` | JVM heap headroom percentage |
| `BPL_JVM_LOADED_CLASS_COUNT` | Loaded class count estimate |
| `HTTP_PROXY` / `HTTPS_PROXY` | Network proxy |
| `JAVA_TOOL_OPTIONS` | JVM options at runtime |

### Docker daemon configuration

```bash
# Minikube
eval $(minikube docker-env)

# Custom daemon
export DOCKER_HOST=tcp://192.168.99.100:2376
export DOCKER_TLS_VERIFY=1
export DOCKER_CERT_PATH=/path/to/certs

# Paketo image for JDK 11 specifically
mvn spring-boot:build-image \
  -Dspring-boot.build-image.builder=gcr.io/paketo-buildpacks/builder:base
```

---

## 4. Layered JARs

Layered JARs split the fat JAR into distinct layers that Docker can cache independently, significantly reducing image rebuild times when only application code changes.

### Default layers (in cache order, least to most likely to change)

1. `dependencies` — non-SNAPSHOT third-party dependencies
2. `spring-boot-loader` — Spring Boot JAR launcher classes
3. `snapshot-dependencies` — SNAPSHOT dependencies
4. `application` — application classes and resources (changes most often)

### Maven configuration

```xml
<plugin>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-maven-plugin</artifactId>
    <configuration>
        <layers>
            <enabled>true</enabled>
        </layers>
    </configuration>
</plugin>
```

### Gradle configuration

```gradle
bootJar {
    layered()
}
```

### Custom layers (custom layers.xml)

```xml
<!-- src/layers.xml -->
<layers xmlns="http://www.springframework.org/schema/boot/layers"
        xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
        xsi:schemaLocation="http://www.springframework.org/schema/boot/layers
                            https://www.springframework.org/schema/boot/layers/layers-2.3.xsd">
    <application>
        <into layer="spring-boot-loader">
            <include>org/springframework/boot/loader/**</include>
        </into>
        <into layer="application"/>
    </application>
    <dependencies>
        <into layer="snapshot-dependencies">
            <include>*:*:*SNAPSHOT</include>
        </into>
        <into layer="company-dependencies">
            <include>com.mycompany:*</include>
        </into>
        <into layer="dependencies"/>
    </dependencies>
    <layerOrder>
        <layer>dependencies</layer>
        <layer>spring-boot-loader</layer>
        <layer>snapshot-dependencies</layer>
        <layer>company-dependencies</layer>
        <layer>application</layer>
    </layerOrder>
</layers>
```

```xml
<!-- pom.xml -->
<configuration>
    <layers>
        <enabled>true</enabled>
        <configuration>${project.basedir}/src/layers.xml</configuration>
    </layers>
</configuration>
```

### Optimized Dockerfile using layered JARs

```dockerfile
# Stage 1: Extract layers
FROM eclipse-temurin:11-jre as builder
WORKDIR /application
ARG JAR_FILE=target/*.jar
COPY ${JAR_FILE} application.jar
RUN java -Djarmode=layertools -jar application.jar extract

# Stage 2: Build final image with layers in cache-friendly order
FROM eclipse-temurin:11-jre
WORKDIR /application

# Copy layers (least-frequently-changing first = best Docker cache hit rate)
COPY --from=builder /application/dependencies/ ./
COPY --from=builder /application/spring-boot-loader/ ./
COPY --from=builder /application/snapshot-dependencies/ ./
COPY --from=builder /application/application/ ./

# Run with JarLauncher (maintains correct classpath order)
ENTRYPOINT ["java", "org.springframework.boot.loader.JarLauncher"]
```

List layers in a layered JAR:
```bash
java -Djarmode=layertools -jar myapp.jar list
```

---

## 5. spring-boot-starter-validation Separated

**Breaking change in 2.3**: Bean Validation (JSR-380) is no longer included in `spring-boot-starter-web`. You must explicitly add:

```xml
<!-- Add this explicitly in 2.3+ (was automatic before) -->
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-validation</artifactId>
</dependency>
```

Without this, `@Valid`, `@NotBlank`, `@NotNull`, etc. will not trigger validation.

---

## 6. R2DBC GA Support

Spring Boot 2.3 includes first-class GA support for reactive relational data access via R2DBC.

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-data-r2dbc</artifactId>
</dependency>

<!-- R2DBC drivers -->
<dependency>
    <groupId>io.r2dbc</groupId>
    <artifactId>r2dbc-h2</artifactId>
    <scope>runtime</scope>
</dependency>
<dependency>
    <groupId>io.r2dbc</groupId>
    <artifactId>r2dbc-postgresql</artifactId>
    <scope>runtime</scope>
</dependency>
<dependency>
    <groupId>dev.miku</groupId>
    <artifactId>r2dbc-mysql</artifactId>
    <scope>runtime</scope>
</dependency>
```

```properties
spring.r2dbc.url=r2dbc:h2:mem:///testdb
spring.r2dbc.url=r2dbc:postgresql://localhost:5432/myapp
spring.r2dbc.username=postgres
spring.r2dbc.password=secret
```

See `data-access.md` for full R2DBC examples.

---

## 7. WebClient Auto-Configuration

Spring Boot 2.3 improves `WebClient.Builder` auto-configuration. The builder is now pre-configured with:

- Metrics instrumentation (when Micrometer is on the classpath)
- `WebClientCustomizer` beans automatically applied
- Codec configuration consistent with MVC `HttpMessageConverters`

```java
// Always inject WebClient.Builder, not WebClient directly
// This ensures customizers are applied
@Service
public class ApiService {
    private final WebClient webClient;

    public ApiService(WebClient.Builder builder) {
        // Builder has Micrometer metrics, customizers already applied
        this.webClient = builder
            .baseUrl("https://api.example.com")
            .build();
    }
}
```

WebClient runtime auto-detection order (by classpath availability):
1. Reactor Netty (with `spring-boot-starter-webflux`)
2. Jetty reactive client
3. Apache HttpClient 5
4. JDK HttpClient

---

## 8. ApplicationAvailability Bean

New in 2.3: `ApplicationAvailability` is a first-class auto-configured bean:

```java
@RestController
@RequestMapping("/status")
public class StatusController {

    private final ApplicationAvailability availability;

    public StatusController(ApplicationAvailability availability) {
        this.availability = availability;
    }

    @GetMapping
    public Map<String, String> status() {
        return Map.of(
            "liveness", availability.getLivenessState().name(),
            "readiness", availability.getReadinessState().name()
        );
    }
}
```

---

## 9. Spring Framework 5.2 Highlights (bundled with Boot 2.3)

- `@Configuration(proxyBeanMethods = false)` — Lite mode for config classes (faster startup, no CGLIB proxy)
- `RSocketRequester` — RSockets as first-class citizens
- Kotlin coroutines support in Spring MVC and WebFlux
- Performance improvements: `ApplicationContext` refresh faster, smaller memory footprint

---

## Upgrade Notes: 2.2 → 2.3

| Change | Action Required |
|--------|-----------------|
| Validation not in web starter | Add `spring-boot-starter-validation` explicitly |
| Default Gradle classpath changed | `spring.task.execution.pool.queue-capacity` default changed |
| Spring Data Neumann | Check for Spring Data breaking changes |
| Actuator probes `/actuator/health/liveness` | Available for use in Kubernetes readiness/liveness |
| `server.shutdown=graceful` | Opt in for graceful shutdown |
| `spring.jpa.open-in-view` | Still defaults to `true`, consider setting to `false` |
| `TestRestTemplate` | Now follows redirects by default |
