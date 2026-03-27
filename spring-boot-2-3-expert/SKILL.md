---
name: spring-boot-2-3-expert
description: Expert on Spring Boot 2.3.x (specifically 2.3.9.RELEASE) — project setup, auto-configuration, externalized configuration, Spring MVC, data access, Spring Security, testing, Actuator, messaging, caching, REST clients, scheduling/async, and 2.3-specific features (layered JARs, build-image, graceful shutdown, liveness/readiness probes). Use when building or debugging Spring Boot 2.3 applications, configuring properties, wiring security, setting up data layers, writing tests, or containerizing with Docker. Based on official Spring Boot 2.3.9.RELEASE reference documentation.
---

# Spring Boot 2.3 Expert

Based on the official [Spring Boot 2.3.9.RELEASE Reference Documentation](https://docs.spring.io/spring-boot/docs/2.3.9.RELEASE/reference/html/).

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                     SPRING BOOT APPLICATION                          │
│                                                                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────────┐   │
│  │  @SpringBoot │  │   Auto-      │  │  Externalized Config      │   │
│  │  Application │  │   Config     │  │  (properties/yml/env)     │   │
│  │  (main class)│  │  (factories) │  │  @ConfigurationProperties │   │
│  └──────┬───────┘  └──────┬───────┘  └─────────────┬────────────┘   │
│         │                 │                         │                │
│  ┌──────▼─────────────────▼─────────────────────────▼────────────┐  │
│  │               APPLICATION CONTEXT (Spring IoC)                 │  │
│  │  Beans · DI · AOP · Events · Profiles · Conditional wiring     │  │
│  └────────────┬────────────────────────────────────┬─────────────┘  │
│               │                                    │                 │
│  ┌────────────▼────────────┐      ┌────────────────▼─────────────┐  │
│  │    WEB LAYER             │      │    DATA LAYER                 │  │
│  │  DispatcherServlet       │      │  DataSource / JPA / JDBC      │  │
│  │  @RestController         │      │  Spring Data Repositories     │  │
│  │  Spring Security Filter  │      │  Flyway / Liquibase           │  │
│  │  Embedded Tomcat/Jetty   │      │  R2DBC (reactive, new 2.3)    │  │
│  └────────────┬────────────┘      └────────────────┬─────────────┘  │
│               │                                    │                 │
│  ┌────────────▼────────────────────────────────────▼─────────────┐  │
│  │                  SPRING BOOT ACTUATOR                           │  │
│  │  /health (liveness/readiness probes)  /metrics  /loggers       │  │
│  │  Micrometer · Custom endpoints · Kubernetes-ready              │  │
│  └────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘

2.3-SPECIFIC ADDITIONS:
  graceful shutdown (server.shutdown=graceful)
  layered JARs  ·  spring-boot:build-image (Cloud Native Buildpacks)
  spring-boot-starter-validation (split from web starter)
  liveness/readiness health groups  ·  R2DBC GA  ·  WebClient auto-config
```

## Quick Reference — Load the Right File

| Task | Reference File |
|------|---------------|
| Project setup, Maven/Gradle builds, starters, main class, packaging JAR/WAR | [setup.md](references/setup.md) |
| Auto-configuration mechanism, spring.factories, @Conditional, custom auto-config | [auto-configuration.md](references/auto-configuration.md) |
| application.properties/yml, @Value, @ConfigurationProperties, profiles, relaxed binding | [configuration.md](references/configuration.md) |
| @RestController, @RequestMapping, request params, exception handling, CORS, Thymeleaf | [web-mvc.md](references/web-mvc.md) |
| JPA entities, repositories, pagination, @Transactional, datasource, Flyway, JdbcTemplate | [data-access.md](references/data-access.md) |
| WebSecurityConfigurerAdapter, HttpSecurity, JWT, UserDetailsService, method security | [security.md](references/security.md) |
| @SpringBootTest, @WebMvcTest, @DataJpaTest, MockMvc, @MockBean, TestRestTemplate | [testing.md](references/testing.md) |
| Actuator endpoints, health indicators, Micrometer metrics, custom endpoints | [actuator.md](references/actuator.md) |
| RabbitMQ, Kafka, JMS, @RabbitListener, @KafkaListener, RabbitTemplate, KafkaTemplate | [messaging.md](references/messaging.md) |
| @EnableCaching, @Cacheable, @CacheEvict, Redis cache, Caffeine cache | [caching.md](references/caching.md) |
| RestTemplate, WebClient, RestTemplateBuilder, WebClient.Builder customization | [rest-clients.md](references/rest-clients.md) |
| @Scheduled, @Async, @EnableScheduling, @EnableAsync, thread pool configuration | [scheduling-async.md](references/scheduling-async.md) |
| 2.3 features: build-image, layered JARs, graceful shutdown, probes, R2DBC, validation | [spring-boot-2-3-features.md](references/spring-boot-2-3-features.md) |
| Logging: Logback, log levels, log groups, file output, structured logging | [logging.md](references/logging.md) |

## Core Decision Trees

### What Auto-Configuration Is Active?

```
Need to know what's being configured?
├── Run with --debug flag
│   └── java -jar app.jar --debug  (prints conditions evaluation report)
├── Hit /actuator/conditions endpoint (if actuator exposed)
└── @SpringBootApplication(exclude=SomeAutoConfiguration.class)
    └── Disable specific auto-config you don't want
```

### Which Config Source Takes Priority?

```
High → Low priority:
  1. Command line args  (--server.port=9090)
  2. SPRING_APPLICATION_JSON  (env var or system prop)
  3. OS environment variables  (SPRING_PROFILES_ACTIVE)
  4. Java system properties  (-Dserver.port=9090)
  5. Profile-specific outside jar  (application-prod.properties)
  6. Profile-specific inside jar
  7. application.properties outside jar  (./config/application.properties)
  8. application.properties inside jar  (classpath:application.properties)
  9. @PropertySource annotations
 10. Default properties

Rule: Higher number = lower priority (overridden by sources above it)
```

### Which Web Layer Test Slice to Use?

```
What do you need to test?
├── Full application stack → @SpringBootTest(webEnvironment=RANDOM_PORT)
│   └── Use TestRestTemplate or WebTestClient
├── Just the controller layer (no DB, no services) → @WebMvcTest(MyController.class)
│   └── Use MockMvc; @MockBean service dependencies
├── Just JPA repositories → @DataJpaTest
│   └── Uses in-memory H2 by default; real @Entity scanning
├── Just JDBC → @JdbcTest
└── Just caching, messaging, etc. → @SpringBootTest with @ActiveProfiles("test")
```

### Which Cache Provider?

```
What cache technology is available on classpath?
├── Redis on classpath → RedisCacheManager auto-configured
│   └── spring.cache.redis.time-to-live=600000
├── Caffeine on classpath → CaffeineCacheManager auto-configured
│   └── spring.cache.caffeine.spec=maximumSize=500,expireAfterAccess=600s
├── EhCache XML present → EhCacheCacheManager
├── Hazelcast present → HazelcastCacheManager
├── Nothing → ConcurrentMapCacheManager (simple, no TTL)
└── Force specific: spring.cache.type=redis|caffeine|simple|none
```

### Graceful Shutdown vs Abrupt?

```
Containerized / Kubernetes workload?
├── Yes → server.shutdown=graceful
│         spring.lifecycle.timeout-per-shutdown-task=30s
│         Configure Kubernetes preStop hook: sleep 10
│         Use /actuator/health/readiness probe
└── No  → default (abrupt) is fine for most dev/test scenarios
```

## Key Concepts Cheatsheet

| Annotation | Purpose |
|-----------|---------|
| `@SpringBootApplication` | = @Configuration + @EnableAutoConfiguration + @ComponentScan |
| `@ConfigurationProperties("prefix")` | Bind a group of properties to a bean |
| `@Value("${prop:default}")` | Inject single property |
| `@Profile("dev")` | Conditional on active profile |
| `@ConditionalOnClass(Foo.class)` | Conditional on classpath presence |
| `@ConditionalOnMissingBean` | Only create bean if not already defined |
| `@ConditionalOnProperty(name="x", havingValue="true")` | Conditional on property value |
| `@Transactional` | Demarcate transaction boundary |
| `@Cacheable("cacheName")` | Cache method result |
| `@Scheduled(fixedDelay=5000)` | Schedule periodic task |
| `@Async` | Execute method in thread pool |
| `@SpringBootTest` | Full context integration test |
| `@WebMvcTest` | Slice test: controller layer only |
| `@DataJpaTest` | Slice test: JPA repository layer only |
| `@MockBean` | Replace bean with Mockito mock in test context |
