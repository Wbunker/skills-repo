# Testing APIs

This reference covers testing strategies for API-driven architectures, drawn from Chapter 2 of *Mastering API Architecture* by James Gough. It addresses how to build confidence in API behavior across unit, integration, contract, component, and end-to-end testing layers, with guidance on when to apply each approach.

## Testing Strategies for API-Driven Architectures

APIs sit at the boundary between systems. Testing them requires strategies that go beyond verifying internal logic: you must confirm that contracts between services hold, that integrations behave correctly under realistic conditions, and that the system as a whole delivers expected outcomes. A well-designed testing strategy combines multiple layers of feedback, each with a distinct purpose and cost profile.

Two foundational models guide test strategy decisions: the Test Quadrant and the Test Pyramid.

## The Test Quadrant

The Test Quadrant, originally from Brian Marick and popularized by Lisa Crisping and Janet Gregory, classifies tests along two axes:

- **Technology-facing vs. business-facing**: Does the test verify a technical implementation detail, or does it validate a business requirement?
- **Supporting development vs. critiquing the product**: Does the test guide development (written before or during coding), or does it evaluate the finished product?

This produces four quadrants:

| | Supporting Development | Critiquing the Product |
|---|---|---|
| **Business-facing** | Q2: Functional tests, story tests, prototypes, simulations | Q3: Exploratory testing, usability testing, UAT |
| **Technology-facing** | Q1: Unit tests, component tests, integration tests | Q4: Performance tests, security tests, load tests |

For API architectures, Q1 and Q4 are where most automated investment lands. Q2 tests often manifest as contract tests that encode business expectations. Q3 remains largely manual but is critical for API usability (e.g., reviewing developer experience of an API surface). The quadrant model helps teams avoid over-investing in one area while neglecting another.

## The Test Pyramid

The Test Pyramid provides a cost and speed model for layering tests:

```
        /  E2E   \          <- Few, slow, expensive, high confidence
       /----------\
      / Integration \       <- Moderate number, moderate speed
     /--------------\
    /   Unit Tests    \     <- Many, fast, cheap, low integration confidence
   /------------------\
```

**Unit tests** form the base. They are fast, isolated, and cheap to run. For APIs, unit tests verify request parsing, validation logic, serialization, error mapping, and business rules within a single service.

**Integration tests** occupy the middle. They verify that a service correctly communicates with its dependencies: databases, message brokers, downstream APIs. They are slower and require infrastructure but catch issues that unit tests cannot.

**End-to-end tests** sit at the top. They exercise the full request path across multiple services. They provide the highest confidence but are the most expensive to write, maintain, and run.

The pyramid shape is prescriptive: you should have many unit tests, fewer integration tests, and even fewer E2E tests. In API architectures, contract tests and component tests fill important roles between unit and full integration, often reducing the need for expensive E2E tests.

### ADR: Choosing a Testing Strategy

When establishing a testing strategy, an Architecture Decision Record (ADR) captures the rationale:

- **Context**: The system comprises multiple API services with independent deployment cycles. Teams need fast feedback without sacrificing confidence in cross-service behavior.
- **Decision**: Adopt a layered strategy: unit tests for internal logic, contract tests for inter-service agreements, component tests for service-level behavior in isolation, integration tests for critical infrastructure dependencies, and a small suite of E2E smoke tests.
- **Consequences**: Teams own their contract tests. Contract breakage blocks the provider pipeline. E2E tests run in a shared staging environment on a schedule rather than per-commit.

## Contract Testing

Contract testing verifies that two services agree on the shape and semantics of their interaction without requiring both services to be running simultaneously. This makes it faster and more reliable than integration testing for validating API boundaries.

### Why Contract Testing Over Integration Testing

Integration tests that call live downstream services are brittle. They break when the downstream service is unavailable, when test data drifts, or when environments are misconfigured. Contract tests decouple the two sides: each side verifies against a shared contract artifact independently.

The key insight is that most integration failures at API boundaries are structural: a field was renamed, a status code changed, a required header was dropped. Contract tests catch exactly these failures without the operational overhead of running multiple services together.

### Consumer-Driven Contract Testing with Pact

In consumer-driven contract testing, the consumer (the service calling the API) defines its expectations. The provider then verifies it can meet those expectations.

**Step 1: Consumer writes expectations.** The consumer test declares what request it will send and what response it expects:

```java
// Consumer side (Pact JVM)
@Pact(consumer = "OrderService", provider = "InventoryService")
public RequestResponsePact checkInventory(PactDslWithProvider builder) {
    return builder
        .given("product SKU-123 is in stock")
        .uponReceiving("a request to check inventory")
            .path("/inventory/SKU-123")
            .method("GET")
        .willRespondWith()
            .status(200)
            .body(newJsonBody(body -> {
                body.stringType("sku", "SKU-123");
                body.integerType("quantity", 42);
                body.booleanType("available", true);
            }).build())
        .toPact();
}
```

This generates a contract file (a Pact JSON artifact) that captures the interaction.

**Step 2: Provider verifies.** The provider runs the contract against its actual implementation:

```java
// Provider side
@Provider("InventoryService")
@PactBroker(url = "https://pact-broker.internal")
public class InventoryProviderTest {
    @TestTemplate
    @ExtendWith(PactVerificationInvocationContextProvider.class)
    void verifyPact(PactVerificationContext context) {
        context.verifyInteraction();
    }

    @State("product SKU-123 is in stock")
    void setupInventory() {
        inventoryRepository.save(new Product("SKU-123", 42, true));
    }
}
```

If the provider cannot satisfy the consumer's expectations, the verification fails. This failure happens in the provider's CI pipeline, giving the provider team immediate feedback before deployment.

### Provider-Driven Contracts

In some cases, the provider defines the contract. This is common when a single API serves many consumers and the provider team wants to control the API surface. The provider publishes a contract (often an OpenAPI specification), and consumers validate their usage against it. Provider-driven contracts are simpler to manage but offer less protection against provider changes that break specific consumer usage patterns.

### Schema-Based Contract Testing

Schema-based approaches use an API specification (OpenAPI, JSON Schema, Protobuf) as the contract. Tools like Schemathesis or Dredd generate tests from the schema and run them against the live API. This validates that the implementation matches the documented specification but does not capture consumer-specific interaction patterns the way Pact does.

```bash
# Validate an API against its OpenAPI spec using Schemathesis
schemathesis run --url http://localhost:8080/openapi.json --checks all
```

### ADR: Contract Testing Decisions

- **Context**: Three consumer services depend on the Payment API. Breaking changes have caused production incidents twice in the past quarter.
- **Decision**: Adopt consumer-driven contract testing with Pact. Each consumer publishes contracts to a Pact Broker. The Payment API provider pipeline verifies all consumer contracts before deployment.
- **Consequences**: Consumer teams must maintain their contract tests. The Pact Broker becomes shared infrastructure. Provider deployments are gated on contract verification, which may slow releases if contracts are stale.

## API Component Testing

Component testing exercises a single service in isolation, with its external dependencies replaced by stubs or in-memory substitutes. The service is started as a real process (or in-process with a test framework), and tests send HTTP requests to its actual endpoints.

This differs from contract testing in scope: contract tests verify the shape of interactions, while component tests verify the service's behavior, including business logic, error handling, data transformation, and state management.

### When to Use Each

| Concern | Contract Testing | Component Testing |
|---|---|---|
| Cross-service API shape | Yes | No |
| Single-service business logic | No | Yes |
| Error handling and edge cases | Limited | Yes |
| Requires running the service | No (consumer side) | Yes |
| Catches internal regressions | No | Yes |

### Case Study: Verifying Behavior

Consider an order service that applies discount rules, validates inventory, and calculates tax. A component test starts the service with a stubbed inventory client and an in-memory database, then verifies:

```java
@SpringBootTest(webEnvironment = WebEnvironment.RANDOM_PORT)
public class OrderComponentTest {

    @Autowired
    private TestRestTemplate restTemplate;

    @MockBean
    private InventoryClient inventoryClient;

    @Test
    void applyDiscountForBulkOrder() {
        when(inventoryClient.check("SKU-100")).thenReturn(new Stock("SKU-100", 500));

        OrderRequest request = new OrderRequest("SKU-100", 50);
        ResponseEntity<OrderResponse> response =
            restTemplate.postForEntity("/orders", request, OrderResponse.class);

        assertThat(response.getStatusCode()).isEqualTo(HttpStatus.CREATED);
        assertThat(response.getBody().getDiscount()).isEqualTo(BigDecimal.valueOf(0.10));
    }
}
```

This test verifies that the bulk discount logic works correctly without depending on a live inventory service. It exercises the real HTTP layer, routing, serialization, and business logic of the order service.

## API Integration Testing

Integration tests verify that a service communicates correctly with real external dependencies. Unlike component tests that stub dependencies, integration tests use actual (or containerized) instances of databases, message brokers, and third-party APIs.

### Stub Servers: WireMock and MockServer

When testing against downstream HTTP APIs, stub servers simulate the dependency:

```java
// WireMock example
@WireMockTest(httpPort = 9091)
class PaymentGatewayIntegrationTest {

    @Test
    void processPaymentSuccessfully(WireMockRuntimeInfo wmInfo) {
        stubFor(post(urlPathEqualTo("/charges"))
            .withRequestBody(matchingJsonPath("$.amount"))
            .willReturn(okJson("{\"id\": \"ch_123\", \"status\": \"succeeded\"}")));

        PaymentResult result = paymentClient.charge(new Money(50, "USD"));
        assertThat(result.getStatus()).isEqualTo("succeeded");
    }
}
```

WireMock and MockServer support request matching, response templating, fault injection (delays, connection resets), and stateful scenarios. They are useful for testing retry logic, timeout handling, and error recovery against downstream APIs without needing the real service.

### Testcontainers

Testcontainers provides lightweight, disposable containers for integration test dependencies. Instead of maintaining shared test databases or message brokers, each test run starts fresh containers:

```java
@Testcontainers
@SpringBootTest
class OrderRepositoryIntegrationTest {

    @Container
    static PostgreSQLContainer<?> postgres =
        new PostgreSQLContainer<>("postgres:15")
            .withDatabaseName("orders")
            .withUsername("test")
            .withPassword("test");

    @DynamicPropertySource
    static void configureProperties(DynamicPropertyRegistry registry) {
        registry.add("spring.datasource.url", postgres::getJdbcUrl);
        registry.add("spring.datasource.username", postgres::getUsername);
        registry.add("spring.datasource.password", postgres::getPassword);
    }

    @Test
    void persistAndRetrieveOrder() {
        Order order = new Order("SKU-100", 5, BigDecimal.valueOf(49.99));
        orderRepository.save(order);

        Optional<Order> found = orderRepository.findBySku("SKU-100");
        assertThat(found).isPresent();
        assertThat(found.get().getQuantity()).isEqualTo(5);
    }
}
```

Testcontainers supports PostgreSQL, MySQL, MongoDB, Kafka, Redis, RabbitMQ, Elasticsearch, and many other services. Tests are reproducible across developer machines and CI because the container version is pinned.

### ADR: Integration Testing Decisions

- **Context**: The service writes to PostgreSQL and publishes events to Kafka. Shared test environments are unreliable and cause flaky tests.
- **Decision**: Use Testcontainers for PostgreSQL and Kafka in integration tests. Use WireMock for downstream HTTP API dependencies.
- **Consequences**: CI builds require Docker. Test execution time increases by 10-20 seconds for container startup. Tests are fully isolated and reproducible.

## End-to-End Testing

End-to-end tests validate the complete request flow across multiple services and infrastructure components. They provide the highest confidence that the system works as a whole but are the most expensive to create and maintain.

### Types of E2E Tests

**Smoke tests** verify that critical paths are functional after deployment. They are lightweight and fast:

```bash
# Smoke test: verify the API is reachable and authentication works
curl -sf -o /dev/null -w "%{http_code}" \
  -H "Authorization: Bearer $TOKEN" \
  https://api.example.com/health
# Expected: 200
```

**Journey tests** simulate realistic user workflows across multiple API calls:

1. Create a customer account (POST /customers)
2. Add items to a cart (POST /carts/{id}/items)
3. Submit an order (POST /orders)
4. Verify order status (GET /orders/{id})
5. Process payment webhook (POST /webhooks/payment)
6. Confirm order completion (GET /orders/{id} returns status "completed")

**Performance tests** measure latency, throughput, and resource consumption under load. These typically use dedicated tools (see Performance Testing below).

### The Cost of E2E Tests

E2E tests are expensive because they require a fully deployed environment, are slow to execute, are brittle (any service failure causes test failure), and are difficult to debug when they fail. Teams should minimize E2E tests and prefer contract and component tests for most coverage. Reserve E2E tests for validating critical business flows that span multiple services and cannot be adequately covered by lower-level tests.

### ADR: E2E Testing Decisions

- **Context**: The checkout flow spans five services. Contract tests cover individual API boundaries, but the team lacks confidence that the full flow works after deployment.
- **Decision**: Implement a small suite of journey tests (fewer than 10) covering the primary checkout path. Run them against the staging environment after each deployment. Do not run them per-commit.
- **Consequences**: A dedicated staging environment must remain stable. Flaky tests are investigated immediately rather than tolerated. The suite is owned by the platform team, not individual service teams.

## Testing Streaming and Async APIs

Streaming and asynchronous APIs require testing approaches beyond request-response patterns.

For **message-driven APIs** (Kafka, RabbitMQ, AMQP), test that producers emit correctly structured messages and that consumers handle them properly. Testcontainers with an embedded broker makes this practical:

```java
@Container
static KafkaContainer kafka = new KafkaContainer(
    DockerImageName.parse("confluentinc/cp-kafka:7.4.0"));

@Test
void orderEventPublishedOnCreation() {
    // Trigger order creation via the API
    restTemplate.postForEntity("/orders", orderRequest, Void.class);

    // Consume from the topic and verify the event
    ConsumerRecord<String, String> record =
        KafkaTestUtils.getSingleRecord(consumer, "order-events");
    OrderEvent event = objectMapper.readValue(record.value(), OrderEvent.class);
    assertThat(event.getType()).isEqualTo("ORDER_CREATED");
    assertThat(event.getSku()).isEqualTo("SKU-100");
}
```

For **WebSocket and SSE (Server-Sent Events) APIs**, tests establish a connection, send messages, and assert on the stream of received events. Test both the happy path and disconnection/reconnection behavior.

For **gRPC streaming**, test unary calls like REST, but also test client-streaming, server-streaming, and bidirectional-streaming RPCs. Verify behavior when streams are cancelled, when backpressure occurs, and when the connection drops mid-stream.

Contract testing for async APIs is supported by Pact (via the message pact interaction type) and by AsyncAPI specifications with associated validation tooling.

## Performance and Load Testing

Performance testing validates that APIs meet latency and throughput requirements under expected and peak load. Key test types:

- **Load tests**: Sustained traffic at expected production levels to measure steady-state latency percentiles (p50, p95, p99) and throughput.
- **Stress tests**: Traffic beyond expected capacity to identify breaking points and degradation behavior.
- **Soak tests**: Extended-duration load to detect memory leaks, connection pool exhaustion, and other time-dependent failures.
- **Spike tests**: Sudden bursts of traffic to validate autoscaling and queuing behavior.

Tools like Gatling, k6, and Apache JMeter are commonly used:

```javascript
// k6 load test example
import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
    stages: [
        { duration: '2m', target: 100 },   // ramp up
        { duration: '5m', target: 100 },   // sustain
        { duration: '2m', target: 0 },     // ramp down
    ],
    thresholds: {
        http_req_duration: ['p(95)<300'],   // 95th percentile under 300ms
        http_req_failed: ['rate<0.01'],     // less than 1% errors
    },
};

export default function () {
    const res = http.get('https://api.example.com/products');
    check(res, { 'status is 200': (r) => r.status === 200 });
    sleep(1);
}
```

Performance test results should be baselined and tracked over time. Regressions should be investigated before deployment, ideally caught in CI.

## API Testing Tools

A summary of widely used tools across ecosystems:

| Tool | Language/Ecosystem | Strengths |
|---|---|---|
| **REST Assured** | Java | Fluent API for HTTP assertions, strong JSON/XML path support, integrates with JUnit |
| **Pact** | Polyglot (JVM, JS, Ruby, Go, .NET, Python) | Consumer-driven contract testing, Pact Broker for contract management |
| **WireMock** | Java (standalone available) | HTTP stub server, request matching, fault simulation, record/playback |
| **MockServer** | Java (standalone available) | Similar to WireMock, supports expectations and verification |
| **Testcontainers** | Java, .NET, Go, Python, Node.js | Disposable Docker containers for test dependencies |
| **Karate** | JVM (standalone DSL) | BDD-style API testing, built-in assertions, no Java coding required |
| **Postman/Newman** | Standalone/CLI | Collection-based API testing, shareable across teams, CI via Newman |
| **pytest + requests/httpx** | Python | Lightweight, flexible, strong fixture model, pairs well with hypothesis for property testing |
| **supertest** | Node.js | HTTP assertions for Express/Koa apps, integrates with Jest and Mocha |
| **Schemathesis** | Python | Property-based testing generated from OpenAPI specs |
| **k6** | Go (JS scripting) | Performance testing with developer-friendly scripting |
| **Gatling** | Scala/Java | High-performance load testing with detailed reporting |
| **Dredd** | Node.js | Validates API implementation against API Blueprint or OpenAPI specs |

The choice of tool depends on language ecosystem, team familiarity, and the specific testing layer. Most teams benefit from combining several: a contract testing tool (Pact), a stub server (WireMock), a container tool (Testcontainers), and a performance testing tool (k6 or Gatling).

## Summary

A robust API testing strategy layers multiple test types, each with a distinct cost-confidence tradeoff. Unit tests provide fast feedback on internal logic. Contract tests catch cross-service breakage without requiring integrated environments. Component tests verify service behavior in isolation. Integration tests with Testcontainers and stub servers validate real infrastructure interactions. E2E tests, used sparingly, confirm critical business flows across the full system. ADRs document the rationale behind testing strategy choices, making them reviewable and revisitable as the architecture evolves.
