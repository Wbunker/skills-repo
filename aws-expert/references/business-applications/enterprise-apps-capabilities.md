# AWS Enterprise Apps — Capabilities Reference

For CLI commands, see [enterprise-apps-cli.md](enterprise-apps-cli.md).

## AWS AppFabric

**Purpose**: Rapidly connect SaaS applications to aggregate and normalize security and audit data for security operations (SIEM, SOAR) and productivity use cases, without writing custom integrations.

### Core Concepts

| Concept | Description |
|---|---|
| **App bundle** | A grouping of SaaS app connections (authorizations) with shared ingestion destinations |
| **App authorization** | A configured connection to a SaaS application using OAuth 2.0 or API key credentials |
| **Ingestion** | Data pipeline from an app authorization that pulls audit logs and activity data |
| **Ingestion destination** | Where ingested data is delivered: Amazon S3 or Amazon Kinesis Data Firehose |
| **OCSF normalization** | Open Cybersecurity Schema Framework; AppFabric normalizes all SaaS data to OCSF v1.0 before delivery |

### Supported SaaS Applications

AppFabric supports OAuth or API key integration with:

| Category | Apps |
|---|---|
| **Identity & Access** | Okta, Azure AD / Entra ID, JumpCloud, OneLogin, Ping Identity |
| **Collaboration** | Slack, Microsoft Teams, Zoom, Webex, Google Workspace, Box |
| **CRM & Support** | Salesforce, Zendesk, ServiceNow |
| **Productivity** | Dropbox, Asana, Monday.com, Smartsheet |
| **Security** | CrowdStrike Falcon, Trend Micro, Mimecast |
| **HR** | Workday |

### Data Flow Architecture

```
SaaS App API
    ↓
App Authorization (OAuth/API key credentials)
    ↓
Ingestion (polling/webhook pull)
    ↓  [optional Lambda transform]
OCSF Normalization
    ↓
Ingestion Destination
    ├── S3 (Parquet or JSON; queryable with Athena)
    └── Kinesis Firehose → OpenSearch / Splunk / SIEM
```

### OCSF Normalization

All ingested data is converted to OCSF (Open Cybersecurity Schema Framework) format:

| Feature | Description |
|---|---|
| **Schema version** | OCSF v1.0 |
| **Event classes** | Account Change, Authentication, Audit Activity, File Activity, Network Activity, etc. |
| **Vendor mapping** | AppFabric maps each SaaS app's native event fields to OCSF class attributes |
| **Format options** | JSON (raw OCSF) or Parquet (columnar; optimized for S3/Athena queries) |

### AppFabric for Productivity

A separate use case: aggregate user access and activity data across SaaS apps for IT/HR operations:

| Feature | Description |
|---|---|
| **User access report** | Cross-app view of which users have access to which SaaS tools |
| **App usage insights** | Identify active vs. inactive licensed users for cost optimization |
| **Offboarding automation** | Detect departed employees across apps and trigger access revocation |

### Ingestion Destinations

| Destination | Details |
|---|---|
| **Amazon S3** | Deliver OCSF-normalized logs to S3 bucket; choose JSON or Parquet format; set a prefix |
| **Amazon Kinesis Data Firehose** | Real-time delivery to Firehose → OpenSearch, Splunk, HTTP endpoint |

---

## AWS Supply Chain

**Purpose**: AI-powered cloud application for supply chain visibility, planning, and risk management, connecting data from existing ERP and SCM systems without replacing them.

### Core Concepts

| Concept | Description |
|---|---|
| **Supply Chain instance** | A deployed AWS Supply Chain environment tied to your account and region |
| **Data lake connector** | Ingests data from source systems (ERP, SCM, WMS) into the Supply Chain data lake |
| **Data lake** | Centralized S3-backed repository of supply chain data normalized to a common schema |
| **Insight** | An ML-generated alert or recommendation surfaced in the Supply Chain UI |
| **N-tier visibility** | End-to-end supply chain mapping beyond tier-1 suppliers |

### Data Lake Connector

Pulls data from enterprise systems into AWS Supply Chain:

| Source System | Connection Type |
|---|---|
| **SAP ECC / S4HANA** | SAP-certified connector; extracts purchase orders, inventory, master data |
| **Oracle E-Business Suite** | JDBC-based connector |
| **Custom / Generic** | Flat file upload (CSV/Parquet) to S3; mapped to Supply Chain schema |
| **API ingest** | REST API for pushing data programmatically |

Data entities ingested: purchase orders, sales orders, inventory positions, demand forecasts, shipment statuses, supplier master data, product master data, bills of materials.

### ML-Powered Insights

| Insight Type | Description |
|---|---|
| **Supply planning** | Identifies supply shortages and recommends order adjustments to meet demand |
| **Demand planning** | Statistical and ML-based demand forecasting with configurable horizon |
| **Inventory visibility** | Real-time inventory levels across warehouses, DCs, and in-transit |
| **Inventory health** | Identifies excess, obsolete, and at-risk inventory |
| **Lead time variability** | Tracks supplier lead time trends; flags abnormal delays |
| **Risk alerts** | Proactive alerts on supplier risks, weather disruptions, geopolitical events |

### N-Tier Supply Chain Visibility

| Feature | Description |
|---|---|
| **Supplier network mapping** | Map relationships between buyers, tier-1, tier-2, and deeper suppliers |
| **Sub-tier risk** | Surface risk from suppliers beyond tier-1 that are not directly connected |
| **Network graph** | Visual representation of supply chain network topology |
| **Collaboration portal** | Suppliers can log in to share inventory/capacity data without ERP integration |

### Sustainability Insights

| Feature | Description |
|---|---|
| **Carbon footprint tracking** | Estimate Scope 3 emissions from procurement and logistics |
| **Supplier sustainability scores** | Aggregate ESG metrics from connected suppliers |
| **Mode of transport analysis** | Compare emissions across transportation modes (air, ocean, road) |

### Supply Chain Network

| Feature | Description |
|---|---|
| **Network configuration** | Define nodes (factories, DCs, ports) and lanes (transport routes) |
| **What-if analysis** | Model network changes and evaluate impact on cost, time, and resilience |
| **Optimization recommendations** | ML suggestions for network consolidation or new distribution points |
