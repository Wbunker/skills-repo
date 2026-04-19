# Node Exporter

## Overview

Node Exporter exposes hardware and OS-level metrics from Linux/Unix systems. It is the standard way to monitor physical and virtual hosts with Prometheus.

Port: **9100** | Metrics path: `/metrics`

## Installation

```bash
# Binary
wget https://github.com/prometheus/node_exporter/releases/latest/download/node_exporter-*linux-amd64.tar.gz
tar xvfz node_exporter-*.tar.gz
./node_exporter

# Systemd unit
cat > /etc/systemd/system/node_exporter.service << 'EOF'
[Unit]
Description=Node Exporter
After=network.target

[Service]
User=node_exporter
ExecStart=/usr/local/bin/node_exporter

[Install]
WantedBy=multi-user.target
EOF
systemctl enable --now node_exporter

# Docker
docker run -d \
  --net="host" \
  --pid="host" \
  -v "/:/host:ro,rslave" \
  prom/node-exporter \
  --path.rootfs=/host
```

## Key Collectors and Metrics

### CPU
```promql
# CPU utilization per mode
rate(node_cpu_seconds_total[5m])

# Total CPU usage %
100 - avg by (instance) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100
```

Modes: `idle`, `user`, `system`, `iowait`, `irq`, `softirq`, `steal`, `nice`

### Memory
```promql
node_memory_MemTotal_bytes
node_memory_MemAvailable_bytes
node_memory_MemFree_bytes
node_memory_Cached_bytes
node_memory_Buffers_bytes
node_memory_SwapTotal_bytes
node_memory_SwapFree_bytes

# Used memory
node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes
```

### Disk I/O
```promql
# Read/write bytes per second
rate(node_disk_read_bytes_total[5m])
rate(node_disk_written_bytes_total[5m])

# IOPS
rate(node_disk_reads_completed_total[5m])
rate(node_disk_writes_completed_total[5m])

# I/O wait time
rate(node_disk_io_time_seconds_total[5m])
```

### Filesystem
```promql
node_filesystem_size_bytes{fstype!~"tmpfs|fuse.lxcfs|squashfs"}
node_filesystem_avail_bytes{fstype!~"tmpfs|fuse.lxcfs|squashfs"}

# Used %
(node_filesystem_size_bytes - node_filesystem_avail_bytes)
  / node_filesystem_size_bytes * 100

# Disk fill prediction (4 hour horizon)
predict_linear(node_filesystem_avail_bytes[6h], 4 * 3600)
```

### Network
```promql
rate(node_network_receive_bytes_total[5m])
rate(node_network_transmit_bytes_total[5m])
rate(node_network_receive_errs_total[5m])
rate(node_network_transmit_errs_total[5m])
rate(node_network_receive_drop_total[5m])
```

### System Load
```promql
node_load1    # 1-minute load average
node_load5    # 5-minute load average
node_load15   # 15-minute load average
node_cpu_count  # number of CPUs

# Normalize: load per CPU
node_load1 / count without (cpu, mode) (node_cpu_seconds_total{mode="idle"})
```

### Process / File Descriptors
```promql
node_filefd_allocated
node_filefd_maximum
process_open_fds        # (from instrumented app)
process_max_fds
```

### Boot / Uptime
```promql
node_boot_time_seconds
time() - node_boot_time_seconds   # uptime in seconds
```

## Enabling / Disabling Collectors

```bash
# Disable a collector
node_exporter --no-collector.wifi

# Enable an optional collector
node_exporter --collector.systemd
node_exporter --collector.processes
node_exporter --collector.ethtool
node_exporter --collector.perf
```

Default collectors: cpu, diskstats, filesystem, loadavg, meminfo, netdev, netstat, stat, time, uname, vmstat, ...

Optional (disabled by default): systemd, processes, perf, ethtool, wifi, ntp

## Textfile Collector

Allows external programs to expose custom metrics by writing `.prom` files to a directory.

```bash
# Start node_exporter with textfile directory
node_exporter --collector.textfile.directory=/var/lib/node_exporter/textfile_collector

# Write a metric from a cron job
cat > /var/lib/node_exporter/textfile_collector/backup.prom << 'EOF'
# HELP backup_last_success_timestamp_seconds Unix timestamp of last successful backup.
# TYPE backup_last_success_timestamp_seconds gauge
backup_last_success_timestamp_seconds $(date +%s)
EOF
```

Rules for textfile metrics:
- Files must end in `.prom`
- Must be valid Prometheus text format
- Files are read on each scrape
- Stale files are NOT automatically removed — you must clean them up
- Use atomic writes (write to `.prom.tmp`, then `mv`) to avoid partial reads

## Prometheus Scrape Config

```yaml
scrape_configs:
  - job_name: "node"
    static_configs:
      - targets:
          - "node1:9100"
          - "node2:9100"
    relabel_configs:
      - source_labels: [__address__]
        regex: "([^:]+):.*"
        target_label: instance
        replacement: "$1"
```

## Windows Equivalent

**windows_exporter** (formerly wmi_exporter) provides equivalent metrics for Windows hosts. Port 9182.

```powershell
# Install
.\windows_exporter-*.exe --collectors.enabled "cpu,cs,logical_disk,net,os,system,memory"
```
