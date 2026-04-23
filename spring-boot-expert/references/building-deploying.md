# Building and Deploying Spring Boot Applications

Chapter 7 of *Spring Boot Up & Running* — Maven/Gradle builds, executable JAR/WAR, Docker, Buildpacks, Kubernetes, cloud deployment.

---

## Build Systems

### Maven

```xml
<!-- pom.xml — the spring-boot-maven-plugin is required for executable JARs -->
<build>
    <plugins>
        <plugin>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-maven-plugin</artifactId>
            <!-- Repackages the JAR to be self-executable -->
        </plugin>
    </plugins>
</build>
```

Common Maven commands:
```bash
./mvnw clean package          # compile, test, package → target/*.jar
./mvnw clean package -DskipTests  # skip tests (not recommended for CI)
./mvnw spring-boot:run        # run without packaging
./mvnw dependency:tree        # inspect dependency tree
./mvnw help:effective-pom     # see the fully resolved POM
```

### Gradle

```groovy
// build.gradle
plugins {
    id 'org.springframework.boot' version '3.2.0'
    id 'io.spring.dependency-management' version '1.1.4'
    id 'java'
}
```

Common Gradle commands:
```bash
./gradlew build               # compile, test, package → build/libs/*.jar
./gradlew bootRun             # run the app
./gradlew dependencies        # inspect dependency tree
./gradlew bootJar             # build executable JAR only
./gradlew bootBuildImage      # build OCI image via Buildpacks
```

---

## Executable JAR (Fat JAR)

Spring Boot's `spring-boot-maven-plugin` / `spring-boot-gradle-plugin` repackages the JAR to include all dependencies. The result is a self-contained executable:

```
target/myapp-0.0.1-SNAPSHOT.jar   ← fat JAR (includes Tomcat, all deps)
target/myapp-0.0.1-SNAPSHOT.jar.original  ← original thin JAR
```

Run:
```bash
java -jar target/myapp-0.0.1-SNAPSHOT.jar
java -jar myapp.jar --spring.profiles.active=prod --server.port=443
```

### JAR Structure

```
myapp.jar
├── BOOT-INF/
│   ├── classes/          ← compiled application classes
│   ├── classpath.idx     ← classpath ordering
│   └── lib/              ← all dependency JARs
├── META-INF/
│   └── MANIFEST.MF       ← Main-Class: org.springframework.boot.loader.JarLauncher
└── org/springframework/boot/loader/  ← Spring Boot launcher classes
```

---

## Layered JARs (Docker Optimization)

Spring Boot 2.3+ supports layered JARs to maximize Docker layer caching:

```bash
# Extract layers (Maven)
java -Djarmode=layertools -jar myapp.jar list
java -Djarmode=layertools -jar myapp.jar extract
```

This extracts 4 layers (dependencies, spring-boot-loader, snapshot-dependencies, application), which change at different frequencies, improving cache hit rate.

---

## Dockerfile (Multi-Stage Build)

```dockerfile
# Stage 1: extract layered JAR
FROM eclipse-temurin:17-jre as builder
WORKDIR /app
COPY target/myapp-0.0.1-SNAPSHOT.jar app.jar
RUN java -Djarmode=layertools -jar app.jar extract

# Stage 2: final image with layers in optimal order
FROM eclipse-temurin:17-jre
WORKDIR /app
COPY --from=builder /app/dependencies/ ./
COPY --from=builder /app/spring-boot-loader/ ./
COPY --from=builder /app/snapshot-dependencies/ ./
COPY --from=builder /app/application/ ./
EXPOSE 8080
ENTRYPOINT ["java", "org.springframework.boot.loader.JarLauncher"]
```

Build and run:
```bash
docker build -t myapp:latest .
docker run -p 8080:8080 -e SPRING_PROFILES_ACTIVE=prod myapp:latest
```

---

## Cloud Native Buildpacks (CNB)

Spring Boot integrates with Buildpacks — no Dockerfile needed:

```bash
# Maven
./mvnw spring-boot:build-image -Dspring-boot.build-image.imageName=myapp:latest

# Gradle
./gradlew bootBuildImage --imageName=myapp:latest
```

Benefits over Dockerfile:
- No Dockerfile to maintain
- Automatically applies security patches (OS layer rebuilt by Paketo team)
- Produces OCI-compliant images
- Uses layered JARs automatically
- Includes memory calculator (JVM tuning)

Configure the builder:
```xml
<plugin>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-maven-plugin</artifactId>
    <configuration>
        <image>
            <name>myregistry/myapp:${project.version}</name>
            <builder>paketobuildpacks/builder:base</builder>
            <env>
                <BP_JVM_VERSION>17</BP_JVM_VERSION>
            </env>
        </image>
    </configuration>
</plugin>
```

---

## WAR Deployment (Legacy App Servers)

For deploying to external Tomcat/WildFly (not recommended for new apps):

```xml
<!-- pom.xml -->
<packaging>war</packaging>

<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-tomcat</artifactId>
    <scope>provided</scope>  <!-- exclude embedded Tomcat -->
</dependency>
```

```java
// Main class must extend SpringBootServletInitializer
@SpringBootApplication
public class MyApp extends SpringBootServletInitializer {
    @Override
    protected SpringApplicationBuilder configure(SpringApplicationBuilder builder) {
        return builder.sources(MyApp.class);
    }
    public static void main(String[] args) {
        SpringApplication.run(MyApp.class, args);
    }
}
```

---

## Kubernetes Deployment

Minimal Kubernetes manifests for a Spring Boot app:

```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: myapp
spec:
  replicas: 2
  selector:
    matchLabels:
      app: myapp
  template:
    metadata:
      labels:
        app: myapp
    spec:
      containers:
      - name: myapp
        image: myregistry/myapp:1.0.0
        ports:
        - containerPort: 8080
        env:
        - name: SPRING_PROFILES_ACTIVE
          value: "prod"
        readinessProbe:
          httpGet:
            path: /actuator/health/readiness
            port: 8080
          initialDelaySeconds: 10
        livenessProbe:
          httpGet:
            path: /actuator/health/liveness
            port: 8080
          initialDelaySeconds: 30
---
apiVersion: v1
kind: Service
metadata:
  name: myapp
spec:
  selector:
    app: myapp
  ports:
  - port: 80
    targetPort: 8080
  type: LoadBalancer
```

Spring Boot 2.3+ exposes separate Kubernetes probes automatically:
```properties
management.endpoint.health.probes.enabled=true
management.health.livenessstate.enabled=true
management.health.readinessstate.enabled=true
```

---

## Graceful Shutdown

```properties
# Enable graceful shutdown (waits for in-flight requests to complete)
server.shutdown=graceful
spring.lifecycle.timeout-per-shutdown-phase=30s
```

---

## Environment-Specific Configuration in Deployment

Preferred approach: keep secrets out of the JAR. Use:

1. **Environment variables** (12-factor app):
   ```bash
   SPRING_DATASOURCE_URL=jdbc:postgresql://prod-db/mydb
   SPRING_DATASOURCE_PASSWORD=secret
   ```
   Spring Boot maps `SPRING_DATASOURCE_URL` → `spring.datasource.url` automatically.

2. **Kubernetes Secrets → environment variables**:
   ```yaml
   env:
   - name: SPRING_DATASOURCE_PASSWORD
     valueFrom:
       secretKeyRef:
         name: db-secret
         key: password
   ```

3. **Spring Cloud Config Server**: centralized config for multiple services.

4. **External config file**: mount `application-prod.properties` into the container at `/config/`.

---

## Docker Compose (Local Development)

Spring Boot 3.1+ has built-in Docker Compose support:

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-docker-compose</artifactId>
    <scope>runtime</scope>
</dependency>
```

Spring Boot automatically starts services defined in `compose.yaml` on startup and stops them on shutdown — no manual `docker compose up` needed during development.
