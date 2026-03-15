# Foundations — Chapters 1-3

Apache Iceberg architecture, the three metadata layers, data and delete files, catalog types, and format versions.

## Table of Contents

- [What Apache Iceberg Is](#what-apache-iceberg-is)
- [Three-Layer Architecture](#three-layer-architecture)
- [Data Layer](#data-layer)
- [Metadata Layer](#metadata-layer)
- [Catalog Layer](#catalog-layer)
- [Format Versions](#format-versions)
- [Setup and Installation](#setup-and-installation)

---

## What Apache Iceberg Is

Apache Iceberg is an open table format for large analytic datasets. It brings database-like behavior to data lakes on object storage (S3, ADLS, GCS, HDFS).

Key properties:
- **ACID transactions** on cloud object storage via optimistic concurrency
- **Schema evolution** — add, drop, rename, reorder, widen columns without rewriting data
- **Hidden partitioning** — partition layout decoupled from queries
- **Partition evolution** — change partition scheme without rewriting data
- **Time travel** — query any historical snapshot
- **Engine-agnostic** — 30+ engines (Spark, Trino, Flink, Athena, Dremio, DuckDB, etc.)
- **Open format** — Parquet/ORC/Avro data files + Avro/JSON metadata

## Three-Layer Architecture

```
Catalog   →  Tracks current metadata pointer per table
              │
Metadata  →  metadata.json  →  manifest-list.avro  →  manifest.avro
              (table state)     (snapshot contents)     (file listings + stats)
              │
Data      →  Parquet/ORC/Avro data files + delete files
```

Every write creates a new snapshot. The catalog atomically swaps the metadata pointer. Readers see a consistent snapshot — never blocked by writers.

## Data Layer

### Data files

Actual table data stored as Parquet (most common), ORC, or Avro files on object storage. Each data file belongs to one partition and contains rows for that partition.

### Delete files (v2+)

Three mechanisms for marking rows as deleted without rewriting data files:

#### Position delete files

Mark rows by file path + row position:

```
file_path                          pos
data/part-00001.parquet            14
data/part-00001.parquet            203
data/part-00003.parquet            89
```

- Precise — reader knows exactly which rows to skip
- Written during DELETE/UPDATE when using merge-on-read
- Can accumulate many small files that slow reads

#### Equality delete files

Mark rows by column values:

```
id
42
107
```

- Any row matching `id=42` or `id=107` is deleted
- Faster to write (no need to find position)
- More expensive to read (must evaluate predicate against all rows)
- Best when delete key is a primary key

#### Deletion vectors (v3)

Binary bitmaps stored in Puffin files, one per data file:

- Most compact representation
- Fastest read reconciliation (bitmap check)
- Stored alongside statistics in Puffin sidecar files
- Replaces position delete files in practice

### Copy-on-Write vs Merge-on-Read

| Strategy | Write behavior | Read behavior | Best for |
|----------|---------------|---------------|----------|
| Copy-on-Write (COW) | Rewrite entire data file | No reconciliation needed | Read-heavy workloads |
| Merge-on-Read (MOR) | Write small delete file | Reconcile at query time | Write-heavy workloads |

**Configurable per operation** (Spark example):
```python
# Set MOR for deletes, COW for updates
spark.conf.set("spark.sql.iceberg.merge-on-read.enabled.delete", "true")
spark.conf.set("spark.sql.iceberg.merge-on-read.enabled.update", "false")
```

## Metadata Layer

### Metadata files (metadata.json)

JSON files containing the complete table definition:

```json
{
  "format-version": 2,
  "table-uuid": "...",
  "location": "s3://bucket/warehouse/db/table",
  "schema": { "fields": [...] },
  "partition-spec": [...],
  "sort-order": {...},
  "current-snapshot-id": 1234567890,
  "snapshots": [
    {
      "snapshot-id": 1234567890,
      "timestamp-ms": 1719100000000,
      "manifest-list": "s3://bucket/.../snap-1234567890.avro",
      "summary": { "operation": "append", "added-records": "50000" }
    }
  ],
  "properties": {...}
}
```

Each write creates a new metadata.json file. The catalog atomically updates its pointer to the latest metadata file.

### Manifest lists (snap-*.avro)

Avro files listing all manifest files for a specific snapshot:

```
manifest_path                       added_files  existing_files  deleted_files  partition_summaries
s3://bucket/.../manifest-001.avro   5            0               0              [date >= 2024-06-01]
s3://bucket/.../manifest-002.avro   0            120             0              [date < 2024-06-01]
```

- One manifest list per snapshot
- Contains partition summaries for quick pruning
- Reader can skip entire manifests based on query predicates

### Manifest files (manifest-*.avro)

Avro files listing individual data files and delete files:

```
file_path                    partition_data    record_count  file_size  column_sizes  value_counts  null_counts  lower_bounds  upper_bounds
data/part-00001.parquet      {date: 2024-06-15}  100000      45MB      {...}         {...}         {...}        {id: 1}       {id: 99999}
```

- Immutable — once written, never modified
- Contain per-file column-level statistics (min, max, null count, distinct count)
- Enable fine-grained file skipping (data skipping)
- A manifest tracks files in one or more partitions

### Puffin files

Binary sidecar files for statistics and indexes:

- Column-level statistics beyond min/max (e.g., NDV sketches, histograms)
- Deletion vectors (v3) — binary bitmaps for deleted rows
- Extensible blob format for future enhancements
- Reduce the need to scan manifests for statistics

### How a read works

1. Catalog returns current metadata.json location
2. Read metadata.json → find current snapshot → find manifest list
3. Read manifest list → prune manifests by partition summaries
4. Read remaining manifests → prune data files by column statistics
5. Read remaining data files → apply any delete files/deletion vectors
6. Return results

## Catalog Layer

The catalog is responsible for:
- Tracking the current metadata.json pointer for each table
- Providing atomic metadata swaps (ACID guarantee)
- Namespace management (database/schema organization)

### REST Catalog (recommended for new deployments)

Vendor-neutral OpenAPI specification. Implementation details live on the server, not the client.

```python
# Spark config
spark.conf.set("spark.sql.catalog.my_catalog", "org.apache.iceberg.spark.SparkCatalog")
spark.conf.set("spark.sql.catalog.my_catalog.type", "rest")
spark.conf.set("spark.sql.catalog.my_catalog.uri", "https://catalog.example.com")
spark.conf.set("spark.sql.catalog.my_catalog.credential", "client_id:client_secret")
```

**Implementations**: Apache Polaris, Project Nessie, Tabular, Snowflake Open Catalog, Gravitino

**Advantages**: Multi-engine, multi-cloud, language-agnostic, server-side governance

### Hive Metastore

Mature, battle-tested. Majority of current Iceberg deployments.

```python
spark.conf.set("spark.sql.catalog.hive_catalog", "org.apache.iceberg.spark.SparkCatalog")
spark.conf.set("spark.sql.catalog.hive_catalog.type", "hive")
spark.conf.set("spark.sql.catalog.hive_catalog.uri", "thrift://metastore:9083")
```

**Limitations**: Single-table commits only, requires infrastructure management.

### AWS Glue Catalog

Managed, serverless Hive Metastore in AWS.

```python
spark.conf.set("spark.sql.catalog.glue_catalog", "org.apache.iceberg.spark.SparkCatalog")
spark.conf.set("spark.sql.catalog.glue_catalog.catalog-impl", "org.apache.iceberg.aws.glue.GlueCatalog")
spark.conf.set("spark.sql.catalog.glue_catalog.warehouse", "s3://my-bucket/warehouse")
```

**Advantages**: Serverless, integrates with Athena/EMR/Lake Formation.
**Limitations**: AWS lock-in, single-table commits.

### Project Nessie

Git-style versioning for data. Multi-table atomic commits.

```python
spark.conf.set("spark.sql.catalog.nessie_catalog", "org.apache.iceberg.spark.SparkCatalog")
spark.conf.set("spark.sql.catalog.nessie_catalog.catalog-impl", "org.apache.iceberg.nessie.NessieCatalog")
spark.conf.set("spark.sql.catalog.nessie_catalog.uri", "http://nessie:19120/api/v1")
spark.conf.set("spark.sql.catalog.nessie_catalog.ref", "main")
```

**Unique features**: Catalog-level branches, tags, commit history, multi-table transactions, experimentation isolation.

### JDBC Catalog

Simple database-backed catalog. Good for development or smaller deployments.

```python
spark.conf.set("spark.sql.catalog.jdbc_catalog", "org.apache.iceberg.spark.SparkCatalog")
spark.conf.set("spark.sql.catalog.jdbc_catalog.catalog-impl", "org.apache.iceberg.jdbc.JdbcCatalog")
spark.conf.set("spark.sql.catalog.jdbc_catalog.uri", "jdbc:postgresql://host:5432/iceberg")
```

## Format Versions

### v1 — Foundation
- Immutable data files, snapshots, time travel
- Schema evolution via unique column IDs
- Hidden partitioning and partition evolution
- Manifest-level statistics for data skipping
- Atomic metadata swaps (optimistic concurrency)
- Operations: append and partition-level overwrite only

### v2 — Row-Level Operations
- Position delete files and equality delete files
- Merge-on-read architecture
- Row-level UPDATE, DELETE, MERGE
- Writer validation for optimistic concurrency on row-level ops
- Streaming support enabled by row-level deletes

### v3 — Advanced Performance
- **Deletion vectors**: Binary bitmaps in Puffin files (faster than v2 delete files)
- **VARIANT type**: Semi-structured JSON data
- **GEOMETRY/GEOGRAPHY types**: Geospatial analytics
- **Nanosecond timestamps**: Higher precision temporal data
- **Default column values**: Schema evolution without NULL handling complexity
- **Multi-argument transforms**: Composite partitioning strategies

## Setup and Installation

### Spark

```python
from pyspark.sql import SparkSession

spark = SparkSession.builder \
    .appName("iceberg") \
    .config("spark.jars.packages", "org.apache.iceberg:iceberg-spark-runtime-3.5_2.12:1.7.1") \
    .config("spark.sql.extensions", "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions") \
    .config("spark.sql.catalog.local", "org.apache.iceberg.spark.SparkCatalog") \
    .config("spark.sql.catalog.local.type", "hadoop") \
    .config("spark.sql.catalog.local.warehouse", "/tmp/warehouse") \
    .getOrCreate()
```

### Trino

```properties
# /etc/trino/catalog/iceberg.properties
connector.name=iceberg
iceberg.catalog.type=rest
iceberg.rest-catalog.uri=https://catalog.example.com
```

### PyIceberg (Python-native)

```bash
pip install "pyiceberg[s3fs,glue]"
```

```python
from pyiceberg.catalog import load_catalog

catalog = load_catalog("default", **{
    "type": "rest",
    "uri": "https://catalog.example.com"
})

table = catalog.load_table("db.my_table")
df = table.scan().to_pandas()
```

### Flink

```sql
CREATE CATALOG iceberg_catalog WITH (
  'type' = 'iceberg',
  'catalog-type' = 'rest',
  'uri' = 'https://catalog.example.com'
);
```
