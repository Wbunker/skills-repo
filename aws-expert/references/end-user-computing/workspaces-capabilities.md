# AWS End User Computing — Capabilities Reference

For CLI commands, see [workspaces-cli.md](workspaces-cli.md).

---

## Amazon WorkSpaces Personal

**Purpose**: Managed, persistent cloud-based virtual desktops (Windows or Linux) for individual users. Each user owns a dedicated WorkSpace that persists across sessions.

### Core Concepts

| Concept | Description |
|---|---|
| **WorkSpace** | A persistent virtual desktop assigned to a single user; backed by EBS volumes |
| **Bundle** | Hardware + software template defining the compute, storage, and OS image for a WorkSpace |
| **Directory** | AWS Directory Service directory linked to WorkSpaces; controls user authentication and group policy |
| **Running Mode** | Determines when a WorkSpace is active: AlwaysOn (always running) or AutoStop (stops after inactivity) |
| **Streaming Protocol** | PCoIP (PC over IP) or DCV (NICE DCV / WSP); controls display remoting quality and performance |
| **Root Volume** | OS and system software volume; 80 GB default; can be up to 2000 GB |
| **User Volume** | User profile and data volume (D: on Windows, /home on Linux); 50 GB default; up to 2000 GB |
| **Client App** | Native app or browser used to connect to the WorkSpace |

### Bundles

| Bundle | vCPUs | Memory | Use Case |
|---|---|---|---|
| **Value** | 1 | 2 GB | Light tasks: email, browsing, light productivity |
| **Standard** | 2 | 4 GB | Standard office work, productivity apps |
| **Performance** | 2 | 8 GB | Power users, development, heavier office apps |
| **Power** | 4 | 16 GB | Software development, data analytics, data processing |
| **PowerPro** | 8 | 32 GB | Complex software development, large data sets |
| **Graphics** | 8 vCPUs + NVIDIA GPU | 15 GB | GPU-accelerated apps; CAD, 3D modeling |
| **GraphicsPro** | 16 vCPUs + NVIDIA GPU | 122 GB | High-end GPU; advanced 3D, rendering, simulation |

Custom bundles can be created from a running WorkSpace image to standardize software deployments.

### Billing Modes

| Mode | Billing | Best For |
|---|---|---|
| **Monthly** | Flat monthly fee; WorkSpace can run 24/7 | Users who work full-time (>80 hrs/month) |
| **Hourly** | Per-hour charge while running + small monthly infrastructure fee; AutoStop required | Shift workers, occasional users, hot-desking |

Billing mode can be switched per WorkSpace at any time; change takes effect the next billing period.

### Directory Service Integration

WorkSpaces requires an AWS Directory Service directory in the same VPC (or connected via VPN/Direct Connect):

| Directory Type | Description | Use Case |
|---|---|---|
| **Simple AD** | Standalone Samba-based directory; no on-premises AD required | SMB with no existing AD infrastructure |
| **AD Connector** | Proxy that connects to an existing on-premises Microsoft AD | Enterprises with on-premises AD; users authenticate against on-prem |
| **AWS Managed Microsoft AD** | Fully managed Microsoft AD on AWS; supports trusts with on-premises AD | Enterprises needing cloud-native AD; hybrid environments |

One directory can be registered per WorkSpaces deployment per region. User accounts must exist in the linked directory.

### Running Modes

| Mode | Behavior | Billing |
|---|---|---|
| **AlwaysOn** | WorkSpace is always running; fastest connection time | Monthly billing only |
| **AutoStop** | WorkSpace stops after configurable inactivity period (default 1 hour); starts on next login | Required for hourly billing; ~2-minute start time from stopped |

### Streaming Protocols

| Protocol | Description | Strengths |
|---|---|---|
| **PCoIP** (PC over IP) | Teradici PCoIP protocol; UDP-based | Mature, broad hardware thin client support |
| **DCV** (NICE DCV / WSP) | AWS-native WorkSpaces Streaming Protocol; UDP + TCP | Better on high-latency/lossy networks; supports in-session audio input; preferred for new deployments |

Protocol is set per bundle/WorkSpace at creation; some bundles support only one protocol.

### Encryption

- **Root Volume Encryption**: Encrypts the OS volume using AWS KMS CMK
- **User Volume Encryption**: Encrypts the user data volume using AWS KMS CMK
- Encryption is configured at WorkSpace creation; cannot be enabled after launch
- Key must be in the same region as the WorkSpace

### BYOL (Bring Your Own License)

- Import your own Windows Desktop OS licenses into WorkSpaces
- Requires qualifying Microsoft volume licensing (SA with virtualization rights)
- Must create a custom BYOL image from an on-premises VM
- Account must have BYOL enabled by AWS (prerequisite: dedicated hardware)
- Enables use of Windows 10/11 images with existing Microsoft licenses

### Connection Gateway

- WorkSpaces Connection Gateway handles the front-end connection from clients to WorkSpaces
- Clients connect to gateway endpoints; gateway proxies to the WorkSpace in the VPC
- Health checks and connection monitoring are managed by the service
- Supports IP Access Control Groups to restrict which source IPs can connect

### Client Applications

| Platform | Client |
|---|---|
| Windows | WorkSpaces client app (MSI) |
| macOS | WorkSpaces client app (pkg) |
| Linux | WorkSpaces client app (Ubuntu/RHEL/Amazon Linux) |
| iOS | WorkSpaces app (App Store) |
| Android | WorkSpaces app (Google Play) |
| Web | WorkSpaces Web Access (browser-based, no client install required; limited feature set) |
| Chromebook | WorkSpaces client app (Chrome OS) |

### Key Features

- **IP Access Control Groups**: Whitelist source IP ranges allowed to connect; attached to a directory
- **Self-Service Portal**: Optional; allows users to restart, rebuild, or increase volume size without admin
- **WorkSpace Snapshots**: Automatic daily snapshots of user volume; restore available for last 2 snapshots
- **Maintenance Windows**: Weekly window for OS patching and WorkSpaces agent updates
- **Multi-Region Resilience**: Cross-region redirect using Route 53 health checks for DR scenarios
- **Smart Card Support**: Smart card authentication for CAC/PIV cards (DCV protocol, AD domain-joined)
- **FIPS Endpoints**: FIPS 140-2 compliant endpoints available for US government workloads

---

## Amazon WorkSpaces Pools

**Purpose**: Non-persistent, pooled desktops for task workers who do not need a dedicated, persistent desktop. Multiple users share a pool of WorkSpaces; sessions are stateless.

### Core Concepts

| Concept | Description |
|---|---|
| **Pool** | A collection of non-persistent WorkSpace sessions; users get a fresh desktop each session |
| **Capacity** | Minimum and maximum number of sessions in the pool; scales to meet demand |
| **Session** | A single user's active pooled desktop; terminated and reset when the user disconnects |
| **Directory** | Active Directory integration for user authentication (AD Connector or AWS Managed Microsoft AD) |
| **Image** | Custom WorkSpaces image used for all sessions in the pool |

### Key Differentiators from WorkSpaces Personal

| Feature | WorkSpaces Personal | WorkSpaces Pools |
|---|---|---|
| Persistence | Per-user persistent desktop | Non-persistent; session reset on disconnect |
| Assignment | One dedicated WorkSpace per user | Pool of desktops shared across users |
| Storage | Persistent user volume (D: drive) | No persistent local storage; use S3/file shares for data |
| Use Case | Knowledge workers, individual heavy users | Task workers, shift workers, call centers, hot-desking |
| Billing | Monthly or hourly per WorkSpace | Hourly per active session |

### Capacity Management

- **Minimum capacity**: Always-running instances to absorb immediate demand
- **Maximum capacity**: Upper limit; prevents runaway scaling costs
- **Scale-in/Scale-out**: Automatic; tracks active sessions and scales accordingly
- **Stopped capacity**: Pools can have stopped instances that start on demand (within ~2 min)

### Access and Protocols

- Web access via browser supported (no client install required)
- DCV (NICE DCV) streaming protocol
- Directory service integration for SSO and group policy application
- IP Access Control Groups supported

### Application Management

- Applications installed in the pool image (baked in at image creation)
- All users in the pool receive the same application set
- No per-user application assignment (use AppStream 2.0 for dynamic app delivery)

---

## Amazon WorkSpaces Thin Client

**Purpose**: A physical, purpose-built thin client device that pairs with AWS End User Computing services (WorkSpaces, AppStream 2.0, WorkSpaces Web). All compute runs in the cloud; the device is a zero-client endpoint.

### Hardware Specifications

| Attribute | Value |
|---|---|
| **Price** | ~$195 USD |
| **Form Factor** | Ultra-compact desktop; smaller than a paperback book |
| **Local Storage** | Zero persistent local data after session ends |
| **Connectivity** | Ethernet, Wi-Fi (optional dongle), USB ports, HDMI/DisplayPort |
| **OS** | Purpose-built, locked-down embedded Linux |

### Key Features

- **Zero local data**: Sessions stream from the cloud; no data persists on device after logout
- **Remote management**: Centrally managed via AWS WorkSpaces Thin Client console
- **OTA software updates**: Automatic OS and firmware updates pushed from AWS
- **Environment assignments**: Each device is assigned to a WorkSpaces, AppStream 2.0, or WorkSpaces Web environment
- **Device registration**: Devices register to AWS using an activation code during setup
- **Fleet management**: Manage thousands of devices from a single console; view status, update software, deregister

### Use Cases

- Replacing legacy thin clients or zero clients in call centers and retail
- Secure BYOD alternative for highly regulated industries
- Branch office desktop replacement
- Kiosk and shared workstation deployments

### Console Capabilities

- View device inventory (serial number, status, software version)
- Remotely restart or deregister devices
- Assign/reassign environment (WorkSpaces, AppStream, WorkSpaces Web)
- Push software updates
- Monitor device health and last-seen timestamps

---

## Amazon WorkSpaces Web

**Purpose**: A managed, browser-based service providing secure access to internal web applications and SaaS apps from any browser, without installing a full VDI client. Eliminates data download risk on unmanaged endpoints.

### Core Concepts

| Concept | Description |
|---|---|
| **Web Portal** | A WorkSpaces Web endpoint; users navigate to the portal URL to start a secure browser session |
| **Network Settings** | VPC, subnets, and security groups used to connect the portal to internal web resources |
| **User Access Logging** | Policy that logs user activity (URLs visited, file transfers) to an S3 bucket via Kinesis Data Firehose |
| **Browser Settings** | Policy controlling clipboard, printing, file download/upload, and other browser behaviors |
| **Trust Store** | Custom certificate authorities uploaded for internal HTTPS sites |
| **IP Access Settings** | IP allowlist controlling which source IP ranges can access the portal |

### Architecture

```
User's device (browser) → WorkSpaces Web portal URL
                         → Managed browser session runs in AWS (Fargate-like isolation)
                         → Outbound connections go through VPC to internal apps / internet
```

Each user session is isolated; no data is downloaded to the endpoint device (unless file download is explicitly permitted in browser settings).

### Network Settings

- Portal is deployed into a VPC with specified subnets and security groups
- Access to internal web apps via VPC routing (VPN, Direct Connect, or VPC peering)
- Security groups control which internal resources the browser session can reach
- Multiple portals can share network settings

### Browser Settings

| Setting | Options |
|---|---|
| Clipboard | Disabled / Copy-only / Paste-only / Enabled |
| File download | Allowed / Blocked |
| File upload | Allowed / Blocked |
| Print | Allowed / Blocked |
| Toolbar | Visible / Hidden |

### User Access Logging

- Logs per-session activity: URLs visited, file download/upload events
- Delivered to S3 via Kinesis Data Firehose (near-real-time)
- Requires an S3 bucket and Kinesis Data Firehose delivery stream
- Useful for compliance, DLP monitoring, and audit trails

### Key Features

- **No persistent storage on endpoint**: All browsing stays within the managed AWS session
- **Browser extension**: Optional WorkSpaces Web browser extension for Chrome/Firefox improves rendering performance and enables clipboard/file integration
- **SAML 2.0 / IAM Identity Center**: User authentication via IdP; no local user accounts needed
- **Session isolation**: Each user session runs in a fresh, isolated container; no session bleed between users
- **Certificates**: Upload custom CA certificates for internal sites with private PKI

---

## Amazon WorkSpaces Applications (AppStream 2.0)

**Purpose**: Application streaming service that delivers desktop applications to users in a browser, without installing apps locally. Users access applications via a URL; compute runs in AWS.

### Core Concepts

| Concept | Description |
|---|---|
| **Fleet** | A group of streaming instances that run applications and serve user sessions |
| **Stack** | A user-facing endpoint; combines a fleet with access policies, storage, and user settings |
| **Image** | An EC2-based snapshot containing the OS and installed applications for streaming |
| **Image Builder** | A temporary EC2 instance used to install apps and create a new image |
| **Application Catalog** | The set of applications exposed to users in a stack; users select which app to launch |
| **User Pool** | Built-in user directory for AppStream 2.0; email-based authentication without external IdP |
| **Session** | A single streaming session; one user connected to one instance in the fleet |
| **Persistent Storage** | Per-user S3-backed home folders that persist across sessions |

### Fleet Types

| Type | Behavior | Use Case |
|---|---|---|
| **Always-On** | Instances run 24/7; sessions connect immediately with no wait | Low-latency requirement; users expect immediate access |
| **On-Demand** | Instances start when a session is requested; ~2 min startup time | Intermittent usage; cost savings over always-on |
| **Elastic** | Instances start per-session from a base image; no pre-provisioned pool | Highly variable demand; short-duration jobs; lowest cost at scale |

### Stacks

- Each stack is associated with exactly one fleet
- Stack defines: application catalog visible to users, persistent storage settings, clipboard/file transfer policies, redirect domains (for embedded apps)
- Stack URL is shared with users; users authenticate and then launch apps from the catalog
- Multiple stacks can point to the same fleet (different access policies per user group)

### Images and Image Builders

**Image Builder workflow:**
1. Launch an Image Builder instance (temporary EC2 with AppStream agent)
2. Connect via browser or NICE DCV client
3. Install applications; configure settings
4. Use Image Assistant to catalog apps and create the image
5. Terminate Image Builder; image is stored in the account

**Image features:**
- Based on Windows Server 2019/2022 or Amazon Linux 2
- Can be shared across AWS accounts (for centralized image management)
- Versioned; fleets can be updated to new image versions
- AWS provides base images with common software pre-installed (Office, Firefox, etc.)

### Authentication

| Method | Description |
|---|---|
| **User Pool** | AppStream 2.0 built-in user directory; email invite + temporary password; no IdP required |
| **SAML 2.0 Federation** | Integrate with Okta, Azure AD, ADFS, or any SAML 2.0 IdP; SSO experience |
| **Streaming URL** | Generate a temporary signed URL for embedding AppStream into an application (API-driven) |

### Persistent Storage (Home Folders)

- Each user gets a personal S3-backed folder (mapped to `My Files > Home Folder` in the session)
- Files saved to home folder persist across sessions
- Backed by S3; can be accessed directly via S3 console for admin/backup purposes
- Optional: Google Drive and OneDrive integration (OAuth-based)
- Storage quotas configurable per stack

### Application Settings Persistence

- Windows registry, application preferences, and files in specific directories can persist across sessions
- Configured by specifying a VHD-backed settings group per stack
- Stored in S3; loaded at session start, saved at session end

### Session Scripting

- Run PowerShell or batch scripts at session start or stop events
- Use cases: mount network drives, configure user settings, load/save state, enforce DLP at logoff
- Scripts are stored in S3 and referenced in the image or fleet configuration

### Key Features

- **Smart Card Support**: CAC/PIV smart card authentication via USB redirection or in-session use
- **USB Redirection**: Forward USB devices (e.g., smart cards, specialized hardware) into the streaming session
- **Clipboard**: Configurable clipboard direction (bidirectional, copy-only, paste-only, disabled)
- **File Transfer**: Upload/download files to/from the streaming session
- **Print to Local Printer**: Via virtual print driver; redirects print jobs to user's local printer
- **Multiple Monitors**: Multi-monitor support in native client and browser
- **Embedded Streaming**: Embed AppStream sessions in web portals using the AppStream SDK
- **Usage Reports**: Daily/monthly CSV reports delivered to S3 with session-level metrics
- **Tags and Cost Allocation**: Full tagging support for cost allocation across fleets, stacks, image builders

### Instance Families for AppStream 2.0

| Family | Use Case |
|---|---|
| **stream.standard** | Standard productivity apps, Office, browsers |
| **stream.compute** | CPU-intensive apps, simulation, data processing |
| **stream.memory** | Memory-intensive apps, financial modeling, large datasets |
| **stream.graphics-design** | GPU-accelerated design apps (NVIDIA Quadro): CAD, 3D modeling |
| **stream.graphics-pro** | High-performance GPU (NVIDIA Tesla): advanced rendering, VFX |
| **stream.graphics-g4dn** | NVIDIA T4 GPU: ML inference, moderate graphics workloads |

### Networking

- Fleets are deployed into a VPC; specify subnets for streaming instances
- Instances can access internal resources via VPC routing
- Internet access: configure a NAT gateway or internet gateway for outbound connectivity
- If no internet access is needed, use VPC endpoints for AWS service calls

### Capacity and Scaling

- Minimum and maximum fleet capacity set in the fleet configuration
- Auto-scaling policies based on capacity utilization (percentage of available sessions used)
- Scale-out adds instances; scale-in terminates idle instances (after configurable idle timeout)
- Elastic fleet: no pre-provisioned capacity; instances spawn per-session

---

## End User Computing — Decision Guide

| Requirement | Recommended Service |
|---|---|
| Individual user needs a persistent, full Windows/Linux desktop | WorkSpaces Personal |
| Task workers sharing desktops, no persistent data needed | WorkSpaces Pools |
| Stream specific applications (not full desktop) to any browser | AppStream 2.0 (WorkSpaces Applications) |
| Secure access to internal websites/SaaS only, no local install | WorkSpaces Web |
| Replace physical thin clients with a managed cloud endpoint device | WorkSpaces Thin Client |
| Kiosk/shared station with zero persistent local data | WorkSpaces Thin Client + WorkSpaces Web or AppStream 2.0 |
| Embed app streaming in your own web portal | AppStream 2.0 (Streaming URL API) |
| CAD / 3D rendering / GPU workloads for individuals | WorkSpaces Personal (Graphics/GraphicsPro bundle) |
| GPU app streaming without dedicated desktop | AppStream 2.0 (stream.graphics family) |
