# Big Data Architectures on the Cloud
## Chapter 2: Modern Data Warehouse, Data Lakehouse, Data Mesh

---

## Cloud Data Lake Architecture Fundamentals

Before choosing an architecture pattern, understand the building blocks that all patterns share.

### A Word on Variety of Data

| Data Type | Examples | Storage Format |
|-----------|----------|---------------|
| **Structured** | Database tables, CSVs, transactional records | Parquet, ORC, Delta, Iceberg |
| **Semi-structured** | JSON logs, XML, Avro, sensor payloads | JSON, Avro, Parquet |
| **Unstructured** | Images, video, audio, PDFs, text documents | Native (JPEG, MP4, PDF) |

A data lake's defining advantage is storing all three types in the same place.

### Core Components

```
┌──────────────────────────────────────────────────────────────────┐
│                   CLOUD DATA LAKE COMPONENTS                      │
│                                                                   │
│  SOURCES          INGESTION          STORAGE          ANALYTICS  │
│  ───────          ─────────          ───────          ─────────  │
│  Databases   ──►  Batch ETL     ──►  Object Store ──► SQL/BI    │
│  Apps        ──►  CDC/streaming ──►  (S3/ADLS/GCS)──► Spark    │
│  APIs        ──►  File transfer ──►  +Table format──► ML        │
│  IoT/streams ──►  Kafka/Kinesis ──►  (Iceberg/    ──► Streaming │
│  SaaS        ──►  Data pipeline ──►   Delta/Hudi)  ──► Ad-hoc   │
└──────────────────────────────────────────────────────────────────┘
```

**Cloud Data Lake Storage**: Object stores (S3, ADLS Gen2, GCS) provide cheap, durable, schema-agnostic storage. They are the foundation of all three architecture patterns.

**Big Data Analytics Engines**: Spark, Presto/Trino, Flink, and cloud-native engines (Athena, BigQuery, Synapse) run compute against object storage without requiring data to be loaded into proprietary formats.

**Cloud Data Warehouses**: Snowflake, BigQuery, Redshift, and Azure Synapse provide structured query performance on top of — or alongside — the data lake.

---

## Architecture Pattern 1: Modern Data Warehouse

### What It Is

The Modern Data Warehouse combines a cloud data lake (for raw/staging data) with a cloud data warehouse (for serving BI queries). The data lake acts as a staging and archive layer; the warehouse is the serving layer.

### Reference Architecture

```
Sources → [Ingestion] → Data Lake (S3/ADLS/GCS)
                              │
                         [ETL/Transform]
                              │
                              ▼
                    Cloud Data Warehouse
                  (Snowflake / BigQuery /
                   Redshift / Synapse)
                              │
                         [SQL / BI]
                              │
                    Dashboards & Reports
                    (Tableau, Power BI, Looker)
```

### Sample Use Case (Klodars Corporation)

Klodars uses the Modern Data Warehouse pattern for its sales analytics:
- Raw Salesforce data lands in S3
- dbt transforms clean it and load them into Snowflake
- Tableau dashboards query Snowflake for weekly sales reports

### Benefits

| Benefit | Description |
|---------|-------------|
| **Familiar SQL interface** | Business analysts use existing SQL skills |
| **High query performance** | Warehouse optimizes for BI query patterns |
| **Separation of raw and curated** | Lake retains raw history; warehouse serves fast queries |
| **Mature tooling** | Snowflake, BigQuery, Redshift have strong ecosystems |

### Challenges

| Challenge | Description |
|-----------|-------------|
| **Data duplication** | Data lives in both lake and warehouse — storage and sync cost |
| **ETL complexity** | Pipeline from lake to warehouse must be maintained |
| **Limited ML support** | ML training happens on lake, not warehouse; two separate ecosystems |
| **Cost of warehouse** | Cloud DW compute is expensive for exploratory queries |
| **Schema rigidity in warehouse** | Semi-structured and unstructured data still can't live in the warehouse |

### Best For
- Organizations with strong BI/reporting as the primary use case
- Teams with existing SQL skills and BI tooling
- Workloads that are primarily structured and relational
- When warehouse performance requirements are non-negotiable

---

## Architecture Pattern 2: Data Lakehouse

### What It Is

The Data Lakehouse collapses the lake and warehouse into a single system. Open table formats (Apache Iceberg, Delta Lake, Apache Hudi) add ACID transactions, schema enforcement, and query optimization directly on top of object storage — eliminating the need for a separate data warehouse for most workloads.

### Reference Architecture

```
Sources → [Ingestion] → Object Storage (S3/ADLS/GCS)
                              │
                    ┌─────────┴──────────┐
                    │   Open Table Format │
                    │  (Iceberg / Delta / │
                    │       Hudi)         │
                    │  - ACID guarantees  │
                    │  - Schema evolution │
                    │  - Time travel      │
                    │  - Partition pruning│
                    └─────────┬──────────┘
                              │
               ┌──────────────┼──────────────┐
               ▼              ▼              ▼
           Spark/EMR      Athena/Trino    Databricks
           (batch/ML)     (SQL/BI)       (unified)
               │              │
           ML Models      BI Dashboards
```

### Reference Architecture for Data Lakehouse

| Layer | Technology |
|-------|-----------|
| Storage | S3, ADLS Gen2, GCS |
| Table format | Apache Iceberg, Delta Lake, or Apache Hudi |
| Compute (batch) | Apache Spark, AWS EMR, Databricks |
| Compute (SQL) | Amazon Athena, Trino, Google BigQuery (via external tables) |
| Compute (streaming) | Apache Flink, Spark Structured Streaming |
| Orchestration | Apache Airflow, AWS Step Functions, Dagster, dbt |
| Catalog | AWS Glue Catalog, Hive Metastore, Apache Polaris, Unity Catalog |

### Sample Use Case (Klodars)

Klodars adopts Data Lakehouse for its ML platform:
- All data (structured + semi-structured) stored in S3 with Iceberg table format
- Data scientists run Spark ML jobs directly on the same tables that BI analysts query with Athena
- ACID guarantees prevent analysts from reading partial pipeline results
- Time travel allows reproducing ML experiment results from 6 months ago

### Benefits

| Benefit | Description |
|---------|-------------|
| **Single storage layer** | No data duplication between lake and warehouse |
| **ACID on object storage** | Reliable writes, no partial reads, concurrent access |
| **Schema evolution** | Add/rename/drop columns without rewriting data |
| **Time travel** | Query historical snapshots for debugging and auditing |
| **Unified ML + BI** | Same data serves ML training and BI queries |
| **Cost efficiency** | Object storage pricing; no separate warehouse compute |
| **Multi-engine** | Different engines can read the same data simultaneously |

### Challenges

| Challenge | Description |
|-----------|-------------|
| **Newer patterns** | Less mature tooling compared to traditional DW in some areas |
| **Table format lock-in risk** | Choosing between Iceberg, Delta, Hudi has long-term implications |
| **Performance tuning** | Requires careful partitioning, compaction, and file sizing |
| **Governance complexity** | Access control on object storage is more complex than a DW |

### Unstructured Data

Even in a lakehouse, unstructured data (images, video, text) lives alongside structured tables in the same object store — just without a table format wrapper. This is a key advantage over the data warehouse pattern.

### Best For
- Organizations running both ML and BI workloads on the same data
- Cost-conscious architectures that want to minimize compute costs
- Teams with polyglot data (structured + semi-structured + unstructured)
- Greenfield architectures starting fresh

---

## Architecture Pattern 3: Data Mesh

### What It Is

Data Mesh is not a technology — it is an organizational and architectural paradigm. It decentralizes data ownership to domain teams, who treat their data as products published for consumption by other domains.

**Core principles (Zhamak Dehghani):**
1. **Domain ownership** — each domain team owns and operates its data products
2. **Data as a product** — data is designed for discoverability, usability, and SLA adherence
3. **Self-serve data platform** — central platform team provides tooling; domains use it without bottlenecks
4. **Federated governance** — global standards (security, privacy, interoperability) enforced centrally; local decisions delegated to domains

### Reference Architecture

```
┌────────────────────────────────────────────────────────────┐
│                    SELF-SERVE PLATFORM                      │
│   Storage infra · Catalog · Governance · CI/CD · Access    │
└────────────────────────────────────────────────────────────┘
          │                 │                  │
          ▼                 ▼                  ▼
┌──────────────┐   ┌──────────────┐   ┌──────────────┐
│   SALES      │   │   PRODUCT    │   │   FINANCE    │
│   DOMAIN     │   │   DOMAIN     │   │   DOMAIN     │
│              │   │              │   │              │
│  Owns:       │   │  Owns:       │   │  Owns:       │
│  - Orders    │   │  - Catalog   │   │  - Revenue   │
│  - Pipeline  │   │  - Inventory │   │  - Costs     │
│  - SLAs      │   │  - Pricing   │   │  - Budget    │
│              │   │              │   │              │
│  Publishes:  │   │  Publishes:  │   │  Publishes:  │
│  customer_   │   │  product_    │   │  revenue_    │
│  orders_v1   │   │  catalog_v2  │   │  monthly_v1  │
└──────┬───────┘   └──────┬───────┘   └──────┬───────┘
       │                  │                   │
       └──────────────────┼───────────────────┘
                          ▼
                   Data Marketplace /
                   Catalog (discovery)
```

### Sample Use Case (Klodars)

Klodars adopts Data Mesh when it reaches 5 distinct business domains, each with its own team:
- Sales team publishes `customer_orders_v1` as a data product with documented SLAs
- ML team subscribes to that product for training recommendation models
- Finance team publishes `revenue_monthly_v1` certified by the CFO
- Central platform team maintains the catalog, IAM infrastructure, and governance standards

### Benefits

| Benefit | Description |
|---------|-------------|
| **Eliminates central team bottleneck** | Domain teams self-serve without waiting for central data engineering |
| **Domain expertise in data products** | Teams that know the data best produce and maintain it |
| **Scalable** | Adding domains doesn't require central team to grow proportionally |
| **Product mindset** | Data quality and usability treated as a product responsibility |

### Challenges

| Challenge | Description |
|-----------|-------------|
| **Organizational maturity required** | Domains need data engineering capability; not all do |
| **Platform investment** | Self-serve platform is a major upfront engineering investment |
| **Federated governance is hard** | Consistent security and compliance standards across autonomous teams |
| **Cross-domain joins** | Data products may need to be joined — requires careful design |
| **Coordination overhead** | Domain teams must agree on shared standards (schemas, SLAs) |

### Best For
- Large organizations (typically 500+ people, multiple distinct domains)
- Organizations where central data team is a chronic bottleneck
- Mature engineering cultures comfortable with platform engineering
- When data ownership and accountability across domains is the primary problem

---

## Choosing the Right Architecture

### Decision Criteria

```
What is your primary pain point?
├── "BI queries are slow, data is structured, analysts want SQL"
│   └── Modern Data Warehouse
│
├── "We need ML + BI on same data, cost is a concern"
│   └── Data Lakehouse
│
├── "Central data team can't keep up, many domain teams"
│   └── Data Mesh
│
└── "We have some of all these problems"
    └── Hybrid approach
```

### Know Your Customers

Gopalan emphasizes understanding data consumers before choosing an architecture:

| Consumer Type | Needs | Architecture Fit |
|---------------|-------|-----------------|
| **BI Analysts** | SQL, fast queries, governed tables | Modern DW or Lakehouse |
| **Data Scientists** | Raw data, ML frameworks, Python/Scala | Lakehouse |
| **Business Users** | Dashboards, no code | Modern DW |
| **Application Developers** | APIs, low-latency reads | Lakehouse with serving layer |
| **Domain Teams** | Ownership, autonomy | Data Mesh |

### Know Your Business Drivers

| Business Driver | Architecture Implication |
|----------------|-------------------------|
| **Cost reduction** | Lakehouse (avoid duplicate DW storage) |
| **Speed to insight** | Modern DW (mature BI tooling) |
| **ML/AI capability** | Lakehouse (unified data, Spark integration) |
| **Compliance/governance** | All patterns need governance; DW is most mature |
| **Data democratization** | Data Mesh (domain autonomy) |
| **Real-time analytics** | Lakehouse with Hudi/Iceberg for CDC |

### Hybrid Approaches

Most large organizations use hybrid patterns:

- **Modern DW + Lakehouse**: Use lakehouse for ML/raw data; DW for curated BI serving
- **Data Mesh + Lakehouse**: Each domain operates a lakehouse; mesh provides the organizational model
- **Incremental adoption**: Start with Modern DW; add lakehouse capabilities over time as table formats mature

The key insight: **these patterns are not mutually exclusive**. The architecture evolves as business needs and technical capabilities mature.
