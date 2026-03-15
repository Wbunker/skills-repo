---
name: cloud-data-lake-expert
description: Expert on cloud data lake technologies, architectures, design, and operations. Use when discussing data lake architecture selection (modern data warehouse, data lakehouse, data mesh), data lake zones and organization, open table formats (Apache Iceberg, Delta Lake, Apache Hudi), scalability strategies, performance optimization, cost management, data governance on data lakes, or choosing the right architecture for a given use case. Based on "The Cloud Data Lake" by Rukmani Gopalan (O'Reilly, 2022).
---

# Cloud Data Lake Expert

Based on "The Cloud Data Lake: A Guide to Building Robust Cloud Data Architecture" by Rukmani Gopalan (O'Reilly, 2022).

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                   CLOUD DATA LAKE LANDSCAPE                      │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                    ARCHITECTURE PATTERNS                  │   │
│  │                                                          │   │
│  │  Modern Data Warehouse   Data Lakehouse    Data Mesh     │   │
│  │  ─────────────────────   ─────────────    ─────────     │   │
│  │  DW + data lake          Lake + DW ACID   Domain-owned  │   │
│  │  BI-centric              unified storage  data products  │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
│  ┌────────────────┐  ┌──────────────┐  ┌──────────────────┐    │
│  │   DATA LAKE    │  │   COMPUTE    │  │   TABLE FORMATS  │    │
│  │   STORAGE      │  │   ENGINES    │  │                  │    │
│  │                │  │              │  │  Apache Iceberg  │    │
│  │  S3 / ADLS /   │  │  Spark       │  │  Delta Lake      │    │
│  │  GCS           │  │  Presto/Trino│  │  Apache Hudi     │    │
│  │  Object store  │  │  Flink       │  │                  │    │
│  │  + zones       │  │  Cloud DW    │  │  ACID · Schema   │    │
│  └────────────────┘  └──────────────┘  │  evolution ·    │    │
│                                        │  Time travel     │    │
│  ┌────────────────────────────────┐    └──────────────────┘    │
│  │        GOVERNANCE LAYER        │                             │
│  │  Classification · Catalog ·    │                             │
│  │  Access control · Quality      │                             │
│  └────────────────────────────────┘                             │
└─────────────────────────────────────────────────────────────────┘
```

## Quick Reference — Load the Right File

| Task | Reference File |
|------|---------------|
| Big Data concepts, cloud fundamentals, value proposition of data lakes | [foundations.md](references/foundations.md) |
| Architecture patterns: modern DW, lakehouse, data mesh, choosing between them | [architectures.md](references/architectures.md) |
| Data lake zones, infrastructure setup, governance intro, cost management | [design-and-operations.md](references/design-and-operations.md) |
| Partitioning, compaction, file sizing, scaling strategies | [scalability.md](references/scalability.md) |
| Query performance, caching, storage optimization, compute tuning | [performance.md](references/performance.md) |
| Apache Iceberg, Delta Lake, Apache Hudi — deep dive and comparison | [data-formats.md](references/data-formats.md) |
| Architecture selection framework, decision criteria, cloud provider guidance | [decision-framework.md](references/decision-framework.md) |
| Data lake maturity model, paths to building a lake, Work/Sensitive zones, self-service tiers, logical data lake, data federation, multiple lakes, automated cataloging | [enterprise-patterns.md](references/enterprise-patterns.md) |

## Reference Files

| File | Source | Topics |
|------|--------|--------|
| `foundations.md` | Gopalan Ch. 1 | Big Data definition, 3 Vs, cloud computing value, data lake value proposition, on-prem limitations, cloud data lake journey |
| `architectures.md` | Gopalan Ch. 2 | Modern Data Warehouse, Data Lakehouse, Data Mesh reference architectures, use cases, tradeoffs |
| `design-and-operations.md` | Gopalan Ch. 3 + Gorelik | Infrastructure setup, data lake zones (raw/staging/gold/work/sensitive), governance actors, data classification, metadata/catalog, access management, cost strategy |
| `scalability.md` | Gopalan Ch. 4 | File sizing, partitioning strategies, compaction, small file problem, scaling patterns, cost/performance balance |
| `performance.md` | Gopalan Ch. 5 | Query optimization, predicate pushdown, columnar formats, caching, compute autoscaling, data skew |
| `data-formats.md` | Gopalan Ch. 6 | Open table format overview, Apache Iceberg internals, Delta Lake internals, Apache Hudi internals, format comparison matrix |
| `decision-framework.md` | Gopalan Ch. 7 | Architecture decision criteria, customer types, business drivers, growth scenarios, hybrid approaches, cloud provider considerations |
| `enterprise-patterns.md` | Gorelik | Data lake maturity ladder (puddle→pond→lake→ocean), paths to building a lake, Work Zone, Sensitive Zone, self-service tiers by persona, logical data lake, data federation, multiple lakes topology, automated cataloging, Right Platform/Data/Interface framework |

*This skill synthesizes two books: "The Cloud Data Lake" by Rukmani Gopalan (O'Reilly, 2022) — cloud-native architecture focus — and "The Enterprise Big Data Lake" by Alex Gorelik (O'Reilly, 2019) — enterprise patterns, maturity, and self-service focus.*

## Core Decision Trees

### Which Architecture Pattern?

```
What is your primary use case?
├── Structured analytics + BI reporting, mostly structured data
│   └── Modern Data Warehouse Architecture
│       ├── Best for: SQL-heavy workloads, BI tools, low data variety
│       └── Use: Cloud DW (Snowflake, BigQuery, Redshift) + data lake staging
│
├── Mix of structured + unstructured, ML + BI, cost-conscious
│   └── Data Lakehouse Architecture
│       ├── Best for: Unified storage, ACID on lake, data science + BI
│       └── Use: Open table format (Iceberg/Delta/Hudi) on object storage
│
└── Large org, multiple domains, data as a product mindset
    └── Data Mesh Architecture
        ├── Best for: Decentralized ownership, domain autonomy, scale
        └── Use: Domain-owned data products + federated governance
```

### Which Open Table Format?

```
What ecosystem are you in?
├── Primarily Databricks → Delta Lake (native integration)
├── Primarily AWS (EMR, Athena, Glue) → Apache Iceberg (best AWS support)
├── Near-real-time upserts / CDC → Apache Hudi (built for record-level upserts)
├── Multi-cloud / multi-engine → Apache Iceberg (broadest engine support)
└── Kafka streaming + lakehouse → Apache Hudi or Iceberg with Flink
```

### Which Data Lake Zone for This Data?

```
Where does the data land?
├── Raw / Landing Zone — all data arrives here unchanged
│   └── Original format, append-only, immutable source of truth
├── Staging / Silver Zone — cleaned and standardized
│   └── Deduped, schema-enforced, PII masked, joined to reference data
├── Gold / Curated Zone — business-ready
│   └── Aggregated, certified, domain-specific, served to consumers
├── Work Zone — user experimentation workspace
│   └── Data science projects, sandboxes; no PII; light governance; time-bounded
└── Sensitive Zone — high-risk data requiring maximum controls
    └── PII/PHI/PCI; physically separate storage; MFA + full audit + column masking
```

### Where Is This Organization on the Maturity Ladder? (Gorelik)

```
What describes this organization's data initiative?
├── Single project, high IT involvement, narrow use case
│   └── Data Puddle — scale up by adding self-service and more data sources
├── Multiple projects, SQL-centric, IT-mediated, DW replacement mindset
│   └── Data Pond — add self-service, broader data types, and governance to reach lake
├── Enterprise-wide, multiple user types, self-service, governed, cataloged
│   └── Data Lake — full maturity; focus on optimization and domain expansion
└── Multi-org federated, cross-enterprise data sharing
    └── Data Ocean — advanced; adopt data mesh or marketplace patterns
```

### What Is the Right Starting Path? (Gorelik)

```
Where are you starting from?
├── Existing DW that is too expensive or slow
│   └── DW Offloading — migrate data to lake; treat as pond initially; expand from there
├── Data science team needing raw data + ML frameworks
│   └── Analytical Sandbox — build for scientists first; expand to analysts + BI later
├── One high-value use case that outgrew existing tools
│   └── Puddle to Lake — deliver one use case; let success pull in more data and users
└── Greenfield / no existing data infrastructure
    └── Greenfield Build — design zones and governance upfront; iterate with real consumers fast
```

## Key Concepts

### The 3 Vs of Big Data
- **Volume**: Data too large for traditional systems (petabytes)
- **Velocity**: Data arriving faster than batch can handle (streaming)
- **Variety**: Structured + semi-structured + unstructured data together

### Cloud Data Lake vs. On-Premises Data Warehouse

| Dimension | On-Prem DW | Cloud Data Lake |
|-----------|-----------|-----------------|
| Storage cost | High (SAN/NAS) | Low (object store) |
| Schema requirement | Schema-on-write | Schema-on-read |
| Data types | Structured only | All types |
| Scale | Fixed capacity | Elastic |
| Latency to value | Weeks/months | Days/weeks |
| Compute/storage | Coupled | Decoupled |

### Data Lake Zones (Klodars Corporation Model)
Gopalan uses the fictional "Klodars Corporation" throughout the book as a running case study for illustrating patterns.

1. **Raw/Landing Zone** — immutable, original data as received
2. **Staging/Processing Zone** — in-flight transformations, intermediate state
3. **Curated/Gold Zone** — certified, business-ready data products
4. **Sandbox Zone** (optional) — exploration and experimentation, not production
