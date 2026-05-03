# Chapter 7: Open Liberty, Docker, and Kubernetes

## Open Liberty Runtime

Open Liberty is the reference implementation runtime for the book examples. It is a lightweight, modular, open-source Jakarta EE + MicroProfile runtime from IBM.

### Feature-Based Configuration

Open Liberty uses `server.xml` to declare which features (specs) to activate. Only activated features are loaded — minimal footprint.

```xml
<!-- src/main/liberty/config/server.xml -->
<server description="Stock Trader Portfolio Service">

    <featureManager>
        <feature>microProfile-4.1</feature>  <!-- all MP 4.1 specs at once -->
        <!-- OR individually: -->
        <feature>jaxrs-2.1</feature>
        <feature>cdi-2.0</feature>
        <feature>mpConfig-2.0</feature>
        <feature>mpFaultTolerance-3.0</feature>
        <feature>mpHealth-3.1</feature>
        <feature>mpMetrics-3.0</feature>
        <feature>mpJwt-1.2</feature>
        <feature>mpOpenAPI-2.0</feature>
        <feature>mpOpenTracing-2.0</feature>
        <feature>mpRestClient-2.0</feature>
    </featureManager>

    <httpEndpoint id="defaultHttpEndpoint" host="*"
                  httpPort="9080" httpsPort="9443"/>

    <webApplication location="portfolio.war" contextRoot="/"/>

    <!-- Data source -->
    <dataSource id="PortfolioDB" jndiName="jdbc/PortfolioDB">
        <jdbcDriver libraryRef="DB2Lib"/>
        <properties.db2.jcc databaseName="STOCKTRADER"
                            serverName="${DB_HOST}" portNumber="50000"
                            user="${DB_USER}" password="${DB_PASSWORD}"/>
    </dataSource>

</server>
```

### Maven Plugin

```xml
<plugin>
    <groupId>io.openliberty.tools</groupId>
    <artifactId>liberty-maven-plugin</artifactId>
    <version>3.5</version>
    <configuration>
        <serverName>defaultServer</serverName>
    </configuration>
</plugin>
```

Commands:
- `mvn liberty:dev` — dev mode with hot reload
- `mvn liberty:run` — run packaged server
- `mvn liberty:package` — create runnable JAR or ZIP

---

## Docker

### Multi-Stage Dockerfile

```dockerfile
# Stage 1: Build the application
FROM maven:3.8.4-openjdk-11 AS builder
WORKDIR /build
COPY pom.xml .
RUN mvn dependency:go-offline -B
COPY src ./src
RUN mvn package -DskipTests

# Stage 2: Runtime image
FROM open-liberty:22.0.0.1-kernel-slim-java11-openj9

# Copy server configuration
COPY --chown=1001:0 src/main/liberty/config/server.xml /config/server.xml

# Install only required features
RUN features.sh

# Copy application WAR
COPY --chown=1001:0 --from=builder /build/target/portfolio.war /config/dropins/

# Expose ports
EXPOSE 9080 9443
```

### Build and Run

```bash
docker build -t stock-trader/portfolio:latest .
docker run -p 9080:9080 \
  -e DB_HOST=mydb.example.com \
  -e DB_USER=dbuser \
  -e DB_PASSWORD=secret \
  stock-trader/portfolio:latest
```

### Environment Variable Injection

MicroProfile Config automatically reads environment variables. Variable names are transformed:
- Dots (`.`) → underscores (`_`)
- Lowercase → uppercase

So `stock.api.key` in config maps to `STOCK_API_KEY` as an env var.

---

## Kubernetes Deployment

### ConfigMap for Non-Sensitive Config

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: portfolio-config
data:
  stock.api.url: "https://api.iexcloud.io/v1"
  loyalty.gold.threshold: "50000"
  JAEGER_ENDPOINT: "http://jaeger-collector:14268/api/traces"
```

### Secret for Sensitive Config

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: portfolio-secrets
type: Opaque
stringData:
  stock.api.key: "my-iex-api-token"
  DB_PASSWORD: "supersecret"
```

### Deployment Manifest

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: portfolio
spec:
  replicas: 2
  selector:
    matchLabels:
      app: portfolio
  template:
    metadata:
      labels:
        app: portfolio
    spec:
      containers:
        - name: portfolio
          image: stock-trader/portfolio:latest
          ports:
            - containerPort: 9080
          envFrom:
            - configMapRef:
                name: portfolio-config
            - secretRef:
                name: portfolio-secrets
          livenessProbe:
            httpGet:
              path: /health/live
              port: 9080
            initialDelaySeconds: 30
            periodSeconds: 10
          readinessProbe:
            httpGet:
              path: /health/ready
              port: 9080
            initialDelaySeconds: 20
            periodSeconds: 5
          resources:
            requests:
              memory: "256Mi"
              cpu: "250m"
            limits:
              memory: "512Mi"
              cpu: "500m"
```

### Service Manifest

```yaml
apiVersion: v1
kind: Service
metadata:
  name: portfolio
spec:
  selector:
    app: portfolio
  ports:
    - protocol: TCP
      port: 9080
      targetPort: 9080
  type: ClusterIP   # internal only; use Ingress for external access
```

### Horizontal Pod Autoscaler

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: portfolio-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: portfolio
  minReplicas: 2
  maxReplicas: 10
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70
```

### MicroProfile Config from ConfigMap (Open Liberty operator)

When using the Open Liberty Operator, mount ConfigMaps directly as MicroProfile Config properties files:

```yaml
spec:
  env:
    - name: MP_CONFIG_ORDINAL_CONFIGMAP
      value: "200"
  volumeMounts:
    - name: config-volume
      mountPath: /config/configDropins/overrides
  volumes:
    - name: config-volume
      configMap:
        name: portfolio-config
```
