# Windows 365 & Remote Desktop Services — Capabilities Reference
For CLI commands, see [w365-rds-cli.md](w365-rds-cli.md).

## Windows 365 (Cloud PC)

**Purpose**: Fixed-spec, persistent Cloud PCs provisioned on a per-user, per-month subscription. Unlike AVD, Windows 365 requires no infrastructure management — Microsoft provisions and manages everything; IT manages via Intune.

### Core Characteristics

| Characteristic | Windows 365 | Azure Virtual Desktop |
|---|---|---|
| **Pricing model** | Fixed per-user/month (predictable) | Pay-per-use (session host VMs) |
| **Session type** | Personal only (dedicated Cloud PC per user) | Pooled or personal |
| **Management** | Microsoft Intune (same as physical PCs) | AVD portal + Intune |
| **Infrastructure** | Zero (Microsoft-managed) | Session host VMs to manage |
| **Scaling** | Add/remove licenses (per user) | Add/remove session host VMs |
| **GPU** | Available (GPU-enabled Cloud PCs) | NV-series VMs |
| **Customization** | Provisioning policies, gallery images | Full VM customization |

### Editions

| Edition | Target | Features |
|---|---|---|
| **Business** | SMBs (up to 300 users) | Simple setup; no AD domain join; Azure AD only |
| **Enterprise** | Large organizations | Full features; Hybrid Azure AD join; custom images; custom VNet |
| **Frontline** | Shift workers / shared use | Shared Cloud PCs; time-limited sessions; lower cost per user |

### Cloud PC Specifications

| Spec | Options | Notes |
|---|---|---|
| **vCPU** | 2, 4, 8, 16, 32 vCPU | Choose based on workload needs |
| **RAM** | 4–128 GB | Paired with vCPU selection |
| **Storage** | 64–512 GB SSD | OS + user data |
| **GPU** | NVIDIA T4 (available add-on) | For graphics-intensive work |

### Provisioning Policy

- **Azure AD join**: No domain controller needed; Intune for management; Microsoft-hosted network or customer VNet
- **Hybrid Azure AD join**: Requires AD domain controller reachable from provisioned Cloud PC's VNet
- **Image**: Windows 11 gallery images or custom images from Azure Compute Gallery
- **Network**: Microsoft-hosted (no VNet required) or customer-managed VNet (for private resource access)
- **User experience**: Web browser (`windows365.microsoft.com`) or Windows App client

### Cloud PC Lifecycle Management

| Action | Description |
|---|---|
| **Provision** | Assign W365 license to user; Cloud PC provisioned within minutes/hours |
| **Reprovision** | Factory reset; wipes user data; re-provisions from provisioning policy image |
| **Resize** | Change Cloud PC spec (CPU/RAM/storage) |
| **Restore** | Restore from a snapshot (point-in-time recovery) |
| **End grace period** | User's Cloud PC in grace period after license removed; end to immediately deprovision |
| **Restart/Troubleshoot** | Remote actions from Intune; connectivity diagnostics |

### Windows 365 Frontline

- Shared Cloud PCs for shift workers (one Cloud PC shared across multiple users)
- Users sign in/out; sessions end when user signs out (non-persistent)
- More cost-effective for workers who only use Cloud PC for specific shifts
- Requires Enterprise license; configured differently from standard Enterprise Cloud PCs

---

## Remote Desktop Services (RDS) on Azure VMs

**Purpose**: Bring-your-own traditional RDS infrastructure deployed on Azure VMs. Appropriate when Windows 365 or AVD don't meet requirements (legacy infrastructure, specific RDS features, existing RDS licensing/expertise).

### RDS Architecture on Azure

| Role | Description | VM SKU Guidance |
|---|---|---|
| **RD Session Host** | Users connect and run applications | D/E series (scale to user count) |
| **RD Connection Broker** | Load balancer and session routing | D2/D4s for small; D8s for large |
| **RD Web Access** | Web interface for RDS Web Feed | B2ms or D2s (lightweight) |
| **RD Gateway** | Secure HTTPS tunnel from internet to RD Session Hosts | D2/D4s + public IP |
| **RD Licensing** | Per-device/per-user CAL management | Small VM (D2s) |

### Deployment Approach

1. **Domain**: Deploy AD Domain Services on Azure VMs or use Azure AD DS
2. **Networking**: VNet with internal subnets for each role; RD Gateway in DMZ subnet with NSG
3. **Storage**: Azure Files or Azure NetApp Files for user profiles (UPD or FSLogix)
4. **High Availability**:
   - Session Hosts: Multiple VMs + Connection Broker load balancing
   - Connection Broker: SQL Server database backend for HA; deploy in active/passive pair
   - Gateway: Azure Load Balancer across multiple RD Gateway instances
5. **Automation**: ARM templates or Bicep for repeatable deployment; DSC for role installation

### RDS Licensing

| License Type | Description |
|---|---|
| **Per Device CAL** | One CAL per client device; device can be used by multiple users |
| **Per User CAL** | One CAL per user; user can use any device |
| **External Connector** | For non-employees accessing RDS from the internet |

> Note: RDS CALs must be installed on RD Licensing Server within 120-day grace period.

### DSC for Role Installation

```powershell
# Example DSC configuration for RD Session Host
Configuration RDSSessionHost {
    Import-DscResource -ModuleName PSDesiredStateConfiguration

    Node "SessionHost01" {
        WindowsFeature RDSSessionHost {
            Name = "RDS-RD-Server"
            Ensure = "Present"
        }
        WindowsFeature RDSLicensing {
            Name = "RDS-Licensing"
            Ensure = "Present"
        }
    }
}
```

---

## Citrix DaaS on Azure

**Purpose**: Citrix Cloud Desktop as a Service using Azure as the resource layer. Citrix Cloud provides the control plane (Citrix Virtual Apps and Desktops service); Azure provides compute for session hosts.

### Architecture

- **Citrix Cloud**: Citrix-managed control plane (Delivery Controllers, Citrix Gateway, StoreFront equivalent)
- **Citrix Cloud Connector**: Small VM deployed in customer Azure subscription; connects cloud control plane to Azure VMs
- **Machine Catalog**: Group of Azure VMs (managed by Citrix); created from master image
- **Delivery Group**: Assignment of apps/desktops to users from machine catalogs
- **Citrix Gateway**: Secure remote access via Citrix Gateway service (cloud-managed) or on-premises

### Advantages Over Native AVD/RDS

- Advanced HDX protocol: superior multimedia, graphics, USB redirection vs RDP
- Mature session recording and monitoring (Citrix Director)
- Multi-cloud/on-prem unified management
- MCS (Machine Creation Services): fast VM provisioning from master image

---

## VMware Horizon on Azure

**Purpose**: VMware Horizon Cloud (next-gen) uses Azure as the compute layer; VMware Unified Access Gateway (UAG) and Horizon Control Plane provide the management and connectivity layer.

### Architecture

- **Horizon Control Plane**: VMware Cloud-managed; no customer-deployed control plane VMs required
- **VMware Edge**: Lightweight edge appliance (Azure VM) in customer subscription
- **Desktop pools**: Azure VMs managed by Horizon; Windows 10/11 or Server
- **VMware Blast Extreme**: High-performance display protocol (superior multimedia vs RDP)
- **Universal Broker**: Cloud-based brokering; users assigned to pods/sessions globally

### When to Choose VMware Horizon

- Existing VMware Horizon on-prem investment extending to Azure
- VMware Blast Extreme protocol requirement
- Unified management of on-premises and Azure desktops from single console
- Multi-cloud strategy (Azure + AWS + GCP + on-prem)
