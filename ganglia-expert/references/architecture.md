# Ganglia Architecture

From Chapter 1 of *Monitoring with Ganglia* by Bernard Li (O'Reilly).

## What Is Ganglia?

Ganglia is a scalable distributed monitoring system designed for high-performance computing clusters and grids. Key design goals:

- **Low overhead** — lightweight agents on each node
- **Scalability** — tested on clusters of thousands of nodes
- **Fault tolerance** — gossip protocol handles node failures gracefully
- **Hierarchical** — supports cluster-level and grid-level aggregation

## Component Roles

### gmond (Ganglia Monitoring Daemon)

Runs on every monitored node. Responsibilities:

1. **Collect** metrics via built-in C modules and optional Python modules
2. **Gossip** metric data to cluster peers over UDP (multicast or unicast)
3. **Serve** the current cluster state as XML over TCP on request

gmond maintains a soft-state in-memory table of all metric values it has heard from peers. This table expires if no refreshes arrive (TTL-based).

### gmetad (Ganglia Meta Daemon)

Runs on one or more aggregation hosts. Responsibilities:

1. **Poll** gmond nodes (or other gmetad instances for grid federation) at a configurable interval
2. **Store** metric time series in RRD (Round Robin Database) files
3. **Serve** aggregated XML for gweb and other consumers

gmetad is stateful: it owns the RRD files and persists data across restarts.

### gweb (Ganglia Web Frontend)

PHP (original) or Python/Django application. Reads RRD files directly (or via gmetad) and renders graphs using RRDtool. Provides:

- Per-node, per-cluster, and grid-level views
- Metric comparison across nodes
- Configurable time ranges

## Gossip Protocol

gmond uses a **peer-to-peer gossip** (epidemic) protocol:

1. Each node periodically broadcasts its own metrics to the multicast group (or configured unicast peers)
2. Each node also forwards metrics it has received from peers
3. This creates redundancy — no single point of failure for metric propagation

Key parameters controlling gossip:

| Parameter | Default | Effect |
|-----------|---------|--------|
| `host_dmax` | 86400 s | Time before a silent host is removed from the table |
| `cleanup_threshold` | 300 s | How often gmond prunes expired entries |
| `send_metadata_interval` | 0 (startup only) | How often to re-send metadata headers |
| `max_udp_msg_len` | 1472 | MTU-safe UDP payload size |

## Metric XML Format

When you `telnet <gmond-host> 8649`, gmond returns XML like:

```xml
<GANGLIA_XML VERSION="3.6.0" SOURCE="gmond">
  <CLUSTER NAME="my_cluster" LOCALTIME="1234567890" ...>
    <HOST NAME="node01" IP="10.0.0.1" REPORTED="1234567890" ...>
      <METRIC NAME="cpu_user" VAL="12.5" TYPE="float"
              UNITS="%" TN="15" TMAX="60" DMAX="0"
              SLOPE="both" SOURCE="gmond">
        <EXTRA_ELEMENT NAME="GROUP" VAL="cpu"/>
        <EXTRA_ELEMENT NAME="DESC" VAL="Percentage of CPU utilization..."/>
      </METRIC>
      ...
    </HOST>
  </CLUSTER>
</GANGLIA_XML>
```

Important XML attributes on `<METRIC>`:

| Attribute | Meaning |
|-----------|---------|
| `VAL` | Current value |
| `TN` | Time since last update (seconds) |
| `TMAX` | Max expected update interval; alerts if `TN > TMAX` |
| `DMAX` | Time after which metric is deleted; 0 = never |
| `SLOPE` | `zero`, `positive`, `negative`, `both`, `unspecified` — describes expected value change direction |

## Metric Types

| Ganglia type | Description |
|-------------|-------------|
| `string` | Arbitrary text value |
| `int8`, `uint8` | Signed/unsigned 8-bit integer |
| `int16`, `uint16` | Signed/unsigned 16-bit integer |
| `int32`, `uint32` | Signed/unsigned 32-bit integer |
| `float` | 32-bit floating point |
| `double` | 64-bit floating point |

## Data Flow Timing

```
t=0       gmond collects metric (e.g., cpu_user)
t=0       gmond gossips metric to multicast group
t=~15s    gmetad polls gmond XML (configurable: poll_interval in data_source)
t=~15s    gmetad writes RRDtool files
t=~15s    gweb renders updated graph on next page load
```

Metric staleness is `poll_interval + collection_interval`. For real-time dashboards, keep both low (15–30 s is typical).

## Cluster vs. Grid

- **Cluster**: a named set of nodes all running gmond; one gmetad polls them
- **Grid**: a named set of clusters; a grid-level gmetad polls cluster-level gmetad instances

Grid federation enables centralized visibility across many clusters without routing all traffic to a single gmetad.

## Ports and Protocols

| Port | Protocol | Component | Purpose |
|------|----------|-----------|---------|
| 8649 | UDP | gmond | Metric gossip (multicast or unicast) |
| 8649 | TCP | gmond | XML serving to gmetad |
| 8651 | TCP | gmetad | XML serving to gweb and clients |
| 8652 | TCP | gmetad | Interactive XML queries |
