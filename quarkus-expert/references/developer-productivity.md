# Developer Productivity
## Chapter 3: Live Coding, Configuration, Dev UI, Dev Services, Continuous Testing

---

## Dev Mode — Live Coding

Start dev mode with a single command:

```bash
./mvnw quarkus:dev
# or
quarkus dev
```

Dev mode watches source files and **reloads on the next HTTP request** — no manual restart needed. Changes to:
- Java source files → recompiled and redeployed in milliseconds
- `application.properties` → hot-reloaded
- Static resources (`META-INF/resources/`) → served immediately
- Templates (Qute) → picked up on next render

### How Live Coding Works

```
HTTP request arrives
    │
    ▼
Quarkus checks: have source files changed since last request?
    ├── No  → serve normally
    └── Yes → compile changed classes → reload CDI context → serve
```

No server restart; only the changed beans are re-wired. CDI application scope is preserved across reloads unless you change the scope itself.

---

## Configuration

### application.properties

All configuration lives in `src/main/resources/application.properties`:

```properties
# Application port
quarkus.http.port=8080

# Database
quarkus.datasource.db-kind=postgresql
quarkus.datasource.username=app
quarkus.datasource.password=secret
quarkus.datasource.jdbc.url=jdbc:postgresql://localhost:5432/mydb

# Log level
quarkus.log.level=INFO
quarkus.log.category."com.example".level=DEBUG
```

### Injecting Configuration

```java
import org.eclipse.microprofile.config.inject.ConfigProperty;

@ApplicationScoped
public class GreetingService {

    @ConfigProperty(name = "greeting.message", defaultValue = "Hello")
    String message;

    @ConfigProperty(name = "greeting.suffix")
    Optional<String> suffix;      // Optional = not required

    @ConfigProperty(name = "greeting.name")
    Instance<String> name;        // Lazy, re-read on each call
}
```

### Typed Config Groups

```java
@ConfigMapping(prefix = "greeting")
public interface GreetingConfig {
    String message();
    Optional<String> suffix();
    Map<String, String> aliases();
}
```

```properties
greeting.message=Hello
greeting.suffix=!
greeting.aliases.en=Hello
greeting.aliases.fr=Bonjour
```

### Configuration Profiles

Quarkus ships with three built-in profiles:

| Profile | Activation |
|---|---|
| `dev` | `quarkus:dev` |
| `test` | `@QuarkusTest` runs |
| `prod` | `java -jar` / native binary |

Profile-specific properties use the `%profile.` prefix:

```properties
# Default (prod)
quarkus.datasource.jdbc.url=jdbc:postgresql://db.prod:5432/mydb

# Override in dev mode only
%dev.quarkus.datasource.jdbc.url=jdbc:postgresql://localhost:5432/devdb

# Override in test only
%test.quarkus.datasource.db-kind=h2
%test.quarkus.datasource.jdbc.url=jdbc:h2:mem:test
```

### Custom Profiles

```bash
# Activate a custom profile
java -Dquarkus.profile=staging -jar app.jar
# or
QUARKUS_PROFILE=staging ./app-runner
```

```properties
%staging.quarkus.datasource.jdbc.url=jdbc:postgresql://staging-db:5432/mydb
```

### Configuration Sources (Priority, Highest First)

1. System properties (`-Dkey=value`)
2. Environment variables (`QUARKUS_HTTP_PORT=9090`)
3. `.env` file in working directory
4. `application.properties` in `$PWD/config/`
5. `application.properties` in classpath
6. Extension defaults

### Environment Variable Mapping

MicroProfile Config maps env vars to property names:
- `QUARKUS_HTTP_PORT` → `quarkus.http.port`
- `GREETING_MESSAGE` → `greeting.message`
- Replace `.` and `-` with `_`, uppercase

---

## Dev UI

Available at **http://localhost:8080/q/dev** in dev mode only.

### What It Shows

- **Extensions panel** — all installed extensions with links to their Dev UI pages
- **Configuration editor** — read and modify `application.properties` live
- **CDI beans browser** — all beans, their scopes, injection points
- **Routes** — all HTTP routes registered by the app
- **Dev Services status** — which services are running, their ports

### Extension-Specific Dev UIs

| Extension | Dev UI feature |
|---|---|
| `hibernate-orm` | Run JPQL queries, view entity metadata |
| `smallrye-health` | Trigger health checks, see results |
| `smallrye-openapi` | Swagger UI |
| `kafka` | Browse topics, send/consume messages |
| `keycloak` (Dev Service) | Pre-configured realm, users |
| `redis` | Redis CLI |

---

## Dev Services

Dev Services **automatically start containerized dependencies** (via Testcontainers) when no explicit configuration is provided. Zero config needed for local development.

### Supported Dev Services

| Extension | Dev Service Starts |
|---|---|
| `jdbc-postgresql` | PostgreSQL container |
| `jdbc-mysql` | MySQL container |
| `jdbc-mariadb` | MariaDB container |
| `mongodb-client` | MongoDB container |
| `smallrye-reactive-messaging-kafka` | Kafka + Zookeeper containers |
| `smallrye-reactive-messaging-rabbitmq` | RabbitMQ container |
| `oidc` (Keycloak) | Keycloak container with dev realm |
| `redis-client` | Redis container |
| `elasticsearch` | Elasticsearch container |

### How It Works

```
quarkus:dev starts
    │
    ▼
Quarkus checks: is quarkus.datasource.jdbc.url set?
    ├── Yes → use it (your own DB)
    └── No  → start PostgreSQL container via Testcontainers
               inject generated JDBC URL automatically
               stop container when dev mode exits
```

### Dev Services Configuration

```properties
# Disable a specific Dev Service
quarkus.devservices.enabled=false
quarkus.datasource.devservices.enabled=false

# Use a specific container image
quarkus.datasource.devservices.image-name=postgres:15

# Expose a fixed port (default is random)
quarkus.datasource.devservices.port=5432

# Shared across multiple Quarkus apps
quarkus.datasource.devservices.shared=true
quarkus.datasource.devservices.service-name=shared-postgres
```

---

## Continuous Testing

Quarkus runs tests **in the background** as you code — results appear in the terminal and Dev UI without running `mvn test` manually.

### Activation

```
# In dev mode terminal, press:
r  → run all tests now
o  → toggle continuous testing on/off
d  → run failing tests only
?  → list all shortcuts
```

Or set permanently:
```properties
quarkus.test.continuous-testing=enabled
```

### Test Output in Dev Mode

```
Tests paused
Press [r] to resume testing, [o] to toggle test output, [h] for more options>

All 12 tests are passing (0 skipped), 12 tests were run in 1.23s.
```

### Test Profiles with Dev Services

Tests automatically get their own Dev Service containers isolated from the dev mode containers. No port conflicts.

---

## Remote Dev Mode

Sync live code to a **remote Quarkus instance** (useful for K8s dev loops):

```bash
# Package as mutable JAR
./mvnw package -Dquarkus.package.jar.type=mutable-jar

# Connect to remote instance
./mvnw quarkus:remote-dev -Dquarkus.live-reload.url=http://my-remote-host:8080 \
  -Dquarkus.live-reload.password=mysecret
```

The local file watcher syncs class changes to the remote pod over HTTP; same live-reload semantics without rebuilding the container image.
