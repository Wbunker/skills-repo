# Stream Processing with Kafka Streams
## Chapters 13–14: Kafka Streams API, Stateful/Stateless Ops, Windowing, Exactly-Once

---

## What Is Stream Processing?

Stream processing operates on data **continuously as it arrives**, rather than in scheduled batches. Kafka Streams is a Java library (not a separate cluster) for building stream processing applications on top of Kafka.

```
Traditional Batch:                  Stream Processing:
──────────────────                  ──────────────────
Collect data → Store → Process →    Process record as it arrives
Result at scheduled interval        Results updated continuously
Minutes to hours of latency         Milliseconds to seconds of latency
```

### When to Use Kafka Streams vs. Alternatives

| Option | Best For |
|--------|---------|
| **Kafka Streams** | Java/Kotlin apps; embedded in microservices; no separate cluster needed |
| **ksqlDB** | SQL-based stream processing; interactive queries; data team users |
| **Apache Flink** | Very large-scale; complex event processing; heavy stateful ops |
| **Spark Structured Streaming** | Existing Spark ecosystem; micro-batch acceptable |

---

## Kafka Streams Architecture

Kafka Streams runs **inside your application process** — there is no separate streaming cluster to manage:

```
Your Application
┌──────────────────────────────────────────────────────┐
│                   Kafka Streams                       │
│  ┌────────────────────────────────────────────────┐  │
│  │              Stream Processing Topology         │  │
│  │                                                 │  │
│  │  Source Processor                               │  │
│  │       ↓                                         │  │
│  │  Stateless Ops (filter, map, flatMap)           │  │
│  │       ↓                                         │  │
│  │  Stateful Ops (aggregate, join, window)         │  │
│  │       ↓                                         │  │
│  │  Sink Processor                                 │  │
│  └────────────────────────────────────────────────┘  │
│                                                       │
│  State Stores (RocksDB on local disk + changelog      │
│                topic in Kafka for fault tolerance)    │
└──────────────────────────────────────────────────────┘
        ↑ reads                          ↓ writes
   Kafka Source Topics             Kafka Sink Topics
```

**Scalability**: Run multiple instances of the application with the same `application.id`. Kafka Streams distributes partitions (and their state stores) across instances automatically.

---

## Getting Started

### Dependencies

```xml
<dependency>
    <groupId>org.apache.kafka</groupId>
    <artifactId>kafka-streams</artifactId>
    <version>3.7.0</version>
</dependency>
```

### Basic Application

```java
Properties props = new Properties();
props.put(StreamsConfig.APPLICATION_ID_CONFIG, "order-processor");
props.put(StreamsConfig.BOOTSTRAP_SERVERS_CONFIG, "broker:9092");
props.put(StreamsConfig.DEFAULT_KEY_SERDE_CLASS_CONFIG, Serdes.String().getClass());
props.put(StreamsConfig.DEFAULT_VALUE_SERDE_CLASS_CONFIG, Serdes.String().getClass());

StreamsBuilder builder = new StreamsBuilder();

// Define topology
KStream<String, String> orders = builder.stream("orders");
orders
    .filter((key, value) -> value.contains("CONFIRMED"))
    .mapValues(value -> value.toUpperCase())
    .to("confirmed-orders");

// Build and start
KafkaStreams streams = new KafkaStreams(builder.build(), props);
streams.start();

// Graceful shutdown
Runtime.getRuntime().addShutdownHook(new Thread(streams::close));
```

---

## Core Abstractions

### KStream — Record Stream

A `KStream` represents an **unbounded stream of records**. Each record is an independent event.

```java
KStream<String, Order> orders = builder.stream("orders",
    Consumed.with(Serdes.String(), orderSerde));

// Stateless operations
KStream<String, Order> filtered = orders
    .filter((key, order) -> order.getAmount() > 100.0)
    .mapValues(order -> enrichOrder(order))
    .selectKey((key, order) -> order.getCustomerId());

// Split stream
orders.split()
    .branch((key, order) -> "US".equals(order.getRegion()), Branched.withConsumer(
        usOrders -> usOrders.to("us-orders")))
    .branch((key, order) -> "EU".equals(order.getRegion()), Branched.withConsumer(
        euOrders -> euOrders.to("eu-orders")));
```

### KTable — Changelog Stream (Materialized View)

A `KTable` represents the **latest value per key** — like a database table updated by a stream of changes.

```java
KTable<String, Order> latestOrderPerCustomer = builder.table("orders",
    Consumed.with(Serdes.String(), orderSerde),
    Materialized.as("latest-order-store"));

// KTable updates: only the latest value per key is retained
// Reading by key: O(1) lookup
```

**Key difference**:
- `KStream`: every record is processed (stream of events)
- `KTable`: only the latest record per key is retained (current state)

### GlobalKTable

A `GlobalKTable` is replicated to **all stream processing instances** — useful for small lookup tables (e.g., product catalog, user profile).

```java
GlobalKTable<String, Product> products = builder.globalTable("products",
    Consumed.with(Serdes.String(), productSerde));

// Join stream with global table (no co-partitioning required)
KStream<String, EnrichedOrder> enriched = orders.join(products,
    (orderKey, order) -> order.getProductId(),    // key extractor
    (order, product) -> enrich(order, product));  // value joiner
```

---

## Stateless Operations

Stateless operations process each record independently — no memory of prior records:

```java
// filter: keep records matching predicate
stream.filter((k, v) -> v.getStatus().equals("ACTIVE"))

// filterNot: keep records NOT matching predicate
stream.filterNot((k, v) -> v.isDeleted())

// map: transform key and value
stream.map((k, v) -> new KeyValue<>(v.getId(), transform(v)))

// mapValues: transform only the value (key unchanged)
stream.mapValues(v -> v.toUpperCase())

// flatMap: one record → zero or more records
stream.flatMap((k, v) -> splitOrder(v).stream()
    .map(line -> new KeyValue<>(k, line))
    .collect(Collectors.toList()))

// selectKey: change the key (triggers repartition if followed by stateful op)
stream.selectKey((k, v) -> v.getCustomerId())

// peek: observe records without modifying (logging, metrics)
stream.peek((k, v) -> log.info("Processing: {}", k))

// merge: combine two streams into one
KStream<String, Order> merged = stream1.merge(stream2)
```

---

## Stateful Operations

### Aggregations

```java
// Group by key (required before aggregating)
KGroupedStream<String, Order> groupedByCustomer = orders
    .groupByKey();  // or .groupBy(keyExtractor)

// Count records per key
KTable<String, Long> orderCount = groupedByCustomer
    .count(Materialized.as("order-count-store"));

// Aggregate with custom logic
KTable<String, OrderSummary> summary = groupedByCustomer
    .aggregate(
        OrderSummary::new,                             // initializer
        (key, order, summary) -> summary.add(order),  // aggregator
        Materialized.<String, OrderSummary, KeyValueStore<Bytes, byte[]>>
            as("order-summary-store")
            .withValueSerde(orderSummarySerde));
```

### Joins

**Stream-Stream Join** (both sides are KStream):
```java
KStream<String, Payment> payments = builder.stream("payments");
KStream<String, Order> orders = builder.stream("orders");

// Join orders with payments within 5 minutes
KStream<String, Invoice> invoices = orders.join(
    payments,
    (order, payment) -> new Invoice(order, payment),
    JoinWindows.ofTimeDifferenceWithNoGrace(Duration.ofMinutes(5)),
    StreamJoined.with(Serdes.String(), orderSerde, paymentSerde));
```

**Stream-Table Join** (enrich stream records with table lookup):
```java
KStream<String, EnrichedOrder> enriched = orders.join(
    customerTable,                      // KTable
    (order, customer) -> enrich(order, customer));
// No window needed; latest table value used for each stream record
```

**Table-Table Join** (combine two tables):
```java
KTable<String, CustomerProfile> joined = customerTable.join(
    addressTable,
    (customer, address) -> new CustomerProfile(customer, address));
```

**Co-partitioning requirement**: Stream-stream and stream-table joins require input topics to have the **same number of partitions** and records with the **same key to be in the same partition**. Use `selectKey()` and allow repartitioning if needed.

---

## Windowing

Windowing groups records by time for aggregations:

### Tumbling Windows (Fixed, Non-Overlapping)

```java
// Count orders per customer per hour
KTable<Windowed<String>, Long> hourlyOrderCount = orders
    .groupByKey()
    .windowedBy(TimeWindows.ofSizeWithNoGrace(Duration.ofHours(1)))
    .count(Materialized.as("hourly-count-store"));
```

```
Timeline:  [---window 1---][---window 2---][---window 3---]
           |               |               |
           00:00           01:00           02:00
```

### Hopping Windows (Fixed Size, Overlapping)

```java
// 1-hour window, advancing every 15 minutes (4 windows overlap)
TimeWindows.ofSizeAndGrace(Duration.ofHours(1), Duration.ofMinutes(5))
    .advanceBy(Duration.ofMinutes(15))
```

```
Timeline:  [----W1----]
                [----W2----]
                     [----W3----]
```

### Session Windows (Activity-Based)

```java
// Group records into sessions with max 5 minutes of inactivity
SessionWindows.ofInactivityGapWithNoGrace(Duration.ofMinutes(5))
```

Records close together in time are grouped into the same session. Sessions merge if a new record falls within the inactivity gap.

### Window Grace Period

```java
// Accept late records up to 2 minutes after the window closes
TimeWindows.ofSizeAndGrace(Duration.ofHours(1), Duration.ofMinutes(2))
```

Late records within the grace period update the window result. Records outside the grace period are dropped.

---

## State Stores

State stores hold the state for stateful operations (counts, aggregates, tables):

```
Application Instance:
  RocksDB (local disk) ← read/write during processing
       ↕ backed by
  Kafka changelog topic ← fault tolerance (replay to rebuild state)
       ↕ replicated to
  Standby replicas ← faster failover (state already partially populated)
```

**Interactive Queries** — query state stores from outside the topology:

```java
// Start interactive queries
streams.start();

// Get a read-only view of a state store
ReadOnlyKeyValueStore<String, Long> orderCounts =
    streams.store(StoreQueryParameters.fromNameAndType(
        "order-count-store", QueryableStoreTypes.keyValueStore()));

// Query by key
Long count = orderCounts.get("customer-123");

// Range scan
KeyValueIterator<String, Long> range = orderCounts.range("a", "z");
while (range.hasNext()) {
    KeyValue<String, Long> next = range.next();
    // process
}
range.close();
```

---

## Exactly-Once Processing (EOS)

```java
props.put(StreamsConfig.PROCESSING_GUARANTEE_CONFIG,
    StreamsConfig.EXACTLY_ONCE_V2);  // Use v2 (Kafka 2.6+)
```

With exactly-once enabled, Kafka Streams:
- Uses Kafka transactions internally
- Commits processed offsets + state store changes + output records atomically
- Guarantees each record is processed exactly once end-to-end

**Trade-offs**:
- Higher latency (transaction commits add overhead)
- Lower throughput (fewer records per transaction commit)
- Requires brokers with `transaction.state.log.replication.factor ≥ 3`

**When to use**: Financial transactions, order processing, anything where duplicates have real-world consequences.

**When not to use**: High-throughput metrics/logging where at-least-once is sufficient.

---

## Kafka Streams Configuration

```java
// Core settings
props.put(StreamsConfig.APPLICATION_ID_CONFIG, "my-app");
props.put(StreamsConfig.BOOTSTRAP_SERVERS_CONFIG, "broker:9092");

// Performance tuning
props.put(StreamsConfig.NUM_STREAM_THREADS_CONFIG, 4);   // threads per instance
props.put(StreamsConfig.COMMIT_INTERVAL_MS_CONFIG, 100); // offset/state commit frequency
props.put(StreamsConfig.CACHE_MAX_BYTES_BUFFERING_CONFIG, 10 * 1024 * 1024L); // 10MB record cache

// State store settings
props.put(StreamsConfig.STATE_DIR_CONFIG, "/var/kafka-streams");
props.put(StreamsConfig.NUM_STANDBY_REPLICAS_CONFIG, 1); // standby replicas for fast failover

// Exactly-once
props.put(StreamsConfig.PROCESSING_GUARANTEE_CONFIG, StreamsConfig.EXACTLY_ONCE_V2);
```

---

## Topology Visualization

```java
Topology topology = builder.build();
System.out.println(topology.describe());
```

Output shows all processors, source topics, sink topics, and state stores — essential for debugging complex topologies.

---

## ksqlDB

**ksqlDB** is a SQL-based stream processing engine built on Kafka Streams. Instead of writing Java, you write SQL:

```sql
-- Create a stream from a topic
CREATE STREAM orders (
    order_id VARCHAR,
    customer_id VARCHAR,
    amount DOUBLE
) WITH (kafka_topic='orders', value_format='JSON');

-- Filter and transform
CREATE STREAM confirmed_orders AS
    SELECT order_id, customer_id, amount * 1.1 AS amount_with_tax
    FROM orders
    WHERE status = 'CONFIRMED'
    EMIT CHANGES;

-- Aggregation (creates a table)
CREATE TABLE order_counts AS
    SELECT customer_id, COUNT(*) AS order_count
    FROM orders
    WINDOW TUMBLING (SIZE 1 HOUR)
    GROUP BY customer_id
    EMIT CHANGES;

-- Query current state
SELECT * FROM order_counts WHERE customer_id = '123';
```

ksqlDB is ideal for data engineering teams comfortable with SQL but not Java. For complex logic, use Kafka Streams directly.
