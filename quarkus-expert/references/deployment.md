# Deployment
## Chapter 11: Container Images, Kubernetes, OpenShift, Serverless (Funqy, Knative)

---

## Container Image Building

### Available Builders

| Extension | Tool | Notes |
|---|---|---|
| `quarkus-container-image-docker` | Docker/Podman | Uses generated Dockerfiles |
| `quarkus-container-image-jib` | Jib | No Docker daemon needed |
| `quarkus-container-image-buildpack` | Cloud Native Buildpacks | No Dockerfile needed |
| `quarkus-container-image-openshift` | OpenShift S2I | Remote build on OpenShift |

### Build and Push

```bash
# Build JVM image
./mvnw package -Dquarkus.container-image.build=true

# Build native image
./mvnw package -Pnative \
  -Dquarkus.native.container-build=true \
  -Dquarkus.container-image.build=true

# Build and push
./mvnw package \
  -Dquarkus.container-image.build=true \
  -Dquarkus.container-image.push=true
```

### Image Configuration

```properties
quarkus.container-image.group=myorg
quarkus.container-image.name=my-app
quarkus.container-image.tag=1.0.0
quarkus.container-image.registry=quay.io
quarkus.container-image.username=${REGISTRY_USER}
quarkus.container-image.password=${REGISTRY_PASSWORD}

# Jib-specific
quarkus.jib.base-jvm-image=registry.access.redhat.com/ubi8/openjdk-17:latest
quarkus.jib.base-native-image=quay.io/quarkus/quarkus-micro-image:2.0
```

### Generated Dockerfiles

Quarkus generates optimized multi-stage Dockerfiles:

```
src/main/docker/
├── Dockerfile.jvm           # Multi-layer JVM image
├── Dockerfile.native        # Native binary image
└── Dockerfile.native-micro  # Distroless native image (smallest)
```

---

## Kubernetes Deployment

```xml
<dependency>
    <groupId>io.quarkus</groupId>
    <artifactId>quarkus-kubernetes</artifactId>
</dependency>
```

### Generate Kubernetes Manifests

```bash
./mvnw package
# Generated at: target/kubernetes/kubernetes.yml
```

### Key Configuration

```properties
# Deployment
quarkus.kubernetes.name=my-app
quarkus.kubernetes.namespace=production
quarkus.kubernetes.replicas=3
quarkus.kubernetes.image-pull-policy=Always

# Resources
quarkus.kubernetes.resources.requests.memory=256Mi
quarkus.kubernetes.resources.requests.cpu=250m
quarkus.kubernetes.resources.limits.memory=512Mi
quarkus.kubernetes.resources.limits.cpu=500m

# Service
quarkus.kubernetes.service-type=ClusterIP    # or LoadBalancer, NodePort

# Health probes (auto-configured when quarkus-smallrye-health is present)
quarkus.kubernetes.liveness-probe.http-action-path=/q/health/live
quarkus.kubernetes.readiness-probe.http-action-path=/q/health/ready

# Environment variables
quarkus.kubernetes.env.vars.JAVA_OPTS=-Xmx256m

# Secrets
quarkus.kubernetes.env.secrets=db-credentials
quarkus.kubernetes.env.configmaps=app-config
```

### ConfigMap and Secret Injection

```properties
# Inject entire ConfigMap as env vars
quarkus.kubernetes.env.configmaps=app-config

# Inject specific key
quarkus.kubernetes.env.mapping.DB_HOST.from-configmap=app-config
quarkus.kubernetes.env.mapping.DB_HOST.with-key=database.host

# Inject from Secret
quarkus.kubernetes.env.mapping.DB_PASSWORD.from-secret=db-credentials
quarkus.kubernetes.env.mapping.DB_PASSWORD.with-key=password
```

### Deploy

```bash
# Generate and apply
./mvnw package -Dquarkus.kubernetes.deploy=true

# Or apply manually
kubectl apply -f target/kubernetes/kubernetes.yml
```

---

## OpenShift Deployment

```xml
<dependency>
    <groupId>io.quarkus</groupId>
    <artifactId>quarkus-openshift</artifactId>
</dependency>
```

```properties
quarkus.openshift.route.expose=true           # create a Route
quarkus.openshift.replicas=2
```

```bash
# Build image on OpenShift using S2I and deploy
./mvnw package -Dquarkus.openshift.deploy=true
```

OpenShift extension generates a `DeploymentConfig`, `Service`, `Route`, and `BuildConfig`.

---

## Serverless with Funqy

Funqy provides a cloud-function API that targets multiple platforms (AWS Lambda, Azure Functions, Google Cloud Functions, Knative).

```xml
<!-- Funqy + target platform -->
<dependency>
    <groupId>io.quarkus</groupId>
    <artifactId>quarkus-funqy-knative-events</artifactId>
    <!-- or: quarkus-funqy-amazon-lambda -->
    <!-- or: quarkus-funqy-azure-functions -->
    <!-- or: quarkus-funqy-gcp-functions -->
</dependency>
```

### Writing a Function

```java
@ApplicationScoped
public class GreetingFunction {

    @Funq
    public Greeting greet(Person person) {
        return new Greeting("Hello, " + person.getName());
    }

    // Reactive
    @Funq
    public Uni<Greeting> greetAsync(Person person) {
        return Uni.createFrom().item(() ->
            new Greeting("Hello, " + person.getName()));
    }

    // CloudEvents (Knative)
    @Funq
    @FunqyKnativeEventMapping(source = "/quarkus/funqy", type = "greet")
    public CloudEvent<Greeting> greetCloud(@CloudEventMapping Person person) {
        return CloudEventBuilder.create()
            .build(new Greeting("Hello, " + person.getName()));
    }
}
```

### AWS Lambda

```bash
./mvnw package -Pnative -Dquarkus.native.container-build=true

# Deploy via SAM CLI or AWS CDK
aws lambda create-function \
  --function-name my-function \
  --runtime provided.al2 \
  --handler io.quarkus.amazon.lambda.runtime.QuarkusStreamHandler::handleRequest \
  --zip-file fileb://target/function.zip
```

```properties
quarkus.lambda.handler=greet          # which @Funq method to invoke
```

---

## Knative (Serverless on Kubernetes)

```xml
<dependency>
    <groupId>io.quarkus</groupId>
    <artifactId>quarkus-kubernetes-config</artifactId>
</dependency>
<dependency>
    <groupId>io.quarkus</groupId>
    <artifactId>quarkus-funqy-knative-events</artifactId>
</dependency>
```

```yaml
# knative-service.yaml (generated or manual)
apiVersion: serving.knative.dev/v1
kind: Service
metadata:
  name: my-quarkus-app
spec:
  template:
    spec:
      containers:
        - image: quay.io/myorg/my-app:1.0.0
          resources:
            limits:
              memory: 128Mi
```

Native mode is ideal for Knative: scale-to-zero with ~20ms cold start.

---

## Kubernetes Config — Reading ConfigMaps/Secrets

```xml
<dependency>
    <groupId>io.quarkus</groupId>
    <artifactId>quarkus-kubernetes-config</artifactId>
</dependency>
```

```properties
quarkus.kubernetes-config.enabled=true
quarkus.kubernetes-config.config-maps=app-config
quarkus.kubernetes-config.secrets=app-secrets
quarkus.kubernetes-config.namespace=production
```

Values in the ConfigMap/Secret are injected as standard `@ConfigProperty` values.

---

## Graceful Shutdown

```properties
quarkus.shutdown.timeout=10S       # wait up to 10s for in-flight requests to finish
```

Kubernetes drain: Quarkus marks readiness as DOWN immediately when `SIGTERM` is received, then waits for `quarkus.shutdown.timeout` before exiting. Combine with a `preStop` hook delay:

```yaml
lifecycle:
  preStop:
    exec:
      command: ["sh", "-c", "sleep 5"]   # let kube-proxy drain before SIGTERM
```

---

## Multi-Architecture Builds

```bash
# Buildx for multi-arch JVM image
docker buildx build --platform linux/amd64,linux/arm64 \
  -f src/main/docker/Dockerfile.jvm \
  -t quay.io/myorg/my-app:1.0.0 \
  --push .
```

For native ARM64 binary, build on an ARM64 host or use cross-compilation with GraalVM container builder.
