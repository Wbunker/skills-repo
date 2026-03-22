# Microsoft Purview & Power BI — Capabilities

## Microsoft Purview Overview

Microsoft Purview is the unified data governance, risk, and compliance platform for Azure and Microsoft 365. It consolidates Azure Purview (data catalog and governance) with Microsoft 365 Compliance Center capabilities (sensitivity labels, DLP, compliance management).

**Access**: [purview.microsoft.com](https://purview.microsoft.com)

---

## Microsoft Purview: Data Governance

### Data Map

The foundational layer — a managed graph of all your data assets across sources:

- **Automated scanning**: Register and scan data sources to discover assets automatically.
- **Auto-classification**: Apply 200+ built-in classifiers (PII, PHI, financial data, geography) plus custom regex/keyword classifiers.
- **Schema capture**: Tables, columns, data types captured with statistical metadata.
- **Lineage**: End-to-end data lineage — source → transformation → report.

### Supported Data Sources (100+)

| Category | Sources |
|---|---|
| **Azure** | ADLS Gen2, Blob Storage, Azure SQL, Synapse, Databricks, Azure ML, Cosmos DB, Data Factory, Event Hubs |
| **Multi-cloud** | Amazon S3, GCS, Redshift, BigQuery, Snowflake |
| **On-premises** | SQL Server, Oracle, SAP ECC/S4, Teradata, Hive |
| **SaaS** | Salesforce, Power BI, Looker, Tableau |
| **File formats** | Parquet, Delta, CSV, JSON, ORC, Avro |

### Scanning

- **Managed IR** (Azure) or **Self-hosted IR** for on-premises/private network sources.
- **Scan rule sets**: Define which classifiers to apply and file types to scan.
- **Incremental scanning**: Re-scan only changed assets.
- **Scheduling**: One-time or recurring scans.

### Data Catalog

Search and browse all discovered data assets:

- **Unified search**: Search by asset name, classification, schema, or business glossary term.
- **Asset details**: Schema, lineage, classifications, sensitivity labels, contacts, certification status.
- **Business glossary**: Define business terms and map to technical assets.
  - Hierarchical term structure (domain → category → term).
  - Assign term stewards and experts.
  - Map terms to columns, tables, and reports.
- **Collections**: Hierarchical namespace for organizing assets and applying access control.
- **Asset certification**: Mark assets as verified/certified by data stewards.
- **Contacts**: Assign data owners and experts to assets.

### Lineage

Automatic lineage captured from integrated sources:

| Source | Lineage Type |
|---|---|
| Azure Data Factory | Pipeline-level lineage (source → sink per activity) |
| Azure Synapse Analytics | Pipeline + Spark lineage |
| Azure Databricks | Table-level lineage via Unity Catalog integration |
| Power BI | Dataset → Report lineage |
| Azure ML | Training data → Model lineage |

```
[SQL Database: dbo.Sales]
    ↓ (ADF Copy Activity)
[ADLS Gen2: /processed/sales.parquet]
    ↓ (Synapse Spark job)
[Synapse: dbo.SalesAgg]
    ↓ (Power BI Dataset)
[Power BI Report: Sales Dashboard]
```

### Data Policy

Author and enforce access policies from Purview directly to data sources — without writing SQL GRANTs:

| Policy Type | Description |
|---|---|
| **Data Owner policies** | Grant Read/Modify access to data assets |
| **DevOps policies** | Grant access for engineering/ops personas |
| **Self-service policies** | Allow data consumers to request access |

Supported policy enforcement targets: ADLS Gen2, Azure SQL, Azure Arc-enabled SQL Server, Synapse workspaces.

### Data Sharing

Share data assets with other organizations or tenants:

- **Snapshot-based sharing**: Copy data to recipient's storage on share.
- **In-place sharing (ADX)**: Recipient queries source data without copying.
- Recipient uses Purview portal to receive and access shared data.
- No data duplication for in-place — always fresh.

---

## Microsoft Purview: Information Protection (from M365)

### Sensitivity Labels

Classify and protect content across Microsoft 365 and Azure:

- Labels: Public, General, Confidential, Highly Confidential (customizable).
- Applied to: files, emails, Teams messages, Power BI reports, Azure Purview assets.
- **Automatic labeling**: Rules classify content automatically based on sensitive information types.
- **Encryption**: Apply rights management (IRM) encryption at label assignment.
- **Visual markings**: Headers, footers, watermarks on labeled documents.

### Data Loss Prevention (DLP)

Prevent sensitive data from leaving organization:

- Policies: Block/audit/warn when sensitive data detected in Exchange, Teams, SharePoint, OneDrive, Endpoints.
- Sensitive information types: 300+ built-in (credit cards, SSN, IBAN, medical terms) + custom regex.
- **Endpoint DLP**: Monitor data movement on Windows devices.

---

## Microsoft Purview: Compliance

### Compliance Manager

Regulatory compliance assessment and tracking:

- Pre-built assessments: GDPR, ISO 27001, SOC 2, HIPAA, NIST, PCI DSS, FedRAMP.
- Compliance score: Aggregate score based on implemented controls.
- Improvement actions: Actionable recommendations with implementation guidance.
- Multi-cloud support: AWS and GCP assessments.

### Audit Logs

Unified audit log across Microsoft 365 and Azure:

- Retention: 90 days (standard) or 1 year (Microsoft 365 E5 or add-on license).
- 10-year retention with audit premium add-on.
- Query via Compliance portal, PowerShell, or Management Activity API.

---

## Power BI Embedded

Embed Power BI reports and dashboards in custom applications.

### Embedding Models

| Model | License | Description |
|---|---|---|
| **For your customers** | A-SKU (Azure) | Embed without Power BI license per user — app-owns-data |
| **For your organization** | P or E SKU | Embed for internal users with Power BI license — user-owns-data |

### A-SKU (Azure Embedding)

- Provision **Power BI Embedded** resource in Azure (A1–A8 SKUs).
- Your app authenticates to Power BI service with a service principal.
- End users see reports without needing Power BI accounts or licenses.
- Scale A-SKU capacity based on concurrent users.
- **Pause/resume**: Stop charges when not in use (unlike P-SKU which is always-on).

```javascript
// React embedding with Power BI JavaScript SDK
import { PowerBIEmbed } from 'powerbi-client-react';
import { models } from 'powerbi-client';

<PowerBIEmbed
  embedConfig={{
    type: 'report',
    id: reportId,
    embedUrl: embedUrl,     // from Power BI REST API
    accessToken: token,     // generated by backend using SP credentials
    tokenType: models.TokenType.Embed,
    settings: {
      panes: { filters: { visible: false } },
      background: models.BackgroundType.Transparent
    }
  }}
/>
```

### Embedding Flow

```
1. Backend: Service principal authenticates to Power BI service
   POST https://login.microsoftonline.com/{tenant}/oauth2/token

2. Backend: Get embed token for report
   POST https://api.powerbi.com/v1.0/myorg/groups/{groupId}/reports/{reportId}/GenerateToken

3. Frontend: Embed using Power BI JavaScript SDK
   powerbi.embed(container, embedConfiguration)
```

---

## Azure Analysis Services

Enterprise semantic model server — provides a tabular data model (SSAS Tabular) as a service.

> **Important**: Microsoft recommends **Power BI Premium** for new deployments of semantic models. Azure Analysis Services is in maintenance mode — no new features, supported for existing customers.

### Key Features

- Tabular model server with DAX query language.
- Connects to: Azure SQL, Synapse, ADLS, SQL Server, Excel files.
- DirectQuery and Import storage modes.
- Row-level security (RLS) at model layer.
- Processing: full/incremental refresh of imported data.
- Client tools: Excel, Power BI Desktop, SSMS, Tabular Editor.

### SKUs

| Tier | Description |
|---|---|
| B1 (Basic) | Dev/test, no HA |
| S0–S9 (Standard) | Production workloads, scale up/out |
| D1 (Developer) | Single-server development |

- **Pause/resume**: Scale to zero when not needed.
- **Scale out**: Up to 7 query replicas for read scaling.
