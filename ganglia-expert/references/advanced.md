# Advanced Topics: Performance, Security, and Troubleshooting

From Chapter 8 of *Monitoring with Ganglia* by Bernard Li (O'Reilly).

## Performance Tuning

### gmond Tuning

**Reduce collection overhead for rarely-changing metrics:**

```
collection_group {
  collect_every = 300     /* collect every 5 minutes */
  time_threshold = 3600   /* force send every hour even if unchanged */

  metric { name = "disk_total" value_threshold = 1.0 }
  metric { name = "cpu_num"    value_threshold = 1.0 }
}
```

**Tune gossip frequency:**

```
globals {
  send_metadata_interval = 300  /* re-announce metric descriptors every 5 min */
  /* default 0 = only on startup; increase if nodes join mid-run */
}
```

**Memory usage per node:**

gmond's in-memory table scales with `(nodes in cluster) × (metrics per node)`. For 1000-node clusters:

```
globals {
  host_dmax = 3600        /* shorter TTL = smaller table */
  cleanup_threshold = 60  /* prune expired entries more aggressively */
}
```

### gmetad Tuning

**Poll fewer nodes for large clusters:**

gmetad doesn't need to poll every node — just one (or a few for redundancy), since all nodes gossip the full cluster picture:

```
# Poll 3 nodes for redundancy; gmetad uses first available
data_source "my_cluster" 15 node01:8649 node02:8649 node03:8649
```

**Separate RRD I/O from XML serving:**

gmetad is I/O-bound when writing many RRD files. Use a fast local disk or tmpfs for RRDs (with periodic rsync to durable storage):

```bash
# Mount tmpfs for RRDs
mount -t tmpfs -o size=2g tmpfs /var/lib/ganglia/rrds

# Cron: sync to durable storage every hour
0 * * * * rsync -a /var/lib/ganglia/rrds/ /mnt/nas/ganglia-rrds/
```

**Reduce RRD file count:**

Only enable modules/metrics you actually use. Each additional metric = one RRD per host. On a 500-node cluster, 100 metrics = 50,000 RRD files.

### RRDtool Tuning

```bash
# Check if RRD writes are causing I/O pressure
iostat -x 1 5

# Use rrdcached to batch RRD writes
rrdcached -d -l /var/run/rrdcached.sock \
          -j /var/lib/rrdcached/journal/ \
          -F -b /var/lib/ganglia/rrds
```

Configure gmetad to use rrdcached:

```
# gmetad.conf
rrdcached_address /var/run/rrdcached.sock
```

## Security

### Network-Level Security

Ganglia has no built-in encryption or authentication for gmond gossip. Mitigations:

**Restrict gmond to a management VLAN:**
```bash
# iptables: only accept gossip from known subnets
iptables -A INPUT -p udp --dport 8649 -s 10.0.0.0/8 -j ACCEPT
iptables -A INPUT -p udp --dport 8649 -j DROP

iptables -A INPUT -p tcp --dport 8649 -s 10.0.0.0/8 -j ACCEPT
iptables -A INPUT -p tcp --dport 8649 -j DROP
```

**Restrict gmetad access:**
```bash
iptables -A INPUT -p tcp --dport 8651 -s 10.0.0.0/8 -j ACCEPT
iptables -A INPUT -p tcp --dport 8651 -j DROP
```

### Trusted Hosts

gmetad can restrict which hosts can inject metrics (anti-spoofing):

```
# gmetad.conf
trusted_hosts 10.0.0.0/8 192.168.0.0/16
```

### gweb Authentication

```apache
# Apache: require authentication for gweb
<Location /ganglia>
    AuthType Basic
    AuthName "Ganglia Monitoring"
    AuthUserFile /etc/ganglia/.htpasswd
    Require valid-user
</Location>

# Or restrict by IP for internal-only access
<Location /ganglia>
    Require ip 10.0.0.0/8
</Location>
```

### Securing gmetad XML with TLS (via stunnel)

```
# /etc/stunnel/stunnel.conf
[gmetad-tls]
accept  = 8661
connect = 8651
cert    = /etc/stunnel/server.pem
key     = /etc/stunnel/server.key
```

Clients connect to port 8661 with TLS; stunnel decrypts and forwards to gmetad's plain 8651.

## Troubleshooting

### Diagnostic Commands

```bash
# Is gmond running and accepting connections?
telnet localhost 8649
# Expected: XML output starting with <GANGLIA_XML ...>

# Is gmetad receiving and storing data?
telnet localhost 8651
# Expected: full grid XML

# Which hosts does gmetad know about?
gstat -a
gstat --all --gmetad-hostname localhost --gmetad-port 8652

# Check gmond log
journalctl -u gmond --since "1 hour ago"

# Check gmetad log
journalctl -u gmetad --since "1 hour ago"

# Are RRD files being updated?
watch -n 5 'ls -lt /var/lib/ganglia/rrds/my_cluster/node01/ | head'
```

### Common Issues and Fixes

| Symptom | Diagnosis | Fix |
|---------|-----------|-----|
| No hosts in gweb | gmetad not polling | Check `data_source` in gmetad.conf; verify node:8649 reachable from gmetad host |
| Host shows all metrics as zero | gmond module not loading | Check `/etc/ganglia/conf.d/` includes; run gmond with `--debug 10` |
| Metric appears but never updates | `deaf = yes` on sending node | Check gmond.conf globals; verify gmond restarts cleanly |
| RRD files exist but graphs are flat | RRD type mismatch (COUNTER vs GAUGE) | Delete RRD and let gmetad recreate it |
| "NaN" values in graphs | Metric not arriving within `tmax` | Lower `tmax` or increase collection frequency |
| gmetad uses 100% CPU | Too many clusters/nodes polled at 15s | Increase poll intervals; reduce number of metrics |
| Custom Python module not loading | Python import error | Run `gmond --debug 10 --no-daemon`; look for Python traceback |
| Multicast not working across subnets | TTL too low or routing blocks multicast | Switch to unicast; increase `ttl` in udp_send_channel |

### Verifying Python Module Loading

```bash
# List loaded modules in running gmond
gmond --check-modules --conf /etc/ganglia/gmond.conf

# Force a module reload (restart gmond)
systemctl restart gmond

# Manually test the Python module
cd /usr/lib64/ganglia/python_modules
python3 -c "
import my_module
descs = my_module.metric_init({'poll_interval': '10'})
print('Registered metrics:')
for d in descs:
    v = d['call_back'](d['name'])
    print(f'  {d[\"name\"]} = {v} {d[\"units\"]}')
"
```

### RRD Troubleshooting

```bash
# Inspect RRD file structure
rrdtool info /var/lib/ganglia/rrds/my_cluster/node01/cpu_user.rrd

# Check last update time
rrdtool last /var/lib/ganglia/rrds/my_cluster/node01/cpu_user.rrd
date -d "@$(rrdtool last ...)"  # convert epoch to human time

# Dump RRD to XML (useful for migration/inspection)
rrdtool dump /var/lib/ganglia/rrds/my_cluster/node01/cpu_user.rrd > cpu_user.xml

# Re-create a corrupted RRD (gmetad will rebuild it)
rm /var/lib/ganglia/rrds/my_cluster/node01/broken_metric.rrd
systemctl restart gmetad
```

### Collecting a Diagnostic Bundle

```bash
#!/bin/bash
# Collect ganglia diagnostics

echo "=== gmond XML ===" > /tmp/ganglia-diag.txt
timeout 5 nc localhost 8649 >> /tmp/ganglia-diag.txt 2>&1

echo "=== gmetad XML (first 200 lines) ===" >> /tmp/ganglia-diag.txt
timeout 5 nc localhost 8651 | head -200 >> /tmp/ganglia-diag.txt 2>&1

echo "=== gstat ===" >> /tmp/ganglia-diag.txt
gstat -a >> /tmp/ganglia-diag.txt 2>&1

echo "=== RRD file ages ===" >> /tmp/ganglia-diag.txt
find /var/lib/ganglia/rrds -name '*.rrd' -printf '%T@ %p\n' | \
  sort -rn | head -20 >> /tmp/ganglia-diag.txt

echo "=== Recent gmond log ===" >> /tmp/ganglia-diag.txt
journalctl -u gmond --since "30 minutes ago" >> /tmp/ganglia-diag.txt 2>&1

echo "=== Recent gmetad log ===" >> /tmp/ganglia-diag.txt
journalctl -u gmetad --since "30 minutes ago" >> /tmp/ganglia-diag.txt 2>&1

cat /tmp/ganglia-diag.txt
```
