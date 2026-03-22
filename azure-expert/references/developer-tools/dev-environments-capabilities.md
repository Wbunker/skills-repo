# Developer Environments — Capabilities Reference
For CLI commands, see [dev-environments-cli.md](dev-environments-cli.md).

## Azure DevTest Labs

**Purpose**: Managed service for creating self-service development and test environments with enforced policies, cost controls, and automated lifecycle management. Designed for teams who need on-demand VMs or environments without admin overhead.

### Key Concepts

| Concept | Description |
|---|---|
| **Lab** | Container for all DevTest Labs resources; scoped to a resource group |
| **VM policies** | Enforce allowed VM sizes, OS images, number of VMs per user |
| **Auto-shutdown** | Schedule automatic shutdown (and optional startup) of all lab VMs; reduces waste |
| **Formulas** | Reusable VM configuration templates (size, image, artifacts, network settings) |
| **Claimable VMs** | Pre-created VMs in a pool; users claim one on demand |
| **Artifacts** | Post-deployment software/configuration scripts (Chocolatey, PowerShell, Shell); shared via GitHub/Azure Repos |
| **Environments** | ARM-template-based multi-VM environment definitions; whole application stacks |
| **Cost tracking** | Per-lab and per-resource cost reporting; spending targets and alerts |
| **Marketplace images** | Use Azure Marketplace VM images or custom images from a shared gallery |
| **Custom images** | Capture a configured VM as a lab image; shared via Azure Compute Gallery |

### Policies and Governance

- **Allowed VM sizes**: Restrict which VM SKUs users can select (prevent accidental expensive VMs)
- **Allowed images**: Whitelist specific OS images (Windows/Linux distributions)
- **Max VMs per user**: Limit number of VMs each lab user can create
- **Max VMs per lab**: Lab-wide VM count ceiling
- **Auto-shutdown policy**: Lab-wide default shutdown time; overridable per VM if permitted
- **Cost threshold**: Notify or auto-delete when lab cost exceeds budget

---

## Microsoft Dev Box

**Purpose**: Cloud-hosted developer workstations running Windows 11, pre-configured with project-specific tools and code. Developers get a powerful, consistent dev environment in minutes via a self-service portal without IT provisioning overhead.

### Key Concepts

| Concept | Description |
|---|---|
| **Dev Center** | Top-level organizational unit managing Dev Box definitions, catalogs, and projects |
| **Project** | Unit of access control; developers are members of projects; each project has pools |
| **Dev Box Pool** | Collection of identically configured Dev Boxes for a project (definition + network + region) |
| **Dev Box Definition** | VM image + compute SKU (e.g., 8 vCPU, 32 GB RAM, Windows 11 Enterprise) |
| **Dev Box** | Individual cloud PC assigned to a developer; persists between sessions |
| **Dev Portal** | Self-service web UI (`devportal.microsoft.com`) where devs create/start/stop their Dev Boxes |
| **Network Connection** | Links Dev Boxes to a VNet (Microsoft-hosted or customer VNet) for corporate network access |
| **Hibernate** | Suspend Dev Box to reduce cost while preserving state (faster resume than cold start) |

### Developer Experience

- **SSO via Entra ID**: No separate credentials; sign in with corporate account
- **Access via browser** (Windows App / web) or Windows App on macOS/iOS
- **Customization**: `winget` packages, `Chocolatey`, Dev Drive (ReFS volume optimized for code repos)
- **Customization files**: `devbox.yaml` committed to repo; team-standard tool installation on first boot
- **Multiple Dev Boxes**: Developer can have Dev Boxes for different projects simultaneously
- **Microsoft-hosted network**: Simplest setup; no VNet required; outbound internet + Microsoft 365 access
- **Customer-managed VNet**: Required for access to private resources (on-premises, Azure private endpoints)

### Compute SKUs

| SKU | vCPU | RAM | Storage | Use Case |
|---|---|---|---|---|
| `general_8c32gb256ssd_v2` | 8 | 32 GB | 256 GB SSD | Standard development |
| `general_16c64gb512ssd_v2` | 16 | 64 GB | 512 GB SSD | Heavier builds, data science |
| `general_32c128gb2048ssd_v2` | 32 | 128 GB | 2 TB SSD | Game development, video editing |

---

## Azure Deployment Environments

**Purpose**: Enable developers to self-provision pre-approved application infrastructure (Bicep, ARM, Terraform) from a catalog, without needing Azure permissions or deep cloud knowledge. Pairs with Dev Box for inner-loop/outer-loop developer workflow.

### Key Concepts

| Concept | Description |
|---|---|
| **Dev Center** | Shared with Dev Box; organizes projects, catalogs, and environment types |
| **Catalog** | Git repository (GitHub/Azure Repos) containing environment template definitions |
| **Environment Definition** | Template (Bicep/ARM/Terraform/Pulumi) + parameter schema for a deployable environment |
| **Environment Type** | Named deployment target (e.g., Dev, Test, Staging) with associated subscription and permissions |
| **Environment** | Instantiated deployment of a definition; developer-owned or project-scoped |
| **Self-service portal** | `devportal.microsoft.com`; developers pick a definition, fill parameters, deploy |

### Governance Controls

- Environment types map to specific subscriptions → isolate dev/test/prod billing
- Permissions: Platform engineers define what developers can deploy; developers can't modify infrastructure outside approved templates
- Catalog templates version-controlled in Git; approved by platform team before use
- Automated cleanup: environments can expire and be auto-deleted after a set duration

---

## VS Code Azure Extensions

**Purpose**: Integrate Azure management and development capabilities directly into Visual Studio Code, eliminating context-switching to portal or CLI for common tasks.

### Key Extensions

| Extension | Publisher | Capabilities |
|---|---|---|
| **Azure Account** | Microsoft | Sign in to Azure; manage subscriptions; prerequisite for most other extensions |
| **Azure Resources** | Microsoft | Browse all Azure resources in tree view; open Cloud Shell; view resource JSON |
| **Azure Functions** | Microsoft | Create/debug/deploy Function Apps; local func host integration |
| **Azure App Service** | Microsoft | Deploy web apps; manage deployment slots; stream logs |
| **Azure Databases** | Microsoft | Connect to Azure SQL, Cosmos DB, PostgreSQL, MySQL; run queries in-editor |
| **Azure Containers** | Microsoft | Manage AKS clusters, Container Registry, Container Instances |
| **Bicep** | Microsoft | IntelliSense, validation, go-to-definition, resource type completions for Bicep files |
| **Azure CLI Tools** | Microsoft | Inline documentation for az CLI commands while typing |
| **Remote - SSH** | Microsoft | SSH into Azure VMs; develop on remote environment as if local |

### Bicep Extension Features

- **IntelliSense**: Property completions based on ARM type system
- **Validation**: Real-time syntax and semantic error highlighting
- **Go to definition**: Navigate to resource type definitions
- **Resource type browser**: Explore available resource types and properties
- **Decompile**: Convert ARM JSON to Bicep in-editor
- **Parameter file support**: Linked parameter files with type validation

---

## Microsoft Dev Tunnels

**Purpose**: Expose localhost ports to the internet for webhook testing, OAuth redirect URIs, and collaboration — without deploying to a public server. The Azure-native alternative to ngrok.

### Key Capabilities

- Persistent tunnels: named tunnels with stable URLs (`https://<tunnelId>-<port>.devtunnels.ms`)
- Authentication: Tunnels can require Entra ID authentication (only team members can access)
- Anonymous/public tunnels: for simple webhook testing
- Multi-port: expose multiple local ports via a single tunnel
- VS Code integration: dev tunnels management built into VS Code Remote Tunnels
- Port forwarding: exposes local ports (HTTP, HTTPS, TCP)

```bash
# Install
winget install Microsoft.devtunnel      # Windows
brew install devtunnel                  # macOS

# Create and host a tunnel
devtunnel host --port 3000              # Expose localhost:3000

# Named persistent tunnel
devtunnel create my-webhook-tunnel
devtunnel port add my-webhook-tunnel --port-number 3000
devtunnel host my-webhook-tunnel
```
