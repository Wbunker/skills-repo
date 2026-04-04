---
name: configuration
description: Spring Cloud Config Server setup, Git backend, environment profiles, property encryption, @RefreshScope, and Spring Cloud Bus broadcast. Chapter 3 of Spring Microservices in Action.
type: reference
---

# Configuration Management: Spring Cloud Config Server

## Why Centralized Configuration?

Microservices multiply the number of configuration surfaces. Hardcoding or bundling properties into each service image creates:
- Drift between environments
- Secrets in source control
- Restart required to change a value
- No audit trail for configuration changes

Spring Cloud Config Server solves all four.

---

## Architecture

```
┌─────────────┐        ┌───────────────────────┐       ┌──────────────┐
│  Config      │        │  Spring Cloud Config  │       │   Git Repo   │
│  Client      │◄──────►│  Server               │◄─────►│  (backend)   │
│  (service)   │  REST  │  Port 8888 (default)  │       │              │
└─────────────┘        └───────────────────────┘       └──────────────┘
```

Clients fetch config on startup via:
`http://config-server:8888/{application}/{profile}/{label}`

---

## Config Server Setup

### Dependencies
```xml
<dependency>
    <groupId>org.springframework.cloud</groupId>
    <artifactId>spring-cloud-config-server</artifactId>
</dependency>
```

### Server Application

```java
@SpringBootApplication
@EnableConfigServer
public class ConfigServerApplication {
    public static void main(String[] args) {
        SpringApplication.run(ConfigServerApplication.class, args);
    }
}
```

### `application.yml` for Server
```yaml
server:
  port: 8888
spring:
  cloud:
    config:
      server:
        git:
          uri: https://github.com/myorg/config-repo
          search-paths: '{application}'    # Subdirectory per service
          default-label: main             # Branch
          # For private repos:
          username: ${GIT_USER}
          password: ${GIT_TOKEN}
```

### Git Repository Layout
```
config-repo/
├── application.yml              # Shared defaults (all services)
├── license-service/
│   ├── license-service.yml      # license-service defaults
│   ├── license-service-dev.yml  # dev profile overrides
│   └── license-service-prod.yml # prod profile overrides
└── organization-service/
    └── organization-service.yml
```

---

## Config Client Setup

### Dependencies
```xml
<dependency>
    <groupId>org.springframework.cloud</groupId>
    <artifactId>spring-cloud-starter-config</artifactId>
</dependency>
```

### `bootstrap.yml` (loads before application context)
```yaml
spring:
  application:
    name: license-service          # Maps to config-repo subdirectory
  profiles:
    active: dev
  cloud:
    config:
      uri: http://config-server:8888
      fail-fast: true              # Crash on startup if config unavailable
      retry:
        max-attempts: 6
        initial-interval: 1000
```

> **Note (Spring Boot 2.4+):** `bootstrap.yml` is deprecated. Use `spring.config.import=configserver:` in `application.yml` with the `spring-cloud-starter-bootstrap` dependency if needed.

---

## Property Resolution Order
1. Command-line arguments (`--server.port=9090`)
2. OS environment variables (`SERVER_PORT=9090`)
3. Config Server (remote properties)
4. `application-{profile}.yml` in classpath
5. `application.yml` in classpath

Higher precedence overrides lower. Use this to allow environment variables to override Config Server values in production.

---

## Encrypting Secrets

Never store passwords or API keys in plaintext in Git.

### Setup Symmetric Encryption
```yaml
# Config Server application.yml
encrypt:
  key: ${ENCRYPT_KEY}    # Set via environment variable
```

### Encrypt a Value
```bash
curl http://config-server:8888/encrypt -d 'mysecretpassword'
# Returns: AQA6... (cipher text)
```

Store in Git as:
```yaml
spring:
  datasource:
    password: '{cipher}AQA6...'
```

Config Server decrypts before returning to client. Client never sees the cipher text.

### Asymmetric Encryption (Production)
Use a Java KeyStore for RSA key pairs — more secure than symmetric.
```yaml
encrypt:
  keyStore:
    location: classpath:/server.jks
    password: ${KEYSTORE_PASS}
    alias: mykey
```

---

## Refreshing Configuration at Runtime

### Manual Refresh
1. Change property in Git and push
2. POST to the service's actuator endpoint:
   ```bash
   curl -X POST http://service:8080/actuator/refresh
   ```
3. Only beans annotated with `@RefreshScope` are re-initialized

```java
@RefreshScope
@RestController
public class LicenseServiceController {
    @Value("${example.property}")
    private String exampleProperty;
    // ...
}
```

### Broadcast Refresh with Spring Cloud Bus

Avoids calling `/refresh` on each instance individually.

**Dependencies (add to each service):**
```xml
<dependency>
    <groupId>org.springframework.cloud</groupId>
    <artifactId>spring-cloud-starter-bus-amqp</artifactId>
    <!-- or spring-cloud-starter-bus-kafka -->
</dependency>
```

**Flow:**
```
Git push → webhook → Config Server /bus/refresh
    → publishes RefreshRemoteApplicationEvent to RabbitMQ/Kafka
    → all subscribed service instances refresh their @RefreshScope beans
```

POST to Config Server (not each service):
```bash
curl -X POST http://config-server:8888/actuator/bus-refresh
```

---

## Backend Alternatives to Git

| Backend | Config |
|---------|--------|
| Local filesystem | `spring.cloud.config.server.native.searchLocations=file:///config` |
| Vault (secrets) | `spring.cloud.config.server.vault.*` |
| JDBC | `spring.cloud.config.server.jdbc.*` |
| AWS S3 | `spring.cloud.config.server.awss3.*` |

Use Vault for secrets in production; Git for non-sensitive structured config.

---

## Health and Troubleshooting

| Issue | Diagnosis |
|-------|-----------|
| Client can't reach Config Server | Check `spring.cloud.config.uri`, network, `fail-fast` setting |
| Properties not updating after push | Ensure `@RefreshScope` is on the bean; POST `/actuator/refresh` |
| Wrong profile loaded | Check `spring.profiles.active`; verify file naming (`-dev`, `-prod`) |
| Cipher decryption fails | Verify `ENCRYPT_KEY` env var matches the one used to encrypt |
| Git auth failure | Check credentials; use deploy keys for private repos |

Access raw config via:
```
GET http://config-server:8888/license-service/dev
```
Returns the resolved property tree for that service+profile.
