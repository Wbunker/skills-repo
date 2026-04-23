# Configuration and Actuator

Chapter 6 of *Spring Boot Up & Running* — application.properties/yml, property binding, @ConfigurationProperties, profiles, Spring Boot Actuator, health indicators.

---

## Externalized Configuration

Spring Boot loads configuration from multiple sources, in priority order (highest first):

1. Command-line arguments (`--server.port=9090`)
2. `SPRING_APPLICATION_JSON` environment variable
3. OS environment variables
4. `application-{profile}.properties` / `application-{profile}.yml`
5. `application.properties` / `application.yml` (in classpath root)
6. `@PropertySource` annotations
7. Default property values

This means you can override any property without recompiling.

---

## application.properties vs. application.yml

Both are equivalent. YAML is better for hierarchical config; prefer it for complex settings:

```properties
# application.properties
server.port=8080
server.servlet.context-path=/api
spring.datasource.url=jdbc:postgresql://localhost/mydb
spring.datasource.username=myuser
```

```yaml
# application.yml
server:
  port: 8080
  servlet:
    context-path: /api
spring:
  datasource:
    url: jdbc:postgresql://localhost/mydb
    username: myuser
```

---

## @Value

Inject individual properties:

```java
@Service
public class GreetingService {
    @Value("${app.greeting:Hello}")   // default value after colon
    private String greeting;

    @Value("${app.max-items:100}")
    private int maxItems;
}
```

Limitations: doesn't support type conversion for complex types; not validated; hard to test. Prefer `@ConfigurationProperties` for structured config.

---

## @ConfigurationProperties

Binds a block of properties to a type-safe POJO. Best practice for custom configuration:

```properties
# application.properties
app.coffee.name=Espresso
app.coffee.max-orders=50
app.coffee.origins=Brazil,Ethiopia,Colombia
```

```java
@ConfigurationProperties(prefix = "app.coffee")
@Component   // or use @EnableConfigurationProperties(CoffeeProperties.class) on @Configuration
public class CoffeeProperties {
    private String name;
    private int maxOrders;
    private List<String> origins;
    // getters/setters required (or record in Spring Boot 2.6+)
}
```

Add the annotation processor for IDE autocompletion:
```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-configuration-processor</artifactId>
    <optional>true</optional>
</dependency>
```

Add validation:
```java
@ConfigurationProperties(prefix = "app.coffee")
@Validated
public class CoffeeProperties {
    @NotBlank
    private String name;

    @Min(1) @Max(1000)
    private int maxOrders;
}
```

---

## Profiles

Profiles activate environment-specific configuration:

```yaml
# application.yml — base config
spring:
  jpa:
    hibernate:
      ddl-auto: validate

---
# application-dev.yml — or use spring.config.activate.on-profile in single file
spring:
  config:
    activate:
      on-profile: dev
  jpa:
    hibernate:
      ddl-auto: create-drop
  h2:
    console:
      enabled: true
```

Activate profiles:
```bash
# Command line
java -jar app.jar --spring.profiles.active=dev,debug

# Environment variable
SPRING_PROFILES_ACTIVE=dev

# application.properties (sets default profile)
spring.profiles.active=dev
```

Profile-specific beans:
```java
@Profile("dev")
@Bean
public DataLoader devDataLoader() { return new DevDataLoader(); }

@Profile("!prod")   // active when NOT in prod
@Component
public class DevTools { ... }
```

---

## Spring Boot Actuator

Adds production-ready HTTP endpoints for monitoring and management:

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-actuator</artifactId>
</dependency>
```

### Key Endpoints

| Endpoint | Path | Purpose |
|----------|------|---------|
| `/actuator/health` | Always exposed | App health status |
| `/actuator/info` | Always exposed | App info (version, git commit, etc.) |
| `/actuator/metrics` | Requires exposure | Micrometer metrics |
| `/actuator/env` | Requires exposure | Environment properties |
| `/actuator/beans` | Requires exposure | All Spring beans |
| `/actuator/mappings` | Requires exposure | All HTTP request mappings |
| `/actuator/loggers` | Requires exposure | View/change log levels at runtime |
| `/actuator/threaddump` | Requires exposure | JVM thread dump |
| `/actuator/heapdump` | Requires exposure | JVM heap dump |
| `/actuator/shutdown` | Disabled by default | Graceful shutdown (POST) |

### Exposing Endpoints

```properties
# Expose all endpoints over HTTP (use sparingly in prod; secure them)
management.endpoints.web.exposure.include=*

# Expose specific endpoints only
management.endpoints.web.exposure.include=health,info,metrics,loggers

# Change the actuator base path
management.endpoints.web.base-path=/actuator

# Run actuator on a different port (good for internal network only)
management.server.port=8081
```

### Health Endpoint

```json
GET /actuator/health
{
  "status": "UP",
  "components": {
    "db": { "status": "UP", "details": { "database": "PostgreSQL" } },
    "diskSpace": { "status": "UP" },
    "ping": { "status": "UP" }
  }
}
```

Show details (by default only shown to authenticated users):
```properties
management.endpoint.health.show-details=always   # dev
management.endpoint.health.show-details=when-authorized   # prod
```

### Custom Health Indicator

```java
@Component
public class CoffeeInventoryHealthIndicator implements HealthIndicator {

    private final CoffeeRepository repo;

    @Override
    public Health health() {
        long count = repo.count();
        if (count > 0) {
            return Health.up()
                    .withDetail("coffeeCount", count)
                    .build();
        }
        return Health.down()
                .withDetail("reason", "No coffees in inventory")
                .build();
    }
}
```

---

## Info Endpoint

```properties
# application.properties
info.app.name=My Coffee App
info.app.version=@project.version@   # Maven property expansion
info.app.description=Coffee ordering system
```

Enable build info (Maven):
```xml
<plugin>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-maven-plugin</artifactId>
    <executions>
        <execution>
            <goals><goal>build-info</goal></goals>
        </execution>
    </executions>
</plugin>
```

Enable git info:
```xml
<plugin>
    <groupId>io.github.git-commit-id</groupId>
    <artifactId>git-commit-id-maven-plugin</artifactId>
</plugin>
```

---

## Loggers Endpoint

View and change log levels at runtime without restart:

```bash
# View all loggers
GET /actuator/loggers

# View specific logger
GET /actuator/loggers/com.example.myapp

# Change log level at runtime
POST /actuator/loggers/com.example.myapp
Content-Type: application/json
{"configuredLevel": "DEBUG"}
```

---

## Securing Actuator

Always secure actuator endpoints in production:

```java
@Bean
public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
    http.authorizeHttpRequests(auth -> auth
        .requestMatchers("/actuator/health", "/actuator/info").permitAll()
        .requestMatchers("/actuator/**").hasRole("ADMIN")
        .anyRequest().authenticated()
    );
    return http.build();
}
```

Or run actuator on a separate port accessible only within your internal network (`management.server.port=8081`).

---

## Common Properties Reference

```properties
# Server
server.port=8080
server.servlet.context-path=/
server.error.include-message=always   # show error message in response

# Logging
logging.level.root=INFO
logging.level.com.example=DEBUG
logging.level.org.hibernate.SQL=DEBUG
logging.file.name=app.log
logging.pattern.console=%d{HH:mm:ss} %-5level %logger{36} - %msg%n

# Jackson
spring.jackson.serialization.indent-output=true
spring.jackson.default-property-inclusion=non-null

# Async
spring.task.execution.pool.core-size=5
spring.task.execution.pool.max-size=20
```
