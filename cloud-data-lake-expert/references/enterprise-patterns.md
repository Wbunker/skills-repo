# Enterprise Data Lake Patterns
## Gorelik's "The Enterprise Big Data Lake" — Enterprise-Specific Frameworks

Source: "The Enterprise Big Data Lake: Delivering the Promise of Big Data and Data Science" by Alex Gorelik (O'Reilly, 2019).

---

## The Right Platform, Right Data, Right Interface Framework

Gorelik's three-pillar framework for a successful enterprise data lake. All three must be in place; failure in any one causes lake failure regardless of the other two.

```
┌─────────────────────────────────────────────────────────────┐
│                 DATA LAKE SUCCESS FORMULA                    │
│                                                             │
│   RIGHT PLATFORM        RIGHT DATA        RIGHT INTERFACE   │
│   ─────────────         ──────────        ──────────────   │
│   Technology that        Data that is      Interface that   │
│   scales and fits        trustworthy,      matches the      │
│   enterprise needs       discoverable,     user's skill     │
│                          and governed      level            │
└─────────────────────────────────────────────────────────────┘
```

### Right Platform

The platform must handle the enterprise's scale, security, and integration requirements:
- Object storage or HDFS-based storage at enterprise scale
- Compute engines appropriate to workload mix (SQL, ML, streaming)
- Security integration (LDAP/AD, Kerberos, encryption)
- Enterprise-grade availability and disaster recovery
- Cost model that fits enterprise budgeting cycles

### Right Data

Data must be findable, understandable, and trustworthy:
- Comprehensive metadata (technical + business + operational)
- Automated cataloging so data is discoverable without tribal knowledge
- Data quality monitoring with observable SLAs
- Lineage from source to consumption
- Sensitive data identification and appropriate controls
- Data provisioning — a clear process for getting new data into the lake

### Right Interface

Different users need different interfaces — a single interface serves no one well:

| User Type | Skill Level | Interface | Zone |
|-----------|------------|-----------|------|
| Business User | Low | Self-service BI (Tableau, Power BI, Looker) | Gold only |
| Business Analyst | Medium | SQL interface, pre-built datasets | Gold zone |
| Data Analyst | Medium-High | Notebooks, SQL, visual exploration | Gold + Work zones |
| Data Scientist | High | Python/R notebooks, direct data access, ML frameworks | All zones |
| Data Engineer | Expert | CLI, APIs, raw data access, pipeline tools | All zones |

**Key insight**: Providing only one interface means power users are frustrated by constraints and novice users are overwhelmed by complexity. A successful enterprise lake offers a spectrum.

---

## The Data Lake Maturity Model

Gorelik's maturity ladder describes how data initiatives evolve from small, project-specific data stores to enterprise-wide data platforms:

```
                        MATURITY
                           │
      Data Ocean           │   Multi-org, federated lakes
         ▲                 │   Cross-enterprise data sharing
         │                 │
      Data Lake            │   Enterprise-wide, self-service
         ▲                 │   All data types, broad user access
         │                 │   Governed, cataloged, quality SLAs
      Data Pond            │
         ▲                 │   DW-replacement using big data tech
         │                 │   SQL-centric, batch-oriented
         │                 │   IT-managed, limited self-service
      Data Puddle          │
                           │   Single project, single team
                           │   Data mart equivalent in big data tech
                           │   Narrow use case, high IT involvement
```

### Data Puddle

**What it is**: A big-data-scale data store built for a single project or team. Functionally equivalent to a data mart but built on Hadoop/cloud object storage instead of a relational database.

**Characteristics:**
- Narrow scope: one business question or one team's needs
- High IT involvement: analysts rely on engineers to pull and prepare data
- Little governance: usually no formal catalog, lineage, or SLAs
- Often born from necessity: a specific use case that outgrew the DW

**Examples**: A fraud detection team's feature store built on Spark; a single data science project's feature dataset.

### Data Pond

**What it is**: A collection of data puddles. Architecturally similar to a data warehouse but built on big data technology. IT-managed, SQL-centric, batch-oriented.

**Characteristics:**
- Multiple projects or teams served, but still IT-mediated
- DW offloading is the most common path to a data pond
- Focused on structured data and SQL workloads
- Limited self-service: users request data; IT provides it
- Low data variety: mostly structured data, similar to what was in the DW

**The key distinction from a data lake**: A data pond provides a less-expensive, more-scalable *alternative* to an existing DW. A data lake *enables* business users to answer their own questions with data they discover themselves.

### Data Lake

**What it is**: Enterprise-wide data platform with self-service access for users at multiple skill levels. Covers all data types, all business domains, with appropriate governance.

**Characteristics:**
- Multi-domain: all business areas represented
- Self-service: users can find, understand, and provision data themselves
- All data types: structured, semi-structured, unstructured
- Governed: catalog, data quality, lineage, access control
- Multiple interfaces: BI tools, SQL, notebooks, APIs
- Zone-based organization with differentiated governance per zone

### Data Ocean

**What it is**: Federated networks of data lakes across multiple organizations or very large enterprises with many sub-organizations. Data is shared across lakes.

**Characteristics:**
- Cross-organizational or cross-enterprise data sharing
- Federated governance: each lake has autonomy + shared standards
- Data marketplace or exchange capabilities
- Advanced lineage across organizational boundaries

**Practical relevance**: Data Mesh at large scale; cloud data marketplaces (AWS Data Exchange, Azure Data Share, Snowflake Data Marketplace) represent emerging data ocean patterns.

---

## Paths to Building a Data Lake

Gorelik identifies four common starting points. Each has different implications for architecture, team structure, and governance maturity needed.

### Path 1: DW Offloading

**What it is**: Start by migrating data from an expensive on-premises data warehouse to a cloud data lake, reducing storage and compute costs.

**Motivation**: DW is expensive, slow to scale, or approaching capacity. The lake is initially just a cheaper DW.

**Characteristics:**
- Starts with structured, well-understood data
- Users are already SQL-trained
- Governance often already exists (migrate it)
- Risk: low (data is already known and governed)
- Result: a Data Pond, not yet a Data Lake

**Path to lake maturity**: After offloading, add raw data ingestion, expand to new data types, build self-service capabilities.

**Common mistake**: Treating DW offloading as the destination rather than the starting point. A DW replica in the cloud is a pond, not a lake.

### Path 2: Analytical Sandbox

**What it is**: Build a playground for data scientists and analysts to experiment with new data types and workloads that can't run in the DW.

**Motivation**: Data science team needs raw data access, ML frameworks, and the ability to experiment without waiting for IT.

**Characteristics:**
- Starts with data scientists as primary users
- Focus on notebooks, Python/R, flexible schemas
- Governance is light initially (sandbox)
- Risk: medium (new tools, but limited blast radius)
- Result: strong data science foundation but may lack BI/analyst capabilities

**Path to lake maturity**: Expand user base to analysts, add BI interfaces, formalize governance, onboard business domains.

**Common mistake**: Sandbox stays a sandbox — data science playground never expands to serve the broader organization.

### Path 3: Data Puddle to Lake (Organic Growth)

**What it is**: One successful project data store (puddle) demonstrates value, attracts other teams, and grows organically into a lake.

**Motivation**: Bottoms-up adoption — no top-down mandate, just proven value spreading.

**Characteristics:**
- Starts with one high-value use case
- Growth is demand-driven
- Governance is often retrofitted as scale demands it
- Risk: low initially, medium later (technical debt in governance, inconsistent standards)
- Result: highly practical, business-aligned, but potentially inconsistent architecture

**Path to lake maturity**: As the platform grows, invest in governance, catalog, zone formalization, and access standardization. The hardest part is formalizing what grew organically.

### Path 4: Greenfield Build

**What it is**: Design and build the data lake from scratch, often as a strategic initiative, without an existing DW or data science infrastructure.

**Motivation**: New organization, major digital transformation, or complete replacement of legacy systems.

**Characteristics:**
- Full design freedom (no legacy constraints)
- Requires strong architectural vision upfront
- Governance and zones can be designed correctly from the start
- Risk: high (no existing data consumers to validate design; "build and they will come" risk)
- Takes longest before delivering value

**Path to lake maturity**: Rapid iteration with early consumer feedback; don't over-engineer upfront; deliver working data products to real consumers quickly.

---

## Extended Zone Model (Gorelik's 4-Zone Model)

Gorelik's zone model extends the basic 3-zone (raw/staging/gold) with two important additions:

```
┌────────────────────────────────────────────────────────────┐
│                    DATA LAKE ZONES                          │
│                                                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │  RAW /       │  │   GOLD /     │  │    WORK      │    │
│  │  LANDING     │  │  PRODUCTION  │  │    ZONE      │    │
│  │  ZONE        │  │  ZONE        │  │              │    │
│  │              │  │              │  │ Experiments  │    │
│  │ Original     │  │ Governed,    │  │ Sandboxes    │    │
│  │ immutable    │  │ quality SLAs │  │ Data science │    │
│  │ data         │  │ certified    │  │ workspaces   │    │
│  └──────────────┘  └──────────────┘  └──────────────┘    │
│                                                            │
│  ┌────────────────────────────────────────────────────┐   │
│  │                 SENSITIVE ZONE                      │   │
│  │   PII · PHI · PCI · Trade secrets                  │   │
│  │   Maximum access controls · Mandatory audit         │   │
│  │   Separate physical storage · Encryption keys       │   │
│  └────────────────────────────────────────────────────┘   │
└────────────────────────────────────────────────────────────┘
```

### The Work Zone

The Work Zone is a user-managed workspace for experimentation, data science projects, and analysis that is not yet production-ready.

**Governance level**: Light — no quality or freshness SLAs; primary control is preventing sensitive data from leaking into the work zone.

**Who uses it**: Data scientists, analysts, data engineers during development.

**Key rules:**
- Data must not contain unmasked sensitive/PII data
- Results are not served to production consumers without promotion to gold zone
- Storage is bounded per user/team (quota enforcement)
- Data expires after a defined period (e.g., 90 days) unless renewed
- Users own their workspace data and pipelines

**Governance by zone (Gorelik's model):**

| Zone | Governance Level | SLAs | Who Writes | Who Reads |
|------|-----------------|------|-----------|-----------|
| Raw/Landing | Minimal | None | Ingestion pipelines | Data engineers |
| Gold/Production | Strong | Quality + freshness | Data engineers | Analysts, BI, apps |
| Work | Light | Project-specific | Data scientists, analysts | Work zone owner + team |
| Sensitive | Maximum | Strict + audited | Controlled pipelines | Privileged roles only |

### The Sensitive Zone

The Sensitive Zone is a physically separate storage location for data that contains PII, PHI, PCI, trade secrets, or other high-risk data. It is NOT simply a classification tag — it requires separate storage and stricter controls.

**Why separate physical storage:**
- Prevents accidental access through misconfigured permissions on shared buckets
- Enables different encryption key management (customer-managed keys)
- Simplifies audit scope (audit everything touching this zone, not everything in the lake)
- Supports regulatory requirements (some regulations require physical separation)

**Controls required:**
- Explicit role-based access with MFA for human access
- All access logged and audited
- Column-level masking for analytic users who need aggregate access
- Data minimization: only store what is strictly necessary
- Retention limits enforced technically, not just by policy

**Access pattern:**
```
Sensitive zone → masked/aggregated view → Gold zone (for analytics)
                                       ↑
                   Data engineer creates de-identified derivative dataset
                   Original PII stays in sensitive zone only
```

---

## Multiple Data Lakes

Gorelik addresses enterprise scenarios where a single data lake is insufficient:

### When Multiple Lakes Are Needed

| Scenario | Pattern |
|----------|---------|
| **Geographic data residency** | Regional lakes (EU lake, US lake) with no cross-region data movement |
| **Business unit autonomy** | BU-specific lakes with shared platform but separate governance |
| **Security clearance levels** | Classified vs. unclassified lakes (government/defense) |
| **Cloud provider diversity** | One lake per cloud (AWS lake + Azure lake); federation layer |
| **Acquisition integration** | Acquired company's lake maintained separately while integration proceeds |

### Hub-and-Spoke Pattern

```
       [Domain Lake A]     [Domain Lake B]
              │                   │
              └──────┬────────────┘
                     ▼
              [Central Enterprise Lake]
              (curated, governed, federated)
                     │
              ┌──────┴────────────┐
              ▼                   ▼
       [BI/Analytics]      [ML Platform]
```

Domains own and operate their domain lakes; the central enterprise lake contains certified, cross-domain datasets for enterprise analytics.

---

## Logical Data Lake and Data Federation

**One of Gorelik's most distinctive contributions**: the concept of the Logical Data Lake — querying data in place without physically moving it to the lake.

### What It Is

A Logical Data Lake (also called a Virtual Data Lake) creates a unified query interface over data that remains in its original systems — databases, APIs, SaaS applications, other data lakes — without requiring physical ingestion.

```
Traditional:              Logical / Federated:
────────────              ────────────────────
Source A → ingest →       Source A ─────┐
Source B → ingest → Lake  Source B ─────┤ → Logical
Source C → ingest →       Source C ─────┘    Layer → Users
(data moves)              (data stays in place; queries federate)
```

### Data Federation Technologies

Also called: **EII (Enterprise Information Integration)**, **data virtualization**, **query federation**.

| Technology | Examples | Approach |
|-----------|---------|---------|
| **Query federation** | Presto/Trino, Dremio, Starburst | Pushes SQL queries to remote sources; returns results |
| **Data virtualization** | Denodo, TIBCO Data Virtualization | Creates virtual tables/views over heterogeneous sources |
| **Polyglot query engines** | Apache Drill, Amazon Athena Federated | Query S3, JDBC, DynamoDB etc. in one SQL statement |
| **Semantic layer** | AtScale, Kyligence | Business-level virtual tables with pre-aggregation |

### When to Use Federation vs. Physical Ingestion

| Situation | Prefer Federation | Prefer Ingestion |
|-----------|-----------------|-----------------|
| Data changes frequently in source | Yes | No |
| Latency tolerance | Low (real-time) | Any |
| Query volume | Low | High |
| Source can handle query load | Yes | No |
| Need complex transformations | No | Yes |
| Need historical versions | No | Yes |
| Source data governance concerns | Yes (data doesn't leave source) | Requires data sharing agreements |

**Hybrid pattern** (most common in enterprise): Physically ingest high-volume, frequently-queried data; federate low-volume, sensitive, or rapidly-changing data that is better left at source.

---

## Self-Service Data Provisioning

Gorelik emphasizes that self-service is not just about query interfaces — users also need to **get data into the lake** and **discover data** without IT mediation.

### Self-Service Data Onboarding

A self-service onboarding workflow lets domain teams add their own data to the lake:

```
Data Owner submits request:
  - Source system and credentials
  - Data classification (sensitivity level)
  - Desired refresh frequency
  - Initial consumer(s)
        │
        ▼
Platform performs automated checks:
  - Schema validation
  - PII scan (automated classifier)
  - Source system connectivity
        │
        ▼
Auto-provisioned:
  - Ingestion pipeline created
  - Raw zone path allocated
  - Catalog entry created (auto-populated technical metadata)
  - Data owner notified
        │
        ▼
Data owner completes business metadata:
  - Description, business terms, owner, SLA
```

### Self-Service Data Discovery

Users must be able to find data **without knowing it exists**:

1. **Search**: Full-text search over catalog (table names, column names, descriptions, tags)
2. **Browse by domain**: Organized hierarchy (Finance → Revenue → Monthly Revenue Summary)
3. **Automated tagging**: ML classifiers suggest tags (PII, date-like, currency-like, categorical)
4. **Similarity search**: "Show me tables similar to this one"
5. **Usage signals**: "Most queried tables this week" surfaces popular data assets
6. **Lineage navigation**: "What tables are derived from this source?"

### Automated Cataloging and Data Fingerprinting

Gorelik's Waterline Data background shapes this section — automated cataloging is a key enabler of self-service at enterprise scale.

**Automated cataloging techniques:**

| Technique | What It Does |
|-----------|-------------|
| **Schema crawling** | Extracts table/column names and types from all registered sources |
| **Statistical profiling** | Computes null rates, cardinality, min/max, value distributions automatically |
| **PII detection** | Pattern matching + ML classifiers identify SSNs, emails, phone numbers, etc. |
| **Data fingerprinting** | Identifies semantically similar columns across tables (e.g., `cust_id` in 47 tables is the same concept) |
| **Tag suggestion** | ML suggests business tags based on column name patterns and sample values |
| **Duplicate detection** | Identifies tables that appear to contain the same or similar data |
| **Usage tracking** | Automatically enriches catalog with who is querying what (social metadata) |

**Key insight**: Human curation cannot scale to thousands of tables. Automated cataloging handles the first 80%; human stewards focus on the 20% that automation can't resolve (business definitions, ambiguous cases, cross-domain standards).
