# Spring Boot 2.3 — Auto-Configuration

## How It Works

Spring Boot auto-configuration inspects the classpath, existing beans, and properties to automatically configure Spring beans. It is triggered by `@EnableAutoConfiguration` (included in `@SpringBootApplication`).

Auto-configuration candidates are registered in `META-INF/spring.factories` under the key `org.springframework.boot.autoconfigure.EnableAutoConfiguration`. Spring Boot scans all jars on the classpath for this file.

---

## spring.factories

```
# META-INF/spring.factories  (inside any jar)
org.springframework.boot.autoconfigure.EnableAutoConfiguration=\
  com.example.autoconfigure.FooAutoConfiguration,\
  com.example.autoconfigure.BarAutoConfiguration
```

Spring Boot loads these classes lazily at startup. Each auto-configuration class is a `@Configuration` class with conditional annotations that gate whether it runs.

---

## @Conditional Annotations

| Annotation | Condition |
|-----------|-----------|
| `@ConditionalOnClass(Foo.class)` | Applies if `Foo` is on the classpath |
| `@ConditionalOnMissingClass("com.Foo")` | Applies if `Foo` is NOT on classpath |
| `@ConditionalOnBean(Foo.class)` | Applies if a `Foo` bean exists |
| `@ConditionalOnMissingBean` | Applies if the declared bean type is NOT already defined |
| `@ConditionalOnProperty(name="x", havingValue="true")` | Applies if property matches |
| `@ConditionalOnProperty(name="x", matchIfMissing=true)` | Applies if property absent or matches |
| `@ConditionalOnResource(resources="classpath:foo.xml")` | Applies if resource exists |
| `@ConditionalOnWebApplication` | Applies in any web application |
| `@ConditionalOnWebApplication(type=SERVLET)` | Applies in servlet web app |
| `@ConditionalOnWebApplication(type=REACTIVE)` | Applies in reactive web app |
| `@ConditionalOnExpression("${feature.on:false}")` | SpEL expression |

---

## Disabling Auto-Configuration

```java
// Exclude by class reference
@SpringBootApplication(exclude = {DataSourceAutoConfiguration.class})
public class MyApp {}

// Exclude by name (when class not on classpath)
@SpringBootApplication(excludeName = {
    "org.springframework.boot.autoconfigure.jdbc.DataSourceAutoConfiguration"
})
public class MyApp {}
```

Via properties:
```properties
spring.autoconfigure.exclude=\
  org.springframework.boot.autoconfigure.jdbc.DataSourceAutoConfiguration,\
  org.springframework.boot.autoconfigure.data.redis.RedisAutoConfiguration
```

---

## Diagnosing What Was Auto-Configured

```bash
# See conditions evaluation report in console
java -jar myapp.jar --debug

# Or via Actuator (expose first)
management.endpoints.web.exposure.include=conditions
GET /actuator/conditions
```

---

## Custom Auto-Configuration

### 1. Define the auto-configuration class

```java
package com.example.autoconfigure;

import org.springframework.boot.autoconfigure.condition.ConditionalOnClass;
import org.springframework.boot.autoconfigure.condition.ConditionalOnMissingBean;
import org.springframework.boot.context.properties.EnableConfigurationProperties;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration(proxyBeanMethods = false)
@ConditionalOnClass(AcmeClient.class)          // only if AcmeClient jar is present
@EnableConfigurationProperties(AcmeProperties.class)
public class AcmeAutoConfiguration {

    @Bean
    @ConditionalOnMissingBean                  // back off if user defines their own
    public AcmeClient acmeClient(AcmeProperties properties) {
        return new AcmeClient(properties.getUrl(), properties.getApiKey());
    }
}
```

### 2. Define the properties class

```java
package com.example.autoconfigure;

import org.springframework.boot.context.properties.ConfigurationProperties;

@ConfigurationProperties(prefix = "acme")
public class AcmeProperties {

    private String url = "https://api.acme.com";
    private String apiKey;

    public String getUrl() { return url; }
    public void setUrl(String url) { this.url = url; }
    public String getApiKey() { return apiKey; }
    public void setApiKey(String apiKey) { this.apiKey = apiKey; }
}
```

### 3. Register in META-INF/spring.factories

```
org.springframework.boot.autoconfigure.EnableAutoConfiguration=\
  com.example.autoconfigure.AcmeAutoConfiguration
```

---

## Ordering Auto-Configuration

```java
// Run after DataSource is configured
@Configuration(proxyBeanMethods = false)
@AutoConfigureAfter(DataSourceAutoConfiguration.class)
public class MyJdbcAutoConfiguration { }

// Run before something else
@Configuration(proxyBeanMethods = false)
@AutoConfigureBefore(DataSourceAutoConfiguration.class)
public class EarlyAutoConfiguration { }

// Explicit ordering
@Configuration(proxyBeanMethods = false)
@AutoConfigureOrder(Ordered.HIGHEST_PRECEDENCE)
public class FirstAutoConfiguration { }
```

---

## @ConfigurationProperties (Auto-Configuration Pattern)

```java
@ConfigurationProperties(prefix = "app.database")
@Validated
public class DatabaseProperties {

    @NotEmpty
    private String url;

    @NotNull
    @Min(1)
    @Max(65535)
    private Integer port;

    private String username = "root";
    private String password;

    // standard getters and setters
    public String getUrl() { return url; }
    public void setUrl(String url) { this.url = url; }
    // ...
}
```

Registering with `@EnableConfigurationProperties`:

```java
@Configuration(proxyBeanMethods = false)
@EnableConfigurationProperties(DatabaseProperties.class)
public class DatabaseAutoConfiguration {

    @Bean
    @ConditionalOnMissingBean
    public DataSource dataSource(DatabaseProperties props) {
        // create DataSource from props
    }
}
```

Or via `@ConfigurationPropertiesScan` on main class (scans entire package tree):

```java
@SpringBootApplication
@ConfigurationPropertiesScan({"com.example.app", "com.example.shared"})
public class MyApplication {}
```

---

## Constructor Binding (Immutable ConfigurationProperties)

```java
package com.example;

import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.boot.context.properties.ConstructorBinding;
import org.springframework.boot.context.properties.bind.DefaultValue;

@ConstructorBinding
@ConfigurationProperties("acme")
public class AcmeProperties {

    private final boolean enabled;
    private final String host;
    private final int port;
    private final List<String> roles;

    public AcmeProperties(boolean enabled,
                          String host,
                          @DefaultValue("8080") int port,
                          @DefaultValue("USER") List<String> roles) {
        this.enabled = enabled;
        this.host = host;
        this.port = port;
        this.roles = roles;
    }

    // only getters — no setters (immutable)
    public boolean isEnabled() { return enabled; }
    public String getHost() { return host; }
    public int getPort() { return port; }
    public List<String> getRoles() { return roles; }
}
```

`@ConstructorBinding` requires enabling via `@EnableConfigurationProperties` or `@ConfigurationPropertiesScan`.

---

## Testing Auto-Configuration

Use `ApplicationContextRunner` (no Spring context startup overhead):

```java
import org.springframework.boot.test.context.runner.ApplicationContextRunner;
import org.springframework.boot.autoconfigure.AutoConfigurations;

class AcmeAutoConfigurationTest {

    private final ApplicationContextRunner contextRunner =
        new ApplicationContextRunner()
            .withConfiguration(AutoConfigurations.of(AcmeAutoConfiguration.class));

    @Test
    void withRequiredClass_createsClient() {
        contextRunner
            .withPropertyValues("acme.url=https://test.acme.com",
                                "acme.api-key=secret")
            .run(context -> {
                assertThat(context).hasSingleBean(AcmeClient.class);
                AcmeClient client = context.getBean(AcmeClient.class);
                assertThat(client.getUrl()).isEqualTo("https://test.acme.com");
            });
    }

    @Test
    void withUserDefinedBean_backsOff() {
        contextRunner
            .withUserConfiguration(UserDefinedAcmeClientConfig.class)
            .run(context -> {
                assertThat(context).hasSingleBean(AcmeClient.class);
                // the user's bean, not the auto-configured one
            });
    }
}
```

---

## Custom Starter Structure

```
acme-spring-boot-starter/
├── acme-spring-boot-autoconfigure/   ← auto-config module
│   └── src/main/
│       ├── java/com/acme/autoconfigure/
│       │   ├── AcmeAutoConfiguration.java
│       │   └── AcmeProperties.java
│       └── resources/META-INF/
│           └── spring.factories
└── acme-spring-boot-starter/         ← starter module (just POM)
    └── pom.xml  (depends on autoconfigure + acme-core)
```

Naming convention: `{name}-spring-boot-starter` for third-party starters (never `spring-boot-starter-{name}`, which is reserved for official starters).
