# Decision Framework for Your Architecture
## Chapter 7: Putting It All Together

---

## The Decision Framework

Chapter 7 synthesizes all prior concepts into a structured framework for making architecture decisions at different points in the data lake journey. The framework has three elements:

1. **Know your customers** — who consumes this data and what do they need?
2. **Know your business drivers** — what outcomes must the data platform deliver?
3. **Consider growth and future scenarios** — what must the architecture handle in 2–3 years?

This is not a one-time exercise — these questions must be revisited as the business and data landscape evolve.

---

## Know Your Customers

### Data Consumer Profiles

| Consumer Type | Primary Need | Latency Tolerance | Technical Skill | Architecture Implication |
|---------------|-------------|------------------|-----------------|--------------------------|
| **Business Analyst** | SQL, governed tables, BI tools | Hours to days | Medium (SQL) | Curated zone with Parquet; DW or Lakehouse |
| **Data Scientist** | Raw + cleaned data, Python/R, ML frameworks | Hours acceptable | High | Staging zone access; Spark/notebook environment |
| **ML Engineer** | Feature stores, model training data, versioned datasets | Hours to days | High | Lakehouse with reproducibility (time travel) |
| **Application Developer** | Low-latency API reads, structured data | Sub-second | Medium | Serving layer on top of lake (DynamoDB, Redis, Postgres) |
| **Data Engineer** | All zones, pipeline control, schema management | N/A (builds it) | High | Full access; DevOps tooling |
| **Executive / Business User** | Dashboard KPIs, no-code | Real-time to daily | Low | Pre-built dashboards; curated zone only |
| **Regulatory / Audit** | Immutable audit trails, lineage | Batch | Low-medium | Raw zone access; lineage metadata |

### Customer Discovery Questions

Before finalizing architecture:
- What tools are they using today, and what are they satisfied/frustrated with?
- What questions can't they answer with current data, and why?
- How frequently do they need data refreshed?
- Do they write SQL, Python, or neither?
- What data quality expectations do they have?
- Who do they call when something breaks?

---

## Know Your Business Drivers

### Business Driver → Architecture Mapping

| Business Driver | Primary Architecture Need | Key Design Decision |
|----------------|--------------------------|---------------------|
| **Reduce analytics costs** | Consolidate from expensive DW to lakehouse | Open table format; Athena/Trino vs. Snowflake |
| **Enable ML/AI at scale** | Unified data for feature engineering + training | Lakehouse with Spark; feature store integration |
| **Real-time analytics** | Near-real-time ingestion and query | Streaming pipeline; Hudi/Iceberg; Flink |
| **Regulatory compliance** | Immutable audit trail, data lineage, PII control | Raw zone retention; column masking; lineage tracking |
| **Data democratization** | Self-service analytics for non-engineers | Strong catalog; curated zone governance; BI-friendly serving |
| **Speed to insight** | Reduce time from question to answer | Pre-built curated data products; BI tool integration |
| **Data monetization** | Share data externally as product | Data sharing (Delta Sharing, Iceberg sharing); API layer |
| **Domain team autonomy** | Reduce central team bottleneck | Data Mesh organizational pattern |

### Prioritization Matrix

Not all drivers are equally important. Map drivers to urgency and impact:

```
High Impact │ Enable ML     │ Reduce costs  │
            │ (strategic)   │ (immediate)   │
────────────┼───────────────┼───────────────┤
Low Impact  │ Real-time     │ Data sharing  │
            │ (future)      │ (nice to have)│
            │ Low Urgency   │ High Urgency  │
```

Design the architecture to serve **high-urgency, high-impact drivers first** while not closing doors on future drivers.

---

## Consider Growth and Future Scenarios

### Planning Horizons

| Horizon | Questions to Ask |
|---------|-----------------|
| **6 months** | What data sources must we onboard? What use cases go live? |
| **1 year** | How many teams will use the platform? What query SLAs are committed? |
| **3 years** | Will we expand to new clouds? New regulatory requirements? ML at scale? |

### Growth Scenarios to Design For

**Data volume growth:**
- At what volume do current partitioning schemes break? (Validate at 10× current scale)
- Are compaction jobs sized for 10× file count?
- Will catalog listing times remain acceptable at 100× table count?

**Team growth:**
- Can governance scale from 3 data stewards to 30 without redesign?
- Is access control model manageable when user count triples?
- Does the catalog support self-service onboarding?

**Use case expansion:**
- If ML becomes a priority, does the architecture support Spark at scale?
- If streaming becomes required, does the table format handle frequent upserts?
- If we go multi-cloud, does the catalog/format work across providers?

### Design for Extensibility Without Over-Engineering

Gopalan's principle: **solve for today's requirements + the next two known growth inflection points, but no further.**

Common over-engineering traps:
- Building a Data Mesh when there's one data team and two consumers
- Implementing all three open table formats "to keep options open"
- Building real-time pipelines for data that only needs daily refresh
- Over-partitioning for query patterns that don't yet exist

---

## Architecture Selection Framework

### The Decision Process

```
Step 1: Document your top 3 consumer types and their primary needs
        └── Who uses this data and how?

Step 2: List your top 3 business drivers
        └── What outcomes must the data platform deliver?

Step 3: Identify your most critical constraint
        └── Cost? Time? Team capability? Regulatory?

Step 4: Map to architecture pattern
        └── Modern DW / Lakehouse / Data Mesh (or hybrid)

Step 5: Choose open table format (if lakehouse path)
        └── Iceberg / Delta / Hudi based on workload and ecosystem

Step 6: Define data lake zones and governance model
        └── 3-zone or 4-zone; centralized or federated governance

Step 7: Validate against 3-year growth scenarios
        └── Does this architecture hold at 10× scale?
```

### Architecture Comparison for Decision-Making

| Criterion | Modern Data Warehouse | Data Lakehouse | Data Mesh |
|-----------|----------------------|----------------|-----------|
| **SQL BI performance** | Excellent | Good | Depends on domain |
| **ML/AI support** | Limited | Excellent | Depends on domain |
| **Storage cost** | High (DW + lake duplication) | Low (single store) | Medium |
| **Time to first value** | Fast (DW is mature) | Moderate | Slow (platform investment) |
| **Operational complexity** | Low-Medium | Medium | High |
| **Org maturity required** | Low | Medium | High |
| **Governance maturity required** | Medium | Medium | High (federated) |
| **Best team size** | Any | Any | Large (multiple domains) |
| **Real-time support** | Limited | Good | Depends on domain |
| **Unstructured data** | No | Yes | Yes |

---

## Cloud Provider Considerations

### AWS

| Component | AWS Option | Notes |
|-----------|-----------|-------|
| Object storage | Amazon S3 | Industry reference; excellent tooling |
| Table format | Apache Iceberg (preferred by AWS) | Native Glue, Athena, EMR support |
| Catalog | AWS Glue Data Catalog | Integrates across all AWS analytics services |
| SQL engine | Amazon Athena (serverless), EMR Trino | Athena = pay-per-scan; EMR = persistent cluster |
| Batch compute | AWS EMR (Spark), Glue ETL | EMR more flexible; Glue serverless simpler |
| Streaming | Amazon Kinesis, MSK (Kafka) | Kinesis = managed; MSK = Kafka API |
| ML | Amazon SageMaker | Full ML lifecycle; integrates with S3 |
| Governance | AWS Lake Formation | Column masking; row-level filters; sharing |

### Azure

| Component | Azure Option | Notes |
|-----------|-------------|-------|
| Object storage | Azure Data Lake Storage Gen2 (ADLS) | Hierarchical namespace enables Hadoop-compatible paths |
| Table format | Delta Lake (strong Azure support), Iceberg growing | Databricks on Azure is common |
| Catalog | Azure Purview / Unity Catalog | Purview for governance; Unity for Databricks |
| SQL engine | Azure Synapse Analytics, Databricks | Synapse serverless + dedicated pools |
| Batch compute | Azure Databricks (dominant), HDInsight | Databricks is the de facto Azure lake compute |
| Streaming | Azure Event Hubs, HDInsight Kafka | Event Hubs = managed Kafka |
| ML | Azure Machine Learning | Full ML lifecycle |

### Google Cloud

| Component | GCP Option | Notes |
|-----------|-----------|-------|
| Object storage | Google Cloud Storage (GCS) | Strong multi-regional and analytics integration |
| Table format | Apache Iceberg (via BigQuery), Delta | BigQuery external Iceberg tables growing |
| Catalog | BigQuery, Dataplex | BigQuery as unified catalog emerging |
| SQL engine | BigQuery (serverless DW + lake queries) | Unique: BigQuery unifies DW and lake |
| Batch compute | Dataproc (Spark), BigQuery | BigQuery can query GCS directly |
| Streaming | Pub/Sub, Dataflow | Pub/Sub = managed; Dataflow = Beam-based streaming |
| ML | Vertex AI | Full ML platform |

### Multi-Cloud Considerations

If the organization uses multiple clouds:
- **Storage**: Each cloud's object store; data transfer costs for cross-cloud movement
- **Table format**: Apache Iceberg has the broadest cross-cloud support
- **Catalog**: Apache Polaris (open Iceberg REST catalog) or Nessie can serve as a neutral catalog
- **Compute**: Separate compute per cloud; Trino/Presto can federate queries across clouds

---

## The Klodars Corporation Journey

Gopalan uses Klodars Corporation as a running case study throughout the book. Their journey illustrates the decision framework in practice:

### Klodars Phase 1: Starting Out
- **Situation**: Growing e-commerce company; data in Salesforce, MySQL, S3 raw logs
- **Customers**: 3 analysts needing weekly sales reports
- **Decision**: Modern Data Warehouse (Redshift) + S3 raw storage
- **Why**: Small team, SQL-centric, BI is the only use case

### Klodars Phase 2: Expansion
- **Situation**: Data science team added; ML on customer behavior needed; costs rising
- **Customers**: Analysts (SQL/BI) + data scientists (Python/Spark)
- **Decision**: Data Lakehouse with Apache Iceberg on S3
- **Why**: Unified storage for both workloads; Redshift costs were high; ML requires raw data access

### Klodars Phase 3: Scale
- **Situation**: 5 distinct business domains; data engineering team is a bottleneck
- **Customers**: Multiple domain teams wanting autonomy
- **Decision**: Data Mesh organizational pattern layered on the Lakehouse
- **Why**: No single team can keep up; domain teams have data expertise; platform team provides tooling

This progression illustrates Gopalan's core message: **the right architecture depends on where you are in your journey, not where you want to eventually be.**

---

## Common Architecture Anti-Patterns

| Anti-Pattern | Symptom | Correction |
|-------------|---------|-----------|
| **Data swamp** | Data exists but no one trusts or uses it | Add governance, catalog, and curation |
| **Lift and shift** | On-prem patterns applied to cloud; costs as high as on-prem | Redesign for cloud-native; decouple compute/storage |
| **Premature Data Mesh** | One team, small scale, data mesh anyway | Use simpler lakehouse pattern; add mesh when org demands it |
| **Format zoo** | Iceberg + Delta + Hudi all in one lake | Choose one primary format; use XTable for interop if needed |
| **Over-partitioning** | Millions of partitions, most nearly empty | Coarsen partition scheme; use Z-ordering for column filters |
| **Governance theater** | Policies exist on paper; not enforced technically | Implement technical controls; catalog-first access management |
| **Compute waste** | Large clusters running 24/7 | Autoscaling + spot instances; serverless where workload allows |
