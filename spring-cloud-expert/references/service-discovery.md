---
name: service-discovery
description: Eureka server and client setup, self-registration, client-side load balancing with Ribbon, Feign declarative REST client, zone affinity. Chapter 4 of Spring Microservices in Action.
type: reference
---

# Service Discovery: Eureka, Ribbon, and Feign

## Why Service Discovery?

In a cloud environment, service instances have dynamic IP addresses and ports. Hardcoded URLs break as services scale up, restart, or move. Service discovery solves this with a runtime registry.

### Client-Side vs. Server-Side Discovery

| Pattern | How it works | Spring Cloud approach |
|---------|-------------|----------------------|
| **Client-side** | Client queries registry, picks instance, calls directly | Eureka + Ribbon |
| **Server-side** | Load balancer queries registry; client calls LB | AWS ALB, Nginx |

Spring Cloud uses **client-side discovery**: services register with Eureka; consumers use Ribbon to load-balance across registered instances. The API gateway (Zuul/Gateway) still provides a single entry point for external clients.

---

## Eureka Server

### Setup
```xml
<dependency>
    <groupId>org.springframework.cloud</groupId>
    <artifactId>spring-cloud-starter-netflix-eureka-server</artifactId>
</dependency>
```

```java
@SpringBootApplication
@EnableEurekaServer
public class EurekaServerApplication {
    public static void main(String[] args) {
        SpringApplication.run(EurekaServerApplication.class, args);
    }
}
```

### `application.yml` (standalone, non-HA)
```yaml
server:
  port: 8761

eureka:
  instance:
    hostname: localhost
  client:
    register-with-eureka: false    # Don't register self
    fetch-registry: false          # Don't fetch own registry
    service-url:
      defaultZone: http://${eureka.instance.hostname}:${server.port}/eureka/
```

### High-Availability Eureka (Peer Replication)
Run two instances. Each registers with the other:
```yaml
# eureka-1 application.yml
eureka:
  client:
    register-with-eureka: true
    fetch-registry: true
    service-url:
      defaultZone: http://eureka-2:8761/eureka/
```

Eureka is designed for **AP** (availability + partition tolerance). During partitions, stale data is served rather than failing requests.

---

## Eureka Client (Service Registration)

### Dependencies
```xml
<dependency>
    <groupId>org.springframework.cloud</groupId>
    <artifactId>spring-cloud-starter-netflix-eureka-client</artifactId>
</dependency>
```

### `bootstrap.yml`
```yaml
spring:
  application:
    name: license-service    # This becomes the Eureka service ID

eureka:
  instance:
    prefer-ip-address: true               # Register with IP, not hostname
    lease-renewal-interval-in-seconds: 30 # Heartbeat interval (default 30)
    lease-expiration-duration-in-seconds: 90
  client:
    register-with-eureka: true
    fetch-registry: true
    service-url:
      defaultZone: http://eureka-server:8761/eureka/
```

The service automatically registers on startup and deregisters on graceful shutdown. `@EnableEurekaClient` annotation is optional with Spring Boot auto-configuration.

### Registration Flow
```
Service starts → registers with Eureka (POST /eureka/apps/{appName})
             → sends heartbeats every 30s (PUT /eureka/apps/{appName}/{instanceId})
             → Eureka marks UNKNOWN→UP after initial lease
Service stops → sends deregistration (DELETE /eureka/apps/{appName}/{instanceId})
```

### Eureka Self-Preservation Mode
When Eureka stops receiving heartbeats at the expected rate (network partition), it enters self-preservation: **it stops evicting instances**. This prevents mass deregistration during network blips.

Disable for development:
```yaml
eureka:
  server:
    enable-self-preservation: false
```

---

## Client-Side Load Balancing with Ribbon

Ribbon is integrated into Eureka clients. When you inject a `@LoadBalanced RestTemplate`, it intercepts requests and substitutes the service name for a real IP:port.

```java
@Bean
@LoadBalanced
public RestTemplate restTemplate() {
    return new RestTemplate();
}
```

Usage — use the Eureka service name as hostname:
```java
Organization org = restTemplate.getForObject(
    "http://organization-service/v1/organizations/{orgId}",
    Organization.class, orgId);
```

Ribbon resolves `organization-service` → fetches instance list from local Eureka cache → picks one instance using round-robin (default) → executes the call.

### Ribbon Load Balancing Policies
| Policy | Behavior |
|--------|----------|
| `RoundRobinRule` (default) | Cycle through instances |
| `RandomRule` | Pick randomly |
| `WeightedResponseTimeRule` | Prefer faster instances |
| `ZoneAvoidanceRule` | Avoid failing availability zones |

Configure per service:
```yaml
organization-service:
  ribbon:
    NFLoadBalancerRuleClassName: com.netflix.loadbalancer.RandomRule
```

---

## Feign Declarative REST Client

Feign generates an HTTP client from an annotated interface — no boilerplate RestTemplate code.

### Enable Feign
```java
@SpringBootApplication
@EnableFeignClients
public class LicenseServiceApplication { ... }
```

### Define a Feign Client

```java
@FeignClient("organization-service")   // Eureka service name
public interface OrganizationFeignClient {

    @GetMapping(value = "/v1/organizations/{organizationId}",
                consumes = "application/json")
    Organization getOrganization(
        @PathVariable("organizationId") String organizationId);
}
```

Feign automatically:
- Resolves the service name via Eureka
- Load-balances via Ribbon
- Integrates with Hystrix (circuit breaker) when on the classpath

### Inject and Use

```java
@Service
public class LicenseService {

    @Autowired
    private OrganizationFeignClient organizationFeignClient;

    public License getLicense(String licenseId, String organizationId) {
        Organization org = organizationFeignClient.getOrganization(organizationId);
        // ...
    }
}
```

### Feign Logging
```yaml
logging:
  level:
    com.example.clients.OrganizationFeignClient: DEBUG

feign:
  client:
    config:
      default:
        loggerLevel: full   # none | basic | headers | full
```

---

## Zone Affinity

In multi-AZ deployments, route traffic to the same availability zone to reduce latency.

```yaml
eureka:
  instance:
    metadata-map:
      zone: us-east-1a    # Tag instance with its zone
  client:
    prefer-same-zone-eureka: true
```

Ribbon's `ZoneAvoidanceRule` (default in cloud environments) respects this.

---

## Troubleshooting

| Symptom | Likely Cause |
|---------|-------------|
| Service shows UP in Eureka but calls fail | Stale cache; wait up to 30s or set `ribbon.ServerListRefreshInterval` |
| Service stays UNKNOWN | Slow startup; increase `lease-renewal-interval-in-seconds` |
| `UnknownHostException` on service name | Feign/Ribbon not wired; check `@EnableFeignClients`, `@LoadBalanced` |
| Self-preservation warning in Eureka dashboard | Expected in dev; disable `enable-self-preservation: false` |
| Calls never go to new instance | Ribbon cache TTL; default refresh is 30s |

### Check Registered Instances
```
GET http://eureka-server:8761/eureka/apps
GET http://eureka-server:8761/eureka/apps/ORGANIZATION-SERVICE
```
