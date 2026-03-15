# Amazon QLDB — CLI Reference
For service concepts, see [qldb-capabilities.md](qldb-capabilities.md).

## Amazon QLDB

```bash
# --- Ledgers ---
aws qldb create-ledger \
  --name my-ledger \
  --permissions-mode STANDARD \
  --no-deletion-protection \
  --tags Environment=dev

# STANDARD permissions mode enforces table-level IAM actions (PartiQLSelect, etc.)
# ALLOW_ALL grants any user with ledger access full permissions (legacy; not recommended)

aws qldb describe-ledger --name my-ledger

aws qldb list-ledgers

aws qldb update-ledger \
  --name my-ledger \
  --deletion-protection   # re-enable deletion protection

aws qldb update-ledger \
  --name my-ledger \
  --no-deletion-protection

aws qldb delete-ledger --name my-ledger
# Note: deletion-protection must be disabled before delete is accepted

# --- QLDB Streams (journal to Kinesis) ---
aws qldb stream-journal-to-kinesis \
  --ledger-name my-ledger \
  --stream-name my-ledger-stream \
  --role-arn arn:aws:iam::123456789012:role/QLDBStreamRole \
  --kinesis-configuration '{
    "StreamArn": "arn:aws:kinesis:us-east-1:123456789012:stream/my-qldb-stream",
    "AggregationEnabled": true
  }' \
  --inclusive-start-time 2024-01-01T00:00:00Z

# With explicit end time
aws qldb stream-journal-to-kinesis \
  --ledger-name my-ledger \
  --stream-name my-ledger-stream-ranged \
  --role-arn arn:aws:iam::123456789012:role/QLDBStreamRole \
  --kinesis-configuration '{
    "StreamArn": "arn:aws:kinesis:us-east-1:123456789012:stream/my-qldb-stream",
    "AggregationEnabled": false
  }' \
  --inclusive-start-time 2024-01-01T00:00:00Z \
  --exclusive-end-time 2024-06-30T23:59:59Z

aws qldb describe-journal-kinesis-stream \
  --ledger-name my-ledger \
  --stream-id abc123def456

aws qldb list-journal-kinesis-streams-for-ledger --ledger-name my-ledger

aws qldb cancel-journal-kinesis-stream \
  --ledger-name my-ledger \
  --stream-id abc123def456

# --- Digest and Cryptographic Verification ---
# Request the current digest (tip-of-chain hash) for the ledger
aws qldb get-digest --name my-ledger
# Returns: Digest (base64 SHA-256), DigestTipAddress (blockAddress), LedgerDigest

# Get a document revision and its Merkle proof
aws qldb get-revision \
  --name my-ledger \
  --block-address '{"strandId":"BlFTjlSXze9J","sequenceNo":14}' \
  --document-id "JoJoFromDocumentInsert" \
  --digest-tip-address '{"strandId":"BlFTjlSXze9J","sequenceNo":100}'
# Returns: Revision (Ion-encoded document), Proof (Merkle path hashes)

# Get a full journal block and its proof
aws qldb get-block \
  --name my-ledger \
  --block-address '{"strandId":"BlFTjlSXze9J","sequenceNo":14}' \
  --digest-tip-address '{"strandId":"BlFTjlSXze9J","sequenceNo":100}'
# Returns: Block (Ion-encoded block data), Proof (Merkle path to digest)

# --- Journal S3 Export ---
aws qldb export-journal-to-s3 \
  --name my-ledger \
  --inclusive-start-time 2024-01-01T00:00:00Z \
  --exclusive-end-time 2024-02-01T00:00:00Z \
  --s3-export-configuration '{
    "Bucket": "my-qldb-exports",
    "Prefix": "exports/my-ledger/",
    "EncryptionConfiguration": {
      "ObjectEncryptionType": "SSE_S3"
    }
  }' \
  --role-arn arn:aws:iam::123456789012:role/QLDBExportRole

aws qldb list-journal-s3-exports --name my-ledger

aws qldb list-journal-s3-exports-for-ledger --name my-ledger

aws qldb describe-journal-s3-export \
  --name my-ledger \
  --export-id export-abc123
```

---

## QLDB Shell (PartiQL Interactive Queries)

The QLDB shell (`qldb`) is a separate open-source CLI tool for running PartiQL statements interactively. Install via pip: `pip install qldbshell`.

```bash
# Start an interactive session against a ledger
qldb --ledger my-ledger --region us-east-1

# All commands below are run inside the shell (qldb> prompt)

# --- Table and Index Management ---
CREATE TABLE Vehicle

CREATE INDEX ON Vehicle (VIN)

DROP INDEX ON Vehicle (VIN)

DROP TABLE Vehicle

# --- Insert ---
INSERT INTO Vehicle VALUE {
  'VIN': '1HVBBAANXWH544237',
  'Type': 'Truck',
  'Make': 'Ford',
  'Model': 'F-150',
  'Year': 2020,
  'Color': 'Silver',
  'PendingPenaltyTicketAmount': 90.25
}

# --- Select (current state) ---
SELECT * FROM Vehicle WHERE VIN = '1HVBBAANXWH544237'

-- Select with metadata (documentId, version, txTime, txId)
SELECT v.*, m.metadata FROM Vehicle AS v BY m WHERE v.VIN = '1HVBBAANXWH544237'

# --- Update ---
UPDATE Vehicle SET Color = 'Red' WHERE VIN = '1HVBBAANXWH544237'

# Each UPDATE creates a new document revision; prior revisions are preserved in the journal

# --- Delete ---
DELETE FROM Vehicle WHERE VIN = '1HVBBAANXWH544237'

# Deletion creates a final "tombstone" revision; history remains accessible via history()

# --- History Function ---
-- All revisions for a specific document by documentId
SELECT * FROM history(Vehicle) AS h
WHERE h.metadata.id = 'JoJoFromDocumentInsert'

-- Revisions within a time range
SELECT h.data, h.metadata.txTime, h.metadata.version
FROM history(Vehicle, `2024-01-01T00:00:00Z`, `2024-12-31T23:59:59Z`) AS h
WHERE h.data.VIN = '1HVBBAANXWH544237'

# --- Transactions ---
-- QLDB shell wraps each statement in an implicit transaction
-- Use explicit BEGIN / COMMIT for multi-statement transactions:
BEGIN
INSERT INTO Vehicle VALUE {'VIN': 'AAA111', 'Type': 'Car'}
INSERT INTO Registration VALUE {'VIN': 'AAA111', 'LicensePlate': 'ZZZA1'}
COMMIT
```
