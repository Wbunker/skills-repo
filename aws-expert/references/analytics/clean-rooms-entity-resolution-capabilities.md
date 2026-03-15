# AWS Clean Rooms & Entity Resolution — Capabilities Reference
For CLI commands, see [clean-rooms-entity-resolution-cli.md](clean-rooms-entity-resolution-cli.md).

## AWS Clean Rooms

**Purpose**: Enable multiple organizations to collaborate on combined datasets and derive insights without any party exposing their raw data to the others.

### Core Concepts

| Concept | Description |
|---|---|
| **Collaboration** | A workspace created by one member; defines the parties and privacy controls |
| **Member** | An AWS account participating in a collaboration; can be query runner, contributor, or both |
| **Configured table** | A table (from S3/Glue, Athena, or Snowflake) linked to a collaboration with analysis rules applied |
| **Analysis rule** | SQL restrictions on a configured table; controls what queries members can run |
| **Analysis template** | Pre-approved SQL query template that members can execute |
| **Protected query** | A query executed within the collaboration; results returned only to the requesting member |

### Analysis Rule Types

| Type | Description |
|---|---|
| **Aggregation** | Only allows aggregate queries (SUM, COUNT, AVG); requires minimum row threshold to prevent re-identification |
| **List** | Returns a list of values (e.g., matching user IDs); restricted to specific columns |
| **Custom** | Allows pre-approved analysis templates; most flexible; full query execution |

### Differential Privacy

Mathematically backed privacy guarantees: adds controlled noise to query outputs to prevent individual-level inference. Configured with a privacy budget (epsilon). Fully managed — no statistical expertise required to configure.

### AWS Clean Rooms ML

Enables lookalike modeling: one party provides a training segment, the other receives audience scores without exchanging raw data. Useful for advertising and marketing collaboration use cases.

### Data Sources for Configured Tables

- Amazon S3 (via AWS Glue Data Catalog)
- Amazon Athena (Glue catalog views)
- Snowflake (via AWS Secrets Manager connection)

---

## AWS Entity Resolution

**Purpose**: Match and link related records across different data sources without sharing underlying sensitive data, using rule-based and ML-based matching.

### Core Concepts

| Concept | Description |
|---|---|
| **Matching workflow** | Pipeline that compares records across input sources and outputs matched record groups |
| **Schema mapping** | Maps source fields to standardized entity attribute types (NAME, ADDRESS, PHONE, EMAIL, etc.) |
| **ID namespace** | Collection of entity IDs from a single provider (e.g., a LiveRamp ID graph); used for ID resolution |
| **Matching rule (rule-based)** | Exact or fuzzy match conditions on mapped attributes; deterministic |
| **ML matching** | Probabilistic matching using pre-trained AWS model; no rule writing required |
| **ID mapping workflow** | Link IDs from one namespace to IDs in another (e.g., internal ID to partner ID) |
| **Match group** | Set of records determined to refer to the same real-world entity |

### Matching Approaches

| Approach | When to use |
|---|---|
| **Rule-based** | High-quality, consistent data; deterministic requirements; auditable results |
| **ML-based** | Messy, inconsistent data; catching fuzzy matches rule-based misses; higher recall |
| **Provider service** | Use third-party identity graph (LiveRamp, TransUnion) directly from Entity Resolution |

### Key Integrations

- Input data from **Amazon S3** (CSV, Parquet) or **AWS Glue Data Catalog** tables
- Output match results written to **Amazon S3**
- Integrated with **AWS Lake Formation** for access control on matched data
- Works with **Amazon DataZone** for governed data sharing of matched records
