# Azure Virtual Desktop — Capabilities Reference
For CLI commands, see [avd-cli.md](avd-cli.md).

## Azure Virtual Desktop (AVD)

**Purpose**: Managed Virtual Desktop Infrastructure (VDI) service on Azure. Run Windows 10/11 Enterprise multi-session (exclusive to Azure) or single-session desktops, and stream individual apps (RemoteApp) — without managing RDS infrastructure.

### Why AVD vs Traditional VDI

| Aspect | Traditional On-prem VDI | Azure Virtual Desktop |
|---|---|---|
| Infrastructure | Customer-managed servers, brokers | Microsoft-managed control plane |
| Windows multi-session | Not available commercially | Windows 11 Enterprise multi-session (Azure exclusive) |
| Scaling | Manual; slow | Autoscale based on schedule or demand |
| DR/HA | Complex and expensive | Azure zone-redundancy + geo-redundancy |
| Licensing | Separate VDI CAL required | Included in M365 E3/E5, F3, A3/A5, Business Premium |
| Cost | CapEx + OpEx | Pure OpEx; session hosts billed only when running |

---

## Core Architecture

### Components

| Component | Description |
|---|---|
| **Host pool** | Collection of session host VMs with same configuration; unit of management and scaling |
| **Session host** | Azure VM running AVD client software; users connect to these |
| **Application group** | Collection of apps or desktops published to users |
| **Workspace** | Logical grouping of application groups; what users subscribe to |
| **FSLogix profile container** | Roaming user profile stored in Azure Files / Azure NetApp Files |

### Host Pool Types

| Type | Description | Use Case |
|---|---|---|
| **Pooled** | Multiple users share session host VMs; load balanced | Knowledge workers; office apps; standardized desktops |
| **Personal** | Each user assigned a dedicated VM | Power users; developers; GPU workloads; persistent customizations |

### Application Group Types

| Type | Description |
|---|---|
| **Desktop** | Full Windows desktop experience (one desktop app group per host pool) |
| **RemoteApp** | Individual applications streamed to user (appear as local windows) |

### Workspace

- Users subscribe to a workspace URL or via Windows App / Microsoft Remote Desktop
- Workspace aggregates multiple application groups
- One workspace can span multiple host pools (pooled + personal)

---

## Session Host Configuration

### Windows Editions

| Edition | Sessions per VM | Notes |
|---|---|---|
| **Windows 11 Enterprise multi-session** | Multiple concurrent users | Azure-exclusive; most cost-efficient for pooled |
| **Windows 11 Enterprise** | Single user | Personal host pools; full enterprise features |
| **Windows Server** | Multiple concurrent users | When existing licensing justifies; fewer features than Win11 multi-session |

### VM Sizing Recommendations

| Use Case | Recommended VM | Notes |
|---|---|---|
| Light (office, web, email) | D4as_v5 / 4 vCPU | 6–10 users per VM |
| Medium (LOB apps, light analytics) | D8as_v5 / 8 vCPU | 4–6 users per VM |
| Heavy (rendering, dev, analytics) | D16as_v5 or NV-series | 2–4 users per VM; NV for GPU |
| GPU graphics workloads | NV6, NV12s_v3, NC4as_T4_v3 | NVIDIA GRID or vGPU; AMD |

### Domain Join Options

| Method | Requirements | Notes |
|---|---|---|
| **Microsoft Entra ID join** | No AD domain controller needed; Intune management | Modern management; recommended for cloud-only orgs |
| **Microsoft Entra Hybrid join** | On-premises AD + Azure AD Connect | Existing on-prem AD environments |
| **Active Directory Domain Services** | Domain controller reachable from VNet | Legacy; required for certain apps needing on-prem AD |

---

## FSLogix Profile Containers

**Purpose**: Roam user profiles (AppData, registry hive, Outlook OST files) across different session hosts. Essential for pooled host pools where users land on different VMs.

### How It Works

1. User signs in to a session host
2. FSLogix agent mounts the user's VHD(x) from Azure Files/ANF as a local disk
3. User profile directory is redirected to the mounted VHD(x)
4. User experience is identical to a persistent local profile
5. On sign-out, VHD(x) is unmounted; changes persisted to storage

### Storage Options

| Storage | Performance | Use Case |
|---|---|---|
| **Azure Files Standard** | Moderate | Small-to-medium deployments; cost-effective |
| **Azure Files Premium** | High IOPS | 50+ concurrent users; faster profile load times |
| **Azure NetApp Files** | Highest | Enterprise scale; regulated industries; highest performance |

### Key FSLogix Settings

| Setting | Description |
|---|---|
| `VHDLocations` | UNC path(s) to storage where profile VHDs are stored |
| `Enabled` | Enable FSLogix Profile Container (set to 1) |
| `DeleteLocalProfileWhenVHDShouldApply` | Remove local profile if a VHD profile exists |
| `SizeInMBs` | Default VHD size (default: 30,720 MB = 30 GB) |
| `FlipFlopProfileDirectoryName` | Use `user_SID` instead of `SID_user` for profile folder name |

---

## Scaling Plans

**Purpose**: Automatically scale session host VM count up/down based on schedule and user demand. Reduces costs by deallocating VMs during off-peak hours.

### Scaling Schedule

| Phase | Action |
|---|---|
| **Ramp-up** | Scale out to minimum capacity before business hours |
| **Peak** | Maintain adequate capacity; scale out if usage threshold exceeded |
| **Ramp-down** | Scale in when sessions drop below threshold; drain and deallocate VMs |
| **Off-peak** | Minimum capacity (can be 0 for full shutdown) |

### Scaling Algorithms

| Algorithm | Description |
|---|---|
| **Breadth-first** | Distribute users across maximum number of VMs (good for pooled) |
| **Depth-first** | Fill one VM before moving to next (reduces VMs running simultaneously — cost optimization) |

---

## Additional Features

### RDP Shortpath

- Establishes direct UDP connection between AVD client and session host
- Bypasses AVD gateway (avoids the relay); lower latency, higher throughput
- Requires: Public IP on session hosts OR managed private UDP path
- Significant improvement for users connecting over low-latency networks

### Multimedia Redirection (MMR)

- Redirects video playback from session host to client endpoint
- Offloads video decoding from session host CPU to client GPU
- Supports: YouTube, Teams video calls, general web video
- Requires: AVD client on Windows with MMR extension

### Screen Capture Protection

- Prevents screenshots/screen capture of AVD sessions from local machine
- Enforced by session host policy; protects sensitive data from screen grabs

### Azure Monitor for AVD (Insights Workbook)

- Pre-built Azure Monitor workbook for AVD monitoring
- Dashboards: Session history, connection quality, host pool utilization, user diagnostics
- Requires: Diagnostic settings sending data to Log Analytics workspace

### GPU Session Hosts

| GPU Feature | Description |
|---|---|
| **NVIDIA GRID vGPU** | Virtual GPU slices; multiple users per GPU; RemoteFX replacement |
| **NV-series VMs** | NVIDIA Tesla M60; vGPU for graphics; NV6s_v2 → NV72ads_A10_v5 |
| **NC-series VMs** | NVIDIA T4/A100; AI/ML inference on desktop |
| **AMD RX 5700 XT** | NVadsA10 v5 with AMD GPU option |
| **Required extensions** | NVIDIA GPU Driver Extension or AMD GPU Driver Extension on VM |
