# Using the Datadog REST API

Reference for interacting with Datadog programmatically via the REST API and client libraries.

## Table of Contents
- [Authentication](#authentication)
- [API Endpoints Overview](#api-endpoints-overview)
- [Common Operations](#common-operations)
- [Client Libraries](#client-libraries)
- [Rate Limits](#rate-limits)
- [Scripting Patterns](#scripting-patterns)

## Authentication

Every API request requires:
- **DD-API-KEY**: Your API key (for sending data)
- **DD-APPLICATION-KEY**: Your application key (for reading data / managing resources)

```bash
export DD_API_KEY="your_api_key"
export DD_APP_KEY="your_application_key"
export DD_SITE="datadoghq.com"  # or datadoghq.eu, us3.datadoghq.com, etc.
```

Base URL: `https://api.${DD_SITE}/api/v1/` (v1) or `https://api.${DD_SITE}/api/v2/` (v2)

## API Endpoints Overview

| Endpoint | Methods | Description |
|----------|---------|-------------|
| `/v1/monitor` | GET, POST, PUT, DELETE | Manage monitors |
| `/v1/dashboard` | GET, POST, PUT, DELETE | Manage dashboards |
| `/v1/downtime` | GET, POST, PUT, DELETE | Manage downtimes |
| `/v2/series` | POST | Submit metrics |
| `/v1/events` | GET, POST | Submit/query events |
| `/v1/graph/snapshot` | GET | Generate graph snapshots |
| `/v1/query` | GET | Query timeseries data |
| `/v1/check_run` | POST | Submit service checks |
| `/v1/hosts` | GET | Search/filter hosts |
| `/v1/tags/hosts` | GET, POST, PUT, DELETE | Manage host tags |
| `/v2/logs/events/search` | POST | Search logs |
| `/v1/synthetics/tests` | GET, POST, PUT, DELETE | Manage synthetic tests |
| `/v2/users` | GET, POST | Manage users |
| `/v2/api_keys` | GET, POST, DELETE | Manage API keys |

## Common Operations

### Query Metrics
```bash
# Query timeseries data
curl -s -G "https://api.datadoghq.com/api/v1/query" \
  -H "DD-API-KEY: ${DD_API_KEY}" \
  -H "DD-APPLICATION-KEY: ${DD_APP_KEY}" \
  --data-urlencode "from=$(date -d '1 hour ago' +%s)" \
  --data-urlencode "to=$(date +%s)" \
  --data-urlencode "query=avg:system.cpu.user{env:production} by {host}"
```

### Submit Metrics
```bash
curl -X POST "https://api.datadoghq.com/api/v2/series" \
  -H "Content-Type: application/json" \
  -H "DD-API-KEY: ${DD_API_KEY}" \
  -d '{
    "series": [{
      "metric": "custom.app.metric",
      "type": 1,
      "points": [{"timestamp": '"$(date +%s)"', "value": 42.0}],
      "tags": ["env:production", "service:myapp"]
    }]
  }'
```

### Manage Monitors
```bash
# List monitors with tag filter
curl -s "https://api.datadoghq.com/api/v1/monitor?monitor_tags=team:backend" \
  -H "DD-API-KEY: ${DD_API_KEY}" \
  -H "DD-APPLICATION-KEY: ${DD_APP_KEY}"

# Create monitor
curl -s -X POST "https://api.datadoghq.com/api/v1/monitor" \
  -H "Content-Type: application/json" \
  -H "DD-API-KEY: ${DD_API_KEY}" \
  -H "DD-APPLICATION-KEY: ${DD_APP_KEY}" \
  -d @monitor.json

# Update monitor
curl -s -X PUT "https://api.datadoghq.com/api/v1/monitor/<id>" \
  -H "Content-Type: application/json" \
  -H "DD-API-KEY: ${DD_API_KEY}" \
  -H "DD-APPLICATION-KEY: ${DD_APP_KEY}" \
  -d @monitor_update.json

# Delete monitor
curl -s -X DELETE "https://api.datadoghq.com/api/v1/monitor/<id>" \
  -H "DD-API-KEY: ${DD_API_KEY}" \
  -H "DD-APPLICATION-KEY: ${DD_APP_KEY}"
```

### Manage Dashboards
```bash
# List all dashboards
curl -s "https://api.datadoghq.com/api/v1/dashboard" \
  -H "DD-API-KEY: ${DD_API_KEY}" \
  -H "DD-APPLICATION-KEY: ${DD_APP_KEY}"

# Get dashboard by ID
curl -s "https://api.datadoghq.com/api/v1/dashboard/<dashboard_id>" \
  -H "DD-API-KEY: ${DD_API_KEY}" \
  -H "DD-APPLICATION-KEY: ${DD_APP_KEY}"

# Create dashboard from JSON
curl -s -X POST "https://api.datadoghq.com/api/v1/dashboard" \
  -H "Content-Type: application/json" \
  -H "DD-API-KEY: ${DD_API_KEY}" \
  -H "DD-APPLICATION-KEY: ${DD_APP_KEY}" \
  -d @dashboard.json
```

### Search Logs
```bash
curl -s -X POST "https://api.datadoghq.com/api/v2/logs/events/search" \
  -H "Content-Type: application/json" \
  -H "DD-API-KEY: ${DD_API_KEY}" \
  -H "DD-APPLICATION-KEY: ${DD_APP_KEY}" \
  -d '{
    "filter": {
      "query": "service:myapp status:error",
      "from": "now-1h",
      "to": "now"
    },
    "sort": "timestamp",
    "page": {"limit": 50}
  }'
```

### Host Tags
```bash
# Get tags for a host
curl -s "https://api.datadoghq.com/api/v1/tags/hosts/<hostname>" \
  -H "DD-API-KEY: ${DD_API_KEY}" \
  -H "DD-APPLICATION-KEY: ${DD_APP_KEY}"

# Add tags to a host
curl -s -X POST "https://api.datadoghq.com/api/v1/tags/hosts/<hostname>" \
  -H "Content-Type: application/json" \
  -H "DD-API-KEY: ${DD_API_KEY}" \
  -H "DD-APPLICATION-KEY: ${DD_APP_KEY}" \
  -d '{"tags": ["team:backend", "role:web"]}'
```

## Client Libraries

### Python (datadog-api-client)
```python
from datadog_api_client import Configuration, ApiClient
from datadog_api_client.v1.api.monitors_api import MonitorsApi

configuration = Configuration()
# Reads DD_API_KEY, DD_APP_KEY from environment

with ApiClient(configuration) as api_client:
    api = MonitorsApi(api_client)
    monitors = api.list_monitors(monitor_tags="team:backend")
    for m in monitors:
        print(f"{m.id}: {m.name} [{m.overall_state}]")
```

### Python (datadog — legacy/DogStatsD)
```python
from datadog import initialize, api

initialize(api_key='<key>', app_key='<key>')

# Create a monitor
api.Monitor.create(
    type='metric alert',
    query='avg(last_5m):avg:system.cpu.user{*} > 90',
    name='High CPU',
    message='CPU is high @slack-ops'
)
```

### Go
```go
import "github.com/DataDog/datadog-api-client-go/v2/api/datadogV1"

ctx := datadog.NewDefaultContext(context.Background())
configuration := datadog.NewConfiguration()
apiClient := datadog.NewAPIClient(configuration)
api := datadogV1.NewMonitorsApi(apiClient)
monitors, _, _ := api.ListMonitors(ctx)
```

### Ruby, Java, TypeScript
Official client libraries available: `datadog-api-client-ruby`, `datadog-api-client-java`, `datadog-api-client-typescript`

## Rate Limits

| Endpoint | Rate Limit |
|----------|-----------|
| Metric submission | 500,000 data points/minute |
| Event submission | 1,000 events/minute |
| Log submission | Varies by plan |
| API queries | 300 requests/hour per API+App key pair (varies by endpoint) |

Rate limit headers returned:
- `X-RateLimit-Limit`: max requests
- `X-RateLimit-Remaining`: remaining requests
- `X-RateLimit-Reset`: seconds until reset

## Scripting Patterns

### Bulk Operations
```python
"""Bulk mute monitors by tag during maintenance."""
from datadog_api_client import Configuration, ApiClient
from datadog_api_client.v1.api.monitors_api import MonitorsApi

with ApiClient(Configuration()) as client:
    api = MonitorsApi(client)
    monitors = api.list_monitors(monitor_tags="env:staging")
    for m in monitors:
        api.update_monitor(m.id, body={"options": {"silenced": {"*": None}}})
        print(f"Muted: {m.name}")
```

### Dashboard Export/Import
```python
"""Export all dashboards to JSON files for version control."""
import json
from datadog_api_client import Configuration, ApiClient
from datadog_api_client.v1.api.dashboards_api import DashboardsApi

with ApiClient(Configuration()) as client:
    api = DashboardsApi(client)
    dashboards = api.list_dashboards()
    for d in dashboards.dashboards:
        detail = api.get_dashboard(d.id)
        with open(f"dashboards/{d.id}.json", "w") as f:
            json.dump(detail.to_dict(), f, indent=2, default=str)
```

### Monitor-as-Code
```python
"""Create monitors from YAML definitions."""
import yaml
from datadog_api_client import Configuration, ApiClient
from datadog_api_client.v1.api.monitors_api import MonitorsApi
from datadog_api_client.v1.model.monitor import Monitor

with open("monitors.yaml") as f:
    monitors_config = yaml.safe_load(f)

with ApiClient(Configuration()) as client:
    api = MonitorsApi(client)
    for m in monitors_config["monitors"]:
        body = Monitor(**m)
        result = api.create_monitor(body=body)
        print(f"Created: {result.name} (ID: {result.id})")
```
