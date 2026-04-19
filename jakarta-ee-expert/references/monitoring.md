# Monitoring and Logging
*Chapters 34–39 — JMX Monitoring Workflow, Logging, Custom Log4j Appenders*

## Chapter 34: Monitoring Workflow Using JMX

JMX (Java Management Extensions) provides a standard interface to monitor and manage Java applications at runtime — without restarting.

### JMX Architecture
```
Management Application (JConsole, VisualVM, custom)
         │ JMX Remote Protocol (RMI, JMXMP, WildFly Remoting)
         ▼
MBeanServer (platform or custom)
         │
MBeans (Standard, Dynamic, Open, Model, MXBeans)
         │
Application internals (metrics, configuration, operations)
```

### Creating an MXBean (simplest, type-safe)
```java
// Interface — defines the management contract
public interface AppHealthMXBean {
    // Attributes (read via getter)
    long getActiveConnections();
    long getProcessedRequests();
    double getErrorRate();
    boolean isHealthy();

    // Operations (callable from JConsole)
    void resetCounters();
    String getStatus();
    Map<String, Long> getMetricSnapshot();
}

// Implementation — register it
@ApplicationScoped
public class AppHealth implements AppHealthMXBean {
    private final AtomicLong activeConnections = new AtomicLong();
    private final AtomicLong processedRequests = new AtomicLong();
    private final AtomicLong errors = new AtomicLong();

    @PostConstruct
    public void register() {
        try {
            ObjectName name = new ObjectName("com.example:type=AppHealth");
            ManagementFactory.getPlatformMBeanServer()
                             .registerMBean(this, name);
        } catch (Exception e) {
            throw new RuntimeException("Failed to register MBean", e);
        }
    }

    @PreDestroy
    public void unregister() {
        try {
            ObjectName name = new ObjectName("com.example:type=AppHealth");
            ManagementFactory.getPlatformMBeanServer().unregisterMBean(name);
        } catch (Exception ignored) {}
    }

    @Override public long getActiveConnections() { return activeConnections.get(); }
    @Override public long getProcessedRequests() { return processedRequests.get(); }
    @Override public double getErrorRate() {
        long total = processedRequests.get();
        return total == 0 ? 0.0 : (double) errors.get() / total;
    }
    @Override public boolean isHealthy() { return getErrorRate() < 0.05; }
    @Override public void resetCounters() {
        activeConnections.set(0); processedRequests.set(0); errors.set(0);
    }
    @Override public String getStatus() {
        return isHealthy() ? "GREEN" : "RED";
    }
    @Override public Map<String, Long> getMetricSnapshot() {
        return Map.of(
            "connections", activeConnections.get(),
            "requests", processedRequests.get(),
            "errors", errors.get());
    }
}
```

### Connecting to JMX in WildFly
```bash
# JConsole with WildFly remote
./bin/jconsole.sh \
  -J-Djava.class.path=bin/client/jboss-client.jar:$JDK_HOME/lib/tools.jar \
  service:jmx:remote+http://localhost:9990

# Or VisualVM — install WildFly plugin, same URL
```

**Programmatic JMX client:**
```java
Map<String, Object> env = new HashMap<>();
env.put(CallbackHandler.class.getName(),
    new SimpleCallbackHandler("admin", "admin".toCharArray()));

JMXServiceURL url = new JMXServiceURL(
    "service:jmx:remote+http://localhost:9990");

try (JMXConnector connector = JMXConnectorFactory.connect(url, env)) {
    MBeanServerConnection mbs = connector.getMBeanServerConnection();

    ObjectName name = new ObjectName("com.example:type=AppHealth");
    long reqs = (Long) mbs.getAttribute(name, "ProcessedRequests");
    System.out.println("Processed: " + reqs);

    // Invoke operation
    mbs.invoke(name, "resetCounters", null, null);
}
```

### JMX Notifications
```java
public class ThresholdNotifier extends NotificationBroadcasterSupport
        implements ThresholdNotifierMXBean {

    private long sequenceNumber = 0;

    public void checkAndNotify(double errorRate) {
        if (errorRate > 0.10) {
            Notification n = new Notification(
                "com.example.highErrorRate",
                this,
                ++sequenceNumber,
                System.currentTimeMillis(),
                "Error rate exceeded 10%: " + errorRate);
            sendNotification(n);
        }
    }
}

// Client listener
mbs.addNotificationListener(name, (notification, handback) -> {
    System.out.println("Alert: " + notification.getMessage());
}, null, null);
```

### MicroProfile Metrics → JMX Bridge
MicroProfile Metrics exposes counters/gauges at `/metrics`; Prometheus scrapes that endpoint. For JMX consumption, expose the same metrics via MXBeans:
```java
@Counted(name="requests.total", description="Total HTTP requests")
public Response handleRequest() { ... }
// Prometheus: GET /metrics
// JMX: com.example:type=Metrics attribute RequestsTotal
```

---

## Chapters 35–38: Logging Workflows

### Jakarta EE Logging Best Practices

**Use `java.util.logging` (JUL) — universal, available everywhere:**
```java
import java.util.logging.Logger;

public class UserService {
    private static final Logger log =
        Logger.getLogger(UserService.class.getName());

    public User create(String email) {
        log.fine("Creating user: " + email);
        try {
            User user = repo.save(new User(email));
            log.info("Created user id=" + user.getId());
            return user;
        } catch (Exception e) {
            log.severe("Failed to create user: " + e.getMessage());
            throw e;
        }
    }
}
```

**Use SLF4J + Logback/Log4j2 — industry standard, more features:**
```xml
<dependency>
  <groupId>org.slf4j</groupId>
  <artifactId>slf4j-api</artifactId>
  <version>2.0.12</version>
</dependency>
<!-- Bridge JUL to SLF4J -->
<dependency>
  <groupId>org.slf4j</groupId>
  <artifactId>jul-to-slf4j</artifactId>
  <version>2.0.12</version>
</dependency>
```

```java
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class UserService {
    private static final Logger log = LoggerFactory.getLogger(UserService.class);

    public User create(String email) {
        log.debug("Creating user: {}", email);    // lazy param substitution
        log.info("User created: id={}, email={}", user.getId(), email);
        log.error("Failed to create user", exception);  // exception with stack trace
    }
}
```

### Structured Logging (JSON)
For log aggregation (ELK, Splunk, Grafana Loki):
```xml
<!-- Log4j2 JSON layout -->
<dependency>
  <groupId>org.apache.logging.log4j</groupId>
  <artifactId>log4j-layout-template-json</artifactId>
  <version>2.23.1</version>
</dependency>
```

`log4j2.xml`:
```xml
<Configuration>
  <Appenders>
    <Console name="json-console" target="SYSTEM_OUT">
      <JsonTemplateLayout eventTemplateUri="classpath:EcsLayout.json"/>
    </Console>
  </Appenders>
  <Loggers>
    <Root level="INFO"><AppenderRef ref="json-console"/></Root>
    <Logger name="com.example" level="DEBUG" additivity="false">
      <AppenderRef ref="json-console"/>
    </Logger>
  </Loggers>
</Configuration>
```

### MDC (Mapped Diagnostic Context) — Correlation IDs
```java
// In a filter/interceptor — set at request start
MDC.put("requestId", UUID.randomUUID().toString());
MDC.put("userId", currentUser.getId().toString());

// In your log format: %X{requestId} %X{userId}
// Or in JSON layout: "requestId": "${ctx:requestId}"

// Clean up at request end
MDC.clear();
```

**CDI-based MDC interceptor:**
```java
@Slf4j @Interceptor @Priority(Interceptor.Priority.PLATFORM_BEFORE)
public class CorrelationIdInterceptor {
    @AroundInvoke
    public Object correlate(InvocationContext ctx) throws Exception {
        MDC.put("method", ctx.getMethod().getName());
        try {
            return ctx.proceed();
        } finally {
            MDC.remove("method");
        }
    }
}
```

### WildFly Logging Configuration
```bash
# CLI — set log level for a package
./bin/jboss-cli.sh --connect
/subsystem=logging/logger=com.example:add(level=DEBUG)
/subsystem=logging/logger=org.hibernate.SQL:add(level=DEBUG)

# Set root handler level
/subsystem=logging/root-logger=ROOT:write-attribute(name=level, value=INFO)

# View current log handlers
/subsystem=logging:read-resource(recursive=true)
```

Or in `standalone.xml`:
```xml
<subsystem xmlns="urn:jboss:domain:logging:8.0">
  <console-handler name="CONSOLE">
    <level name="DEBUG"/>
    <formatter><named-formatter name="COLOR-PATTERN"/></formatter>
  </console-handler>
  <logger category="com.example">
    <level name="DEBUG"/>
  </logger>
  <root-logger>
    <level name="INFO"/>
    <handlers><handler name="CONSOLE"/><handler name="FILE"/></handlers>
  </root-logger>
</subsystem>
```

---

## Chapter 39: Custom Log4j Appender

A custom appender sends log events to a non-standard destination (database, message queue, external API, custom file format).

### Log4j2 Custom Appender
```java
import org.apache.logging.log4j.core.*;
import org.apache.logging.log4j.core.appender.AbstractAppender;
import org.apache.logging.log4j.core.config.plugins.*;
import org.apache.logging.log4j.core.layout.PatternLayout;

@Plugin(name="DatabaseAppender", category=Core.CATEGORY_NAME,
        elementType=Appender.ELEMENT_TYPE, printObject=true)
public class DatabaseAppender extends AbstractAppender {

    private final DataSource dataSource;

    protected DatabaseAppender(String name, Filter filter,
                                Layout<?> layout, DataSource ds) {
        super(name, filter, layout, true, Property.EMPTY_ARRAY);
        this.dataSource = ds;
    }

    @PluginFactory
    public static DatabaseAppender createAppender(
            @PluginAttribute("name") String name,
            @PluginElement("Filter") Filter filter,
            @PluginElement("Layout") Layout<? extends Serializable> layout,
            @PluginAttribute("dataSource") String dsJndi) {
        try {
            DataSource ds = (DataSource) new InitialContext().lookup(dsJndi);
            return new DatabaseAppender(
                name, filter,
                layout != null ? layout : PatternLayout.createDefaultLayout(),
                ds);
        } catch (NamingException e) {
            LOGGER.error("Cannot find DataSource: " + dsJndi);
            return null;
        }
    }

    @Override
    public void append(LogEvent event) {
        String message = new String(getLayout().toByteArray(event));
        try (Connection conn = dataSource.getConnection();
             PreparedStatement ps = conn.prepareStatement(
                 "INSERT INTO app_log(ts, level, logger, message) " +
                 "VALUES(?, ?, ?, ?)")) {
            ps.setTimestamp(1, new Timestamp(event.getTimeMillis()));
            ps.setString(2, event.getLevel().name());
            ps.setString(3, event.getLoggerName());
            ps.setString(4, message);
            ps.executeUpdate();
        } catch (Exception e) {
            error("Failed to log to database", event, e);
        }
    }
}
```

### Register and Configure Custom Appender
```xml
<!-- log4j2.xml -->
<Configuration packages="com.example.logging">
  <Appenders>
    <DatabaseAppender name="DB" dataSource="java:comp/DefaultDataSource">
      <PatternLayout pattern="%m"/>
    </DatabaseAppender>
    <Console name="Console" target="SYSTEM_OUT">
      <PatternLayout pattern="%d{HH:mm:ss} %-5p %c{1}:%L - %m%n"/>
    </Console>
  </Appenders>
  <Loggers>
    <Root level="INFO">
      <AppenderRef ref="Console"/>
      <AppenderRef ref="DB" level="WARN"/>  <!-- only WARN+ to DB -->
    </Root>
  </Loggers>
</Configuration>
```

### Custom Appender for JMS (async log shipping)
```java
@Plugin(name="JmsLogAppender", category=Core.CATEGORY_NAME,
        elementType=Appender.ELEMENT_TYPE)
public class JmsLogAppender extends AbstractAppender {

    @Inject private ConnectionFactory jmsFactory;
    @Inject private Queue logQueue;

    @Override
    public void append(LogEvent event) {
        try (JMSContext ctx = jmsFactory.createContext()) {
            JMSProducer producer = ctx.createProducer();
            ObjectMessage msg = ctx.createObjectMessage();
            msg.setObject(new LogRecord(event));
            producer.send(logQueue, msg);
        } catch (JMSException e) {
            error("Failed to send log to JMS", event, e);
        }
    }
}
```

---

## Monitoring Dashboards Integration

### Prometheus + Grafana (via MicroProfile Metrics)
```yaml
# prometheus.yml scrape config
scrape_configs:
  - job_name: 'jakarta-ee-app'
    metrics_path: /myapp/metrics
    scrape_interval: 15s
    static_configs:
      - targets: ['localhost:8080']
```

Grafana: create dashboards from MicroProfile Metrics counters/timers/gauges.

### Elastic Stack (ELK) via JSON logging
1. App outputs JSON logs to stdout/file
2. Filebeat ships logs to Elasticsearch
3. Kibana visualizes

```yaml
# filebeat.yml
filebeat.inputs:
  - type: log
    paths: ["/opt/wildfly/standalone/log/server.log"]
    json.keys_under_root: true
    json.add_error_key: true

output.elasticsearch:
  hosts: ["http://elasticsearch:9200"]
  index: "jakarta-ee-logs-%{+yyyy.MM.dd}"
```

---

## Common Monitoring/Logging Issues

| Problem | Cause | Fix |
|---------|-------|-----|
| MBean not visible in JConsole | Not registered on platform MBeanServer | Use `ManagementFactory.getPlatformMBeanServer()` |
| JMX connection refused | WildFly management port not bound | Check `management-http` listener in standalone.xml |
| Log level not changing at runtime | Using hardcoded JUL level | Use WildFly CLI or Log4j2 JMX to change at runtime |
| MDC values lost between threads | ManagedExecutorService spawns new thread | Use `ContextService` to propagate MDC or set MDC in runnable |
| Custom appender not loaded | Package not in `packages=` attribute | Add `packages="com.example.logging"` to `<Configuration>` |
| DB appender causing log loss | DB down, write blocks logging thread | Make DB writes async; use `AsyncAppender` wrapper |
| JSON logs not parsed by ELK | Timestamp format wrong | Use ISO-8601 in JsonTemplateLayout |
