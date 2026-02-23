# Developing Custom Integrations

Reference for building custom Datadog integrations and extending the Agent.

## Table of Contents
- [Custom Agent Checks](#custom-agent-checks)
- [Integration Development Kit](#integration-development-kit)
- [Webhooks and Pipelines](#webhooks-and-pipelines)
- [Terraform Provider](#terraform-provider)
- [Ansible Module](#ansible-module)

## Custom Agent Checks

Write Python checks that run inside the Datadog Agent.

### Basic Custom Check
```python
# /etc/datadog-agent/checks.d/my_check.py
from datadog_checks.base import AgentCheck

class MyCheck(AgentCheck):
    def check(self, instance):
        # Submit a gauge metric
        self.gauge('my_app.queue_depth', self.get_queue_depth(),
                   tags=['service:myapp', 'env:production'])

        # Submit a service check
        try:
            if self.is_healthy():
                self.service_check('my_app.health', AgentCheck.OK,
                                   message='Service is healthy')
            else:
                self.service_check('my_app.health', AgentCheck.CRITICAL,
                                   message='Service is unhealthy')
        except Exception as e:
            self.service_check('my_app.health', AgentCheck.CRITICAL,
                               message=str(e))

        # Submit an event
        self.event({
            'msg_title': 'Queue depth high',
            'msg_text': 'Queue depth exceeded threshold',
            'alert_type': 'warning',
            'tags': ['service:myapp']
        })

    def get_queue_depth(self):
        # Custom logic to measure queue depth
        return 42

    def is_healthy(self):
        return True
```

### Configuration
```yaml
# /etc/datadog-agent/conf.d/my_check.d/conf.yaml
init_config:

instances:
  - endpoint: http://localhost:8080/stats
    min_collection_interval: 30
    tags:
      - service:myapp
```

### HTTP Check Example
```python
from datadog_checks.base import AgentCheck
import requests

class HttpApiCheck(AgentCheck):
    def check(self, instance):
        url = instance.get('endpoint')
        timeout = instance.get('timeout', 10)

        try:
            response = requests.get(url, timeout=timeout)
            response_time = response.elapsed.total_seconds()

            self.gauge('api.response_time', response_time,
                       tags=instance.get('tags', []))

            if response.status_code == 200:
                self.service_check('api.status', AgentCheck.OK)
                data = response.json()
                for key, value in data.items():
                    if isinstance(value, (int, float)):
                        self.gauge(f'api.{key}', value,
                                   tags=instance.get('tags', []))
            else:
                self.service_check('api.status', AgentCheck.WARNING,
                                   message=f'HTTP {response.status_code}')
        except Exception as e:
            self.service_check('api.status', AgentCheck.CRITICAL,
                               message=str(e))
```

## Integration Development Kit

For publishing integrations to the Datadog community or marketplace.

### Setup
```bash
pip install "datadog-checks-dev[cli]"
ddev config set repo extras

# Scaffold a new integration
ddev create <integration_name>
```

### Generated Structure
```
<integration_name>/
├── datadog_checks/
│   └── <integration_name>/
│       ├── __init__.py
│       ├── check.py          # Main check logic
│       ├── config_models/    # Pydantic config models
│       └── data/
│           └── conf.yaml.example
├── tests/
│   ├── conftest.py
│   └── test_<integration_name>.py
├── manifest.json             # Integration metadata
├── metadata.csv              # Metric definitions
├── service_checks.json       # Service check definitions
└── setup.py
```

### Testing
```bash
ddev test <integration_name>
ddev test <integration_name> --bench  # Performance benchmarks
```

## Webhooks and Pipelines

### Webhook Integration
Send Datadog alerts to any HTTP endpoint:

1. Configure in Datadog: Integrations > Webhooks
2. Set URL, payload template, custom headers

```json
{
  "name": "custom-webhook",
  "url": "https://api.example.com/webhook",
  "custom_headers": {"Authorization": "Bearer <token>"},
  "payload": {
    "alert_id": "$ALERT_ID",
    "alert_title": "$ALERT_TITLE",
    "alert_status": "$ALERT_STATUS",
    "hostname": "$HOSTNAME",
    "event_msg": "$EVENT_MSG",
    "tags": "$TAGS"
  }
}
```

Use in monitor notifications: `@webhook-custom-webhook`

## Terraform Provider

Manage Datadog resources as infrastructure-as-code.

### Provider Setup
```hcl
terraform {
  required_providers {
    datadog = {
      source  = "DataDog/datadog"
      version = "~> 3.0"
    }
  }
}

provider "datadog" {
  api_key = var.datadog_api_key
  app_key = var.datadog_app_key
  api_url = "https://api.datadoghq.com/"
}
```

### Common Resources
```hcl
# Monitor
resource "datadog_monitor" "cpu" {
  name    = "High CPU on {{host.name}}"
  type    = "metric alert"
  query   = "avg(last_5m):avg:system.cpu.user{env:production} by {host} > 90"
  message = "CPU high @slack-ops"
  tags    = ["team:platform"]
  monitor_thresholds { critical = 90; warning = 80 }
}

# Dashboard
resource "datadog_dashboard_json" "overview" {
  dashboard = file("${path.module}/dashboards/overview.json")
}

# Downtime
resource "datadog_downtime" "maintenance" {
  scope      = ["env:staging"]
  start      = 1234567890
  end        = 1234571490
  message    = "Weekly maintenance"
  recurrence { type = "weeks"; period = 1; week_days = ["Sat"] }
}

# SLO
resource "datadog_service_level_objective" "api_availability" {
  name = "API Availability"
  type = "metric"
  query {
    numerator   = "sum:api.requests.success{service:api}.as_count()"
    denominator = "sum:api.requests.total{service:api}.as_count()"
  }
  thresholds { timeframe = "30d"; target = 99.9; warning = 99.95 }
  tags = ["service:api", "team:platform"]
}

# Synthetic test
resource "datadog_synthetics_test" "api_health" {
  name      = "API Health Check"
  type      = "api"
  subtype   = "http"
  status    = "live"
  locations = ["aws:us-east-1", "aws:eu-west-1"]
  request_definition {
    method = "GET"
    url    = "https://api.example.com/health"
  }
  assertion { type = "statusCode"; operator = "is"; target = "200" }
  options_list { tick_every = 60 }
}
```

## Ansible Module

### Datadog Agent Role
```yaml
- hosts: all
  roles:
    - role: datadog.datadog
      datadog_api_key: "{{ vault_datadog_api_key }}"
      datadog_agent_version: "7.50.0"
      datadog_config:
        tags:
          - env:production
          - team:backend
        logs_enabled: true
        apm_config:
          enabled: true
      datadog_checks:
        nginx:
          instances:
            - nginx_status_url: http://localhost/nginx_status
        postgres:
          instances:
            - host: localhost
              port: 5432
              username: datadog
              password: "{{ vault_postgres_password }}"
              dbm: true
```

### Monitor Management with Ansible
```yaml
- name: Create Datadog monitor
  datadog_monitor:
    api_key: "{{ datadog_api_key }}"
    app_key: "{{ datadog_app_key }}"
    state: present
    type: "metric alert"
    name: "High CPU on {{ '{{host.name}}' }}"
    query: "avg(last_5m):avg:system.cpu.user{env:production} by {host} > 90"
    message: "CPU is high @slack-ops"
    thresholds:
      critical: 90
      warning: 80
    tags:
      - team:platform
```
