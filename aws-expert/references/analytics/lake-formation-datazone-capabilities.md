# AWS Lake Formation & DataZone — Capabilities Reference
For CLI commands, see [lake-formation-datazone-cli.md](lake-formation-datazone-cli.md).

## AWS Lake Formation

**Purpose**: Centrally govern, secure, and share data stored in Amazon S3 and AWS Glue Data Catalog with fine-grained, database-style permissions for all integrated analytics services.

### Core Concepts

| Concept | Description |
|---|---|
| **Data lake administrator** | IAM principal with elevated Lake Formation privileges; manages permissions for others |
| **Registered location** | S3 path registered with Lake Formation; Lake Formation manages access via a service role |
| **Database/table permissions** | Grant SELECT, INSERT, DROP, ALTER, etc. on catalog resources to IAM principals |
| **Column permissions** | Grant SELECT on specific columns only; exclude sensitive columns from grants |
| **Row filter** | Data filter that restricts rows visible to a principal based on column conditions |
| **Cell filter** | Combines row filter and column restriction into a single grant |

### LF-Tags (Attribute-Based Access Control)

Define custom tags (key-value pairs) and attach them to databases, tables, or columns. Grant permissions via tag expressions instead of individual resource ARNs. Manages access to thousands of resources with a handful of tag-based policies.

```
LF-Tag: Sensitivity = PII
LF-Tag: Department = Finance

Grant: principal=analyst-role, tag=Department:Finance, permissions=SELECT
```

### Governed Tables

Tables registered as "governed" support ACID transactions — multi-table, multi-partition atomic commits and rollbacks. Use `StartTransaction`, `CommitTransaction`, `AbortTransaction` APIs. Requires Lake Formation storage optimizations.

### Blueprints

Pre-built ingestion workflows that automate the creation of Glue crawlers, ETL jobs, and workflows for common patterns (incremental DB import, log file ingestion). Generates a Glue workflow from a template.

### Cross-Account Data Sharing

Share Data Catalog databases and tables (and their underlying S3 data) across AWS accounts using Lake Formation permissions plus AWS RAM (Resource Access Manager). Consumers query data using Athena, Redshift Spectrum, or EMR without copying data.

### Service Integration

| Service | Integration |
|---|---|
| **Amazon Athena** | Enforces Lake Formation column/row/cell permissions at query time |
| **Amazon Redshift Spectrum** | Enforces LF permissions on external tables |
| **Amazon EMR** | Enforces LF permissions via EMR runtime role; requires Glue catalog |
| **AWS Glue ETL** | Jobs run as IAM role; LF permissions determine accessible tables |
| **Amazon QuickSight** | Dataset-level enforcement via LF-integrated data sources |

---

## AWS DataZone

**Purpose**: Data management service that enables organizations to catalog, discover, share, and govern data across AWS, on-premises, and third-party sources through a business-friendly data portal.

### Core Concepts

| Concept | Description |
|---|---|
| **Domain** | Top-level organizational unit; contains all DataZone resources for a business unit or org |
| **Data portal** | Browser-based portal where producers publish and consumers discover data assets |
| **Business data catalog** | Searchable catalog of data assets with business metadata (descriptions, glossary terms) |
| **Data project** | Group within a domain; producers and consumers belong to projects; has its own IAM role |
| **Asset** | A cataloged data resource (Glue table, Redshift table, S3 dataset, etc.) |
| **Subscription** | Request from a consumer project to access an asset; requires approval from producer |
| **Business glossary** | Controlled vocabulary of business terms linked to catalog assets |
| **Environment** | AWS infrastructure provisioned for a project (Athena workgroup, Redshift cluster, etc.) |

### Data Flow

1. Producer publishes an asset to the domain catalog
2. Consumer discovers the asset via the data portal
3. Consumer submits a subscription request
4. Producer (or automated policy) approves or rejects
5. DataZone provisions access (Lake Formation grant, Redshift grant) automatically
6. Consumer queries data using Athena, Redshift, or other tools in their environment

### Key Integrations

| Integration | Role |
|---|---|
| **AWS Glue Data Catalog** | Source for table/database assets; metadata imported into DataZone catalog |
| **Amazon Redshift** | Source for table and view assets |
| **AWS Lake Formation** | Access fulfillment for S3/Glue assets (LF grant on approval) |
| **Amazon Athena** | Consumer query tool in DataZone environments |
| **Amazon EventBridge** | Custom integrations and workflow automation |
