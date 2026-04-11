# Cluster Federation and Large-Scale Deployments

From Chapters 6–7 of *Monitoring with Ganglia* by Bernard Li (O'Reilly).

## Federation Concepts

Ganglia scales via **hierarchical federation**:

```
Level 0: gmond on each monitored node (gossip within cluster)
Level 1: gmetad per cluster  (polls gmond nodes)
Level 2: gmetad for the grid (polls cluster-level gmetads)
```

A *grid* gmetad instance acts as a single pane of glass across all clusters.

## Multi-Cluster Setup

### Step 1: Each Cluster Has Its Own gmetad

Cluster A gmetad (`/etc/ganglia/gmetad.conf` on host `gmetad-a`):

```
data_source "cluster_a" 15 node-a01:8649 node-a02:8649 node-a03:8649
rrd_rootdir "/var/lib/ganglia/rrds"
gridname "MyGrid"
```

Cluster B gmetad on `gmetad-b`:

```
data_source "cluster_b" 15 node-b01:8649 node-b02:8649
rrd_rootdir "/var/lib/ganglia/rrds"
gridname "MyGrid"
```

### Step 2: Grid-Level gmetad Polls Cluster gmetads

Grid gmetad on `gmetad-grid`:

```
# data_source "name" [interval] host[:port]
# Port 8651 is the default gmetad XML port
data_source "cluster_a" 60 gmetad-a:8651
data_source "cluster_b" 60 gmetad-b:8651

rrd_rootdir "/var/lib/ganglia/rrds"
gridname "MyGrid"
xml_port 8651
```

The grid gmetad receives the full XML tree from each cluster gmetad, builds a combined view, and stores summary RRDs.

### Step 3: gweb Points at Grid gmetad

```php
// conf.php
$conf['rrds'] = "/var/lib/ganglia/rrds";  // grid gmetad's RRD directory
$conf['gmetad_root'] = "gmetad-grid";
$conf['gmetad_port'] = 8652;
```

## Aggregation in Cluster View

gmetad automatically computes cluster-level aggregates stored in `__SummaryInfo__/`:

| Metric | Aggregation |
|--------|-------------|
| `cpu_user` | Average across all nodes |
| `mem_free` | Sum across all nodes |
| `bytes_in` | Sum across all nodes |
| `disk_free` | Sum across all nodes |
| `load_one` | Sum across all nodes (total cluster load) |

Custom metrics use `slope` to determine default aggregation:
- `positive` / `negative` slopes → SUM
- `both` / `zero` slopes → SUM (can override in gmetad.conf)

### Aggregation Function Override

```
# gmetad.conf
aggregation_function "cpu_user" average
aggregation_function "mem_free" sum
aggregation_function "my_custom_metric" max
```

Valid functions: `sum`, `average`, `max`, `min`.

## Reducing gmond Gossip in Large Clusters

With 500+ nodes, multicast gossip can overwhelm the network. Mitigation strategies:

### Deaf/Mute Topology

Designate one or more *receiver* nodes that listen but don't re-broadcast:

On receiver nodes:
```
globals {
  deaf = no    /* still listens */
  mute = no    /* and gossips back — acts as relay */
}
```

On send-only leaf nodes:
```
globals {
  deaf = yes   /* don't store peer metrics — saves memory */
  mute = no    /* still sends own metrics */
}
```

gmetad only needs to poll the receiver nodes (which have the full picture).

### Unicast Aggregation Trees

For clusters spanning multiple subnets:

```
# Spine nodes (aggregators per rack/subnet):
udp_recv_channel { port = 8649 }  /* receive from rack nodes */
udp_send_channel { host = gmetad-host; port = 8649 }  /* forward up */
tcp_accept_channel { port = 8649 }  /* serve to gmetad */

# Leaf nodes (per-server gmond):
udp_send_channel { host = spine-node; port = 8649 }
globals { deaf = yes }  /* don't cache peer data — only forward own */
```

## Handling Node Churn (Cloud / Auto-scaling)

**Problem:** Cloud nodes appear and disappear; gmetad accumulates stale RRDs.

**Solutions:**

1. Set `host_dmax` in gmond.conf to a value appropriate for your node lifetime:
   ```
   globals { host_dmax = 3600 }  /* purge after 1 hour of silence */
   ```

2. Use gmetad's `trusted_hosts` to prevent spoofed metric injection from terminated nodes:
   ```
   trusted_hosts 10.0.0.0/8
   ```

3. Implement an RRD cleanup script to remove old host directories:
   ```bash
   #!/bin/bash
   # Remove host RRD dirs not updated in > 2 hours
   find /var/lib/ganglia/rrds/my_cluster/ -maxdepth 1 -type d \
     -not -name '__SummaryInfo__' \
     -mmin +120 \
     -exec rm -rf {} \;
   ```

## gmetad Scaling

gmetad is single-threaded. With many clusters and high poll frequency it can become a bottleneck.

**Tuning tips:**

```
# gmetad.conf

# Reduce poll frequency for non-critical clusters
data_source "batch_cluster" 60 batch-gmetad:8651  /* 60s instead of 15s */

# Increase gmetad's own max connections
# (compile-time; not runtime-configurable)

# Separate gmetad instances for separate grid segments
# then aggregate with a top-level gmetad
```

## Verifying Federation

```bash
# Check cluster-level gmetad XML
telnet gmetad-a 8651 | xmllint --format - | head -50

# Check grid-level gmetad XML (should include multiple CLUSTER elements)
telnet gmetad-grid 8651 | grep '<CLUSTER'

# Confirm RRD files exist for all clusters
ls /var/lib/ganglia/rrds/

# gstat across all clusters
gstat --all --gmetad-hostname gmetad-grid --gmetad-port 8652
```

## Network Sizing Guidelines

| Cluster size | Recommended topology | gmetad poll interval |
|-------------|---------------------|---------------------|
| < 50 nodes | Single gmetad, multicast | 15 s |
| 50–500 nodes | Single gmetad, multicast or unicast | 15–30 s |
| 500–2000 nodes | Cluster gmetads + grid gmetad; unicast trees | 30–60 s |
| > 2000 nodes | Spine/leaf unicast; multiple grid gmetads | 60 s |
