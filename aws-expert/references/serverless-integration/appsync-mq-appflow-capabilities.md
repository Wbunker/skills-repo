# AWS AppSync, MQ & AppFlow — Capabilities Reference
For CLI commands, see [appsync-mq-appflow-cli.md](appsync-mq-appflow-cli.md).

## AWS AppSync

**Purpose**: Fully managed GraphQL and Pub/Sub API service. Simplifies development by allowing clients to access data from multiple sources via a single GraphQL endpoint.

### Core Concepts

| Concept | Description |
|---|---|
| **GraphQL schema** | Defines types, queries, mutations, and subscriptions |
| **Data source** | Backend connected to AppSync: DynamoDB, Lambda, RDS (Aurora Serverless), HTTP endpoint, OpenSearch, EventBridge, or None |
| **Resolver** | Code that maps a GraphQL operation to a data source operation |
| **Unit resolver** | Single resolver connected to one data source |
| **Pipeline resolver** | Chains multiple functions (each with its own data source) sequentially |
| **Function** | Reusable resolver component used in pipeline resolvers |
| **Subscription** | Real-time updates delivered to subscribed clients via WebSocket |

### Resolvers

| Type | Description | Use case |
|---|---|---|
| **Unit resolver** | Single data source mapping | Simple CRUD operations |
| **Pipeline resolver** | Ordered list of functions; each can query a different data source | Multi-step logic, authorization checks, aggregation |
| **Direct Lambda resolver** | Lambda as resolver; AppSync passes the full request | Complex business logic, arbitrary data transformations |

Resolvers are written in JavaScript (recommended) or Apache Velocity Template Language (VTL).

### Data Sources

| Source | Operations |
|---|---|
| **Amazon DynamoDB** | GetItem, PutItem, UpdateItem, DeleteItem, Query, Scan, BatchGetItem, TransactWriteItems |
| **AWS Lambda** | Invoke any Lambda function |
| **Amazon RDS (Aurora Serverless)** | SQL via Data API |
| **HTTP endpoint** | Any HTTP/HTTPS endpoint |
| **Amazon OpenSearch Service** | Search and aggregation queries |
| **Amazon EventBridge** | Put events to a bus |
| **None** | Local resolver for transformations without a backend call |

### Subscriptions

- Clients subscribe to mutation operations via WebSocket (`graphql-ws` or `graphql-transport-ws`)
- AppSync triggers subscription notifications when the subscribed mutation runs
- **Enhanced subscriptions**: Filter subscription events server-side; reduce client-side processing

### Authorization Modes

| Mode | Description |
|---|---|
| **API key** | Simple; key included in request header; suitable for public or development APIs |
| **Amazon Cognito User Pools** | Validates Cognito JWT; access control via group claims |
| **IAM** | SigV4 signed requests; suitable for server-to-server or authenticated AWS clients |
| **OpenID Connect (OIDC)** | Validates JWT from any OIDC-compliant provider |
| **Lambda** | Custom authorization logic; Lambda returns an authorization decision |

Multiple authorization modes can be active simultaneously; set a default and specify per field with `@auth` directive.

### Caching

- Enable server-side caching per API with configurable TTL (1–3,600 s)
- Cache instance sizes: small, medium, large, xlarge, 2xlarge, 4xlarge, 8xlarge, 12xlarge
- Cache by resolver or per-field; can flush entire cache or individual keys

### Conflict Detection and Resolution (Offline Sync)

For mobile/offline-first applications using AWS Amplify DataStore:
- **Optimistic concurrency**: Version field compared; conflict if mismatch
- **Auto merge**: AppSync resolves non-conflicting field changes
- **Lambda**: Custom conflict resolution logic
- **None**: Last-write-wins

### Merged APIs

Combine multiple AppSync APIs (source APIs) into a single merged API endpoint. Each source team owns their schema independently; the merged API exposes a unified schema. Useful for micro-frontend or team-based development models.

---

## Amazon MQ

**Purpose**: Managed message broker service for Apache ActiveMQ and RabbitMQ. Supports industry-standard messaging protocols for migrating existing message broker workloads to AWS without rewriting code.

### Supported Brokers

| Broker | Use case |
|---|---|
| **Apache ActiveMQ Classic** | OpenWire, AMQP, STOMP, MQTT, WebSocket protocols; JMS-compliant |
| **RabbitMQ** | AMQP 0-9-1 protocol; supports quorum queues for HA |

### Supported Protocols

| Protocol | ActiveMQ | RabbitMQ |
|---|---|---|
| **AMQP 1.0** | Yes | No |
| **AMQP 0-9-1** | No | Yes |
| **OpenWire** | Yes | No |
| **STOMP** | Yes | No |
| **MQTT** | Yes | No |
| **WebSocket** | Yes | Yes |

### Deployment Options

| Option | Description |
|---|---|
| **Single-instance** | One broker; development and testing; no HA |
| **Active/standby** | Two brokers across AZs; automatic failover; for production |
| **Cluster (RabbitMQ)** | 3-node cluster across AZs; quorum queues for durability and HA |

### When to Use Amazon MQ vs SQS/SNS

| Use Amazon MQ when | Use SQS/SNS when |
|---|---|
| Migrating on-premises ActiveMQ or RabbitMQ without code changes | Building new cloud-native applications |
| Existing code uses JMS, AMQP, STOMP, MQTT, or OpenWire | Need infinite scale and zero management overhead |
| Need wire-protocol compatibility | Cost-sensitive; pay per message not per broker-hour |
| Using messaging features specific to ActiveMQ/RabbitMQ | Native AWS service integrations (Lambda ESM, EventBridge, etc.) |

### Security

- Encryption at rest and in transit (TLS)
- Deploy in a VPC; accessible only via private endpoint
- IAM authentication for management APIs; broker-native users for messaging

---

## Amazon AppFlow

**Purpose**: Fully managed integration service for securely transferring data between SaaS applications (Salesforce, ServiceNow, Marketo, Zendesk) and AWS services (S3, Redshift, EventBridge) without writing code.

### Key Concepts

| Concept | Description |
|---|---|
| **Flow** | Defines source, destination, field mappings, and transformation tasks |
| **Connector profile** | Stores authentication credentials for a connector |
| **Connector** | Plugin for a specific SaaS or AWS service |

### Flow Trigger Types

| Type | Description |
|---|---|
| **On-demand** | Run manually or via API |
| **Scheduled** | Run on a cron or rate schedule |
| **Event-triggered** | Source fires event (e.g., Salesforce Change Data Capture) |

### Supported Connectors (sample)

SaaS sources: Salesforce, ServiceNow, Marketo, Zendesk, Slack, HubSpot, Google Analytics, SAP OData, Datadog, Dynatrace, Veeva, Infor Nexus, Amplitude, Trend Micro, LinkedIn

AWS targets: S3, Redshift, EventBridge, Salesforce Marketing Cloud, Upsolver, SnowFlake, Lookout for Metrics

### Data Transformation Tasks

- Field mapping and renaming
- Concatenation and arithmetic
- Filter (include/exclude records based on field values)
- Mask or truncate sensitive fields
- Validate field values against constraints

### Private Connections (PrivateLink)

AppFlow can use AWS PrivateLink to connect to SaaS endpoints without traversing the public internet. Supported for Salesforce, Snowflake, and select other connectors.
