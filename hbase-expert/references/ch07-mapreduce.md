# Ch 7 — MapReduce Integration

## Table of Contents
- [Overview](#overview)
- [TableInputFormat — Reading HBase in MapReduce](#tableinputformat--reading-hbase-in-mapreduce)
- [TableOutputFormat — Writing to HBase in MapReduce](#tableoutputformat--writing-to-hbase-in-mapreduce)
- [TableMapper and TableReducer Helpers](#tablemapper-and-tablereducer-helpers)
- [MultiTableInputFormat](#multitableinputformat)
- [Bulk Loading with HFileOutputFormat2](#bulk-loading-with-hfileoutputformat2)
- [Importing Data from HDFS to HBase](#importing-from-hdfs-to-hbase)
- [CopyTable Utility](#copytable-utility)
- [Export / Import Utilities](#export--import-utilities)
- [Spark with HBase](#spark-with-hbase)

---

## Overview

HBase ships with MapReduce integration classes in `hbase-mapreduce` module:

```xml
<dependency>
  <groupId>org.apache.hbase</groupId>
  <artifactId>hbase-mapreduce</artifactId>
  <version>2.5.x</version>
</dependency>
```

Key classes:
| Class | Purpose |
|-------|---------|
| `TableInputFormat` | Scan HBase table as MR input splits |
| `TableOutputFormat` | Write `Put`/`Delete` objects to HBase |
| `TableMapper` | Convenience base class for mappers reading HBase |
| `TableReducer` | Convenience base class for reducers writing HBase |
| `HFileOutputFormat2` | Write HFiles directly (for bulk loading) |
| `LoadIncrementalHFiles` | Bulk-load HFiles into live HBase table |

---

## TableInputFormat — Reading HBase in MapReduce

Each input split corresponds to one HBase **region** (one mapper per region).

```java
Configuration conf = HBaseConfiguration.create();

// Configure which table and scan to use
Job job = Job.getInstance(conf, "HBase Read Job");
job.setJarByClass(MyMapper.class);

// Set the scan
Scan scan = new Scan();
scan.addColumn(Bytes.toBytes("cf"), Bytes.toBytes("status"));
scan.setCaching(500);         // rows per RPC to RegionServer
scan.setCacheBlocks(false);   // don't evict hot blocks during full scan

TableMapReduceUtil.initTableMapperJob(
    "orders",        // table name
    scan,            // scan configuration
    MyMapper.class,  // mapper class
    Text.class,      // output key
    IntWritable.class, // output value
    job
);

// Optional: set TableInputFormat properties directly
conf.set(TableInputFormat.INPUT_TABLE, "orders");
conf.set(TableInputFormat.SCAN,
    TableMapReduceUtil.convertScanToString(scan));
job.setInputFormatClass(TableInputFormat.class);
```

### Example Mapper

```java
public class OrderStatusMapper
        extends TableMapper<Text, IntWritable> {

    private static final byte[] CF     = Bytes.toBytes("cf");
    private static final byte[] STATUS = Bytes.toBytes("status");

    @Override
    public void map(ImmutableBytesWritable rowKey, Result row, Context context)
            throws IOException, InterruptedException {
        byte[] statusBytes = row.getValue(CF, STATUS);
        if (statusBytes != null) {
            String status = Bytes.toString(statusBytes);
            context.write(new Text(status), new IntWritable(1));
        }
    }
}
```

---

## TableOutputFormat — Writing to HBase in MapReduce

```java
TableMapReduceUtil.initTableReducerJob(
    "order_summary",   // output table
    MyReducer.class,   // reducer class
    job
);

// Or set manually:
job.setOutputFormatClass(TableOutputFormat.class);
conf.set(TableOutputFormat.OUTPUT_TABLE, "order_summary");
```

### Example Reducer

```java
public class SummaryReducer
        extends TableReducer<Text, IntWritable, ImmutableBytesWritable> {

    private static final byte[] CF    = Bytes.toBytes("cf");
    private static final byte[] COUNT = Bytes.toBytes("count");

    @Override
    public void reduce(Text key, Iterable<IntWritable> values, Context context)
            throws IOException, InterruptedException {
        int total = 0;
        for (IntWritable val : values) {
            total += val.get();
        }
        Put put = new Put(Bytes.toBytes(key.toString()));
        put.addColumn(CF, COUNT, Bytes.toBytes(total));
        context.write(new ImmutableBytesWritable(put.getRow()), put);
    }
}
```

---

## TableMapper and TableReducer Helpers

`TableMapper<KEYOUT, VALUEOUT>` extends `Mapper<ImmutableBytesWritable, Result, KEYOUT, VALUEOUT>`
`TableReducer<KEYIN, VALUEIN, KEYOUT>` extends `Reducer<KEYIN, VALUEIN, ImmutableBytesWritable, Mutation>`

Use `TableMapReduceUtil` to configure the job cleanly:

```java
// Add HBase dependencies to the distributed cache
TableMapReduceUtil.addDependencyJars(job);
TableMapReduceUtil.addDependencyJarsForClasses(job.getConfiguration(),
    MyClass.class, OtherClass.class);

// Convert scan to/from string for job conf
String scanStr = TableMapReduceUtil.convertScanToString(scan);
Scan recovered = TableMapReduceUtil.convertStringToScan(scanStr);
```

---

## MultiTableInputFormat

Read from multiple tables in a single job:

```java
List<Scan> scans = new ArrayList<>();

Scan scan1 = new Scan();
scan1.addFamily(Bytes.toBytes("cf"));
scan1.setAttribute(Scan.SCAN_ATTRIBUTES_TABLE_NAME, Bytes.toBytes("orders_2024"));
scans.add(scan1);

Scan scan2 = new Scan();
scan2.addFamily(Bytes.toBytes("cf"));
scan2.setAttribute(Scan.SCAN_ATTRIBUTES_TABLE_NAME, Bytes.toBytes("orders_2025"));
scans.add(scan2);

TableMapReduceUtil.initTableMapperJob(scans, MyMapper.class,
    Text.class, IntWritable.class, job);
```

The mapper receives `ImmutableBytesWritable` row key and `Result` as before.

---

## Bulk Loading with HFileOutputFormat2

Bulk loading is the **preferred way to load large datasets** into HBase:
1. MapReduce job writes HFiles directly to HDFS (bypasses MemStore and WAL)
2. `completebulkload` moves HFiles into HBase regions atomically

### Why Bulk Load?

| Normal Puts | Bulk Load |
|-------------|-----------|
| Goes through WAL + MemStore | Writes HFiles directly |
| Causes heavy compaction | No compaction triggered |
| Throttles on handler count | Scales to HDFS write throughput |
| Suitable for incremental writes | Suitable for initial load / large batches |

### Step 1: Generate HFiles

```java
Configuration conf = HBaseConfiguration.create();
Job job = Job.getInstance(conf, "Bulk Load HFile Generation");
job.setJarByClass(BulkLoadMapper.class);

// Input from HDFS
FileInputFormat.addInputPath(job, new Path("/data/input/orders"));
job.setInputFormatClass(TextInputFormat.class);

// Output to HDFS (HFiles)
Path outputPath = new Path("/data/hfiles/orders");
FileOutputFormat.setOutputPath(job, outputPath);

// Configure HFileOutputFormat2
Connection connection = ConnectionFactory.createConnection(conf);
Table table = connection.getTable(TableName.valueOf("orders"));
HFileOutputFormat2.configureIncrementalLoad(job, table, connection.getRegionLocator(TableName.valueOf("orders")));

// Mapper must output: ImmutableBytesWritable (row key) → Put
job.setMapperClass(BulkLoadMapper.class);
job.setMapOutputKeyClass(ImmutableBytesWritable.class);
job.setMapOutputValueClass(Put.class);
```

### BulkLoad Mapper

```java
public class BulkLoadMapper
        extends Mapper<LongWritable, Text, ImmutableBytesWritable, Put> {

    @Override
    public void map(LongWritable key, Text line, Context context)
            throws IOException, InterruptedException {
        String[] fields = line.toString().split(",");
        String orderId = fields[0];
        String status  = fields[1];

        byte[] rowKey = Bytes.toBytes(orderId);
        Put put = new Put(rowKey);
        put.addColumn(Bytes.toBytes("cf"),
                      Bytes.toBytes("status"),
                      Bytes.toBytes(status));

        context.write(new ImmutableBytesWritable(rowKey), put);
    }
}
```

**Critical requirement:** Output keys MUST be in **sorted order** within each partition (HFileOutputFormat2 enforces this via TotalOrderPartitioner).

### Step 2: Load HFiles into HBase

```bash
# After the MR job completes:
bin/hbase completebulkload /data/hfiles/orders orders

# Or programmatically:
```

```java
BulkLoadHFiles loader = BulkLoadHFiles.create(conf);
loader.bulkLoad(TableName.valueOf("orders"), new Path("/data/hfiles/orders"));
```

### Important Considerations

- The HFile output directory must be accessible from RegionServers (HDFS)
- After bulk load, HFiles are moved (not copied) — the output dir is consumed
- Run a major compaction after bulk load to normalize file sizes
- Use `--moveFiles` flag if files are already on HDFS in the right location

---

## Importing from HDFS to HBase

### ImportTsv — TSV/CSV Files

```bash
# Load TSV from HDFS directly via puts
bin/hbase importtsv \
  -Dimporttsv.separator=, \
  -Dimporttsv.columns=HBASE_ROW_KEY,cf:status,cf:amount \
  orders /data/orders.csv

# Generate HFiles instead (then completebulkload)
bin/hbase importtsv \
  -Dimporttsv.separator=, \
  -Dimporttsv.columns=HBASE_ROW_KEY,cf:status,cf:amount \
  -Dimporttsv.bulk.output=/data/hfiles/orders \
  orders /data/orders.csv

bin/hbase completebulkload /data/hfiles/orders orders
```

---

## CopyTable Utility

Copy data between tables (same or different cluster):

```bash
# Copy within same cluster
bin/hbase org.apache.hadoop.hbase.mapreduce.CopyTable \
  --new.name=orders_copy orders

# Copy to a different cluster
bin/hbase org.apache.hadoop.hbase.mapreduce.CopyTable \
  --peer.adr=zk1,zk2,zk3:2181:/hbase \
  --new.name=orders_backup orders

# Copy a time range
bin/hbase org.apache.hadoop.hbase.mapreduce.CopyTable \
  --starttime=1700000000000 --endtime=1800000000000 \
  orders

# Copy specific families
bin/hbase org.apache.hadoop.hbase.mapreduce.CopyTable \
  --families=cf orders
```

---

## Export / Import Utilities

Export table to SequenceFiles on HDFS, then import:

```bash
# Export
bin/hbase org.apache.hadoop.hbase.mapreduce.Export \
  orders /data/exports/orders

# With time range
bin/hbase org.apache.hadoop.hbase.mapreduce.Export \
  orders /data/exports/orders 1 1700000000000 1800000000000
  # args: table output_path versions starttime endtime

# Import
bin/hbase org.apache.hadoop.hbase.mapreduce.Import \
  orders /data/exports/orders

# Import to different table
bin/hbase org.apache.hadoop.hbase.mapreduce.Import \
  -Dimport.bulk.output=/data/hfiles/orders_restored \
  orders_restored /data/exports/orders

bin/hbase completebulkload /data/hfiles/orders_restored orders_restored
```

---

## Spark with HBase

HBase-Spark connector (Apache HBase Connectors project):

```xml
<dependency>
  <groupId>org.apache.hbase.connectors.spark</groupId>
  <artifactId>hbase-spark</artifactId>
  <version>1.0.1</version>
</dependency>
```

```scala
import org.apache.hadoop.hbase.spark.HBaseContext
import org.apache.hadoop.hbase.spark.HBaseScanRDD

val sc: SparkContext = ...
val conf = HBaseConfiguration.create()
val hbaseContext = new HBaseContext(sc, conf)

val scan = new Scan()
scan.addColumn(Bytes.toBytes("cf"), Bytes.toBytes("status"))

val rdd = hbaseContext.hbaseRDD(TableName.valueOf("orders"), scan)
rdd.map { case (key, result) =>
    val status = Bytes.toString(result.getValue(
        Bytes.toBytes("cf"), Bytes.toBytes("status")))
    (Bytes.toString(key.get()), status)
}.toDF("order_id", "status").show()
```

**Alternative: Apache Phoenix** provides SQL interface to HBase with Spark SQL integration.
