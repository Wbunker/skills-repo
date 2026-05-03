# Chapter 12: MicroProfile LRA and the Future of MicroProfile

## The Distributed Transaction Problem

In a microservices architecture, a business operation often spans multiple services (portfolio + account + trade-history). ACID transactions cannot span service boundaries — each service has its own database. Traditional 2-phase commit (2PC) is impractical across HTTP services.

**Solutions:**
- **Saga pattern**: sequence of local transactions, each with a compensating transaction
- **LRA (Long Running Actions)**: MicroProfile's saga implementation

---

## MicroProfile LRA 1.0

LRA coordinates distributed business transactions using HTTP. An LRA coordinator tracks participants; if any step fails, the coordinator triggers compensation (rollback equivalent) in all participants that have already committed.

### Participant Lifecycle Methods

| Annotation | When Called | Purpose |
|-----------|------------|---------|
| `@LRA` | On entry | Starts or joins an LRA |
| `@Complete` | LRA completes successfully | Confirm/finalize the local action |
| `@Compensate` | LRA fails or is cancelled | Undo the local action |
| `@AfterLRA` | After LRA ends (either way) | Cleanup, notification |
| `@Forget` | After compensation acknowledged | Release compensating records |
| `@Status` | Coordinator queries state | Return current participant status |
| `@Leave` | Participant withdraws | Remove from LRA |

### Example: Trade Execution LRA

```java
@Path("/trades")
@ApplicationScoped
public class TradeService {

    // Start or join an LRA on this method
    @PUT
    @Path("/execute")
    @LRA(value = LRA.Type.REQUIRED, end = false)
    public Response executeTrade(
            @HeaderParam(LRA.LRA_HTTP_CONTEXT_HEADER) URI lraId,
            Trade trade) {
        // Debit account
        accountService.debit(trade.getOwner(), trade.getCost());
        // Record trade
        tradeRepository.save(trade);
        return Response.ok(trade).build();
    }

    // Called when LRA completes successfully
    @PUT
    @Path("/complete")
    @Complete
    public Response completeTrade(
            @HeaderParam(LRA.LRA_HTTP_CONTEXT_HEADER) URI lraId) {
        tradeRepository.confirm(lraId);
        return Response.ok(ParticipantStatus.Completed.name()).build();
    }

    // Called when LRA fails — undo the trade
    @PUT
    @Path("/compensate")
    @Compensate
    public Response compensateTrade(
            @HeaderParam(LRA.LRA_HTTP_CONTEXT_HEADER) URI lraId) {
        Trade trade = tradeRepository.find(lraId);
        accountService.credit(trade.getOwner(), trade.getCost());  // refund
        tradeRepository.cancel(lraId);
        return Response.ok(ParticipantStatus.Compensated.name()).build();
    }
}
```

### LRA Types

| Type | Behavior |
|------|---------|
| `REQUIRED` | Join existing LRA or start new one |
| `REQUIRES_NEW` | Always start a new LRA |
| `MANDATORY` | Must join an existing LRA; fails if none |
| `SUPPORTS` | Join LRA if one exists; otherwise run without |
| `NOT_SUPPORTED` | Run without LRA even if one exists |
| `NEVER` | Fail if an LRA exists |

### LRA Coordinator

The LRA coordinator is a separate service (Narayana LRA Coordinator) deployed in Kubernetes:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: lra-coordinator
spec:
  template:
    spec:
      containers:
        - name: lra-coordinator
          image: quay.io/jbosstm/lra-coordinator:5.13
          ports:
            - containerPort: 8080
```

```properties
# MicroProfile Config
lra.coordinator.url=http://lra-coordinator:8080/lra-coordinator
```

### Open Liberty Feature

```xml
<featureManager>
    <feature>mpLRA-1.0</feature>
</featureManager>
```

---

## Saga vs. LRA vs. Reactive Messaging

| | Saga (choreography) | LRA (orchestration) | Reactive Messaging |
|---|---|---|---|
| Coordination | Each service reacts to events | LRA coordinator drives | None — fire and forget |
| Rollback | Compensating events | `@Compensate` callbacks | Not guaranteed |
| Coupling | Loose | Moderate (coordinator) | Very loose |
| Traceability | Harder | LRA ID tracks everything | Requires tracing |
| Use when | High throughput, eventual consistency OK | Strong consistency required | Notifications, audit logs |

---

## MicroProfile Roadmap and Future Directions

### MicroProfile 5.0+

- Aligns with Jakarta EE 9.1 (package rename: `javax.*` → `jakarta.*`)
- MicroProfile Telemetry (replaces OpenTracing with OpenTelemetry)
- MicroProfile JWT 2.0 (enhanced token propagation)

### MicroProfile Telemetry 1.0

Replaces `mpOpenTracing` with OpenTelemetry — the current industry standard:

```java
// OpenTelemetry replaces the OpenTracing Tracer
@Inject
private OpenTelemetry openTelemetry;

Tracer tracer = openTelemetry.getTracer("portfolio-service");
Span span = tracer.spanBuilder("fetch-stock-price").startSpan();
try (Scope scope = span.makeCurrent()) {
    return client.fetchQuote(symbol);
} finally {
    span.end();
}
```

### Quarkus and MicroProfile

Quarkus implements MicroProfile and compiles to native binaries (GraalVM), achieving sub-100ms startup and reduced memory footprint. Same MicroProfile annotations compile to native — no code changes required.

### Standalone Spec Release Cadence

MicroProfile standalone specs (GraphQL, LRA, Reactive Messaging, Context Propagation) release independently of the platform umbrella, allowing faster iteration. Users can pick specific versions.

### Community and Governance

- Governed by the Eclipse Foundation
- Contributions via GitHub: `https://github.com/eclipse/microprofile`
- Spec proposals: MicroProfile issue tracker
- Compatible implementations certified via TCK (Technology Compatibility Kit)

### Key Vendors

| Vendor | Runtime |
|--------|---------|
| IBM | Open Liberty |
| Red Hat | Quarkus, WildFly |
| Payara | Payara Micro |
| Oracle | Helidon |
| Apache | TomEE |
