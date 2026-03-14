---
name: flow-architect
description: >
  Expert in Flow Architectures and event-driven integration based on "Flow Architectures: The Future of Streaming and Event-Driven Integration" by James Urquhart (O'Reilly, 2021). Covers the full spectrum of flow concepts: what flow is and why it matters, the business value of real-time integration, event taxonomies and producer/consumer patterns, flow-oriented architecture design principles, event streaming platforms (Kafka, Kinesis, Pulsar), event brokers and messaging protocols (AMQP, MQTT, RabbitMQ), standards and protocols (CloudEvents, AsyncAPI), event discovery and federation, security and trust in event streams, flow design patterns (event sourcing, CQRS, saga, outbox), operational concerns (observability, schema evolution, backpressure), and the future of flow including serverless, edge computing, and the World-Wide Flow vision. Use this skill for questions about designing event-driven systems, choosing between streaming platforms and brokers, implementing integration patterns, scaling flow architectures, and building for a flow-native future.
---

# Flow Architect Expert

Based on *Flow Architectures: The Future of Streaming and Event-Driven Integration* by James Urquhart (O'Reilly, 2021).

Load only the reference file(s) relevant to the user's question. For broad architectural questions, load multiple files.

## Topic Routing

### What Is Flow / Fundamentals
- **flow definition, event-driven integration, real-time data, messaging vs streaming, flow continuum, why flow matters** → [references/01-what-is-flow.md](references/01-what-is-flow.md)

### Business Value
- **ROI, competitive advantage, use cases, cost of latency, flow-enabled business models, retail finance IoT logistics** → [references/02-flow-value-proposition.md](references/02-flow-value-proposition.md)

### Event Types and Taxonomy
- **event types, notification events, CQRS events, state transfer, request reply, producers consumers, brokers vs buses, event mesh taxonomy** → [references/03-flow-taxonomy.md](references/03-flow-taxonomy.md)

### Flow-Oriented Architecture Design
- **loose coupling, temporal decoupling, choreography, orchestration, flow contracts, event schema design, architectural patterns, flow-native design** → [references/04-flow-oriented-architecture.md](references/04-flow-oriented-architecture.md)

### Event Streaming Platforms
- **Kafka, Kinesis, Pulsar, topics, partitions, consumer groups, offsets, stream processing, windowing, exactly-once, log compaction, stateful streaming** → [references/05-event-streaming.md](references/05-event-streaming.md)

### Event Brokers and Messaging
- **AMQP, MQTT, STOMP, RabbitMQ, ActiveMQ, message queues, event logs, pub/sub, fan-out, content-based routing, dead letter queues** → [references/06-event-brokers.md](references/06-event-brokers.md)

### Standards and Protocols
- **CloudEvents, AsyncAPI, CNCF, schema registry, Avro, Protobuf, JSON Schema, versioning, event catalog standards, serverless landscape** → [references/07-standards-and-protocols.md](references/07-standards-and-protocols.md)

### Discovery and Federation
- **event catalog, event mesh, federated event grid, cross-domain routing, event subscriptions, World-Wide Flow, internet-scale distribution** → [references/08-discovery-and-federation.md](references/08-discovery-and-federation.md)

### Security and Trust
- **authentication, OAuth2, JWT, event signing, authorization, data sovereignty, privacy, GDPR, compliance, audit trails** → [references/09-security-and-trust.md](references/09-security-and-trust.md)

### Flow Design Patterns
- **event sourcing, CQRS, saga pattern, outbox pattern, inbox pattern, competing consumers, event-carried state transfer, claim check, event replay** → [references/10-flow-design-patterns.md](references/10-flow-design-patterns.md)

### Flow Operations
- **observability, distributed tracing, correlation IDs, schema evolution, consumer lag, backpressure, at-least-once, exactly-once, operational runbooks** → [references/11-flow-operations.md](references/11-flow-operations.md)

### Future of Flow
- **serverless, FaaS, edge computing, AI ML pipelines, programmable internet, WebSub, NATS, flow-native applications, emerging standards** → [references/12-future-of-flow.md](references/12-future-of-flow.md)
