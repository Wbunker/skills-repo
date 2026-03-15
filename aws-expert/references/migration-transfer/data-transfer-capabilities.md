# AWS Data Transfer — Capabilities Reference

For CLI commands, see [data-transfer-cli.md](data-transfer-cli.md).

## AWS DataSync

**Purpose**: Managed online data transfer service for moving large amounts of data between on-premises storage (NFS, SMB, HDFS, object storage) and AWS storage services, and between AWS storage services. Automates scheduling, monitoring, verification, and bandwidth throttling.

### Core Concepts

| Concept | Description |
|---|---|
| **Agent** | VM deployed in your on-premises environment (VMware ESXi, KVM, Hyper-V) or cloud provider; connects DataSync to on-premises storage |
| **Agentless** | For AWS-to-AWS transfers (S3-to-S3, EFS-to-EFS, FSx-to-FSx); no agent needed |
| **Location** | A specific storage endpoint (NFS share, SMB share, S3 bucket, EFS, FSx, etc.) used as source or destination |
| **Task** | Defines a transfer: source location, destination location, options (verification, bandwidth throttle, filters) |
| **Task execution** | A single run of a task; has its own status, metrics, and logs |
| **Transfer verification** | DataSync verifies data integrity by comparing checksums at source and destination after transfer |

### Supported Locations

| Location Type | Direction | Agent Required |
|---|---|---|
| **NFS share (on-premises)** | Source or Destination | Yes |
| **SMB share (on-premises)** | Source or Destination | Yes |
| **HDFS (Hadoop)** | Source | Yes |
| **S3-compatible (on-premises, other clouds)** | Source or Destination | Yes |
| **Amazon S3** | Source or Destination | No (for AWS-to-AWS) |
| **Amazon EFS** | Source or Destination | No |
| **Amazon FSx for Windows File Server** | Source or Destination | No (agent for on-prem source) |
| **Amazon FSx for Lustre** | Destination | No |
| **Amazon FSx for NetApp ONTAP** | Source or Destination | No |
| **Amazon FSx for OpenZFS** | Source or Destination | No |
| **Azure Blob Storage** | Source (agentless, preview) | No |
| **Google Cloud Storage** | Source (agentless, via S3-compatible) | Yes |

### Task Configuration Options

| Option | Description |
|---|---|
| **VerifyMode** | `ONLY_FILES_TRANSFERRED` (verify transferred files), `ALL` (verify all), `NONE` (skip) |
| **OverwriteMode** | `ALWAYS` (overwrite existing), `NEVER` (skip existing) |
| **PreserveDeletedFiles** | `PRESERVE` (keep files on destination that were deleted on source) or `REMOVE` |
| **TransferMode** | `CHANGED` (only changed files), `ALL` (all files every run) |
| **BytesPerSecond** | Bandwidth throttle limit (-1 = no limit) |
| **Posix permissions** | Copy file owner, group, permissions (for NFS/HDFS sources) |
| **Timestamps** | Preserve mtime |
| **Logging** | CloudWatch log group for task execution logs |

### Scheduling

- Tasks can be scheduled with a cron expression or run manually via console, CLI, or EventBridge trigger
- Multiple executions of the same task cannot run in parallel; a new execution is queued if another is running

### Filtering

- **Include filters**: Transfer only files matching specified patterns (glob syntax)
- **Exclude filters**: Skip files matching specified patterns
- Filters apply to both the source scan and the transfer

### Agent Deployment

| Platform | Image Type |
|---|---|
| VMware ESXi | OVA |
| KVM | QCOW2 |
| Microsoft Hyper-V | VHD |
| Amazon EC2 | AMI (for cloud-to-cloud with agent) |

Agent activation: after deploying the VM, activate via console or CLI using an activation key bound to your AWS account and region. Agents communicate with DataSync service over TCP 443.

### Bandwidth Throttling

- Set at the task level in bytes per second
- Can be dynamically adjusted via `update-task-execution` while a task is running
- Useful for off-hours acceleration or daytime throttling to protect production traffic

### Transfer Verification Details

DataSync uses a two-phase verification:
1. **During transfer**: Checksum (SHA-256) calculated on blocks during transfer and verified at destination
2. **Post-transfer (optional)**: Full directory scan comparing source and destination checksums

---

## AWS Snow Family

**Purpose**: Physical devices for offline bulk data transfer to and from AWS, and for edge computing in disconnected or bandwidth-constrained environments. AWS ships the device to your location, you load data, and ship it back (or run compute workloads on the device).

### Device Comparison

| Feature | Snowcone HDD | Snowcone SSD | Snowball Edge Storage Optimized | Snowball Edge Compute Optimized | Snowmobile |
|---|---|---|---|---|---|
| **Usable Storage** | 8 TB HDD | 14 TB SSD | 80 TB S3-compatible | 28 TB NVMe | Up to 100 PB |
| **vCPUs (EC2)** | 4 | 4 | 104 vCPU (optional) | 52 vCPU | N/A |
| **Memory** | 4 GB | 4 GB | 416 GB (compute option) | 208 GB | N/A |
| **GPU** | No | No | No | Optional NVIDIA V100 | No |
| **Networking** | 1 GbE / Wi-Fi | 1 GbE / Wi-Fi | 25 GbE / 100 GbE | 25 GbE / 100 GbE | Dedicated fiber |
| **Form factor** | Small, ruggedized (2.1 kg) | Small, ruggedized | Rack-mountable sled | Rack-mountable sled | Semi-truck |
| **Typical use** | Edge IoT, remote sites | Edge with more storage | Large-scale data migration | ML inference at edge | Exabyte migration |

### Snowcone

- Smallest Snow device; fits in a backpack
- Can be deployed with or without internet connectivity
- **AWS DataSync agent pre-installed**: transfer data online via DataSync after loading
- Supports offline transfer (ship back) and online transfer (DataSync over internet)
- IoT Greengrass and edge compute capabilities
- Battery-powered option available

### Snowball Edge Storage Optimized

- Primary device for large-scale data migration
- 80 TB usable S3-compatible storage
- **Standard option**: 40 vCPU, 80 GB RAM (for basic EC2 workloads)
- **Compute option**: 104 vCPU, 416 GB RAM, 7.68 TB NVMe SSD (for intensive edge compute)
- Supports S3-compatible API, NFS, and EFS interfaces locally
- Can be clustered (5–10 devices) for larger migrations and HA

### Snowball Edge Compute Optimized

- For intensive edge compute (ML, analytics, media processing)
- 28 TB NVMe usable storage + 1 TB SSD for EC2 root volumes
- Optional NVIDIA Tesla V100 GPU
- 52 vCPU, 208 GB RAM
- Supports EC2-compatible instances, S3-compatible API, NFS

### Snowmobile

- Exabyte-scale data migration: up to 100 PB per Snowmobile
- 45-foot shipping container pulled by a semi-truck
- AWS personnel deliver, set up, and manage the transfer
- High-bandwidth connection to your datacenter (up to 1 Tbps)
- AWS Security: GPS tracking, 24/7 video surveillance, security escort, tamper-resistant design
- Use when migration would take over 10 years over network, or > 10 PB to move

### OpsHub GUI

- Desktop application (Windows/macOS) to manage Snow devices locally
- Manage device unlock, file browser, start/stop services
- Launch EC2 instances on device
- View device metrics, network configuration
- No internet connection required

### Edge Compute Capabilities

All Snowball Edge and Snowcone devices support:
- **EC2-compatible instances**: Run AMIs locally (sbe-c.xlarge, sbe-g.xlarge, etc.)
- **AWS Lambda on Greengrass**: Trigger Lambda functions from local events
- **Amazon S3-compatible API**: Local S3 for apps on the device
- **NFS interface**: Mount device storage as NFS from other local machines

### Device Clustering

- 5 to 10 Snowball Edge Storage Optimized devices can be clustered
- Provides increased storage capacity and durability (N+2 redundancy)
- Data distributed and replicated across cluster nodes
- Single failure domain per device; cluster tolerates up to 2 device failures

### Job Lifecycle

1. Create a job in the Snow Family console
2. AWS ships device to your address
3. Receive device, connect to network, unlock with credentials from Snowball console
4. Transfer data (AWS S3 CLI, OpsHub, NFS mount, or direct copy)
5. Power off device, apply shipping label (displayed on E-Ink screen), ship back
6. AWS receives device, imports data to S3, and certificate of data destruction provided

### Pricing

- Per-job fee + per-day fee after 10 free days
- Long-term pricing: 1-year or 3-year committed pricing for Snowball Edge devices deployed for extended periods

---

## AWS Transfer Family

**Purpose**: Managed SFTP, FTPS, FTP, and AS2 server that stores files directly in Amazon S3 or Amazon EFS. Enables legacy file transfer workflows to move to cloud storage without changing client software.

### Core Concepts

| Concept | Description |
|---|---|
| **Server** | Managed endpoint that accepts SFTP/FTPS/FTP/AS2 connections; backed by S3 or EFS |
| **User** | An identity that can connect to the server; has a home directory and IAM role for S3/EFS access |
| **SSH public key** | Used for SFTP authentication (key-based); stored per user |
| **Identity provider** | How users are authenticated: Service Managed, AWS Directory Service (AD/LDAP), Amazon Cognito, or custom Lambda |
| **Workflow** | Post-upload processing steps triggered automatically after a file is fully uploaded |
| **Connector** | Outbound SFTP or AS2 connector for sending files to external trading partners |
| **Agreement** | AS2 trading partner agreement defining certificates, message format, and MDN settings |

### Supported Protocols

| Protocol | Port | Storage Backend | Use Case |
|---|---|---|---|
| **SFTP** (SSH FTP) | 22 (customizable) | S3 or EFS | Secure file transfer; most common; key or password auth |
| **FTPS** (FTP over TLS) | 21 (implicit/explicit) | S3 or EFS | Legacy FTP clients that require TLS; certificate-based server identity |
| **FTP** (plain) | 21 | S3 or EFS | Internal VPC-only transfers; not recommended for internet-facing |
| **AS2** (Applicability Statement 2) | 443 or custom | S3 | EDI/B2B file transfer; signed and encrypted payloads; MDN receipts |

### Identity Providers

| Type | Description |
|---|---|
| **Service Managed** | AWS Transfer manages users; SSH keys or passwords stored in Transfer Family console |
| **AWS Managed Active Directory** | Authenticate users via Microsoft AD or AWS Managed AD; LDAP-based |
| **Custom Lambda** | Lambda function called at authentication; can integrate with any IdP (LDAP, RADIUS, existing DB) |
| **Amazon Cognito** | User pools for SFTP; supports web identity federation; FTPS/SFTP only |

### User Configuration

| Setting | Description |
|---|---|
| **Home directory** | Mapped to a path in S3 (`/bucket-name/prefix`) or EFS (`/efs/mount/path`) |
| **Home directory type** | `PATH` (direct path) or `LOGICAL` (chroot-like mapping; hides real S3 paths from user) |
| **IAM role** | Role assumed by the user's session; must allow `s3:GetObject`, `s3:PutObject`, etc. |
| **SSH public keys** | Up to 50 SSH public keys per user for SFTP key-based auth |
| **Policy scoping** | Session policy to further restrict S3 access for the user |
| **POSIX profile** | UID, GID, secondary GIDs for EFS-backed servers (EFS uses POSIX permissions) |

### Managed Workflows

Workflows execute after a successful upload. Steps execute sequentially:

| Step Type | Description |
|---|---|
| **Copy** | Copy file to another S3 location |
| **Tag** | Add S3 object tags |
| **Delete** | Delete the original upload (after copy step, for move operations) |
| **Custom Lambda** | Invoke a Lambda for custom processing (virus scan, format validation, ETL) |
| **Decrypt** | PGP decrypt a file uploaded to S3 |

Exception handlers: each step can have an exception handler (another workflow step) to handle failures.

### Connectors

**SFTP Connector**: Send files outbound to external SFTP servers from S3. Trigger via Lambda, EventBridge, or direct API call.

**AS2 Connector**: Send AS2 messages to trading partners. Configure partner certificates, signing, and encryption. MDN (Message Disposition Notification) confirms receipt.

### AS2 Details

- Inbound: AS2 messages sent to your Transfer Family AS2 server endpoint; payload stored in S3
- Outbound: Send S3 files to partners via AS2 Connector
- **Agreement**: Defines local and partner profiles (certificates, encryption algorithms)
- **Profile**: Your identity (certificate + private key); can be local or partner profile
- MDN responses: synchronous or asynchronous; stored in S3
- Supported algorithms: SHA-1, SHA-256 (signing); AES-128, AES-256, 3DES (encryption)

### Networking Options

| Option | Description |
|---|---|
| **Public endpoint** | Internet-facing; AWS-managed IP addresses; supports all protocols |
| **VPC endpoint (internet-facing)** | Elastic IPs in your VPC; fixed IPs; internet-accessible |
| **VPC endpoint (internal)** | Private IPs only; accessible only within VPC or via Direct Connect/VPN |

### Monitoring & Logging

- **CloudWatch metrics**: BytesIn, BytesOut, FilesIn, FilesOut, InboundMessage (AS2)
- **CloudWatch Logs**: Per-server, per-user log groups for all file transfer activities
- **EventBridge events**: Upload started, upload completed, workflow step completed/failed
- **Server access logging**: Detailed log of all API and protocol-level access
