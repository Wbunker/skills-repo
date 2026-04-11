# Deploying Ganglia

From Chapter 2 of *Monitoring with Ganglia* by Bernard Li (O'Reilly).

## Installation

### Package-Based (Recommended)

**RHEL / CentOS / Rocky:**
```bash
# EPEL provides ganglia packages
yum install epel-release
yum install ganglia ganglia-gmond ganglia-gmetad ganglia-web
```

**Debian / Ubuntu:**
```bash
apt-get install ganglia-monitor gmetad ganglia-webfrontend
```

**Ganglia packages:**
| Package | Installs |
|---------|----------|
| `ganglia-gmond` | gmond daemon and built-in modules |
| `ganglia-gmetad` | gmetad daemon |
| `ganglia-web` | gweb PHP frontend |
| `rrdtool` | required by gmetad for storage |

### Build from Source

```bash
# Prerequisites
yum install apr-devel libconfuse-devel pcre-devel expat-devel rrdtool-devel

git clone https://github.com/ganglia/ganglia-monitoring-daemon.git
cd ganglia-monitoring-daemon
./configure --with-gmetad --sysconfdir=/etc/ganglia
make && make install
```

## Configuring gmond

Config file: `/etc/ganglia/gmond.conf`

### Minimal gmond.conf

```
globals {
  daemonize = yes
  setuid = yes
  user = ganglia
  debug_level = 0
  max_udp_msg_len = 1472
  mute = no
  deaf = no
  allow_extra_data = yes
  host_dmax = 86400 /* secs: remove silent host after 1 day */
  cleanup_threshold = 300 /* secs */
  gexec = no
  send_metadata_interval = 60 /* re-send metadata every 60 s */
}

cluster {
  name = "my_cluster"
  owner = "ops-team"
  latlong = "unspecified"
  url = "unspecified"
}

host {
  location = "unspecified"
}

/* Multicast channel — use this for LAN clusters */
udp_send_channel {
  mcast_join = 239.2.11.71
  port = 8649
  ttl = 1
}

udp_recv_channel {
  mcast_join = 239.2.11.71
  port = 8649
  bind = 239.2.11.71
}

/* TCP for gmetad polls */
tcp_accept_channel {
  port = 8649
}
```

### Unicast Mode (for routed networks or cloud)

Replace multicast channels with unicast:

```
udp_send_channel {
  host = ganglia-receiver.internal   /* designated receiver node */
  port = 8649
  ttl = 1
}

udp_recv_channel {
  port = 8649
}
```

Or use a list of peers:

```
udp_send_channel { host = node01; port = 8649 }
udp_send_channel { host = node02; port = 8649 }
```

### Loading Metric Modules

```
/* Python modules directory */
modules {
  module {
    name = "python_module"
    path = "/usr/lib64/ganglia/modpython.so"
    params = "/usr/lib64/ganglia/python_modules"
  }
}

/* Individual built-in modules are auto-loaded from modules dir */
include ("/etc/ganglia/conf.d/*.conf")
```

Default module config snippets live in `/etc/ganglia/conf.d/` — each `.conf` file activates one module (e.g., `cpu.conf`, `mem.conf`, `disk.conf`).

### gmond.conf: Key Parameters

| Section | Parameter | Default | Purpose |
|---------|-----------|---------|---------|
| `globals` | `host_dmax` | 86400 | Seconds before silent host is purged |
| `globals` | `send_metadata_interval` | 0 | 0 = send once at startup; >0 = re-send periodically |
| `globals` | `deaf` | no | If `yes`, gmond won't listen to UDP gossip (send-only) |
| `globals` | `mute` | no | If `yes`, gmond won't send metrics |
| `cluster` | `name` | — | **Must be unique** across all clusters reported to the same gmetad |
| `udp_send_channel` | `ttl` | 1 | Multicast TTL; 1 = same subnet |

## Configuring gmetad

Config file: `/etc/ganglia/gmetad.conf`

### Minimal gmetad.conf

```
# data_source "cluster_name" [polling_interval] host[:port] [host[:port] ...]
data_source "my_cluster" 15 node01:8649 node02:8649 node03:8649

# Where to store RRD files
rrd_rootdir "/var/lib/ganglia/rrds"

# Serve XML on port 8651
xml_port 8651

# Interactive query port
interactive_port 8652

# Aggregation interval
gridname "MyGrid"

# Authority URL shown in XML
authority "http://ganglia.example.com/ganglia/"
```

### data_source Syntax

```
data_source "name" [interval_seconds] host1[:port] [host2[:port]] ...
```

- **name** must match the `cluster { name = "..." }` in gmond.conf exactly
- **interval_seconds** defaults to 15; how often gmetad polls
- List multiple hosts for redundancy — gmetad tries each in order

### RRD Directory Structure

After first data collection:

```
/var/lib/ganglia/rrds/
└── my_cluster/
    ├── __SummaryInfo__/
    │   ├── cpu_user.rrd
    │   └── mem_free.rrd
    ├── node01/
    │   ├── cpu_user.rrd
    │   ├── cpu_system.rrd
    │   └── ...
    └── node02/
        └── ...
```

gmetad creates one RRD per (host, metric) pair plus `__SummaryInfo__` cluster aggregates.

## Starting and Enabling Services

```bash
# systemd
systemctl enable gmond gmetad
systemctl start  gmond gmetad

# Verify gmond is gossiping
telnet localhost 8649   # should return XML

# Verify gmetad is collecting
telnet localhost 8651   # should return full grid XML

# Check cluster state
gstat -a              # lists all hosts gmetad knows about
```

## Firewall Rules

```bash
# gmond UDP gossip (multicast)
firewall-cmd --permanent --add-port=8649/udp

# gmond XML serving to gmetad
firewall-cmd --permanent --add-port=8649/tcp

# gmetad XML serving to gweb
firewall-cmd --permanent --add-port=8651/tcp
firewall-cmd --reload
```

## Common Deployment Patterns

### Single Cluster

```
[node01] gmond ──┐
[node02] gmond ──┼──(multicast 239.2.11.71:8649)──▶ gmond gossip ring
[node03] gmond ──┘
                    gmetad polls node01:8649
                    gweb reads RRDs from gmetad host
```

### Dedicated Aggregation Host

Keep gmetad and gweb on a host that is NOT in the monitored cluster to avoid metric noise from the monitoring system itself.

### High-Availability gmetad

Run two gmetad instances both polling the same cluster. Each writes its own RRD directory. gweb can be pointed at either. (gmetad has no built-in HA — use filesystem replication or DNS failover externally.)
