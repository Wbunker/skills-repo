# Ch 11 — Cluster Operations, Replication, Backup & Monitoring

## Table of Contents
- [Cluster Administration](#cluster-administration)
- [Region Management Operations](#region-management-operations)
- [Replication](#replication)
- [Snapshots](#snapshots)
- [Backup and Restore](#backup-and-restore)
- [Monitoring and Metrics](#monitoring-and-metrics)
- [Troubleshooting Guide](#troubleshooting-guide)
- [Upgrade Procedures](#upgrade-procedures)
- [HBCK — HBase Consistency Checker](#hbck--hbase-consistency-checker)

---

## Cluster Administration

### Managing RegionServers

```bash
# Graceful decommission (drains regions before stopping)
bin/graceful_stop.sh rs1.example.com

# Graceful rolling restart (for config changes)
bin/rolling-restart.sh

# Add a new RegionServer (just start it — HMaster will assign regions)
bin/hbase-daemon.sh start regionserver   # on the new node

# Remove a RegionServer from the cluster
# 1. Drain regions:
hbase shell
> unassign 'all regions on rs1'  # or use graceful_stop.sh
# 2. Stop:
bin/hbase-daemon.sh stop regionserver   # on the node to remove
```

### Master HA (High Availability)

```bash
# Active + backup master setup in conf/backup-masters
echo "master2.example.com" >> conf/backup-masters

# Start backup master manually
bin/hbase-daemon.sh start master --backup

# Check master status
hbase shell
> status 'simple'  # shows active master and backup
```

### ZooKeeper Management

```bash
# Check ZK status
echo stat | nc zk1 2181
echo mntr | nc zk1 2181  # detailed metrics
echo ruok | nc zk1 2181  # should return "imok"

# ZK CLI (for debugging)
bin/hbase zkcli
ls /hbase
ls /hbase/master
ls /hbase/rs
get /hbase/master  # shows active master
```

### Configuration Reload (without restart)

Some hbase-site.xml properties can be reloaded via shell:

```ruby
# Reload certain configs online (HBase 2.x)
# Note: not all properties support hot reload
update_config 'rs1.example.com,16020,1234567890'
update_all_config
```

---

## Region Management Operations

### Monitoring Region Distribution

```ruby
# Check number of regions per RegionServer
status 'detailed'

# List regions for a table
list_regions 'orders'

# Check region server assignment
hbase hbck -details 2>/dev/null | grep "Region in META"
```

### Manual Region Operations

```ruby
# Flush a table's MemStores to disk
flush 'orders'

# Force minor compaction
compact 'orders'

# Force major compaction (rewrites all HFiles, expensive)
major_compact 'orders'

# Compact a specific region
compact 'regionEncodedName'

# Split a region at its midpoint
split 'orders'

# Split at a specific row key
split 'orders', 'order-500'

# Merge adjacent regions (HBase 2.x)
merge_region 'encodedRegion1', 'encodedRegion2'
merge_region 'encodedRegion1', 'encodedRegion2', true  # forcible

# Move region to specific RS
move 'encodedRegionName', 'rs2.example.com,16020,1234567890'

# Balance load across RegionServers
balancer

# Enable/disable balancer
balance_switch true
balance_switch false
is_in_maintenance_mode
```

### Region Splitting Best Practices

```
Strategy 1: Pre-split at table creation (recommended)
  → Prevents initial hotspot during data load
  → Use knowledge of key distribution

Strategy 2: Controlled auto-split
  → Set hbase.hregion.max.filesize appropriately (e.g., 5–10 GB)
  → Monitor region count per RS

Strategy 3: Disable auto-split, split manually
  → For tables with predictable growth
  → Avoids compaction spikes from unexpected splits

alter 'orders', SPLIT_POLICY => 'org.apache.hadoop.hbase.regionserver.DisabledRegionSplitPolicy'
```

---

## Replication

HBase replication copies mutations from a source cluster to one or more peer clusters at the **column-family level**.

### Architecture

```
Source Cluster                      Sink Cluster
─────────────────────────────────────────────────────
RegionServer 1                      RegionServer A
  WAL → Replication Source ────────→ ReplicationSink
RegionServer 2                      RegionServer B
  WAL → Replication Source ────────→ ReplicationSink

• Each RS reads its own WAL and ships entries to peers
• ZooKeeper tracks replication progress (WAL offsets)
• Replication lag is typically seconds to minutes
```

### Replication Modes

| Mode | Description | Use Case |
|------|-------------|----------|
| Master-Slave | A → B (one way) | DR, reporting cluster |
| Master-Master | A ↔ B (bidirectional) | Multi-region active-active |
| Cyclic | A → B → C → A | Multi-region ring topology |

### Setup Replication

**Step 1: Enable replication on column families**

```ruby
# On source cluster: enable replication scope
alter 'orders', {NAME => 'cf', REPLICATION_SCOPE => '1'}
# REPLICATION_SCOPE => 0 = local only (default)
# REPLICATION_SCOPE => 1 = global (replicate this CF)
```

**Step 2: Add peer cluster**

```ruby
# On source cluster: add peer (sink cluster ZooKeeper)
add_peer '1', CLUSTER_KEY => 'zk-sink1,zk-sink2,zk-sink3:2181:/hbase'

# Add peer with specific tables/CFs
add_peer '1',
  CLUSTER_KEY => 'zk-sink1,zk-sink2:2181:/hbase',
  TABLE_CFS => {'orders' => ['cf'], 'users' => []}

# Verify peer status
list_peers
get_peer_config '1'

# Enable/disable a peer
enable_peer '1'
disable_peer '1'

# Remove a peer
remove_peer '1'
```

**Step 3: Verify replication is running**

```ruby
# Check replication status
status 'replication'
status 'replication', 'source'
status 'replication', 'sink'
```

### Replication Monitoring

```bash
# Check replication lag via JMX/Metrics
# Key metric: hbase.regionserver.sink.ageOfLastAppliedOp (should be < 60s)

# ReplicationSource metrics (per peer):
# hbase.regionserver.source.sizeOfLogQueue  → WAL backlog
# hbase.regionserver.source.ageOfLastShippedOp → lag in ms
# hbase.regionserver.source.shippedBytes    → throughput
```

### Replication Troubleshooting

```
Replication lag increasing:
1. Check source RS: is WAL shipping queue backing up?
2. Check network bandwidth between clusters
3. Check sink RS: is it applying mutations fast enough?
4. Check if a RegionServer died (reassignment may pause replication)

Replication stopped:
1. Check ZK: /hbase-replication path for peer status
2. Check RS logs for replication errors
3. Use: hbase org.apache.hadoop.hbase.replication.ReplicationPeerStatus
```

---

## Snapshots

Snapshots provide point-in-time, zero-copy backups of tables.

### How Snapshots Work

- A snapshot records which HFiles belong to the table at that moment
- No data is copied — just references
- HFiles referenced by a snapshot are not deleted by compaction until snapshot is deleted
- Snapshots can be exported to another cluster

### Snapshot Operations

```ruby
# Create a snapshot
snapshot 'orders', 'orders_snap_20250101_0000'

# List snapshots
list_snapshots
list_snapshots 'orders.*'

# Describe a snapshot
describe_namespace 'orders_snap_20250101_0000'  # not a standard command
# Use: list_snapshots with table filter

# Restore from snapshot (table must be disabled)
disable 'orders'
restore_snapshot 'orders_snap_20250101_0000'
enable 'orders'

# Clone (create new table from snapshot — does not disable original)
clone_snapshot 'orders_snap_20250101_0000', 'orders_restored'

# Delete snapshot
delete_snapshot 'orders_snap_20250101_0000'

# Delete all snapshots matching pattern
delete_all_snapshot 'orders_snap_.*'
```

### Export Snapshot to Another Cluster

```bash
# Export snapshot to HDFS (same cluster, different path)
bin/hbase snapshot export \
  --snapshot orders_snap_20250101 \
  --copy-to hdfs://backup-cluster/hbase

# Export to different cluster
bin/hbase snapshot export \
  --snapshot orders_snap_20250101 \
  --copy-to hdfs://backup-namenode:8020/hbase \
  --mappers 4

# Import on destination cluster
bin/hbase snapshot restore \
  --snapshot orders_snap_20250101
# Then: clone_snapshot or restore_snapshot in shell
```

---

## Backup and Restore

HBase 1.2+ provides native incremental backup (ExportSnapshot + WAL-based incremental).

### Full Backup

```bash
# Full backup of a table to HDFS
bin/hbase backup create full hdfs://backup/hbase-backups \
  -t orders,users \
  -w 3  # 3 worker threads

# Full backup of all tables
bin/hbase backup create full hdfs://backup/hbase-backups
```

### Incremental Backup

```bash
# Incremental backup (captures changes since last backup)
bin/hbase backup create incremental hdfs://backup/hbase-backups \
  -t orders,users

# List backups
bin/hbase backup list

# Describe backup
bin/hbase backup describe BACKUP_ID
```

### Restore

```bash
# Restore from backup
bin/hbase restore hdfs://backup/hbase-backups BACKUP_ID \
  -t orders \
  -m orders_restored  # optional: restore to different table name

# Restore to original table names
bin/hbase restore hdfs://backup/hbase-backups BACKUP_ID
```

### Export/Import (older method)

```bash
# Export (creates SequenceFiles on HDFS)
bin/hbase org.apache.hadoop.hbase.mapreduce.Export orders /backup/orders

# Import
bin/hbase org.apache.hadoop.hbase.mapreduce.Import orders /backup/orders
```

---

## Monitoring and Metrics

### Web UIs

| Component | Default URL | Key Info |
|-----------|-------------|----------|
| HMaster | http://master:16010 | Table list, RegionServer list, region balance |
| RegionServer | http://rs:16030 | Regions served, request rates, memory usage |
| HMaster (old) | http://master:60010 | Pre-2.x |
| RegionServer (old) | http://rs:60030 | Pre-2.x |

### Key Metrics (JMX / Prometheus)

**RegionServer — Requests:**
```
hbase.regionserver.readRequestCount          # reads/second
hbase.regionserver.writeRequestCount         # writes/second
hbase.regionserver.rpcQueueLength            # RPC queue depth (alarm if > 0 consistently)
hbase.regionserver.rpcProcessingTime_num_ops # RPC processing time
```

**RegionServer — Memory:**
```
hbase.regionserver.memstoreSize              # total MemStore bytes
hbase.regionserver.blockCacheCount          # blocks in BlockCache
hbase.regionserver.blockCacheHitPercent     # cache hit rate (alarm if < 90%)
hbase.regionserver.blockCacheFreeSize       # available BlockCache bytes
```

**RegionServer — Compaction:**
```
hbase.regionserver.compactionQueueLength    # compaction queue depth
hbase.regionserver.flushQueueLength         # flush queue depth
hbase.regionserver.storeFileCount           # total HFiles (alarm if high)
```

**JVM:**
```
jvm.metrics.gcTimeMillis                    # GC pause time
jvm.metrics.memHeapUsedM                    # heap usage MB
jvm.metrics.memNonHeapUsedM                 # off-heap usage
```

### Prometheus + Grafana Integration

```xml
<!-- hbase-site.xml: enable metrics sink -->
<property>
  <name>hbase.metrics.exposeOperationTimes</name>
  <value>true</value>
</property>
```

Add to `hadoop-metrics2-hbase.properties`:
```properties
# Export metrics via Prometheus HTTP endpoint
hbase.sink.prometheus.class=org.apache.hadoop.metrics2.sink.PrometheusMetricsSink
hbase.sink.prometheus.port=9100
```

Then scrape `http://regionserver:9100/metrics` from Prometheus.

### Important Alerts to Configure

| Alert | Threshold | Severity |
|-------|-----------|----------|
| BlockCache hit rate | < 90% | Warning |
| MemStore size | > 80% of configured limit | Warning |
| RPC queue length | > 10 consistently | Warning |
| GC pause time | > 500ms | Critical |
| Compaction queue | > 20 | Warning |
| Dead RegionServers | > 0 | Critical |
| Replication lag | > 60 seconds | Warning |
| Disk usage | > 80% | Warning |

---

## Troubleshooting Guide

### RegionServer Won't Start

```bash
# Check logs: $HBASE_LOG_DIR/hbase-hbase-regionserver-<hostname>.log
grep -i "error\|exception\|fatal" $HBASE_LOG_DIR/hbase-*.log | tail -100

# Common causes:
# 1. Port already in use: check hbase.regionserver.port (16020)
# 2. ZK connection refused: verify hbase.zookeeper.quorum
# 3. HDFS not accessible: verify hbase.rootdir
# 4. Java version mismatch: check JAVA_HOME
```

### RegionServer Crashes (OOM)

```bash
# Enable heap dump on OOM in hbase-env.sh:
export HBASE_REGIONSERVER_OPTS="$HBASE_REGIONSERVER_OPTS \
  -XX:+HeapDumpOnOutOfMemoryError \
  -XX:HeapDumpPath=/var/log/hbase/heapdump.hprof"

# Analyze with:
jmap -heap <pid>
# Or: jvisualvm, Eclipse MAT
```

### Region Not Assigned

```ruby
# Check unassigned regions
hbase hbck

# Force assign
hbase shell
> assign 'encodedRegionName'

# For stuck regions in OPENING/CLOSING state (HBase 2.x):
bin/hbase hbck2 assigns encodedRegionName
bin/hbase hbck2 unassigns encodedRegionName
```

### Data Consistency Issues

```bash
# Run HBase consistency check
bin/hbase hbck

# Fix inconsistencies (HBase 2.x: use HBCK2)
bin/hbase hbck2 fixMeta
bin/hbase hbck2 assigns -skip encodedRegionName1 encodedRegionName2

# Check for holes/overlaps in region key space
bin/hbase hbck -details 2>&1 | grep -E "ERROR|WARNING"
```

---

## Upgrade Procedures

### Rolling Upgrade (minor versions)

```
1. Update HBase binaries on each node (keep old version as backup)
2. Update HMaster (active) → backup HMaster starts serving
3. Active HMaster comes back up on new version
4. Rolling restart of RegionServers: bin/rolling-restart.sh
5. Verify: hbase shell > version; status 'detailed'
```

### Major Version Upgrade

```
1. Review upgrade guide: https://hbase.apache.org/book.html#upgrading
2. Take snapshots of all critical tables
3. Check compatibility matrix (HDFS, ZooKeeper, Java versions)
4. For 0.x → 1.x: API compatibility shim is available
5. For 1.x → 2.x:
   - Remove deprecated HTable usage (use Connection API)
   - HBCK has changed (HBCK2 for 2.x)
   - Procedure v2 changes master internal state
```

---

## HBCK — HBase Consistency Checker

### HBase 1.x (hbck)

```bash
# Read-only check
bin/hbase hbck

# Check with details
bin/hbase hbck -details

# Fix common issues
bin/hbase hbck -fixAssignments     # fix mis-assigned regions
bin/hbase hbck -fixMeta            # fix hbase:meta inconsistencies
bin/hbase hbck -repair             # fix all repairable issues (use carefully)

# Fix a specific table
bin/hbase hbck -fixAssignments orders
```

### HBase 2.x (HBCK2 — preferred)

```bash
# Download hbase-hbck2 tool separately or use bundled version

# Report issues
bin/hbase hbck2 -j /path/to/hbck2.jar reportMissingRegionsInMeta

# Fix meta table
bin/hbase hbck2 fixMeta

# Re-assign stuck regions
bin/hbase hbck2 assigns encodedRegion1 encodedRegion2

# Force set region state in meta
bin/hbase hbck2 setRegionState encodedRegion CLOSED

# Recover unknown servers
bin/hbase hbck2 scheduleRecoveries serverName1 serverName2
```

> **Warning:** Never run hbck with fix flags while the cluster is under heavy load.
> Always take snapshots before running hbck repairs.
> HBCK1 (hbase hbck) on HBase 2.x can make things worse — use HBCK2 instead.
