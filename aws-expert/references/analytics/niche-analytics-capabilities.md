# Niche Analytics — Capabilities Reference
For CLI commands, see [niche-analytics-cli.md](niche-analytics-cli.md).

## Amazon CloudSearch

> **Note**: Amazon CloudSearch is no longer available to new customers. Existing customers can continue using it; AWS recommends migrating to Amazon OpenSearch Service.

**Purpose**: Fully managed search service for adding full-text and structured search to applications. Handles index management, scaling, and availability automatically.

### Core Concepts

| Concept | Description |
|---|---|
| **Search domain** | The core resource; contains your indexed data, search instances, and configuration |
| **Index field** | Typed field in the search schema; determines how data is indexed and what search features are available |
| **Document** | JSON or XML record uploaded for indexing; identified by a unique `id` |
| **Document service endpoint** | Per-domain endpoint for uploading documents (add/delete batches) |
| **Search endpoint** | Per-domain endpoint for submitting search queries |
| **Suggester** | Configuration for autocomplete suggestions based on indexed field values |
| **Analysis scheme** | Language-specific text processing configuration (tokenization, stemming, stopwords) |
| **Expression** | Custom numeric expression used for sorting or ranking results |

### Index Field Types

| Field type | Description |
|---|---|
| **text** | Arbitrary alphanumeric text; full-text search with stemming and stopword removal |
| **text-array** | Multi-value text field |
| **literal** | Exact-match identifier; case-sensitive; supports faceting |
| **literal-array** | Multi-value literal field |
| **int** | 64-bit signed integer; supports range searches and sorting |
| **int-array** | Multi-value integer field |
| **double** | Double-precision floating point; supports range searches and sorting |
| **double-array** | Multi-value double field |
| **date** | UTC timestamp (RFC 3339); supports range searches and sorting |
| **date-array** | Multi-value date field |
| **latlon** | Latitude/longitude pair (`lat,lon`); supports geospatial distance and bounding-box queries |

### Search Features

| Feature | Description |
|---|---|
| **Full-text search** | Language-specific processing in 34 languages; stemming, stopwords, and tokenization |
| **Boolean queries** | AND, OR, NOT operators; structured query syntax for combining field predicates |
| **Prefix search** | Match on the beginning of a term; useful for autocomplete without a suggester |
| **Range search** | Filter results by numeric, date, or string value ranges |
| **Faceting** | Count results by field value to drive navigation filters; requires `FacetEnabled` on literal/int/double/date fields |
| **Highlighting** | Return matching snippets with match terms emphasized; requires `HighlightEnabled` on text fields |
| **Autocomplete** | Suggester-based completions returned via the `/2013-01-01/suggest` endpoint |
| **Geospatial** | Distance calculations and bounding-box filters on `latlon` fields |
| **Term boosting** | Increase relevance weight for matches in specific fields using `^N` syntax |
| **Result sorting** | Sort by field value (requires `SortEnabled`) or by custom expression |

### Supported Languages (Analysis Schemes)

Arabic, Armenian, Basque, Bulgarian, Catalan, Chinese (Simplified/Traditional), Czech, Danish, Dutch, English, Finnish, French, Galician, German, Greek, Hindi, Hungarian, Indonesian, Irish, Italian, Japanese, Korean, Latvian, Norwegian, Persian, Portuguese, Romanian, Russian, Spanish, Swedish, Thai, Turkish, and a language-agnostic `mul` scheme.

---

## Amazon FinSpace

**Purpose**: Managed data management and analytics platform for financial services organizations. Provides a central repository for petabytes of financial data alongside managed compute for quantitative analysis, particularly for capital markets workflows.

### Deployment Modes

| Mode | Description |
|---|---|
| **FinSpace Managed Service** | Data catalog and analytics environment with Dataset Browser; integrated with AWS analytics services |
| **Managed kdb Clusters** | Fully managed kdb+ (KX Systems) clusters for ultra-low-latency time-series analytics; no kdb+ infrastructure to operate |

### Core Concepts (Managed Service)

| Concept | Description |
|---|---|
| **Environment** | Top-level FinSpace resource; an isolated workspace for your organization's data and users |
| **Dataset** | Named collection of related financial data; includes schema, data type, and permission model |
| **Dataset Browser** | Web UI for discovering, browsing, and requesting access to datasets within an environment |
| **Changeset** | An append-only record of data additions to a dataset; provides immutable audit history |
| **Data view** | A queryable projection of a dataset; maps dataset data to a specific format for analytics tools |
| **Permission group** | Manages which users have access to which datasets and what operations they can perform |

### Managed kdb Clusters

| Concept | Description |
|---|---|
| **kdb+ database** | Column-oriented time-series database optimized for financial tick data; uses q query language |
| **Cluster** | Managed kdb+ compute nodes; types include HDB (historical database), RDB (real-time database), gateway, and cache |
| **HDB (Historical Database)** | Queries partitioned historical tick data stored in FinSpace S3-backed storage |
| **RDB (Real-time Database)** | Ingests and holds intraday data; typically flushed to HDB at end of day |
| **Dataview (kdb)** | Virtual view across one or more kdb databases used to serve data to clusters |
| **Scaling group** | Manages auto-scaling of kdb cluster nodes based on workload |

### Capital Markets Use Cases

- Tick-by-tick market data ingestion and time-series queries
- Intraday and end-of-day risk calculations
- Trade analytics and execution analysis
- Market surveillance and compliance monitoring
- Portfolio optimization and back-testing

### Key Features

| Feature | Description |
|---|---|
| **Integrated data catalog** | Centralized metadata for all datasets; search and discovery across the environment |
| **Audit trail** | Immutable changesets provide full provenance for regulatory compliance |
| **AWS analytics integration** | Connect datasets to Athena, SageMaker, and Glue for broader analytics workflows |
| **Fine-grained access control** | Column- and row-level permissions per dataset per permission group |
| **Private networking** | Clusters run in your VPC via FinSpace-managed VPC attachments |

---

## AWS Data Exchange

**Purpose**: Subscribe to, use, and publish third-party datasets from AWS Marketplace. Eliminates manual data licensing and delivery logistics; data is delivered directly into your AWS environment.

### Core Concepts

| Concept | Description |
|---|---|
| **Data product** | A Marketplace listing from a provider; contains one or more data sets, pricing, and licensing terms |
| **Data set** | The unit of data within a product; each data set has a type (Files, API, Redshift, S3, Lake Formation) |
| **Revision** | A versioned snapshot of a data set; providers publish new revisions as data is updated |
| **Asset** | The individual data objects within a revision (S3 objects, API endpoints, Redshift tables) |
| **Subscription** | Entitlement that grants access to a provider's product for the subscription duration |
| **Data grant** | Direct peer-to-peer data sharing (no Marketplace listing required); sender creates a grant, receiver accepts it |

### Data Set Types

| Type | Description |
|---|---|
| **Files (S3)** | File assets imported from and exported to S3 buckets; most common type |
| **Amazon Redshift** | Read-only access to provider's Redshift data share; query without extracting data |
| **APIs** | Call provider APIs via API Gateway; subscribers get managed API keys |
| **AWS Lake Formation** | Direct access to provider's Lake Formation-governed data lake; query and transform in place |

### Delivery Methods

| Destination | Description |
|---|---|
| **Amazon S3** | Export file revisions to your S3 bucket; configure auto-export on new revisions |
| **Amazon Redshift** | Accept a Redshift data share and query directly from your Redshift cluster |
| **API calls** | Invoke provider APIs using subscriber-scoped API keys managed by Data Exchange |
| **AWS Lake Formation** | Accept Lake Formation data permissions and query via Athena or EMR |

### Auto-export to S3

Configure a revision destination so that each time a provider publishes a new revision, it is automatically exported to your S3 bucket. Useful for keeping downstream pipelines current without manual steps.

### Key Features

| Feature | Description |
|---|---|
| **AWS Marketplace catalog** | Discover thousands of datasets: financial, health, geospatial, weather, and more |
| **Provider publishing** | Publish and monetize your own data sets; AWS handles billing and delivery |
| **Licensing and terms** | Subscription terms, refund policies, and data use agreements managed by Marketplace |
| **Event-driven delivery** | EventBridge events emitted when new revisions are published; trigger Lambda or Step Functions workflows |
| **Audit and governance** | CloudTrail logs all Data Exchange API calls; track subscription activity |

### Common Data Categories

Financial market data, alternative data (satellite imagery, social sentiment, weather), health and life sciences, geospatial, and public sector datasets.
