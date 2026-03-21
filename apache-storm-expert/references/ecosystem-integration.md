# Storm Ecosystem Integration
## Chapters 9–10: Hadoop, HBase, Redis, Elasticsearch, and Esper

---

## Storm and Hadoop/HDFS Integration

### Why Integrate with HDFS?

Storm processes streams in real-time; HDFS provides durable long-term storage. A common pattern is to persist Storm output to HDFS for:
- Batch analytics (Hive/Spark queries over historical data)
- Long-term archival
- Replay and reprocessing

### HDFS Bolt (storm-hdfs)

```xml
<dependency>
    <groupId>org.apache.storm</groupId>
    <artifactId>storm-hdfs</artifactId>
    <version>2.4.0</version>
</dependency>
```

```java
// Write tuples to HDFS as delimited text
RecordFormat format = new DelimitedRecordFormat()
    .withFieldDelimiter("\t");

FileNameFormat fileNameFormat = new DefaultFileNameFormat()
    .withPath("/storm/events/")
    .withPrefix("events-")
    .withExtension(".txt");

SyncPolicy syncPolicy = new CountSyncPolicy(1000);  // sync every 1000 tuples
RotationPolicy rotationPolicy = new FileSizeRotationPolicy(128, Units.MB);

HdfsBolt bolt = new HdfsBolt()
    .withFsUrl("hdfs://namenode:9000")
    .withFileNameFormat(fileNameFormat)
    .withRecordFormat(format)
    .withSyncPolicy(syncPolicy)
    .withRotationPolicy(rotationPolicy);

builder.setBolt("hdfs-bolt", bolt, 2).shuffleGrouping("processing-bolt");
```

### Rotation Policies

| Policy | Trigger |
|--------|---------|
| `FileSizeRotationPolicy(128, MB)` | Rotate when file reaches 128 MB |
| `TimedRotationPolicy(60, MINUTES)` | Rotate every 60 minutes |
| `NoRotationPolicy` | Never rotate (manual management) |

### Rotation Actions

After rotation (file closed), optionally move/rename:

```java
bolt.addRotationAction(new MoveFileAction()
    .withDestination("/storm/events/archive/"));
```

### Sequence Files and Avro

```java
// Write as Avro
AvroGenericRecordBolt avroBolt = new AvroGenericRecordBolt()
    .withFsUrl("hdfs://namenode:9000")
    .withSourceParallelism(2)
    .withFileNameFormat(fileNameFormat)
    .withRotationPolicy(rotationPolicy)
    .withSchema(avroSchema);
```

---

## Storm and HBase Integration

### Why HBase?

HBase provides random-read/write access to HDFS-backed storage. Storm writes per-record results; downstream systems query by row key.

### HBase Bolt (storm-hbase)

```xml
<dependency>
    <groupId>org.apache.storm</groupId>
    <artifactId>storm-hbase</artifactId>
    <version>2.4.0</version>
</dependency>
```

```java
// Define column family mapper
SimpleHBaseMapper mapper = new SimpleHBaseMapper()
    .withRowKeyField("user_id")
    .withColumnFamily("cf")
    .withColumnFields(new Fields("event_type", "count"))
    .withCounterFields(new Fields("count"));  // auto-increment

// Create HBase bolt
HBaseBolt hbaseBolt = new HBaseBolt("UserEvents", mapper)
    .withConfigKey("hbase.conf");

// HBase connection config
Map<String, Object> hbaseConf = new HashMap<>();
hbaseConf.put("hbase.rootdir", "hdfs://namenode:9000/hbase");
hbaseConf.put("hbase.zookeeper.quorum", "zk1,zk2,zk3");
conf.put("hbase.conf", hbaseConf);

builder.setBolt("hbase-bolt", hbaseBolt, 4).shuffleGrouping("count-bolt");
```

### HBase Lookup (Spout or Bolt)

Use `HBaseValueMapper` for lookups during processing:

```java
HBaseLookupBolt lookupBolt = new HBaseLookupBolt("UserProfiles",
    new SimpleHBaseLookupMapper(new Fields("profile_data"), "cf", "profile"),
    new UserIdLookupMapper());  // maps input tuple to row key

builder.setBolt("enrich-bolt", lookupBolt, 2)
       .fieldsGrouping("parse-bolt", new Fields("user_id"));
```

### HBase Trident State

For exactly-once writes to HBase via Trident:

```java
TridentHBaseMapState.Options opts = new TridentHBaseMapState.Options();
opts.tableName = "WordCounts";
opts.columnFamily = "cf";
opts.columnName = "count";

TridentState state = stream
    .groupBy(new Fields("word"))
    .persistentAggregate(
        TridentHBaseMapState.transactional(opts),
        new Count(), new Fields("count"));
```

---

## Storm and Redis Integration

### Use Cases

- **Caching**: Enrichment lookups (user profiles, config data)
- **State storage**: Trident state backend for exactly-once counts
- **Pub/Sub**: Publish processed results to Redis channels
- **Rate limiting**: Track per-key counters in Redis

### Redis Bolt (storm-redis)

```xml
<dependency>
    <groupId>org.apache.storm</groupId>
    <artifactId>storm-redis</artifactId>
    <version>2.4.0</version>
</dependency>
```

```java
JedisPoolConfig poolConfig = new JedisPoolConfig.Builder()
    .setHost("redis.example.com")
    .setPort(6379)
    .setTimeout(2000)
    .setMaxTotal(20)
    .build();

// Store tuple fields as Redis hash
RedisStoreMapper storeMapper = new WordCountStoreMapper();
// Implement RedisStoreMapper:
//   getKeyFromTuple(Tuple t) → Redis key
//   getAdditionalKey(Tuple t) → Hash field (for HSET)
//   getExpireIntervalSec() → TTL (-1 = no expiry)

RedisStoreBolt redisBolt = new RedisStoreBolt(poolConfig, storeMapper);
builder.setBolt("redis-bolt", redisBolt, 2).shuffleGrouping("count-bolt");
```

### Redis Lookup Bolt

Enrich tuples with data from Redis:

```java
public class RedisEnrichBolt extends AbstractRedisBolt {
    public RedisEnrichBolt(JedisPoolConfig config) { super(config); }

    public void execute(Tuple input) {
        try (Jedis jedis = container.getInstance()) {
            String userId = input.getStringByField("user_id");
            String profile = jedis.hget("user-profiles", userId);
            collector.emit(input, new Values(userId, profile));
            collector.ack(input);
        }
    }
}
```

### Redis as Trident State

```java
RedisState.Options redisOpts = new RedisState.Options();
redisOpts.host = "redis.example.com";
redisOpts.port = 6379;
redisOpts.expireIntervalSec = 3600;  // 1 hour TTL

TridentState counts = stream
    .groupBy(new Fields("user_id"))
    .persistentAggregate(
        RedisMapState.opaque(redisOpts),
        new Count(), new Fields("count"));
```

---

## Storm and Elasticsearch Integration

### Use Cases

- Real-time full-text search indexing
- Event log analytics (ELK stack integration)
- Storing structured analytics results for Kibana dashboards

### Elasticsearch Bolt (storm-elasticsearch)

```java
EsConfig esConfig = new EsConfig("http://elasticsearch:9200");

// Define mapper: tuple → Elasticsearch document
EsTupleMapper mapper = EsMapperFactory.createDefaultEsMapper(
    "events",        // index name
    "user-event",    // document type (ES 7.x: use "_doc")
    "event_id",      // tuple field for document ID
    null             // source — null means use all fields
);

EsBolt esBolt = new EsBolt(esConfig, mapper);
builder.setBolt("es-bolt", esBolt, 4).shuffleGrouping("parse-bolt");
```

### Custom ES Document Mapper

```java
public class EventEsMapper implements EsTupleMapper {
    public String getIndex(Tuple tuple) {
        return "events-" + tuple.getStringByField("date");  // daily index
    }
    public String getType(Tuple tuple) { return "_doc"; }
    public String getId(Tuple tuple) { return tuple.getStringByField("event_id"); }
    public String getSource(Tuple tuple) {
        return new JSONObject()
            .put("user_id", tuple.getStringByField("user_id"))
            .put("event_type", tuple.getStringByField("event_type"))
            .put("timestamp", tuple.getLongByField("ts"))
            .toString();
    }
}
```

---

## Storm and Esper (Complex Event Processing)

Esper is an in-process CEP (Complex Event Processing) engine that runs inside Storm bolts to enable:
- **Sliding time windows**: sum/count over the last N seconds
- **Event correlation**: detect sequences of events across streams
- **Pattern matching**: "alert if event A is followed by event B within 5 minutes"

### Esper Bolt Pattern

```java
public class EsperBolt extends BaseRichBolt {
    private EPServiceProvider epService;
    private OutputCollector collector;

    public void prepare(Map conf, TopologyContext ctx, OutputCollector collector) {
        this.collector = collector;
        Configuration esConfig = new Configuration();
        esConfig.addEventType("UserEvent", UserEvent.class);
        epService = EPServiceProviderManager.getDefaultProvider(esConfig);

        // Sliding window: count events per user over last 60 seconds
        String epl = "SELECT user_id, count(*) as cnt " +
                     "FROM UserEvent.win:time(60 sec) " +
                     "GROUP BY user_id";

        EPStatement stmt = epService.getEPAdministrator().createEPL(epl);
        stmt.addListener((newEvents, oldEvents) -> {
            for (EventBean event : newEvents) {
                collector.emit(new Values(
                    event.get("user_id"),
                    event.get("cnt")
                ));
            }
        });
    }

    public void execute(Tuple input) {
        UserEvent event = new UserEvent(
            input.getStringByField("user_id"),
            input.getLongByField("timestamp")
        );
        epService.getEPRuntime().sendEvent(event);
        collector.ack(input);
    }
}
```

### Common Esper EPL Patterns

```sql
-- Sliding count window
SELECT user_id, count(*) FROM UserEvent.win:length(100) GROUP BY user_id

-- Sliding time window
SELECT user_id, sum(amount) FROM OrderEvent.win:time(5 min) GROUP BY user_id

-- Event sequence detection (A then B within 10 minutes)
SELECT * FROM PATTERN [
    every a=LoginEvent ->
    b=FailedLoginEvent(user_id = a.user_id)
    where timer:within(10 min)
]

-- Threshold alert
SELECT user_id FROM UserEvent.win:time(1 min)
GROUP BY user_id HAVING count(*) > 100
```

---

## Integration Pattern Summary

| Sink | Use Case | Library | Write Pattern |
|------|----------|---------|---------------|
| HDFS | Archival, batch analytics | storm-hdfs | HdfsBolt with rotation |
| HBase | Random-access lookups, row-key queries | storm-hbase | HBaseBolt / HBaseValueMapper |
| Redis | Caching, fast counters, Trident state | storm-redis | RedisStoreBolt / Trident RedisMapState |
| Elasticsearch | Full-text search, Kibana analytics | storm-elasticsearch | EsBolt |
| Kafka | Downstream stream processing | storm-kafka-client | KafkaBolt |
| RDBMS | Relational queries, reports | JDBC Bolt (custom) | Custom AbstractRichBolt + JDBC |
| Esper | Windowed aggregations, CEP in-bolt | Esper (embedded) | EsperBolt wrapping EPL statements |
