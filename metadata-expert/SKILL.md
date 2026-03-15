---
name: metadata-expert
description: Metadata management expertise covering metadata types, business/technical/operational metadata, data lineage, governance, quality, data catalogs, standards, and implementation programs. Use when designing metadata strategies, building data catalogs, defining business glossaries, establishing data governance, managing data lineage, assessing metadata maturity, or implementing metadata management programs. Based on Olesen-Bagneux's semiotic framework: metadata is fundamentally about signs and meaning, not just technical attributes.
---

# Metadata Management Expert

Based on "Fundamentals of Metadata Management" by Ole Olesen-Bagneux (Technics Publications, 2022).

## The Metadata Framework

```
┌────────────────────────────────────────────────────────────┐
│                    METADATA UNIVERSE                        │
│                                                            │
│   ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │
│   │   BUSINESS   │  │  TECHNICAL   │  │ OPERATIONAL  │   │
│   │   METADATA   │  │   METADATA   │  │   METADATA   │   │
│   │              │  │              │  │              │   │
│   │ Glossary     │  │ Schema       │  │ Process logs │   │
│   │ Definitions  │  │ Lineage      │  │ Job stats    │   │
│   │ Taxonomies   │  │ Data types   │  │ Quality runs │   │
│   │ KPIs         │  │ Profiles     │  │ Audit trails │   │
│   └──────┬───────┘  └──────┬───────┘  └──────┬───────┘   │
│          │                 │                  │            │
│          └─────────────────┼──────────────────┘           │
│                            ▼                               │
│              ┌─────────────────────────┐                  │
│              │      DATA CATALOG        │                  │
│              │  (unified discovery &    │                  │
│              │   governance layer)      │                  │
│              └─────────────┬───────────┘                  │
│                            │                               │
│              ┌─────────────▼───────────┐                  │
│              │   METADATA GOVERNANCE    │                  │
│              │  Stewardship · Quality   │                  │
│              │  Standards · Policies    │                  │
│              └─────────────────────────┘                  │
└────────────────────────────────────────────────────────────┘
```

## Quick Reference

| Task | Reference |
|------|-----------|
| What is metadata, semiotic foundations, metadata types, ecosystem | [foundations.md](references/foundations.md) |
| Business glossary, data dictionaries, taxonomies, ontologies, KPIs | [business-metadata.md](references/business-metadata.md) |
| Schemas, data profiles, technical lineage, storage/format attributes | [technical-metadata.md](references/technical-metadata.md) |
| Process metadata, job execution, pipeline lineage, audit logs | [operational-metadata.md](references/operational-metadata.md) |
| Stewardship, ownership, policies, metadata quality dimensions | [governance.md](references/governance.md) |
| Data catalog architecture, tool selection, standards, implementation | [catalogs-and-standards.md](references/catalogs-and-standards.md) |
| Maturity models, program design, change management, roadmaps | [implementation.md](references/implementation.md) |

## Reference Files

| File | Chapters | Topics |
|------|----------|--------|
| `foundations.md` | 1–2 | Semiotic theory of metadata, triadic sign model, metadata vs. data, three fundamental types, the metadata ecosystem, metadata relationships |
| `business-metadata.md` | 3–4 | Business glossary design, data dictionary, taxonomies, ontologies, KPIs/metrics definitions, stewardship roles, term lifecycle |
| `technical-metadata.md` | 5 | Schema metadata, data profiling, column statistics, format/encoding, storage attributes, technical lineage, API metadata |
| `operational-metadata.md` | 6 | Process lineage, ETL/pipeline metadata, job execution records, SLAs, data freshness, audit trails, observability |
| `governance.md` | 7–8 | Governance models, data stewardship, ownership patterns, metadata policies, metadata quality dimensions (completeness, accuracy, timeliness), quality scoring |
| `catalogs-and-standards.md` | 9–10 | Data catalog architecture, active vs. passive catalogs, metadata standards (Dublin Core, DCAT, OpenMetadata, Egeria), interoperability, API patterns |
| `implementation.md` | 11–12 | Metadata management program design, maturity model, incremental rollout, change management, metrics for success, organizational patterns |

## Core Decision Trees

### What Type of Metadata Do You Need?

```
What question are you trying to answer?
├── "What does this data mean?" → Business Metadata
│   ├── Define terms → Business Glossary
│   ├── Organize concepts → Taxonomy / Ontology
│   └── Track KPIs → Metric definitions
├── "How is this data structured?" → Technical Metadata
│   ├── Tables/columns/types → Schema metadata
│   ├── Data quality stats → Data profiles
│   └── Where does it live? → Storage/format metadata
├── "Where did this data come from?" → Lineage Metadata
│   ├── System-to-system path → Technical lineage
│   ├── Transformation logic → Process lineage
│   └── Business impact → Business lineage
├── "How was this data processed?" → Operational Metadata
│   ├── Job runs, timing → Process logs
│   ├── Data volumes, errors → Execution statistics
│   └── Who accessed what → Audit metadata
└── "Is this data trustworthy?" → Governance Metadata
    ├── Who owns it → Ownership/stewardship
    ├── Is it certified → Certification status
    └── What policy applies → Policy metadata
```

### Catalog vs. Repository vs. Inventory

```
What do you need to build?
├── Need discovery + context + governance → Data Catalog (active)
│   └── Integrates technical, business, operational metadata
├── Need authoritative definitions only → Business Glossary
│   └── Part of catalog or standalone
├── Need technical specs documented → Data Dictionary
│   └── Column-level documentation, often static
├── Just need to know what exists → Data Inventory
│   └── Simplest form, no enrichment
└── Need full metadata management platform → Metadata Repository
    └── Stores and manages all metadata types with governance
```

### Metadata Governance Model

```
Who should own metadata?
├── Small org / single domain → Centralized model
│   └── One metadata team owns all definitions
├── Large org / many domains → Federated model
│   ├── Domain stewards own domain metadata
│   └── Central team sets standards & enforces quality
├── Highly regulated industry → Governed federated
│   ├── Mandatory policies centrally enforced
│   └── Execution delegated to domain stewards
└── Data mesh org → Domain-oriented ownership
    ├── Domain teams own and publish their metadata
    └── Central platform provides standards and tooling
```

## Key Concepts (Olesen-Bagneux Framework)

### The Semiotic Triangle
Metadata is fundamentally **semiotic** — it creates meaning through signs:
- **Sign** — the metadata element itself (e.g., column name `cust_id`)
- **Object** — what it refers to (actual customer identifier in the database)
- **Interpretant** — how a person or system understands it (business context, rules)

Good metadata bridges all three: syntactic correctness alone is insufficient without semantic clarity.

### Metadata Typology
| Type | Answers | Examples |
|------|---------|----------|
| **Business** | What does it mean? | Glossary terms, KPI definitions, data owners |
| **Technical** | How is it structured? | Schema, data types, format, encoding, profile stats |
| **Operational** | How was it used? | Job logs, lineage events, access records, SLAs |

### The Metadata Lifecycle
```
Create → Capture → Store → Maintain → Publish → Use → Archive/Retire
```
Each stage requires different governance controls and tooling.

### Fitness for Purpose (Not Universal Truth)
Metadata quality is **contextual** — metadata that is fit for one use may be unfit for another. Always evaluate metadata quality relative to the consuming use case, not in the abstract.
