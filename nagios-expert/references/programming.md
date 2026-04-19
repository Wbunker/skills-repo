# Programming Nagios
## Chapter 11: Custom Plugins, C/libnagios, Scripting, Cloud/VMware Monitoring

---

## The Plugin API Contract

Every Nagios plugin must follow this contract regardless of language:

### Exit Codes

| Code | State | Meaning |
|------|-------|---------|
| 0 | OK | Check passed; everything normal |
| 1 | WARNING | Check passed but approaching threshold or minor issue |
| 2 | CRITICAL | Check failed or threshold exceeded |
| 3 | UNKNOWN | Plugin could not execute the check (missing args, connection error) |

### Output Format

```
STATUS MESSAGE - details|perfdata_label=value[UOM];[warn];[crit];[min];[max]
```

**First line** is the status message shown in the web interface.
**After `|`** is performance data (optional).
**Lines 2+** are long output (shown in extended info, not one-liners).

```
DISK OK - free space: / 18295 MB (73% inode=99%);|/=6734MB;20000;23000;0;25045 /tmp=1234MB;4000;4500;0;5000
```

Performance data units (UOM):
- `s` = seconds, `ms` = milliseconds, `us` = microseconds
- `%` = percentage
- `B`, `KB`, `MB`, `GB`, `TB` = bytes
- `c` = continuous counter (e.g., network octets)
- (none) = dimensionless number

---

## Writing Shell Script Plugins

```bash
#!/bin/bash
# check_process_count.sh — alert if process count outside range
PROCESS=$1
WARN=$2
CRIT=$3

if [ -z "$PROCESS" ] || [ -z "$WARN" ] || [ -z "$CRIT" ]; then
    echo "UNKNOWN - Usage: $0 <process_name> <warn_count> <crit_count>"
    exit 3
fi

COUNT=$(pgrep -c "$PROCESS" 2>/dev/null || echo 0)

if [ "$COUNT" -ge "$CRIT" ]; then
    echo "CRITICAL - $COUNT instances of $PROCESS running (threshold: $CRIT)|count=$COUNT;$WARN;$CRIT;0"
    exit 2
elif [ "$COUNT" -ge "$WARN" ]; then
    echo "WARNING - $COUNT instances of $PROCESS running (threshold: $WARN)|count=$COUNT;$WARN;$CRIT;0"
    exit 1
elif [ "$COUNT" -eq 0 ]; then
    echo "CRITICAL - $PROCESS not running|count=0;$WARN;$CRIT;0"
    exit 2
else
    echo "OK - $COUNT instances of $PROCESS running|count=$COUNT;$WARN;$CRIT;0"
    exit 0
fi
```

Deploy and test:

```bash
chmod +x /usr/local/nagios/libexec/check_process_count.sh
sudo -u nagios /usr/local/nagios/libexec/check_process_count.sh httpd 5 20
```

---

## Writing Python Plugins

```python
#!/usr/bin/env python3
"""check_queue_depth.py — check message queue depth via Redis"""
import sys
import redis
import argparse

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-H', '--host', default='localhost')
    parser.add_argument('-p', '--port', type=int, default=6379)
    parser.add_argument('-q', '--queue', required=True)
    parser.add_argument('-w', '--warn', type=int, required=True)
    parser.add_argument('-c', '--crit', type=int, required=True)
    args = parser.parse_args()

    try:
        r = redis.Redis(host=args.host, port=args.port, socket_timeout=5)
        depth = r.llen(args.queue)
    except Exception as e:
        print(f"UNKNOWN - Cannot connect to Redis: {e}")
        sys.exit(3)

    perfdata = f"depth={depth};{args.warn};{args.crit};0"

    if depth >= args.crit:
        print(f"CRITICAL - Queue {args.queue} depth {depth} >= {args.crit}|{perfdata}")
        sys.exit(2)
    elif depth >= args.warn:
        print(f"WARNING - Queue {args.queue} depth {depth} >= {args.warn}|{perfdata}")
        sys.exit(1)
    else:
        print(f"OK - Queue {args.queue} depth {depth}|{perfdata}")
        sys.exit(0)

if __name__ == '__main__':
    main()
```

---

## Writing C Plugins with libnagios

libnagios provides helper functions for threshold parsing, performance data formatting, and network checks. Available in Nagios 4 source.

```c
#include "common.h"
#include "utils.h"
#include "utils_base.h"

int main(int argc, char **argv) {
    int result;
    double value;
    thresholds *thresh;
    
    /* parse thresholds using libnagios helper */
    set_thresholds(&thresh, "80", "95");
    
    /* your check logic */
    value = get_cpu_usage();
    
    /* evaluate against thresholds */
    result = get_status(value, thresh);
    
    /* output with performance data */
    printf("%s - CPU usage %.1f%%|cpu=%.1f%%;80;95;0;100\n",
           state_text(result), value, value);
    
    return result;  /* exit code = state */
}
```

Compile against libnagios:

```bash
gcc -o check_mycpu check_mycpu.c -lnagios -lm
```

---

## Testing Database Correctness

Custom plugin that validates query results:

```python
#!/usr/bin/env python3
"""check_db_row_count.py — verify a table has expected row count"""
import sys
import psycopg2

def check(host, dbname, user, password, table, min_rows, max_rows):
    try:
        conn = psycopg2.connect(host=host, dbname=dbname, user=user, password=password, connect_timeout=5)
        cur = conn.cursor()
        cur.execute(f"SELECT COUNT(*) FROM {table}")
        count = cur.fetchone()[0]
        conn.close()
    except Exception as e:
        print(f"UNKNOWN - DB error: {e}")
        sys.exit(3)

    perfdata = f"rows={count};{min_rows};{max_rows}"
    if count < min_rows or count > max_rows:
        print(f"CRITICAL - {table} has {count} rows (expected {min_rows}-{max_rows})|{perfdata}")
        sys.exit(2)
    print(f"OK - {table} has {count} rows|{perfdata}")
    sys.exit(0)
```

---

## Monitoring Time Servers (NTP)

```bash
# check_ntp_time from nagios-plugins
check_ntp_time -H ntp.example.com -w 0.5 -c 1.0
# -w warn offset (seconds)  -c crit offset

check_ntp_peer -H ntp.example.com -w 0.5 -c 1.0
# Also checks stratum and jitter
```

---

## Monitoring Websites (HTTP Application Checks)

Beyond simple check_http, check for application-level correctness:

```python
#!/usr/bin/env python3
"""check_webapp_health.py — check JSON health endpoint"""
import sys
import urllib.request
import json

url = sys.argv[1]
try:
    with urllib.request.urlopen(url, timeout=10) as r:
        data = json.loads(r.read())
except Exception as e:
    print(f"CRITICAL - Cannot reach {url}: {e}")
    sys.exit(2)

if data.get('status') != 'healthy':
    details = data.get('message', 'no details')
    print(f"CRITICAL - App reports unhealthy: {details}")
    sys.exit(2)

print(f"OK - App healthy: {data.get('version', 'unknown')}")
sys.exit(0)
```

---

## Monitoring VMware/vSphere

Use the community `check_vmware_api.pl` plugin:

```bash
# VM power state
check_vmware_api.pl -H vcenter.example.com -u monitoring -p pass \
  --sessionfile /tmp/vmware_sess \
  -l runtime --subcommand con

# Datastore space
check_vmware_api.pl -H vcenter.example.com -u monitoring -p pass \
  --sessionfile /tmp/vmware_sess \
  -l datastores -x "Datastore01" -w 80 -c 90

# Host CPU/memory
check_vmware_api.pl -H vcenter.example.com -u monitoring -p pass \
  --sessionfile /tmp/vmware_sess \
  -l cpu -w 80 -c 95
```

---

## Monitoring Amazon Web Services (AWS)

### Using AWS CLI + custom plugins

```bash
#!/bin/bash
# check_aws_rds_connections.sh
INSTANCE=$1
WARN=$2
CRIT=$3

CONNECTIONS=$(aws cloudwatch get-metric-statistics \
  --namespace AWS/RDS \
  --metric-name DatabaseConnections \
  --dimensions Name=DBInstanceIdentifier,Value="$INSTANCE" \
  --start-time "$(date -u -d '5 minutes ago' +%Y-%m-%dT%H:%M:%SZ)" \
  --end-time "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
  --period 300 \
  --statistics Average \
  --query 'Datapoints[0].Average' \
  --output text)

if [ "$CONNECTIONS" = "None" ]; then
    echo "UNKNOWN - No CloudWatch data available"
    exit 3
fi

# Compare and exit appropriately
python3 -c "
c=$CONNECTIONS; w=$WARN; cr=$CRIT
if c >= cr:
    print(f'CRITICAL - {c:.0f} connections|connections={c:.0f};{w};{cr}'); exit(2)
elif c >= w:
    print(f'WARNING - {c:.0f} connections|connections={c:.0f};{w};{cr}'); exit(1)
else:
    print(f'OK - {c:.0f} connections|connections={c:.0f};{w};{cr}'); exit(0)
"
```

### nagios-cloudwatch-plugin (community)

```bash
check_cloudwatch.py --namespace AWS/EC2 \
  --metric-name CPUUtilization \
  --dimensions InstanceId=i-1234567890abcdef0 \
  --statistics Average --period 300 \
  --warning 80 --critical 95
```

---

## Plugin Best Practices

1. **Always handle timeout**: Use `alarm()` (C) or `socket_timeout` to avoid hanging checks
2. **Validate all arguments**: Return UNKNOWN with usage message for missing/invalid args
3. **Single line of key output**: Web interface shows only first line prominently
4. **Include performance data**: Enables graphing and trending
5. **Test as nagios user**: `sudo -u nagios /path/to/plugin [args]`
6. **Use specific exit codes**: Never exit without explicit code (shell default is 0 = OK)
7. **Handle connection errors**: Network unavailable → UNKNOWN, not CRITICAL
8. **Sign/copyright header**: Helps maintainability and attribution
