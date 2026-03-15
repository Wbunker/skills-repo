# App Engine — CLI Reference

Capabilities reference: [app-engine-capabilities.md](app-engine-capabilities.md)

App Engine uses `gcloud app` commands. The current directory must contain `app.yaml` for most deploy operations.

```bash
gcloud config set project my-project-id
```

---

## Application Setup

```bash
# Create the App Engine application in a project (one-time, region is permanent)
gcloud app create --region=us-central1

# Describe the app (shows region, services count, etc.)
gcloud app describe
```

---

## Deploy

```bash
# Deploy from the current directory (must contain app.yaml)
gcloud app deploy

# Deploy a specific app.yaml
gcloud app deploy app.yaml

# Deploy without prompting
gcloud app deploy --quiet

# Deploy a specific version (custom version name)
gcloud app deploy app.yaml --version=v20240115-1

# Deploy and do not promote to receive traffic (useful for canary staging)
gcloud app deploy app.yaml --version=v2 --no-promote

# Deploy multiple services at once
gcloud app deploy service1/app.yaml service2/app.yaml service3/app.yaml

# Deploy cron.yaml (update cron jobs)
gcloud app deploy cron.yaml

# Deploy dispatch.yaml (update URL routing rules)
gcloud app deploy dispatch.yaml

# Deploy queue.yaml (legacy task queue configuration)
gcloud app deploy queue.yaml

# Deploy with environment variables set at deploy time
gcloud app deploy app.yaml \
  --set-env-vars=ENVIRONMENT=production,DB_HOST=10.0.0.5

# Deploy to the staging environment (use a separate project)
gcloud app deploy app.yaml --project=my-project-staging
```

---

## Services

```bash
# List all services
gcloud app services list

# Describe a service
gcloud app services describe default
gcloud app services describe api-service

# Set traffic splitting between versions
gcloud app services set-traffic default \
  --splits=v2=0.8,v1=0.2 \
  --split-by=random

# Send 100% traffic to a specific version
gcloud app services set-traffic default \
  --splits=v3=1 \
  --split-by=random

# IP-based traffic splitting (session sticky)
gcloud app services set-traffic default \
  --splits=v2=0.9,v1=0.1 \
  --split-by=ip

# Cookie-based traffic splitting
gcloud app services set-traffic default \
  --splits=v2=0.9,v1=0.1 \
  --split-by=cookie

# Delete a service (deletes all its versions too)
gcloud app services delete old-service --quiet
```

---

## Versions

```bash
# List all versions of a service
gcloud app versions list

# List versions of a specific service
gcloud app versions list --service=default

# List versions with format showing traffic allocation
gcloud app versions list \
  --service=default \
  --format="table(id,service,traffic_split,servingStatus,environment,last_deployed_time.date())"

# Describe a specific version
gcloud app versions describe v20240115-1 --service=default

# Migrate 100% traffic to a specific version (gradual migration)
gcloud app versions migrate v3 --service=default

# Start a stopped version
gcloud app versions start v2 --service=default

# Stop a version (keeps it deployed but stops serving traffic and instances)
gcloud app versions stop v1 --service=default

# Delete a specific version (must not be receiving traffic)
gcloud app versions delete v1 --service=default --quiet

# Delete multiple old versions
gcloud app versions delete v1 v2 v3 --service=default --quiet

# Delete all versions not currently serving traffic
gcloud app versions list \
  --service=default \
  --filter="traffic_split=0" \
  --format="get(id)" | \
xargs gcloud app versions delete --service=default --quiet
```

---

## Browse

```bash
# Open the app in a browser
gcloud app browse

# Open a specific service
gcloud app browse --service=api-service

# Open a specific version
gcloud app browse --service=default --version=v2
```

---

## Logs

```bash
# Stream recent logs (tails by default)
gcloud app logs tail

# Tail logs for a specific service
gcloud app logs tail --service=api-service

# Read logs with a limit
gcloud app logs read --limit=100

# Read logs for a specific service and level
gcloud app logs read \
  --service=default \
  --level=error \
  --limit=50

# Read logs since a specific time
gcloud app logs read \
  --service=default \
  --start-time="2024-01-15T10:00:00Z"

# Use Cloud Logging for more powerful filtering
gcloud logging read \
  'resource.type="gae_app" AND resource.labels.module_id="default"' \
  --limit=100 \
  --format="table(timestamp,textPayload,severity)"

# View request logs
gcloud logging read \
  'resource.type="gae_app" AND logName=~"request_log"' \
  --limit=50
```

---

## Instances

```bash
# List running instances
gcloud app instances list

# List instances for a specific service and version
gcloud app instances list --service=default --version=v2

# Describe an instance
gcloud app instances describe i1a2b3c4 --service=default --version=v2

# SSH into a Flexible environment instance
gcloud app instances ssh i1a2b3c4 --service=backend --version=v2

# Enable debug mode on a Standard instance (for live debugging)
gcloud app instances enable-debug i1a2b3c4 \
  --service=default \
  --version=v2
```

---

## Domain Mappings

```bash
# Add a custom domain mapping
gcloud app domain-mappings create www.example.com

# List domain mappings
gcloud app domain-mappings list

# Describe a domain mapping (shows DNS records to configure)
gcloud app domain-mappings describe www.example.com

# Delete a domain mapping
gcloud app domain-mappings delete www.example.com --quiet
```

---

## Firewall Rules

```bash
# List App Engine firewall rules
gcloud app firewall-rules list

# Create a rule to allow a specific IP range
gcloud app firewall-rules create 100 \
  --action=ALLOW \
  --source-range=203.0.113.0/24 \
  --description="Allow corporate VPN"

# Create a deny rule
gcloud app firewall-rules create 200 \
  --action=DENY \
  --source-range=198.51.100.0/24 \
  --description="Block suspicious range"

# Update the default rule (allow/deny all other traffic)
gcloud app firewall-rules update default --action=DENY

# Delete a rule
gcloud app firewall-rules delete 100 --quiet
```

---

## Cron Jobs

```bash
# View current cron configuration
gcloud app describe  # cron jobs shown in output

# Deploy updated cron.yaml
gcloud app deploy cron.yaml

# Example cron.yaml content:
# cron:
# - description: "Daily cleanup"
#   url: /tasks/cleanup
#   schedule: every 24 hours
# - description: "Hourly sync"
#   url: /tasks/sync
#   schedule: every 1 hours
#   retry_parameters:
#     min_backoff_seconds: 2.5
#     max_backoff_seconds: 1000
#     max_retry_attempts: 5
```

---

## Dispatch Configuration

```bash
# Deploy dispatch.yaml to route URLs to services
# Example dispatch.yaml:
# dispatch:
# - url: "*/admin/*"
#   service: admin-service
# - url: "*/api/*"
#   service: api-service
# - url: "*/*"
#   service: default

gcloud app deploy dispatch.yaml
```
