# Spring Boot 2.3 — Configuration & Properties

## Property Sources (Priority Order, High to Low)

1. Command line arguments (`--server.port=9090`)
2. `SPRING_APPLICATION_JSON` (inline JSON in env var or system property)
3. `ServletConfig` init params
4. `ServletContext` init params
5. JNDI (`java:comp/env`)
6. Java System properties (`System.getProperties()`)
7. OS environment variables
8. `RandomValuePropertySource` (`random.*`)
9. Profile-specific properties **outside** jar (`application-{profile}.properties`)
10. Profile-specific properties **inside** jar
11. Application properties **outside** jar (`./config/`, `./`, etc.)
12. Application properties **inside** jar (classpath)
13. `@PropertySource` annotations
14. Default properties (`SpringApplication.setDefaultProperties`)

## Default Config File Search Order

```
1. file:./config/
2. file:./config/*/
3. file:./
4. classpath:/config/
5. classpath:/
```

---

## application.properties

```properties
# Server
server.port=8080
server.servlet.context-path=/api

# Application name
spring.application.name=my-app

# Profiles
spring.profiles.active=dev,mysql

# Property placeholders
app.name=MyApp
app.description=${app.name} is a Spring Boot application
```

## application.yml

```yaml
server:
  port: 8080
  servlet:
    context-path: /api

spring:
  application:
    name: my-app
  profiles:
    active: dev,mysql

app:
  name: MyApp
  description: "${app.name} is a Spring Boot application"
```

YAML lists:
```yaml
my:
  servers:
    - dev.example.com
    - another.example.com
```
Equivalent to: `my.servers[0]=dev.example.com`, `my.servers[1]=another.example.com`

---

## @Value

```java
@Component
public class AppConfig {

    @Value("${app.name}")
    private String name;

    @Value("${app.timeout:30}")   // with default
    private int timeout;

    @Value("${app.servers}")      // comma-separated → List<String>
    private List<String> servers;

    @Value("#{systemProperties['user.home']}")   // SpEL
    private String userHome;
}
```

**Limitation:** `@Value` does not support relaxed binding. Use exact property name.

---

## @ConfigurationProperties

Preferred for groups of related properties. Supports relaxed binding, type conversion, and JSR-303 validation.

### JavaBean (setter) binding

```java
import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.validation.annotation.Validated;
import javax.validation.constraints.*;
import java.time.Duration;
import java.util.List;
import java.util.Map;

@ConfigurationProperties(prefix = "acme")
@Validated
public class AcmeProperties {

    private boolean enabled = true;

    @NotEmpty
    private String remoteHost;

    @Min(1) @Max(65535)
    private int port = 8080;

    private Duration timeout = Duration.ofSeconds(30);

    private List<String> roles = List.of("USER");

    private Map<String, String> metadata = new HashMap<>();

    private final Security security = new Security();

    // all getters and setters required for JavaBean binding
    public boolean isEnabled() { return enabled; }
    public void setEnabled(boolean enabled) { this.enabled = enabled; }
    public String getRemoteHost() { return remoteHost; }
    public void setRemoteHost(String remoteHost) { this.remoteHost = remoteHost; }
    public int getPort() { return port; }
    public void setPort(int port) { this.port = port; }
    public Duration getTimeout() { return timeout; }
    public void setTimeout(Duration timeout) { this.timeout = timeout; }
    public List<String> getRoles() { return roles; }
    public void setRoles(List<String> roles) { this.roles = roles; }
    public Map<String, String> getMetadata() { return metadata; }
    public void setMetadata(Map<String, String> metadata) { this.metadata = metadata; }
    public Security getSecurity() { return security; }

    public static class Security {
        private String username;
        private String password;
        public String getUsername() { return username; }
        public void setUsername(String username) { this.username = username; }
        public String getPassword() { return password; }
        public void setPassword(String password) { this.password = password; }
    }
}
```

```properties
acme.enabled=true
acme.remote-host=server.example.com
acme.port=9000
acme.timeout=60s
acme.roles=USER,ADMIN
acme.metadata.key1=value1
acme.security.username=admin
acme.security.password=secret
```

### Constructor (immutable) binding

```java
import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.boot.context.properties.ConstructorBinding;
import org.springframework.boot.context.properties.bind.DefaultValue;

@ConstructorBinding
@ConfigurationProperties(prefix = "mail")
public class MailProperties {

    private final String host;
    private final int port;
    private final String from;

    public MailProperties(String host,
                          @DefaultValue("25") int port,
                          @DefaultValue("noreply@example.com") String from) {
        this.host = host;
        this.port = port;
        this.from = from;
    }

    public String getHost() { return host; }
    public int getPort() { return port; }
    public String getFrom() { return from; }
}
```

### Enabling @ConfigurationProperties

Option A — `@EnableConfigurationProperties` on a config class:
```java
@Configuration
@EnableConfigurationProperties({AcmeProperties.class, MailProperties.class})
public class AppConfig {}
```

Option B — `@ConfigurationPropertiesScan` on main class (scans entire package tree):
```java
@SpringBootApplication
@ConfigurationPropertiesScan
public class MyApplication {}
```

### Injecting in services

```java
@Service
public class AcmeService {
    private final AcmeProperties props;

    public AcmeService(AcmeProperties props) {
        this.props = props;
    }

    public void connect() {
        String url = props.getRemoteHost() + ":" + props.getPort();
        // ...
    }
}
```

---

## Relaxed Binding

For `@ConfigurationProperties(prefix = "acme.my-project.person")` with field `firstName`:

| Format | Example |
|--------|---------|
| Kebab-case (recommended for .properties/.yml) | `acme.my-project.person.first-name` |
| Camel-case | `acme.myProject.person.firstName` |
| Underscore notation | `acme.my_project.person.first_name` |
| Uppercase env var | `ACME_MYPROJECT_PERSON_FIRSTNAME` |

**Note:** `@Value` does NOT support relaxed binding — use exact key.

### Binding Maps with special key characters

```yaml
acme:
  map:
    "[/key1]": value1     # slash preserved because in brackets
    "[/key2]": value2
    "/key3": value3       # slash stripped — becomes "key3"
```

---

## Profiles

### Profile-specific property files

```
application-dev.properties
application-prod.properties
application-dev.yml
application-prod.yml
```

Profile-specific files always override non-profile files.

### Activating profiles

```properties
# application.properties
spring.profiles.active=dev,mysql
```

```bash
java -jar app.jar --spring.profiles.active=prod
export SPRING_PROFILES_ACTIVE=prod
```

```java
// Programmatically
SpringApplication app = new SpringApplication(MyApp.class);
app.setAdditionalProfiles("local");
app.run(args);
```

### @Profile on beans

```java
@Configuration
@Profile("dev")
public class DevConfig {
    @Bean
    public DataSource devDataSource() {
        return new EmbeddedDatabaseBuilder()
            .setType(EmbeddedDatabaseType.H2).build();
    }
}

@Service
@Profile("!test")   // active when 'test' is NOT active
public class RealPaymentService implements PaymentService {}

@Service
@Profile("test")
public class MockPaymentService implements PaymentService {}
```

### Multi-document YAML with profile expressions

```yaml
server:
  address: 192.168.1.100
---
spring:
  profiles: development
server:
  address: 127.0.0.1
---
spring:
  profiles: production & eu-central
server:
  address: 10.0.1.5
```

---

## Type Conversion

### Duration

```properties
app.timeout=30s       # 30 seconds
app.timeout=5m        # 5 minutes
app.timeout=PT30S     # ISO-8601
app.timeout=30        # unit depends on @DurationUnit
```

Units: `ns`, `us`, `ms`, `s`, `m`, `h`, `d`

```java
@ConfigurationProperties("app")
public class AppProps {
    @DurationUnit(ChronoUnit.SECONDS)
    private Duration timeout = Duration.ofSeconds(30);
    // getter/setter
}
```

### DataSize

```properties
app.buffer-size=10MB
app.threshold=256B
```

Units: `B`, `KB`, `MB`, `GB`, `TB`

```java
@DataSizeUnit(DataUnit.MEGABYTES)
private DataSize bufferSize = DataSize.ofMegabytes(2);
```

---

## Random Values

```properties
my.secret=${random.value}
my.number=${random.int}
my.bignumber=${random.long}
my.uuid=${random.uuid}
my.number-less-than-ten=${random.int(10)}
my.number-in-range=${random.int[1024,65536]}
```

---

## SPRING_APPLICATION_JSON (Inline JSON)

```bash
# Unix
SPRING_APPLICATION_JSON='{"acme":{"name":"test"}}' java -jar app.jar

# System property
java -Dspring.application.json='{"acme":{"name":"test"}}' -jar app.jar

# Command line arg
java -jar app.jar --spring.application.json='{"acme":{"name":"test"}}'
```

---

## Externalized Config Locations

```bash
# Override default locations entirely
java -jar app.jar \
  --spring.config.location=classpath:/custom.properties,file:./override.properties

# Add locations on top of defaults
java -jar app.jar \
  --spring.config.additional-location=file:/etc/myapp/config.properties
```

---

## @ConfigurationProperties vs @Value

| Feature | @ConfigurationProperties | @Value |
|---------|--------------------------|--------|
| Binding style | Hierarchical / bulk | Single property |
| Relaxed binding | Yes | No (exact key) |
| Type conversion | Rich (Duration, DataSize, etc.) | Basic |
| Validation (JSR-303) | Yes (`@Validated`) | No |
| IDE metadata support | Yes (generates metadata) | No |
| Constructor binding | Yes (`@ConstructorBinding`) | No |
| Best for | Configuration classes | Simple one-off injection |
