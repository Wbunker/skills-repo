---
name: spring-cloud-expert
description: >
  Spring Cloud and Spring Boot microservices expertise covering service decomposition,
  configuration management, service discovery, client resiliency, API gateways, security,
  event-driven messaging, distributed tracing, and containerized deployment. Use when
  designing or implementing microservices with Spring Boot, Spring Cloud Config, Eureka,
  Hystrix/Resilience4j, Zuul/Gateway, OAuth2/JWT, Spring Cloud Stream, Sleuth/Zipkin,
  or deploying to Docker/Kubernetes. Based on Carnell's "Spring Microservices in Action."
---

# Spring Cloud Expert

Based on "Spring Microservices in Action" by John Carnell (Manning Publications).

## The Spring Cloud Microservices Landscape

```
┌──────────────────────────────────────────────────────────────────┐
│                     CLIENT / CONSUMERS                           │
└────────────────────────────┬─────────────────────────────────────┘
                             │
                             ▼
┌──────────────────────────────────────────────────────────────────┐
│              API GATEWAY  (Zuul / Spring Cloud Gateway)          │
│   Route · Filter · Rate-limit · Auth token relay                 │
└───────┬──────────────────────────────────────┬───────────────────┘
        │                                       │
        ▼                                       ▼
┌───────────────────┐                ┌──────────────────────┐
│  MICROSERVICE A   │                │   MICROSERVICE B     │
│  Spring Boot app  │◄──Feign/REST──►│   Spring Boot app    │
│  + Hystrix/R4j    │                │   + Hystrix/R4j      │
└────────┬──────────┘                └──────────┬───────────┘
         │                                       │
         ▼                                       ▼
┌──────────────────────────────────────────────────────────────────┐
│              SERVICE REGISTRY  (Eureka)                          │
│   Register · Discover · Health-check                             │
└──────────────────────────────────────────────────────────────────┘
         │                                       │
         ▼                                       ▼
┌──────────────────────────────────────────────────────────────────┐
│           SPRING CLOUD CONFIG SERVER                             │
│   Git-backed · Env profiles · Encrypted secrets                  │
└──────────────────────────────────────────────────────────────────┘
         │
         ▼
┌──────────────────────────────────────────────────────────────────┐
│  CROSS-CUTTING CONCERNS                                          │
│  Security (OAuth2/JWT) · Tracing (Sleuth+Zipkin)                 │
│  Messaging (Spring Cloud Stream) · Deployment (Docker/K8s)       │
└──────────────────────────────────────────────────────────────────┘
```

## Quick Reference

| Task | Reference |
|------|-----------|
| Microservice principles, decomposition, Spring Boot setup | [foundations.md](references/foundations.md) |
| Spring Cloud Config Server, profiles, encryption, refresh | [configuration.md](references/configuration.md) |
| Eureka server/client, client-side load balancing, Ribbon | [service-discovery.md](references/service-discovery.md) |
| Circuit breakers, Hystrix, Resilience4j, bulkheads, fallbacks | [resiliency.md](references/resiliency.md) |
| API gateway, Zuul filters, routing, Spring Cloud Gateway | [routing.md](references/routing.md) |
| OAuth2, JWT, Spring Security, token relay, service-to-service auth | [security.md](references/security.md) |
| Spring Cloud Stream, Kafka, RabbitMQ, event-driven patterns | [messaging.md](references/messaging.md) |
| Spring Cloud Sleuth, Zipkin, correlation IDs, log aggregation | [observability.md](references/observability.md) |
| Docker, Docker Compose, Kubernetes, CI/CD deployment pipelines | [deployment.md](references/deployment.md) |

## Reference Files

| File | Chapters | Topics |
|------|----------|--------|
| `foundations.md` | 1–2 | Microservice principles, monolith vs. microservice trade-offs, Spring Boot auto-configuration, actuator, REST endpoints, 12-factor app |
| `configuration.md` | 3 | Spring Cloud Config Server setup, Git backend, property encryption, `@RefreshScope`, Spring Cloud Bus broadcast |
| `service-discovery.md` | 4 | Eureka server, `@EnableEurekaClient`, Ribbon client-side LB, Feign declarative REST client, zone affinity |
| `resiliency.md` | 5 | Client resiliency patterns, Hystrix `@HystrixCommand`, circuit breaker states, thread pool isolation, fallback, Resilience4j equivalents |
| `routing.md` | 6 | Zuul API gateway, pre/route/post filters, dynamic routing, Spring Cloud Gateway predicates and filters, rate limiting |
| `security.md` | 7 | OAuth2 authorization server, resource server, JWT tokens, Spring Security, token propagation across service calls |
| `messaging.md` | 8 | Spring Cloud Stream binders (Kafka/RabbitMQ), `@StreamListener`, message channels, consumer groups, event-driven choreography |
| `observability.md` | 9 | Spring Cloud Sleuth trace/span IDs, Zipkin server, log correlation, custom spans, ELK stack integration |
| `deployment.md` | 10 | Dockerizing Spring Boot services, Docker Compose multi-service stacks, Kubernetes deployments and services, CI/CD patterns |

## Core Decision Trees

### Where Does This Problem Belong?

```
What are you trying to solve?
│
├── "Services can't find each other at runtime"
│   → Service Discovery → service-discovery.md
│
├── "Config values differ per environment / need secrets"
│   → Config Server → configuration.md
│
├── "Downstream service is slow or failing"
│   → Resiliency patterns → resiliency.md
│
├── "Need a single entry point for all clients"
│   → API Gateway → routing.md
│
├── "Need to secure inter-service calls / user identity"
│   → OAuth2 / JWT → security.md
│
├── "Services need to communicate without tight coupling"
│   → Event-driven messaging → messaging.md
│
├── "Can't trace a request across multiple services"
│   → Distributed tracing → observability.md
│
└── "Need to package and ship services consistently"
    → Docker / Kubernetes → deployment.md
```

### Choosing a Communication Style

```
How should services communicate?
│
├── Synchronous required (immediate response)
│   ├── Internal service-to-service → Feign + Eureka (service-discovery.md)
│   └── External clients → API Gateway (routing.md)
│
└── Asynchronous acceptable (decouple producers/consumers)
    ├── Fire-and-forget → Spring Cloud Stream + Kafka/Rabbit (messaging.md)
    └── Event sourcing / saga → Spring Cloud Stream choreography (messaging.md)
```

### Circuit Breaker: When to Use What

```
Which resiliency library?
│
├── Legacy Spring Cloud (pre-2020) → Netflix Hystrix
│   └── @HystrixCommand + HystrixDashboard
│
└── Modern Spring Cloud (2020+) → Resilience4j
    ├── @CircuitBreaker for state machine
    ├── @Bulkhead for thread/semaphore isolation
    ├── @RateLimiter for throttling
    └── @Retry for transient failures
```

## Key Concepts

### The 12-Factor Microservice (Carnell's Lens)
| Factor | Spring Cloud Mechanism |
|--------|----------------------|
| Config | Spring Cloud Config Server |
| Backing services | Spring Data + profiles |
| Port binding | Spring Boot embedded server |
| Processes (stateless) | JWT tokens, no server-side session |
| Disposability | Actuator `/shutdown`, graceful shutdown |
| Logs | Sleuth trace IDs, ELK aggregation |

### Service Communication Patterns
- **Feign** — declarative REST client; auto-integrates with Ribbon (load balancing) and Hystrix (circuit breaking)
- **RestTemplate** with `@LoadBalanced` — imperative alternative to Feign
- **Spring Cloud Gateway** — reactive API gateway; replaces Zuul 1.x for new projects

### Correlation ID Pattern
Every inbound request gets a correlation ID at the gateway edge. Sleuth propagates it automatically as an MDC variable through all downstream calls, making cross-service log stitching trivial.

### Config Refresh Without Restart
1. Actuator exposes `/actuator/refresh` (POST)
2. Annotate beans with `@RefreshScope`
3. Spring Cloud Bus + Kafka/Rabbit: broadcast refresh to all instances at once
