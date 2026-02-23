# Monitoring Infrastructure

Reference for infrastructure monitoring with Datadog — host metrics, integrations, host maps, and platform components.

## Table of Contents
- [Host-Level Metrics](#host-level-metrics)
- [Host Map](#host-map)
- [Infrastructure Integrations](#infrastructure-integrations)
- [Network Monitoring](#network-monitoring)
- [Cloud Integrations](#cloud-integrations)
- [Database Monitoring](#database-monitoring)

## Host-Level Metrics

Core system metrics collected by the Agent:

### CPU
| Metric | Description |
|--------|-------------|
| `system.cpu.user` | % CPU in user space |
| `system.cpu.system` | % CPU in kernel space |
| `system.cpu.idle` | % CPU idle |
| `system.cpu.iowait` | % CPU waiting on I/O |
| `system.cpu.stolen` | % CPU stolen by hypervisor |
| `system.load.1` / `.5` / `.15` | Load average |

### Memory
| Metric | Description |
|--------|-------------|
| `system.mem.total` | Total physical memory |
| `system.mem.used` | Used memory |
| `system.mem.free` | Free memory |
| `system.mem.cached` | Cached memory |
| `system.mem.pct_usable` | % memory usable |
| `system.swap.used` | Swap usage |

### Disk
| Metric | Description |
|--------|-------------|
| `system.disk.total` | Total disk space |
| `system.disk.used` | Used disk space |
| `system.disk.free` | Free disk space |
| `system.disk.in_use` | % disk used |
| `system.io.r_s` / `w_s` | Read/write operations per second |
| `system.io.await` | Average I/O wait time |

### Network
| Metric | Description |
|--------|-------------|
| `system.net.bytes_rcvd` | Bytes received per second |
| `system.net.bytes_sent` | Bytes sent per second |
| `system.net.packets_in.error` | Inbound packet errors |
| `system.net.packets_out.error` | Outbound packet errors |

## Host Map

Visual representation of all hosts, grouped and colored by metrics or tags.

**Use cases:**
- Spot CPU hotspots across a fleet
- Identify hosts with high memory usage by availability zone
- Visualize deployment rollouts by coloring with app version

**Configuration:**
- Group by: tag key (e.g., `availability-zone`, `service`)
- Color by: metric (e.g., `system.cpu.user`)
- Size by: metric (e.g., `system.mem.total`)

## Infrastructure Integrations

### Web Servers
```yaml
# /etc/datadog-agent/conf.d/nginx.d/conf.yaml
init_config:
instances:
  - nginx_status_url: http://localhost:80/nginx_status
    tags:
      - service:web
      - env:production
```

```yaml
# /etc/datadog-agent/conf.d/apache.d/conf.yaml
init_config:
instances:
  - apache_status_url: http://localhost/server-status?auto
```

### Message Queues
```yaml
# /etc/datadog-agent/conf.d/kafka.d/conf.yaml
init_config:
instances:
  - host: localhost
    port: 9999  # JMX port
    tags:
      - service:kafka
```

```yaml
# /etc/datadog-agent/conf.d/rabbitmq.d/conf.yaml
init_config:
instances:
  - rabbitmq_api_url: http://localhost:15672/api/
    rabbitmq_user: datadog
    rabbitmq_pass: <password>
```

## Network Monitoring

### SNMP Monitoring
```yaml
# /etc/datadog-agent/conf.d/snmp.d/conf.yaml
init_config:
instances:
  - ip_address: 192.168.1.1
    community_string: public
    metrics:
      - OID: 1.3.6.1.2.1.2.2.1.10
        name: ifInOctets
      - OID: 1.3.6.1.2.1.2.2.1.16
        name: ifOutOctets
```

### Network Performance Monitoring (NPM)
Enable in `datadog.yaml`:
```yaml
network_config:
  enabled: true
```
Provides: flow-level visibility, DNS monitoring, service-to-service dependency mapping.

## Cloud Integrations

### AWS
1. Create IAM role with the Datadog AWS integration policy
2. Configure in Datadog: Integrations > Amazon Web Services
3. Select services to monitor (EC2, RDS, ELB, S3, Lambda, etc.)

Key AWS metrics auto-collected:
- EC2: `aws.ec2.cpuutilization`, `aws.ec2.network_in/out`
- RDS: `aws.rds.cpuutilization`, `aws.rds.database_connections`
- ELB/ALB: `aws.elb.request_count`, `aws.elb.latency`
- Lambda: `aws.lambda.duration`, `aws.lambda.errors`

### GCP
1. Create service account with Monitoring Viewer role
2. Configure in Datadog: Integrations > Google Cloud Platform
3. Upload service account key JSON

### Azure
1. Register Datadog as an app in Azure AD
2. Grant Reader role on subscriptions
3. Configure in Datadog: Integrations > Azure

## Database Monitoring

### PostgreSQL
```yaml
# conf.d/postgres.d/conf.yaml
init_config:
instances:
  - host: localhost
    port: 5432
    username: datadog
    password: <password>
    dbname: mydb
    dbm: true  # Enable Database Monitoring (query metrics, plans, activity)
    tags:
      - service:postgres
```

### MySQL
```yaml
# conf.d/mysql.d/conf.yaml
init_config:
instances:
  - host: localhost
    port: 3306
    username: datadog
    password: <password>
    dbm: true
```

### Redis
```yaml
# conf.d/redisdb.d/conf.yaml
init_config:
instances:
  - host: localhost
    port: 6379
    password: <password>
    tags:
      - service:redis
```

### Database Monitoring (DBM) Features
- **Query Metrics**: throughput, latency, errors per query
- **Query Samples**: individual query executions with explain plans
- **Active Sessions**: real-time view of running queries (wait events, blocking)
- **Connection tracking**: monitor connection pool utilization
