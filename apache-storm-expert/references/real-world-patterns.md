# Real-World Storm Patterns
## Chapters 11–12: Log Processing, Twitter Streaming, and ML on Streams

---

## Chapter 11: Apache Log Processing with Storm

### Use Case

Parse and analyze Apache HTTP server access logs in real-time:
- Count requests per URL, status code, or user agent
- Detect traffic spikes or error rate anomalies
- Feed dashboards with live request metrics

### Log Format

Standard Apache Combined Log Format:
```
127.0.0.1 - frank [10/Oct/2000:13:55:36 -0700] "GET /apache_pb.gif HTTP/1.0" 200 2326 "http://www.example.com/start.html" "Mozilla/4.08"
```

Fields: `ip`, `ident`, `user`, `datetime`, `request`, `status`, `bytes`, `referer`, `user_agent`

### Log Processing Topology

```
LogFileSpout (tail log file or Kafka)
    │ shuffle
    ▼
ParseLogBolt (regex parse → ip, method, url, status, bytes, ts)
    │ shuffle
    ├─────────────────────────────────────────────┐
    ▼ fields(url)                                 ▼ fields(status)
UrlCountBolt                               StatusCountBolt
    │ shuffle                                     │ shuffle
    ▼                                             ▼
RedisBolt (url→count)                     AlertBolt (5xx rate > threshold)
```

### Log Spout (Tailing a File)

```java
public class TailFileSpout extends BaseRichSpout {
    private SpoutOutputCollector collector;
    private RandomAccessFile raf;
    private long lastPosition = 0;

    public void open(Map conf, TopologyContext ctx, SpoutOutputCollector collector) {
        this.collector = collector;
        try {
            raf = new RandomAccessFile("/var/log/apache/access.log", "r");
            raf.seek(raf.length()); // start at end of file
            lastPosition = raf.getFilePointer();
        } catch (IOException e) { throw new RuntimeException(e); }
    }

    public void nextTuple() {
        try {
            String line = raf.readLine();
            if (line != null) {
                collector.emit(new Values(line), line);
                lastPosition = raf.getFilePointer();
            } else {
                Utils.sleep(100);
            }
        } catch (IOException e) { throw new RuntimeException(e); }
    }

    public void declareOutputFields(OutputFieldsDeclarer d) {
        d.declare(new Fields("log_line"));
    }
}
```

### Log Parse Bolt

```java
public class ApacheLogParseBolt extends BaseRichBolt {
    private static final Pattern LOG_PATTERN = Pattern.compile(
        "^(\\S+) \\S+ \\S+ \\[([^\\]]+)\\] \"(\\S+) (\\S+) \\S+\" (\\d{3}) (\\d+).*");

    public void execute(Tuple input) {
        String line = input.getStringByField("log_line");
        Matcher m = LOG_PATTERN.matcher(line);
        if (m.matches()) {
            collector.emit(input, new Values(
                m.group(1),   // ip
                m.group(2),   // datetime
                m.group(3),   // method
                m.group(4),   // url
                Integer.parseInt(m.group(5)),  // status
                Long.parseLong(m.group(6))     // bytes
            ));
        }
        collector.ack(input);
    }

    public void declareOutputFields(OutputFieldsDeclarer d) {
        d.declare(new Fields("ip", "datetime", "method", "url", "status", "bytes"));
    }
}
```

### Error Rate Alerting Bolt

```java
public class ErrorRateAlertBolt extends BaseRichBolt {
    private Map<Integer, Long> statusCounts = new HashMap<>();
    private long totalCount = 0;
    private long lastAlertTime = 0;

    public void execute(Tuple input) {
        int status = input.getIntegerByField("status");
        statusCounts.merge(status, 1L, Long::sum);
        totalCount++;

        long now = System.currentTimeMillis();
        if (now - lastAlertTime > 60_000) {  // check every minute
            long errorCount = statusCounts.entrySet().stream()
                .filter(e -> e.getKey() >= 500)
                .mapToLong(Map.Entry::getValue).sum();

            double errorRate = totalCount > 0 ? (double) errorCount / totalCount : 0;
            if (errorRate > 0.05) {  // > 5% error rate
                sendAlert(String.format("5xx error rate: %.1f%%", errorRate * 100));
            }
            statusCounts.clear();
            totalCount = 0;
            lastAlertTime = now;
        }
        collector.ack(input);
    }
}
```

---

## Chapter 12: Twitter Streaming and Machine Learning

### Use Case

1. Stream live tweets via Twitter Streaming API
2. Buffer tweets in Kafka
3. Consume from Kafka in Storm
4. Apply sentiment analysis (ML model)
5. Store results in Redis/Elasticsearch

### Architecture

```
Twitter Streaming API
    │ HTTP stream
    ▼
Tweet Collector (standalone app or Kafka Producer)
    │
    ▼ Kafka topic: raw-tweets
KafkaSpout
    │ shuffle
    ▼
TweetParseBolt (extract text, user, lang, timestamp)
    │ shuffle
    ▼
LanguageFilterBolt (pass only English tweets)
    │ shuffle
    ▼
SentimentBolt (classify: positive/negative/neutral)
    │ fields(sentiment)
    ▼
SentimentCountBolt (count per sentiment per 5-min window)
    │ shuffle
    ├─────────────────────────────────────────────┐
    ▼                                             ▼
RedisBolt (live counts)               ElasticSearchBolt (archive)
```

### Twitter Spout (using Twitter4J)

```java
public class TwitterSpout extends BaseRichSpout {
    private SpoutOutputCollector collector;
    private BlockingQueue<Status> queue = new LinkedBlockingQueue<>(1000);
    private TwitterStream twitterStream;

    public void open(Map conf, TopologyContext ctx, SpoutOutputCollector collector) {
        this.collector = collector;
        ConfigurationBuilder cb = new ConfigurationBuilder()
            .setOAuthConsumerKey((String) conf.get("twitter.consumer.key"))
            .setOAuthConsumerSecret((String) conf.get("twitter.consumer.secret"))
            .setOAuthAccessToken((String) conf.get("twitter.access.token"))
            .setOAuthAccessTokenSecret((String) conf.get("twitter.access.secret"));

        twitterStream = new TwitterStreamFactory(cb.build()).getInstance();
        twitterStream.addListener(new StatusAdapter() {
            public void onStatus(Status status) {
                queue.offer(status);
            }
        });
        twitterStream.sample("en");  // English sample stream
    }

    public void nextTuple() {
        Status status = queue.poll();
        if (status != null) {
            collector.emit(new Values(
                status.getId(),
                status.getText(),
                status.getUser().getScreenName(),
                status.getCreatedAt()
            ), status.getId());
        } else {
            Utils.sleep(50);
        }
    }

    public void declareOutputFields(OutputFieldsDeclarer d) {
        d.declare(new Fields("tweet_id", "text", "user", "created_at"));
    }
}
```

### Kafka Producer for Tweets (Decoupled Architecture)

Better pattern: separate the Twitter API connection from Storm:

```java
// Standalone tweet collector → Kafka
public class TweetKafkaProducer {
    public static void main(String[] args) throws Exception {
        KafkaProducer<String, String> producer = new KafkaProducer<>(producerProps);

        twitterStream.addListener(new StatusAdapter() {
            public void onStatus(Status status) {
                JSONObject tweet = new JSONObject()
                    .put("id", status.getId())
                    .put("text", status.getText())
                    .put("user", status.getUser().getScreenName())
                    .put("ts", status.getCreatedAt().getTime());

                producer.send(new ProducerRecord<>("raw-tweets",
                    String.valueOf(status.getId()),
                    tweet.toString()));
            }
        });
        twitterStream.sample("en");
    }
}
```

Then consume from Kafka with `KafkaSpout` in the Storm topology (see kafka-integration.md).

### Sentiment Analysis Bolt

#### Approach 1: Lexicon-Based (Simple)

```java
public class SentimentBolt extends BaseRichBolt {
    private Map<String, Integer> sentimentLexicon;

    public void prepare(Map conf, TopologyContext ctx, OutputCollector collector) {
        this.collector = collector;
        sentimentLexicon = loadSentimentLexicon();  // load AFINN or SentiWordNet
    }

    public void execute(Tuple input) {
        String text = input.getStringByField("text").toLowerCase();
        String[] words = text.split("\\s+");

        int score = 0;
        for (String word : words) {
            score += sentimentLexicon.getOrDefault(word, 0);
        }

        String sentiment = score > 0 ? "positive" : (score < 0 ? "negative" : "neutral");
        collector.emit(input, new Values(
            input.getLongByField("tweet_id"),
            text,
            sentiment,
            score
        ));
        collector.ack(input);
    }

    public void declareOutputFields(OutputFieldsDeclarer d) {
        d.declare(new Fields("tweet_id", "text", "sentiment", "score"));
    }
}
```

#### Approach 2: ML Model (Scikit-learn / PyTorch via multi-lang)

For Python-based ML models, use Storm's multi-lang protocol:

```java
// Java wrapper for Python sentiment bolt
public class PythonSentimentBolt extends ShellBolt implements IRichBolt {
    public PythonSentimentBolt() {
        super("python3", "sentiment_bolt.py");
    }
    public void declareOutputFields(OutputFieldsDeclarer d) {
        d.declare(new Fields("tweet_id", "text", "sentiment", "confidence"));
    }
}
```

```python
# sentiment_bolt.py
import storm
import pickle

class SentimentBolt(storm.BasicBolt):
    def initialize(self, conf, ctx):
        with open("sentiment_model.pkl", "rb") as f:
            self.model = pickle.load(f)
        with open("vectorizer.pkl", "rb") as f:
            self.vectorizer = pickle.load(f)

    def process(self, tup):
        text = tup.values[1]
        features = self.vectorizer.transform([text])
        sentiment = self.model.predict(features)[0]
        confidence = max(self.model.predict_proba(features)[0])
        storm.emit([tup.values[0], text, sentiment, confidence])

SentimentBolt().run()
```

### Windowed Trending Topics

Use Trident with time-bucketed groupBy for trending hashtags:

```java
TridentTopology topology = new TridentTopology();
topology.newStream("tweets", kafkaSpout)
    .each(new Fields("text"), new ExtractHashtags(), new Fields("hashtag"))
    .each(new Fields("hashtag"), new AddTimeBucket(300), new Fields("bucket"))  // 5-min buckets
    .groupBy(new Fields("bucket", "hashtag"))
    .persistentAggregate(new RedisMapState.opaque(redisOpts),
                         new Count(), new Fields("count"));
```

Query: sort Redis keys for current bucket by count to get trending hashtags.

---

## General Real-Time ML Patterns in Storm

### Load-Once, Score-Many

ML models are expensive to load. Load them in `prepare()`, score in `execute()`:

```java
public class MLScoringBolt extends BaseRichBolt {
    private transient Model model;  // transient: not Java-serialized

    public void prepare(Map conf, TopologyContext ctx, OutputCollector collector) {
        this.collector = collector;
        this.model = ModelLoader.load((String) conf.get("model.path"));
    }

    public void execute(Tuple input) {
        double[] features = extractFeatures(input);
        double score = model.predict(features);
        collector.emit(input, new Values(score));
        collector.ack(input);
    }
}
```

`transient` prevents the field from being serialized when Storm ships the bolt to workers — the model is loaded fresh on each worker during `prepare()`.

### Model Hot-Reload

Periodically check for a new model version without redeploying the topology:

```java
public void execute(Tuple input) {
    if (System.currentTimeMillis() - lastModelCheck > 60_000) {
        String currentVersion = ModelRegistry.getLatestVersion();
        if (!currentVersion.equals(loadedVersion)) {
            model = ModelLoader.load(currentVersion);
            loadedVersion = currentVersion;
        }
        lastModelCheck = System.currentTimeMillis();
    }
    // score with current model
}
```

### Feature Engineering in a Bolt

```java
public class FeatureBolt extends BaseRichBolt {
    public void execute(Tuple input) {
        String text = input.getStringByField("text");

        // Numeric features
        double wordCount = text.split("\\s+").length;
        double exclamationCount = text.chars().filter(c -> c == '!').count();
        double urlCount = countUrls(text);
        double capsRatio = (double) text.chars().filter(Character::isUpperCase).count()
                           / text.length();

        collector.emit(input, new Values(wordCount, exclamationCount, urlCount, capsRatio));
        collector.ack(input);
    }
}
```

### A/B Testing in Topologies

Route traffic to different model versions using fields grouping on a hash:

```java
public class ABRouteBolt extends BaseRichBolt {
    public void execute(Tuple input) {
        String userId = input.getStringByField("user_id");
        String variant = Math.abs(userId.hashCode()) % 10 < 5 ? "model-a" : "model-b";
        collector.emit(variant, input, input.getValues());  // emit to named stream
        collector.ack(input);
    }
    public void declareOutputFields(OutputFieldsDeclarer d) {
        d.declareStream("model-a", new Fields("user_id", "features"));
        d.declareStream("model-b", new Fields("user_id", "features"));
    }
}

// Subscribe each scoring bolt to its designated stream
builder.setBolt("score-a", new ModelABolt(), 4).shuffleGrouping("ab-route", "model-a");
builder.setBolt("score-b", new ModelBBolt(), 4).shuffleGrouping("ab-route", "model-b");
```
