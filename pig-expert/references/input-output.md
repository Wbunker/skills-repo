# Input and Output
_Ch. 6 of "Programming Pig" — Load/Store functions, file formats, cloud storage, HCatalog/Hive Metastore_

## Built-in Load/Store Functions

### PigStorage (default)

```pig
-- Load tab-separated (default delimiter)
a = LOAD 'path/' USING PigStorage() AS (f1:int, f2:chararray);

-- Custom delimiter
b = LOAD 'path/' USING PigStorage(',') AS (...);
b = LOAD 'path/' USING PigStorage('|') AS (...);
b = LOAD 'path/' USING PigStorage('\u0001') AS (...);  -- Hive default (SOH)

-- Store
STORE result INTO 'output/' USING PigStorage('\t');
STORE result INTO 'output/' USING PigStorage(',');

-- Multi-character delimiter: not supported natively — use a UDF or pre-process
```

### TextLoader

```pig
-- Loads each line as a single chararray field
lines = LOAD 'path/' USING TextLoader() AS (line:chararray);

-- Useful for log files, free-form text, pre-parsing
```

### JsonLoader / JsonStorage

```pig
-- Built-in since Pig 0.8
-- JsonLoader: schema must be declared; nested structures mapped to bags/tuples/maps
json_data = LOAD 'path/' USING JsonLoader('id:int, name:chararray, tags:bag{t:(tag:chararray)}');

-- JsonStorage: writes each tuple as a JSON object
STORE result INTO 'output/' USING JsonStorage();
```

### BinStorage (binary, internal format)

```pig
-- Used for intermediate storage between jobs
-- Not human-readable; faster than text
STORE tmp INTO 'scratch/' USING BinStorage();
loaded = LOAD 'scratch/' USING BinStorage() AS (...);
```

## Piggybank and Community UDFs

Piggybank is the official Pig UDF library. Register from your cluster or cloud storage:

```pig
REGISTER '/usr/lib/pig/piggybank.jar';
-- or
REGISTER 's3://bucket/libs/piggybank-0.17.0.jar';
REGISTER 'gs://bucket/libs/piggybank-0.17.0.jar';
```

### CSV with Excel compatibility

```pig
DEFINE CSVLoader org.apache.pig.piggybank.storage.CSVExcelStorage();
-- Handles quoted fields, embedded commas, multiline fields

data = LOAD 'path/' USING CSVLoader() AS (id:int, desc:chararray, amount:float);
STORE result INTO 'output/' USING CSVLoader();

-- With explicit delimiter and options:
DEFINE CsvCustom org.apache.pig.piggybank.storage.CSVExcelStorage(',', 'NO_MULTILINE', 'UNIX', 'WRITE_OUTPUT_HEADER');
```

## Columnar Formats (Modern — Recommended)

### ORC (Optimized Row Columnar)

OrcStorage is included in Pig 0.15+.

```pig
-- Load ORC
orc_data = LOAD 'path/' USING OrcStorage() AS (id:int, name:chararray, amount:float);

-- Store ORC (schema inferred from relation)
STORE result INTO 'output/' USING OrcStorage();

-- With compression
STORE result INTO 'output/' USING OrcStorage('-c SNAPPY');
STORE result INTO 'output/' USING OrcStorage('-c ZLIB');
```

### Parquet

Requires parquet-pig library (included in most EMR/Dataproc Pig distributions).

```pig
REGISTER '/usr/lib/pig/lib/parquet-pig.jar';  -- path varies by cluster

DEFINE ParquetLoader parquet.pig.ParquetLoader;
DEFINE ParquetStorer parquet.pig.ParquetStorer;

-- Load
parquet_data = LOAD 'path/' USING ParquetLoader() AS (...);

-- Store
STORE result INTO 'output/' USING ParquetStorer();

-- AWS EMR: parquet-pig typically pre-registered
-- GCP Dataproc: verify jar path with ls /usr/lib/pig/lib/
```

### Avro

```pig
REGISTER '/usr/lib/pig/lib/piggybank.jar';

DEFINE AvroStorage org.apache.pig.piggybank.storage.avro.AvroStorage;

-- Load (schema inferred from Avro file)
avro_data = LOAD 'path/' USING AvroStorage();

-- Store
STORE result INTO 'output/' USING AvroStorage('{"debug": 5}');

-- Store with explicit schema
STORE result INTO 'output/' USING AvroStorage(
    '{"schema": {"type":"record","name":"Result","fields":[{"name":"id","type":"int"}]}}'
);
```

## HCatalog / Hive Metastore Integration

HCatalog allows reading and writing Hive-managed tables directly from Pig.

```pig
-- Enable HCatalog (required before using HCatLoader/HCatStorer)
-- On EMR: add --properties-file /etc/pig/conf/pig-env.sh with PIG_CLASSPATH set
-- Or launch with: pig -useHCatalog

-- Load from Hive table
events = LOAD 'mydb.events' USING org.apache.hive.hcatalog.pig.HCatLoader();
-- Schema is inferred from the Hive table definition automatically

-- Store to Hive table (table must already exist)
STORE result INTO 'mydb.output_table'
    USING org.apache.hive.hcatalog.pig.HCatStorer();

-- Partitioned table: specify partition values
STORE result INTO 'mydb.daily_events'
    USING org.apache.hive.hcatalog.pig.HCatStorer('date=2024-01-15');

-- EMR: Hive Metastore can be AWS Glue Data Catalog
-- GCP Dataproc: Hive Metastore can be Cloud SQL (MySQL) or Dataproc Metastore service
```

### AWS Glue Data Catalog as Hive Metastore (EMR)

```bash
# Enable Glue catalog at cluster creation:
aws emr create-cluster \
  --configurations '[{"Classification":"hive-site","Properties":{"hive.metastore.client.factory.class":"com.amazonaws.glue.catalog.metastore.AWSGlueDataCatalogHiveClientFactory"}}]' \
  ...
```

```pig
-- Then HCatLoader reads Glue tables directly
events = LOAD 'my_glue_database.events' USING org.apache.hive.hcatalog.pig.HCatLoader();
```

## Cloud Storage Paths

### AWS S3

```pig
-- Standard S3 path
data = LOAD 's3://bucket-name/prefix/year=2024/' USING PigStorage(',') AS (...);

-- Glob pattern
data = LOAD 's3://bucket/prefix/*/events/' USING PigStorage(',') AS (...);

-- Output
STORE result INTO 's3://bucket/output/2024-01-15/' USING PigStorage('\t');

-- S3A (preferred on EMR 6.x — higher performance)
data = LOAD 's3a://bucket/prefix/' USING PigStorage('\t') AS (...);
```

**Important:** S3 output is written to a temporary directory and moved on commit. Check `_SUCCESS` file to verify job completion.

### GCP GCS

```pig
-- GCS path
data = LOAD 'gs://bucket-name/prefix/' USING PigStorage(',') AS (...);

-- Glob
data = LOAD 'gs://bucket/prefix/*/events/' USING PigStorage(',') AS (...);

-- Output
STORE result INTO 'gs://bucket/output/' USING PigStorage('\t');
```

## Format Selection Guide

```
What are your requirements?
├── Human-readable, simple ETL → PigStorage (TSV/CSV)
├── Interoperability with Hive/Spark/Presto → ORC or Parquet
│   ├── Hive-heavy environment → ORC (Hive's native format)
│   └── Spark/general ecosystem → Parquet
├── Schema evolution needs → Avro
├── Existing Hive tables → HCatLoader (reads table format transparently)
└── Intermediate scratch data → BinStorage (fastest, Pig-internal)

Compression:
├── ORC: built-in SNAPPY or ZLIB
├── Parquet: SNAPPY (default), GZIP
├── PigStorage output: use STORE ... USING PigStorage() with
│   SET mapreduce.output.fileoutputformat.compress true;
│   SET mapreduce.output.fileoutputformat.compress.codec org.apache.hadoop.io.compress.GzipCodec;
└── Or use Snappy codec for splittable compression
```

## Multiple Inputs / Outputs

```pig
-- Load from multiple paths (union automatically)
all_data = LOAD '{s3://bucket/2024/01/,s3://bucket/2024/02/}' USING PigStorage(',') AS (...);

-- Multiple STORE in one script (multi-query optimization kicks in)
STORE high_value INTO 's3://bucket/output/high/' USING PigStorage('\t');
STORE low_value  INTO 's3://bucket/output/low/'  USING PigStorage('\t');
-- Pig optimizer may merge these into a single scan of the input
```
