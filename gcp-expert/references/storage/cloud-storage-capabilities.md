# Cloud Storage — Capabilities Reference

CLI reference: [cloud-storage-cli.md](cloud-storage-cli.md)

## Purpose

Unified object storage for developers and enterprises. Cloud Storage stores and serves any amount of data globally with high durability (11 nines / 99.999999999%), strong consistency, and a global edge network. It is the foundation for data lakes, backup, static web hosting, ML datasets, data sharing, and archive.

---

## Core Concepts

| Concept | Description |
|---|---|
| Bucket | Named container for objects. Bucket names are globally unique across all GCP projects. Region/multi-region is set at creation and cannot be changed. |
| Object | Any file stored in a bucket. Consists of data (arbitrary bytes) + metadata (name, content type, custom metadata, etc.). Max size: 5 TB. |
| Storage class | Policy attached to a bucket or individual object that determines storage cost and access cost trade-offs. |
| Bucket location | Geographic region(s) where data is stored: single-region, dual-region, or multi-region. |
| IAM | Identity and Access Management for bucket-level and project-level access. Preferred for all new buckets (`uniformBucketLevelAccess`). |
| ACL (Access Control List) | Legacy per-object or per-bucket access grants. Avoid for new buckets; use IAM with uniform bucket-level access. |
| Object versioning | When enabled, overwritten or deleted objects are retained as non-current versions. Enables recovery from accidental deletion. |
| Lifecycle rule | Policy-based automation to transition objects between storage classes or delete objects based on age, number of versions, storage class, etc. |
| Retention policy | Minimum retention duration for objects in a bucket. Objects cannot be deleted or modified before the retention period expires. Supports compliance lock (immutable). |
| CORS | Cross-Origin Resource Sharing configuration on buckets for browser-based access to bucket objects from a different domain. |
| Signed URL | Time-limited URL granting temporary access (read or write) to a specific object without requiring a Google account. |
| CMEK | Customer-Managed Encryption Keys. Encrypts bucket data using a key in Cloud KMS you manage. Default: Google-managed encryption. |
| Requester Pays | When enabled, the requester (not the bucket owner) pays for data access and egress costs. Used for large public datasets. |
| Pub/Sub notifications | Bucket notifications sent to a Pub/Sub topic when objects are created, deleted, or have metadata updated. |
| HMAC keys | Hash-based Message Authentication Code keys for authenticating requests using the AWS S3-compatible XML API. |
| Soft delete | When enabled (default: 7 days), deleted objects are retained in a soft-deleted state and can be restored. Provides protection beyond versioning. |
| Object holds | Event-based hold or temporary hold prevents deletion of specific objects. Used for legal holds or compliance. |

---

## Storage Classes

| Storage Class | Min Storage Duration | Access Frequency | Per-Operation Cost | Ideal For |
|---|---|---|---|---|
| Standard | None | Frequent (multiple times/day) | Low | Active data, web apps, streaming, data analytics |
| Nearline | 30 days | Infrequent (~once per month) | Medium | Backups accessed monthly, disaster recovery data |
| Coldline | 90 days | Rare (~once per quarter) | Higher | Archival data accessed a few times per year |
| Archive | 365 days | Very rare (~once per year) | Highest | Regulatory archives, long-term cold storage |

**Cost model**: Standard has highest storage price and lowest access cost. Archive has lowest storage price and highest access cost. Early deletion fees apply if an object is deleted before its minimum storage duration.

**Autoclass**: an optional bucket feature that automatically transitions objects to the most cost-effective storage class based on actual access patterns (no lifecycle rules required). Best for mixed-access buckets.

---

## Bucket Location Types

| Location Type | Description | Redundancy | Use Case |
|---|---|---|---|
| Single-region | Data in one specific region (e.g., `us-central1`, `europe-west1`) | Replicated within the region | Lowest latency to compute in same region; lowest cost for regional workloads |
| Dual-region | Data replicated across two specific regions (e.g., `nam4` = Iowa + South Carolina; `eur4` = Netherlands + Finland) | Synchronous replication; survives region failure | High availability for regional failover; Turbo Replication option (15-min RPO guaranteed) |
| Multi-region | Data replicated across multiple regions in a continent (`us`, `eu`, `asia`) | At least two regions; survives region failure | Global distribution; serving objects worldwide; highest availability |

**Note**: multi-region `us` stores data in the continental US; `eu` stores in European Union countries; `asia` stores in Asia-Pacific.

---

## Key Features

### Strong Global Consistency (since November 2020)
All Cloud Storage operations (read-your-writes, list-after-write, delete-then-list) are strongly consistent globally. There is no eventual consistency window for metadata or data reads after any write operation.

### Uniform Bucket-Level Access
When enabled, ACLs are disabled and all access is controlled exclusively through IAM. **Required for all new buckets**. Enables consistent IAM auditing, simpler access management, and VPC Service Controls compatibility.

### Object Versioning
When enabled on a bucket, every overwrite or delete creates a non-current version retained in the bucket. Non-current versions can be listed, downloaded, or restored. Billing applies to non-current versions. Use lifecycle rules to expire old versions.

### Object Holds
- **Temporary hold**: prevents deletion and modification. Cleared manually.
- **Event-based hold**: cleared when a specific event occurs (e.g., contract expiration). Clears must be done explicitly via API.

### Retention Policies
Set a minimum retention period (seconds, days, years). Objects cannot be deleted or overwritten until the period expires. Lock the policy to make it immutable (for regulatory compliance like SEC Rule 17a-4).

### Soft Delete
Retains deleted or overwritten objects for a configurable window (default 7 days, max 90 days). Objects are transparently recovered within the retention window. Bucket-level setting; incurs additional storage cost during the retention period.

### Signed URLs
Generate time-limited access URLs using a service account key or Workload Identity Federation. Supports GET, PUT, DELETE. Common uses: pre-signed upload URLs for clients, temporary download links for private content.

```
https://storage.googleapis.com/BUCKET_NAME/OBJECT_NAME?X-Goog-Algorithm=...&X-Goog-Expires=3600&X-Goog-Signature=...
```

### HMAC Keys
Allows applications using the AWS S3 SDK or XML API to authenticate to Cloud Storage using HMAC-SHA256. Associate HMAC keys with a service account. Useful for migrating S3-compatible workloads without SDK changes.

### Pub/Sub Notifications
Configure a bucket to publish notifications to a Pub/Sub topic when:
- Object finalized (created or overwritten)
- Object deleted
- Object archived (moved to non-current version)
- Object metadata updated

Used to trigger Cloud Functions, Cloud Run, or other event-driven workflows on file uploads.

---

## IAM vs ACLs

| Feature | IAM (Uniform Bucket-Level Access) | ACLs (Legacy) |
|---|---|---|
| Scope | Bucket-level and project-level | Per-bucket or per-object |
| Recommendation | Preferred for all new buckets | Legacy; avoid for new workloads |
| VPC Service Controls compatibility | Yes | No |
| Object-level permissions | No (bucket-level only) | Yes (per-object ACLs) |
| IAM Conditions support | Yes | No |
| Audit logging | Consistent | Less predictable |

**Common IAM roles for Cloud Storage:**
- `roles/storage.objectViewer` — read objects, list objects
- `roles/storage.objectCreator` — create/overwrite objects (no delete, no read)
- `roles/storage.objectAdmin` — full object access (read, write, delete)
- `roles/storage.admin` — full control including bucket IAM, metadata
- `roles/storage.legacyBucketReader` — read bucket metadata and list objects (used with ACLs)

---

## Lifecycle Rules

Lifecycle rules automate object management. Each rule has **conditions** and an **action**.

### Conditions
| Condition | Description |
|---|---|
| `age` | Object age in days since creation |
| `createdBefore` | Objects created before a specific date |
| `isLive` | `true` = current version; `false` = non-current versions |
| `matchesStorageClass` | Only apply to objects with specified storage class |
| `numNewerVersions` | Number of newer versions of the same object |
| `daysSinceNoncurrentTime` | Days since object became non-current |
| `matchesPrefix` | Object name prefix |
| `matchesSuffix` | Object name suffix |

### Actions
| Action | Description |
|---|---|
| `Delete` | Permanently delete the object |
| `SetStorageClass` | Transition to a different storage class |
| `AbortIncompleteMultipartUpload` | Cancel incomplete multipart uploads after N days |

### Example Lifecycle Policy (JSON)
```json
{
  "lifecycle": {
    "rule": [
      {
        "action": {"type": "SetStorageClass", "storageClass": "NEARLINE"},
        "condition": {"age": 30, "matchesStorageClass": ["STANDARD"]}
      },
      {
        "action": {"type": "SetStorageClass", "storageClass": "COLDLINE"},
        "condition": {"age": 90, "matchesStorageClass": ["NEARLINE"]}
      },
      {
        "action": {"type": "Delete"},
        "condition": {"age": 365}
      },
      {
        "action": {"type": "Delete"},
        "condition": {"isLive": false, "numNewerVersions": 3}
      }
    ]
  }
}
```

---

## Transfer Options

| Method | Best For | Throughput |
|---|---|---|
| `gcloud storage cp` | Small to medium transfers, scripting | Limited by client bandwidth |
| `gsutil -m cp` | Medium transfers, parallel upload | Parallelized, better for large files |
| `gcloud storage rsync` | Sync local directory to/from GCS | Parallel, skip unchanged files |
| Storage Transfer Service | Scheduled large transfers, cross-cloud (S3→GCS, Azure→GCS), on-prem to GCS | Google-managed, high throughput |
| Transfer Appliance | Offline transfer of petabyte-scale datasets | Physical shipping; bypasses internet bandwidth |
| Dataflow | Transfer with transformation (ETL during transfer) | Depends on Dataflow job |

---

## When to Use Storage Classes

| Scenario | Recommended Class |
|---|---|
| Serving website assets, app data, frequently read files | Standard |
| Database backups kept for 30+ days, accessed for recovery | Nearline |
| Compliance archives accessed occasionally | Coldline |
| Legal archives, multi-year regulatory retention, accessed rarely | Archive |
| Mixed access patterns (some hot, some cold) | Autoclass |

---

## Important Patterns & Constraints

- **Bucket name is global and permanent**: choose carefully. Once deleted, the name can be claimed by anyone else (with a delay). Use project IDs as prefixes (e.g., `my-project-prod-assets`).
- **Object naming**: avoid sequential prefixes (e.g., `log-000001`, `log-000002`) for high-throughput workloads; GCS shards based on key prefix and sequential names can create hotspots. Use random prefixes or hashed prefixes for high-QPS workloads.
- **Maximum object size**: 5 TB. Use multipart uploads (composite objects or XML API multipart) for files >5 GB.
- **Eventual consistency for list after delete**: after deleting an object, list operations may briefly still show it. For applications relying on list results, build in retry or consistency checks.
- **Cross-region egress charges**: data transferred between GCP regions incurs egress costs. Store buckets in the same region as compute workloads when possible.
- **Default encryption**: all objects encrypted at rest by default with Google-managed keys. CMEK available for additional control.
- **Versioning + lifecycle**: always pair versioning with lifecycle rules to expire non-current versions; otherwise storage costs grow unboundedly.
- **Public access prevention**: enable `publicAccessPrevention` on buckets that should never be public. Prevents accidental `allUsers` / `allAuthenticatedUsers` grants.
- **Signed URLs expire**: test signed URL generation with realistic TTLs. Do not share very long-lived signed URLs as they can be leaked.
- **gsutil vs gcloud storage**: `gcloud storage` is the newer, recommended CLI; `gsutil` is legacy. Both work but `gcloud storage` has better performance and output formatting.
- **Composite objects**: up to 32 component objects can be composed into one; used for parallel uploads of large files. Composed objects are treated as a single object.
