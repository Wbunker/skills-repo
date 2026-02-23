# Working with Monitoring Standards

Reference for JMX, DogStatsD, SNMP, and client libraries for extending Datadog.

## Table of Contents
- [DogStatsD](#dogstatsd)
- [JMX Monitoring](#jmx-monitoring)
- [SNMP Monitoring](#snmp-monitoring)
- [Client Libraries](#client-libraries)

## DogStatsD

DogStatsD is a metrics aggregation service bundled with the Agent. Applications send metrics over UDP (port 8125) and the Agent aggregates and forwards them to Datadog.

### Protocol
UDP-based, extended StatsD format:
```
<METRIC_NAME>:<VALUE>|<TYPE>|@<SAMPLE_RATE>|#<TAG1>,<TAG2>
```

Types: `c` (count), `g` (gauge), `ms` (timer), `h` (histogram), `d` (distribution), `s` (set)

### Python Client
```python
from datadog import initialize, statsd

initialize(statsd_host='127.0.0.1', statsd_port=8125)

# Count
statsd.increment('app.page.views', tags=['page:home', 'env:prod'])
statsd.decrement('app.queue.size')

# Gauge
statsd.gauge('app.active_connections', 42, tags=['service:api'])

# Histogram (generates avg, median, max, 95th, count)
statsd.histogram('app.request.duration', 0.234, tags=['endpoint:/users'])

# Distribution (server-side aggregation, more accurate)
statsd.distribution('app.request.latency', 0.042, tags=['endpoint:/users'])

# Set (unique counts)
statsd.set('app.users.uniques', user_id, tags=['env:prod'])

# Timed decorator
@statsd.timed('app.function.runtime')
def my_function():
    pass

# Context manager
with statsd.timed('app.db.query_time', tags=['query:get_users']):
    results = db.query("SELECT * FROM users")

# Events
statsd.event('Deploy completed', 'v2.3.1 deployed to production',
             alert_type='success', tags=['env:prod'])

# Service checks
statsd.service_check('app.health', statsd.OK,
                     message='Service is healthy', tags=['service:api'])
```

### Other Language Clients

**Ruby:**
```ruby
require 'datadog/statsd'
statsd = Datadog::Statsd.new('127.0.0.1', 8125)
statsd.increment('app.page.views', tags: ['page:home'])
statsd.gauge('app.queue.size', 42)
statsd.histogram('app.request.duration', 0.234)
```

**Go:**
```go
import "github.com/DataDog/datadog-go/v5/statsd"

client, _ := statsd.New("127.0.0.1:8125")
client.Incr("app.page.views", []string{"page:home"}, 1)
client.Gauge("app.queue.size", 42, []string{"service:api"}, 1)
client.Histogram("app.request.duration", 0.234, []string{"endpoint:/users"}, 1)
```

**Java:**
```java
import com.timgroup.statsd.NonBlockingStatsDClient;

StatsDClient statsd = new NonBlockingStatsDClient("app", "localhost", 8125);
statsd.incrementCounter("page.views", "page:home");
statsd.recordGaugeValue("queue.size", 42, "service:api");
statsd.recordHistogramValue("request.duration", 234, "endpoint:/users");
```

**Node.js:**
```javascript
const StatsD = require('hot-shots');
const client = new StatsD({ host: '127.0.0.1', port: 8125, prefix: 'app.' });

client.increment('page.views', { page: 'home' });
client.gauge('queue.size', 42, { service: 'api' });
client.histogram('request.duration', 234, { endpoint: '/users' });
```

### DogStatsD Configuration
In `datadog.yaml`:
```yaml
dogstatsd_port: 8125
dogstatsd_non_local_traffic: true  # Accept from remote hosts (containers)
dogstatsd_buffer_size: 8192
dogstatsd_tags:
  - env:production
```

### Unix Domain Socket (UDS)
Higher performance, no network overhead:
```yaml
# datadog.yaml
dogstatsd_socket: /var/run/datadog/dsd.socket
```

```python
initialize(statsd_socket_path='/var/run/datadog/dsd.socket')
```

### Sampling
Reduce volume for high-throughput metrics:
```python
statsd.increment('app.requests', sample_rate=0.5)  # Only send 50% of calls
```

## JMX Monitoring

Java Management Extensions (JMX) exposes Java application metrics as MBeans. Datadog Agent connects to JMX remotely or locally to collect these metrics.

### Enable JMX on Java Application
```bash
java -Dcom.sun.management.jmxremote \
     -Dcom.sun.management.jmxremote.port=9999 \
     -Dcom.sun.management.jmxremote.authenticate=false \
     -Dcom.sun.management.jmxremote.ssl=false \
     -jar myapp.jar
```

### JMX Integration Config
```yaml
# /etc/datadog-agent/conf.d/jmx.d/conf.yaml
init_config:
  is_jmx: true

instances:
  - host: localhost
    port: 9999
    tags:
      - service:myapp
      - env:production

    conf:
      # Collect specific MBeans
      - include:
          domain: java.lang
          type: Memory
          attribute:
            HeapMemoryUsage.used:
              alias: jvm.heap.used
              metric_type: gauge
            NonHeapMemoryUsage.used:
              alias: jvm.nonheap.used
              metric_type: gauge

      - include:
          domain: java.lang
          type: Threading
          attribute:
            ThreadCount:
              alias: jvm.thread.count
              metric_type: gauge

      - include:
          domain: java.lang
          type: GarbageCollector
          attribute:
            CollectionCount:
              alias: jvm.gc.collection_count
              metric_type: counter
            CollectionTime:
              alias: jvm.gc.collection_time
              metric_type: counter
```

### Cassandra (JMX Example)
```yaml
# /etc/datadog-agent/conf.d/cassandra.d/conf.yaml
init_config:
  is_jmx: true

instances:
  - host: localhost
    port: 7199
    tags:
      - service:cassandra

    conf:
      - include:
          domain: org.apache.cassandra.metrics
          type: ClientRequest
          scope: Read
          name: Latency
          attribute:
            99thPercentile:
              alias: cassandra.read.latency.99th
              metric_type: gauge
```

### Kafka (JMX Example)
```yaml
# /etc/datadog-agent/conf.d/kafka.d/conf.yaml
init_config:
  is_jmx: true

instances:
  - host: localhost
    port: 9999
    tags:
      - service:kafka
```
Datadog provides OOTB Kafka metrics via its Kafka integration; custom JMX beans can supplement these.

### JMX Troubleshooting
```bash
# Test JMX connectivity
sudo datadog-agent jmx list everything

# List matching beans
sudo datadog-agent jmx list matching

# List collected metrics
sudo datadog-agent jmx list collected

# List beans with errors
sudo datadog-agent jmx list with-metrics
```

## SNMP Monitoring

Simple Network Management Protocol for monitoring network devices (routers, switches, firewalls, printers).

### SNMP v2c Config
```yaml
# /etc/datadog-agent/conf.d/snmp.d/conf.yaml
init_config:

instances:
  - ip_address: 192.168.1.1
    community_string: public
    snmp_version: 2
    tags:
      - device:core-router
    metrics:
      - OID: 1.3.6.1.2.1.1.3.0
        name: sysUpTime
      - OID: 1.3.6.1.2.1.2.2.1.10
        name: ifInOctets
        metric_tags:
          - tag: interface
            index: 1
      - OID: 1.3.6.1.2.1.2.2.1.16
        name: ifOutOctets
        metric_tags:
          - tag: interface
            index: 1
```

### SNMP v3 Config
```yaml
instances:
  - ip_address: 192.168.1.1
    snmp_version: 3
    user: datadogUser
    authProtocol: SHA
    authKey: <auth_key>
    privProtocol: AES
    privKey: <priv_key>
```

### Network Device Monitoring (NDM)
Datadog's NDM extends basic SNMP with:
- Auto-discovery of devices on subnets
- Device profiles (pre-built for Cisco, Juniper, Palo Alto, etc.)
- Topology mapping
- Interface dashboard OOTB

```yaml
# Auto-discovery
init_config:

instances:
  - network_address: 192.168.1.0/24
    community_string: public
    loader: core
```

## Client Libraries

### REST API Client Libraries
Official Datadog API clients for programmatic access:

| Language | Package |
|----------|---------|
| Python | `datadog-api-client-python` |
| Go | `datadog-api-client-go` |
| Ruby | `datadog-api-client-ruby` |
| Java | `datadog-api-client-java` |
| TypeScript | `@datadog/datadog-api-client` |

### DogStatsD Client Libraries
| Language | Package |
|----------|---------|
| Python | `datadog` (includes statsd) |
| Go | `datadog-go` |
| Ruby | `dogstatsd-ruby` |
| Java | `java-dogstatsd-client` |
| Node.js | `hot-shots` |
| .NET | `DogStatsD-CSharp-Client` |
| PHP | `php-datadogstatsd` |
