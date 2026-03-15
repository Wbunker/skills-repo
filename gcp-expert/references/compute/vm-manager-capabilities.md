# VM Manager — Capabilities Reference

For CLI commands, see [vm-manager-cli.md](vm-manager-cli.md).

## VM Manager

**Purpose**: Suite of OS management tools for Compute Engine VMs at fleet scale — including OS patching, OS configuration enforcement, and OS inventory collection.

### Core Concepts

| Concept | Description |
|---|---|
| **OS Patch Management** | Automates patch application across GCE VM fleets; supports Linux and Windows; patch jobs and patch deployments (schedules) |
| **OS Config** | Enforces desired-state OS configuration using guest policies (software installation, file management, script execution) |
| **OS Inventory** | Collects and reports installed packages, package updates available, kernel version, and OS details from VMs |
| **OS Policy** | Newer replacement for guest policies; define OS policies (ensure package installed, file present, etc.) and assign via OS Policy Assignments to VM groups |
| **Patch Job** | One-time or ad-hoc patching operation targeting a filter of VMs |
| **Patch Deployment** | Scheduled recurring patch job (cron-based); defines patch config, instance filter, and schedule |
| **Patch Config** | Defines which patches to apply: all, critical only, security only; package manager options (apt/yum/zypper/Windows Update) |
| **OS Config Agent** | Agent running on each VM (included in most GCP images); communicates with VM Manager service |
| **Compliance Report** | Inventory-based report showing patch compliance status across fleet |

### OS Patch Management

#### Patch Job Targets
Filter VMs by: all instances in project, zone, instance name prefix, or label selector.

#### Patch Config Options

| Category | Options |
|---|---|
| **Linux (apt)** | All upgrades, security updates only, custom apt-get args |
| **Linux (yum)** | All updates, security only, minimal, custom exclusions |
| **Linux (zypper)** | All patches, security category, severity filter |
| **Windows Update** | All updates, critical only, security only, definition only; pre/post patch scripts |
| **Pre/Post scripts** | Run scripts before or after patching (stored in Cloud Storage) |

#### Patch Rollout Strategies
- **Zone-by-zone**: patch one zone at a time; configurable disruption budget
- **Concurrent zones**: patch % of zones simultaneously
- **Disruption budget**: max % of VMs that can be patched simultaneously per zone (avoid full zone outage)

#### Reboot Configuration
Options: always reboot, never reboot, reboot if required.

### OS Config (Guest Policies / OS Policies)

#### OS Policy Types
- **VALIDATION mode**: check compliance without enforcing (report only)
- **ENFORCEMENT mode**: actively apply configuration; remediate drift

#### OS Policy Resources
- **Package**: ensure package is installed or absent (apt, yum, zypper, MSI, deb, rpm, googet)
- **Repository**: add/manage package repositories
- **File**: ensure file content matches (template from Cloud Storage or inline)
- **Exec**: run script if condition met (check + enforce scripts)

#### OS Policy Assignment
Assign OS policies to VMs using:
- Label selectors (`env=prod`, `os=ubuntu`)
- Rollout policy (% of VMs per time window to avoid fleet-wide disruption)
- Rollout disruption budget (max concurrent VMs under policy change)

### OS Inventory

Collected data per VM:
- OS name, version, kernel version
- Installed packages (name, version, architecture)
- Available package updates (name, current version, available version)
- Last collection timestamp

Data retention: 60 days in VM Manager; export to Cloud Storage or BigQuery for longer retention.

### IAM Requirements

| Role | Purpose |
|---|---|
| `roles/osconfig.patchJobExecutor` | Execute patch jobs |
| `roles/osconfig.patchJobViewer` | View patch jobs |
| `roles/osconfig.osPolicyAssignmentAdmin` | Manage OS policy assignments |
| `roles/osconfig.osPolicyAssignmentViewer` | View OS policies |
| `roles/osconfig.inventoryViewer` | View OS inventory data |

### VM Requirements
- OS Config agent installed (pre-installed on all GCP-provided Debian, Ubuntu, RHEL, CentOS, SLES, and Windows images from 2019+)
- Metadata server access (no external IP needed if Private Google Access enabled)
- Service account with `roles/osconfig.inventoryViewer` or VM metadata scopes

### When to Use VM Manager

- **OS patching at scale**: automate monthly/weekly patching across hundreds or thousands of GCE VMs
- **Compliance auditing**: verify all VMs are on current patch baseline for SOC 2, PCI DSS, or internal security policy
- **Configuration drift detection**: ensure specific packages are installed/absent across a VM group
- **Inventory reporting**: generate software inventory for audits, license tracking, or SBOM
- **Pre/post patch hooks**: run test suites before/after patching to catch regressions

### Important Patterns & Constraints

- VM Manager is enabled per-project via the `osconfig.googleapis.com` API
- The OS Config agent reports to the regional VM Manager endpoint; VMs in any zone are supported
- OS Policies (newer API) replace Guest Policies; new implementations should use OS Policies
- Patch jobs that exceed the disruption budget will pause until VMs return to healthy state
- Pre/post patch scripts must be stored in Cloud Storage and referenced by `gs://` URI
- Windows VMs require the `google-cloud-ops-agent` or legacy `google-osconfig-agent` service running
- Inventory collection runs every ~10 minutes by default; not real-time
- Maximum patch job targets: no hard limit, but large fleets (10,000+ VMs) should use zone-by-zone rollout
