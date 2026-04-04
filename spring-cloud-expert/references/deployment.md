---
name: deployment
description: Dockerizing Spring Boot services, Docker Compose multi-service stacks, Kubernetes deployments and services, ConfigMaps, Secrets, health probes, and CI/CD pipeline patterns. Chapter 10 of Spring Microservices in Action.
type: reference
---

# Deploying Microservices: Docker and Kubernetes

## Why Containers for Microservices?

Microservices multiply deployment complexity. Running 10 services manually on VMs is error-prone and environment-specific. Containers solve this with:
- **Reproducibility** — same image runs in dev, staging, and production
- **Isolation** — no dependency conflicts between services
- **Fast startup** — Spring Boot in < 5 seconds
- **Orchestration** — Kubernetes handles scheduling, scaling, and self-healing

---

## Dockerizing a Spring Boot Service

### Dockerfile (Layered JAR)

Spring Boot 2.3+ supports layered JARs, which produce smaller Docker layer caches.

```dockerfile
# Stage 1: Extract layers
FROM eclipse-temurin:17-jre AS builder
WORKDIR /application
ARG JAR_FILE=target/*.jar
COPY ${JAR_FILE} application.jar
RUN java -Djarmode=layertools -jar application.jar extract

# Stage 2: Build final image
FROM eclipse-temurin:17-jre
WORKDIR /application
COPY --from=builder /application/dependencies/ ./
COPY --from=builder /application/spring-boot-loader/ ./
COPY --from=builder /application/snapshot-dependencies/ ./
COPY --from=builder /application/application/ ./
ENTRYPOINT ["java", "org.springframework.boot.loader.JarLauncher"]
```

### Build and Run
```bash
mvn clean package -DskipTests
docker build -t license-service:1.0 .
docker run -p 8080:8080 \
  -e SPRING_PROFILES_ACTIVE=dev \
  -e DB_URL=jdbc:postgresql://db:5432/licenses \
  license-service:1.0
```

### Buildpacks (No Dockerfile Needed)
Spring Boot 2.3+ can build OCI images without a Dockerfile:
```bash
mvn spring-boot:build-image -Dspring-boot.build-image.imageName=license-service:1.0
```

---

## Docker Compose (Local Development)

### docker-compose.yml

```yaml
version: '3.8'

services:
  # Infrastructure
  postgres:
    image: postgres:15
    environment:
      POSTGRES_USER: root
      POSTGRES_PASSWORD: root
      POSTGRES_DB: licenses
    ports:
      - "5432:5432"

  zookeeper:
    image: confluentinc/cp-zookeeper:7.4.0
    environment:
      ZOOKEEPER_CLIENT_PORT: 2181

  kafka:
    image: confluentinc/cp-kafka:7.4.0
    depends_on: [zookeeper]
    environment:
      KAFKA_BROKER_ID: 1
      KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://kafka:9092
    ports:
      - "9092:9092"

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  zipkin:
    image: openzipkin/zipkin
    ports:
      - "9411:9411"

  # Spring Cloud Infrastructure
  config-server:
    image: config-server:1.0
    environment:
      SPRING_PROFILES_ACTIVE: native
      SPRING_CLOUD_CONFIG_SERVER_NATIVE_SEARCHLOCATIONS: /config
    volumes:
      - ./config:/config
    ports:
      - "8888:8888"

  eureka-server:
    image: eureka-server:1.0
    depends_on: [config-server]
    ports:
      - "8761:8761"

  # Business Services
  organization-service:
    image: organization-service:1.0
    depends_on: [config-server, eureka-server, postgres]
    environment:
      SPRING_PROFILES_ACTIVE: dev
      SPRING_CLOUD_CONFIG_URI: http://config-server:8888
    ports:
      - "8085:8085"

  license-service:
    image: license-service:1.0
    depends_on: [config-server, eureka-server, organization-service]
    environment:
      SPRING_PROFILES_ACTIVE: dev
      SPRING_CLOUD_CONFIG_URI: http://config-server:8888
    ports:
      - "8080:8080"

  gateway-server:
    image: gateway-server:1.0
    depends_on: [config-server, eureka-server]
    ports:
      - "5555:5555"
```

### Service Startup Order

Use `depends_on` for container start order, but also implement retry logic (`spring.cloud.config.fail-fast=true` + retry) for cases where the dependency container starts but isn't ready yet.

Consider `wait-for-it.sh` or `dockerize` for strict readiness gating:
```yaml
command: ["sh", "-c", "wait-for-it config-server:8888 -- java -jar /app.jar"]
```

---

## Kubernetes Deployment

### Deployment

```yaml
# license-service-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: license-service
  labels:
    app: license-service
spec:
  replicas: 3
  selector:
    matchLabels:
      app: license-service
  template:
    metadata:
      labels:
        app: license-service
    spec:
      containers:
        - name: license-service
          image: myregistry/license-service:1.0
          ports:
            - containerPort: 8080
          env:
            - name: SPRING_PROFILES_ACTIVE
              value: "prod"
            - name: SPRING_CLOUD_CONFIG_URI
              value: "http://config-server:8888"
            - name: DB_PASSWORD
              valueFrom:
                secretKeyRef:
                  name: db-secret
                  key: password
          resources:
            requests:
              memory: "256Mi"
              cpu: "250m"
            limits:
              memory: "512Mi"
              cpu: "500m"
          livenessProbe:
            httpGet:
              path: /actuator/health/liveness
              port: 8080
            initialDelaySeconds: 30
            periodSeconds: 10
          readinessProbe:
            httpGet:
              path: /actuator/health/readiness
              port: 8080
            initialDelaySeconds: 20
            periodSeconds: 5
```

### Service (ClusterIP)

```yaml
# license-service-service.yaml
apiVersion: v1
kind: Service
metadata:
  name: license-service
spec:
  selector:
    app: license-service
  ports:
    - port: 8080
      targetPort: 8080
  type: ClusterIP   # Internal only; expose externally via Ingress or LoadBalancer
```

### ConfigMap (Non-sensitive Config)

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: license-service-config
data:
  application.yml: |
    spring:
      datasource:
        url: jdbc:postgresql://postgres:5432/licenses
    server:
      port: 8080
```

Mount in the deployment:
```yaml
volumeMounts:
  - name: config
    mountPath: /config
volumes:
  - name: config
    configMap:
      name: license-service-config
```

### Secret (Sensitive Config)

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: db-secret
type: Opaque
data:
  password: bXlzZWNyZXRwYXNz   # base64 encoded
```

Create from command line:
```bash
kubectl create secret generic db-secret --from-literal=password=mysecretpass
```

---

## Spring Boot Actuator Health Probes

Configure separate liveness and readiness groups for Kubernetes:

```yaml
management:
  health:
    livenessstate:
      enabled: true
    readinessstate:
      enabled: true
  endpoint:
    health:
      probes:
        enabled: true
      show-details: always
  endpoints:
    web:
      exposure:
        include: health, info, metrics, prometheus
```

| Probe | Path | Meaning |
|-------|------|---------|
| Liveness | `/actuator/health/liveness` | Is the app alive? (Restart if DOWN) |
| Readiness | `/actuator/health/readiness` | Ready for traffic? (Remove from LB if DOWN) |

### Custom Health Indicator

```java
@Component
public class DatabaseHealthIndicator implements HealthIndicator {

    private final DataSource dataSource;

    @Override
    public Health health() {
        try (Connection conn = dataSource.getConnection()) {
            conn.createStatement().executeQuery("SELECT 1");
            return Health.up().build();
        } catch (Exception e) {
            return Health.down(e).build();
        }
    }
}
```

---

## CI/CD Pipeline Pattern

```
Developer push
    ↓
Git (feature branch)
    ↓
Pull Request → CI Build
    │  mvn test
    │  mvn spring-boot:build-image
    │  docker push registry/service:${GIT_SHA}
    ↓
Merge to main
    ↓
Deploy to Staging
    │  kubectl set image deployment/license-service \
    │         license-service=registry/license-service:${GIT_SHA}
    │  kubectl rollout status deployment/license-service
    ↓
Smoke Tests
    ↓
Deploy to Production (gated / manual approval)
```

### Rolling Update (Zero Downtime)

Kubernetes performs rolling updates by default:
```bash
kubectl set image deployment/license-service \
    license-service=registry/license-service:2.0

# Monitor progress
kubectl rollout status deployment/license-service

# Rollback if needed
kubectl rollout undo deployment/license-service
```

### Canary Deployment

Run two Deployments with the same Service selector, controlling traffic via replica count:
```yaml
# v1: 9 replicas (90%)
# v2-canary: 1 replica (10%)
```

Or use an Ingress controller (Nginx, Istio) for weighted routing.

---

## Kubernetes vs. Docker Compose Equivalents

| Docker Compose | Kubernetes |
|---------------|-----------|
| `service:` block | `Deployment` + `Service` |
| `environment:` | `env` in Pod spec + `ConfigMap` / `Secret` |
| `volumes:` | `PersistentVolumeClaim` + `Volume` |
| `depends_on:` | Init containers or retry logic |
| `ports:` | `Service` with `NodePort` or `LoadBalancer` |
| `networks:` | Namespaces + `NetworkPolicy` |
| `docker-compose scale` | `kubectl scale deployment` |

---

## Common Issues

| Issue | Resolution |
|-------|------------|
| Service can't reach Config Server on startup | Add retry: `spring.cloud.config.retry.*`; use init container |
| OOMKilled in Kubernetes | Increase memory limit; tune JVM: `-XX:MaxRAMPercentage=75.0` |
| Pods stuck in CrashLoopBackOff | `kubectl logs <pod>` + `kubectl describe pod <pod>` |
| Health probe fails on startup | Increase `initialDelaySeconds` or use startup probe |
| Config changes not picked up | POST `/actuator/busrefresh` or rolling restart |
| Image pull errors | Check `imagePullPolicy`, registry credentials, image tag |
