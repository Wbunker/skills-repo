# Cloud Monitoring — CLI Reference

---

## Alerting Policies

```bash
# List alerting policies
gcloud monitoring policies list --project=my-project

# Describe a policy
gcloud monitoring policies describe POLICY_ID --project=my-project

# Create alerting policy from JSON file
# (policies are complex JSON; easier to define in file than inline)
cat > alert-policy.json << 'EOF'
{
  "displayName": "High CPU Alert",
  "conditions": [
    {
      "displayName": "CPU utilization > 80%",
      "conditionThreshold": {
        "filter": "resource.type = \"gce_instance\" AND metric.type = \"compute.googleapis.com/instance/cpu/utilization\"",
        "comparison": "COMPARISON_GT",
        "thresholdValue": 0.8,
        "duration": "300s",
        "aggregations": [
          {
            "alignmentPeriod": "60s",
            "perSeriesAligner": "ALIGN_MEAN"
          }
        ]
      }
    }
  ],
  "alertStrategy": {
    "notificationRateLimit": {
      "period": "300s"
    }
  },
  "combiner": "OR",
  "enabled": true,
  "notificationChannels": ["projects/my-project/notificationChannels/CHANNEL_ID"],
  "documentation": {
    "content": "Runbook: https://wiki.example.com/runbooks/high-cpu",
    "mimeType": "text/markdown"
  }
}
EOF

gcloud monitoring policies create \
  --policy-from-file=alert-policy.json \
  --project=my-project

# Update an alerting policy from file
gcloud monitoring policies update POLICY_ID \
  --policy-from-file=updated-policy.json \
  --project=my-project

# Enable/disable a policy
gcloud monitoring policies update POLICY_ID \
  --enabled \
  --project=my-project

gcloud monitoring policies update POLICY_ID \
  --no-enabled \
  --project=my-project

# Delete a policy
gcloud monitoring policies delete POLICY_ID --project=my-project

# Create a snooze (suppress alert notifications temporarily)
gcloud monitoring snoozes create \
  --display-name="Planned maintenance window" \
  --start-time="2024-06-01T02:00:00Z" \
  --end-time="2024-06-01T04:00:00Z" \
  --criteria-policies=POLICY_ID_1,POLICY_ID_2 \
  --project=my-project

# List snoozes
gcloud monitoring snoozes list --project=my-project
```

---

## Notification Channels

```bash
# Create an email notification channel
gcloud monitoring channels create \
  --display-name="On-call Email" \
  --type=email \
  --channel-labels=email_address=oncall@example.com \
  --project=my-project

# Create a Slack notification channel
gcloud monitoring channels create \
  --display-name="Alerts Slack Channel" \
  --type=slack \
  --channel-labels=channel_name=#alerts,auth_token=xoxb-your-token \
  --project=my-project

# Create a Pub/Sub notification channel (for webhooks / custom integrations)
gcloud monitoring channels create \
  --display-name="Alert Pub/Sub" \
  --type=pubsub \
  --channel-labels=topic=projects/my-project/topics/monitoring-alerts \
  --project=my-project

# Create a PagerDuty notification channel
gcloud monitoring channels create \
  --display-name="PagerDuty Production" \
  --type=pagerduty \
  --channel-labels=service_key=YOUR_PAGERDUTY_SERVICE_KEY \
  --project=my-project

# List notification channels
gcloud monitoring channels list --project=my-project

# Describe a channel
gcloud monitoring channels describe CHANNEL_ID --project=my-project

# Update a channel
gcloud monitoring channels update CHANNEL_ID \
  --display-name="Updated Channel Name" \
  --project=my-project

# Verify a channel (sends test notification)
gcloud monitoring channels verify CHANNEL_ID --project=my-project

# Delete a channel
gcloud monitoring channels delete CHANNEL_ID --project=my-project
```

---

## Uptime Checks

```bash
# Create an HTTPS uptime check
gcloud monitoring uptime create my-service-uptime \
  --display-name="My Service HTTPS Check" \
  --resource-type=uptime_url \
  --hostname=my-service.example.com \
  --path=/health \
  --port=443 \
  --check-interval=5m \
  --timeout=10s \
  --project=my-project

# Create an HTTP check with content matching
gcloud monitoring uptime create api-health-check \
  --display-name="API Health Check" \
  --resource-type=uptime_url \
  --hostname=api.example.com \
  --path=/api/health \
  --port=80 \
  --check-interval=1m \
  --content-type=text/plain \
  --body='"status":"ok"' \
  --project=my-project

# Create a TCP uptime check
gcloud monitoring uptime create db-tcp-check \
  --display-name="Database TCP Check" \
  --resource-type=uptime_url \
  --hostname=10.1.2.3 \
  --port=5432 \
  --check-interval=5m \
  --project=my-project

# List uptime checks
gcloud monitoring uptime list --project=my-project

# Describe an uptime check
gcloud monitoring uptime describe CHECK_ID --project=my-project

# Update an uptime check
gcloud monitoring uptime update CHECK_ID \
  --display-name="Updated Check Name" \
  --check-interval=10m \
  --project=my-project

# Delete an uptime check
gcloud monitoring uptime delete CHECK_ID --project=my-project
```

---

## Dashboards

```bash
# List dashboards
gcloud monitoring dashboards list --project=my-project

# Describe a dashboard (outputs full JSON)
gcloud monitoring dashboards describe DASHBOARD_NAME --project=my-project

# Create a dashboard from JSON file
gcloud monitoring dashboards create \
  --config-from-file=my-dashboard.json \
  --project=my-project

# Update a dashboard from JSON file
gcloud monitoring dashboards update DASHBOARD_NAME \
  --config-from-file=updated-dashboard.json \
  --project=my-project

# Delete a dashboard
gcloud monitoring dashboards delete DASHBOARD_NAME --project=my-project

# Export an existing dashboard to JSON (for version control)
gcloud monitoring dashboards describe DASHBOARD_NAME \
  --format=json \
  --project=my-project > dashboard-backup.json
```

---

## Metrics

```bash
# List all available metric types
gcloud monitoring metrics list --project=my-project

# List metrics for a specific service
gcloud monitoring metrics list \
  --filter="metric.type:starts_with('compute.googleapis.com')" \
  --project=my-project

# List custom metrics only
gcloud monitoring metrics list \
  --filter="metric.type:starts_with('custom.googleapis.com')" \
  --project=my-project

# Describe a metric type (shows labels, value type, units)
gcloud monitoring metrics describe \
  compute.googleapis.com/instance/cpu/utilization \
  --project=my-project

# List log-based metrics
gcloud logging metrics list --project=my-project
```

---

## SLO Monitoring

```bash
# Create a service (required before creating SLOs)
gcloud monitoring services create \
  --display-name="My Production API" \
  --custom \
  --project=my-project

# Or create from App Engine / GKE (auto-discovers services)
# Services are often auto-created; list them:
gcloud monitoring services list --project=my-project

# Create a request-based availability SLO (99.9% over 30 days)
cat > slo-config.json << 'EOF'
{
  "displayName": "99.9% API Availability",
  "goal": 0.999,
  "rollingPeriod": "2592000s",
  "requestBased": {
    "goodTotalRatio": {
      "goodServiceFilter": "metric.type=\"loadbalancing.googleapis.com/https/request_count\" resource.type=\"https_lb_rule\" metric.label.response_code_class=\"2xx\"",
      "totalServiceFilter": "metric.type=\"loadbalancing.googleapis.com/https/request_count\" resource.type=\"https_lb_rule\""
    }
  }
}
EOF

gcloud monitoring services slos create SERVICE_ID \
  --slo-from-file=slo-config.json \
  --project=my-project

# Create a latency-based SLO (95% of requests < 200ms)
cat > latency-slo.json << 'EOF'
{
  "displayName": "95% Requests < 200ms",
  "goal": 0.95,
  "rollingPeriod": "86400s",
  "requestBased": {
    "distributionCut": {
      "distributionFilter": "metric.type=\"loadbalancing.googleapis.com/https/backend_latencies\" resource.type=\"https_lb_rule\"",
      "range": {
        "max": 200
      }
    }
  }
}
EOF

gcloud monitoring services slos create SERVICE_ID \
  --slo-from-file=latency-slo.json \
  --project=my-project

# List SLOs for a service
gcloud monitoring services slos list SERVICE_ID --project=my-project

# Describe an SLO
gcloud monitoring services slos describe SLO_ID \
  --service=SERVICE_ID \
  --project=my-project

# Delete an SLO
gcloud monitoring services slos delete SLO_ID \
  --service=SERVICE_ID \
  --project=my-project
```

---

## Managed Prometheus

```bash
# Enable the GKE Managed Prometheus collection on a cluster
gcloud container clusters update my-cluster \
  --enable-managed-prometheus \
  --region=us-central1 \
  --project=my-project

# Apply a PodMonitoring resource (Kubernetes CRD)
kubectl apply -f - << 'EOF'
apiVersion: monitoring.googleapis.com/v1
kind: PodMonitoring
metadata:
  name: my-app-monitoring
  namespace: production
spec:
  selector:
    matchLabels:
      app: my-app
  endpoints:
  - port: metrics
    interval: 30s
    path: /metrics
EOF

# Apply a ClusterPodMonitoring resource (cluster-wide)
kubectl apply -f - << 'EOF'
apiVersion: monitoring.googleapis.com/v1
kind: ClusterPodMonitoring
metadata:
  name: kubelet-monitoring
spec:
  selector:
    matchLabels:
      k8s-app: kubelet
  endpoints:
  - port: 10255
    interval: 30s
EOF

# Apply a Prometheus Rules resource (recording + alerting rules)
kubectl apply -f - << 'EOF'
apiVersion: monitoring.googleapis.com/v1
kind: Rules
metadata:
  name: my-app-rules
  namespace: production
spec:
  groups:
  - name: my-app-alerts
    interval: 30s
    rules:
    - alert: HighErrorRate
      expr: rate(http_requests_total{status=~"5.."}[5m]) / rate(http_requests_total[5m]) > 0.05
      for: 5m
      labels:
        severity: critical
      annotations:
        summary: "High error rate on {{ $labels.job }}"
EOF

# Query GMP from the command line (requires GMP query frontend)
# Get frontend service URL
kubectl get service frontend \
  -n gmp-public \
  -o jsonpath='{.status.loadBalancer.ingress[0].ip}'

# Query via curl (use bearer token)
TOKEN=$(gcloud auth print-access-token)
GMP_URL="https://monitoring.googleapis.com/v1/projects/my-project/location/global/prometheus"

curl -s "${GMP_URL}/api/v1/query" \
  -H "Authorization: Bearer ${TOKEN}" \
  --data-urlencode 'query=up' \
  --data-urlencode "time=$(date +%s)"
```

---

## Ops Agent Installation

```bash
# Install Ops Agent on Debian/Ubuntu
curl -sSO https://dl.google.com/cloudagents/add-google-cloud-ops-agent-repo.sh
sudo bash add-google-cloud-ops-agent-repo.sh --also-install
sudo systemctl status google-cloud-ops-agent

# Install on RHEL 8/CentOS 8
curl -sSO https://dl.google.com/cloudagents/add-google-cloud-ops-agent-repo.sh
sudo bash add-google-cloud-ops-agent-repo.sh --also-install

# Install on Windows Server (Run as Administrator in PowerShell)
(New-Object Net.WebClient).DownloadFile(
  "https://dl.google.com/cloudagents/add-google-cloud-ops-agent-repo.ps1",
  "$env:UserProfile\add-google-cloud-ops-agent-repo.ps1"
)
Invoke-Expression "$env:UserProfile\add-google-cloud-ops-agent-repo.ps1 -AlsoInstall"

# Verify Ops Agent is running
sudo systemctl status google-cloud-ops-agent

# View Ops Agent logs
sudo journalctl -u google-cloud-ops-agent --follow

# Install via gcloud (for GCE instances — uses VM manager)
gcloud compute instances ops-agents policies create ops-agent-policy \
  --agent-rules="type=ops-agent,version=current-major,package-state=installed,enable-autoupgrade=true" \
  --os-types=short-name=debian,version=11 \
  --instances=zones/us-central1-a/instances/my-vm \
  --project=my-project

# Apply Ops Agent policy to instances with specific labels
gcloud compute instances ops-agents policies create all-debian-policy \
  --agent-rules="type=ops-agent,version=current-major,package-state=installed,enable-autoupgrade=true" \
  --os-types=short-name=debian,version=11 \
  --group-labels=env=production \
  --project=my-project
```
