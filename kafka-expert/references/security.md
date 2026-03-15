# Securing Kafka
## Chapter 12: TLS Encryption, SASL Authentication, ACLs, Authorization

---

## Security Model Overview

Kafka security covers three concerns:

```
┌─────────────────────────────────────────────────────────────┐
│                   KAFKA SECURITY LAYERS                      │
│                                                             │
│  1. ENCRYPTION (TLS)                                        │
│     Data in transit encrypted between clients and brokers   │
│     Data in transit encrypted between brokers (replication) │
│                                                             │
│  2. AUTHENTICATION (SASL or mTLS)                           │
│     Who is connecting? Verify client identity               │
│     Supports: PLAIN, SCRAM-SHA-256/512, GSSAPI, OAUTHBEARER │
│                                                             │
│  3. AUTHORIZATION (ACLs)                                    │
│     What is this client allowed to do?                      │
│     Resource-based: Topic, Group, Cluster, TransactionId    │
└─────────────────────────────────────────────────────────────┘
```

---

## TLS Encryption

TLS (Transport Layer Security) encrypts data in transit. Without TLS, credentials and message content are visible to network eavesdroppers.

### Generating Certificates

**Production approach**: Use an internal CA (or cert manager in Kubernetes) to issue certificates. Avoid self-signed certs in production.

```bash
# Generate broker keystore (per broker)
keytool -keystore kafka.broker1.keystore.jks -alias broker1 -validity 365 \
  -genkey -keyalg RSA -dname "CN=broker1.example.com" \
  -storepass keystore-password -keypass key-password

# Generate CSR (Certificate Signing Request)
keytool -keystore kafka.broker1.keystore.jks -alias broker1 \
  -certreq -file broker1.csr -storepass keystore-password

# Sign CSR with CA (your CA process)
openssl x509 -req -CA ca.crt -CAkey ca.key -in broker1.csr \
  -out broker1.crt -days 365 -CAcreateserial

# Import CA cert + signed cert into keystore
keytool -keystore kafka.broker1.keystore.jks -alias CARoot \
  -import -file ca.crt -storepass keystore-password -noprompt
keytool -keystore kafka.broker1.keystore.jks -alias broker1 \
  -import -file broker1.crt -storepass keystore-password

# Create truststore (containing CA cert)
keytool -keystore kafka.truststore.jks -alias CARoot \
  -import -file ca.crt -storepass truststore-password -noprompt
```

### Broker TLS Configuration

```properties
# In server.properties
listeners=PLAINTEXT://broker1:9092,SSL://broker1:9093
advertised.listeners=PLAINTEXT://broker1:9092,SSL://broker1:9093

ssl.keystore.location=/etc/kafka/ssl/kafka.broker1.keystore.jks
ssl.keystore.password=keystore-password
ssl.key.password=key-password
ssl.truststore.location=/etc/kafka/ssl/kafka.truststore.jks
ssl.truststore.password=truststore-password
ssl.client.auth=required  # required for mTLS; requested/none for one-way TLS

# Protocol versions
ssl.enabled.protocols=TLSv1.3,TLSv1.2
ssl.protocol=TLSv1.2
```

### Client TLS Configuration

```properties
# Client (producer/consumer)
security.protocol=SSL
ssl.truststore.location=/etc/kafka/ssl/kafka.truststore.jks
ssl.truststore.password=truststore-password

# For mTLS (client certificate):
ssl.keystore.location=/etc/kafka/ssl/kafka.client.keystore.jks
ssl.keystore.password=keystore-password
ssl.key.password=key-password
```

### Inter-Broker Replication over TLS

```properties
security.inter.broker.protocol=SSL
```

---

## SASL Authentication

SASL (Simple Authentication and Security Layer) authenticates clients without requiring client certificates. Multiple mechanisms are supported:

| Mechanism | Description | Use Case |
|-----------|-------------|---------|
| `PLAIN` | Username/password in clear text over TLS | Simple setups; must use with TLS |
| `SCRAM-SHA-256` | Challenge-response; credentials stored in ZK/KRaft | Modern password auth |
| `SCRAM-SHA-512` | Same as SCRAM-SHA-256 with stronger hash | Preferred over SHA-256 |
| `GSSAPI` (Kerberos) | Enterprise Kerberos integration | Corporate environments with AD/Kerberos |
| `OAUTHBEARER` | OAuth 2.0 token-based auth | Cloud-native; service accounts; short-lived tokens |

### SASL_SSL — Most Common Production Setup

Uses SASL for authentication over a TLS-encrypted channel.

**Broker configuration (SCRAM-SHA-512):**

```properties
listeners=SASL_SSL://broker1:9093
advertised.listeners=SASL_SSL://broker1:9093
security.inter.broker.protocol=SASL_SSL

sasl.mechanism.inter.broker.protocol=SCRAM-SHA-512
sasl.enabled.mechanisms=SCRAM-SHA-512

# TLS settings (same as above)
ssl.keystore.location=...
ssl.truststore.location=...

# JAAS config for broker
listener.name.sasl_ssl.scram-sha-512.sasl.jaas.config=\
  org.apache.kafka.common.security.scram.ScramLoginModule required \
  username="inter-broker-user" \
  password="inter-broker-password";
```

**Create SCRAM credentials:**

```bash
# Add user credentials (stored in ZooKeeper or KRaft metadata)
kafka-configs.sh --bootstrap-server broker:9092 \
  --alter --add-config 'SCRAM-SHA-512=[iterations=8192,password=my-password]' \
  --entity-type users --entity-name alice

kafka-configs.sh --bootstrap-server broker:9092 \
  --alter --add-config 'SCRAM-SHA-512=[iterations=8192,password=broker-password]' \
  --entity-type users --entity-name inter-broker-user
```

**Client configuration (SCRAM-SHA-512):**

```properties
security.protocol=SASL_SSL
sasl.mechanism=SCRAM-SHA-512
sasl.jaas.config=org.apache.kafka.common.security.scram.ScramLoginModule required \
  username="alice" \
  password="my-password";
ssl.truststore.location=/etc/kafka/ssl/kafka.truststore.jks
ssl.truststore.password=truststore-password
```

### OAUTHBEARER

For modern, cloud-native environments using OAuth 2.0:

```properties
# Client
sasl.mechanism=OAUTHBEARER
sasl.oauthbearer.token.endpoint.url=https://auth-server/oauth/token
sasl.login.callback.handler.class=org.apache.kafka.common.security.oauthbearer.secured.OAuthBearerLoginCallbackHandler
sasl.jaas.config=org.apache.kafka.common.security.oauthbearer.OAuthBearerLoginModule required \
  clientId="kafka-client" \
  clientSecret="client-secret" \
  scope="kafka";
```

Tokens are automatically refreshed before expiry. No long-lived credentials stored in config files.

---

## ACLs (Access Control Lists)

ACLs define **who can do what** with which Kafka resources.

### ACL Model

```
Principal (who): User:alice, User:service-account, Group:analytics-team
Operation (what): Read, Write, Create, Delete, Describe, Alter, All
Resource (which): Topic:orders, Group:payment-processor, Cluster:*
Pattern (how): Literal (exact match) or Prefixed (prefix match)
Host (from where): * (any host) or specific IP
```

### Managing ACLs

**Enable ACLs on broker:**

```properties
authorizer.class.name=org.apache.kafka.metadata.authorizer.StandardAuthorizer
allow.everyone.if.no.acl.found=false  # deny by default
super.users=User:admin,User:kafka
```

**Create ACLs:**

```bash
# Allow alice to write to orders topic
kafka-acls.sh --bootstrap-server broker:9092 \
  --add --allow-principal User:alice \
  --operation Write --topic orders

# Allow payment-processor group to read from orders topic
kafka-acls.sh --bootstrap-server broker:9092 \
  --add --allow-principal User:payment-service \
  --operation Read --topic orders

# Allow payment-service to commit to consumer group
kafka-acls.sh --bootstrap-server broker:9092 \
  --add --allow-principal User:payment-service \
  --operation Read --group payment-processor

# Allow all operations on topics with prefix "app-"
kafka-acls.sh --bootstrap-server broker:9092 \
  --add --allow-principal User:app-service \
  --operation All --topic 'app-' --resource-pattern-type prefixed

# List ACLs for a topic
kafka-acls.sh --bootstrap-server broker:9092 \
  --list --topic orders

# Remove ACL
kafka-acls.sh --bootstrap-server broker:9092 \
  --remove --allow-principal User:alice \
  --operation Write --topic orders
```

### Typical ACL Patterns

```
Producer service:
  Write → topic (its output topic)
  Describe → topic (to check partition count)

Consumer service:
  Read → topic
  Read → group (its consumer group ID)
  Describe → group

Admin tool:
  Describe → cluster
  Alter → cluster (for config changes)
  Create/Delete → topic

Kafka Connect worker:
  All → topic (for connector topics)
  Read → group (connect worker group)
  All → cluster (for offset management)

MirrorMaker 2:
  All → cluster (source: to read; destination: to write + create topics)
```

---

## Encryption at Rest

Kafka does **not** encrypt data at rest natively. Encryption at rest must be provided by:

1. **Storage encryption**: Encrypt the disk/volume where Kafka stores logs (LUKS on Linux, EBS encryption on AWS, etc.)
2. **Application-level encryption**: Encrypt message values before producing; decrypt after consuming
3. **Cloud-native**: AWS KMS, Azure Key Vault, GCP KMS managed disk encryption

For regulated industries (HIPAA, PCI), application-level encryption is often required so the Kafka infrastructure team cannot read sensitive message content.

---

## Security Best Practices

| Practice | Why |
|---------|-----|
| Always use TLS in production | Prevents eavesdropping and credential interception |
| Use SCRAM-SHA-512 or OAUTHBEARER over SASL PLAIN | PLAIN transmits credentials in plaintext (even over TLS, more auditable with SCRAM) |
| `allow.everyone.if.no.acl.found=false` | Default deny; explicit grants only |
| Rotate credentials regularly | Limit blast radius of credential compromise |
| Separate credentials per service | If one service is compromised, others are isolated |
| Use prefixed ACLs for teams | `team-payments-` prefix allows self-service topic creation within a namespace |
| Audit access logs | Log all authentication events and authorization decisions |
| Rotate TLS certificates before expiry | Certificate expiry causes outage if not managed |
| Use `super.users` sparingly | Super users bypass ACL checks entirely |
| Test ACLs in staging | Overly permissive ACLs are hard to tighten later |
