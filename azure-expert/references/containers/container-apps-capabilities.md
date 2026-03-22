# Azure Container Apps — Capabilities Reference
For CLI commands, see [container-apps-cli.md](container-apps-cli.md).

## Azure Container Apps

**Purpose**: Fully managed serverless container platform built on Kubernetes and open-source technologies (KEDA, Dapr, Envoy). Run microservices and containerized applications without managing Kubernetes infrastructure.

---

## Architecture Overview

```
Azure Container Apps Environment
├── Shared VNet (optional custom VNet injection)
├── Shared Log Analytics workspace
├── Dapr configuration (optional)
└── Container Apps
    ├── App A (Revisions → containers + sidecars)
    ├── App B (Jobs)
    └── App C (internal only, no ingress)
```

---

## Environment

The **Environment** is the secure isolation boundary shared by all container apps within it.

| Feature | Description |
|---|---|
| **Shared infrastructure** | All apps in an environment share a Log Analytics workspace and (optionally) a VNet |
| **VNet injection** | Custom VNet for private networking; environment gets a dedicated subnet |
| **Workload profiles** | Consumption (serverless) or dedicated (specific VM sizes) |
| **Dapr configuration** | Environment-level Dapr component definitions shared by all apps |
| **Internal vs external** | Internal: no public endpoint, accessible only within VNet; External: public load balancer with public IP |
| **Managed certificates** | Automatic TLS certificates for custom domains (Let's Encrypt) |

### Workload Profile Environments
- Newer environment type supporting mixed workload profiles
- **Consumption profile**: serverless, scale to zero, shared infrastructure
- **Dedicated profiles**: specific Azure VM SKUs (General Purpose, Memory Optimized, GPU); reserve capacity for demanding workloads
- Apps can use any profile defined in the environment

---

## Container App

The **Container App** is the deployable unit: one or more containers (in a pod-like group) with associated configuration.

### Container App Components

| Component | Description |
|---|---|
| **Containers** | One or more containers per app; share lifecycle, network, and storage |
| **Init containers** | Run before app containers start; for initialization tasks |
| **Sidecars** | Additional containers (e.g., log shippers, proxies) alongside the main container |
| **Revisions** | Immutable snapshots of container app configuration; new revision on each configuration change |
| **Replicas** | Running instances of the active revision |
| **Ingress** | HTTP/TCP/gRPC endpoint configuration |
| **Secrets** | Encrypted key-value pairs referenced by env vars or volume mounts |

---

## Revisions

Container Apps uses an immutable revision model for deployments.

| Concept | Description |
|---|---|
| **Revision** | A new revision is created on every container app update (image, env vars, scaling rules, etc.) |
| **Single-revision mode** | Only one active revision at a time; new revision immediately replaces old (default) |
| **Multiple-revision mode** | Multiple revisions active simultaneously; enables traffic splitting |
| **Revision suffix** | Auto-generated or custom suffix appended to the app name (e.g., `myapp--v2`) |
| **Traffic weight** | Assign % of traffic to each active revision (must sum to 100%) |

### Traffic Splitting Patterns

**Blue-Green Deployment:**
```bash
# Shift 100% traffic from blue to green
az containerapp ingress traffic set \
  --name myapp \
  --resource-group myRG \
  --revision-weight myapp--green=100 myapp--blue=0
```

**Canary Release:**
```bash
# Send 10% to new revision, 90% to stable
az containerapp ingress traffic set \
  --name myapp \
  --resource-group myRG \
  --revision-weight myapp--stable=90 myapp--canary=10
```

---

## Scaling

Container Apps scales replicas based on configurable rules. Scale to zero is supported for HTTP and event-based triggers.

### Scaling Rules

| Rule Type | Description | Scale-to-Zero |
|---|---|---|
| **HTTP** | Scale based on concurrent HTTP requests per replica (default: 10 req/replica) | Yes |
| **CPU** | Scale based on CPU utilization (%) | No (min 1 replica required) |
| **Memory** | Scale based on memory utilization (%) | No (min 1 replica required) |
| **KEDA scalers** | Any KEDA trigger: Service Bus, Event Hubs, Queue Storage, Cron, Prometheus, custom | Yes (most) |

### KEDA Scaler Examples

**Service Bus queue depth:**
```yaml
scale:
  minReplicas: 0
  maxReplicas: 10
  rules:
  - name: servicebus-rule
    custom:
      type: azure-servicebus
      metadata:
        queueName: myQueue
        namespace: myServiceBusNS
        messageCount: "10"
      auth:
      - secretRef: servicebus-connection
        triggerParameter: connection
```

**Cron schedule:**
```yaml
scale:
  minReplicas: 0
  maxReplicas: 5
  rules:
  - name: cron-rule
    custom:
      type: cron
      metadata:
        timezone: America/New_York
        start: "0 8 * * 1-5"
        end: "0 18 * * 1-5"
        desiredReplicas: "3"
```

### Scale Configuration Parameters

| Parameter | Description |
|---|---|
| `--min-replicas` | Minimum replicas (0 = scale to zero) |
| `--max-replicas` | Maximum replicas |
| `--scale-rule-name` | Name for the scale rule |
| `--scale-rule-type` | `http`, `cpu`, `memory`, or custom KEDA type |
| `--scale-rule-metadata` | Key-value pairs for scaler configuration |
| `--scale-rule-auth` | Auth references for scalers requiring credentials |

---

## Jobs

Container Apps Jobs run containers to completion (not continuously running services).

| Job Type | Description | Use Case |
|---|---|---|
| **Manual** | Triggered on-demand via CLI or REST API | Ad-hoc data processing, testing |
| **Scheduled** | Cron schedule triggers job execution | Nightly batch, report generation |
| **Event-triggered** | KEDA scaler triggers job (e.g., each Service Bus message triggers one job instance) | Queue-driven processing, parallel workloads |

### Job Configuration

| Parameter | Description |
|---|---|
| `--replica-timeout` | Max time in seconds a job replica can run before being terminated |
| `--replica-retry-limit` | Number of retries on failure (default 0) |
| `--parallelism` | Number of replicas that run simultaneously per execution |
| `--replica-completion-count` | Number of replicas that must complete successfully for the job to succeed |

---

## Ingress

| Setting | Options | Description |
|---|---|---|
| **Exposure** | External / Internal | External: publicly accessible; Internal: environment VNet only |
| **Protocol** | HTTP, TCP, gRPC | HTTP supports TLS termination; TCP for arbitrary TCP traffic |
| **Target port** | Any port | Port the container listens on |
| **Transport** | HTTP/1.1, HTTP/2, auto | Auto detects protocol |
| **Managed TLS** | Enabled by default | Automatic TLS certificate for `*.azurecontainerapps.io` domain |
| **Custom domains** | Yes | Bind custom domain with managed or BYO certificate |
| **Session affinity** | Sticky sessions | Route requests from same client to same replica |

### Custom Domains
```bash
# Add a custom domain with managed certificate (Let's Encrypt)
az containerapp hostname add \
  --hostname api.contoso.com \
  --resource-group myRG \
  --name myapp

# Bind a managed certificate to the custom hostname
az containerapp ssl upload \
  --hostname api.contoso.com \
  --resource-group myRG \
  --name myapp \
  --certificate-file mycert.pfx \
  --certificate-password mypassword
```

---

## Dapr Integration

Dapr (Distributed Application Runtime) is natively integrated in Azure Container Apps.

### Enable and Configure Dapr

```yaml
# In container app definition
dapr:
  enabled: true
  appId: my-service
  appPort: 8080
  appProtocol: http
```

### Dapr Capabilities Available

| Capability | Description | Common Components |
|---|---|---|
| **Service invocation** | Reliable service-to-service calls with retries, mTLS | Built-in (no component needed) |
| **Pub/sub** | Publish and subscribe to message topics | Azure Service Bus, Event Hubs, Redis |
| **State management** | Consistent key-value state storage | Azure Cosmos DB, Redis, Azure Table Storage |
| **Secrets** | Secure secret retrieval | Azure Key Vault, Kubernetes secrets |
| **Bindings** | Connect to external systems (input/output) | Azure Blob Storage, Twilio, SMTP |
| **Actors** | Virtual actor pattern for stateful entities | Built-in with configurable state store |

### Dapr Components

```bash
# Create a Dapr pub/sub component (Service Bus)
az containerapp env dapr-component set \
  --environment myEnv \
  --resource-group myRG \
  --dapr-component-name pubsub \
  --yaml - << 'EOF'
componentType: pubsub.azure.servicebus.topics
version: v1
metadata:
- name: connectionString
  secretRef: servicebus-connection
scopes:
- publisher-app
- subscriber-app
EOF
```

---

## Secrets Management

| Method | Description |
|---|---|
| **App secrets** | Defined at the container app level; referenced by revision-level env vars |
| **Key Vault references** | Secret value fetched from Azure Key Vault using managed identity |
| **Environment variables** | Map secret to container environment variable with `secretRef` |
| **Volume mounts** | Mount secret as a file in the container filesystem |

```bash
# Set a secret on a container app
az containerapp secret set \
  --name myapp \
  --resource-group myRG \
  --secrets db-password=mysecretvalue

# Reference Key Vault secret
az containerapp secret set \
  --name myapp \
  --resource-group myRG \
  --secrets "db-password=keyvaultref:https://myKV.vault.azure.net/secrets/DbPassword,identityref:/subscriptions/{subId}/resourceGroups/myRG/providers/Microsoft.ManagedIdentity/userAssignedIdentities/myIdentity"
```

---

## Networking

| Feature | Description |
|---|---|
| **Default (no VNet)** | Environment uses Azure-managed VNet; public egress with shared IP |
| **Custom VNet injection** | Bring your own VNet subnet (min /23 CIDR for consumption; /27 for workload profiles) |
| **Internal environment** | No public IP; only accessible within VNet or peered networks |
| **Service discovery** | Apps communicate using app name as hostname: `http://{app-name}` within same environment |
| **Peer environments** | VNet peering enables communication across environments |
| **User-defined routes** | Route outbound traffic through Azure Firewall or NVA |

---

## Container Apps vs AKS vs Functions

| Criterion | Container Apps | AKS | Azure Functions |
|---|---|---|---|
| **Control level** | Low (serverless managed) | High (full K8s control) | Very low (code only) |
| **Kubernetes expertise needed** | None | High | None |
| **Long-running workloads** | Yes | Yes | Limited (plan-dependent) |
| **Scale to zero** | Yes | Partial (with KEDA) | Yes (Consumption/Flex) |
| **Event-driven** | Yes (KEDA built-in) | Yes (KEDA add-on) | Yes (many triggers) |
| **Custom networking** | VNet injection | Full CNI control | VNet integration |
| **Dapr built-in** | Yes (native) | Add-on | No |
| **Best for** | Microservices, APIs, event-driven containers | Complex K8s workloads, stateful apps | Short-lived functions, many Azure triggers |
