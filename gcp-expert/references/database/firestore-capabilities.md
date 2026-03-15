# Firestore — Capabilities Reference

## Purpose

Firestore is Google Cloud's serverless, fully managed document database. It provides hierarchical data storage (collections of documents), real-time data synchronization via listeners, offline support with local caching, and tight integration with Firebase client SDKs. Firestore scales automatically with no capacity provisioning.

---

## Firestore Modes

Firestore operates in one of two mutually exclusive modes, selected at database creation time. The mode cannot be changed after creation.

| Feature | Native Mode | Datastore Mode |
|---|---|---|
| Primary SDK | Firebase client SDKs + Google Cloud client libraries | Google Cloud client libraries (Datastore API) |
| Real-time listeners | Yes (`onSnapshot`) | No |
| Offline sync | Yes (mobile/web SDKs) | No |
| Subcollections | Yes | No |
| Collection group queries | Yes | No |
| Transactions | Yes (multi-document) | Yes |
| Queries | Rich (compound, range, in/not-in, array-contains) | Limited (no composite filters on multiple inequality fields) |
| Firebase Authentication integration | Yes | No |
| Firebase Security Rules | Yes | No |
| Legacy App Engine apps | No (use Datastore mode) | Yes |
| Multiple databases per project | Yes (up to 100) | No (one Datastore per project) |

**When to use Native mode**: New projects, mobile/web apps, real-time features, Firebase integration.
**When to use Datastore mode**: Legacy Google App Engine applications using the Datastore API; migrating from Cloud Datastore.

---

## Core Concepts

| Concept | Description |
|---|---|
| Database | A named Firestore instance within a project. Projects can have up to 100 databases. The default database is named `(default)`. |
| Collection | A container for documents. Collections are identified by a path: `users`, `orders`. Collections are created implicitly when a document is written to them. |
| Document | A unit of storage. A JSON-like object with string-keyed fields. Maximum size: 1 MB. Identified by a path: `users/alice`. |
| Field | A key-value pair in a document. Supported types: string, number (integer or float), boolean, null, timestamp, geopoint, bytes, reference, array, map. |
| Subcollection | A collection nested within a document: `users/alice/orders`. A document can have any number of subcollections. Subcollections are not returned when the parent document is fetched — they must be queried separately. |
| Collection group | All collections sharing the same name, regardless of their path. Enables `collectionGroup("orders")` queries across all users. Requires a collection group index. |
| Index | Single-field indexes are created automatically for each field. Composite indexes (multiple fields, or field + orderBy) must be defined in `firestore.indexes.json` and deployed. |
| Transaction | An atomic set of read-then-write operations. Reads must precede writes. Automatically retried on contention. Maximum 500 document writes per transaction. |
| Batch write | An atomic set of write operations (create, set, update, delete) without reads. Maximum 500 operations per batch. More efficient than individual writes. |
| Real-time listener | `onSnapshot()` — registers a callback that fires immediately with current data and again on every subsequent change. Firestore pushes updates to the client. |
| Security rules | Firebase Security Rules — declarative access control for client SDK access. Evaluated server-side. Not applicable to Admin SDK (server-side) access. |
| TTL policy | Time-to-live: automatically delete documents when a specified timestamp field passes the current time. Processed within 72 hours (not guaranteed to be exact). |

---

## Data Model

```
/users                    (collection)
  /alice                  (document)
    name: "Alice"
    email: "alice@example.com"
    created_at: Timestamp
    /orders               (subcollection)
      /order-001          (document)
        total: 99.99
        status: "shipped"
      /order-002          (document)
        total: 24.50
        status: "pending"
  /bob                    (document)
    name: "Bob"
    ...
```

**Document limits**:
- Maximum 1 MB per document (includes field names and values)
- Maximum 20,000 fields per document (including nested map fields counted separately)
- Maximum 1500 bytes for a document path

**Nested data**: Use embedded maps for data that is always accessed together. Use subcollections for data that might be queried or paginated independently.

---

## Indexes

### Single-Field Indexes (Automatic)

Firestore automatically creates single-field indexes for all document fields (ascending and descending). This supports simple equality and range queries on individual fields.

### Composite Indexes (Manual)

Required for:
- Queries with multiple `where` clauses on different fields
- Queries combining `where` + `orderBy` on different fields
- `collectionGroup` queries

Defined in `firestore.indexes.json`:
```json
{
  "indexes": [
    {
      "collectionGroup": "orders",
      "queryScope": "COLLECTION",
      "fields": [
        { "fieldPath": "userId", "order": "ASCENDING" },
        { "fieldPath": "createdAt", "order": "DESCENDING" }
      ]
    }
  ],
  "fieldOverrides": [
    {
      "collectionGroup": "logs",
      "fieldPath": "rawData",
      "indexes": []
    }
  ]
}
```

Deploy with Firebase CLI: `firebase deploy --only firestore:indexes`

### Index Exemptions

Disable automatic indexing for large string fields (improves write performance, reduces index storage costs):
- `fieldOverrides` with empty `indexes: []` disables all automatic indexes for that field.

---

## Query Capabilities

### Supported Query Operators

| Operator | Description |
|---|---|
| `==` | Equality |
| `!=` | Inequality (requires index; excludes documents where field is absent) |
| `<`, `<=`, `>`, `>=` | Range queries (all range operators must be on the same field) |
| `in` | Field value in a list (max 30 values) |
| `not-in` | Field value not in a list (max 10 values; excludes absent fields) |
| `array-contains` | Array field contains a specific value |
| `array-contains-any` | Array field contains any value from a list (max 30) |

### Query Limitations

- Only one `!=`, `not-in`, or `array-contains` per query.
- Range filters (`<`, `<=`, `>`, `>=`) can only apply to a single field per query.
- `orderBy` field must be the same as a range filter field (or added after).
- Cannot combine `array-contains` with `array-contains-any` in one query.
- No full-text search (use Algolia, Typesense, or BigQuery for text search).
- No aggregations (COUNT, SUM, AVG) in standard queries (Firestore Aggregation Queries support `count()`, `sum()`, `average()` as of 2023).

### Collection Group Queries

```javascript
// Query all 'orders' subcollections across all users
db.collectionGroup('orders')
  .where('status', '==', 'shipped')
  .orderBy('createdAt', 'desc')
  .limit(50)
  .get();
```

Requires a collection group index configured in `firestore.indexes.json`.

---

## Real-Time Listeners

```javascript
// Listen to a document
const unsubscribe = db.collection('users').doc('alice').onSnapshot(doc => {
  console.log('Current data:', doc.data());
});

// Listen to a query
const unsubscribe = db.collection('orders')
  .where('status', '==', 'pending')
  .onSnapshot(snapshot => {
    snapshot.docChanges().forEach(change => {
      if (change.type === 'added') console.log('New order:', change.doc.data());
      if (change.type === 'modified') console.log('Updated:', change.doc.data());
      if (change.type === 'removed') console.log('Removed:', change.doc.id);
    });
  });

// Unsubscribe when done
unsubscribe();
```

---

## TTL Policies

TTL policies automatically delete documents when a timestamp field exceeds the current time. Deletion is processed asynchronously (within 72 hours of the TTL timestamp passing).

```bash
# Create a TTL policy on a field named 'expireAt' in 'sessions' collection
gcloud firestore fields ttls update expireAt \
  --collection-group=sessions \
  --enable-ttl \
  --database="(default)"
```

In documents:
```json
{
  "sessionId": "abc123",
  "userId": "alice",
  "expireAt": "2024-04-01T00:00:00Z"
}
```

Documents where `expireAt < now` will be deleted automatically.

---

## Security Rules

Firebase Security Rules control read/write access for client SDK access (not Admin SDK):

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // Users can read/write their own document
    match /users/{userId} {
      allow read, write: if request.auth != null && request.auth.uid == userId;
    }
    // Anyone authenticated can read orders; only the owner can write
    match /users/{userId}/orders/{orderId} {
      allow read: if request.auth != null;
      allow write: if request.auth != null && request.auth.uid == userId;
    }
    // Public read for products
    match /products/{productId} {
      allow read: if true;
      allow write: if request.auth.token.admin == true;
    }
  }
}
```

Deploy rules: `firebase deploy --only firestore:rules`

---

## Pricing

| Operation | Cost (approximate; verify current pricing) |
|---|---|
| Document reads | $0.06 per 100,000 |
| Document writes | $0.18 per 100,000 |
| Document deletes | $0.02 per 100,000 |
| Storage | $0.18 per GB/month |
| Network egress | Standard GCP egress rates |

Free tier (Spark plan): 50,000 reads/day, 20,000 writes/day, 1 GB storage.

---

## Firestore vs. Bigtable vs. Cloud SQL vs. Datastore Mode

| Factor | Firestore Native | Bigtable | Cloud SQL | Datastore Mode |
|---|---|---|---|---|
| Data model | Document (JSON-like) | Wide-column | Relational | Entity (property bags) |
| Real-time sync | Yes | No | No | No |
| Offline support | Yes (client SDKs) | No | No | No |
| Query richness | Moderate (no joins) | Row-key and scan only | Full SQL | Limited |
| Max throughput | ~10,000 writes/s (soft) | Millions of ops/s | ~10,000–50,000 TPS | ~10,000 writes/s |
| Schema | Schemaless | Schemaless | Fixed schema | Schemaless |
| Use case | Mobile/web apps, real-time | Analytics, IoT, time-series | OLTP relational | Legacy GAE apps |
| Firebase integration | Full | None | None | Partial |

---

## Important Constraints

- **No joins**: Firestore does not support JOIN operations. Model your data to avoid joins (denormalization, embedding related data in documents).
- **1 MB document limit**: Documents with large arrays or embedded objects can hit this limit. Use subcollections for large lists.
- **Write rate per document**: Avoid updating a single document more than ~1 write/second sustained (can cause contention). Use distributed counters for high-frequency increments.
- **Transaction limits**: Max 500 document operations per transaction. Transactions time out after 270 seconds.
- **Index limits**: Max 200 composite indexes per database. Plan index requirements before deployment.
- **No full-text search**: Use an external search service (Algolia, Elasticsearch, BigQuery) integrated with Firestore triggers.
- **Consistency**: Firestore is strongly consistent for individual documents and queries. Real-time listeners deliver updates in order.
