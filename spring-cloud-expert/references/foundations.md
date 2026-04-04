---
name: foundations
description: Microservice principles, monolith vs. microservice trade-offs, Spring Boot setup, auto-configuration, Actuator, REST endpoint design, and the 12-factor app. Chapters 1–2 of Spring Microservices in Action.
type: reference
---

# Foundations: Microservices and Spring Boot

## Why Microservices?

### Monolith Trade-offs
| Monolith | Microservices |
|----------|--------------|
| Simple to develop initially | Independent deployability |
| Single deployment unit | Per-service scaling |
| Tight coupling breeds fragility | Failure isolation |
| Technology lock-in | Polyglot services possible |
| Long build/test cycles | Small, fast CI pipelines |

Rule of thumb (Carnell): migrate when **deployment coupling** or **scaling bottlenecks** become the primary source of pain.

### Microservice Characteristics
- **Single Responsibility** — one bounded context, one deployable unit
- **Stateless** — state lives in databases or caches, not in JVM heap
- **Contract-first** — API is the public surface; internals are hidden
- **Observable** — health, metrics, and traces are first-class concerns
- **Resilient** — assume dependencies will fail; design for graceful degradation

### When NOT to Use Microservices
- Team is small (< 5 engineers); coordination overhead exceeds benefit
- Domain is not well understood; premature decomposition creates wrong boundaries
- Low operational maturity; microservices demand good CI/CD and monitoring

---

## Decomposition Strategies

### By Business Capability
Split along what the business does, not how the code is organized:
- `order-service` — manage order lifecycle
- `inventory-service` — track product stock
- `notification-service` — send emails/SMS

### By Subdomain (DDD)
- Identify bounded contexts with domain experts
- Each context owns its data model and language
- Use anti-corruption layers at context boundaries

### Sizing Heuristics
- Can be rewritten by one team in two weeks → reasonable size
- Owns exactly one database schema
- Has one reason to be deployed independently

---

## Spring Boot Essentials

### Auto-configuration
Spring Boot scans the classpath and wires beans automatically based on what's present.

```java
// @SpringBootApplication = @Configuration + @EnableAutoConfiguration + @ComponentScan
@SpringBootApplication
public class LicenseServiceApplication {
    public static void main(String[] args) {
        SpringApplication.run(LicenseServiceApplication.class, args);
    }
}
```

### Starter Dependencies
| Starter | Purpose |
|---------|---------|
| `spring-boot-starter-web` | Embedded Tomcat + Spring MVC |
| `spring-boot-starter-data-jpa` | Hibernate + Spring Data repositories |
| `spring-boot-starter-actuator` | Health, metrics, info endpoints |
| `spring-cloud-starter-config` | Config Server client |
| `spring-cloud-starter-netflix-eureka-client` | Service discovery client |

### REST Controller Pattern

```java
@RestController
@RequestMapping(value = "/v1/organizations/{organizationId}/licenses")
public class LicenseServiceController {

    @Autowired
    private LicenseService licenseService;

    @GetMapping(value = "/{licenseId}")
    public License getLicense(
            @PathVariable("organizationId") String organizationId,
            @PathVariable("licenseId") String licenseId) {
        return licenseService.getLicense(licenseId, organizationId);
    }

    @PostMapping
    public ResponseEntity<License> createLicense(
            @PathVariable("organizationId") String organizationId,
            @RequestBody License license) {
        return ResponseEntity.ok(licenseService.createLicense(license));
    }
}
```

### Spring Boot Actuator Endpoints
| Endpoint | Purpose |
|----------|---------|
| `/actuator/health` | Liveness/readiness probe |
| `/actuator/info` | App metadata |
| `/actuator/metrics` | JVM, HTTP, custom metrics |
| `/actuator/env` | Resolved property sources |
| `/actuator/refresh` | Trigger `@RefreshScope` reload |
| `/actuator/loggers` | Change log levels at runtime |

Enable all endpoints in `application.yml`:
```yaml
management:
  endpoints:
    web:
      exposure:
        include: "*"
```

---

## application.yml Structure

```yaml
spring:
  application:
    name: license-service          # Used by Eureka and Config Server
  profiles:
    active: dev                    # Active profile
  datasource:
    url: jdbc:postgresql://db:5432/licenses
    username: ${DB_USER}           # Read from environment
    password: ${DB_PASS}

server:
  port: 8080
```

### Profile-specific Files
- `application.yml` — shared defaults
- `application-dev.yml` — dev overrides
- `application-prod.yml` — production overrides

Activate with: `--spring.profiles.active=prod` or env var `SPRING_PROFILES_ACTIVE=prod`

---

## The 12-Factor App in Spring

| Factor | Implementation |
|--------|---------------|
| Codebase | One repo per service |
| Dependencies | Maven/Gradle BOM, no system-level deps |
| Config | Spring Cloud Config; environment variables |
| Backing services | Treat DB, cache, queue as attached resources |
| Build/release/run | Maven build → Docker image → Kubernetes deployment |
| Processes | Stateless; session state in Redis/JWT |
| Port binding | Spring Boot embedded server |
| Concurrency | Scale via additional instances (Kubernetes replicas) |
| Disposability | Fast startup; graceful shutdown; Actuator `/shutdown` |
| Dev/prod parity | Docker Compose mirrors production topology |
| Logs | Write to stdout; aggregate with ELK / Zipkin |
| Admin processes | Spring Batch jobs or one-off `CommandLineRunner` beans |

---

## Common Pitfalls

- **Chatty interfaces** — too many fine-grained calls; aggregate in the service, not the client
- **Shared database** — two services writing to the same schema = coupling; each service owns its schema
- **Synchronous chains** — A calls B calls C; consider async messaging for non-critical paths
- **No correlation ID** — impossible to trace failures across services; add at gateway entry
