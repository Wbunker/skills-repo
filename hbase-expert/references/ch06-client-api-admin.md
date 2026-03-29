# Ch 6 — Client API: Administrative Features

## Table of Contents
- [Getting an Admin Instance](#getting-an-admin-instance)
- [Namespace Management](#namespace-management)
- [Table Management (DDL)](#table-management-ddl)
- [Column Family Configuration](#column-family-configuration)
- [Table Properties](#table-properties)
- [Region Management](#region-management)
- [Cluster Operations](#cluster-operations)
- [Schema Best Practices Summary](#schema-best-practices-summary)

---

## Getting an Admin Instance

```java
try (Connection connection = ConnectionFactory.createConnection(conf);
     Admin admin = connection.getAdmin()) {
    // perform admin operations
}
// Admin is NOT thread-safe — get one per operation/thread
```

---

## Namespace Management

```java
// Create namespace
NamespaceDescriptor ns = NamespaceDescriptor.create("prod")
    .addConfiguration("hbase.namespace.quota.maxtables", "50")
    .addConfiguration("hbase.namespace.quota.maxregions", "200")
    .build();
admin.createNamespace(ns);

// List namespaces
NamespaceDescriptor[] namespaces = admin.listNamespaceDescriptors();

// Describe a namespace
NamespaceDescriptor desc = admin.getNamespaceDescriptor("prod");

// Modify namespace config
admin.modifyNamespace(NamespaceDescriptor.create("prod")
    .addConfiguration("hbase.namespace.quota.maxtables", "100")
    .build());

// Delete namespace (must be empty)
admin.deleteNamespace("dev");
```

Shell equivalents:
```ruby
create_namespace 'prod', {'hbase.namespace.quota.maxtables' => '50'}
describe_namespace 'prod'
alter_namespace 'prod', {METHOD => 'set', 'hbase.namespace.quota.maxtables' => '100'}
drop_namespace 'dev'
list_namespace
list_namespace_tables 'prod'
```

---

## Table Management (DDL)

### Creating Tables

```java
// Simple table with one CF
TableName tableName = TableName.valueOf("orders");
TableDescriptorBuilder tableDesc = TableDescriptorBuilder.newBuilder(tableName);

ColumnFamilyDescriptor cfDesc = ColumnFamilyDescriptorBuilder
    .newBuilder(Bytes.toBytes("cf"))
    .setMaxVersions(3)
    .setCompressionType(Compression.Algorithm.SNAPPY)
    .setBloomFilterType(BloomType.ROW)
    .build();

tableDesc.setColumnFamily(cfDesc);
admin.createTable(tableDesc.build());

// With pre-split regions (avoid initial hotspot)
byte[][] splitKeys = {
    Bytes.toBytes("order-200"),
    Bytes.toBytes("order-400"),
    Bytes.toBytes("order-600"),
    Bytes.toBytes("order-800")
};
admin.createTable(tableDesc.build(), splitKeys);

// Pre-split by hex key pattern
admin.createTable(tableDesc.build(),
    Bytes.toBytes("00000000"),
    Bytes.toBytes("ffffffff"),
    16);  // 16 regions
```

### Check Existence / Enable / Disable / Drop

```java
boolean exists = admin.tableExists(tableName);

admin.disableTable(tableName);  // required before drop and some alters
admin.enableTable(tableName);
admin.deleteTable(tableName);   // table must be disabled

boolean enabled  = admin.isTableEnabled(tableName);
boolean disabled = admin.isTableDisabled(tableName);

// Truncate (drops and recreates preserving schema)
admin.truncateTable(tableName, true);  // true = preserve splits
```

### Listing Tables

```java
List<TableDescriptor> tables = admin.listTableDescriptors();
List<TableDescriptor> prodTables = admin.listTableDescriptors(
    Pattern.compile("prod:.*"));

TableName[] tableNames = admin.listTableNames();
```

### Altering Tables

```java
// Modify table-level property
TableDescriptor existing = admin.getDescriptor(tableName);
TableDescriptorBuilder builder = TableDescriptorBuilder.newBuilder(existing);
builder.setValue("DURABILITY", "ASYNC_WAL");
admin.modifyTable(builder.build());

// Add a new column family (table does NOT need to be disabled in HBase 1+)
ColumnFamilyDescriptor newCF = ColumnFamilyDescriptorBuilder
    .newBuilder(Bytes.toBytes("stats"))
    .setMaxVersions(1)
    .build();
admin.addColumnFamily(tableName, newCF);

// Modify existing CF
ColumnFamilyDescriptor modified = ColumnFamilyDescriptorBuilder
    .newBuilder(Bytes.toBytes("cf"))
    .setMaxVersions(5)
    .setCompressionType(Compression.Algorithm.SNAPPY)
    .build();
admin.modifyColumnFamily(tableName, modified);

// Remove a CF
admin.deleteColumnFamily(tableName, Bytes.toBytes("old_cf"));
```

Shell equivalents:
```ruby
alter 'orders', {NAME => 'cf', VERSIONS => 5, COMPRESSION => 'SNAPPY'}
alter 'orders', {NAME => 'stats', BLOOMFILTER => 'ROWCOL'}
alter 'orders', 'delete' => 'old_cf'
alter 'orders', DURABILITY => 'ASYNC_WAL'
```

---

## Column Family Configuration

### ColumnFamilyDescriptorBuilder Options

```java
ColumnFamilyDescriptorBuilder cfBuilder = ColumnFamilyDescriptorBuilder
    .newBuilder(Bytes.toBytes("cf"));

// Versions
cfBuilder.setMinVersions(0);        // min versions to keep regardless of TTL (default 0)
cfBuilder.setMaxVersions(1);        // max versions to keep (default 1)

// TTL
cfBuilder.setTimeToLive(86400);     // seconds; cells older than this are deleted at compaction
                                     // Integer.MAX_VALUE = forever (default)

// Compression
cfBuilder.setCompressionType(Compression.Algorithm.SNAPPY);   // SNAPPY, GZ, LZ4, ZSTD, BZIP2
cfBuilder.setCompactionCompressionType(Compression.Algorithm.GZ); // heavier compression for compacted files

// Bloom Filters
cfBuilder.setBloomFilterType(BloomType.ROW);     // bloom on row key (default)
cfBuilder.setBloomFilterType(BloomType.ROWCOL);  // bloom on row+qualifier (for column lookups)
cfBuilder.setBloomFilterType(BloomType.NONE);    // disable

// Block Size (data blocks in HFile)
cfBuilder.setBlocksize(65536);   // default 64KB; smaller = better random read; larger = better scan

// Block Cache
cfBuilder.setBlockCacheEnabled(true);   // cache data blocks on read (default true)
cfBuilder.setInMemory(true);            // hint to keep in L1 BlockCache (high priority)
cfBuilder.setCacheDataOnWrite(false);   // cache on write path (default false)
cfBuilder.setCacheDataInL1(false);      // force to L1 bucket cache

// Data Block Encoding (reduces size of keys in data blocks)
cfBuilder.setDataBlockEncoding(DataBlockEncoding.PREFIX);    // common prefix compression
cfBuilder.setDataBlockEncoding(DataBlockEncoding.DIFF);      // delta encoding
cfBuilder.setDataBlockEncoding(DataBlockEncoding.FAST_DIFF); // recommended default
cfBuilder.setDataBlockEncoding(DataBlockEncoding.ROW_INDEX_V1); // for large rows with many cols

// Replication Scope (for cluster replication)
cfBuilder.setScope(HConstants.REPLICATION_SCOPE_GLOBAL);  // 1 = replicate
cfBuilder.setScope(HConstants.REPLICATION_SCOPE_LOCAL);   // 0 = don't replicate (default)

// MOB (Medium Object Blobs) for values 100KB–10MB
cfBuilder.setMobEnabled(true);
cfBuilder.setMobThreshold(102400);  // 100KB threshold

ColumnFamilyDescriptor cf = cfBuilder.build();
```

### Compression Algorithms Comparison

| Algorithm | Speed | Ratio | CPU | Best For |
|-----------|-------|-------|-----|----------|
| `NONE` | Fastest | 1:1 | Lowest | Hot data, simple values |
| `SNAPPY` | Very fast | ~2:1 | Low | General purpose (Google default) |
| `LZ4` | Fastest compressed | ~2:1 | Very low | High-throughput, low-latency |
| `ZSTD` | Fast | ~3:1 | Medium | Best balance (HBase 2.x+) |
| `GZ` (GZIP) | Slow | ~3.5:1 | High | Cold/archival data |
| `BZIP2` | Slowest | ~4:1 | Highest | Maximum compression only |

**Recommended defaults:**
- Hot tables: `SNAPPY` or `LZ4`
- Mixed: `ZSTD` (HBase 2+)
- Cold/archive: `GZ`

Also enable **Data Block Encoding** (`FAST_DIFF`) — separate from compression, reduces key overhead within data blocks.

---

## Table Properties

Set at table level via `TableDescriptorBuilder`:

```java
TableDescriptorBuilder builder = TableDescriptorBuilder.newBuilder(tableName);

// Durability at table level (overrides per-mutation setting)
builder.setDurability(Durability.ASYNC_WAL);

// Region split policy
builder.setValue("SPLIT_POLICY",
    "org.apache.hadoop.hbase.regionserver.ConstantSizeRegionSplitPolicy");

// Max region file size (overrides hbase-site.xml for this table)
builder.setMaxFileSize(5L * 1024 * 1024 * 1024);  // 5 GB

// Read-only table
builder.setReadOnly(true);

// Compaction enabled/disabled
builder.setCompactionEnabled(false);  // disable for bulk load tables

// Normalization enabled
builder.setNormalizationEnabled(true);

// Custom metadata
builder.setValue("owner", "team-platform");
builder.setValue("sla", "tier-1");
```

Shell:
```ruby
alter 'orders', DURABILITY => 'ASYNC_WAL', MAX_FILESIZE => 5368709120
alter 'orders', READONLY => true
alter 'orders', COMPACTION_ENABLED => false
```

---

## Region Management

```java
// List regions for a table
List<RegionInfo> regions = admin.getRegions(tableName);
for (RegionInfo region : regions) {
    System.out.println(region.getRegionNameAsString());
    System.out.println("  Start key: " + Bytes.toStringBinary(region.getStartKey()));
    System.out.println("  End key:   " + Bytes.toStringBinary(region.getEndKey()));
    System.out.println("  Encoded:   " + region.getEncodedName());
}

// Manual flush
admin.flush(tableName);
admin.flushRegion(regionName);

// Compaction
admin.compact(tableName);                    // minor compaction
admin.majorCompact(tableName);               // major compaction
admin.compactRegion(regionName);
admin.majorCompactRegion(regionName);

// Manual split
admin.split(tableName);                      // split all regions at midpoint
admin.split(tableName, Bytes.toBytes("order-500"));  // split at specific row key

// Manual merge (must be adjacent regions)
admin.mergeRegionsAsync(
    regionInfo1.getEncodedNameAsBytes(),
    regionInfo2.getEncodedNameAsBytes(),
    false  // forcible = false (only merge if truly adjacent)
);

// Move region to specific RegionServer
admin.move(regionInfo.getEncodedNameAsBytes(),
    ServerName.valueOf("rs2.example.com,16020,1234567890"));

// Balance load
admin.setBalancerRunning(true, false);
boolean balanced = admin.balance();
```

Shell equivalents:
```ruby
flush 'orders'
compact 'orders'
major_compact 'orders'
compact_rs 'rs1.example.com,16020,1234'  # compact all regions on an RS
split 'orders', 'order-500'
merge_region '3a456...', '4b789...', false
move '3a456...', 'rs2.example.com,16020,1234'
balancer
```

### Region Split Policies

| Policy | Behavior | Use Case |
|--------|----------|----------|
| `SteppingSplitPolicy` (default) | First split at 128MB, then 10GB | General purpose |
| `ConstantSizeRegionSplitPolicy` | Split at `hbase.hregion.max.filesize` | Uniform data |
| `KeyPrefixRegionSplitPolicy` | Split on key prefix boundary | Prefix-grouped data |
| `BusyRegionSplitPolicy` | Split when region is hot (high request rate) | Hotspot mitigation |
| `DelimitedKeyPrefixRegionSplitPolicy` | Split on delimiter in row key | Compound keys |
| `DisabledRegionSplitPolicy` | Never auto-split | Manually pre-split tables |

```ruby
# Set split policy per table
alter 'orders', SPLIT_POLICY => 'org.apache.hadoop.hbase.regionserver.ConstantSizeRegionSplitPolicy'
```

---

## Cluster Operations

```java
// Get cluster status
ClusterMetrics metrics = admin.getClusterMetrics();
System.out.println("Servers: " + metrics.getLiveServerMetrics().size());
System.out.println("Dead: "    + metrics.getDeadServerNames().size());
System.out.println("Requests/s: " + metrics.getRequestCountPerSecond());

// List RegionServers
for (ServerName server : metrics.getLiveServerMetrics().keySet()) {
    System.out.println(server.getHostname() + ":" + server.getPort());
}

// Stop a RegionServer gracefully
admin.stopRegionServer("rs1.example.com:16020");

// Decommission RegionServers (drains regions first)
admin.decommissionRegionServers(
    Arrays.asList(ServerName.valueOf("rs1.example.com,16020,1234")),
    false  // offload = false: mark for decommission without moving regions now
);
admin.recommissionRegionServer(serverName, null);

// Run balancer
admin.balance();

// Switch compaction on/off cluster-wide
admin.compactionSwitch(false, new ArrayList<>());  // disable all compactions

// WAL rolling
admin.rollWALWriter(serverName);
```

Shell:
```ruby
status 'detailed'
list_regions 'orders'
list_deadservers
assign 'region_encoded_name'
unassign 'region_encoded_name', true  # true = force
```

---

## Schema Best Practices Summary

| Concern | Recommendation |
|---------|---------------|
| Number of CFs | 1–3 per table; prefer 1 |
| CF naming | Use single characters ("d", "m", "s") — stored in every cell key |
| Qualifier naming | Keep short — repeated in every cell in an HFile |
| Versions | Default to 1; only increase if you need history |
| TTL | Set where data expires to reclaim space automatically |
| Compression | Always enable (SNAPPY/LZ4 for hot, ZSTD for balanced) |
| Data Block Encoding | Use FAST_DIFF (reduces key prefix overhead) |
| Bloom filters | ROW for row-key Gets; ROWCOL for column-level Gets |
| Block size | 64KB default; smaller (16KB) for random access; larger (256KB) for sequential scan |
| Pre-splitting | Always pre-split for tables expecting > 1 region — avoids initial write hotspot |
