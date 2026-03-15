# Indexing in Hudi
## Chapter 5: Bloom Filter, Record-Level, Bucket, HBase — Trade-offs and Selection

---

## Why Indexing Matters

During an **upsert**, Hudi must determine for each incoming record:
1. Does this record already exist in the table?
2. If yes, which file group (and which partition) contains it?

Without an index, Hudi would have to scan every file in every partition to answer this. For large tables, that is prohibitively expensive.

The index maps `(record_key, partition_path)` → `file_group_id`, enabling Hudi to route each incoming record directly to the correct file group for merging.

```
Incoming record: { order_id: 12345, region: "US", amount: 99.99 }
                          ↓
                    Index lookup
                          ↓
              → File: s3://bucket/orders/region=US/file007_xxx.parquet
                          ↓
              Read that file, merge record 12345, write new version
```

---

## Index Types

### 1. Bloom Filter Index (Default)

A probabilistic data structure stored inside each Parquet base file's footer.

**How it works:**
```
At write time:
  For each record written to a file, add hash(record_key) to the file's Bloom filter
  Store the filter in the Parquet footer metadata

At upsert time:
  For each incoming key, check each file group's Bloom filter
  If filter says "definitely not" → skip that file (no I/O)
  If filter says "maybe" → read the file and do exact lookup
```

**Properties:**
- **No false negatives**: if a key is in a file, the filter will say "maybe"
- **False positives**: filter may say "maybe" when the key is not there (controlled by FPP)
- Stored inside Parquet files — no external state to manage

**Configuration:**
```python
"hoodie.index.type": "BLOOM",
"hoodie.bloom.index.parallelism": "200",        # parallelism for index lookup
"hoodie.bloom.filter.fpp": "0.000000001",       # false positive probability (default)
"hoodie.bloom.index.use.metadata": "true",      # use metadata table for filter storage
```

**Trade-offs:**
| Aspect | Detail |
|--------|--------|
| Lookup scope | **Partition-local** by default — only checks files in the record's target partition |
| Global dedup | Requires `GLOBAL_BLOOM` (checks all partitions, much slower) |
| Performance | Fast when keys map cleanly to partitions; slow with high FPP or many files |
| Scaling | Degrades as table grows (more files = more filter checks) |
| External state | None — self-contained in Parquet files |

**Best for:** Tables with a natural partition key that also serves as a locality hint for record keys. Example: orders partitioned by `order_date` where you always know the date when upserting.

---

### 2. Record-Level Index (RLI)

An exact, global index stored in Hudi's metadata table. Maps every record key to its exact file group location.

**How it works:**
```
Metadata table (.hoodie/metadata/record_index/)
  { "order_id=12345" → "region=US/file007" }
  { "order_id=67890" → "region=EU/file003" }
  ...

At upsert time:
  Bulk lookup: send all incoming keys to metadata table
  Get exact file group for each key (no false positives)
  Route directly to the right file group
```

**Configuration:**
```python
"hoodie.index.type": "RECORD_INDEX",
"hoodie.metadata.record.index.enable": "true",
"hoodie.metadata.enable": "true",
```

**Trade-offs:**
| Aspect | Detail |
|--------|--------|
| Lookup scope | **Global** — works across all partitions |
| Accuracy | Exact — no false positives |
| Latency | Fast for individual lookups; bulk lookups are parallel |
| Storage | Metadata table grows with record count |
| Maintenance | Metadata table must stay in sync (automatic but adds write overhead) |
| Scale limit | Works well up to billions of records |

**Best for:** Tables that need global deduplication across partitions, where record keys are not correlated with partition columns. Example: user event table partitioned by date but deduplicated by `user_id`.

---

### 3. Bucket Index

Uses consistent hashing to assign records to file groups deterministically — no lookup needed at all.

**How it works:**
```
At table creation: define N buckets
At write time:
  bucket_id = hash(record_key) % N
  Record always goes to file group #bucket_id (within its partition)
  No index lookup — the destination is computed, not looked up

At upsert time:
  Same hash function → same bucket_id
  Write directly to that file group
```

**Configuration:**
```python
"hoodie.index.type": "BUCKET",
"hoodie.storage.layout.type": "BUCKET",
"hoodie.bucket.index.num.buckets": "128",       # number of buckets per partition
"hoodie.bucket.index.hash.field": "order_id",   # field to hash
```

**Trade-offs:**
| Aspect | Detail |
|--------|--------|
| Lookup | Zero — no I/O for index lookup |
| Write throughput | Highest of all index types |
| Flexibility | Bucket count is **fixed at creation** — cannot be changed without rewriting |
| File size | Bucket size depends on data volume; over/under-provisioning is possible |
| Skew | If key distribution is uneven, some buckets get overloaded |
| Global scope | Yes (all records with same key always map to same bucket) |

**Best for:** High-throughput streaming upserts where write latency is critical and key distribution is known and relatively uniform. Example: real-time order processing table with UUID keys.

---

### 4. HBase Index

Stores the index in an external Apache HBase cluster.

**How it works:**
```
External HBase cluster maintains:
  HBase table: { record_key → (partition_path, file_group_id) }

At upsert time:
  Batch GET all incoming keys from HBase
  Get exact file group location (global, exact)
  Route records to correct file groups
  After write: batch PUT updated locations back to HBase
```

**Configuration:**
```python
"hoodie.index.type": "HBASE",
"hoodie.index.hbase.zkquorum": "hbase-zk1,hbase-zk2,hbase-zk3",
"hoodie.index.hbase.zkport": "2181",
"hoodie.index.hbase.table": "hudi_index",
"hoodie.index.hbase.get.batch.size": "100",
"hoodie.index.hbase.put.batch.size": "1000",
```

**Trade-offs:**
| Aspect | Detail |
|--------|--------|
| Scope | Global — across all partitions |
| Accuracy | Exact |
| External dependency | Requires a running HBase cluster |
| Latency | Network I/O to HBase; tunable with batch sizes |
| Scale | Handles trillions of records (HBase scales horizontally) |
| Operational cost | Must maintain HBase cluster |

**Best for:** Extremely large tables (trillions of records) with global key uniqueness requirements, in organizations already running HBase infrastructure.

---

## Index Comparison Matrix

| Aspect | Bloom Filter | Record-Level | Bucket | HBase |
|--------|-------------|-------------|--------|-------|
| Lookup cost | O(n files) probabilistic | O(1) exact | Zero (computed) | O(1) external network |
| False positives | Yes (controllable) | No | No | No |
| Global dedup | Via GLOBAL_BLOOM (slow) | Yes (native) | Yes | Yes |
| External dependency | None | Hudi metadata table | None | HBase cluster |
| Write throughput | Medium | Medium-High | Highest | Medium |
| Scalability | Degrades with table size | Good to billions | Fixed bucket count | Excellent (trillions) |
| Flexibility | High | High | Low (fixed buckets) | High |
| Operational complexity | Low | Low | Low | High |

---

## Index Selection Decision Tree

```
Do you need global deduplication across partitions?
├── No (record key is correlated with partition key)
│   └── Bloom Filter (default)
│       Simple, no external deps, good for most cases
│
└── Yes (record key unrelated to partition)
    ├── Expected table size < 10 billion records?
    │   ├── Need maximum write throughput + keys evenly distributed?
    │   │   └── Bucket Index
    │   │       Zero-lookup writes; fixed bucket count
    │   └── General case with flexible schema/partitioning?
    │       └── Record-Level Index
    │           Exact, global, no external deps
    │
    └── Expected table size > 10 billion records?
        ├── Already have HBase infrastructure?
        │   └── HBase Index
        │       Best raw throughput at extreme scale
        └── No HBase?
            → Record-Level Index (try first; scale HBase if needed)
```

---

## Metadata Table and Index Storage

Hudi's metadata table (`.hoodie/metadata/`) is the storage backend for the Record-Level Index, Bloom Filter Index (as an alternative to Parquet footer storage), and column statistics.

```
.hoodie/metadata/
├── files/          ← file listing (avoids S3 ListObjects)
├── col_stats/      ← column min/max/null counts per file
├── bloom_filters/  ← Bloom filters (alternative to Parquet footer)
└── record_index/   ← Record-Level Index entries
```

**Enable all metadata features:**
```python
"hoodie.metadata.enable": "true",
"hoodie.metadata.index.column.stats.enable": "true",
"hoodie.metadata.index.bloom.filter.enable": "true",
"hoodie.metadata.record.index.enable": "true",   # Record-Level Index only
```

The metadata table itself is a Hudi table internally — it benefits from Hudi's own ACID semantics and timeline.
