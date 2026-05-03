# Chapter 1: Cloud-Native Application Fundamentals

## What Makes an Application Cloud-Native

Cloud-native applications are designed to exploit cloud infrastructure — elastic scaling, automated recovery, distributed deployment — rather than simply running existing software in the cloud. They are:

- **Independently deployable** — each service can be released without coordinating with others
- **Resilient by design** — built to tolerate partial failures and recover automatically
- **Horizontally scalable** — stateless services that scale out, not up
- **Observable** — expose health, metrics, and traces to the platform

## Architecture Styles

### Microservices
Each business capability is a separate, independently deployable service. Services communicate over HTTP/REST or messaging. MicroProfile is the primary Java standard for this style.

### Monolith
All capabilities in one deployable. Suitable as a starting point; migrate to microservices when team size or deployment frequency demands it (Strangler Fig pattern).

### Macroservices
Coarser-grained than microservices. Groups related capabilities into a single service. A pragmatic middle ground when microservice overhead is too high.

### Function as a Service (FaaS)
Event-triggered, short-lived functions. No persistent runtime — platform spins up and tears down on demand. Best for sporadic, stateless workloads.

### Event Sourcing
State changes are stored as an immutable log of events; current state is derived by replaying events. Pairs well with reactive messaging (MicroProfile Reactive Messaging + Kafka).

## The Twelve-Factor App Methodology

| Factor | Principle |
|--------|-----------|
| 1. Codebase | One repo, many deploys |
| 2. Dependencies | Explicitly declare, isolate dependencies (Maven `pom.xml`) |
| 3. Config | Store config in the environment, not in code |
| 4. Backing services | Treat databases, queues, etc. as attached resources |
| 5. Build/Release/Run | Strictly separate build and run stages |
| 6. Processes | Execute the app as stateless processes |
| 7. Port binding | Export services via port binding |
| 8. Concurrency | Scale out via the process model |
| 9. Disposability | Fast startup, graceful shutdown |
| 10. Dev/prod parity | Keep dev, staging, and prod as similar as possible |
| 11. Logs | Treat logs as event streams |
| 12. Admin processes | Run admin tasks as one-off processes |

**MicroProfile alignment:**
- Factor 3 → MicroProfile Config
- Factor 9 → Health checks (liveness/readiness probes)
- Factor 11 → MicroProfile Metrics + OpenTracing

## Cloud-Native Development Best Practices

- **Design for failure**: use Fault Tolerance (retry, circuit breaker, timeout, bulkhead, fallback)
- **Externalize configuration**: never bake environment-specific values into images
- **Immutable infrastructure**: build once, deploy the same image everywhere
- **Automate everything**: CI/CD pipelines, not manual deployments
- **Observe continuously**: health endpoints, metrics, distributed traces
