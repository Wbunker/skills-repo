# Managed Grafana & Managed Prometheus — Capabilities Reference
For CLI commands, see [observability-monitoring-cli.md](observability-monitoring-cli.md).

## Amazon Managed Grafana (AMG)

**Purpose**: Fully managed Grafana service that provisions, scales, and maintains Grafana workspaces; eliminates operational overhead of self-hosting while providing native AWS integrations and enterprise authentication.

### Core Concepts

| Concept | Description |
|---|---|
| **Workspace** | Isolated Grafana environment with its own URL, user base, and data sources; maps to a single Grafana instance |
| **Workspace URL** | Unique endpoint per workspace: `https://<workspace-id>.grafana-workspace.<region>.amazonaws.com` |
| **Grafana version** | AMG supports specific Grafana major versions; upgrades managed by AWS with minimal downtime |
| **Active user** | Billing unit; a user who logs in at least once during the billing month |
| **API key** | Service account token for programmatic access to the Grafana HTTP API (dashboard provisioning, alerting, etc.) |
| **Plugin** | Extension that adds a data source, panel type, or app; marketplace plugins available in addition to built-ins |

### Authentication

| Method | Description |
|---|---|
| **IAM Identity Center (SSO)** | Recommended; integrates with existing IdP (Okta, Azure AD, Active Directory) via IAM Identity Center; users and groups synced automatically |
| **SAML 2.0** | Direct SAML integration with any SAML-compliant IdP; configure assertion mapping for name, email, and role attributes |

### Authorization — Grafana Roles

| Role | Permissions |
|---|---|
| **Admin** | Full workspace control: manage users, data sources, dashboards, alerts, plugins, and workspace settings |
| **Editor** | Create and edit dashboards and alerts; cannot manage users or workspace settings |
| **Viewer** | Read-only access to dashboards; cannot edit dashboards or manage data sources |

Roles are assigned per workspace. IAM Identity Center groups can be mapped to Grafana roles for bulk assignment.

### Built-in Data Source Plugins

| Category | Data Sources |
|---|---|
| **AWS native** | Amazon CloudWatch, Amazon Managed Service for Prometheus (AMP), AWS X-Ray, Amazon Athena, Amazon OpenSearch Service, Amazon Timestream, AWS IoT SiteWise, Amazon Redshift |
| **Databases** | MySQL, PostgreSQL, Microsoft SQL Server, InfluxDB |
| **Time-series** | Prometheus, Graphite, OpenTSDB, Loki |
| **APM / tracing** | Jaeger, Zipkin, Tempo |
| **Other** | Elasticsearch, TestData DB, JSON API, and 30+ additional plugins via the marketplace |

### Alerting

| Feature | Description |
|---|---|
| **Grafana alerting** | Unified alerting engine built into Grafana; define alert rules against any data source using PromQL, CloudWatch Metrics Insights, or other query languages |
| **Alert rules** | Evaluate a query on a schedule; transition between Normal / Pending / Alerting / NoData / Error states |
| **Contact points** | Destinations for notifications: SNS, PagerDuty, Slack, email, OpsGenie, VictorOps, webhook |
| **Notification policies** | Route alerts to contact points based on label matchers; support silences and mutes |
| **SNS integration** | Native AWS SNS contact point; publish alerts to SNS topics for downstream fan-out |

### Network Access

| Mode | Description |
|---|---|
| **Public access** | Workspace reachable over the internet; access controlled by authentication |
| **VPC access** | Workspace endpoint placed inside a VPC; restrict data source connectivity to private resources; requires VPC endpoint configuration |

### Grafana API

The Grafana HTTP API is fully available in AMG workspaces. Use API keys (or Grafana service accounts) to:
- Provision dashboards as code (`POST /api/dashboards/db`)
- Manage data sources programmatically
- Create and update alert rules
- Import/export dashboard JSON models

### Workspace Versioning

AMG manages Grafana version upgrades. Each workspace specifies a supported Grafana version; AWS handles patching within that version. Major version upgrades require explicit workspace update.

### AMG vs Self-Hosted Grafana

| Dimension | Amazon Managed Grafana | Self-Hosted Grafana |
|---|---|---|
| **Operations** | Fully managed (patching, HA, backups) | Customer-managed infrastructure |
| **Authentication** | IAM Identity Center / SAML built-in | Configure auth plugins manually |
| **AWS data sources** | Pre-authorized via IAM roles | Requires manual credential management |
| **Scaling** | Automatic | Manual scaling of Grafana instances |
| **Cost model** | Per active user per month | Infrastructure + licensing (OSS free, Enterprise licensed) |
| **Plugins** | Managed plugin catalog; enterprise plugins included | Full plugin marketplace access |
| **Customization** | Limited to supported configuration options | Full control over Grafana config |

---

## Amazon Managed Service for Prometheus (AMP)

**Purpose**: Managed Prometheus-compatible monitoring service; ingest, store, and query Prometheus metrics at scale without operating Prometheus infrastructure.

### Core Concepts

| Concept | Description |
|---|---|
| **Workspace** | Isolated AMP environment with its own ingestion endpoint, query endpoint, and data store |
| **Remote write endpoint** | HTTPS endpoint for sending metrics: `https://aps-workspaces.<region>.amazonaws.com/workspaces/<workspace-id>/api/v1/remote_write` |
| **Query endpoint** | PromQL query API: `https://aps-workspaces.<region>.amazonaws.com/workspaces/<workspace-id>/api/v1/query` |
| **Workspace retention** | Default 150 days; fixed retention period managed by AWS |
| **SigV4 authentication** | All requests (remote write and query) authenticated with AWS SigV4 signature; no username/password |

### Metric Ingestion

| Source | Mechanism |
|---|---|
| **Amazon EKS** | AWS Distro for OpenTelemetry (ADOT) collector as DaemonSet or Deployment; or Prometheus agent via the Amazon EKS Managed Add-on for ADOT |
| **Amazon ECS** | ADOT sidecar container in task definition; scrape application metrics and remote_write to AMP |
| **Amazon EC2** | CloudWatch agent with Prometheus support; scrapes targets and forwards to AMP via remote_write |
| **Self-managed Prometheus** | Add `remote_write` block to `prometheus.yml` with SigV4 auth config |
| **Any OTLP source** | ADOT collector with prometheusremotewrite exporter |

### remote_write Configuration Example

```yaml
remote_write:
  - url: https://aps-workspaces.us-east-1.amazonaws.com/workspaces/<workspace-id>/api/v1/remote_write
    sigv4:
      region: us-east-1
    queue_config:
      max_samples_per_send: 1000
      max_shards: 200
      capacity: 2500
```

### Rule Groups

| Type | Description |
|---|---|
| **Recording rules** | Pre-compute expensive PromQL expressions on an interval; store results as new metrics for faster dashboard queries |
| **Alerting rules** | Evaluate PromQL expressions on an interval; fire alerts when the expression returns results |

Rule groups are stored as YAML and managed via the AMP API as named namespaces (not to be confused with Kubernetes namespaces).

### Alert Manager

AMP includes a built-in Alertmanager-compatible component for routing and deduplicating alerts fired by alerting rules.

| Feature | Description |
|---|---|
| **Routes** | Tree-based routing: match alerts by label selectors and send to specific receivers |
| **Receivers** | SNS topics (primary AWS-native receiver); also supports PagerDuty and generic webhooks |
| **Inhibition rules** | Suppress alerts when another specified alert is already firing; reduces noise during outages |
| **Grouping** | Batch related alerts together before notifying; configurable by label keys |
| **Repeat interval** | Re-notify if an alert remains firing after a configured duration |

Alert manager configuration is managed as a single YAML definition uploaded via the AMP API.

### PromQL Query API

AMP exposes the full Prometheus HTTP API under the workspace query endpoint:

| Endpoint | Description |
|---|---|
| `GET /api/v1/query` | Instant query at a single point in time |
| `GET /api/v1/query_range` | Range query returning a matrix result over a time range |
| `GET /api/v1/series` | Find series matching label selectors |
| `GET /api/v1/labels` | List all label names |
| `GET /api/v1/label/<name>/values` | List values for a specific label |
| `GET /api/v1/metadata` | Metric metadata |

All query requests require SigV4 signing. Tools like `awscurl` or the AWS SigV4 proxy can be used for ad-hoc queries.

### Grafana Data Source Configuration

To connect AMG (or self-hosted Grafana) to AMP:

1. Add a Prometheus data source in Grafana
2. Set the URL to the AMP query endpoint
3. Enable SigV4 authentication and specify the AWS region
4. Assign the Grafana workspace IAM role `AmazonPrometheusQueryAccess`

AMG natively supports AMP as a first-class data source with automatic SigV4 signing.

### IAM Permissions

| Action | IAM permission |
|---|---|
| Remote write (ingest) | `aps:RemoteWrite` |
| PromQL query | `aps:QueryMetrics`, `aps:GetLabels`, `aps:GetSeries`, `aps:GetMetricMetadata` |
| Rule groups management | `aps:CreateRuleGroupsNamespace`, `aps:PutRuleGroupsNamespace`, `aps:DeleteRuleGroupsNamespace` |
| Alert manager management | `aps:CreateAlertManagerDefinition`, `aps:PutAlertManagerDefinition`, `aps:DeleteAlertManagerDefinition` |
| Scraper management | `aps:CreateScraper`, `aps:DeleteScraper`, `aps:ListScrapers` |

### AMP vs Self-Managed Prometheus

| Dimension | Amazon Managed Service for Prometheus | Self-Managed Prometheus |
|---|---|---|
| **Operations** | Fully managed storage, HA, scaling | Customer manages servers, storage, compaction |
| **Retention** | Fixed 150 days | Configurable; manage storage capacity |
| **Scaling** | Automatic ingestion scaling | Manual sharding and federation |
| **Authentication** | IAM / SigV4 | Basic auth, TLS, or reverse proxy |
| **Alert routing** | Built-in Alertmanager-compatible | Deploy and manage Alertmanager separately |
| **Cost model** | Pay per metric sample ingested + stored + queried | Infrastructure cost |
| **Multi-tenancy** | Per-workspace isolation | Requires Cortex / Thanos / Mimir for multi-tenancy |
| **Long-term storage** | Managed 150-day retention | Requires Thanos / Cortex for extended retention |
