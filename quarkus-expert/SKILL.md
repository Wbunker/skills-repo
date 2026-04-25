---
name: quarkus-expert
description: Quarkus expertise covering project setup, developer productivity, REST/GraphQL/gRPC communications, testing, web UI and security, database access with Panache, reactive programming with Mutiny, messaging with Kafka/RabbitMQ, cloud-native patterns, Kubernetes/OpenShift deployment, and custom extensions. Use when building, debugging, or deploying Quarkus applications. Based on "Quarkus in Action" by Jan Martiska and Martin Štefanko (Manning, 2024).
---

# Quarkus Expert

Based on **"Quarkus in Action"** by Jan Martiska and Martin Štefanko (Manning, 2024).

## Progressive Disclosure — Load Only What You Need

Read the dispatch table below. Load **only the reference file(s)** that match the user's task. Do not load all references.

## Dispatch Table

| Task / Topic | Load This Reference |
|---|---|
| What is Quarkus, project generation, GraalVM native compilation, extensions overview | [foundations.md](references/foundations.md) |
| Dev mode, live coding, Dev UI, Dev Services, configuration profiles | [developer-productivity.md](references/developer-productivity.md) |
| REST endpoints, REST clients, GraphQL, gRPC, Protocol Buffers, streaming | [communications.md](references/communications.md) |
| Unit tests, integration tests, Mockito, native mode tests, test profiles | [testing.md](references/testing.md) |
| Qute templates, HTMX, web apps, OpenID Connect, Keycloak, RBAC | [web-and-security.md](references/web-and-security.md) |
| Panache, JPA/Hibernate ORM, repositories, MongoDB, transactions, reactive data | [database.md](references/database.md) |
| Mutiny, reactive streams, virtual threads (Project Loom), reactive vs. imperative | [reactive.md](references/reactive.md) |
| Kafka, RabbitMQ, MicroProfile Reactive Messaging, message acknowledgment | [messaging.md](references/messaging.md) |
| Health checks, metrics, OpenTelemetry tracing, fault tolerance, service discovery | [cloud-native-patterns.md](references/cloud-native-patterns.md) |
| Container images, Kubernetes, OpenShift, serverless (Funqy, Knative), cloud deploy | [deployment.md](references/deployment.md) |
| Writing custom extensions, build-time augmentation, bytecode generation | [extensions.md](references/extensions.md) |

## Reference Files

| File | Chapters | Topics |
|---|---|---|
| `foundations.md` | 1–2 | Quarkus architecture, project bootstrap, native compilation, extension system |
| `developer-productivity.md` | 3 | Live coding, config profiles, Dev UI, Dev Services, continuous testing |
| `communications.md` | 4 | RESTEasy Reactive, REST clients, SmallRye GraphQL, gRPC, streaming |
| `testing.md` | 5 | `@QuarkusTest`, `@NativeImageTest`, Mockito, `@TestProfile` |
| `web-and-security.md` | 6 | Qute, HTMX, `quarkus-security`, OIDC, Keycloak, RBAC |
| `database.md` | 7 | Panache Active Record & Repository, Hibernate ORM, MongoDB, transactions |
| `reactive.md` | 8 | Mutiny `Uni`/`Multi`, reactive engines, virtual threads, back-pressure |
| `messaging.md` | 9 | `@Incoming`/`@Outgoing`, Kafka connector, RabbitMQ connector, acknowledgment |
| `cloud-native-patterns.md` | 10 | SmallRye Health, Micrometer, OpenTelemetry, SmallRye Fault Tolerance |
| `deployment.md` | 11 | `quarkus-container-image-*`, Kubernetes extension, OpenShift, Funqy, Knative |
| `extensions.md` | 12 | Extension project layout, `@BuildStep`, `@Record`, CDI proxies, config |

## Quarkus Architecture Overview

```
┌──────────────────────────────────────────────────────────────────┐
│                      QUARKUS RUNTIME                             │
│                                                                  │
│  ┌─────────────┐   ┌──────────────┐   ┌────────────────────┐   │
│  │  CDI (ArC)  │   │  RESTEasy    │   │  Vert.x (reactive  │   │
│  │  compile-   │   │  Reactive    │   │  event loop)       │   │
│  │  time proxy │   │  (JAX-RS)    │   │                    │   │
│  └─────────────┘   └──────────────┘   └────────────────────┘   │
│                                                                  │
│  Build-time augmentation ──► Bytecode generation ──► Fast boot  │
│                                                                  │
│  JVM mode: standard JDK classpath                               │
│  Native mode: GraalVM substrate, AOT, ~10ms start, low RSS      │
└──────────────────────────────────────────────────────────────────┘
```

## Quick Decision Trees

### Which mode to use?

```
Target environment?
├── Kubernetes / serverless / short-lived  → Native image (fast start, low memory)
├── Long-running service, rich reflection  → JVM mode (better peak throughput)
└── Development                            → JVM mode (fast iteration with live coding)
```

### Which programming model?

```
Workload type?
├── CPU-bound / synchronous               → Imperative (worker thread, @Blocking)
├── I/O-bound, high concurrency           → Reactive (Mutiny Uni/Multi, event loop)
├── Mixed                                 → Virtual threads (@RunOnVirtualThread)
└── Event-driven, decoupled services      → Reactive Messaging (Kafka/RabbitMQ)
```

### Which database access style?

```
Data store?
├── SQL (relational)
│   ├── Simple entities, less boilerplate  → Panache Active Record
│   ├── Separation of concerns            → Panache Repository
│   └── Full JPA control                  → Hibernate ORM (standard)
├── NoSQL
│   └── Document store                    → Panache MongoDB
└── Reactive data access                  → Hibernate Reactive + Mutiny
```

## Key Annotations Quick Reference

| Annotation | Purpose | Load |
|---|---|---|
| `@Path`, `@GET`, `@POST` | JAX-RS REST endpoints | communications.md |
| `@RegisterRestClient` | Typed REST client | communications.md |
| `@GraphQLApi`, `@Query`, `@Mutation` | GraphQL API | communications.md |
| `@GrpcService` | Inject gRPC stub | communications.md |
| `@QuarkusTest` | Integration test with running app | testing.md |
| `@NativeImageTest` | Test compiled native binary | testing.md |
| `@InjectMock` | CDI bean mock (Mockito) | testing.md |
| `@TestProfile` | Activate a test configuration profile | testing.md |
| `@TemplateExtension` | Qute template extension method | web-and-security.md |
| `@RolesAllowed`, `@Authenticated` | Declarative security | web-and-security.md |
| `@Entity`, `@PanacheEntity` | JPA / Panache entity | database.md |
| `@PanacheRepository` | Repository pattern | database.md |
| `@Transactional` | Demarcate a transaction | database.md |
| `@Incoming`, `@Outgoing` | Reactive Messaging channel | messaging.md |
| `@Liveness`, `@Readiness` | Health check probes | cloud-native-patterns.md |
| `@Fallback`, `@Retry`, `@CircuitBreaker` | Fault tolerance | cloud-native-patterns.md |
| `@BuildStep` | Extension build-time processor | extensions.md |
| `@Record(STATIC_INIT)` | Extension runtime recorder | extensions.md |
