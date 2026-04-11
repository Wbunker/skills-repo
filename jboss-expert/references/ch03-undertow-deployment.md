# Ch 3 — Custom Web Deployment using Undertow (and Modern Containers)

> **Book context:** This chapter covered WildFly Swarm for microservices packaging. Swarm has been superseded. The current equivalents are **Bootable JAR** (Galleon-based, same concept) and **container-based deployment**. Undertow configuration is unchanged.

## Undertow Architecture

Undertow is WildFly's HTTP engine — a non-blocking, high-performance web server used for both the management interface and application deployments.

```
Client Request
     │
     ▼
┌─────────────┐
│   Listener  │  (HTTP/HTTPS/HTTP2, AJP)
│  (port 8080)│
└──────┬──────┘
       │
       ▼
┌──────────────┐
│  Handler     │  (filter chain)
│  Chain       │
│  ─────────   │
│  AccessLog   │
│  RequestDump │
│  Compress    │
│  ─────────   │
│  Servlet     │  (Jakarta Servlet container)
│  Handler     │
└──────────────┘
```

## Undertow Configuration (standalone.xml)

```xml
<subsystem xmlns="urn:jboss:domain:undertow:14.0">
  <buffer-cache name="default"/>

  <server name="default-server">
    <http-listener name="default" socket-binding="http"
                   redirect-socket="https"
                   enable-http2="true"/>
    <https-listener name="https" socket-binding="https"
                    ssl-context="applicationSSC"
                    enable-http2="true"/>
    <host name="default-host" alias="localhost">
      <location name="/" handler="welcome-content"/>
      <access-log pattern="%h %l %u %t &quot;%r&quot; %s %b"/>
      <filter-ref name="server-header"/>
    </host>
  </server>

  <servlet-container name="default">
    <jsp-config/>
    <session-cookie http-only="true" secure="true"/>
    <websockets/>
  </servlet-container>

  <handlers>
    <file name="welcome-content" path="${jboss.home.dir}/welcome-content"/>
  </handlers>

  <filters>
    <response-header name="server-header" header-name="Server"
                     header-value="WildFly"/>
    <gzip name="gzip"/>
  </filters>
</subsystem>
```

## Custom Undertow Filters (Java)

```java
public class CorsFilter implements HttpHandler {
    private final HttpHandler next;

    public CorsFilter(HttpHandler next) { this.next = next; }

    @Override
    public void handleRequest(HttpServerExchange exchange) throws Exception {
        exchange.getResponseHeaders()
            .put(HttpString.tryFromString("Access-Control-Allow-Origin"), "*");
        next.handleRequest(exchange);
    }
}
```

Register via `io.undertow.servlet.ServletExtension` SPI or `@WebFilter` for standard Jakarta filters:

```java
@WebFilter(urlPatterns = "/*")
public class RequestLoggingFilter implements Filter {
    @Override
    public void doFilter(ServletRequest req, ServletResponse res, FilterChain chain)
            throws IOException, ServletException {
        long start = System.currentTimeMillis();
        chain.doFilter(req, res);
        long elapsed = System.currentTimeMillis() - start;
        ((HttpServletRequest)req).getRequestURI(); // log elapsed
    }
}
```

## Deployment Descriptors

### jboss-web.xml

```xml
<?xml version="1.0" encoding="UTF-8"?>
<jboss-web xmlns="http://www.jboss.com/xml/ns/javaee">
  <context-root>/myapp</context-root>
  <security-domain>mySecurityDomain</security-domain>
  <virtual-host>default-host</virtual-host>
  <enable-websockets>true</enable-websockets>
</jboss-web>
```

### jboss-deployment-structure.xml

Controls classloading between modules:

```xml
<jboss-deployment-structure>
  <deployment>
    <dependencies>
      <module name="org.postgresql" services="import"/>
    </dependencies>
    <exclusions>
      <module name="org.hibernate"/>  <!-- use bundled Hibernate instead -->
    </exclusions>
  </deployment>
  <sub-deployment name="myapp-web.war">
    <dependencies>
      <module name="com.example.shared" export="true"/>
    </dependencies>
  </sub-deployment>
</jboss-deployment-structure>
```

## WildFly Swarm → Bootable JAR (Current Approach)

WildFly Swarm (2015–2019) is no longer maintained. The replacement is **WildFly Bootable JAR** via the WildFly Maven Plugin using Galleon layers.

### Bootable JAR — pom.xml

```xml
<plugin>
  <groupId>org.wildfly.plugins</groupId>
  <artifactId>wildfly-maven-plugin</artifactId>
  <version>5.1.0.Final</version>
  <executions>
    <execution>
      <goals><goal>package</goal></goals>
    </execution>
  </executions>
  <configuration>
    <feature-packs>
      <feature-pack>
        <location>wildfly@maven(org.jboss.universe:community-universe):current</location>
      </feature-pack>
    </feature-packs>
    <layers>
      <!-- Choose only what you need -->
      <layer>jaxrs-server</layer>       <!-- Undertow + RESTEasy -->
      <layer>microprofile-platform</layer>
      <layer>datasources-web-server</layer>
    </layers>
    <bootable-jar>true</bootable-jar>
    <bootable-jar-name>myapp-bootable</bootable-jar-name>
    <!-- CLI config applied at build time -->
    <cli-sessions>
      <cli-session>
        <script-files>
          <script>src/main/scripts/datasource.cli</script>
        </script-files>
      </cli-session>
    </cli-sessions>
  </configuration>
</plugin>
```

### Run Bootable JAR

```bash
java -jar target/myapp-bootable.jar
# With dev mode (hot reload):
mvn wildfly:dev
```

## Docker Deployment

### Dockerfile (Bootable JAR)

```dockerfile
FROM eclipse-temurin:21-jre-alpine
COPY target/myapp-bootable.jar /app/app.jar
EXPOSE 8080
ENTRYPOINT ["java", "-jar", "/app/app.jar"]
```

### Dockerfile (Traditional WAR on WildFly)

```dockerfile
FROM quay.io/wildfly/wildfly:latest
COPY target/myapp.war $JBOSS_HOME/standalone/deployments/
```

Or use Bitnami image:
```dockerfile
FROM bitnami/wildfly:latest
COPY target/myapp.war /opt/bitnami/wildfly/standalone/deployments/
```

## Kubernetes Deployment

### Option 1: WildFly Helm Charts

```bash
helm repo add wildfly https://docs.wildfly.org/wildfly-charts/
helm install myapp wildfly/wildfly \
  --set image.name=quay.io/myorg/myapp \
  --set image.tag=1.0.0 \
  --set build.enabled=false
```

`values.yaml`:
```yaml
image:
  name: quay.io/myorg/myapp
  tag: "1.0.0"
deploy:
  replicas: 3
  resources:
    requests:
      memory: "256Mi"
      cpu: "250m"
    limits:
      memory: "512Mi"
      cpu: "500m"
wildfly:
  env:
    - name: DB_URL
      valueFrom:
        secretKeyRef:
          name: db-secret
          key: url
```

### Option 2: WildFly Operator (Kubernetes/OpenShift)

```yaml
apiVersion: wildfly.org/v1alpha1
kind: WildFlyServer
metadata:
  name: myapp
spec:
  applicationImage: quay.io/myorg/myapp:1.0.0
  replicas: 3
  storage:
    volumeClaimTemplate:
      spec:
        resources:
          requests:
            storage: 1Gi
  env:
    - name: POSTGRESQL_SERVICE_HOST
      value: "postgres-service"
```

Install operator:
```bash
kubectl apply -f https://github.com/wildfly/wildfly-operator/releases/latest/download/wildfly-operator.yaml
```

### Option 3: OpenShift S2I

```bash
oc new-app wildfly~https://github.com/myorg/myapp
oc expose svc/myapp
```

## MicroProfile Health (Cloud Liveness/Readiness)

```java
@ApplicationScoped
@Liveness
public class LivenessCheck implements HealthCheck {
    @Override
    public HealthCheckResponse call() {
        return HealthCheckResponse.up("liveness");
    }
}

@ApplicationScoped
@Readiness
public class ReadinessCheck implements HealthCheck {
    @Inject DataSource ds;
    @Override
    public HealthCheckResponse call() {
        try (Connection c = ds.getConnection()) {
            return HealthCheckResponse.up("database");
        } catch (Exception e) {
            return HealthCheckResponse.down("database");
        }
    }
}
```

Endpoints (MicroProfile Health):
- `/health/live` — liveness
- `/health/ready` — readiness
- `/health` — both

Kubernetes probe config:
```yaml
livenessProbe:
  httpGet:
    path: /health/live
    port: 9990
readinessProbe:
  httpGet:
    path: /health/ready
    port: 9990
```

## Performance Tuning — Undertow

```xml
<!-- Tune thread pools -->
<subsystem xmlns="urn:jboss:domain:io:3.0">
  <worker name="default"
          io-threads="4"
          task-max-threads="32"/>
</subsystem>

<!-- Tune HTTP listener -->
<http-listener name="default"
               socket-binding="http"
               max-connections="500"
               receive-buffer-size="65536"
               send-buffer-size="65536"
               max-header-size="51200"
               enable-http2="true"/>
```

## WebSockets (Jakarta WebSocket 2.1)

```java
@ServerEndpoint("/chat/{room}")
@ApplicationScoped
public class ChatEndpoint {
    @OnOpen
    public void onOpen(Session session, @PathParam("room") String room) { }

    @OnMessage
    public void onMessage(String msg, Session session) throws IOException {
        session.getBasicRemote().sendText("Echo: " + msg);
    }

    @OnClose
    public void onClose(Session session) { }
}
```

Enable in `standalone.xml`: `<websockets/>` inside `<servlet-container>`.
