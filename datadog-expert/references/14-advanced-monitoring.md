# Advanced Monitoring Topics

Reference for APM, Synthetic Monitoring, Security Monitoring, and other advanced Datadog features.

## Table of Contents
- [Application Performance Monitoring (APM)](#application-performance-monitoring-apm)
- [Synthetic Monitoring](#synthetic-monitoring)
- [Security Monitoring](#security-monitoring)
- [Real User Monitoring (RUM)](#real-user-monitoring-rum)
- [CI Visibility](#ci-visibility)
- [Service Level Objectives (SLOs)](#service-level-objectives-slos)
- [Incident Management](#incident-management)

## Application Performance Monitoring (APM)

### Tracing Libraries
| Language | Library | Auto-Instrumentation |
|----------|---------|---------------------|
| Python | `ddtrace` | Yes (`ddtrace-run`) |
| Java | `dd-java-agent` | Yes (javaagent) |
| Go | `dd-trace-go` | Manual |
| Node.js | `dd-trace` | Yes (`--require dd-trace/init`) |
| Ruby | `ddtrace` | Yes |
| .NET | `dd-trace-dotnet` | Yes |
| PHP | `dd-trace-php` | Yes |
| Rust | `dd-trace-rb` | Manual |

### Python APM Setup
```bash
pip install ddtrace
```

```bash
# Auto-instrumentation
DD_SERVICE=myapp DD_ENV=production DD_VERSION=1.0.0 \
  ddtrace-run python app.py
```

```python
# Manual instrumentation
from ddtrace import tracer

@tracer.wrap(service="myapp", resource="process_order")
def process_order(order_id):
    with tracer.trace("db.query", service="postgres") as span:
        span.set_tag("order.id", order_id)
        result = db.query(f"SELECT * FROM orders WHERE id = {order_id}")
    return result
```

### Java APM Setup
```bash
java -javaagent:/path/to/dd-java-agent.jar \
  -Ddd.service=myapp \
  -Ddd.env=production \
  -Ddd.version=1.0.0 \
  -Ddd.trace.sample.rate=1.0 \
  -jar myapp.jar
```

### Node.js APM Setup
```javascript
// tracer.js (require first)
const tracer = require('dd-trace').init({
  service: 'myapp',
  env: 'production',
  version: '1.0.0',
});

module.exports = tracer;
```

```bash
DD_TRACE_ENABLED=true node --require ./tracer.js app.js
```

### Kubernetes Auto-Injection
With Admission Controller enabled:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: myapp
spec:
  template:
    metadata:
      labels:
        admission.datadoghq.com/enabled: "true"
      annotations:
        admission.datadoghq.com/java-lib.version: "latest"
    spec:
      containers:
        - name: myapp
          env:
            - name: DD_SERVICE
              value: myapp
            - name: DD_ENV
              value: production
```

### Key APM Concepts
- **Service**: A set of processes that do the same job (e.g., `web-api`, `payment-service`)
- **Resource**: A specific endpoint or query (e.g., `GET /api/users`, `SELECT * FROM orders`)
- **Trace**: End-to-end request journey across services
- **Span**: A single unit of work within a trace
- **Service Map**: Auto-generated dependency graph
- **Flame Graph**: Visual breakdown of span timing

### Trace Search and Analytics
```
# Find slow requests
service:api @duration:>5s

# Error traces for a specific endpoint
service:api resource_name:"GET /api/users" status:error

# Traces by custom tag
@order.id:12345
```

## Synthetic Monitoring

### API Tests
```json
{
  "name": "API Health Check",
  "type": "api",
  "subtype": "http",
  "config": {
    "request": {
      "method": "GET",
      "url": "https://api.example.com/health",
      "headers": {"Authorization": "Bearer {{SYNTHETIC_API_TOKEN}}"}
    },
    "assertions": [
      {"type": "statusCode", "operator": "is", "target": 200},
      {"type": "responseTime", "operator": "lessThan", "target": 2000},
      {"type": "body", "operator": "contains", "target": "\"status\":\"ok\""}
    ]
  },
  "locations": ["aws:us-east-1", "aws:eu-west-1", "aws:ap-northeast-1"],
  "options": {"tick_every": 60}
}
```

### Browser Tests
Record user flows in the Datadog UI:
1. Navigate to Synthetics > New Test > Browser Test
2. Enter starting URL
3. Record steps (click, type, assert, wait)
4. Set locations and frequency
5. Configure alerting

Common steps:
- `click` on element
- `type` text into input
- `assert` element content/visibility
- `wait` for element
- `extract` variable from page
- `upload` file
- `navigate` to URL

### Multi-Step API Tests
Chain multiple API calls with variable extraction:
```
Step 1: POST /auth/login → extract token
Step 2: GET /api/users (with token) → assert 200
Step 3: POST /api/orders (with token) → extract order_id
Step 4: GET /api/orders/{order_id} → assert order details
```

### Private Locations
Run synthetics from inside your network:
```bash
docker run -d --name dd-private-location \
  -e DATADOG_API_KEY=<key> \
  -e DATADOG_ACCESS_KEY=<access_key> \
  -e DATADOG_SECRET_ACCESS_KEY=<secret_key> \
  -e DATADOG_PRIVATE_KEY=<private_key> \
  -e DATADOG_PUBLIC_KEY_PEM=<pem> \
  gcr.io/datadoghq/synthetics-private-location-worker:latest
```

## Security Monitoring

### Cloud SIEM
Detect threats in logs using detection rules:
- **OOTB rules**: 600+ rules for AWS, GCP, Azure, Kubernetes, etc.
- **Custom rules**: Write detection rules in Datadog's query language

### Detection Rule Example
```
Rule: Brute Force Login Attempt
Query: source:auth status:error @action:login
Group by: @usr.id
Threshold: count > 10 in last 5 minutes
Severity: HIGH
```

### Cloud Security Management (CSM)
- **Threats**: Runtime threat detection on hosts and containers
- **Misconfigurations**: Scan cloud resources against compliance benchmarks (CIS, PCI-DSS, SOC 2)
- **Vulnerabilities**: Container image scanning, host vulnerability detection

### Security Signals
Investigated in: Security > Security Signals
- Triage: Info, Low, Medium, High, Critical
- Correlate with logs, traces, and infrastructure metrics
- Assign to team members for investigation

## Real User Monitoring (RUM)

### Browser SDK
```html
<script>
  (function(h,o,u,n,d) {
    h=h[d]=h[d]||{q:[],onReady:function(c){h.q.push(c)}}
    d=o.createElement(u);d.async=1;d.src=n
    n=o.getElementsByTagName(u)[0];n.parentNode.insertBefore(d,n)
  })(window,document,'script','https://www.datadoghq-browser-agent.com/datadog-rum-v5.js','DD_RUM')
  window.DD_RUM.onReady(function() {
    window.DD_RUM.init({
      clientToken: '<CLIENT_TOKEN>',
      applicationId: '<APPLICATION_ID>',
      site: 'datadoghq.com',
      service: 'my-web-app',
      env: 'production',
      version: '1.0.0',
      sessionSampleRate: 100,
      sessionReplaySampleRate: 20,
      trackUserInteractions: true,
      trackResources: true,
      trackLongTasks: true,
    })
  })
</script>
```

### RUM Metrics
- Core Web Vitals (LCP, FID, CLS)
- Page load times, resource timing
- User actions (clicks, scrolls)
- JS errors with stack traces
- Session replays

## CI Visibility

Track CI/CD pipeline performance:
- Pipeline execution time and success rate
- Test execution time and flakiness
- Correlate deployments with production metrics
- Supported: GitHub Actions, GitLab CI, Jenkins, CircleCI, Azure DevOps

## Service Level Objectives (SLOs)

### SLO Types

**Metric-Based:**
```
Numerator: sum:api.requests{status:2xx}.as_count()
Denominator: sum:api.requests{*}.as_count()
Target: 99.9% over 30 days
```

**Monitor-Based:**
```
Based on: Monitor "API Latency < 500ms"
Target: 99.95% uptime over 30 days
```

### Error Budget
- Budget = 100% - target (e.g., 99.9% → 0.1% error budget)
- Track remaining budget over rolling windows
- Alert when burn rate exceeds threshold (consuming budget too fast)

## Incident Management

### Workflow
1. **Declare**: Create incident from monitor alert, manual, or Slack
2. **Triage**: Set severity (SEV-1 to SEV-5), assign commander
3. **Investigate**: Use correlated metrics, logs, traces, dashboards
4. **Communicate**: Auto-update status page, Slack channels
5. **Resolve**: Mark resolved, set customer impact duration
6. **Postmortem**: Auto-generated timeline, link remediation items

### Incident API
```bash
curl -X POST "https://api.datadoghq.com/api/v2/incidents" \
  -H "DD-API-KEY: ${DD_API_KEY}" \
  -H "DD-APPLICATION-KEY: ${DD_APP_KEY}" \
  -d '{
    "data": {
      "type": "incidents",
      "attributes": {
        "title": "API latency spike in us-east-1",
        "customer_impact_scope": "Partial",
        "fields": {
          "severity": {"type": "dropdown", "value": "SEV-2"}
        }
      }
    }
  }'
```
