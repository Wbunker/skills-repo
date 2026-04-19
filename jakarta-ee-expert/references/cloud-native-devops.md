# Cloud-Native DevOps for Jakarta EE

Source: *Pro Cloud-Native Java EE Apps* by Luqman Saeed & Ghazy Abdallah (Apress, 2022/2025), Chapters 1–3 and 12–13. Covers cloud-native architecture principles, TestContainers integration testing, Docker containerization, and Kubernetes deployment for Jakarta EE / MicroProfile applications.

---

## Cloud-Native Concepts for Jakarta EE (Ch 1–3)

### Jakarta EE vs. MicroProfile — Relationship

```
┌───────────────────────────────────────────────────┐
│              Your Application                      │
│                                                   │
│  Jakarta EE APIs        MicroProfile APIs         │
│  (CDI, REST, JPA,  +   (Config, Health,           │
│   Faces, Security)      Metrics, FT, JWT,          │
│                         REST Client, OpenAPI)      │
└───────────────────────────────┬───────────────────┘
                                │
         ┌──────────────────────▼────────────────────────┐
         │         Compatible Runtimes                    │
         │  WildFly · Open Liberty · Payara · Quarkus    │
         │  Helidon · TomEE                               │
         └────────────────────────────────────────────────┘
```

Jakarta EE = enterprise API spec (Eclipse Foundation). MicroProfile = cloud-native extension spec (Eclipse Foundation). Both are **vendor-neutral**; runtimes compete on implementation quality and footprint.

### Twelve-Factor Principles Applied to Jakarta EE

| Factor | Jakarta EE Implementation |
|--------|--------------------------|
| Config | MicroProfile Config (env vars, system props) |
| Processes (stateless) | `@RequestScoped` / `@Stateless` EJBs |
| Port binding | Embedded server (WildFly Bootable JAR, Quarkus) |
| Concurrency | Jakarta Concurrency 3, CDI `@Asynchronous` |
| Disposability | Fast startup via MicroProfile, Galleon layers |
| Backing services | DataSource, JMS via JNDI or MP Config |
| Logs as streams | Log to stdout; aggregate via fluentd/Loki |
| Health | MP Health → Kubernetes probes |

### Cloud-Native Application Structure

The book's case study is a **library management system** built as a set of Jakarta EE microservices:

```
book-service/          ← manages book catalog (JPA + REST)
  src/main/java/
    BookResource.java  ← JAX-RS endpoint
    BookService.java   ← CDI service bean
    Book.java          ← JPA entity
  src/main/resources/
    META-INF/
      persistence.xml
      microprofile-config.properties
  Dockerfile
  pom.xml

patron-service/        ← manages library members
loan-service/          ← handles checkouts (calls book + patron via MP REST Client)
```

Each service: one WAR, one container image, one Kubernetes Deployment.

### MicroProfile REST Client (inter-service calls)

```java
@RegisterRestClient(configKey = "book-service")
public interface BookServiceClient {
    @GET @Path("/books/{id}")
    @Produces(MediaType.APPLICATION_JSON)
    Book findBook(@PathParam("id") long id);
}
```

`microprofile-config.properties`:
```properties
book-service/mp-rest/url=http://book-service:8080
book-service/mp-rest/connectTimeout=3000
book-service/mp-rest/readTimeout=5000
```

Inject and use:
```java
@Inject
@RestClient
BookServiceClient bookClient;
```

### MicroProfile OpenAPI

Auto-generates OpenAPI 3.x doc at `/openapi`. Annotate for richer output:

```java
@Operation(summary = "Find book by ID")
@APIResponse(responseCode = "200", description = "Book found",
             content = @Content(schema = @Schema(implementation = Book.class)))
@APIResponse(responseCode = "404", description = "Not found")
@GET @Path("/{id}")
public Response getBook(@PathParam("id") long id) { ... }
```

Access at `/openapi` (YAML) or `/openapi?format=JSON`. UI available at `/openapi-ui` on some servers.

---

## Testing with TestContainers (Ch 12)

TestContainers spins up real Docker containers (database, app server) during JUnit tests — no mocks.

### Dependency Setup

```xml
<dependency>
    <groupId>org.testcontainers</groupId>
    <artifactId>testcontainers</artifactId>
    <version>1.19.x</version>
    <scope>test</scope>
</dependency>
<dependency>
    <groupId>org.testcontainers</groupId>
    <artifactId>postgresql</artifactId>
    <scope>test</scope>
</dependency>
<dependency>
    <groupId>org.testcontainers</groupId>
    <artifactId>junit-jupiter</artifactId>
    <scope>test</scope>
</dependency>
```

### Database Container Test

```java
@Testcontainers
class BookRepositoryTest {

    @Container
    static PostgreSQLContainer<?> postgres = new PostgreSQLContainer<>("postgres:16")
        .withDatabaseName("librarydb")
        .withUsername("test")
        .withPassword("test");

    static DataSource dataSource;

    @BeforeAll
    static void setup() {
        // build a DataSource pointing at the container
        PGSimpleDataSource ds = new PGSimpleDataSource();
        ds.setUrl(postgres.getJdbcUrl());
        ds.setUser(postgres.getUsername());
        ds.setPassword(postgres.getPassword());
        dataSource = ds;
    }

    @Test
    void shouldPersistBook() {
        // use dataSource with JPA EntityManagerFactory or plain JDBC
    }
}
```

### Application Server Container Test

Test the full WAR in a WildFly container using Arquillian + TestContainers:

```java
@Testcontainers
class BookResourceIT {

    @Container
    static GenericContainer<?> wildfly = new GenericContainer<>("quay.io/wildfly/wildfly:latest")
        .withExposedPorts(8080)
        .withFileSystemBind("target/book-service.war",
                            "/opt/jboss/wildfly/standalone/deployments/book-service.war")
        .waitingFor(Wait.forHttp("/book-service/api/books").forStatusCode(200));

    @Test
    void shouldReturnBooks() {
        String baseUrl = "http://localhost:" + wildfly.getMappedPort(8080);
        given().get(baseUrl + "/book-service/api/books")
               .then().statusCode(200);
    }
}
```

### TestContainers with MicroProfile Config

Override config for tests via system properties set before container starts:

```java
@BeforeAll
static void overrideConfig() {
    System.setProperty("db.url", postgres.getJdbcUrl());
    System.setProperty("external.api.url", wireMockServer.baseUrl());
}
```

### WireMock for External Services

```java
WireMockServer wireMock = new WireMockServer(WireMockConfiguration.options().dynamicPort());
wireMock.start();

wireMock.stubFor(get(urlEqualTo("/external/resource"))
    .willReturn(aResponse().withStatus(200).withBody("{\"id\":1}")));
```

---

## Docker Containerization (Ch 13)

### Dockerfile for Jakarta EE WAR (WildFly)

```dockerfile
FROM quay.io/wildfly/wildfly:31.0-jdk17

# Copy WAR into autodeploy
COPY target/book-service.war $JBOSS_HOME/standalone/deployments/

# Optional: custom standalone.xml
# COPY src/main/docker/standalone.xml $JBOSS_HOME/standalone/configuration/

EXPOSE 8080 9990
CMD ["/opt/jboss/wildfly/bin/standalone.sh", "-b", "0.0.0.0"]
```

### Bootable JAR (preferred for cloud)

Build with WildFly Maven Plugin:

```xml
<plugin>
    <groupId>org.wildfly.plugins</groupId>
    <artifactId>wildfly-maven-plugin</artifactId>
    <version>5.0.x</version>
    <configuration>
        <discover-provisioning-info>
            <version>31.0.Final</version>
        </discover-provisioning-info>
    </configuration>
    <executions>
        <execution>
            <goals><goal>package</goal></goals>
        </execution>
    </executions>
</plugin>
```

Produces `target/book-service-bootable.jar`. Dockerfile:

```dockerfile
FROM eclipse-temurin:21-jre
COPY target/book-service-bootable.jar /app/app.jar
EXPOSE 8080
ENTRYPOINT ["java", "-jar", "/app/app.jar"]
```

### Multi-Stage Build

```dockerfile
# Stage 1: build
FROM maven:3.9-eclipse-temurin-21 AS build
WORKDIR /src
COPY pom.xml .
RUN mvn dependency:go-offline
COPY src/ src/
RUN mvn package -DskipTests

# Stage 2: runtime
FROM eclipse-temurin:21-jre
COPY --from=build /src/target/book-service-bootable.jar /app/app.jar
EXPOSE 8080
ENTRYPOINT ["java", "-jar", "/app/app.jar"]
```

### Build and Push

```bash
docker build -t myregistry/book-service:1.0.0 .
docker push myregistry/book-service:1.0.0
```

---

## Kubernetes Deployment (Ch 13)

### Deployment Manifest

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: book-service
  labels:
    app: book-service
spec:
  replicas: 2
  selector:
    matchLabels:
      app: book-service
  template:
    metadata:
      labels:
        app: book-service
    spec:
      containers:
        - name: book-service
          image: myregistry/book-service:1.0.0
          ports:
            - containerPort: 8080
          env:
            - name: DB_URL
              valueFrom:
                secretKeyRef:
                  name: db-secret
                  key: url
          livenessProbe:
            httpGet:
              path: /health/live
              port: 8080
            initialDelaySeconds: 30
            periodSeconds: 10
          readinessProbe:
            httpGet:
              path: /health/ready
              port: 8080
            initialDelaySeconds: 15
            periodSeconds: 5
          resources:
            requests:
              memory: "256Mi"
              cpu: "250m"
            limits:
              memory: "512Mi"
              cpu: "500m"
```

### Service + Ingress

```yaml
apiVersion: v1
kind: Service
metadata:
  name: book-service
spec:
  selector:
    app: book-service
  ports:
    - port: 80
      targetPort: 8080
---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: library-ingress
spec:
  rules:
    - host: library.example.com
      http:
        paths:
          - path: /books
            pathType: Prefix
            backend:
              service:
                name: book-service
                port:
                  number: 80
```

### ConfigMap for MicroProfile Config

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: book-service-config
data:
  MP_CONFIG_OVERRIDE: "true"
  BOOK_SERVICE_CACHE_TTL: "300"
  LOG_LEVEL: "INFO"
```

Reference in Deployment via `envFrom`:
```yaml
envFrom:
  - configMapRef:
      name: book-service-config
```

MicroProfile Config automatically reads environment variables; no code change needed.

### Secret for DB Credentials

```bash
kubectl create secret generic db-secret \
  --from-literal=url='jdbc:postgresql://postgres:5432/librarydb' \
  --from-literal=user='appuser' \
  --from-literal=password='s3cr3t'
```

---

## Production Readiness Checklist (Ch 13)

### Health & Observability
- [ ] `@Liveness` check — JVM / thread deadlock detection
- [ ] `@Readiness` check — database connectivity, external service reachability
- [ ] MP Metrics → Prometheus scrape target configured
- [ ] Grafana dashboard for key service metrics (request rate, error rate, latency)
- [ ] Structured JSON logging to stdout (fluentd/Loki ingestion)

### Resilience
- [ ] `@Retry` on all external service calls
- [ ] `@CircuitBreaker` on downstream dependencies
- [ ] `@Timeout` on every I/O operation
- [ ] `@Fallback` returns degraded-but-useful response
- [ ] `@Bulkhead` prevents thread pool exhaustion

### Config & Secrets
- [ ] No secrets in code or Docker images
- [ ] All environment-specific config via MicroProfile Config (env vars or ConfigMap)
- [ ] Secrets in Kubernetes Secrets, not ConfigMaps

### Security
- [ ] JWT validation with HTTPS public key endpoint
- [ ] `@RolesAllowed` on every restricted endpoint
- [ ] Token expiry checked (`exp` claim)
- [ ] HTTPS enforced at ingress/load balancer level

### CI/CD Pipeline

```
Code → Unit Tests (JUnit 5)
     → Integration Tests (TestContainers)
     → docker build + push
     → kubectl apply (staging)
     → Smoke test (MP Health endpoint)
     → kubectl apply (production) with rolling update
```

### Rolling Update Strategy

```yaml
spec:
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxUnavailable: 1
      maxSurge: 1
```

Kubernetes uses readiness probe to gate traffic; pods not ready never receive requests.
