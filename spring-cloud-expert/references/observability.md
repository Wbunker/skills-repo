---
name: observability
description: Distributed tracing with Spring Cloud Sleuth and Zipkin, trace/span IDs, correlation ID propagation, MDC logging, log aggregation with ELK, custom spans. Chapter 9 of Spring Microservices in Action.
type: reference
---

# Distributed Tracing: Sleuth and Zipkin

## The Observability Problem

A single user request in a microservice system may fan out across 5+ services. When it fails or is slow:
- Which service is the culprit?
- What was the call chain?
- How long did each hop take?

Without distributed tracing, answering these questions requires manually correlating logs across multiple services — painful and slow.

---

## Spring Cloud Sleuth

Sleuth automatically instruments Spring components (RestTemplate, Feign, `@Async`, messaging) to:
1. **Generate trace IDs** — unique per logical request, shared across all hops
2. **Generate span IDs** — unique per segment (one service's portion)
3. **Inject IDs into MDC** — so every log line includes `[traceId, spanId]`
4. **Propagate via HTTP headers** — `X-B3-TraceId`, `X-B3-SpanId`, `X-B3-ParentSpanId`

### Dependencies

```xml
<dependency>
    <groupId>org.springframework.cloud</groupId>
    <artifactId>spring-cloud-starter-sleuth</artifactId>
</dependency>
```

With Zipkin export:
```xml
<dependency>
    <groupId>org.springframework.cloud</groupId>
    <artifactId>spring-cloud-sleuth-zipkin</artifactId>
</dependency>
```

> **Note (Spring Boot 3):** Sleuth is replaced by [Micrometer Tracing](https://micrometer.io/docs/tracing) + `micrometer-tracing-bridge-brave` + `zipkin-reporter-brave`. The concepts are identical; only the artifact names changed.

---

## Trace / Span Model

```
User Request (traceId: abc123)
│
├── license-service (spanId: 001)
│   ├── Feign call → organization-service (spanId: 002, parentSpanId: 001)
│   │   └── DB query (spanId: 003, parentSpanId: 002)
│   └── Redis lookup (spanId: 004, parentSpanId: 001)
│
└── Response assembled
```

Every log line emitted during this flow includes `[abc123, 001]` or `[abc123, 002]` etc., making log correlation trivial.

---

## Log Format with Sleuth

Sleuth patches the Logback MDC. After adding Sleuth, log lines automatically look like:

```
2024-01-15 10:23:45.123  INFO [license-service,abc123def456,001aabb] 12345 --- [http-nio-8080-exec-1] c.e.l.LicenseController : Getting license for org org-123
```

Format: `[application-name, traceId, spanId]`

### Logback Pattern (application.yml)
```yaml
logging:
  pattern:
    console: "%d{yyyy-MM-dd HH:mm:ss} %-5level [%X{traceId},%X{spanId}] %logger{36} - %msg%n"
```

---

## Configuration

```yaml
spring:
  application:
    name: license-service

  sleuth:
    sampler:
      probability: 1.0    # 1.0 = 100% sampling; use 0.1 in production
    propagation:
      type: B3            # B3 headers (Zipkin standard) or W3C

  zipkin:
    base-url: http://zipkin:9411
    sender:
      type: web           # HTTP sender; or 'kafka', 'rabbit' for async
```

---

## Zipkin Server

Zipkin receives and stores spans, then provides a UI for trace search.

### Run via Docker
```bash
docker run -d -p 9411:9411 openzipkin/zipkin
```

Or with Docker Compose:
```yaml
zipkin:
  image: openzipkin/zipkin
  ports:
    - "9411:9411"
```

### Zipkin UI
- `http://zipkin:9411` — search by service, trace ID, time range, duration
- Click a trace to see the full span waterfall
- Hover a span to see tags, logs, and timing

### Async Transport (Kafka)
In production, avoid synchronous HTTP span export — it adds latency to each service call.

```xml
<dependency>
    <groupId>org.springframework.kafka</groupId>
    <artifactId>spring-kafka</artifactId>
</dependency>
```

```yaml
spring:
  zipkin:
    sender:
      type: kafka
  kafka:
    bootstrap-servers: kafka:9092
```

Zipkin reads from the `zipkin` Kafka topic.

---

## Custom Spans

Add application-level spans to instrument business logic:

```java
@Service
public class LicenseService {

    private final Tracer tracer;

    public LicenseService(Tracer tracer) {
        this.tracer = tracer;
    }

    public License getLicense(String licenseId, String organizationId) {
        Span newSpan = tracer.nextSpan().name("readLicenseDBCall").start();
        try (Tracer.SpanInScope ws = tracer.withSpanInScope(newSpan)) {
            newSpan.tag("licenseId", licenseId);
            return licenseRepository.findById(licenseId).orElseThrow();
        } finally {
            newSpan.finish();
        }
    }
}
```

This creates a child span visible in Zipkin's waterfall under the parent service span.

---

## Correlation ID vs. Trace ID

| | Correlation ID | Sleuth Trace ID |
|-|---------------|-----------------|
| Origin | Your code (gateway filter) | Sleuth auto-generates |
| Propagation | Custom HTTP header | `X-B3-TraceId` header |
| Purpose | Business request tracking, custom logging | Zipkin span correlation |
| Storage | MDC + response header | MDC + Zipkin |

Use both: correlation ID for business logs; trace ID for Zipkin.

---

## Log Aggregation with ELK

### Architecture
```
Service A logs → Logstash (parse) → Elasticsearch (store) → Kibana (visualize)
Service B logs →/
Service C logs →/
```

### Logback JSON Output (for Logstash)

```xml
<!-- logback-spring.xml -->
<appender name="JSON" class="ch.qos.logback.core.ConsoleAppender">
    <encoder class="net.logstash.logback.encoder.LogstashEncoder">
        <includeMdcKeyName>traceId</includeMdcKeyName>
        <includeMdcKeyName>spanId</includeMdcKeyName>
        <includeMdcKeyName>correlationId</includeMdcKeyName>
    </encoder>
</appender>
```

### Kibana Query by Trace ID
```
traceId: "abc123def456"
```
Returns all log lines across all services for that trace.

---

## Sampling Strategy

| Environment | Probability | Reason |
|-------------|-------------|--------|
| Development | `1.0` | Trace everything |
| Staging | `1.0` | Full visibility for testing |
| Production | `0.05`–`0.1` | 5-10% keeps Zipkin storage manageable |

Use `AlwaysSampler` for specific endpoints (health checks: never; payment: always):

```java
@Bean
public Sampler defaultSampler() {
    return Sampler.ALWAYS_SAMPLE;
}
```

Or configure per-path sampling with a custom `SamplerFunction<HttpRequest>`.

---

## Troubleshooting

| Issue | Check |
|-------|-------|
| No traces in Zipkin | `spring.zipkin.base-url` correct? `spring.sleuth.sampler.probability > 0`? |
| Trace ID missing from logs | Sleuth on classpath? Not using plain `new Thread()` (use `@Async`)? |
| Spans not connected | Feign/RestTemplate used? (direct HTTP clients skip propagation) |
| Too many spans in Zipkin | Reduce `sampler.probability` in production |
| Trace broken at async boundary | Use `TraceRunnable`/`TraceCallable` wrappers or `@Async` (Sleuth instruments it) |
