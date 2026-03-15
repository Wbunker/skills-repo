# Foundations — Chapters 1-2

Delta Lake internals, the transaction protocol, and setup.

## Table of Contents

- [What Delta Lake Is](#what-delta-lake-is)
- [The Transaction Log](#the-transaction-log)
- [MVCC and Optimistic Concurrency](#mvcc-and-optimistic-concurrency)
- [Table Features Protocol](#table-features-protocol)
- [Delta Kernel](#delta-kernel)
- [Setup and Installation](#setup-and-installation)

---

## What Delta Lake Is

Delta Lake is an open-source storage layer that brings ACID transactions to Apache Spark and cloud object storage (S3, ADLS, GCS). It stores data as Parquet files with a transaction log (`_delta_log/`) that tracks every change.

Key properties:
- **ACID transactions** on cloud object storage
- **Schema enforcement** — rejects writes that don't match the table schema
- **Time travel** — query any historical version
- **Unified batch and streaming** — same table serves both workloads
- **Open format** — Parquet data files + JSON/Parquet transaction log

## The Transaction Log

The `_delta_log/` directory is the single source of truth:

```
_delta_log/
├── 000000000000000000.json          ← Commit 0 (table creation)
├── 000000000000000001.json          ← Commit 1
├── ...
├── 000000000000000010.checkpoint.parquet  ← Checkpoint at commit 10
└── _last_checkpoint                 ← Pointer to latest checkpoint
```

**JSON commit files** contain actions:
- `add` — new data file added to the table
- `remove` — data file logically removed (physically deleted by VACUUM)
- `metaData` — schema changes, table properties
- `commitInfo` — timestamp, operation type, metrics
- `protocol` — minimum reader/writer versions required

**Checkpoint files** (Parquet format) are created every 10 commits by default. They consolidate the entire table state to avoid replaying all previous JSON files.

**Reading a table**: Start from the latest checkpoint, replay all subsequent JSON commits, build the set of valid data files, then read those Parquet files.

## MVCC and Optimistic Concurrency

Delta Lake uses **Multiversion Concurrency Control (MVCC)**:
- Readers read a consistent snapshot — they are never blocked by writers
- Writers use optimistic concurrency — they write independently, then check for conflicts at commit time
- If two writers modify the same files, the second writer's commit fails and is retried

**Conflict resolution**: When a commit fails, Delta Lake checks if the conflicting commit actually affects the same data. If not (e.g., different partitions), the commit succeeds via automatic conflict resolution. If yes, the operation is retried from the latest table version.

**Isolation levels**:
- Serializable (default for writes): Full conflict detection
- WriteSerializable: Allows certain concurrent writes that don't conflict

## Table Features Protocol

Delta tables declare which features they use via the `protocol` action:

```json
{
  "protocol": {
    "minReaderVersion": 3,
    "minWriterVersion": 7,
    "readerFeatures": ["deletionVectors", "columnMapping"],
    "writerFeatures": ["deletionVectors", "columnMapping", "clustering"]
  }
}
```

This ensures readers and writers that don't support required features will fail fast rather than produce incorrect results. Features include: `deletionVectors`, `columnMapping`, `clustering` (liquid clustering), `typeWidening`, `rowTracking`, `coordinatedCommits`, `variantType`.

**Drop Feature** (Delta 4.0): Remove table features while retaining history, avoiding the need for full table truncation.

## Delta Kernel

A framework for building connectors to Delta tables without depending on Apache Spark. Provides a stable, minimal API for reading (and writing, as of Delta 4.0) Delta tables from any engine.

Use cases: building Delta support in Trino, Flink, Presto, or custom engines.

## Setup and Installation

### Python (delta-rs / deltalake)

```bash
pip install deltalake
```

```python
from deltalake import DeltaTable, write_deltalake
import pandas as pd

# Write
df = pd.DataFrame({"id": [1, 2], "name": ["a", "b"]})
write_deltalake("/tmp/my_table", df)

# Read
dt = DeltaTable("/tmp/my_table")
df = dt.to_pandas()
```

### PySpark

```bash
pip install delta-spark
```

```python
from delta import configure_spark_with_delta_pip
from pyspark.sql import SparkSession

builder = SparkSession.builder \
    .appName("delta") \
    .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
    .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog")

spark = configure_spark_with_delta_pip(builder).getOrCreate()
```

### Scala

```scala
// build.sbt
libraryDependencies += "io.delta" %% "delta-spark" % "4.0.0"
```

### Rust (delta-rs)

```toml
# Cargo.toml
[dependencies]
deltalake = "0.22"
```

### Databricks

Delta Lake is built into Databricks Runtime. No setup needed — `USING DELTA` is the default format.
