# Security and Trust in Flow Systems

Reference for authentication (OAuth2, JWT for events), authorization patterns, event signing, data sovereignty, privacy in event streams, compliance (GDPR), and audit trails.

---

## The Security Challenge in Event-Driven Systems

Traditional request/response security is well understood: authenticate the caller, authorize the operation, done. Event-driven systems introduce new challenges:

- **Producer identity**: How does a consumer verify an event actually came from the claimed producer?
- **Integrity**: How does a consumer know the event wasn't modified in transit or storage?
- **Authorization at scale**: How do you control which consumers can access which event streams without a central gatekeeper per event?
- **Data sovereignty**: Event streams cross regional and organizational boundaries — who controls the data?
- **Audit trail**: With data flowing asynchronously, how do you reconstruct what happened and when?

---

## Authentication

### Producer Authentication to Broker

**TLS Mutual Authentication (mTLS)**
Both producer and broker authenticate each other with certificates. The most secure option for service-to-service connections.

```bash
# Kafka producer TLS configuration
security.protocol=SSL
ssl.keystore.location=/etc/kafka/certs/producer-keystore.jks
ssl.keystore.password=${KEYSTORE_PASSWORD}
ssl.truststore.location=/etc/kafka/certs/ca-truststore.jks
ssl.truststore.password=${TRUSTSTORE_PASSWORD}
```

**SASL Authentication**
Kafka supports several SASL mechanisms:
- `SASL_PLAIN`: Username/password (TLS required to avoid plaintext credential exposure)
- `SASL_SCRAM-SHA-256/512`: Salted Challenge Response Authentication — password hash-based, more secure than PLAIN
- `SASL_GSSAPI`: Kerberos — for enterprise/LDAP-integrated environments
- `SASL_OAUTHBEARER`: OAuth 2.0 token-based — recommended for cloud-native environments

```properties
# Kafka SASL OAUTHBEARER configuration
security.protocol=SASL_SSL
sasl.mechanism=OAUTHBEARER
sasl.login.callback.handler.class=org.apache.kafka.common.security.oauthbearer.OAuthBearerLoginCallbackHandler
sasl.oauthbearer.token.endpoint.url=https://auth.acme.com/oauth2/token
sasl.jaas.config=org.apache.kafka.common.security.oauthbearer.OAuthBearerLoginModule required \
    clientId="kafka-producer-orders" \
    clientSecret="${CLIENT_SECRET}" \
    scope="kafka.write";
```

**API Keys**
For simpler setups (Confluent Cloud, managed services), API key + secret pairs per application:
```bash
# Confluent Cloud API key per producer/consumer application
KAFKA_API_KEY=ABCDE12345
KAFKA_API_SECRET=longRandomSecret
```

### Consumer Authentication
Same mechanisms apply. Key principle: **each producer and consumer service has its own credentials** — no shared service accounts.

### JWT for Events
JWT (JSON Web Tokens) can be used as part of the event payload to:
1. Assert the identity of the event source
2. Carry authorization claims with the event
3. Enable stateless verification by consumers

```json
{
  "specversion": "1.0",
  "type": "com.acme.orders.order.placed",
  "id": "evt-12345",
  "source": "https://orders.acme.com",
  "time": "2024-01-15T14:23:01.123Z",
  "datacontenttype": "application/json",
  "authorization": "Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...",
  "data": {
    "orderId": "ord-12345",
    "customerId": "cust-789"
  }
}
```

The JWT in the `authorization` field (or custom extension `eventjwt`) allows consumers to:
- Verify the event came from a trusted source (via signature verification)
- Extract claims without calling an authorization server
- Support event replay (JWT includes expiry — replay within window is valid)

**JWT Event Token Claims**:
```json
{
  "iss": "https://orders.acme.com",          // Issuer (event producer)
  "sub": "orders-service",                    // Subject (producing service)
  "aud": ["kafka://events.acme.com"],         // Audience (event bus)
  "iat": 1705329781,                          // Issued at
  "exp": 1705416181,                          // Expiry (24 hours)
  "jti": "evt-12345",                         // JWT ID = event ID
  "event_type": "com.acme.orders.order.placed",
  "correlation_id": "saga-001"
}
```

### OAuth 2.0 for Event System Access

**Client Credentials Flow** (service-to-service):
```
Producer Service → Authorization Server
                   (client_credentials grant)
                   ← Access Token (JWT)

Producer Service → Kafka (SASL OAUTHBEARER with token)
                   Broker validates token signature
                   Broker checks token scopes for topic access
```

**Scopes for Event Access**:
```
kafka.orders.write       → produce to orders topics
kafka.orders.read        → consume from orders topics
kafka.inventory.write    → produce to inventory topics
kafka.*.read             → consume from any topic (admin only)
```

---

## Authorization Patterns

### Kafka ACLs (Access Control Lists)
Kafka's native authorization mechanism:

```bash
# Grant OrderService write access to orders-* topics
kafka-acls.sh --bootstrap-server kafka:9092 \
  --add \
  --allow-principal User:orders-service \
  --operation Write \
  --topic 'orders-' --resource-pattern-type prefixed

# Grant ShipmentService read access to orders-* topics
kafka-acls.sh --bootstrap-server kafka:9092 \
  --add \
  --allow-principal User:shipment-service \
  --operation Read \
  --topic 'orders-' --resource-pattern-type prefixed \
  --operation Read \
  --group shipment-service     # Also needs consumer group ACL
```

**Kafka ACL granularity**:
- Per-topic, per-operation (Read, Write, Describe, Create, Delete, Alter)
- Per-consumer-group (Read = join group)
- Per-cluster (Describe, Alter, ClusterAction)
- Per-transactional ID (Write = use transactions)

### RBAC (Role-Based Access Control)
Confluent Platform and other enterprise Kafka distributions support RBAC:

```yaml
# Confluent RBAC role binding
apiVersion: platform.confluent.io/v1beta1
kind: KafkaRoleBinding
metadata:
  name: order-service-producer
spec:
  principal:
    name: orders-service
    type: User
  role: DeveloperWrite
  resourcePatterns:
    - name: orders-
      resourceType: Topic
      patternType: Prefixed
```

### Attribute-Based Access Control (ABAC)
For fine-grained control based on event attributes (not just topic names):
- Consumer A can read order events only for their geographic region
- Consumer B can read customer events only for non-PII fields

ABAC requires enforcement at either:
1. **Topic level**: Separate topics per region/tier (blunt, effective)
2. **Message filtering**: Consumer-side filtering (no enforcement)
3. **Proxy layer**: Kafka proxy that filters messages based on consumer identity claims

---

## Event Signing and Integrity

### Why Sign Events?
Event signing proves:
- **Authenticity**: The event was produced by the claimed producer
- **Integrity**: The event payload was not modified after signing

Without signing, a compromised event broker could alter event payloads, and consumers would have no way to detect tampering.

### Signing Approaches

**Asymmetric Key Signing (Recommended)**
Producer signs events with its private key; consumers verify with producer's public key:

```python
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
import json
import base64

def sign_event(event: dict, private_key) -> dict:
    """Sign a CloudEvent and add signature to extensions"""
    # Canonical representation (deterministic serialization)
    canonical = json.dumps({
        "specversion": event["specversion"],
        "id": event["id"],
        "source": event["source"],
        "type": event["type"],
        "time": event["time"],
        "data": event["data"]
    }, sort_keys=True).encode()

    # Sign with RSA-PSS
    signature = private_key.sign(
        canonical,
        padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH),
        hashes.SHA256()
    )

    event["eventsignature"] = base64.b64encode(signature).decode()
    event["eventsigningkeyid"] = "orders-service-key-v3"   # Key ID for key rotation
    return event

def verify_event(event: dict, public_key) -> bool:
    """Verify event signature"""
    signature = base64.b64decode(event.get("eventsignature", ""))
    canonical = json.dumps({...}, sort_keys=True).encode()
    try:
        public_key.verify(signature, canonical, ...)
        return True
    except Exception:
        return False
```

**HMAC Signing (Symmetric — for webhook delivery)**
Commonly used for webhook event delivery (shared secret between producer and consumer):

```python
import hmac
import hashlib

def sign_webhook(payload: bytes, secret: str) -> str:
    """GitHub-style webhook signing"""
    signature = hmac.new(
        secret.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()
    return f"sha256={signature}"

# Delivery header:
# X-Hub-Signature-256: sha256=<hex-digest>
```

**Key Rotation**
- Include `eventsigningkeyid` extension to identify which key was used
- Publish public keys via JWKS (JSON Web Key Sets) endpoint
- Consumers fetch and cache current public keys
- On key rotation, consumers re-fetch JWKS

---

## Data Sovereignty and Privacy

### Data Sovereignty Challenges
Events flowing across regional, organizational, or national boundaries raise sovereignty questions:
- Can customer PII legally flow to a different jurisdiction?
- Who "owns" the event data once it's on a shared event mesh?
- Can partner organizations access customer event data?

### Data Minimization in Events
**Principle**: Include only the minimum data necessary for consumers to act on the event.

```json
// Too much PII in notification event
{
  "type": "com.acme.orders.order.placed",
  "data": {
    "orderId": "ord-12345",
    "customerName": "Jane Smith",          // Not needed for order processing
    "customerEmail": "jane@example.com",   // Not needed for inventory check
    "creditCardLast4": "1234",             // Definitely not needed
    "shippingAddress": {...}               // Not needed for payment event
  }
}

// Minimized event
{
  "type": "com.acme.orders.order.placed",
  "data": {
    "orderId": "ord-12345",
    "customerId": "cust-789",             // Opaque reference; consumer fetches if needed
    "totalAmount": 59.98,
    "currency": "USD",
    "shippingRegion": "US-EAST"           // Region only, not full address
  }
}
```

### PII in Event Streams — Strategies

**Tokenization**
Replace PII with opaque tokens; maintain a secure token→PII mapping:
```json
{
  "customerId": "cust-789",         // Opaque token
  "emailToken": "tok-email-abc123"  // Token mapped to real email in secure vault
}
```
Consumers needing the actual email call the tokenization service with the token. Event stream never contains PII.

**Claim Check Pattern for PII**
Store PII in a secure, access-controlled store; include a reference in the event:
```json
{
  "orderId": "ord-12345",
  "customerPiiRef": {
    "uri": "https://secure-vault.acme.com/customer-pii/cust-789",
    "accessToken": "one-time-access-token-xyz"
  }
}
```

**Encryption at Field Level**
Encrypt specific PII fields in the event payload. Only consumers with the decryption key can read them:
```json
{
  "orderId": "ord-12345",
  "customerId": "cust-789",
  "encryptedEmail": "AQICAHg...",    // Encrypted with customer-data key
  "encryptedAddress": "AQICAHh..."  // Encrypted with customer-data key
}
```
Key management via AWS KMS, HashiCorp Vault, or similar.

### GDPR and the Right to Erasure

**The Problem**: GDPR's "right to be forgotten" is fundamentally at odds with immutable event logs. How do you delete a person's data from an append-only stream?

**Strategy 1: Crypto-shredding**
Encrypt all PII with a per-customer key. To "delete" the customer, delete their encryption key. All events containing their PII become permanently unreadable (effectively deleted).

```python
# Encrypt event PII with customer-specific key
key = kms.get_customer_key(customer_id)
encrypted_pii = encrypt(raw_pii, key)
event["encryptedPii"] = base64.b64encode(encrypted_pii).decode()

# To "forget" customer:
kms.delete_customer_key(customer_id)
# All historical events with this customer's encrypted PII become unreadable
```

**Strategy 2: PII-Free Events + Separate PII Store**
Events contain only pseudonymous tokens. PII is stored in a separate deletable store. On GDPR request, delete the PII store entry. Events remain in log but are now pseudonymous — no longer linkable to the individual.

**Strategy 3: Event Log Truncation**
Accept that the event log has a finite retention window (e.g., 3 years). After retention expires, events are deleted. GDPR compliance ensured through short enough retention for most personal data use cases.

---

## Compliance and Audit Trails

### Immutable Audit Logs via Event Sourcing
A well-designed event log naturally provides a compliance-ready audit trail:
- Every state change is recorded as an immutable event
- Events carry timestamp, actor identity, and the change made
- Events cannot be modified (append-only log)
- Events can be replayed to reconstruct system state at any point in time

**Financial Services Compliance Example**:
```json
{
  "type": "com.acme.trading.trade.executed",
  "id": "evt-trade-001",
  "source": "https://trading.acme.com",
  "time": "2024-01-15T14:23:01.123456Z",
  "subject": "trades/TRD-001",
  "data": {
    "tradeId": "TRD-001",
    "traderId": "trader-456",
    "instrument": "AAPL",
    "side": "BUY",
    "quantity": 1000,
    "price": 185.50,
    "venue": "NASDAQ",
    "regulatoryStatus": "PENDING_REPORT",
    "clientOrderId": "client-ord-789"
  },
  "actorId": "trader-456",
  "actorIp": "192.168.1.100",
  "sessionId": "sess-abc123"
}
```

**Audit queries against the event log**:
- "Show all trades by trader-456 between Jan 1-15"
- "What was the state of account acct-789 at 14:23:00 yesterday?"
- "Who modified order ord-12345 and when?"

### Ensuring Audit Log Integrity
The audit log is only trustworthy if it cannot be tampered with:

**Kafka Topic Lock-Down**:
```bash
# Prevent deletion of audit topic
kafka-configs.sh --alter \
  --entity-type topics \
  --entity-name audit-log \
  --add-config 'delete.retention.ms=-1,retention.ms=-1'

# Remove delete ACL for all principals except audit-admin
kafka-acls.sh --remove --allow-principal User:* --operation Delete --topic audit-log
```

**Write-Once Object Storage Backup**:
Stream audit events to S3 with Object Lock (WORM) enabled:
```python
# Kafka Connect S3 Sink to WORM bucket
connector_config = {
    "connector.class": "io.confluent.connect.s3.S3SinkConnector",
    "s3.bucket.name": "audit-log-worm-bucket",
    "s3.region": "us-east-1",
    "topics": "audit-log",
    "flush.size": "1000",
    "rotate.interval.ms": "60000",
    "storage.class": "io.confluent.connect.s3.storage.S3Storage",
    # S3 bucket has Object Lock with COMPLIANCE mode
}
```

**Cryptographic Chaining**
Include the hash of the previous event in each audit event, creating a tamper-evident chain:
```json
{
  "id": "evt-audit-1001",
  "previousEventHash": "sha256:a1b2c3...",   // SHA256 of event evt-audit-1000
  "eventHash": "sha256:d4e5f6..."             // SHA256 of this event
}
```
Any modification of a past event breaks the chain — detectable by any auditor.

---

## Security Architecture Summary

### Defense in Depth for Event Systems

| Layer | Control |
|---|---|
| Network | TLS everywhere; no plaintext event transmission |
| Authentication | mTLS or SASL/OAUTHBEARER; no shared credentials |
| Authorization | Kafka ACLs or RBAC; least-privilege per service |
| Integrity | Event signing with asymmetric keys |
| Privacy | Data minimization; tokenization; crypto-shredding for GDPR |
| Audit | Immutable append-only log; Object Lock backup; chain hashing |
| Key management | Centralized key vault (KMS/Vault); automated rotation |
| Monitoring | Alert on ACL violations, authentication failures, schema violations |
