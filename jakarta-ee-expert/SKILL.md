---
name: jakarta-ee-expert
description: Jakarta EE 10/11 expertise covering the full enterprise Java stack — from beginner setup (GlassFish, NetBeans, first Servlet/JSP) through Faces, EL, data tables, AJAX, JPA, JDBC, REST, CDI, MicroProfile (Config, Fault Tolerance, Metrics, Health, JWT, REST Client, OpenAPI), Bean Validation, Concurrency, Batch, WebSockets, Jakarta MVC, XML/JSON binding, Jakarta Mail, Hibernate ORM, NoSQL, JMX monitoring, security, Docker containerization, and Kubernetes deployment. Use when building or learning Jakarta EE or MicroProfile cloud-native applications, configuring WildFly/GlassFish/Payara/Open Liberty, implementing enterprise patterns, testing with TestContainers, or deploying to Kubernetes. Sources: Zambon (Apress), Späth (Apress), Saeed & Abdallah "Pro Cloud-Native Java EE Apps" (Apress 2022/2025).
---

# Jakarta EE 10 Expert

Sources:
- *Beginning Jakarta EE Web Development* by Giulio Zambon (Apress) — beginner-to-intermediate web tier
- *Pro Jakarta EE 10* by Peter Späth (Apress, 2023) — advanced full-stack enterprise
- *Pro Cloud-Native Java EE Apps* by Luqman Saeed & Ghazy Abdallah (Apress, 2022/2025) — MicroProfile APIs, TestContainers, Docker, Kubernetes

**Jakarta EE 10 targets Java 11+; key spec versions:** Faces 4.0, CDI 4.0, Persistence 3.1, REST 3.1, Security 3.0, Concurrency 3.0, Batch 2.1, MVC 2.1, WebSocket 2.1, Bean Validation 3.0, JSON-P 2.1, JSON-B 3.0. **MicroProfile 6.x/7.0**: Config, Fault Tolerance, Metrics, Health, JWT Auth, REST Client, OpenAPI.

## Jakarta EE 10 Architecture Overview

```
┌──────────────────────────────────────────────────────────────────────┐
│                     JAKARTA EE 10 APPLICATION                         │
│                                                                       │
│  ┌────────────────────────────────────────────────────────────────┐  │
│  │  WEB / PRESENTATION TIER                                        │  │
│  │  Jakarta Faces 4 (Facelets)  │  Jakarta MVC 2  │  REST 3.1     │  │
│  │  WebSocket 2.1               │  Servlet 6.0    │  Pages 3.1    │  │
│  └─────────────────────────────┬──────────────────────────────────┘  │
│                                 │                                     │
│  ┌──────────────────────────────▼─────────────────────────────────┐  │
│  │  BUSINESS / SERVICES TIER                                        │  │
│  │  CDI 4.0 (dependency injection, events, interceptors)           │  │
│  │  EJB 4.0 (session beans, MDB)  │  Batch 2.1  │  Concurrency 3  │  │
│  │  Bean Validation 3.0           │  MicroProfile extensions        │  │
│  └─────────────────────────────┬──────────────────────────────────┘  │
│                                 │                                     │
│  ┌──────────────────────────────▼─────────────────────────────────┐  │
│  │  DATA / INTEGRATION TIER                                         │  │
│  │  JPA 3.1 / Hibernate  │  JSON-P 2.1  │  JSON-B 3.0              │  │
│  │  JAXB 4.0 (XML)       │  Jakarta Mail 2.1  │  Connectors 2.1    │  │
│  │  NoSQL  │  Caching     │  JMS 3.1                               │  │
│  └──────────────────────────────────────────────────────────────── ┘  │
│                                                                       │
│  ┌────────────────────────────────────────────────────────────────┐  │
│  │  CROSS-CUTTING                                                   │  │
│  │  Security 3.0 (form/cert/JWT)  │  JMX  │  Log4j  │  Monitoring │  │
│  └────────────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────────┘
```

## Quick Reference

| Task | Reference |
|------|-----------|
| **Beginner start** — GlassFish 7, NetBeans, first WAR, Servlet/JSP basics | [beginner-quickstart.md](references/beginner-quickstart.md) |
| **Faces + EL** — h: components, EL syntax, validation, navigation, data tables, f:ajax | [faces-el-navigation.md](references/faces-el-navigation.md) |
| **JPA + JDBC + REST basics** — entities, JPQL, DataSource, CRUD, JAX-RS | [jpa-jdbc-basics.md](references/jpa-jdbc-basics.md) |
| Advanced server install, Eclipse/NetBeans, Git, CI, Maven repos | [devworkflow.md](references/devworkflow.md) |
| Advanced Facelets, custom Faces components, Flows, WebSockets, frontend, Jakarta MVC | [web-tier.md](references/web-tier.md) |
| Form auth, client certs, REST security, JWT, JMX security, enterprise security API | [security.md](references/security.md) |
| MicroProfile, CDI extensions, interceptors, Bean Validation, Concurrency, Batch | [architecture.md](references/architecture.md) |
| XML binding (JAXB), JSON-P/JSON-B, Jakarta Mail, app client, scripting languages | [supporting-tech.md](references/supporting-tech.md) |
| Hibernate/JPA advanced, connectors, caching, NoSQL | [resources.md](references/resources.md) |
| JMX monitoring, logging workflows, Log4j custom appenders | [monitoring.md](references/monitoring.md) |
| **MicroProfile Config, Fault Tolerance, Metrics, Health, JWT Auth** — full API reference | [microprofile-apis.md](references/microprofile-apis.md) |
| Cloud-native concepts, TestContainers testing, Docker, Kubernetes, production checklist | [cloud-native-devops.md](references/cloud-native-devops.md) |

## Reference Files

| File | Source | Chapters | Topics |
|------|--------|----------|--------|
| `beginner-quickstart.md` | Zambon | 1–3 | GlassFish 7 setup, NetBeans, Maven WAR project, first Servlet, JSP + JSTL, servlet lifecycle |
| `faces-el-navigation.md` | Zambon | 4–10 | h: component guide, EL syntax, validation/converters, navigation, bookmarkable URLs, data tables, f:ajax |
| `jpa-jdbc-basics.md` | Zambon | 11–13 | JPA entities, persistence.xml, JPQL, JDBC DataSource, CRUD patterns, JAX-RS REST basics |
| `devworkflow.md` | Späth | 1–6 | Server install, Eclipse/NetBeans projects, Git/SVN, CI pipelines, Nexus/Artifactory Maven repos |
| `web-tier.md` | Späth | 7–11, 15 | Facelets templates, custom components, Flows, WebSocket API, frontend integration, Jakarta MVC |
| `security.md` | Späth | 12–14, 31–33 | Form-based auth, client certificates, REST JWT security, JMX security, enterprise security API |
| `architecture.md` | Späth | 16–21 | MicroProfile extensions, custom CDI, interceptors, Bean Validation 3, Concurrency 3, Batch 2.1 |
| `supporting-tech.md` | Späth | 22–26 | JAXB 4 XML binding, JSON-P/JSON-B, Jakarta Mail, application client, Groovy/scripting |
| `resources.md` | Späth | 27–30 | Hibernate as JPA provider, resource adapters/connectors, caching (Infinispan), NoSQL |
| `monitoring.md` | Späth | 34–39 | JMX monitoring workflow, enterprise logging, custom Log4j appenders |
| `microprofile-apis.md` | Saeed & Abdallah | 7–11 | MP Config (sources, @ConfigProperty), Fault Tolerance (@Retry/@CircuitBreaker/@Bulkhead/@Fallback/@Timeout), Metrics (@Counted/@Timed/@Gauge), Health (@Liveness/@Readiness/@Startup), JWT Auth (@Claim, token verification, claim injection) |
| `cloud-native-devops.md` | Saeed & Abdallah | 1–3, 12–13 | Cloud-native architecture, 12-factor Jakarta EE, MP REST Client, OpenAPI, TestContainers integration testing, Docker/Bootable JAR, Kubernetes Deployment/Service/Ingress/ConfigMap, production readiness checklist |

## Core Decision Trees

### New to Jakarta EE or Experienced?

```
What is your starting point?
├── Just starting out / need to set up environment
│   └── → beginner-quickstart.md (GlassFish, NetBeans, first Servlet/JSP)
├── Building a Faces web UI and need component / EL / AJAX reference
│   └── → faces-el-navigation.md (h: components, EL, data tables, f:ajax)
├── Working with database (JPA or JDBC) or building a REST API
│   └── → jpa-jdbc-basics.md (entities, JPQL, DataSource, JAX-RS)
└── Already comfortable with Jakarta EE, need advanced patterns
    ├── Multi-step wizards, WebSockets, frontend integration → web-tier.md
    ├── CDI, MicroProfile, Batch, Concurrency         → architecture.md
    ├── Security (JWT, certs, LDAP)                   → security.md
    ├── JAXB, JSON-P/B, Jakarta Mail                  → supporting-tech.md
    ├── Hibernate advanced, NoSQL, connectors          → resources.md
    ├── JMX monitoring, Log4j appenders               → monitoring.md
    ├── MicroProfile Config / Fault Tolerance / Metrics / Health / JWT → microprofile-apis.md
    └── Docker, Kubernetes, TestContainers, cloud-native ops → cloud-native-devops.md
```

### Which Spec/API Handles This?

```
What do I need to build?
├── Web UI (server-side rendered) → Jakarta Faces 4 (Facelets)
│   └── Complex flows / wizards → Jakarta Faces Flows (Ch 9)
├── REST / HTTP API → Jakarta REST (JAX-RS) 3.1
│   └── Controller-based MVC (not component-based) → Jakarta MVC 2
├── Real-time push / bidirectional → WebSocket 2.1
├── Background long-running jobs → Jakarta Batch 2.1
├── Async/parallel tasks → Jakarta Concurrency 3.0
├── Dependency injection / events → CDI 4.0
├── Transactional services → CDI beans + JTA
├── Database ORM → JPA 3.1 (Hibernate provider)
├── Document/graph/key-value store → NoSQL connector
├── XML marshal/unmarshal → JAXB 4.0 (Jakarta XML Binding)
├── JSON → JSON-P 2.1 (streaming/object model) or JSON-B 3.0 (binding)
├── Sending email → Jakarta Mail 2.1
└── Application security → Jakarta Security 3.0
```

### Which Security Mechanism?

```
What is my threat model / use case?
├── Browser users, HTML form login → Form-based authentication (Ch 12)
│   └── Uses @FormAuthenticationMechanismDefinition
├── Mutual TLS / enterprise PKI → Client certificates (Ch 13)
│   └── Configure server truststore + CLIENT-CERT auth
├── Stateless REST clients / SPAs → JWT Bearer tokens (Ch 14, 32)
│   └── @JwtAuthenticationMechanismDefinition (MP-JWT) or custom
├── Programmatic authorization → Jakarta Security IdentityStore / SecurityContext
└── Service-to-service internal → JMX secured channel (Ch 31)
```

### MicroProfile vs. Jakarta EE — When to Use Which?

```
Need cloud-native extension?
├── Health endpoints (/health, /health/live) → MP Health
├── Metrics for Prometheus → MP Metrics
├── Distributed tracing → MP OpenTelemetry
├── Circuit breaker, retry, timeout → MP Fault Tolerance
├── Config from env/files/k8s → MP Config
├── Type-safe REST client → MP REST Client
├── JWT propagation → MP JWT Auth
└── OpenAPI docs → MP OpenAPI
All are supplemental to core Jakarta EE specs; use together.
```

## Key Concepts

### CDI — The Glue of Jakarta EE
CDI 4.0 is the foundation. Beans are discovered automatically (via `beans.xml` or annotation). Key annotations: `@ApplicationScoped`, `@SessionScoped`, `@RequestScoped`, `@Dependent`. Events (`@Observes`), interceptors (`@Interceptor`), decorators, and producers (`@Produces`) make it a complete DI + AOP system.

### Portability
Jakarta EE applications are portable across certified servers: **WildFly**, **GlassFish 7**, **Payara 6**, **Open Liberty**, **TomEE 10**, **Quarkus** (subset). Vendor-specific config (e.g., `standalone.xml` in WildFly) is separate from portable `web.xml`/`beans.xml`.

### Packaging
| Artifact | Content | Deployed as |
|----------|---------|------------|
| `.war` | Web components (Servlets, Faces, REST) | Web container |
| `.jar` (with `beans.xml`) | CDI bean archive | Embedded in WAR or EAR |
| `.ear` | Multiple WARs + EJB JARs | Full EE server |
| Executable JAR / container image | Microservice packaging | Cloud / Kubernetes |
