# Data Catalogs and Metadata Standards
## Chapters 9–10: Catalog Architecture, Tool Selection, Standards, Interoperability

---

## What Is a Data Catalog?

A **data catalog** is a managed inventory of data assets that combines:
- **Discovery**: Find data assets across the organization
- **Context**: Understand what the data means and where it came from
- **Governance**: Know who owns it, how to access it, and what policies apply
- **Trust**: Assess quality, freshness, and reliability before using it

### Catalog vs. Other Tools

| Tool | What it does | What it's not |
|------|-------------|---------------|
| **Data catalog** | Active discovery, governance, lineage, collaboration | Not a data storage system |
| **Data dictionary** | Static column-level documentation | Not discovery; not lineage |
| **Business glossary** | Authoritative term definitions | Not technical metadata |
| **Metadata repository** | Stores and manages metadata (often the backend of a catalog) | Not user-facing discovery |
| **Data inventory** | Lists what assets exist | No enrichment, governance, or search |
| **Schema registry** | Machine-readable format schemas | Not business context |

---

## Active vs. Passive Catalogs

### Passive Catalog (Documentation Catalog)
- Metadata is **manually entered** by users
- Acts as a documentation system (like a wiki)
- Does not auto-discover or sync with source systems
- Examples: Confluence-based data wikis, early-generation catalogs

**Weaknesses**: Immediately starts going stale; requires high manual effort; poor for large-scale deployments

### Active Catalog (Intelligent Catalog)
- Automatically **crawls and ingests** technical metadata from source systems
- Surfaces metadata to users through search and discovery
- Integrates lineage, quality, and access patterns automatically
- Business metadata is layered on top through stewardship workflows

**Key capabilities of active catalogs:**
1. **Automated crawling**: Connect to databases, lakes, warehouses, BI tools and extract schema/stats
2. **Semantic classification**: Auto-classify PII, PHI, financial data using ML
3. **Lineage ingestion**: Ingest lineage from pipelines (via OpenLineage, SQL parsing, API)
4. **Search and discovery**: Full-text search with metadata-aware ranking
5. **Collaboration**: Ratings, reviews, endorsements, questions
6. **Governance workflows**: Stewardship tasks, certification, access requests

---

## Catalog Architecture

```
┌────────────────────────────────────────────────────────────┐
│                    DATA CATALOG                             │
│                                                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │   DISCOVERY  │  │  GOVERNANCE  │  │ COLLABORATION │    │
│  │   LAYER      │  │   LAYER      │  │    LAYER      │    │
│  │  Search      │  │  Stewardship │  │  Ratings      │    │
│  │  Browse      │  │  Policies    │  │  Comments     │    │
│  │  Recommend   │  │  Workflows   │  │  Questions    │    │
│  └──────┬───────┘  └──────┬───────┘  └──────┬────────┘   │
│         └─────────────────┼─────────────────┘            │
│                           ▼                               │
│              ┌────────────────────────┐                   │
│              │   METADATA REPOSITORY  │                   │
│              │  (Graph / Search DB)   │                   │
│              └───────────┬────────────┘                   │
│                          │                                │
│          ┌───────────────┼───────────────┐               │
│          ▼               ▼               ▼               │
│   ┌──────────┐   ┌──────────────┐  ┌──────────┐         │
│   │ CRAWLERS │   │  LINEAGE     │  │  API /   │         │
│   │ (ingestion│  │  INGESTION   │  │  MANUAL  │         │
│   │  agents) │   │  (OpenLineage│  │  INPUT   │         │
│   └────┬─────┘   └──────┬───────┘  └────┬─────┘         │
└────────┼────────────────┼───────────────┼────────────────┘
         ▼                ▼               ▼
   [Databases]      [ETL/Pipelines]   [Business Users]
   [Data Lakes]     [Airflow/dbt]     [API Producers]
   [Warehouses]     [Spark/Flink]
   [BI Tools]
```

### Metadata Repository Storage Options

| Storage Type | Use Case | Examples |
|-------------|---------|---------|
| **Graph database** | Rich relationship queries, lineage traversal | Neo4j, Amazon Neptune, JanusGraph |
| **Document store** | Flexible schema for heterogeneous metadata | Elasticsearch, MongoDB |
| **Relational DB** | Structured metadata with strong consistency | PostgreSQL, MySQL |
| **Triple store** | RDF/semantic web; ontology-based | Apache Jena, Virtuoso |
| **Hybrid** | Combined approach for different metadata types | Most enterprise catalogs use multiple |

---

## Data Catalog Tool Landscape

### Open Source / Community

| Tool | Strengths | Weaknesses |
|------|-----------|------------|
| **Apache Atlas** | Deep Hadoop ecosystem integration; policy engine (Ranger) | Complex setup; Hadoop-centric |
| **OpenMetadata** | Modern API-first design; active community; good lineage | Younger project; evolving |
| **DataHub (LinkedIn)** | Rich lineage; strong dbt/Airflow integration; production-proven | Heavy infrastructure |
| **Amundsen (Lyft)** | Simple search-focused; good for smaller orgs | Limited governance; basic lineage |
| **Egeria (ODPi)** | Open standard; interoperability focus | Complex; more framework than product |

### Commercial

| Tool | Strengths | Best For |
|------|-----------|----------|
| **Collibra** | Deep governance, workflow, policy | Large enterprise with strong governance needs |
| **Alation** | User adoption, ML-driven; strong SQL curation | Analyst-focused organizations |
| **Atlan** | Modern UI; collaborative; good integrations | Mid-market, data-mesh-oriented teams |
| **Microsoft Purview** | Azure-native; end-to-end governance | Azure-centric enterprises |
| **Google Dataplex** | GCP-native; auto-classification; DQ rules | GCP-centric enterprises |
| **AWS Glue Data Catalog** | Technical metadata; S3/EMR native | AWS shops needing schema registry |
| **Informatica** | Mature; AI-powered; enterprise-grade | Large enterprise with legacy Informatica stack |

### Selection Criteria

```
Choosing a data catalog:
├── Team size < 50 data users → Start with lighter tooling (Amundsen, OpenMetadata)
├── Primary need is governance/compliance → Collibra, Purview
├── Primary need is analyst self-service → Alation, Atlan
├── Cloud-native / single cloud → Cloud provider native (Dataplex, Purview, Glue)
├── Data mesh architecture → OpenMetadata, DataHub, Atlan
├── Strong budget, all needs → Enterprise: Collibra, Informatica, Alation
└── Open source preference → DataHub or OpenMetadata
```

---

## Metadata Standards

### Why Standards Matter
Without metadata standards:
- Different systems use incompatible schemas
- Metadata cannot be exchanged or integrated
- Vendor lock-in for metadata storage
- Governance policies cannot be enforced across tools

### Key Metadata Standards

**Dublin Core (ISO 15836)**
- Purpose: Basic descriptive metadata for any resource
- 15 core elements: title, creator, subject, description, publisher, contributor, date, type, format, identifier, source, language, relation, coverage, rights
- Use case: Document libraries, web resources, archives; not data-specific enough for modern analytics

**DCAT (Data Catalog Vocabulary)**
- Purpose: RDF vocabulary for describing catalogs and datasets
- Core concepts: Catalog, Dataset, Distribution, DataService
- Use case: Government open data portals; interoperability between catalogs
- Standard: W3C recommendation

**OpenMetadata Schema**
- Purpose: Open standard for data asset metadata
- Key entities: Table, Topic (Kafka), Pipeline, Dashboard, MlModel, User, Team
- Use case: API-first catalog implementations; tool interoperability
- Standard: Community-driven open standard

**OpenLineage**
- Purpose: Standard for lineage events from data pipelines
- Model: Run events (START/COMPLETE/FAIL) with input/output datasets
- Use case: Collecting lineage from Airflow, dbt, Spark, Flink, etc.
- Standard: Linux Foundation project; widely adopted

**FIBO (Financial Industry Business Ontology)**
- Purpose: Ontology for financial services concepts
- Use case: Financial institutions that need shared semantic definitions
- Standard: EDM Council / OMG

**HL7 FHIR (Healthcare)**
- Purpose: Standard for healthcare data exchange including metadata
- Use case: Healthcare organizations exchanging clinical data
- Standard: HL7 international

### Metadata Interoperability Patterns

**Pattern 1: Canonical Metadata Model**
Define a central metadata schema that all tools must conform to when exchanging metadata.
```
Tool A metadata → transform → canonical model → transform → Tool B
```
Pro: Clean integration. Con: High upfront design cost.

**Pattern 2: Hub-and-Spoke (Catalog as Hub)**
The catalog is the central metadata store; all tools push/pull to/from it.
```
Tool A → REST API → Central Catalog ← REST API ← Tool B
```
Pro: Single source of truth. Con: Catalog becomes critical dependency.

**Pattern 3: Event-Driven Metadata Bus**
Tools publish metadata events to a shared bus; consumers subscribe.
```
Tool A → metadata events → Kafka → metadata consumers (catalog, monitoring, governance)
```
Pro: Decoupled, scalable. Con: Complex to implement and operate.

---

## Catalog Adoption Best Practices

### The Trust Flywheel
```
Good metadata → Users find reliable data → Users contribute back (ratings, comments)
     ↑                                                            │
     └────────────────────────────────────────────────────────────┘
                        Virtuous cycle
```

### Common Adoption Failures

| Failure | Cause | Fix |
|---------|-------|-----|
| Low search usage | Poor relevance; users don't know catalog exists | Training, embed in workflows |
| Catalog goes stale | No stewardship; no automated sync | Governance + crawling automation |
| "Empty catalog" syndrome | Launched before data ingested | Seed with 20–30 key assets first |
| Stewards don't update | No tooling; not part of workflow | Stewardship tasks in catalog UI |
| IT-only catalog | Business not involved | Involve business stewards from day 1 |

### Metrics for Catalog Success

| Metric | Measurement |
|--------|-------------|
| Active monthly users | Unique users accessing catalog per month |
| Search-to-asset rate | % of searches that result in an asset click |
| Asset coverage | % of production assets registered in catalog |
| Enrichment rate | % of assets with business description |
| Time-to-find | Average time from data need to data access |
| Self-service rate | % of data access requests resolved via catalog (no tickets) |
