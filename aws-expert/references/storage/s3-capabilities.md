# AWS S3 — Capabilities Reference
For CLI commands, see [s3-cli.md](s3-cli.md).

## Amazon S3

**Purpose**: Object storage service offering industry-leading scalability, durability (11 nines), and availability for any amount of data; serves as the foundation for data lakes, backups, static websites, and application assets.

### Storage Classes

| Storage Class | Use Case | Min Duration | Min Billable Size | Retrieval | AZs |
|---|---|---|---|---|---|
| **S3 Standard** | Frequently accessed data | None | None | Milliseconds | ≥3 |
| **S3 Express One Zone** | Latency-sensitive (<10ms); 10x faster than Standard | None | None | Single-digit ms | 1 |
| **S3 Intelligent-Tiering** | Unknown/changing access patterns; auto-moves between tiers | None | None | ms–hours (tier-dependent) | ≥3 |
| **S3 Standard-IA** | Infrequent access; primary copy; quick retrieval required | 30 days | 128 KB | Milliseconds | ≥3 |
| **S3 One Zone-IA** | Infrequent, recreatable data; CRR replicas | 30 days | 128 KB | Milliseconds | 1 |
| **S3 Glacier Instant Retrieval** | Archives accessed quarterly | 90 days | 128 KB | Milliseconds | ≥3 |
| **S3 Glacier Flexible Retrieval** | Archives accessed annually; minutes-to-hours OK | 90 days | N/A (40 KB overhead) | Minutes–hours | ≥3 |
| **S3 Glacier Deep Archive** | Compliance/regulatory; <1x/year access | 180 days | N/A (40 KB overhead) | Hours | ≥3 |

**S3 Intelligent-Tiering tiers**: Frequent Access → (30 days inactive) → Infrequent Access → (90 days inactive) → Archive Instant Access. Optional: Archive Access (90+ days) and Deep Archive Access (180+ days) must be activated manually. No retrieval fees; small monthly monitoring fee per object. Objects <128 KB always remain in Frequent Access tier.

### Key Concepts

| Concept | Description |
|---|---|
| **Bucket** | Container for objects; globally unique name; created in a specific region; private by default |
| **Object** | A file plus metadata; uniquely identified by bucket + key + version ID |
| **Key** | Unique identifier (path) for an object within a bucket |
| **Versioning** | Preserve, retrieve, and restore every version of an object; must be explicitly enabled |
| **Block Public Access** | Account- or bucket-level setting; blocks all public access; enabled by default |
| **S3 Access Points** | Named network endpoints with dedicated access policies; can restrict to a specific VPC |
| **Object Lambda** | Intercept S3 GET/HEAD/LIST requests to transform data inline (filter rows, redact PII, resize images) |
| **S3 Select** | SQL-like expressions to retrieve a subset of data from an object (CSV, JSON, Parquet) without downloading the full object |
| **Requester Pays** | Requester (not bucket owner) pays data transfer and request costs; owner still pays storage |
| **Presigned URL** | Time-limited URL granting temporary access to a private object without AWS credentials |
| **Multipart Upload** | Upload large objects in parts (required for >5 GB; recommended for >100 MB) |
| **Strong consistency** | Read-after-write consistency for PUT/DELETE on single objects; eventual for bucket listing after bucket deletion |

### Bucket Types

| Type | Description |
|---|---|
| **General Purpose** | Default; global or regional namespace; all storage classes except Express One Zone |
| **Directory Bucket** | For S3 Express One Zone; hierarchical prefix structure; 100/account by default; public access always blocked |
| **Table Bucket** | Apache Iceberg format for analytics/ML; queryable via Athena, Redshift, Spark |
| **Vector Bucket** | Purpose-built for vector storage/search; integrates with Bedrock and OpenSearch |

### Access Control

| Method | Description |
|---|---|
| **Bucket policy** | Resource-based JSON policy; 20 KB limit; preferred for most use cases |
| **IAM policy** | Identity-based; controls AWS principal access; use with bucket policy for cross-account |
| **ACLs** | Legacy; not recommended; disabled by default via S3 Object Ownership |
| **Block Public Access** | Overrides bucket policies and ACLs that would grant public access; enforce at account level |
| **S3 Access Points** | Delegate access control for shared datasets; restrict by VPC or network origin |

### Key Features

| Feature | Description |
|---|---|
| **CRR (Cross-Region Replication)** | Replicate objects to a bucket in a different region; requires versioning on both buckets |
| **SRR (Same-Region Replication)** | Replicate within the same region; log aggregation, data residency, live replication |
| **Lifecycle rules** | Transition objects to lower-cost classes or expire/delete them; applied to existing and new objects; bucket policies cannot prevent lifecycle deletions |
| **Event notifications** | Trigger SNS, SQS, Lambda, or EventBridge on object-level events (PUT, DELETE, etc.) |
| **S3 Object Lock** | WORM storage; prevent deletion/overwrite for fixed retention period or indefinitely; Compliance or Governance mode |
| **Versioning** | When enabled, DELETE creates a delete marker rather than removing the object |
| **S3 Batch Operations** | Run operations (copy, invoke Lambda, restore) across billions of objects with a single API call |
| **CORS** | Configure cross-origin resource sharing for browser-based applications accessing S3 |
| **Static website hosting** | Serve a bucket as a website; set index and error documents; supports redirect rules |
| **Storage Lens** | 60+ usage and activity metrics aggregated across org/account/region/bucket/prefix |
| **Storage Class Analysis** | Analyze access patterns to identify data suitable for transition to Standard-IA |
| **S3 Inventory** | Scheduled report of objects and metadata (daily or weekly); export to S3 as CSV/ORC/Parquet |
| **Server-side encryption** | SSE-S3 (default), SSE-KMS (CMK), SSE-C (customer-provided key) |

### Important Patterns & Constraints

- Objects not transitioned from Standard-IA or One Zone-IA before 30 days are charged for the full 30 days
- Glacier Flexible Retrieval and Deep Archive objects must be **restored** to Standard before access; restore creates a temporary copy
- Last-writer-wins semantics for concurrent PUTs; no atomic cross-key updates
- Bucket names must be globally unique (3–63 lowercase characters, no underscores)
- Maximum object size: 5 TB; single PUT limit: 5 GB
- Lifecycle billing changes take effect immediately when objects become eligible, even if the action is delayed

---

## Amazon S3 Vectors

**Purpose**: Purpose-built vector storage within S3 for storing and querying billions of vector embeddings at scale; enables approximate nearest neighbor (ANN) similarity search for AI/ML applications such as RAG pipelines, semantic search, and recommendations.

### Key Concepts

| Concept | Description |
|---|---|
| **Vector bucket** | New S3 bucket type purpose-built for vector workloads; Block Public Access always enabled; uses the `s3vectors` IAM namespace |
| **Vector index** | Organized within a vector bucket; stores vector embeddings; no infrastructure provisioning required; automatically optimizes for price/performance as data scales |
| **Vector** | A float32 embedding with a unique key and optional metadata key-value pairs; strongly consistent (immediately readable after write) |
| **Metadata** | Filterable or non-filterable key-value pairs attached to each vector; filterable metadata is indexed for use in query filters |
| **ANN query** | Approximate nearest neighbor search returning the top-K most similar vectors; supports optional metadata filter expressions |

### Supported Distance Metrics

| Metric | Description |
|---|---|
| **Cosine** | Measures angular similarity between vectors; suitable for text/document embeddings |
| **Euclidean** | Measures straight-line (L2) distance; suitable for image and dense embeddings |

### Key Features

| Feature | Description |
|---|---|
| **Elastic scale** | Stores up to 2 billion vectors per index; 10,000 indexes per bucket; 10,000 buckets per region per account |
| **Sub-second queries** | ~100 ms latency for ANN queries on frequently accessed indexes |
| **Metadata filtering** | All metadata filterable by default; use filter expressions in `QueryVectors` to narrow results |
| **Strong consistency** | Vectors immediately available after `PutVectors`; no eventual consistency lag |
| **Encryption** | At rest via SSE-S3 or SSE-KMS; bucket-level and index-level encryption settings; immutable after creation |
| **Access control** | IAM policies and SCPs using the `s3vectors` service namespace; bucket-level or index-level policies |

### Integrations

| Integration | Description |
|---|---|
| **Amazon Bedrock Knowledge Bases** | Use S3 vector indexes as the vector store for RAG applications |
| **SageMaker Unified Studio** | Develop and test knowledge bases backed by S3 Vectors |
| **Amazon OpenSearch Service** | Export S3 vector index snapshots to OpenSearch Serverless for hybrid search, aggregations, or high-QPS workloads |

### Pricing Model

Pay-per-use: charges for vectors stored (per vector per month) and per query (per `QueryVectors` request). No provisioned capacity or idle infrastructure costs.

### Important Constraints

- Distance metric, dimension, vector bucket name, index name, and non-filterable metadata keys are **immutable after creation** — plan schema carefully
- Vector dimensions: 1–4,096 (must match the embedding model output; e.g., Amazon Titan Text Embeddings V2 outputs 1,024 dimensions)
- Filterable metadata per vector: up to 2 KB; total metadata (filterable + non-filterable): up to 40 KB
- `PutVectors` / `DeleteVectors`: up to 500 vectors per call; up to 2,500 vectors/second per index
- `QueryVectors` top-K: maximum 100 results per request
- All DRA-linked data is read-only from the cache's perspective (no write-back to S3 or NFS from S3 Vectors)
