# Integrating with Platform Components

Reference for configuring Datadog integrations with common platform services and tools.

## Table of Contents
- [Integration Architecture](#integration-architecture)
- [Web Server Integrations](#web-server-integrations)
- [Database Integrations](#database-integrations)
- [Cache and Queue Integrations](#cache-and-queue-integrations)
- [Cloud Platform Integrations](#cloud-platform-integrations)
- [Configuration Management](#configuration-management)

## Integration Architecture

### Integration Types
| Type | Mechanism | Example |
|------|-----------|---------|
| **Agent Check** | Agent polls service metrics via protocol | Nginx, PostgreSQL, Redis |
| **JMX Check** | Agent connects to JMX MBeans | Kafka, Cassandra, Tomcat |
| **Crawler** | Datadog backend polls external API | AWS, GCP, Azure, GitHub |
| **Library** | App-embedded SDK sends data | APM tracing libraries |
| **Log Integration** | Agent tails/collects logs with parsing pipelines | Any log source |

### Integration Configuration
All agent-based integrations configured in `/etc/datadog-agent/conf.d/<integration>.d/conf.yaml`:

```yaml
init_config:
  # Global settings for the integration

instances:
  - <instance_config>
    tags:
      - env:production
      - service:myservice

logs:
  - type: file
    path: /var/log/myservice/*.log
    service: myservice
    source: myservice
```

## Web Server Integrations

### Nginx
Enable the stub_status module:
```nginx
server {
    location /nginx_status {
        stub_status;
        allow 127.0.0.1;
        deny all;
    }
}
```

Agent config:
```yaml
instances:
  - nginx_status_url: http://localhost/nginx_status
```

Key metrics: `nginx.net.connections`, `nginx.net.request_per_s`, `nginx.net.waiting`

### Apache
Enable mod_status:
```apache
<Location "/server-status">
    SetHandler server-status
    Require local
</Location>
```

Agent config:
```yaml
instances:
  - apache_status_url: http://localhost/server-status?auto
```

### HAProxy
```yaml
instances:
  - url: http://localhost/admin?stats
    username: admin
    password: <password>
```

## Database Integrations

### PostgreSQL
Create monitoring user:
```sql
CREATE USER datadog WITH PASSWORD '<password>';
GRANT pg_monitor TO datadog;
GRANT SELECT ON pg_stat_database TO datadog;
```

Agent config:
```yaml
instances:
  - host: localhost
    port: 5432
    username: datadog
    password: <password>
    dbm: true
    tags:
      - service:postgres
```

### MySQL
```sql
CREATE USER 'datadog'@'localhost' IDENTIFIED BY '<password>';
GRANT REPLICATION CLIENT, PROCESS ON *.* TO 'datadog'@'localhost';
GRANT SELECT ON performance_schema.* TO 'datadog'@'localhost';
```

### MongoDB
```yaml
instances:
  - hosts:
      - localhost:27017
    username: datadog
    password: <password>
    database: admin
```

### Elasticsearch
```yaml
instances:
  - url: http://localhost:9200
    cluster_stats: true
    pshard_stats: true
```

## Cache and Queue Integrations

### Redis
```yaml
instances:
  - host: localhost
    port: 6379
    password: <password>
    keys:
      - myapp:queue:*  # Track key patterns
```

Key metrics: `redis.mem.used`, `redis.net.clients`, `redis.keys.count`, `redis.slowlog.micros.95percentile`

### Memcached
```yaml
instances:
  - url: localhost
    port: 11211
```

### Kafka
```yaml
instances:
  - host: localhost
    port: 9999  # JMX port
    tags:
      - service:kafka
```

Key metrics: `kafka.consumer.lag`, `kafka.messages_in.rate`, `kafka.request.produce.time.99percentile`

### RabbitMQ
```yaml
instances:
  - rabbitmq_api_url: http://localhost:15672/api/
    rabbitmq_user: datadog
    rabbitmq_pass: <password>
    queues:
      - myapp.*
    queues_regexes:
      - test_.*
```

## Cloud Platform Integrations

### AWS Setup
1. **CloudFormation**: Use Datadog's CF template to create IAM role
2. **Terraform**:
```hcl
resource "datadog_integration_aws" "main" {
  account_id = "123456789012"
  role_name  = "DatadogIntegrationRole"
}
```

### Supported AWS Services (Partial List)
EC2, ECS, EKS, Lambda, RDS, Aurora, DynamoDB, ElastiCache, S3, SQS, SNS, ALB/NLB, CloudFront, API Gateway, Step Functions, Kinesis, Redshift

### GCP Setup
```hcl
resource "datadog_integration_gcp" "main" {
  project_id     = "my-project-id"
  private_key_id = var.gcp_private_key_id
  private_key    = var.gcp_private_key
  client_email   = "datadog@my-project.iam.gserviceaccount.com"
  client_id      = "1234567890"
}
```

### Azure Setup
Configure via App Registration with Reader role on target subscriptions.

## Configuration Management

### Ansible
```yaml
- name: Configure Datadog Nginx integration
  datadog_integration:
    name: nginx
    instances:
      - nginx_status_url: http://localhost/nginx_status
        tags:
          - env:production
```

### Terraform
```hcl
resource "datadog_integration_aws" "main" {
  account_id = "123456789012"
  role_name  = "DatadogIntegrationRole"
  filter_tags = ["env:production"]
  account_specific_namespace_rules = {
    auto_scaling = false
    opsworks     = false
  }
}
```
