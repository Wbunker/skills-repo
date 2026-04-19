# Query Handler and External Integration
## Chapter 12: Query Handler, Unix Domain Sockets, NERD

---

## What Is the Query Handler?

The **Query Handler** (QH) is a Nagios 4 feature that provides a **bidirectional, socket-based interface** for external applications to communicate with a running Nagios instance.

Unlike the external command pipe (`nagios.cmd`) which is write-only, the Query Handler supports:
- **Queries** — ask Nagios for current status information
- **Commands** — submit commands (like the command pipe)
- **Subscriptions** — register for asynchronous event notifications (via NERD)

```
External Application
        │
        │  Unix domain socket
        │  /usr/local/nagios/var/rw/nagios.qh
        ▼
   ┌─────────────────────┐
   │   Query Handler     │
   │   (Nagios 4 core)   │
   ├─────────────────────┤
   │  @core — core state │
   │  @status — obj state│
   │  @nerd — events     │
   │  @wproc — workers   │
   └─────────────────────┘
```

---

## Enabling the Query Handler

### nagios.cfg

```ini
# Query Handler is enabled by default in Nagios 4
# Socket path:
query_socket=/usr/local/nagios/var/rw/nagios.qh
```

Verify the socket exists:

```bash
ls -la /usr/local/nagios/var/rw/nagios.qh
# srwxrwxr-x 1 nagios nagcmd ... nagios.qh
```

---

## Communicating with the Query Handler

### Using socat or nc

```bash
# Single query then disconnect
echo "@core version" | socat - UNIX-CONNECT:/usr/local/nagios/var/rw/nagios.qh

# Interactive session
socat - UNIX-CONNECT:/usr/local/nagios/var/rw/nagios.qh
```

### Query Syntax

```
@<handler> [command] [arguments]
```

---

## Core Query Handler (@core)

```bash
# Get Nagios version
echo "@core version" | socat - UNIX-CONNECT:/usr/local/nagios/var/rw/nagios.qh

# Get Nagios process information
echo "@core pid" | socat - UNIX-CONNECT:/usr/local/nagios/var/rw/nagios.qh

# Get scheduling queue information
echo "@core scheduling_queue" | socat - UNIX-CONNECT:/usr/local/nagios/var/rw/nagios.qh

# Get worker process stats
echo "@wproc list" | socat - UNIX-CONNECT:/usr/local/nagios/var/rw/nagios.qh
```

---

## Status Query Handler (@status)

Query live object status:

```bash
# List all hosts in non-OK state
echo "@status list hosts state!=0" | socat - UNIX-CONNECT:/usr/local/nagios/var/rw/nagios.qh

# Get status of a specific host
echo "@status list hosts name=web01" | socat - UNIX-CONNECT:/usr/local/nagios/var/rw/nagios.qh

# Get all CRITICAL services
echo "@status list services state=2" | socat - UNIX-CONNECT:/usr/local/nagios/var/rw/nagios.qh

# Get services for a specific host
echo "@status list services host_name=web01" | socat - UNIX-CONNECT:/usr/local/nagios/var/rw/nagios.qh
```

---

## NERD — Nagios Event Radio Dispatcher

NERD is a subscription-based mechanism within the Query Handler that broadcasts Nagios events to connected subscribers in real-time.

### NERD Use Cases

- Build real-time dashboards without polling
- Trigger external actions immediately when state changes
- Feed events into a message bus (Kafka, RabbitMQ)
- Integrate with incident management systems (PagerDuty, ServiceNow)

### Subscribing to Events

```bash
# Subscribe to all service check results
echo "@nerd subscribe servicecheck" | socat - UNIX-CONNECT:/usr/local/nagios/var/rw/nagios.qh

# The connection stays open; Nagios pushes events as they occur:
# servicecheck web01 HTTP 0 "HTTP OK: 200"
# servicecheck db01 MySQL 2 "CRITICAL: Connection refused"
```

### NERD Event Types

| Event | Description |
|-------|-------------|
| `servicecheck` | Service check result |
| `hostcheck` | Host check result |
| `contactnotification` | Notification sent to a contact |
| `contactnotificationmethod` | Specific notification method called |
| `serviceflapping` | Service flap state change |
| `hostflapping` | Host flap state change |
| `comment` | Comment added/removed |
| `downtime` | Downtime scheduled/started/ended |
| `acknowledgement` | Problem acknowledged |

---

## Practical Integration Examples

### Real-Time Status Dashboard (Python)

```python
#!/usr/bin/env python3
"""Subscribe to Nagios events and push to a web dashboard via WebSocket"""
import socket
import threading

QH_SOCKET = "/usr/local/nagios/var/rw/nagios.qh"

def subscribe_to_events():
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    sock.connect(QH_SOCKET)
    
    # Subscribe to service checks
    sock.sendall(b"@nerd subscribe servicecheck\n")
    
    buf = b""
    while True:
        data = sock.recv(4096)
        if not data:
            break
        buf += data
        lines = buf.split(b"\n")
        buf = lines[-1]  # keep partial line
        for line in lines[:-1]:
            process_event(line.decode())

def process_event(line):
    # Parse: "servicecheck hostname service_desc state output"
    parts = line.split(None, 4)
    if len(parts) >= 5:
        event_type, host, service, state, output = parts
        print(f"STATE CHANGE: {host}/{service} → {state}: {output}")
        # push_to_dashboard(host, service, state, output)

if __name__ == "__main__":
    subscribe_to_events()
```

### Query Current Outages (Shell)

```bash
#!/bin/bash
# List all current CRITICAL services
echo "@status list services state=2" | \
  socat - UNIX-CONNECT:/usr/local/nagios/var/rw/nagios.qh | \
  while IFS=$'\t' read -r host svc state output; do
    echo "CRITICAL: $host/$svc — $output"
  done
```

### Submit Commands via Query Handler

The Query Handler also accepts external commands in the same format as the command pipe:

```bash
NOW=$(date +%s)
echo "COMMAND [$NOW] ACKNOWLEDGE_SVC_PROBLEM;web01;HTTP;1;1;1;admin;Investigating" | \
  socat - UNIX-CONNECT:/usr/local/nagios/var/rw/nagios.qh
```

---

## Query Handler vs. Command Pipe

| Feature | Command Pipe (`nagios.cmd`) | Query Handler (socket) |
|---------|----------------------------|----------------------|
| Direction | Write-only | Bidirectional |
| Read status | No | Yes |
| Real-time events | No | Yes (NERD) |
| Protocol | Simple line format | @handler protocol |
| Connection | Open/write/close | Persistent or transient |
| Availability | Nagios 2+ | Nagios 4+ only |

---

## Worker Process Interface (@wproc)

The worker process interface allows monitoring of Nagios's internal check execution workers:

```bash
# List workers and their status
echo "@wproc list" | socat - UNIX-CONNECT:/usr/local/nagios/var/rw/nagios.qh

# Get worker statistics
echo "@wproc info" | socat - UNIX-CONNECT:/usr/local/nagios/var/rw/nagios.qh
```

Worker stats reveal check execution performance — useful for diagnosing:
- Check latency (checks waiting in queue)
- Worker saturation (all workers busy)
- Execution time outliers (slow plugins)
