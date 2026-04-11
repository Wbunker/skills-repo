# Metrics Collection and gmetric

From Chapter 4 of *Monitoring with Ganglia* by Bernard Li (O'Reilly).

## Built-In Metric Modules

gmond ships with C modules that collect standard system metrics. Each is activated by a `.conf` snippet in `/etc/ganglia/conf.d/`.

### CPU Metrics (`cpu.conf`)

| Metric | Type | Units | Description |
|--------|------|-------|-------------|
| `cpu_user` | float | % | User-space CPU utilization |
| `cpu_system` | float | % | Kernel CPU utilization |
| `cpu_idle` | float | % | Idle CPU percentage |
| `cpu_wio` | float | % | CPU waiting on I/O |
| `cpu_num` | uint16 | CPUs | Total logical CPU count |
| `cpu_speed` | uint32 | MHz | CPU clock speed |
| `load_one` | float | — | 1-minute load average |
| `load_five` | float | — | 5-minute load average |
| `load_fifteen` | float | — | 15-minute load average |
| `proc_run` | uint32 | procs | Running processes |
| `proc_total` | uint32 | procs | Total processes |

### Memory Metrics (`mem.conf`)

| Metric | Type | Units | Description |
|--------|------|-------|-------------|
| `mem_total` | float | KB | Total physical memory |
| `mem_free` | float | KB | Free memory |
| `mem_shared` | float | KB | Shared memory |
| `mem_buffers` | float | KB | Buffer cache |
| `mem_cached` | float | KB | Page cache |
| `swap_total` | float | KB | Total swap space |
| `swap_free` | float | KB | Free swap space |

### Network Metrics (`net.conf`)

| Metric | Type | Units | Description |
|--------|------|-------|-------------|
| `bytes_in` | float | bytes/sec | Inbound network throughput |
| `bytes_out` | float | bytes/sec | Outbound network throughput |
| `pkts_in` | float | packets/sec | Inbound packet rate |
| `pkts_out` | float | packets/sec | Outbound packet rate |

### Disk Metrics (`disk.conf`)

| Metric | Type | Units | Description |
|--------|------|-------|-------------|
| `disk_free` | double | GB | Free disk on root filesystem |
| `disk_total` | double | GB | Total disk on root filesystem |
| `part_max_used` | float | % | Highest usage across all partitions |

## The `gmetric` Command-Line Tool

`gmetric` injects a custom metric value into the local gmond, which then gossips it to the cluster.

### Basic Syntax

```bash
gmetric --name <name> --value <value> --type <type> \
        [--units <units>] [--slope <slope>] \
        [--tmax <seconds>] [--dmax <seconds>] \
        [--group <group>] [--title <title>] \
        [--desc <description>] [--spoof <host>]
```

### Type Values

| `--type` value | Meaning |
|---------------|---------|
| `string` | Text string |
| `int8` / `uint8` | Signed/unsigned 8-bit int |
| `int16` / `uint16` | Signed/unsigned 16-bit int |
| `int32` / `uint32` | Signed/unsigned 32-bit int |
| `float` | 32-bit float |
| `double` | 64-bit float |

### Slope Values

| `--slope` value | Meaning | RRD type used |
|----------------|---------|--------------|
| `zero` | Value never changes (e.g., hostname) | GAUGE |
| `positive` | Only increases (e.g., counter) | COUNTER |
| `negative` | Only decreases | DERIVE |
| `both` | Can go up or down (e.g., temperature) | GAUGE |
| `unspecified` | Unknown | GAUGE |

### Examples

```bash
# Simple gauge metric
gmetric --name "app_queue_depth" \
        --value 42 \
        --type int32 \
        --units "jobs" \
        --slope both \
        --group "application" \
        --title "Application Queue Depth" \
        --tmax 120 \
        --dmax 600

# Counter (always increasing — bytes written)
gmetric --name "db_writes_total" \
        --value 123456789 \
        --type uint32 \
        --units "bytes" \
        --slope positive \
        --tmax 60

# String metric (status)
gmetric --name "deploy_status" \
        --value "running" \
        --type string \
        --slope zero \
        --tmax 300
```

### tmax and dmax

- **`--tmax`** (seconds): maximum expected update interval. If a metric hasn't been updated within `tmax` seconds, gmond marks it stale. Set to ~2× your cron/script interval.
- **`--dmax`** (seconds): time after which the metric is deleted from gmond's memory. 0 = never expire. Set to a few times `tmax` for transient metrics.

Example for a metric sent every 60 seconds:

```bash
gmetric ... --tmax 120 --dmax 600
```

## Sending Metrics from Scripts

### Cron-Based Collection

```bash
# /etc/cron.d/ganglia-custom
*/1 * * * * ganglia /usr/local/bin/collect-app-metrics.sh
```

```bash
#!/bin/bash
# collect-app-metrics.sh

QUEUE=$(redis-cli llen job_queue 2>/dev/null || echo 0)
gmetric --name "redis_queue_depth" \
        --value "$QUEUE" \
        --type uint32 \
        --units "jobs" \
        --slope both \
        --tmax 120 \
        --dmax 600 \
        --group "redis"
```

### Python Script

```python
#!/usr/bin/env python3
import subprocess

def send_metric(name, value, mtype, units='', slope='both',
                tmax=120, dmax=600, group='custom'):
    subprocess.run([
        'gmetric',
        '--name', name,
        '--value', str(value),
        '--type', mtype,
        '--units', units,
        '--slope', slope,
        '--tmax', str(tmax),
        '--dmax', str(dmax),
        '--group', group,
    ], check=True)

# Example usage
send_metric('http_latency_ms', 45.2, 'float', units='ms', group='web')
```

## Metric Spoofing

Spoofing lets you inject a metric as if it came from a different host — useful for central collectors or when the emitting host is different from the monitored host.

```bash
gmetric --name "cpu_user" \
        --value 25.3 \
        --type float \
        --units "%" \
        --spoof "db-server-01:10.0.0.50"
        # format: "hostname:ip"
```

The spoofed metric appears in gweb under the specified hostname. The local gmond receives it and gossips it as if that host sent it.

## Metric Grouping

Group related metrics for better gweb organization:

```bash
gmetric --name "jvm_heap_used_mb" --value 512 --type float \
        --units "MB" --group "jvm" --slope both

gmetric --name "jvm_gc_time_ms" --value 23 --type uint32 \
        --units "ms/s" --group "jvm" --slope both
```

In gweb, metrics with the same `--group` are displayed together in the "Metric Summary" view.

## Collecting Metrics from Network Equipment

Using gmetric with SNMP polling (external script):

```bash
#!/bin/bash
# Poll a switch interface counter via SNMP, send to Ganglia
OID=".1.3.6.1.2.1.2.2.1.10.1"  # ifInOctets on interface 1
VALUE=$(snmpget -v2c -c public switch01 "$OID" | awk '{print $NF}')

gmetric --name "switch01_if1_in_bytes" \
        --value "$VALUE" \
        --type uint32 \
        --units "bytes" \
        --slope positive \
        --spoof "switch01:192.168.1.1" \
        --tmax 300
```
