# Ch 10 — Performance Tuning

## Table of Contents
- [Tuning Philosophy](#tuning-philosophy)
- [Hardware Recommendations](#hardware-recommendations)
- [OS-Level Tuning](#os-level-tuning)
- [JVM Tuning](#jvm-tuning)
- [Memory Architecture & Sizing](#memory-architecture--sizing)
- [BlockCache Tuning](#blockcache-tuning)
- [MemStore Tuning](#memstore-tuning)
- [Compaction Tuning](#compaction-tuning)
- [Handler and Thread Tuning](#handler-and-thread-tuning)
- [Client-Side Tuning](#client-side-tuning)
- [Compression and Encoding](#compression-and-encoding)
- [Read Path Optimization](#read-path-optimization)
- [Write Path Optimization](#write-path-optimization)
- [Benchmarking Tools](#benchmarking-tools)
- [Common Performance Problems & Diagnostics](#common-performance-problems--diagnostics)

---

## Tuning Philosophy

> "The most important performance knob in HBase is RAM." — Lars George

Priority order:
1. **Hardware** — right hardware matters more than any software config
2. **Schema design** — bad row key design kills performance permanently
3. **JVM** — correct heap sizing and GC config
4. **HBase config** — memory fractions, handlers, compaction
5. **Client config** — caching, batching

---

## Hardware Recommendations

### RegionServer Nodes

| Component | Minimum | Recommended | Notes |
|-----------|---------|-------------|-------|
| RAM | 24 GB | 64–128 GB | More RAM = bigger BlockCache + MemStore |
| CPU | 8 cores | 16–32 cores | Parallel compaction, multiple handlers |
| Disk | SATA HDD | NVMe SSD | SSDs dramatically improve random reads |
| Disk Count | 4 | 6–12 | JBOD, no RAID (HDFS handles redundancy) |
| Network | 1 GbE | 10 GbE | Critical for replication and compaction |

### Storage

- Use **JBOD** (Just a Bunch of Disks), not RAID — HDFS provides replication
- HDFS should have `dfs.datanode.data.dir` pointing to multiple disk paths
- SSD is transformative for HBase (10-50x random read improvement)
- Separate WAL disk from HFile disk if possible

### HMaster Nodes

- Less critical: 8–16 GB RAM, 4–8 cores
- Run 2 HMasters (active + backup) for HA

---

## OS-Level Tuning

```bash
# /etc/sysctl.conf — apply with: sysctl -p
vm.swappiness=0                     # Disable swap
vm.dirty_ratio=40                   # Max dirty page % before blocking writes
vm.dirty_background_ratio=10        # % at which background writeback starts
net.core.rmem_max=134217728         # Max receive buffer
net.core.wmem_max=134217728         # Max send buffer
net.ipv4.tcp_rmem="4096 87380 134217728"
net.ipv4.tcp_wmem="4096 65536 134217728"
net.core.netdev_max_backlog=300000

# /etc/security/limits.conf
hbase soft nofile 32768
hbase hard nofile 32768
hbase soft nproc  32768
hbase hard nproc  32768

# Transparent Huge Pages — DISABLE (causes GC jitter)
echo never > /sys/kernel/mm/transparent_hugepage/enabled
echo never > /sys/kernel/mm/transparent_hugepage/defrag

# Add to /etc/rc.local for persistence:
echo never > /sys/kernel/mm/transparent_hugepage/enabled
echo never > /sys/kernel/mm/transparent_hugepage/defrag

# CPU frequency scaling — set to performance
for cpu in /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor; do
    echo performance > $cpu
done
```

---

## JVM Tuning

### Heap Sizing Rules

```
Total RAM     | RS Heap | BlockCache (off-heap) | OS / HDFS DataNode
─────────────────────────────────────────────────────────────────────
32 GB node    | 16 GB   | —                     | 16 GB
64 GB node    | 20 GB   | 20 GB BucketCache     | 24 GB
128 GB node   | 24 GB   | 40 GB BucketCache     | 64 GB
```

**Rule:** Keep JVM heap ≤ 20–32 GB to avoid G1GC full-heap scans.
Use off-heap BucketCache for large data sets.

### hbase-env.sh

```bash
# Heap: same for -Xms and -Xmx to prevent resizing
export HBASE_REGIONSERVER_OPTS="\
  -Xms20g -Xmx20g \
  -XX:+UseG1GC \
  -XX:MaxGCPauseMillis=100 \
  -XX:G1HeapRegionSize=32m \
  -XX:InitiatingHeapOccupancyPercent=35 \
  -XX:G1NewSizePercent=5 \
  -XX:G1MaxNewSizePercent=30 \
  -XX:+ParallelRefProcEnabled \
  -XX:+PerfDisableSharedMem \
  -XX:+AlwaysPreTouch \
  -XX:+DisableExplicitGC \
  -verbose:gc \
  -XX:+PrintGCDetails \
  -XX:+PrintGCDateStamps \
  -XX:+PrintAdaptiveSizePolicy \
  -Xloggc:${HBASE_LOG_DIR}/gc-rs.log \
  -XX:+UseGCLogFileRotation \
  -XX:NumberOfGCLogFiles=5 \
  -XX:GCLogFileSize=20m"

export HBASE_MASTER_OPTS="\
  -Xms4g -Xmx4g \
  -XX:+UseG1GC \
  -XX:MaxGCPauseMillis=200"
```

### G1GC Key Parameters

| Parameter | Value | Why |
|-----------|-------|-----|
| `MaxGCPauseMillis` | 100 | Target pause; trade throughput for low latency |
| `G1HeapRegionSize` | 32m | Larger region for HBase's large byte arrays |
| `InitiatingHeapOccupancyPercent` | 35 | Trigger concurrent mark early (default 45 often too late) |
| `ParallelRefProcEnabled` | true | Parallel reference processing reduces pause |
| `AlwaysPreTouch` | true | Pre-fault pages at startup, avoid runtime page faults |

---

## Memory Architecture & Sizing

```
RegionServer JVM Heap (example: 20 GB)
├── MemStore Pool: 40% = 8 GB     (hbase.regionserver.global.memstore.size)
│   └── Per-region MemStore: flushes at 128 MB each
├── BlockCache (on-heap LRU): 40% = 8 GB  (hfile.block.cache.size)
│   └── L1 cache: hot/frequently accessed blocks
└── Other (RPC buffers, coprocessors, overhead): 20% = 4 GB

Off-heap (BucketCache) — separate from JVM heap:
└── L2 cache: larger data set, no GC pressure
```

### Sizing the Ratio

```xml
<!-- Total of memstore + blockcache fractions should be ≤ 0.80 -->
<property>
  <name>hbase.regionserver.global.memstore.size</name>
  <value>0.40</value>
</property>
<property>
  <name>hfile.block.cache.size</name>
  <value>0.40</value>
</property>
```

**For read-heavy workloads:** Reduce MemStore (0.25), increase BlockCache (0.55)
**For write-heavy workloads:** Increase MemStore (0.50), reduce BlockCache (0.30)

---

## BlockCache Tuning

### LRU BlockCache (default, on-heap)

```xml
<property>
  <name>hfile.block.cache.size</name>
  <value>0.40</value>  <!-- 40% of heap -->
</property>
```

Three priority buckets within LRU:
- **Single-access (25%):** blocks accessed once (scan data)
- **Multi-access (50%):** blocks accessed more than once (hot data)
- **In-memory (25%):** blocks from CFs with `IN_MEMORY=true`

### BucketCache (off-heap, recommended for large datasets)

```xml
<!-- Use off-heap BucketCache as L2 -->
<property>
  <name>hbase.bucketcache.ioengine</name>
  <value>offheap</value>  <!-- or: file:/path/to/cache (SSD), mmap:/path -->
</property>
<property>
  <name>hbase.bucketcache.size</name>
  <value>20480</value>  <!-- MB, separate from heap -->
</property>
<!-- L1 (on-heap LRU) stays small, L2 (BucketCache) holds bulk -->
<property>
  <name>hfile.block.cache.size</name>
  <value>0.10</value>  <!-- reduce L1 heap to make room -->
</property>
```

Add to JVM opts: `-XX:MaxDirectMemorySize=22g` (BucketCache size + buffer)

### Per-Table Cache Control

```java
// Disable caching for full-table scans (avoid polluting cache)
scan.setCacheBlocks(false);

// Mark a CF as in-memory (L1 priority)
ColumnFamilyDescriptorBuilder.newBuilder(cf)
    .setInMemory(true)
    .build();

// Cache data blocks on write (useful for recently written hot data)
ColumnFamilyDescriptorBuilder.newBuilder(cf)
    .setCacheDataOnWrite(true)
    .build();
```

---

## MemStore Tuning

```xml
<!-- Flush threshold per region (default 128MB) -->
<property>
  <name>hbase.hregion.memstore.flush.size</name>
  <value>134217728</value>
</property>

<!-- Upper limit: fraction of heap before write blocking -->
<property>
  <name>hbase.regionserver.global.memstore.size</name>
  <value>0.40</value>
</property>

<!-- Lower limit: fraction at which forced flushes start (default = size * 0.95) -->
<property>
  <name>hbase.regionserver.global.memstore.size.lower.limit</name>
  <value>0.38</value>
</property>

<!-- How long to wait for MemStore to drain before giving up (ms) -->
<property>
  <name>hbase.server.thread.wakefrequency</name>
  <value>10000</value>
</property>
```

### In-Memory Compaction (HBase 2.x)

Reduces flush frequency by compacting MemStore data before flush:

```java
ColumnFamilyDescriptorBuilder.newBuilder(cf)
    .setInMemoryCompaction(MemoryCompactionPolicy.BASIC)     // compact indexes
    .setInMemoryCompaction(MemoryCompactionPolicy.EAGER)     // also compact data cells
    .setInMemoryCompaction(MemoryCompactionPolicy.ADAPTIVE)  // auto-choose (recommended)
    .build();
```

Shell:
```ruby
alter 'orders', {NAME => 'cf', IN_MEMORY_COMPACTION => 'ADAPTIVE'}
```

---

## Compaction Tuning

Compaction merges HFiles — improves read performance but consumes I/O.

```xml
<!-- Minor compaction: merge when this many StoreFiles exist (default 3) -->
<property>
  <name>hbase.hstore.compactionThreshold</name>
  <value>3</value>
</property>

<!-- Maximum StoreFiles before writes are throttled (default 7) -->
<property>
  <name>hbase.hstore.blockingStoreFiles</name>
  <value>10</value>
</property>

<!-- Max size of files to include in minor compaction (bytes, default 256MB) -->
<property>
  <name>hbase.hstore.compaction.max.size</name>
  <value>268435456</value>
</property>

<!-- Compaction throughput limit (bytes/sec, 0 = unlimited) -->
<property>
  <name>hbase.regionserver.throughput.controller</name>
  <value>org.apache.hadoop.hbase.regionserver.compactions.PressureAwareCompactionThroughputController</value>
</property>
<property>
  <name>hbase.hstore.compaction.throughput.higher.bound</name>
  <value>52428800</value>  <!-- 50 MB/s during off-peak -->
</property>
<property>
  <name>hbase.hstore.compaction.throughput.lower.bound</name>
  <value>26214400</value>  <!-- 25 MB/s during peak -->
</property>
```

### Major Compaction Scheduling

```xml
<!-- Major compaction interval (ms, default 7 days = 604800000) -->
<!-- Set to 0 to disable auto major compaction (manage manually) -->
<property>
  <name>hbase.hregion.majorcompaction</name>
  <value>604800000</value>
</property>

<!-- Jitter to avoid all regions compacting simultaneously (default 0.5 = ±50%) -->
<property>
  <name>hbase.hregion.majorcompaction.jitter</name>
  <value>0.5</value>
</property>
```

**Recommendation:** Disable auto major compaction and schedule during off-peak hours:
```bash
# Manually trigger major compaction on all tables
echo "list" | hbase shell | grep -v "^TABLE" | grep -v "^$" | \
  while read t; do echo "major_compact '$t'"; done | hbase shell
```

---

## Handler and Thread Tuning

```xml
<!-- RPC handler threads per RegionServer (default 30) -->
<!-- Rule of thumb: CPU_CORES * 5, or start at 30 and monitor queue depth -->
<property>
  <name>hbase.regionserver.handler.count</name>
  <value>30</value>
</property>

<!-- Priority queue size for priority requests (flushes, compactions) -->
<property>
  <name>hbase.regionserver.metahandler.count</name>
  <value>20</value>
</property>

<!-- Maximum request queue size (backpressure) -->
<property>
  <name>ipc.server.max.callqueue.size</name>
  <value>1073741824</value>  <!-- 1 GB -->
</property>

<!-- Split the call queue: separate read and write handlers -->
<property>
  <name>hbase.ipc.server.callqueue.read.ratio</name>
  <value>0.5</value>  <!-- 50% of handlers for reads -->
</property>
<property>
  <name>hbase.ipc.server.callqueue.scan.ratio</name>
  <value>0.5</value>  <!-- 50% of read handlers for scans -->
</property>
```

---

## Client-Side Tuning

```java
// Disable auto-flush for bulk puts (buffer in client, send in batches)
// Note: In HBase 1.0+, use BufferedMutator instead
BufferedMutatorParams params = new BufferedMutatorParams(tableName)
    .writeBufferSize(8 * 1024 * 1024);  // 8 MB write buffer
BufferedMutator mutator = connection.getBufferedMutator(params);

// Scanner caching: rows fetched per RPC (default 100 in HBase 2.x)
scan.setCaching(500);     // increase for large sequential scans
scan.setCacheBlocks(false); // don't cache on full table scans

// Batch: columns per Result returned (useful for very wide rows)
scan.setBatch(100);       // return at most 100 cells per Result object

// Limit fetched columns to only what you need
scan.addColumn(family, qualifier);  // never fetch all columns if you don't need them

// Use Get instead of Scan for point lookups
// Use exists() instead of get() when you only need existence

// Connection pool for multi-threaded clients (Connection is thread-safe)
// Create one Connection per JVM, share across threads
```

---

## Compression and Encoding

### Compression Quick Reference

```ruby
alter 'orders', {NAME => 'cf', COMPRESSION => 'SNAPPY'}    # hot tables
alter 'orders', {NAME => 'cf', COMPRESSION => 'LZ4'}       # highest throughput
alter 'orders', {NAME => 'cf', COMPRESSION => 'ZSTD'}      # balanced (HBase 2+)
alter 'orders', {NAME => 'cf', COMPRESSION => 'GZ'}        # cold/archival
```

Test compression:
```bash
bin/hbase org.apache.hadoop.hbase.util.CompressionTest \
  hdfs://namenode/tmp/test-compression SNAPPY
```

### Data Block Encoding

Separate from compression — reduces key prefix overhead within data blocks:

```ruby
alter 'orders', {NAME => 'cf', DATA_BLOCK_ENCODING => 'FAST_DIFF'}
```

| Encoding | When to use |
|----------|-------------|
| `NONE` | Default; no encoding |
| `PREFIX` | Long row keys with shared prefixes |
| `DIFF` | Rows with similar structure and incremental timestamps |
| `FAST_DIFF` | Recommended default for most tables |
| `ROW_INDEX_V1` | Rows with many columns (improves seeks within rows) |

**Enable both** compression + data block encoding for best storage efficiency.

---

## Read Path Optimization

```
Optimization impact for random reads (approximate):
1. Adequate RAM / BlockCache hit rate     → 10-100x improvement (cache vs disk)
2. SSD storage                            → 10-50x vs spinning disk
3. Bloom filters (ROW or ROWCOL)          → skip irrelevant HFiles (2-5x)
4. Data block encoding (FAST_DIFF)        → smaller blocks = more in cache
5. Column family isolation                → only read the CF you need
6. Scan caching and batching              → fewer RPC round trips
```

### Bloom Filters

```java
// ROW bloom: helps Get operations skip HFiles that don't contain the row key
ColumnFamilyDescriptorBuilder.newBuilder(cf)
    .setBloomFilterType(BloomType.ROW)
    .build();

// ROWCOL bloom: helps Get operations specifying both row AND column
ColumnFamilyDescriptorBuilder.newBuilder(cf)
    .setBloomFilterType(BloomType.ROWCOL)
    .build();
// Use ROWCOL when: you frequently Get specific columns (not entire rows)
// ROWCOL uses more memory than ROW
```

---

## Write Path Optimization

```
Optimization impact for writes (approximate):
1. Pre-split regions                      → avoid hot single-region load
2. Salted/hashed row keys                 → distribute across all RegionServers
3. BufferedMutator (batching)             → reduce RPC overhead (2-5x throughput)
4. ASYNC_WAL or SKIP_WAL                  → eliminate WAL sync wait (2-10x, at risk)
5. Bulk loading (HFileOutputFormat2)      → bypass WAL entirely for large ingestion
6. Adequate MemStore size                 → fewer, larger flushes
7. Compression enabled                   → smaller flushes + less disk I/O
```

---

## Benchmarking Tools

### PerformanceEvaluation

```bash
# Sequential write 1M rows with 4 client threads
bin/hbase org.apache.hadoop.hbase.PerformanceEvaluation \
  --rows=1000000 --nomapred sequentialWrite 4

# Random read 100K rows
bin/hbase org.apache.hadoop.hbase.PerformanceEvaluation \
  --rows=100000 randomRead 4

# Scan all rows
bin/hbase org.apache.hadoop.hbase.PerformanceEvaluation \
  --rows=1000000 scan 1

# Available tests:
# sequentialWrite, randomWrite, scan, randomRead, sequentialRead
# randomSeekScan, filterScan, increment, append, checkAndMutate
```

### LoadTestTool

```bash
# Stress test: write then mixed read/write
bin/hbase org.apache.hadoop.hbase.util.LoadTestTool \
  -write 2:10:100 -num_keys 1000000 -tn load_test_table

# -write numThreads:keySize:valueSize
# -read numThreads:verifyPercent
# -update numThreads:percent:numupdates
```

---

## Common Performance Problems & Diagnostics

| Problem | Symptom | Diagnosis | Fix |
|---------|---------|-----------|-----|
| Hotspot | One RS at 100% CPU, others idle | Web UI region distribution | Salt/hash row keys, pre-split |
| GC pauses | Timeouts, RPC errors | GC log: long pause events | Tune G1GC, reduce heap, add BucketCache |
| Too many HFiles | Slow reads, compaction backlog | RS web UI: StoreFiles per region | Lower compactionThreshold, trigger major compact |
| MemStore OOM | OOM errors, RS crash | Heap dump: MemStore dominates | Lower memstore.size ratio, increase flush frequency |
| Write blocking | `Memstore is above high watermark` | RS logs | Increase flush speed (more disks/threads), reduce write rate |
| RegionServer fail | RPC timeouts | Logs: ZK session timeout | Check ZK, network, GC pauses; check ulimits |
| Slow scans | Full table scan taking too long | No STARTROW/STOPROW on scan | Add row key bounds; use filters; disable block cache |
| RPC queue full | `CallQueueTooBigException` | RS web UI: RPC queue depth | Increase handler.count; add backpressure on client |
| Clock skew | Kerberos errors, timestamp issues | `ntpstat` / `chronyc tracking` | Ensure NTP synchronized within 5 minutes |
