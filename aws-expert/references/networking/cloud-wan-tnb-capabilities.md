# Cloud WAN & Telecom Network Builder — Capabilities Reference
For CLI commands, see [cloud-wan-tnb-cli.md](cloud-wan-tnb-cli.md).

## AWS Cloud WAN

**Purpose**: Managed wide-area networking service for building, managing, and monitoring a global private network across AWS Regions and on-premises locations through a unified core network policy.

### Core Concepts

| Concept | Description |
|---|---|
| **Global Network** | Top-level container in Network Manager that represents your entire network; a single global network can span all AWS Regions |
| **Core Network** | The Cloud WAN resource within a global network; defined by a core network policy; contains segments, edge locations, and attachments |
| **Core Network Policy** | JSON or YAML document that declaratively defines segments, edge locations, attachment policies, and segment actions; changes applied via Change Sets |
| **Network Manager** | AWS service used to manage both Cloud WAN core networks and Transit Gateway-based global networks |

### Core Network Policy Structure

Core network policies are JSON/YAML documents with the following top-level keys:

| Policy Key | Description |
|---|---|
| `version` | Policy document version (e.g., `"2021.12"`) |
| `core-network-configuration` | ASN ranges, edge locations (Regions), and inside CIDR blocks |
| `segments` | Named routing domains with isolation controls |
| `attachment-policies` | Rules that map attachments (by tag or other conditions) to segments |
| `segment-actions` | Cross-segment routing actions such as `share` or `create-route` |

#### `core-network-configuration` example keys
- `vpn-ecmp-support`: enable ECMP across VPN attachments
- `edge-locations`: list of AWS Regions with ASN overrides and inside CIDRs
- `asn-ranges`: pool of ASNs for automatic assignment

#### Segments

- Segments are isolated routing domains within the core network; traffic does not cross segment boundaries unless explicitly permitted
- Each segment has a `name`, optional `require-attachment-acceptance`, `isolate-attachments` flag, and optional `edge-locations` restriction
- Default behavior: all attachments within a segment can communicate with each other

#### Attachment Policies

- Rules evaluated in order by `rule-number`; first match wins
- Conditions can match on: `tag-value`, `tag-exists`, `account-id`, `region`, `resource-id`
- Action associates matched attachment to a named `segment`; optionally sets `require-acceptance`

#### Segment Actions

| Action | Description |
|---|---|
| `share` | Enables route sharing between segments; `mode: attachment-route` shares routes from specific attachment types |
| `create-route` | Injects a static route into a segment pointing to an attachment |

### Attachment Types

| Attachment Type | Description |
|---|---|
| **VPC** | Attach a VPC to the core network in a specific edge location (Region); traffic routes through core network segments |
| **Site-to-Site VPN** | Attach an AWS Site-to-Site VPN; supports BGP for dynamic route propagation |
| **Connect (SD-WAN)** | GRE tunnel over a base attachment (VPC or VPN); used for SD-WAN appliances; supports BGP |
| **Transit Gateway** | Peer a Transit Gateway into the core network as an attachment; enables gradual migration from TGW |

### Transit Gateway Peering (TGW-to-Cloud-WAN)

- Create a TGW peering attachment from the core network to a TGW in the same Region
- After peering is accepted, create TGW route table attachments to import TGW routes into core network segments
- Enables hybrid architectures combining existing TGW deployments with Cloud WAN

### Route Tables

- Cloud WAN manages routing automatically based on the core network policy; no manual route table entries for segment members
- Core network automatically propagates routes from VPC and VPN attachments into the associated segment
- Static routes injected via `create-route` segment actions in the policy

### Bandwidth and QoS

- **Bandwidth allocation**: not a hard-limit service; bandwidth scales with AWS backbone capacity
- Connect attachments (GRE/BGP) support up to 5 Gbps per Connect peer; multiple peers aggregate throughput

### Network Manager: Sites, Links, Devices, Connections

Used to represent on-premises topology within Network Manager (applicable to both Cloud WAN and TGW-based global networks):

| Resource | Description |
|---|---|
| **Site** | Logical representation of a physical location (data center, branch office) |
| **Link** | WAN link at a site with bandwidth and provider attributes |
| **Device** | Physical or virtual appliance at a site (router, SD-WAN device) |
| **Connection** | Link between two devices at the same site (for dual-router setups) |

### Change Sets

- Core network policy changes do not apply immediately; they create a pending **Change Set**
- Review the Change Set to see what will be added, modified, or removed (segments, edge locations, attachments)
- Explicitly execute the Change Set to apply; or reject it to discard
- Only one pending Change Set exists at a time per core network

### Event Notifications and Observability

| Mechanism | Description |
|---|---|
| **CloudWatch Metrics** | Metrics per edge location and segment: `BytesDropped`, `PacketsDropped`, `BytesIn`, `BytesOut`; namespace `AWS/NetworkManager` |
| **CloudWatch Events / EventBridge** | Events emitted on attachment state changes, policy changes, Change Set execution |
| **Route Analyzer** | Tool in Network Manager to trace a path through the core network and identify routing issues |
| **Topology view** | Graphical view in the Network Manager console showing core network topology |

### Cloud WAN vs Transit Gateway

| Dimension | Transit Gateway | Cloud WAN |
|---|---|---|
| **Scope** | Regional (peer for multi-region) | Global (multi-region by design) |
| **Policy model** | Imperative (per-resource CLI/console) | Declarative (single JSON/YAML core network policy) |
| **Routing domains** | Route tables with associations/propagations | Segments with attachment policies |
| **SD-WAN support** | Connect attachments (GRE/BGP) | Connect attachments (GRE/BGP) |
| **On-premises** | VPN, Direct Connect Gateway | VPN, Direct Connect Gateway (via TGW peering or direct) |
| **Multi-account** | RAM sharing | RAM sharing |
| **Best for** | Regional hub-and-spoke; existing deployments | New global networks; large multi-region; policy-driven automation |

---

## AWS Telecom Network Builder (TNB)

**Purpose**: Managed service for telecommunications operators to deploy, manage, and scale virtualized and cloud-native 5G and 4G network functions on AWS infrastructure (EKS and EC2), with ETSI-compliant lifecycle management.

### Key Concepts

| Concept | Description |
|---|---|
| **Function Package** | Container for a single Virtualized Network Function (VNF) or Cloud-native Network Function (CNF); includes a VNFD (ETSI SOL 001 descriptor) and artifacts |
| **Network Package** | Container for a complete network service; includes a Network Service Descriptor (NSD, ETSI SOL 001) referencing one or more function packages |
| **Network Instance** | A running instantiation of a network package; represents the deployed network service |
| **VNFD** | VNF Descriptor — ETSI SOL 001-compliant YAML descriptor defining compute, storage, and connectivity requirements for a VNF |
| **NSD** | Network Service Descriptor — ETSI SOL 001-compliant YAML descriptor defining the composition of VNFs and their interconnections |

### Workflow Overview

```
1. Create Function Package  →  Upload VNFD + artifacts
2. Create Network Package   →  Upload NSD referencing function packages
3. Create Network Instance  →  Instantiate the network service
4. Manage lifecycle         →  Update / Terminate / Delete
```

### Function Packages

- Created in `CREATED` state; content uploaded separately (VNFD YAML + container images or AMI references)
- State transitions: `CREATED` → `UPLOAD_IN_PROGRESS` → `VALIDATING` → `VALIDATED` (or `VALIDATION_FAILED`)
- Descriptors follow ETSI MANO SOL 001 format; TNB validates against the schema on upload
- Artifacts referenced in the VNFD (container images, Helm charts) must be accessible to TNB (e.g., ECR repositories)

### Network Packages

- Reference one or more validated function packages via their IDs in the NSD
- State transitions mirror function packages: `CREATED` → `UPLOAD_IN_PROGRESS` → `VALIDATING` → `VALIDATED`
- NSD specifies topology: VL (Virtual Link), VNF profiles, connectivity to AWS VPC subnets

### Network Instances

- Created from a validated network package; not yet deployed at creation
- **Instantiate**: triggers deployment of resources (EKS node groups, EC2 instances, ENIs, VPCs as defined in NSD); maps to ETSI SOL 003 `POST /ns_instances/{id}/instantiate`
- **Terminate**: tears down deployed resources but retains the instance record; maps to ETSI SOL 003 `POST /ns_instances/{id}/terminate`
- **Update**: modifies a running instance (scale, modify VNF, add VNF); maps to ETSI SOL 003 `POST /ns_instances/{id}/update`
- **Delete**: removes the instance record (must be terminated first)

### ETSI Standards Compliance

| Standard | Usage in TNB |
|---|---|
| **ETSI SOL 001** | Descriptor format for VNFD and NSD (YAML/TOSCA-based) |
| **ETSI SOL 003** | Ve-Vnfm-em reference point; lifecycle management API operations (instantiate, terminate, update, query) |
| **ETSI SOL 005** | Os-Ma-Nfvo reference point; network service lifecycle management |

### Underlying Infrastructure

- **Amazon EKS**: Cloud-native network functions (CNFs) deployed as Kubernetes workloads; TNB creates and manages node groups
- **Amazon EC2**: Virtualized network functions (VNFs) deployed as EC2 instances with specific instance types for performance (e.g., bare metal, enhanced networking)
- **AWS VPC**: Network connectivity between NFs defined in the NSD; TNB provisions subnets and ENIs

### Lifecycle Operation States

| State | Description |
|---|---|
| `NOT_INSTANTIATED` | Instance created but no resources deployed |
| `INSTANTIATING` | Deployment in progress |
| `INSTANTIATED` | Running; resources deployed |
| `UPDATING` | Update operation in progress |
| `TERMINATING` | Teardown in progress |
| `TERMINATED` | Resources removed; record retained |

### Partner Integrations

TNB supports network function vendors whose packages are qualified to run on the platform:

| Partner | Network Functions |
|---|---|
| **Ericsson** | 5G Core (AMF, SMF, UPF), RAN management |
| **Nokia** | 5G Core network functions, packet core |
| **Affirmed Networks (Microsoft)** | vEPC, 5G Core |
| **Mavenir** | Open RAN, 5G Core NFs |

Vendors provide pre-validated function packages and NSDs compatible with TNB descriptors.
