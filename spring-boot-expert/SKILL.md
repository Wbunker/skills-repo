---
name: spring-boot-expert
description: Spring Boot expertise covering auto-configuration, REST APIs, data access, security, configuration, testing, deployment, and reactive programming. Use when building Spring Boot applications, troubleshooting auto-configuration, designing REST APIs, integrating databases with Spring Data JPA, securing endpoints with Spring Security, writing @SpringBootTest tests, configuring Actuator, deploying containers, or adopting reactive WebFlux patterns. Based on "Spring Boot Up & Running" by Mark Heckler (O'Reilly, 2021).
---

# Spring Boot Expert

Based on *Spring Boot Up & Running* by Mark Heckler (O'Reilly, 2021).

## The Spring Boot Mental Model

```
┌──────────────────────────────────────────────────────────────┐
│                     SPRING BOOT APP                          │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐  │
│  │               AUTO-CONFIGURATION ENGINE                │  │
│  │  spring.factories / AutoConfiguration.imports          │  │
│  │  @ConditionalOn* → only wires what's on the classpath  │  │
│  └───────────────────────┬────────────────────────────────┘  │
│                          │                                    │
│  ┌───────────┐  ┌────────▼──────┐  ┌────────────────────┐   │
│  │  Starters │  │  Application  │  │  Embedded Server   │   │
│  │  (POMs)   │  │  Context      │  │  Tomcat/Netty      │   │
│  └───────────┘  └───────────────┘  └────────────────────┘   │
│                                                              │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌───────────────┐  │
│  │  REST    │ │  Data    │ │ Security │ │   Actuator    │  │
│  │  Layer   │ │  Layer   │ │  Layer   │ │  /health etc  │  │
│  └──────────┘ └──────────┘ └──────────┘ └───────────────┘  │
└──────────────────────────────────────────────────────────────┘
```

## Quick Reference

| Task | Reference |
|------|-----------|
| Project setup, auto-configuration, starters, Spring Initializr | [getting-started.md](references/getting-started.md) |
| REST controllers, request mapping, content negotiation, OpenAPI | [rest-api.md](references/rest-api.md) |
| JPA entities, Spring Data repositories, H2, transactions | [database.md](references/database.md) |
| Spring Security, form login, HTTP Basic, OAuth2, method security | [security.md](references/security.md) |
| application.properties/yml, profiles, @ConfigurationProperties, Actuator | [configuration.md](references/configuration.md) |
| Maven/Gradle builds, executable JARs, Docker, cloud deployment | [building-deploying.md](references/building-deploying.md) |
| @SpringBootTest, MockMvc, test slices, TestRestTemplate | [testing.md](references/testing.md) |
| Actuator endpoints, Micrometer metrics, distributed tracing | [production.md](references/production.md) |
| WebFlux, Reactor (Mono/Flux), reactive data, functional routes | [reactive.md](references/reactive.md) |

## Reference Files

| File | Chapters | Topics |
|------|----------|--------|
| `getting-started.md` | 1–2 | Spring Boot philosophy, auto-configuration internals, starters, Spring Initializr, project structure, @SpringBootApplication |
| `rest-api.md` | 3 | @RestController, @RequestMapping, HTTP verbs, path variables, request/response bodies, ResponseEntity, error handling, OpenAPI/Springdoc |
| `database.md` | 4 | JPA entities, @Repository, Spring Data JPA, CrudRepository/JpaRepository, JPQL, H2 console, datasource config, transactions |
| `security.md` | 5 | Spring Security defaults, UserDetailsService, PasswordEncoder, form login, HTTP Basic, OAuth2 client/resource server, method-level security |
| `configuration.md` | 6 | application.properties vs. yml, property binding, @ConfigurationProperties, profiles, Spring Boot Actuator, health indicators, info endpoint |
| `building-deploying.md` | 7 | Maven vs. Gradle, executable JAR/WAR, multi-stage Docker builds, Buildpacks (CNB), deploying to Kubernetes, Cloud Foundry, Heroku |
| `testing.md` | 8 | Test slices (@WebMvcTest, @DataJpaTest), @SpringBootTest modes, MockMvc, WebTestClient, TestRestTemplate, @MockBean, test properties |
| `production.md` | 9 | Actuator deep dive, custom health indicators, Micrometer metrics, Prometheus scraping, distributed tracing (Spring Cloud Sleuth/Zipkin), log correlation |
| `reactive.md` | 10 | Project Reactor (Mono, Flux), WebFlux @RestController vs. functional routes, reactive Spring Data, backpressure, testing with StepVerifier |

## Core Decision Trees

### Which Starter Do I Need?

```
What capability are you adding?
├── HTTP endpoints → spring-boot-starter-web (Tomcat/MVC)
│   └── Reactive HTTP → spring-boot-starter-webflux (Netty/WebFlux)
├── Database access
│   ├── JPA / Hibernate → spring-boot-starter-data-jpa
│   ├── JDBC only → spring-boot-starter-jdbc
│   ├── MongoDB → spring-boot-starter-data-mongodb
│   └── Redis → spring-boot-starter-data-redis
├── Security → spring-boot-starter-security
├── Testing → spring-boot-starter-test (includes JUnit 5, Mockito, AssertJ)
├── Actuator / observability → spring-boot-starter-actuator
├── Messaging
│   ├── RabbitMQ → spring-boot-starter-amqp
│   └── Kafka → spring-kafka
└── Templating (server-side HTML) → spring-boot-starter-thymeleaf
```

### Auto-configuration Not Working?

```
Bean not auto-configured?
├── Is the starter on the classpath? → check pom.xml/build.gradle
├── Is a @ConditionalOn* condition failing?
│   └── Run with --debug flag to see auto-config report
├── Did you define a bean that prevents auto-config?
│   └── Many auto-configs use @ConditionalOnMissingBean
├── Is the property disabled? (e.g., spring.security.enabled=false)
└── Check spring.autoconfigure.exclude in application.properties
```

### REST vs. Reactive?

```
Choose your programming model:
├── Familiar team, JDBC databases, simpler debugging
│   └── spring-boot-starter-web (MVC, Tomcat, blocking I/O)
├── High-concurrency I/O, WebSocket, streaming responses
│   └── spring-boot-starter-webflux (WebFlux, Netty, non-blocking)
└── Mixing both in one app → possible but use with care;
    Spring MVC takes precedence if both are present
```

## Key Spring Boot Annotations

| Annotation | Purpose |
|-----------|---------|
| `@SpringBootApplication` | Combines `@Configuration` + `@EnableAutoConfiguration` + `@ComponentScan` |
| `@RestController` | `@Controller` + `@ResponseBody` — returns data, not view names |
| `@RequestMapping` / `@GetMapping` etc. | Maps HTTP requests to handler methods |
| `@ConfigurationProperties` | Binds a block of properties to a POJO |
| `@ConditionalOnMissingBean` | Auto-config guard: only create if user hasn't defined their own |
| `@SpringBootTest` | Loads full application context for integration tests |
| `@WebMvcTest` | Loads only MVC layer (no full context) for controller tests |
| `@DataJpaTest` | Loads only JPA layer with in-memory DB for repository tests |
| `@MockBean` | Replaces a bean with a Mockito mock in the Spring context |
| `@Transactional` | Wraps method in a transaction; rolls back in tests by default |
