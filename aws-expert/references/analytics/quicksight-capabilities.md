# AWS QuickSight — Capabilities Reference
For CLI commands, see [quicksight-cli.md](quicksight-cli.md).

## Amazon QuickSight

**Purpose**: Scalable, serverless, cloud-native business intelligence service with ML-powered insights, interactive dashboards, and natural language querying.

### Core Concepts

| Concept | Description |
|---|---|
| **Dataset** | Connection to a data source with optional field-level transformations and calculated fields |
| **SPICE** | Super-fast, Parallel, In-memory Calculation Engine; cached dataset for fast queries |
| **Analysis** | Authoring environment where you build visuals and insights |
| **Dashboard** | Published, read-only view of an analysis shared with readers |
| **Visual** | A single chart, table, or KPI in an analysis or dashboard |
| **Sheet** | A page within an analysis or dashboard containing multiple visuals |

### Dataset Modes

| Mode | Description |
|---|---|
| **SPICE** | Data imported and cached in QuickSight's in-memory engine; fast queries; refresh on schedule |
| **Direct query** | Queries run live against the data source; always fresh; latency depends on source |

### ML Insights

| Feature | Description |
|---|---|
| **Anomaly detection** | ML-based detection of outliers in metrics over time; powered by Random Cut Forest |
| **Forecasting** | Time-series forecasting using ML; add forecast bands to line charts |
| **Auto-narratives** | Automatically generated natural language summaries of key trends in a visual |
| **Suggested insights** | QuickSight proactively surfaces interesting patterns in your data |

### Security

| Feature | Description |
|---|---|
| **Row-level security (RLS)** | Restrict rows visible per user/group using a dataset rule |
| **Column-level security (CLS)** | Restrict which columns are visible per user/group |
| **VPC connectivity** | Connect to data sources in private VPCs via ENI in your VPC |
| **IAM Identity Center** | SSO integration for enterprise user management |
| **Namespace isolation** | Multi-tenant deployments with isolated namespaces per customer/tenant |

### Embedding

| Type | Description |
|---|---|
| **1-click embedding** | Simple iframe embedding for dashboards with minimal setup |
| **Anonymous embedding** | Embed dashboards without requiring users to have QuickSight accounts |
| **Registered user embedding** | Embed for authenticated users mapped to QuickSight registered users |
| **Q embedding** | Embed the QuickSight Q natural language query bar in your application |
| **Generative BI embedding** | Embed AI-powered visual authoring capabilities |

### Pricing Tiers

| Tier | Description |
|---|---|
| **Standard** | Individual authors and readers; SPICE and dashboards; per-user monthly pricing |
| **Enterprise** | Adds RLS, CLS, encryption at rest, VPC connectivity, Active Directory integration, paginated reports |
| **Enterprise + Q** | Adds Q (natural language querying) on top of Enterprise |

### Data Sources

QuickSight supports connections to Amazon Redshift, Amazon RDS, Amazon Aurora, Amazon Athena, Amazon S3, Amazon OpenSearch Service, Salesforce, Snowflake, Teradata, SQL Server, MySQL, PostgreSQL, and many other sources via JDBC/ODBC.
