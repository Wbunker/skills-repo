# Azure Batch — Capabilities Reference

For CLI commands, see [batch-cli.md](batch-cli.md).

## Azure Batch

**Purpose**: Cloud-scale parallel and high-performance computing (HPC) job scheduling. Azure Batch manages the provisioning and lifecycle of compute nodes, job scheduling, task distribution, and automatic scaling. Ideal for: rendering, video transcoding, financial simulation, scientific modeling, genomics, and any embarrassingly parallel workload.

---

## Core Architecture

### Account

An Azure Batch account is the top-level resource. It ties to a storage account (for task inputs/outputs and application packages) and optionally a user subscription (for node VMs in your own subscription).

| Pool Allocation Mode | Description |
|---|---|
| **Batch Service (default)** | Nodes are provisioned in Azure-managed subscriptions; simpler but less visibility |
| **User Subscription** | Nodes appear in your Azure subscription; required for certain VM types and for networking with your VNets |

### Pools

A pool is a collection of compute nodes (VMs) that tasks run on.

| Property | Description |
|---|---|
| **VM Configuration** | Uses Azure Marketplace images (Ubuntu, Windows Server, CentOS) or custom images from Compute Gallery |
| **Cloud Service Configuration** | Legacy Windows-only; deprecated |
| **VM size** | Any Azure VM size; use H-series for MPI, N-series for GPU, D/F-series for general HPC |
| **Node count** | Fixed count or auto-scale formula-driven |
| **OS disk** | Managed disk; ephemeral supported for select sizes |
| **Node image** | Azure Marketplace, custom from Shared Image Gallery, or container image |
| **Container support** | Run tasks as Docker containers; requires pool with container configuration |
| **Application packages** | Pre-stage ZIP packages to nodes at pool creation or task execution |
| **Start task** | Script run on every node when it joins the pool (install software, mount shares) |
| **Certificate references** | Install certificates from Azure Key Vault on nodes |
| **Inter-node communication** | Enable for MPI workloads; requires placement on InfiniBand-capable VMs |

### Node Types

| Type | Description | Use Case |
|---|---|---|
| **Dedicated nodes** | Reserved capacity; not preempted | Production, SLA-sensitive workloads |
| **Low-priority / Spot nodes** | Up to 80% discount; can be preempted by Azure | Fault-tolerant batch, rendering, dev/test |

Node requeue behavior on preemption: Batch automatically requeues tasks from preempted nodes if configured.

### Jobs

A job is a collection of tasks with shared configuration (priority, pool association, job manager).

| Property | Description |
|---|---|
| **Pool** | Target pool for tasks; can use auto-pool (create/delete with job) |
| **Priority** | -1000 to 1000; higher priority jobs get nodes first |
| **Job Manager task** | Special task run automatically when job starts; coordinates job execution |
| **Job preparation task** | Run on each node before any task of the job; stage input data, environment setup |
| **Job release task** | Run on each node after all tasks complete; cleanup, aggregate outputs |
| **Termination condition** | Job terminates when all tasks complete, or manually |

### Tasks

A task is the unit of work — a command line or container run on a single node.

| Property | Description |
|---|---|
| **Command line** | Executable + arguments run on the compute node |
| **Resource files** | Input files downloaded to the node before task execution |
| **Output files** | Files uploaded to Blob Storage after task completes |
| **Environment variables** | Key-value pairs injected as environment variables |
| **Max retry count** | Number of times a task is retried on failure |
| **Max wall clock time** | Maximum duration; task killed if exceeded |
| **User identity** | Run as auto-user (admin or non-admin) or named user |
| **Container settings** | Run task in a Docker container with specified image, registry, and options |

---

## Task Dependencies

Azure Batch supports task dependency graphs:

- **Single task dependency**: Task B runs only after Task A completes
- **Task ID range dependency**: Task C runs after all tasks in ID range [A, B] complete
- **Task collection dependency**: Task D runs after specific list of tasks complete

Use `--depends-on` at task creation to define dependencies.

---

## Multi-Instance Tasks (MPI)

Multi-instance tasks run a coordinated task across multiple nodes — required for MPI workloads:

| Component | Description |
|---|---|
| **Primary task** | Runs on one node; launches MPI job (mpirun, mpiexec) |
| **Subtasks** | Run on remaining nodes; wait for primary signal |
| **Coordination command** | Run on all nodes before primary starts (e.g., copy input data) |
| **Application command** | MPI application command run on primary |
| **Number of instances** | Total nodes to use (1 primary + N-1 subtasks) |

Requirements:
- Pool must have `interNodeCommunication` enabled
- VMs must support InfiniBand or at least fast Ethernet (H-series for IB, HB-series for AMD)
- Pool must be in User Subscription mode for most HPC networking configurations

---

## Application Packages

Pre-built ZIP archives deployed to pool nodes automatically:

- Upload package ZIP to Batch account (backed by Azure Storage)
- Reference package and version in pool or task configuration
- Extracted to `AZ_BATCH_APP_PACKAGE_<name>_<version>` environment variable path
- Supports versioning; multiple versions can coexist

---

## Automatic Node Scaling

Auto-scale uses formulas (a domain-specific language) evaluated on a schedule (minimum 5 minutes):

```
// Example auto-scale formula: scale based on pending tasks
$samples = $PendingTasks.GetSamplePercent(TimeInterval_Minute * 15);
$tasks = $samples < 70 ? max(0, $PendingTasks.GetSample(1)) : max($PendingTasks.GetSample(1));
$targetDedicated = min(200, max(0, $tasks));
```

| Built-in variables | Description |
|---|---|
| `$PendingTasks` | Number of tasks in active or running state waiting for a node |
| `$ActiveTasks` | Tasks queued or preparing to run |
| `$RunningTasks` | Tasks currently executing |
| `$SucceededTasks` | Tasks completed successfully in interval |
| `$FailedTasks` | Tasks that failed in interval |
| `$CurrentDedicatedNodes` | Current dedicated node count |
| `$TargetDedicatedNodes` | Output: desired dedicated node count |
| `$TargetLowPriorityNodes` | Output: desired low-priority node count |

---

## Integration with Azure Storage

- **Resource files**: Download blobs from Blob Storage to nodes before task execution (auto-storage account linked to Batch account)
- **Output files**: Upload task stdout, stderr, and output files to Blob Storage after completion
- **Application packages**: Backed by Blob Storage in linked storage account
- **Managed identity**: Grant Batch pool nodes managed identity with Storage Blob Data Reader/Contributor for secure access

---

## Rendering

Azure Batch supports cloud rendering with pre-built marketplace images for:

- **Autodesk Maya / 3ds Max** with Arnold, V-Ray
- **Chaos V-Ray Standalone**
- **Blender**
- **Houdini**
- Custom rendering software via custom images

Batch Explorer (GUI tool) provides a rendering-specific UX for job submission and monitoring.

---

## Batch Explorer and Tools

| Tool | Description |
|---|---|
| **Batch Explorer** | Desktop GUI for managing pools, jobs, and tasks; monitoring node activity |
| **Azure Portal** | Basic management; job/task status; pool metrics |
| **Azure CLI** | Full management via `az batch` commands |
| **Azure SDK** | .NET, Python, Java, Node.js, Go SDKs for programmatic job submission |
| **REST API** | Direct HTTP API; used by all SDKs |
| **Shipyard** | Open-source tool for Docker-based Batch workloads with YAML recipes |

---

## Monitoring

| Metric | Description |
|---|---|
| **Pool metrics** | Node count (dedicated / low-priority), target vs. current, resizing |
| **Task metrics** | Active, running, succeeded, failed task counts |
| **Node diagnostics** | Node state transitions, start task failures, evictions |
| **Application logging** | Task stdout/stderr saved to storage or streamed during execution |
| **Azure Monitor** | Batch emits metrics and logs to Azure Monitor; configure alerts on failures |
