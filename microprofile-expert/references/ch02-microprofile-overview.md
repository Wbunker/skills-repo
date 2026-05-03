# Chapter 2: MicroProfile Overview

## History and Evolution

MicroProfile was created in 2016 as a vendor-neutral open-source initiative under the Eclipse Foundation. It began as a community response to the heavyweight nature of Java EE, optimizing a baseline Java EE subset for microservices.

Key milestones:
- **2016** — MicroProfile 1.0: CDI, JAX-RS, JSON-P
- **2019** — MicroProfile 3.x: stable core, Fault Tolerance, Health, Metrics, OpenTracing, JWT, OpenAPI, Rest Client, Config
- **2021** — MicroProfile 4.1 (covered by this book): adds Context Propagation, Reactive Messaging, GraphQL, LRA (standalone)
- **Ongoing** — Standalone specs can release independently of the platform umbrella

## Platform Specifications (MicroProfile 4.1 Umbrella)

| Specification | Purpose |
|---------------|---------|
| CDI 2.0 | Dependency injection and lifecycle management |
| JAX-RS 2.1 | RESTful web services |
| JSON-B 1.0 | JSON binding (object ↔ JSON) |
| JSON-P 1.1 | JSON processing (streaming/builder API) |
| MicroProfile Config 2.0 | Externalized configuration |
| MicroProfile Fault Tolerance 3.0 | Resilience patterns |
| MicroProfile Health 3.1 | Health check endpoints |
| MicroProfile JWT 1.2 | JSON Web Token authentication |
| MicroProfile Metrics 3.0 | Application and runtime metrics |
| MicroProfile OpenAPI 2.0 | OpenAPI v3 documentation |
| MicroProfile OpenTracing 2.0 | Distributed request tracing |
| MicroProfile Rest Client 2.0 | Type-safe HTTP client |

## Standalone Specifications

These specs release independently; they may not be part of the platform umbrella:

- **MicroProfile Context Propagation 1.2** — thread context across async boundaries
- **MicroProfile Reactive Messaging 2.0** — event-driven messaging (Kafka, AMQP)
- **MicroProfile GraphQL 1.1** — GraphQL server API
- **MicroProfile LRA 1.0** — long-running actions / saga pattern

## MicroProfile vs. Jakarta EE

MicroProfile complements Jakarta EE. MicroProfile builds on Jakarta EE core (CDI, JAX-RS, JSON-B, JSON-P) and adds cloud-native concerns. Runtimes like Open Liberty, Quarkus, Payara Micro, Helidon, and TomEE all implement both.

## MicroProfile Starter

`https://start.microprofile.io` — web UI for generating a project skeleton. Select:
- MicroProfile version
- Runtime (Open Liberty, Quarkus, etc.)
- Specifications to include

Generates a Maven project with `pom.xml`, `microprofile-config.properties`, and sample code.

## Maven Dependency

```xml
<dependency>
    <groupId>org.eclipse.microprofile</groupId>
    <artifactId>microprofile</artifactId>
    <version>4.1</version>
    <type>pom</type>
    <scope>provided</scope>
</dependency>
```

The `provided` scope is critical — the runtime supplies the implementation; do not bundle it in your WAR/JAR.
