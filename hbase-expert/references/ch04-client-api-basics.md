# Ch 4 — Client API: Basics (Shell & Java)

## Table of Contents
- [HBase Shell Reference](#hbase-shell-reference)
- [Java Client Setup](#java-client-setup)
- [Put — Writing Data](#put--writing-data)
- [Get — Reading a Row](#get--reading-a-row)
- [Delete — Removing Data](#delete--removing-data)
- [Scan — Range Reads](#scan--range-reads)
- [Batch Operations](#batch-operations)
- [Row Locks and Atomics](#row-locks-and-atomics)
- [Connection Management](#connection-management)

---

## HBase Shell Reference

### DDL Commands

```ruby
# Create table with one column family
create 'orders', 'cf'

# Create with multiple CFs and options
create 'events',
  {NAME => 'data', COMPRESSION => 'SNAPPY', BLOOMFILTER => 'ROW'},
  {NAME => 'meta', TTL => 86400, VERSIONS => 1}

# Describe a table's schema
describe 'orders'

# Alter table: add CF, change options
alter 'orders', {NAME => 'metrics', BLOOMFILTER => 'ROWCOL'}
alter 'orders', {NAME => 'cf', COMPRESSION => 'SNAPPY'}

# Disable/enable (required before drop or some alters)
disable 'orders'
enable  'orders'
is_enabled  'orders'
is_disabled 'orders'

# Drop table (must be disabled first)
drop 'orders'

# List tables
list
list 'ord.*'   # supports regex

# Truncate (disable + drop + recreate)
truncate 'orders'
```

### DML Commands

```ruby
# Write a cell
put 'orders', 'order-001', 'cf:status', 'pending'
put 'orders', 'order-001', 'cf:amount', '99.99'

# With explicit timestamp (use epoch millis)
put 'orders', 'order-001', 'cf:status', 'shipped', 1700000000000

# Read a row
get 'orders', 'order-001'

# Read specific column
get 'orders', 'order-001', 'cf:status'
get 'orders', 'order-001', {COLUMN => 'cf:status', VERSIONS => 3}

# Scan (range read)
scan 'orders'
scan 'orders', {STARTROW => 'order-001', STOPROW => 'order-100'}
scan 'orders', {COLUMNS => ['cf:status', 'cf:amount'], LIMIT => 10}
scan 'orders', {TIMERANGE => [1700000000000, 1800000000000]}

# Delete
delete 'orders', 'order-001', 'cf:status'           # specific cell (latest version)
delete 'orders', 'order-001', 'cf:status', 1700000000000  # specific version
deleteall 'orders', 'order-001'                       # all columns in row

# Count rows (slow — do not use on large tables in production)
count 'orders'
count 'orders', INTERVAL => 100000

# Increment a counter
incr 'orders', 'counters', 'cf:total_orders', 1
get_counter 'orders', 'counters', 'cf:total_orders'
```

### Admin Commands

```ruby
# Cluster status
status
status 'summary'
status 'simple'
status 'detailed'

# Trigger manual operations
flush 'orders'               # flush MemStores to disk
flush 'regionserver-name'   # flush all regions on an RS
compact 'orders'             # minor compaction
major_compact 'orders'       # major compaction (expensive)
split 'orders'               # split all regions
split 'orders', 'order-500'  # split at specific row key

# Move, assign, balance
balance_switch true
balancer
assign '3a456...'            # assign region by encoded name
move  '3a456...', 'rs2:16020'

# Snapshot
snapshot 'orders', 'orders_snap_20250101'
list_snapshots
restore_snapshot 'orders_snap_20250101'
clone_snapshot   'orders_snap_20250101', 'orders_backup'
delete_snapshot  'orders_snap_20250101'
```

---

## Java Client Setup

### Maven Dependency

```xml
<dependency>
  <groupId>org.apache.hbase</groupId>
  <artifactId>hbase-client</artifactId>
  <version>2.5.x</version>  <!-- use current stable -->
</dependency>
```

### Connection Boilerplate

```java
import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.hbase.HBaseConfiguration;
import org.apache.hadoop.hbase.TableName;
import org.apache.hadoop.hbase.client.*;
import org.apache.hadoop.hbase.util.Bytes;

// Connection is thread-safe and expensive — create once, share across threads
Configuration conf = HBaseConfiguration.create();
conf.set("hbase.zookeeper.quorum", "zk1,zk2,zk3");
conf.set("hbase.zookeeper.property.clientPort", "2181");

// Try-with-resources for automatic cleanup
try (Connection connection = ConnectionFactory.createConnection(conf)) {
    TableName tableName = TableName.valueOf("orders");
    try (Table table = connection.getTable(tableName)) {
        // perform operations
    }
}
```

---

## Put — Writing Data

```java
byte[] row    = Bytes.toBytes("order-001");
byte[] family = Bytes.toBytes("cf");
byte[] qual   = Bytes.toBytes("status");
byte[] value  = Bytes.toBytes("pending");

// Basic put (uses current timestamp)
Put put = new Put(row);
put.addColumn(family, qual, value);
table.put(put);

// Put with explicit timestamp
put.addColumn(family, qual, System.currentTimeMillis(), value);

// Add multiple columns in one Put (atomic for the row)
Put multiPut = new Put(row);
multiPut.addColumn(family, Bytes.toBytes("status"), Bytes.toBytes("pending"));
multiPut.addColumn(family, Bytes.toBytes("amount"), Bytes.toBytes("99.99"));
multiPut.addColumn(family, Bytes.toBytes("customer_id"), Bytes.toBytes("cust-42"));
table.put(multiPut);

// Durability control (trade safety for performance)
put.setDurability(Durability.ASYNC_WAL);   // faster, slight data loss risk
put.setDurability(Durability.SKIP_WAL);    // fastest, risk of loss on crash
put.setDurability(Durability.SYNC_WAL);    // default — safe
```

### Buffered Mutations (batch puts, high throughput)

```java
// BufferedMutator batches puts and flushes when buffer fills
BufferedMutatorParams params = new BufferedMutatorParams(tableName)
    .writeBufferSize(8 * 1024 * 1024);  // 8 MB
try (BufferedMutator mutator = connection.getBufferedMutator(params)) {
    for (String orderId : orderIds) {
        Put put = new Put(Bytes.toBytes(orderId));
        put.addColumn(family, Bytes.toBytes("status"), Bytes.toBytes("new"));
        mutator.mutate(put);
    }
    mutator.flush();  // ensure all buffered puts are sent
}
```

---

## Get — Reading a Row

```java
byte[] row = Bytes.toBytes("order-001");
Get get = new Get(row);

// Get all columns
Result result = table.get(get);

// Get specific column family
get.addFamily(Bytes.toBytes("cf"));

// Get specific column
get.addColumn(Bytes.toBytes("cf"), Bytes.toBytes("status"));

// Control versions
get.readVersions(3);          // return up to 3 versions per cell
get.setTimeRange(minTs, maxTs); // only versions in this time range
get.setTimestamp(exactTs);      // only this exact version

// Read result
byte[] value = result.getValue(family, Bytes.toBytes("status"));
String status = Bytes.toString(value);

// Iterate all cells in result
for (Cell cell : result.rawCells()) {
    byte[] rowKey  = CellUtil.cloneRow(cell);
    byte[] cf      = CellUtil.cloneFamily(cell);
    byte[] qual    = CellUtil.cloneQualifier(cell);
    byte[] val     = CellUtil.cloneValue(cell);
    long   ts      = cell.getTimestamp();
}

// Check if row exists (cheaper than full Get)
get.setCheckExistenceOnly(true);
boolean exists = table.exists(get);
```

---

## Delete — Removing Data

```java
Delete delete = new Delete(Bytes.toBytes("order-001"));

// Delete entire row (all versions of all columns)
table.delete(delete);

// Delete a specific column family (all versions)
delete.addFamily(Bytes.toBytes("cf"));

// Delete a specific column (latest version only)
delete.addColumn(Bytes.toBytes("cf"), Bytes.toBytes("status"));

// Delete a specific column (all versions)
delete.addColumns(Bytes.toBytes("cf"), Bytes.toBytes("status"));

// Delete specific version of a column
delete.addColumn(Bytes.toBytes("cf"), Bytes.toBytes("status"), timestamp);
```

**Important:** Deletes are tombstoned — the actual data is removed during the next major compaction.
Until then, Scanners respect tombstones and skip deleted data.

---

## Scan — Range Reads

```java
Scan scan = new Scan();

// Set row key range (STARTROW inclusive, STOPROW exclusive)
scan.withStartRow(Bytes.toBytes("order-100"));
scan.withStopRow(Bytes.toBytes("order-200"));

// Limit columns
scan.addFamily(Bytes.toBytes("cf"));
scan.addColumn(Bytes.toBytes("cf"), Bytes.toBytes("status"));

// Limit results
scan.setLimit(100);              // max rows to return
scan.readVersions(2);            // max versions per cell
scan.setTimeRange(minTs, maxTs); // time-bounded scan

// Performance: how many rows to cache per RPC call (default 2)
scan.setCaching(100);

// Disable block caching for full-table scans (avoids evicting hot data)
scan.setCacheBlocks(false);

// Use a scanner
try (ResultScanner scanner = table.getScanner(scan)) {
    for (Result row : scanner) {
        byte[] rowKey = row.getRow();
        byte[] value  = row.getValue(family, Bytes.toBytes("status"));
        // process...
    }
}

// Prefix scan (common pattern)
byte[] prefix = Bytes.toBytes("order-");
scan.withStartRow(prefix);
scan.withStopRow(Bytes.add(prefix, new byte[]{(byte)0xFF})); // all rows with prefix
// Or use PrefixFilter instead (see ch05)
```

### Scan Caching Tuning

| `setCaching(n)` | Effect |
|-----------------|--------|
| 1 (default) | One RPC per row — max latency, min memory |
| 100–500 | Good balance for most workloads |
| 1000+ | High throughput bulk scans; more memory on client |

---

## Batch Operations

```java
// Batch mixed operations (puts, gets, deletes) — single RPC round trip
List<Row> batch = new ArrayList<>();
batch.add(new Put(Bytes.toBytes("row1")).addColumn(family, qual, value1));
batch.add(new Get(Bytes.toBytes("row2")));
batch.add(new Delete(Bytes.toBytes("row3")));

Object[] results = new Object[batch.size()];
table.batch(batch, results);

for (int i = 0; i < results.length; i++) {
    if (results[i] instanceof Result) {
        Result r = (Result) results[i];
        // handle get result
    } else if (results[i] == null) {
        // this operation failed
    }
}
```

**Note:** Batch operations are best-effort — partial failures are possible.
Check each result slot for null (failure) vs. Result/Boolean (success).

---

## Row Locks and Atomics

### Compare-and-Swap (checkAndMutate)

```java
// Atomic: only put if cf:status == "pending"
CheckAndMutateResult result = table.checkAndMutate(
    CheckAndMutate.newBuilder(Bytes.toBytes("order-001"))
        .ifEquals(Bytes.toBytes("cf"), Bytes.toBytes("status"),
                  Bytes.toBytes("pending"))
        .build(new Put(Bytes.toBytes("order-001"))
            .addColumn(Bytes.toBytes("cf"),
                       Bytes.toBytes("status"),
                       Bytes.toBytes("shipped")))
);
boolean updated = result.isSuccess();

// Atomic: only put if column doesn't exist (null check)
table.checkAndMutate(
    CheckAndMutate.newBuilder(row)
        .ifNotExists(family, qualifier)
        .build(put)
);
```

### Atomic Increment

```java
// Increment a column value atomically (column stores 8-byte big-endian long)
long newValue = table.incrementColumnValue(
    Bytes.toBytes("counters"),  // row key
    Bytes.toBytes("cf"),        // family
    Bytes.toBytes("total"),     // qualifier
    1L                          // amount to add
);
```

---

## Connection Management

### Best Practices

```java
// CORRECT: One Connection per application (thread-safe, expensive to create)
public class HBaseService {
    private static Connection connection;

    public static synchronized Connection getConnection() throws IOException {
        if (connection == null || connection.isClosed()) {
            connection = ConnectionFactory.createConnection(HBaseConfiguration.create());
        }
        return connection;
    }

    // Table objects are cheap and NOT thread-safe — get one per operation/thread
    public void writeOrder(String orderId) throws IOException {
        try (Table table = getConnection().getTable(TableName.valueOf("orders"))) {
            Put put = new Put(Bytes.toBytes(orderId));
            // ...
            table.put(put);
        }
    }
}

// WRONG: Creating a new Connection per request (expensive, resource leak)
// Connection conn = ConnectionFactory.createConnection(conf);  // ← DON'T DO THIS per request
```

### Connection Pool Summary

| Object | Thread-Safe | Cost | Lifecycle |
|--------|-------------|------|-----------|
| `Configuration` | Yes | Low | Application |
| `Connection` | Yes | High | Application |
| `Table` | **No** | Low | Request/operation |
| `Admin` | **No** | Low | Request/operation |
| `ResultScanner` | **No** | Low | Scan lifetime |
