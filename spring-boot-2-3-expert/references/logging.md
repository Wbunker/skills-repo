# Spring Boot 2.3 — Logging

## Default Logging

Spring Boot uses **Logback** by default (via `spring-boot-starter-logging`, bundled in all starters). Log4j2 is also supported.

Default log format:
```
2021-03-15 10:22:01.456  INFO 12345 --- [           main] com.example.MyApplication : Starting MyApplication v1.0.0
                                                  [thread name]  [logger name]                  [message]
```

Default console output: `INFO` level and above for the root logger.

---

## Configuring Log Levels via application.properties

```properties
# Root logger level
logging.level.root=WARN

# Package-specific levels
logging.level.com.example=DEBUG
logging.level.com.example.service=TRACE
logging.level.org.springframework=WARN
logging.level.org.springframework.web=INFO
logging.level.org.springframework.security=DEBUG
logging.level.org.hibernate.SQL=DEBUG
logging.level.org.hibernate.type.descriptor.sql.BasicBinder=TRACE  # log SQL params
logging.level.org.flywaydb=INFO
logging.level.org.apache.kafka=WARN
```

Level values: `TRACE`, `DEBUG`, `INFO`, `WARN`, `ERROR`, `FATAL`, `OFF`

Via YAML:
```yaml
logging:
  level:
    root: warn
    com.example: debug
    org.springframework.web: info
```

---

## File Output

```properties
logging.file.name=logs/application.log
# OR: logging.file.path=/var/log/myapp   (writes spring.log to this dir)

logging.file.max-size=10MB
logging.file.max-history=30
logging.file.total-size-cap=1GB
logging.file.clean-history-on-start=false
```

**Note:** `logging.file.name` and `logging.file.path` are mutually exclusive; `name` takes precedence.

---

## Log Groups

Group multiple loggers and configure them together:

```properties
# Define a group
logging.group.myservice=com.example.service,com.example.repository

# Set level for the group
logging.level.myservice=DEBUG

# Built-in groups (pre-defined by Spring Boot):
# logging.level.web    → Spring MVC + Tomcat request logs (DEBUG shows full request)
# logging.level.sql    → Spring JDBC + Hibernate SQL
logging.level.web=DEBUG
logging.level.sql=DEBUG
```

Built-in groups:
- `web`: `org.springframework.core.codec`, `org.springframework.http`, `org.springframework.web`, `org.springframework.boot.actuate.endpoint.web`, `org.springframework.boot.web.servlet.ServletContextInitializerBeans`
- `sql`: `org.springframework.jdbc.core`, `org.hibernate.SQL`, `org.jooq.tools.LoggerListener`

---

## Log Pattern Customization

```properties
# Console pattern
logging.pattern.console=%d{yyyy-MM-dd HH:mm:ss.SSS} [%thread] %-5level %logger{36} - %msg%n

# File pattern
logging.pattern.file=%d{yyyy-MM-dd HH:mm:ss.SSS} [%thread] %-5level %logger{36} - %msg%n

# Date format only
logging.pattern.dateformat=yyyy-MM-dd HH:mm:ss.SSS

# Log level
logging.pattern.level=%5p
```

Pattern symbols:
| Symbol | Meaning |
|--------|---------|
| `%d{pattern}` | Date/time |
| `%thread` | Thread name |
| `%-5level` | Level, left-padded to 5 chars |
| `%level` | Level |
| `%logger{length}` | Logger name, optionally shortened |
| `%msg` | Log message |
| `%n` | Newline |
| `%X{key}` | MDC value |
| `%clr(text){color}` | Colored text (ANSI) |

---

## ANSI Color Output

```properties
spring.output.ansi.enabled=always    # always | detect (default) | never
```

In patterns:
```properties
logging.pattern.console=%clr(%d{yyyy-MM-dd HH:mm:ss.SSS}){faint} %clr(%5p) %clr(${PID:- }){magenta} %clr(---){faint} %clr([%15.15t]){faint} %clr(%-40.40logger{39}){cyan} %clr(:){faint} %m%n%wEx
```

---

## Custom Logback Configuration

Use `logback-spring.xml` (preferred, supports Spring extensions) or `logback.xml`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<configuration>

    <!-- Import Spring Boot defaults as base -->
    <include resource="org/springframework/boot/logging/logback/defaults.xml"/>

    <property name="LOG_FILE" value="${LOG_FILE:-${LOG_PATH:-${LOG_TEMP:-${java.io.tmpdir:-/tmp}}/}spring.log}"/>

    <!-- Console appender -->
    <appender name="CONSOLE" class="ch.qos.logback.core.ConsoleAppender">
        <encoder>
            <pattern>%clr(%d{yyyy-MM-dd HH:mm:ss.SSS}){faint} %clr(%-5level) %clr(${PID:- }){magenta} [%15.15t] %clr(%-40.40logger{39}){cyan} : %m%n</pattern>
            <charset>UTF-8</charset>
        </encoder>
    </appender>

    <!-- Rolling file appender -->
    <appender name="FILE" class="ch.qos.logback.core.rolling.RollingFileAppender">
        <file>${LOG_FILE}</file>
        <encoder>
            <pattern>%d{yyyy-MM-dd HH:mm:ss.SSS} [%thread] %-5level %logger{36} - %msg%n</pattern>
            <charset>UTF-8</charset>
        </encoder>
        <rollingPolicy class="ch.qos.logback.core.rolling.SizeAndTimeBasedRollingPolicy">
            <fileNamePattern>${LOG_FILE}.%d{yyyy-MM-dd}.%i.gz</fileNamePattern>
            <maxFileSize>10MB</maxFileSize>
            <maxHistory>30</maxHistory>
            <totalSizeCap>1GB</totalSizeCap>
        </rollingPolicy>
    </appender>

    <!-- Async appender (non-blocking, buffer 256) -->
    <appender name="ASYNC_FILE" class="ch.qos.logback.classic.AsyncAppender">
        <appender-ref ref="FILE"/>
        <queueSize>256</queueSize>
        <discardingThreshold>0</discardingThreshold>
        <neverBlock>false</neverBlock>
    </appender>

    <!-- Per-package loggers -->
    <logger name="com.example" level="DEBUG"/>
    <logger name="org.springframework.web" level="WARN"/>
    <logger name="org.hibernate.SQL" level="DEBUG"/>
    <logger name="org.hibernate.type" level="TRACE"/>

    <!-- Root logger -->
    <root level="INFO">
        <appender-ref ref="CONSOLE"/>
        <appender-ref ref="ASYNC_FILE"/>
    </root>

</configuration>
```

---

## Profile-specific Logback Configuration

```xml
<!-- logback-spring.xml (use logback-spring.xml, not logback.xml, for Spring extensions) -->
<configuration>

    <springProfile name="dev">
        <root level="DEBUG">
            <appender-ref ref="CONSOLE"/>
        </root>
    </springProfile>

    <springProfile name="prod">
        <root level="INFO">
            <appender-ref ref="FILE"/>
        </root>
    </springProfile>

    <springProfile name="!test">
        <!-- applies when 'test' profile is NOT active -->
        <logger name="com.example" level="INFO"/>
    </springProfile>

</configuration>
```

---

## Environment Properties in Logback

```xml
<!-- logback-spring.xml -->
<configuration>

    <!-- Read Spring property into Logback variable -->
    <springProperty scope="context" name="app.name"
                    source="spring.application.name" defaultValue="unknown"/>

    <springProperty scope="context" name="log.level"
                    source="logging.level.root" defaultValue="INFO"/>

    <appender name="CONSOLE" class="ch.qos.logback.core.ConsoleAppender">
        <encoder>
            <pattern>[${app.name}] %d{HH:mm:ss} %-5level %logger{36} - %msg%n</pattern>
        </encoder>
    </appender>

    <root level="${log.level}">
        <appender-ref ref="CONSOLE"/>
    </root>

</configuration>
```

---

## Log4j2

Replace Logback with Log4j2:

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-web</artifactId>
    <exclusions>
        <exclusion>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-logging</artifactId>
        </exclusion>
    </exclusions>
</dependency>
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-log4j2</artifactId>
</dependency>
```

---

## MDC (Mapped Diagnostic Context)

Add per-request/per-thread context to all log messages:

```java
@Component
public class RequestLoggingFilter extends OncePerRequestFilter {

    @Override
    protected void doFilterInternal(HttpServletRequest request,
                                    HttpServletResponse response,
                                    FilterChain chain) throws ServletException, IOException {
        String requestId = request.getHeader("X-Request-Id");
        if (requestId == null) requestId = UUID.randomUUID().toString();

        MDC.put("requestId", requestId);
        MDC.put("userId", getCurrentUserId());
        try {
            chain.doFilter(request, response);
        } finally {
            MDC.clear();
        }
    }
}

// Log pattern to include MDC:
// logging.pattern.console=%d{HH:mm:ss} [%X{requestId}] [%X{userId}] %-5level %logger - %msg%n
```

---

## Structured / JSON Logging

For log aggregation systems (ELK, Splunk, etc.), use JSON format via `logstash-logback-encoder`:

```xml
<dependency>
    <groupId>net.logstash.logback</groupId>
    <artifactId>logstash-logback-encoder</artifactId>
    <version>7.2</version>
</dependency>
```

```xml
<!-- logback-spring.xml -->
<appender name="JSON" class="ch.qos.logback.core.ConsoleAppender">
    <encoder class="net.logstash.logback.encoder.LogstashEncoder">
        <customFields>{"app":"myapp","env":"${SPRING_PROFILES_ACTIVE:-default}"}</customFields>
    </encoder>
</appender>

<springProfile name="prod">
    <root level="INFO">
        <appender-ref ref="JSON"/>
    </root>
</springProfile>
```

JSON output:
```json
{
  "@timestamp": "2021-03-15T10:22:01.456+00:00",
  "@version": "1",
  "message": "User created: 42",
  "logger_name": "com.example.service.UserService",
  "thread_name": "http-nio-8080-exec-1",
  "level": "INFO",
  "level_value": 20000,
  "app": "myapp",
  "env": "prod",
  "requestId": "abc-123",
  "userId": "user-99"
}
```

---

## Runtime Log Level Changes

Via Actuator (in-process, no restart):
```bash
# Check current level
GET /actuator/loggers/com.example.service.UserService

# Set to DEBUG
POST /actuator/loggers/com.example.service.UserService
Content-Type: application/json
{"configuredLevel": "DEBUG"}

# Reset to inherited
POST /actuator/loggers/com.example.service.UserService
{"configuredLevel": null}
```

---

## Startup Logging

```properties
# Disable startup info (Spring Boot banner + startup time)
spring.main.log-startup-info=false
```

Banner customization:
```properties
spring.banner.location=classpath:/banner.txt
spring.main.banner-mode=off    # off | console | log
```
