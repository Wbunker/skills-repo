---
name: jboss-expert
description: JBoss/WildFly application server expertise covering the full platform ecosystem — web applications, deployment, distributed data, REST/SOAP services, integration (Camel/AMQ), security (Elytron), IoT messaging, decision management (Drools), and workflow automation (jBPM). Use when developing, deploying, configuring, or troubleshooting JBoss/WildFly applications. Based on "JBoss: Developer's Guide" by Elvadas Nono Woguia, updated for WildFly 39 / Jakarta EE 10 / MicroProfile 7.1 (2026).
---

# JBoss / WildFly Expert

Based on "JBoss: Developer's Guide" by Elvadas Nono Woguia, updated for current WildFly 39, Jakarta EE 10, and MicroProfile 7.1.

> **Note on naming:** "JBoss" refers to the broader Red Hat middleware ecosystem. The community application server is **WildFly** (v39 as of Jan 2026); the enterprise product is **JBoss EAP** (based on WildFly). Both share the same architecture.

## Platform Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                     JBOSS / WILDFLY PLATFORM                        │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                    APPLICATION LAYER                         │   │
│  │   Web Apps (WAR)  ·  EJBs (JAR)  ·  Enterprise Apps (EAR)  │   │
│  └──────────────────────────┬──────────────────────────────────┘   │
│                             │                                       │
│  ┌───────────┬──────────────┼──────────────┬───────────────────┐   │
│  │ Undertow  │  EJB/CDI     │  JPA/JDBC    │  JMS / Messaging  │   │
│  │ (HTTP)    │  Container   │  (Data)      │  (AMQ Broker)     │   │
│  └───────────┴──────────────┼──────────────┴───────────────────┘   │
│                             │                                       │
│  ┌───────────┬──────────────┼──────────────┬───────────────────┐   │
│  │ RESTEasy  │  Elytron     │  Infinispan  │  WildFly CLI /    │   │
│  │ (JAX-RS)  │  (Security)  │  (Cache/DG)  │  HAL Console      │   │
│  └───────────┴──────────────┴──────────────┴───────────────────┘   │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │               JAKARTA EE 10 + MICROPROFILE 7.1               │   │
│  └─────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘

Deployment targets:
  Standalone  ·  Domain mode  ·  Bootable JAR  ·  Container (Docker/OCI)
  Kubernetes (Helm Charts / WildFly Operator)  ·  OpenShift (S2I)
```

## Quick Reference — Load by Task

| Task | Load This Reference |
|------|---------------------|
| Platform overview, WildFly vs EAP, subsystem architecture, tooling (CLI, HAL, Maven plugin) | [ch01-ecosystem.md](references/ch01-ecosystem.md) |
| Servlets, JSF, CDI, EJB, WAR/EAR packaging, datasources, clustering | [ch02-web-applications.md](references/ch02-web-applications.md) |
| Undertow configuration, deployment descriptors, Bootable JAR, containers, Kubernetes | [ch03-undertow-deployment.md](references/ch03-undertow-deployment.md) |
| Infinispan / Red Hat Data Grid, JPA, distributed caching, JDBC | [ch04-distributed-data.md](references/ch04-distributed-data.md) |
| RESTEasy (JAX-RS), SOAP (JAX-WS), OpenAPI/Swagger, MicroProfile REST Client | [ch05-data-as-service.md](references/ch05-data-as-service.md) |
| Apache Camel, Red Hat Fuse, AMQ (ActiveMQ Artemis), Kafka/AMQ Streams | [ch06-integration.md](references/ch06-integration.md) |
| WildFly Elytron security, SSL/TLS, credential stores, RBAC, IoT/MQTT messaging | [ch07-security-iot.md](references/ch07-security-iot.md) |
| Drools, Red Hat Decision Manager, business rules, DMN, decision tables | [ch08-decisions.md](references/ch08-decisions.md) |
| jBPM, Red Hat Process Automation Manager, BPMN 2.0, human tasks, process variables | [ch09-workflows.md](references/ch09-workflows.md) |

## Reference Files

| File | Book Chapter | Topics |
|------|-------------|--------|
| `ch01-ecosystem.md` | Ch 1 | Ecosystem overview, WildFly vs EAP, subsystems, standalone vs domain, CLI, HAL console, Maven plugin, WildFly 39 features |
| `ch02-web-applications.md` | Ch 2 | Servlets, JSF, CDI, EJB, WAR/EAR/JAR packaging, datasources, JTA transactions, clustering, session replication |
| `ch03-undertow-deployment.md` | Ch 3 | Undertow server, filters, handlers, deployment descriptors, Bootable JAR, Docker, Kubernetes Helm/Operator, OpenShift S2I |
| `ch04-distributed-data.md` | Ch 4 | Infinispan, Red Hat Data Grid 8.x, JPA/Hibernate, JDBC, distributed caching strategies, JDG vs Infinispan |
| `ch05-data-as-service.md` | Ch 5 | RESTEasy, JAX-RS 3.1, JAX-WS, MicroProfile OpenAPI 4.0, MicroProfile REST Client, content negotiation |
| `ch06-integration.md` | Ch 6 | Apache Camel 4.x, Red Hat Fuse/Camel K, AMQ Broker (ActiveMQ Artemis), AMQ Streams (Kafka), EIP patterns |
| `ch07-security-iot.md` | Ch 7 | WildFly Elytron, credential stores, SSL/TLS, RBAC, JACC, MQTT (Mosquitto/AMQ), Paho client, IoT patterns |
| `ch08-decisions.md` | Ch 8 | Drools 9/10, DMN 1.4, DRL rules, decision tables, RETE/PHREAK algorithm, Red Hat Decision Services |
| `ch09-workflows.md` | Ch 9 | jBPM 7/8, BPMN 2.0, human tasks, process variables, KIE Server, Red Hat Process Automation Manager |

## Core Decision Trees

### Deployment Strategy

```
Where are you deploying?
├── Traditional server install
│   ├── Single server → Standalone mode (standalone.xml)
│   └── Multiple managed servers → Domain mode (domain.xml + host.xml)
├── Container / cloud-native
│   ├── Simple Docker → Bootable JAR (fat JAR via Maven plugin)
│   ├── Kubernetes → WildFly Helm Charts or WildFly Operator
│   └── OpenShift → S2I (Source-to-Image) templates
└── Microservices (minimal runtime)
    └── Bootable JAR with Galleon layers (include only needed subsystems)
```

### Which JBoss Middleware Product?

```
What does your application need?
├── Run Jakarta EE / MicroProfile apps → WildFly / JBoss EAP
├── Distributed in-memory cache → Infinispan / Red Hat Data Grid
├── REST or SOAP services → Built into WildFly (RESTEasy / CXF)
├── Message broker / JMS → AMQ Broker (ActiveMQ Artemis)
├── Event streaming (Kafka) → AMQ Streams
├── Application integration / ETL → Apache Camel / Red Hat Fuse
├── Business rules engine → Drools / Red Hat Decision Services
└── Process / workflow automation → jBPM / Red Hat PAM
```

### Security Model Selection

```
What are you securing?
├── HTTP endpoints (web app) → Undertow security domain via Elytron
├── EJBs → EJB security with @RolesAllowed + Elytron domain
├── Management interfaces → Management Elytron domain (not app domain)
├── Credentials / passwords → Elytron credential store (replaces vault)
├── SSL/TLS → Elytron key-store + server-ssl-context
└── External IdP / SSO → Keycloak OIDC adapter or SAML
```

## Key Version Facts (2026)

| Component | Current Version | Notes |
|-----------|----------------|-------|
| WildFly | 39 (Jan 2026) | Community server |
| JBoss EAP | 8.0 | Enterprise (based on WildFly 29+) |
| Jakarta EE | 10 (EE 11 preview) | Java SE 17/21 required |
| MicroProfile | 7.1 | In WildFly 38+ |
| Java SE | 21 (recommended) | 17 minimum |
| Infinispan | 15.x | Embedded in WildFly; standalone as Red Hat Data Grid |
| RESTEasy | 6.2.x | JAX-RS 3.1 (Jakarta) |
| Drools | 9/10 | kogito-based for cloud-native |
| jBPM | 7.74+ / 8.x | kogito-based in newer releases |

## Major Changes Since the Book (2017 → 2026)

| Book Topic | Then (2017) | Now (2026) |
|-----------|-------------|-----------|
| Microservices runtime | WildFly Swarm | Bootable JAR + containers |
| Security subsystem | PicketBox / Security Vault | WildFly Elytron + credential store |
| Java EE spec | Java EE 7/8 | Jakarta EE 10 (namespace: `jakarta.*`) |
| Data Grid | JBoss Data Grid 7.x | Red Hat Data Grid 8.x (Infinispan 14/15) |
| Integration | JBoss Fuse 6.x (OSGi) | Camel K / Red Hat Fuse 7.x (Spring Boot based) |
| Rules | JBoss BRMS | Red Hat Decision Manager → Decision Services |
| Workflow | JBoss BPM Suite | Red Hat PAM → Kogito (cloud-native) |
| Messaging | HornetQ | ActiveMQ Artemis (AMQ Broker) |
| Namespace | `javax.*` | `jakarta.*` (breaking change in EE 9+) |
