# Amazon QLDB — Capabilities Reference
For CLI commands, see [qldb-cli.md](qldb-cli.md).

## Amazon QLDB

**Purpose**: Fully managed ledger database that provides a transparent, immutable, and cryptographically verifiable transaction log owned by a central trusted authority; designed for systems of record where complete, auditable history is required.

### Core Concepts

| Concept | Description |
|---|---|
| **Ledger** | The top-level resource; a named QLDB database instance; contains tables and the journal |
| **Journal** | Append-only, immutable log of every committed transaction; the source of truth for all data in QLDB |
| **Document revision** | A single version of a document at a point in time; each update creates a new revision, old revisions are never deleted |
| **Committed view** | The current (latest) state of all documents across all tables; the default query target |
| **User data view** | The portion of the committed view containing only user-supplied fields, excluding QLDB system metadata |
| **History function** | PartiQL built-in `history()` that returns all revisions of a document over a specified time range |
| **Digest** | A SHA-256 hash representing the entire state of the journal at a given point; used as a trusted anchor for verification |
| **Proof** | A Merkle audit path that cryptographically links a specific document revision to a digest; returned by `GetRevision` |
| **Block address** | A pointer to a specific location in the journal, identified by strand ID and sequence number |
| **Strand** | A partition of the journal; current QLDB ledgers contain a single strand |
| **Sequence number** | A monotonically increasing integer identifying a block's position within a strand |

### Document Model

**Ion data format**: QLDB uses Amazon Ion, a superset of JSON that adds a rich type system (typed nulls, blobs, timestamps, annotations, S-expressions). Ion documents are stored and returned in text or binary format.

**Tables**: Schema-less containers for Ion documents within a ledger. Tables do not enforce a fixed schema; each document can have different fields.

**Indexes**: Each table supports up to 5 indexes. Indexes are defined on a single top-level field and are required for efficient equality lookups. Full-table scans are possible but not recommended for large tables.

**PartiQL queries**: QLDB uses PartiQL, an SQL-compatible query language extended to handle Ion's nested and semi-structured data. Supports `SELECT`, `INSERT`, `UPDATE`, `DELETE`, and the `history()` function.

```sql
-- Query current state
SELECT * FROM Vehicle WHERE VIN = '1HVBBAANXWH544237'

-- Query all historical revisions of a document
SELECT * FROM history(Vehicle, `2023-01-01T`, `2023-12-31T`) AS h
WHERE h.metadata.id = 'documentId123'

-- Insert a document
INSERT INTO Vehicle VALUE {
  'VIN': '1HVBBAANXWH544237',
  'Type': 'Truck',
  'Year': 2020
}

-- Update a document (creates a new revision; old revision preserved in journal)
UPDATE Vehicle SET Color = 'Red' WHERE VIN = '1HVBBAANXWH544237'
```

### Immutability and Cryptographic Verification

**Append-only journal**: Every committed transaction is written as a new block in the journal. Existing blocks are never modified or deleted. This is enforced at the storage layer, not just at the application layer.

**SHA-256 Merkle tree**: Each journal block contains the hash of its data and the hash of the previous block, forming a hash chain. Blocks within a strand are additionally organized into a Merkle tree, enabling efficient proof generation.

**Digest**: A `GetDigest` API call returns the current tip-of-chain hash representing the entire journal history. Store this hash externally (e.g., in S3, a separate system) to create a tamper-evident anchor.

**GetRevision + GetBlock proofs**:
- `GetRevision` returns a document revision along with a Merkle audit proof linking that revision to a digest you provide.
- `GetBlock` returns a journal block and its proof path.
- Any verifier can independently recompute the Merkle path to confirm the revision was recorded in the journal and has not been altered.

### QLDB Streams

**Purpose**: Streams the journal's committed changes in near-real-time to Amazon Kinesis Data Streams, enabling event-driven architectures, analytics pipelines, and downstream replication.

**Record types emitted to Kinesis**:

| Record Type | Description |
|---|---|
| **CONTROL** | Signals the start or completion of a stream; includes stream metadata |
| **BLOCK** | Represents a committed journal block; contains block metadata, transaction ID, and timestamp |
| **REVISION_DETAILS** | Contains the actual document revision data (table name, document ID, revision number, Ion document payload); one record per modified document per transaction |

**Key behaviors**:
- At-least-once delivery; consumers must handle deduplication using the `transactionId` and `documentId`.
- Stream covers a configurable time range (inclusive start time, optional end time).
- Multiple streams can be created for the same ledger simultaneously.
- No additional throughput impact on the ledger's query performance.

### Concurrency Model

**Optimistic concurrency control (OCC)**: QLDB assumes conflicts are rare. Transactions proceed without acquiring locks upfront; at commit time, QLDB validates that no other transaction modified the same documents since the transaction began. If a conflict is detected, the transaction is rejected with an `OccConflictException` and the application must retry.

**Document-level locking**: The OCC conflict check operates at the document level, not the table level, allowing high concurrency across different documents in the same table.

**Transaction limits**: Each transaction can modify up to 40,000 documents and may run for a maximum of 30 seconds before being automatically aborted.

### IAM Integration

QLDB uses standard IAM policies for access control. There is no database-level user/password system.

**Ledger-level actions**:
- `qldb:CreateLedger`, `qldb:DescribeLedger`, `qldb:ListLedgers`, `qldb:DeleteLedger`
- `qldb:UpdateLedger`, `qldb:GetDigest`
- `qldb:StreamJournalToKinesis`, `qldb:DescribeJournalKinesisStream`, `qldb:CancelJournalKinesisStream`
- `qldb:ExportJournalToS3`, `qldb:DescribeJournalS3Export`, `qldb:ListJournalS3Exports`
- `qldb:GetBlock`, `qldb:GetRevision`

**Table-level actions** (specified via resource ARN with `/table/<tableName>`):
- `qldb:PartiQLSelect`, `qldb:PartiQLInsert`, `qldb:PartiQLUpdate`, `qldb:PartiQLDelete`
- `qldb:PartiQLHistoryFunction`
- `qldb:CreateTable`, `qldb:DropTable`, `qldb:CreateIndex`, `qldb:DropIndex`

**Example policy** (read-only access to a specific table):
```json
{
  "Effect": "Allow",
  "Action": ["qldb:PartiQLSelect", "qldb:PartiQLHistoryFunction"],
  "Resource": "arn:aws:qldb:us-east-1:123456789012:ledger/my-ledger/table/Vehicle"
}
```

### Use Cases

- **Financial ledger**: Immutable record of all financial transactions; regulators can verify no data was altered or deleted after the fact
- **Supply chain**: Track provenance of goods at each step; cryptographic proofs confirm chain of custody has not been tampered with
- **Healthcare records**: Maintain complete, auditable history of patient record changes; HIPAA-eligible service
- **DMV / title records**: Vehicle ownership history where each transfer is recorded permanently; state agencies can verify title lineage
- **HR and compliance systems**: Audit trail of employee record changes, access grants, and policy acknowledgements

### Comparison: QLDB vs Alternatives

| Dimension | QLDB | Managed Blockchain (Hyperledger) | DynamoDB + audit table | RDS + triggers |
|---|---|---|---|---|
| **Trust model** | Single central authority owns ledger | Decentralized multi-party consensus | Application-enforced; no system-level guarantee | Application-enforced; no system-level guarantee |
| **Immutability** | Enforced at storage layer; journal cannot be altered | Enforced by consensus across nodes | Mutable; audit table can be updated/deleted by privileged user | Mutable; audit records can be modified |
| **Cryptographic verification** | Built-in digest + Merkle proof; independently verifiable | Built-in per blockchain protocol | None | None |
| **Query language** | PartiQL (SQL-compatible) | Chaincode / Fabric SDK | DynamoDB PartiQL / SDK | SQL |
| **Operational overhead** | Fully serverless; no instances to manage | Manage peer nodes, orderers, channels | Manage table design and audit Lambda | Manage RDS instance, trigger logic |
| **Best for** | Single-owner systems requiring tamper-evident audit trail | Multi-organization workflows where no single party is trusted | Simple change logging where cryptographic proof is not required | Relational workloads with basic audit needs |
