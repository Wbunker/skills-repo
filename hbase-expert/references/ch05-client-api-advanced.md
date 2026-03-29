# Ch 5 — Client API: Advanced Features

## Table of Contents
- [Filters Overview](#filters-overview)
- [Comparison Filters](#comparison-filters)
- [Dedicated Filters](#dedicated-filters)
- [Decorating Filters](#decorating-filters)
- [FilterList](#filterlist)
- [Custom Filters](#custom-filters)
- [Counters](#counters)
- [Coprocessors](#coprocessors)

---

## Filters Overview

Filters run **server-side** on RegionServers, reducing network data transfer.
They attach to Get or Scan operations.

```java
Scan scan = new Scan();
scan.setFilter(myFilter);

Get get = new Get(row);
get.setFilter(myFilter);
```

Filters operate on the cell stream; they can:
- Skip entire rows (`NEXT_ROW`)
- Skip columns within a row (`NEXT_COL`)
- Include/exclude specific cells (`INCLUDE` / `SKIP`)
- Stop the scan entirely (`DONE`)

---

## Comparison Filters

Apply a comparator to row key, column family, qualifier, or value.

### Comparator Types

| Comparator | Class | Description |
|------------|-------|-------------|
| `BinaryComparator` | Default | Exact byte comparison |
| `BinaryPrefixComparator` | | Matches prefix of bytes |
| `RegexStringComparator` | | Regex match (UTF-8 string) |
| `SubstringComparator` | | Substring match (case-insensitive) |
| `BitComparator` | | Bitwise AND/OR/XOR |
| `NullComparator` | | Checks for null/empty value |
| `LongComparator` | | Numeric long comparison |

### Comparison Operators

```java
CompareOperator.EQUAL
CompareOperator.NOT_EQUAL
CompareOperator.GREATER
CompareOperator.GREATER_OR_EQUAL
CompareOperator.LESS
CompareOperator.LESS_OR_EQUAL
CompareOperator.NO_OP  // never matches
```

### RowFilter

```java
// Only return rows whose key starts with "order-"
Filter rowFilter = new RowFilter(
    CompareOperator.EQUAL,
    new BinaryPrefixComparator(Bytes.toBytes("order-"))
);

// Only rows with key > "order-500"
Filter rowFilter2 = new RowFilter(
    CompareOperator.GREATER,
    new BinaryComparator(Bytes.toBytes("order-500"))
);
```

### FamilyFilter / QualifierFilter / ValueFilter

```java
// Only cells in family "cf"
Filter familyFilter = new FamilyFilter(
    CompareOperator.EQUAL,
    new BinaryComparator(Bytes.toBytes("cf"))
);

// Only cells where qualifier matches regex
Filter qualFilter = new QualifierFilter(
    CompareOperator.EQUAL,
    new RegexStringComparator("status|amount|customer_id")
);

// Only cells where value contains "pending"
Filter valueFilter = new ValueFilter(
    CompareOperator.EQUAL,
    new SubstringComparator("pending")
);
```

---

## Dedicated Filters

### SingleColumnValueFilter

Include/exclude entire rows based on a column's value:

```java
// Return rows where cf:status == "shipped"
SingleColumnValueFilter filter = new SingleColumnValueFilter(
    Bytes.toBytes("cf"),
    Bytes.toBytes("status"),
    CompareOperator.EQUAL,
    Bytes.toBytes("shipped")
);
filter.setFilterIfMissing(true);  // exclude rows where column is absent
filter.setLatestVersionOnly(true); // check only latest version (default true)
scan.setFilter(filter);
```

`SingleColumnValueExcludeFilter` — same, but excludes the filter column from results.

### PrefixFilter

```java
// Only rows with keys starting with "user-CA-"
Filter prefixFilter = new PrefixFilter(Bytes.toBytes("user-CA-"));
```

### PageFilter

```java
// Return at most 25 rows per region
Filter pageFilter = new PageFilter(25);
// Note: this limits per REGION, not globally — use scan.setLimit() for global limits
```

### FirstKeyOnlyFilter

Useful for counting rows (only returns first cell per row):

```java
Filter firstKeyFilter = new FirstKeyOnlyFilter();
// Often combined with KeyOnlyFilter to skip values too:
FilterList countFilter = new FilterList(
    new FirstKeyOnlyFilter(),
    new KeyOnlyFilter()
);
```

### KeyOnlyFilter

Returns cells without their values (just the key structure):

```java
Filter keyOnly = new KeyOnlyFilter();
Filter keyOnlyWithLen = new KeyOnlyFilter(true); // set value to value-length as long
```

### ColumnPrefixFilter / MultipleColumnPrefixFilter

```java
// Only columns with qualifier starting with "addr_"
Filter colPrefix = new ColumnPrefixFilter(Bytes.toBytes("addr_"));

// Multiple qualifier prefixes
byte[][] prefixes = { Bytes.toBytes("addr_"), Bytes.toBytes("phone_") };
Filter multiColPrefix = new MultipleColumnPrefixFilter(prefixes);
```

### ColumnRangeFilter

```java
// Qualifiers in range [minCol, maxCol]
Filter colRange = new ColumnRangeFilter(
    Bytes.toBytes("col_a"), true,   // inclusive
    Bytes.toBytes("col_z"), false   // exclusive
);
```

### TimestampsFilter

```java
// Only versions with specific timestamps
List<Long> timestamps = Arrays.asList(ts1, ts2, ts3);
Filter tsFilter = new TimestampsFilter(timestamps);
```

### SkipFilter / WhileMatchFilter

```java
// SkipFilter: skip entire row if any cell doesn't match the wrapped filter
Filter skipFilter = new SkipFilter(new ValueFilter(
    CompareOperator.NOT_EQUAL,
    new BinaryComparator(Bytes.toBytes("DELETE_ME"))
));

// WhileMatchFilter: stop scan as soon as wrapped filter says NEXT_ROW
Filter whileFilter = new WhileMatchFilter(new RowFilter(
    CompareOperator.EQUAL,
    new BinaryPrefixComparator(Bytes.toBytes("order-1"))
));
```

### InclusiveStopFilter

Make STOPROW inclusive instead of exclusive:

```java
scan.withStopRow(Bytes.toBytes("order-999"), true); // HBase 2.x
// OR for older API:
scan.setFilter(new InclusiveStopFilter(Bytes.toBytes("order-999")));
```

### DependentColumnFilter

Return all cells in a row only if a specific column value matches:

```java
// Return all columns in rows where cf:status matches "active"
Filter depFilter = new DependentColumnFilter(
    Bytes.toBytes("cf"),
    Bytes.toBytes("status"),
    false,  // false = drop dependent column from result
    CompareOperator.EQUAL,
    new BinaryComparator(Bytes.toBytes("active"))
);
```

---

## Decorating Filters

### FilterList

Combine multiple filters with AND or OR logic:

```java
// AND: row must pass ALL filters
FilterList andList = new FilterList(FilterList.Operator.MUST_PASS_ALL);
andList.addFilter(new PrefixFilter(Bytes.toBytes("order-")));
andList.addFilter(new SingleColumnValueFilter(...));

// OR: row must pass ANY filter
FilterList orList = new FilterList(FilterList.Operator.MUST_PASS_ONE);
orList.addFilter(filter1);
orList.addFilter(filter2);

// Nested FilterLists
FilterList complex = new FilterList(MUST_PASS_ALL);
complex.addFilter(prefixFilter);
FilterList inner = new FilterList(MUST_PASS_ONE);
inner.addFilter(valueFilter1);
inner.addFilter(valueFilter2);
complex.addFilter(inner);
```

---

## Custom Filters

Implement `org.apache.hadoop.hbase.filter.Filter` (or extend `FilterBase`):

```java
public class MyCustomFilter extends FilterBase {
    private boolean filterRow = false;

    @Override
    public ReturnCode filterCell(final Cell cell) {
        byte[] value = CellUtil.cloneValue(cell);
        // your logic here
        if (Bytes.equals(value, Bytes.toBytes("skip_me"))) {
            return ReturnCode.SKIP;
        }
        return ReturnCode.INCLUDE;
    }

    @Override
    public boolean filterRow() {
        return filterRow; // true = skip the whole row
    }

    @Override
    public boolean hasFilterRow() {
        return true;
    }

    // Serialization (required for server-side execution)
    @Override
    public byte[] toByteArray() {
        // serialize to protobuf or bytes
    }

    public static MyCustomFilter parseFrom(byte[] bytes) {
        // deserialize
    }
}
```

Custom filters must be deployed to RegionServer classpath (in `lib/` or via coprocessor mechanism).

---

## Counters

HBase supports **atomic 64-bit counter columns** — the value is stored as an 8-byte big-endian long.

### Single Counter

```java
// Increment by 1 (returns new value)
long newVal = table.incrementColumnValue(
    Bytes.toBytes("global_counters"),
    Bytes.toBytes("cf"),
    Bytes.toBytes("pageviews"),
    1L
);

// Increment by N
long newVal = table.incrementColumnValue(row, family, qualifier, 5L);

// Decrement
long newVal = table.incrementColumnValue(row, family, qualifier, -1L);
```

### Multiple Counters in One Call

```java
Increment increment = new Increment(Bytes.toBytes("stats-2025-03"));
increment.addColumn(Bytes.toBytes("cf"), Bytes.toBytes("views"), 1L);
increment.addColumn(Bytes.toBytes("cf"), Bytes.toBytes("clicks"), 1L);
increment.addColumn(Bytes.toBytes("cf"), Bytes.toBytes("purchases"), 0L); // read without change

Result result = table.increment(increment);

// Read back the values
long views     = Bytes.toLong(result.getValue(Bytes.toBytes("cf"), Bytes.toBytes("views")));
long clicks    = Bytes.toLong(result.getValue(Bytes.toBytes("cf"), Bytes.toBytes("clicks")));
```

### Reading Counter Values

```java
// A counter column is just a regular column storing 8 bytes
Get get = new Get(Bytes.toBytes("global_counters"));
get.addColumn(Bytes.toBytes("cf"), Bytes.toBytes("pageviews"));
Result result = table.get(get);
long count = Bytes.toLong(result.getValue(family, qualifier));
```

**Shell:**
```ruby
incr 'counters', 'row1', 'cf:total', 1
get_counter 'counters', 'row1', 'cf:total'
```

---

## Coprocessors

Coprocessors run **code on the RegionServer** — analogous to stored procedures or triggers in RDBMS.

### Two Types

| Type | Analogy | Purpose |
|------|---------|---------|
| **Observer** | Database trigger | React to events (pre/post mutations, reads, flushes, compactions) |
| **Endpoint** | Stored procedure | Custom RPC extension (aggregations, custom queries) |

### Observer Coprocessors

Implement one of:
- `RegionObserver` — pre/post put, get, delete, scan, flush, compact, split
- `MasterObserver` — pre/post table DDL, region assign/balance, snapshot
- `RegionServerObserver` — pre/post stop, rollback operations
- `WALObserver` — pre/post WAL write

```java
public class AuditObserver implements RegionObserver, RegionCoprocessor {

    @Override
    public Optional<RegionObserver> getRegionObserver() {
        return Optional.of(this);
    }

    @Override
    public void prePut(ObserverContext<RegionCoprocessorEnvironment> ctx,
                       Put put, WALEdit edit, Durability durability)
            throws IOException {
        // Called before every Put — validate, enrich, or reject
        byte[] user = put.getAttribute("user");
        if (user == null) {
            throw new IOException("Put requires 'user' attribute");
        }
    }

    @Override
    public void postPut(ObserverContext<RegionCoprocessorEnvironment> ctx,
                        Put put, WALEdit edit, Durability durability)
            throws IOException {
        // Called after every Put — log, index, notify
        LOG.info("Put to row: " + Bytes.toStringBinary(put.getRow()));
    }
}
```

### Endpoint Coprocessors (Custom Server-Side Aggregation)

Endpoint coprocessors extend the RPC protocol with custom calls.
Used for: server-side aggregation, custom bulk operations, row-count aggregation.

The built-in `AggregationClient` uses endpoint coprocessors:

```java
// Enable aggregation coprocessor on a table
alter 'orders', METHOD => 'table_att', 'COPROCESSOR' =>
  'hbase.jar|org.apache.hadoop.hbase.coprocessor.AggregateImplementation|1001|'

// Then from Java client:
AggregationClient ac = new AggregationClient(conf);
Scan scan = new Scan();
scan.addColumn(family, qualifier);
long rowCount = ac.rowCount(TableName.valueOf("orders"), null, scan);
```

### Loading Coprocessors

**Method 1: Table-level (recommended)**
```ruby
# In HBase shell — coprocessor loaded only for this table
alter 'orders',
  METHOD => 'table_att',
  'COPROCESSOR' => '/hdfs/path/mycoprocessor.jar|com.example.AuditObserver|1001|key1=val1'

# Format: JAR_PATH | CLASSNAME | PRIORITY | OPTIONAL_PARAMS
```

**Method 2: System-level (hbase-site.xml)**
```xml
<!-- Loads on every region — use with caution -->
<property>
  <name>hbase.coprocessor.region.classes</name>
  <value>com.example.AuditObserver</value>
</property>
<property>
  <name>hbase.coprocessor.master.classes</name>
  <value>com.example.MasterAuditObserver</value>
</property>
```

### Coprocessor Priorities

| Priority | Constant | When to use |
|----------|----------|-------------|
| 0 | `SYSTEM` | Internal HBase coprocessors |
| 100 | `USER` (default) | Application coprocessors |
| Higher number = lower priority (runs later)

### Key Cautions

- **A buggy coprocessor can crash a RegionServer** — test thoroughly
- Coprocessors cannot be updated in-place; disable table → alter → enable
- Use `ObserverContext.bypass()` to abort the default action
- Use `ObserverContext.complete()` to stop processing further coprocessors
