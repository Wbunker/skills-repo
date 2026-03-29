# Ch 3 — Installation & Configuration

## Table of Contents
- [Prerequisites](#prerequisites)
- [Run Modes](#run-modes)
- [Quick Installation](#quick-installation)
- [Configuration Files](#configuration-files)
- [Key Configuration Properties](#key-configuration-properties)
- [hbase-env.sh (JVM Settings)](#hbase-envsh-jvm-settings)
- [Filesystem Requirements](#filesystem-requirements)
- [Starting and Stopping](#starting-and-stopping)
- [Verifying the Installation](#verifying-the-installation)
- [Common Configuration Mistakes](#common-configuration-mistakes)

---

## Prerequisites

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| Java | Java 8 | Java 11 (HBase 2.x+) |
| Hadoop / HDFS | 2.x | 3.x for HBase 2.x+ |
| ZooKeeper | 3.4.x | 3.5+ |
| OS | Linux | RHEL/CentOS/Ubuntu LTS |
| ulimit (open files) | 10240 | 32768+ |
| ulimit (processes) | 32768 | 32768+ |

**OS requirements:**
```bash
# /etc/security/limits.conf
hbase  soft  nofile  32768
hbase  hard  nofile  32768
hbase  soft  nproc   32768
hbase  hard  nproc   32768

# Disable swap — critical for predictable GC pauses
echo "vm.swappiness=0" >> /etc/sysctl.conf
sysctl -p
```

---

## Run Modes

### Standalone (development only)
- Single JVM, no HDFS (uses local filesystem), built-in ZooKeeper
- No data persistence across restarts unless `hbase.rootdir` points to a permanent path
- Start: `bin/start-hbase.sh`

### Pseudo-Distributed (single machine, separate processes)
- HMaster, RegionServer, ZooKeeper each in separate JVMs
- Uses HDFS on the same machine
- Good for testing multi-process behavior

### Fully Distributed (production)
- HMaster(s), RegionServers, ZooKeeper cluster on separate machines
- HDFS cluster required
- Use `conf/regionservers` file to list RS hostnames

---

## Quick Installation

```bash
# Download and extract
wget https://downloads.apache.org/hbase/stable/hbase-X.Y.Z-bin.tar.gz
tar -xzf hbase-X.Y.Z-bin.tar.gz
export HBASE_HOME=/opt/hbase-X.Y.Z
export PATH=$PATH:$HBASE_HOME/bin

# Standalone test
bin/start-hbase.sh
bin/hbase shell
> status
> exit
bin/stop-hbase.sh
```

---

## Configuration Files

All configuration files live in `$HBASE_HOME/conf/`.

| File | Purpose |
|------|---------|
| `hbase-site.xml` | Primary cluster configuration (overrides hbase-default.xml) |
| `hbase-default.xml` | All defaults — DO NOT edit; reference only |
| `hbase-env.sh` | JVM settings, JAVA_HOME, HBASE_HEAPSIZE |
| `regionservers` | List of RegionServer hostnames (one per line) |
| `backup-masters` | List of backup HMaster hostnames |
| `log4j.properties` | Logging configuration |

---

## Key Configuration Properties

### Core (hbase-site.xml)

```xml
<configuration>
  <!-- Root data directory on HDFS -->
  <property>
    <name>hbase.rootdir</name>
    <value>hdfs://namenode:8020/hbase</value>
  </property>

  <!-- ZooKeeper quorum hosts (comma-separated) -->
  <property>
    <name>hbase.zookeeper.quorum</name>
    <value>zk1,zk2,zk3</value>
  </property>

  <!-- ZooKeeper client port -->
  <property>
    <name>hbase.zookeeper.property.clientPort</name>
    <value>2181</value>
  </property>

  <!-- ZooKeeper data directory (when HBase manages ZK) -->
  <property>
    <name>hbase.zookeeper.property.dataDir</name>
    <value>/var/lib/zookeeper</value>
  </property>

  <!-- Distributed mode flag -->
  <property>
    <name>hbase.cluster.distributed</name>
    <value>true</value>
  </property>
</configuration>
```

### Region & MemStore Sizing

```xml
<!-- Max region size before auto-split (default 10GB, reduce for faster splits) -->
<property>
  <name>hbase.hregion.max.filesize</name>
  <value>10737418240</value>  <!-- 10 GB -->
</property>

<!-- MemStore flush threshold per region (default 128MB) -->
<property>
  <name>hbase.hregion.memstore.flush.size</name>
  <value>134217728</value>
</property>

<!-- Fraction of heap for all MemStores combined (default 0.4 = 40%) -->
<property>
  <name>hbase.regionserver.global.memstore.size</name>
  <value>0.4</value>
</property>

<!-- When total MemStore usage exceeds this fraction, block writes (default 0.95) -->
<property>
  <name>hbase.regionserver.global.memstore.size.lower.limit</name>
  <value>0.95</value>
</property>
```

### BlockCache

```xml
<!-- Fraction of heap for BlockCache (default 0.4 = 40%) -->
<property>
  <name>hfile.block.cache.size</name>
  <value>0.4</value>
</property>

<!-- Use BucketCache (off-heap) for L2 cache — avoids GC pressure -->
<property>
  <name>hbase.bucketcache.ioengine</name>
  <value>offheap</value>
</property>
<property>
  <name>hbase.bucketcache.size</name>
  <value>8192</value>  <!-- MB -->
</property>
```

### RPC & Handlers

```xml
<!-- Number of RPC handler threads per RegionServer (default 30, use CPU count * 5) -->
<property>
  <name>hbase.regionserver.handler.count</name>
  <value>30</value>
</property>

<!-- RPC timeout (ms) -->
<property>
  <name>hbase.rpc.timeout</name>
  <value>60000</value>
</property>

<!-- Client-side operation timeout (ms, across retries) -->
<property>
  <name>hbase.client.operation.timeout</name>
  <value>1200000</value>
</property>
```

### Compaction

```xml
<!-- Min number of StoreFiles before minor compaction triggers -->
<property>
  <name>hbase.hstore.compactionThreshold</name>
  <value>3</value>
</property>

<!-- Max StoreFiles per Store before writes are throttled (default 7) -->
<property>
  <name>hbase.hstore.blockingStoreFiles</name>
  <value>7</value>
</property>
```

### Replication Factor (HDFS)

HBase uses HDFS replication. The HDFS default is 3 replicas. Set in `hdfs-site.xml`:
```xml
<property>
  <name>dfs.replication</name>
  <value>3</value>
</property>
```

---

## hbase-env.sh (JVM Settings)

```bash
# Java home
export JAVA_HOME=/usr/java/jdk11

# Heap size (same value for min and max to avoid resizing pauses)
export HBASE_HEAPSIZE=8g          # Applies to HMaster and RegionServer

# RegionServer-specific (overrides HBASE_HEAPSIZE for RS)
export HBASE_REGIONSERVER_OPTS="-Xms16g -Xmx16g \
  -XX:+UseG1GC \
  -XX:MaxGCPauseMillis=100 \
  -XX:+ParallelRefProcEnabled \
  -XX:+PerfDisableSharedMem \
  -XX:+AlwaysPreTouch \
  -XX:G1HeapRegionSize=32m \
  -XX:InitiatingHeapOccupancyPercent=35 \
  -verbose:gc -XX:+PrintGCDetails -XX:+PrintGCDateStamps \
  -Xloggc:${HBASE_LOG_DIR}/gc-rs.log"

# HMaster JVM opts
export HBASE_MASTER_OPTS="-Xms4g -Xmx4g -XX:+UseG1GC"

# PID files and log directories
export HBASE_PID_DIR=/var/run/hbase
export HBASE_LOG_DIR=/var/log/hbase
```

> **Rule of thumb:** Leave 2–4 GB for OS. RegionServer heap: 12–32 GB.
> Above 32 GB heap, G1GC becomes expensive — prefer BucketCache (off-heap) instead.

---

## Filesystem Requirements

### HDFS Short-Circuit Reads

Allows RegionServer to read HFiles directly from local disk (bypassing DataNode RPC):
```xml
<!-- In hdfs-site.xml -->
<property>
  <name>dfs.client.read.shortcircuit</name>
  <value>true</value>
</property>
<property>
  <name>dfs.domain.socket.path</name>
  <value>/var/lib/hadoop-hdfs/dn_socket</value>
</property>
```

### Sync to HDFS

HBase WAL durability requires HDFS sync support. Verify:
```bash
bin/hbase org.apache.hadoop.hbase.util.FSUtils
```

---

## Starting and Stopping

```bash
# Start all (HMaster + RegionServers + built-in ZK)
bin/start-hbase.sh

# Start individual components
bin/hbase master start        # foreground
bin/hbase-daemon.sh start master
bin/hbase-daemon.sh start regionserver

# Rolling restart of RegionServers (graceful, for upgrades)
bin/rolling-restart.sh

# Stop all
bin/stop-hbase.sh

# Stop individual
bin/hbase-daemon.sh stop master
bin/hbase-daemon.sh stop regionserver
```

---

## Verifying the Installation

```bash
# Shell status
hbase shell
> status
> status 'detailed'
> version
> whoami

# Web UIs (default ports)
# HMaster:       http://master:16010
# RegionServer:  http://rs:16030

# Run built-in performance test
bin/hbase org.apache.hadoop.hbase.PerformanceEvaluation --rows=100000 sequentialWrite 4
bin/hbase org.apache.hadoop.hbase.PerformanceEvaluation --rows=100000 randomRead 4
```

---

## Common Configuration Mistakes

| Mistake | Symptom | Fix |
|---------|---------|-----|
| `hbase.rootdir` not set | Uses local /tmp (lost on restart) | Set to `hdfs://...` path |
| ZK quorum wrong/unreachable | `MasterNotRunningException` on connect | Verify `hbase.zookeeper.quorum` hosts |
| Heap too large (>32GB) | Long GC pauses, timeouts | Use BucketCache off-heap; keep heap ≤20GB |
| Swap enabled | Random long pauses | `vm.swappiness=0` in sysctl.conf |
| `nofile` ulimit too low | "Too many open files" errors | Set to 32768+ in limits.conf |
| Not syncing NTP | Clock skew errors, ZK disconnects | Ensure NTP running on all nodes |
| Single ZK node | ZK failure = cluster down | Use 3 or 5 ZK nodes |
