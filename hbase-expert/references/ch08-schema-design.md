# Ch 8 — Schema Design & Row Key Patterns

## Table of Contents
- [Design Philosophy](#design-philosophy)
- [Row Key Design Principles](#row-key-design-principles)
- [Hotspotting and How to Avoid It](#hotspotting-and-how-to-avoid-it)
- [Row Key Patterns](#row-key-patterns)
- [Column Family Design](#column-family-design)
- [Tall-and-Narrow vs Wide Rows](#tall-and-narrow-vs-wide-rows)
- [Versioning Patterns](#versioning-patterns)
- [Time-Series Data Patterns](#time-series-data-patterns)
- [Secondary Index Patterns](#secondary-index-patterns)
- [Case Studies](#case-studies)

---

## Design Philosophy

HBase schema design is fundamentally different from RDBMS:

> **"Design for how you read, not for how it's normalized."**

Key constraints that drive design decisions:
1. **Only one index** — the row key (no secondary indexes natively)
2. **No joins** — denormalize or use application-level lookups
3. **Lexicographic sort** — row keys are sorted by byte comparison
4. **Region granularity** — all writes to sequential keys go to one region (hotspot risk)
5. **Scan is cheap** — contiguous row key ranges scan efficiently
6. **Random access is cheap** — exact row key lookups are fast (Get)

---

## Row Key Design Principles

### Rule 1: Design the row key for your primary access pattern

The row key is the **only guaranteed fast access path**. Everything else requires a full scan or secondary index.

```
Access Pattern → Row Key Design
─────────────────────────────────────────────────────────────────
"Give me user U's order"           → user_id + order_id
"Give me all orders by user U"     → user_id prefix scan
"Give me orders in time range"     → timestamp-based key (careful with hotspot!)
"Give me order by ID"              → order_id (simple)
"Give me latest activity for user" → user_id + reverse_timestamp
```

### Rule 2: Keep row keys short

Row key bytes are stored in **every cell** of that row (in HFiles). A 100-byte row key with 1000 columns = 100KB overhead just for keys.

**Guideline:** Row keys should be 10–100 bytes. Use MD5/SHA hashes or compact representations.

### Rule 3: Distribute writes evenly across regions

Avoid patterns that route all current writes to one region:
- Sequential integers: 1, 2, 3, 4... → all go to last region
- Timestamps: 20250101, 20250102... → all go to last region
- Alphabetical: aaa, aab, aac... → depends on data distribution

---

## Hotspotting and How to Avoid It

A **hotspot** occurs when all read/write traffic concentrates on one RegionServer, while others are idle.

### Common Hotspot Causes

1. **Monotonically increasing keys** (timestamps, auto-increment IDs)
2. **Too few regions** for the data volume
3. **Skewed key distribution** (certain prefixes dominate)

### Hotspot Solutions

#### 1. Salting (prefix randomization)

Prepend a random or computed prefix to distribute rows across N regions:

```java
// Define N "buckets"
int NUM_BUCKETS = 16;

// Assign bucket by hashing the natural key
int bucket = Math.abs(orderId.hashCode()) % NUM_BUCKETS;
String rowKey = String.format("%02d_%s", bucket, orderId);

// Examples:
// "07_order-001", "03_order-002", "11_order-003"
```

**Downside:** Scanning all orders requires N separate scans (one per bucket).

```java
// Scatter-gather scan
List<Scan> scans = new ArrayList<>();
for (int i = 0; i < NUM_BUCKETS; i++) {
    Scan scan = new Scan();
    scan.withStartRow(Bytes.toBytes(String.format("%02d_", i)));
    scan.withStopRow(Bytes.toBytes(String.format("%02d`", i))); // backtick > underscore
    scans.add(scan);
}
// Execute in parallel and merge results
```

#### 2. Hashing (deterministic, consistent)

Replace natural key with its MD5/SHA1 hash:

```java
// MD5 hash gives uniform distribution across full key space
byte[] hash = MessageDigest.getInstance("MD5").digest(Bytes.toBytes(orderId));
byte[] rowKey = Bytes.add(hash, Bytes.toBytes(orderId)); // hash + original for readability
```

**Downside:** Range scans on logical order are impossible (hash order ≠ original order).
Use only for pure point lookups.

#### 3. Reverse Key

Reverse the bytes of the key (useful for strings/IDs with shared prefixes):

```java
// "order-001" → "100-redro" — distributes across key space
String reversed = new StringBuilder(orderId).reverse().toString();
byte[] rowKey = Bytes.toBytes(reversed);
```

#### 4. Reverse Timestamp (for time-series, latest-first queries)

```java
// Subtract from Long.MAX_VALUE so latest events sort first
long reverseTs = Long.MAX_VALUE - System.currentTimeMillis();
byte[] rowKey = Bytes.add(
    Bytes.toBytes(userId),
    Bytes.toBytes(reverseTs)
);
// Scan from start of user's rows → gets latest events first
```

#### 5. Pre-Split Regions

Always pre-split tables that will grow large:

```ruby
# Split into 16 regions with uniform hex key space
create 'orders',
  {NAME => 'cf', COMPRESSION => 'SNAPPY'},
  SPLITS => ['10','20','30','40','50','60','70','80','90','a0','b0','c0','d0','e0','f0']

# Or use create_table_with_region_info utility
```

---

## Row Key Patterns

### Composite Keys

Combine multiple fields into a single row key for multi-dimensional queries:

```
user_id + order_id      → get all orders for user (prefix scan on user_id)
date + region + product → get sales by date+region (range scan)
```

**Key ordering matters** — leftmost component drives the primary sort.

```java
// user:order composite key
byte[] rowKey = Bytes.add(
    MD5Hash.getMD5AsHex(userId).getBytes(),  // 32 chars, uniform hash
    Bytes.toBytes(":"),
    Bytes.toBytes(orderId)
);
```

### Timestamp in Row Key

```
Pattern 1: entity_id + timestamp      → range scan by time for an entity
Pattern 2: entity_id + reverse_ts     → latest events first (most common)
Pattern 3: timestamp + entity_id      → time-ordered scan across all entities (hotspot risk!)
Pattern 4: bucket + timestamp         → time-ordered scan, distributed across buckets
```

### Sequential ID Anti-Pattern

```
BAD:  rowKey = String.format("%09d", autoIncrementId)
      → 000000001, 000000002, 000000003 → all writes to one region

GOOD: rowKey = MD5(autoIncrementId) + autoIncrementId
      → distributed writes, still findable by ID
```

---

## Column Family Design

### Number of Column Families

**Use 1 CF whenever possible. Maximum 2–3.**

Why: Each CF has a separate MemStore and flushes independently. More CFs means:
- More MemStore memory per region
- More small HFiles per region (worse compaction)
- More complex flush/compaction scheduling

When to use multiple CFs:
- Data with very different access patterns (hot metadata + cold bulk data)
- Data with different TTLs or compression needs
- Data you want to cache separately (set `IN_MEMORY` on one CF)

### CF Naming

Use **single-character names** — stored in every cell key in HFiles.

```
cf     → too generic for multi-CF tables
d      → "data" (acceptable short form)
m      → "metadata"
s      → "stats"
```

### Qualifier Naming

Qualifiers are repeated in **every cell** — keep short.

```
Bad:  "user_first_name", "user_last_name", "user_email_address"
Good: "fn", "ln", "email"
```

---

## Tall-and-Narrow vs Wide Rows

### Tall-and-Narrow (many rows, few columns per row)

```
Row key: user_id + metric_name + timestamp
Columns: cf:value

user-001:pageviews:1700000001 → cf:value = "1"
user-001:pageviews:1700000002 → cf:value = "1"
user-001:clicks:1700000001   → cf:value = "1"
```

**Pros:** Efficient range scans; row-level atomicity per event; easy TTL per event
**Cons:** More rows = larger row key index; no single-row multi-metric atomicity

### Wide Rows (few rows, many columns)

```
Row key: user_id + date
Columns: cf:metric_name:timestamp → value

user-001:20250101 → cf:pageviews_1700000001 = "1"
                  → cf:pageviews_1700000002 = "1"
                  → cf:clicks_1700000001 = "1"
```

**Pros:** Atomic update of multiple metrics in one row; single Get for all of a user's daily data
**Cons:** Wide rows can exceed region size; column scanning is less efficient than row scanning

**General guidance:** Prefer tall-and-narrow for time-series. Use wide rows for entity-attribute patterns where you always read all attributes together.

---

## Versioning Patterns

```java
// Enable multiple versions on CF
ColumnFamilyDescriptor cf = ColumnFamilyDescriptorBuilder
    .newBuilder(Bytes.toBytes("history"))
    .setMaxVersions(Integer.MAX_VALUE)  // keep all versions
    .setMinVersions(3)                  // keep at least 3 regardless of TTL
    .setTimeToLive(86400 * 30)          // 30-day TTL
    .build();
```

**Version patterns:**

1. **Audit trail** — `MAX_VERSIONS = N` stores last N updates to each column
2. **Temporal queries** — scan with `setTimeRange()` to query data at a point in time
3. **Latest value only** — `MAX_VERSIONS = 1` (default) — most common, saves space
4. **Immutable event log** — `MAX_VERSIONS = Integer.MAX_VALUE` — store every update

---

## Time-Series Data Patterns

### OpenTSDB-style Pattern

```
Row key: metric_name + reverse_timestamp + entity_id
Columns: cf:delta_seconds → value

Example:
"temperature\x00\xFF\xFF\xEB\xE4\x49\x00sensor-042" → cf:0 = "72.5"
                                                      → cf:300 = "72.8"  # +5 min
                                                      → cf:600 = "73.1"  # +10 min
```

Store one row per metric per hour, with columns as second offsets within the hour.
This creates a compact representation while allowing efficient range queries.

### Simple Time-Series

```
Row key: entity_id + reverse_timestamp
Column:  cf:value → reading

user-001\x00\xFF\xFF\xEB\xE4\x49\x00 → cf:temp = "72.5"
```

Scan from `user-001` start to get latest readings first.

---

## Secondary Index Patterns

HBase has no native secondary indexes. Common workarounds:

### Manual Index Table

```
Main table: orders
  Row key: order_id
  cf:customer_id, cf:date, cf:status

Index table: orders_by_customer
  Row key: customer_id + order_id
  cf:order_id (or empty — just existence marks the relationship)

Lookup pattern:
  1. Scan orders_by_customer where prefix = customer_id
  2. Get each order_id from main orders table
```

**Maintain atomicity:** Use `checkAndMutate` or implement retry logic for writes that must update both tables.

### Coprocessor-based Index

Use an `RegionObserver` to automatically maintain the index table on every put:

```java
@Override
public void postPut(ObserverContext<...> ctx, Put put, WALEdit edit, Durability dur)
        throws IOException {
    byte[] customerId = put.getAttribute("customer_id");
    if (customerId != null) {
        // write to index table
        Put indexPut = new Put(Bytes.add(customerId, put.getRow()));
        indexTable.put(indexPut);
    }
}
```

### Apache Phoenix

For complex secondary indexing needs, Apache Phoenix provides:
- SQL interface over HBase
- Global and local secondary indexes
- Covered indexes (include data columns in index)
- Partial indexes (WHERE clause filtering)

---

## Case Studies

### User Activity Log

**Requirement:** Store all actions a user takes; query by user; get latest N actions.

```
Table: user_activity
Row key: MD5(user_id) + user_id + reverse_timestamp
CF: cf
Qualifiers: action, resource, ip, session_id

Pre-split: 16 regions on MD5 hash prefix
```

```java
// Write
long reverseTs = Long.MAX_VALUE - System.currentTimeMillis();
byte[] rowKey = Bytes.add(
    MD5Hash.getMD5AsHex(userId).substring(0,2).getBytes(),
    Bytes.toBytes(userId + ":"),
    Bytes.toBytes(reverseTs)
);

// Query: latest 100 actions for a user
Scan scan = new Scan();
scan.withStartRow(Bytes.add(
    MD5Hash.getMD5AsHex(userId).substring(0,2).getBytes(),
    Bytes.toBytes(userId + ":")));
scan.withStopRow(Bytes.add(
    MD5Hash.getMD5AsHex(userId).substring(0,2).getBytes(),
    Bytes.toBytes(userId + ";")));  // ";" is one byte after ":" in ASCII
scan.setLimit(100);
```

### URL Crawl Status

**Requirement:** Store crawl result per URL; query by domain.

```
Table: crawl_status
Row key: reverse_domain + "/" + path
  e.g., "com.example.www/about" → groups all pages of a domain together

CF: cf
Qualifiers: status_code, last_crawled, content_hash, links_count
```

```java
// Reverse domain for better locality:
// www.example.com/page → com.example.www/page
String reverseDomain = Arrays.stream(host.split("\\."))
    .map(s -> new StringBuilder(s).reverse().toString())
    .collect(Collectors.joining("."));
// Actually just reverse the parts:
String[] parts = host.split("\\.");
Collections.reverse(Arrays.asList(parts));
String reversed = String.join(".", parts);
byte[] rowKey = Bytes.toBytes(reversed + "/" + path);
```
