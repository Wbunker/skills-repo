# Ganglia Integrations

From Chapter 7 of *Monitoring with Ganglia* by Bernard Li (O'Reilly).

## Nagios Integration

### check_ganglia Plugin

The `check_ganglia` script queries gmetad's interactive port and returns Nagios-compatible exit codes.

**Install:**
```bash
# From nagios-plugins-ganglia or manual install
wget https://raw.githubusercontent.com/ganglia/ganglia-web/master/nagios/check_ganglia.py
cp check_ganglia.py /usr/lib64/nagios/plugins/
chmod +x /usr/lib64/nagios/plugins/check_ganglia.py
```

**Usage:**
```bash
python check_ganglia.py \
  --host gmetad-host \
  --metric cpu_user \
  --cluster my_cluster \
  --node node01 \
  --warning 80 \
  --critical 95
```

Returns:
- `0 OK` — metric within thresholds
- `1 WARNING` — metric > warning threshold
- `2 CRITICAL` — metric > critical threshold
- `3 UNKNOWN` — metric not found or gmetad unreachable

**Nagios command definition:**
```
define command {
    command_name  check_ganglia_metric
    command_line  $USER1$/check_ganglia.py \
                    --host=$HOSTNAME$ \
                    --metric=$ARG1$ \
                    --cluster=$ARG2$ \
                    --warning=$ARG3$ \
                    --critical=$ARG4$
}
```

**Nagios service definition:**
```
define service {
    host_name           node01
    service_description CPU User
    check_command       check_ganglia_metric!cpu_user!my_cluster!80!95
    check_interval      5
    retry_interval      1
}
```

### Passive Nagios Checks via NSCA

Instead of Nagios polling gmetad, push alerts from a Ganglia-watching script:

```bash
#!/bin/bash
# Watch gmetad; send to Nagios passive queue when threshold exceeded
METRIC_VAL=$(python check_ganglia.py --host gmetad-host \
             --metric cpu_user --cluster my_cluster --node "$1" \
             --warning 80 --critical 95 --value-only)

echo "$1;CPU User;$EXIT_CODE;CPU user is $METRIC_VAL%" | \
  send_nsca -H nagios-server -p 5667
```

## Graphite Integration

### Ganglia-to-Graphite Bridge

Forward Ganglia metrics to Graphite's Carbon receiver for longer retention and richer graphing.

**ganglia2graphite.py** pattern:

```python
#!/usr/bin/env python3
"""
Poll gmetad XML and forward metrics to Graphite Carbon.
"""
import socket
import time
import xml.etree.ElementTree as ET

GMETAD_HOST = 'localhost'
GMETAD_PORT = 8651
GRAPHITE_HOST = 'graphite.internal'
GRAPHITE_PORT = 2003
GRAPHITE_PREFIX = 'ganglia'

def fetch_gmetad_xml():
    s = socket.create_connection((GMETAD_HOST, GMETAD_PORT), timeout=10)
    buf = b''
    while True:
        chunk = s.recv(65536)
        if not chunk:
            break
        buf += chunk
    s.close()
    return buf

def xml_to_graphite(xml_data):
    root = ET.fromstring(xml_data)
    now = int(time.time())
    lines = []
    for cluster in root.iter('CLUSTER'):
        cluster_name = cluster.get('NAME', 'unknown').replace(' ', '_')
        for host in cluster.iter('HOST'):
            host_name = host.get('NAME', 'unknown').replace('.', '_').replace('-', '_')
            for metric in host.iter('METRIC'):
                metric_name = metric.get('NAME')
                val = metric.get('VAL')
                try:
                    float(val)  # only numeric metrics
                except (ValueError, TypeError):
                    continue
                path = f"{GRAPHITE_PREFIX}.{cluster_name}.{host_name}.{metric_name}"
                lines.append(f"{path} {val} {now}")
    return '\n'.join(lines)

def send_to_graphite(lines):
    s = socket.create_connection((GRAPHITE_HOST, GRAPHITE_PORT), timeout=10)
    s.sendall((lines + '\n').encode())
    s.close()

if __name__ == '__main__':
    while True:
        try:
            xml_data = fetch_gmetad_xml()
            lines = xml_to_graphite(xml_data)
            if lines:
                send_to_graphite(lines)
        except Exception as e:
            print(f"Error: {e}")
        time.sleep(30)
```

Run as a service:

```ini
# /etc/systemd/system/ganglia2graphite.service
[Unit]
Description=Ganglia to Graphite bridge
After=network.target

[Service]
ExecStart=/usr/local/bin/ganglia2graphite.py
Restart=always
User=ganglia

[Install]
WantedBy=multi-user.target
```

### Graphite Metric Naming Convention

Ganglia → Graphite path convention:
```
ganglia.<cluster_name>.<host_name>.<metric_name>
```

Example:
```
ganglia.my_cluster.node01.cpu_user
ganglia.my_cluster.__SummaryInfo__.cpu_user  # cluster average
```

In Graphite, wildcard queries work across the hierarchy:
```
ganglia.my_cluster.*.cpu_user          # all nodes
ganglia.*.node01.cpu_user              # node01 in any cluster
```

## RRDtool Direct Access

gmetad stores all data as RRD files. Query them directly without gweb:

### Reading an RRD

```bash
# Print last 5 data points for cpu_user on node01
rrdtool fetch /var/lib/ganglia/rrds/my_cluster/node01/cpu_user.rrd AVERAGE \
  --start -1h --end now --resolution 15
```

### Exporting to CSV

```bash
rrdtool xport \
  DEF:cpu=/var/lib/ganglia/rrds/my_cluster/node01/cpu_user.rrd:sum:AVERAGE \
  XPORT:cpu:"CPU User" \
  --start -1d --end now \
  --maxrows 1440 | \
  xmllint --xpath '//row' - | \
  sed 's|<row><t>\([0-9]*\)</t><v>\([^<]*\)</v></row>|\1,\2|g'
```

### Creating Custom Graphs

```bash
rrdtool graph /tmp/cpu_graph.png \
  --start -6h \
  --title "CPU Usage - node01" \
  --vertical-label "%" \
  --width 600 --height 200 \
  DEF:user=/var/lib/ganglia/rrds/my_cluster/node01/cpu_user.rrd:sum:AVERAGE \
  DEF:system=/var/lib/ganglia/rrds/my_cluster/node01/cpu_system.rrd:sum:AVERAGE \
  AREA:user#00FF00:"User" \
  STACK:system#FF0000:"System" \
  COMMENT:"\\n" \
  GPRINT:user:AVERAGE:"Avg User\\: %.1lf%%\\n" \
  GPRINT:system:AVERAGE:"Avg System\\: %.1lf%%\\n"
```

## Integration with Puppet/Chef/Ansible

### Ansible Role for gmond Deployment

```yaml
# tasks/main.yml
- name: Install gmond
  package:
    name: ganglia-gmond
    state: present

- name: Deploy gmond.conf
  template:
    src: gmond.conf.j2
    dest: /etc/ganglia/gmond.conf
  notify: restart gmond

- name: Enable and start gmond
  service:
    name: gmond
    enabled: yes
    state: started
```

```
# templates/gmond.conf.j2
cluster {
  name = "{{ ganglia_cluster_name }}"
}
udp_send_channel {
  {% if ganglia_use_multicast %}
  mcast_join = {{ ganglia_multicast_group }}
  {% else %}
  host = {{ ganglia_receiver_host }}
  {% endif %}
  port = 8649
}
```

## Alerting with Ganglia Events

ganglia-web includes an events API (v3.4+):

```bash
# Post an event (e.g., from a deploy script)
curl -X POST http://ganglia.example.com/ganglia/api/events.php \
  -d "start_time=$(date +%s)" \
  -d "end_time=$(date +%s)" \
  -d "summary=Deploy v1.2.3 to production" \
  -d "host=deploy-server" \
  -d "description=Automated deployment of release 1.2.3"
```

Events appear as vertical marker lines on gweb graphs — useful for correlating metric changes with deployments or configuration changes.
