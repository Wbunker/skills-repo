# Cloud Batch — Capabilities Reference

CLI reference: [cloud-batch-cli.md](cloud-batch-cli.md)

## Purpose

Fully managed batch processing service on GCP VMs. Cloud Batch provisions, manages, and autoscales compute resources required for batch jobs—no cluster to maintain. Jobs define what to run (containers or scripts), resource requirements, and execution parameters. Cloud Batch handles VM provisioning, task scheduling, retries, and cleanup.

---

## Core Concepts

| Concept | Description |
|---|---|
| Job | Top-level resource representing a batch workload. Contains one or more task groups. Has a lifecycle: queued → running → succeeded/failed. |
| Task group | A group of identical tasks within a job. All tasks in a group share the same runnable configuration, resource requirements, and retry policy. |
| Task | A single unit of work within a task group. Each task gets a unique index (`BATCH_TASK_INDEX` env var, 0-based). Typically processes one input item. |
| Runnable | The executable unit within a task. Can be a container image, a script (inline or from GCS), or a barrier (synchronization point). Multiple runnables per task run sequentially. |
| Allocation policy | Specifies how VMs are provisioned: machine type, disk, location, network, provisioning model (standard vs Spot). Defined at the job level. |
| Job queue | Jobs are queued and scheduled by Cloud Batch based on available capacity and quota. No explicit queue management needed. |
| Resource allowance | A quota mechanism that limits the total resource consumption (CPU hours) of jobs tagged with the allowance. Used for budget enforcement. |
| Task environment variables | `BATCH_TASK_INDEX` (0-based task index), `BATCH_TASK_COUNT` (total tasks in group), `BATCH_JOB_UID` (unique job ID). Available in all runnables. |
| Parallelism | Number of tasks running simultaneously. `parallelism` ≤ `taskCount`. Determines how many VMs are provisioned. |

---

## VM Provisioning

### Machine Types
Cloud Batch supports any Compute Engine machine type. Common choices:
- `e2-standard-4` — cost-efficient general-purpose batch
- `n2-standard-8` — compute-balanced workloads
- `c3-standard-8` — compute-intensive, high-frequency clock
- `n2d-standard-16` — AMD EPYC for cost-sensitive CPU workloads
- Custom machine types via `machineType: custom-N-MEMORY`

### Spot VMs
Set `provisioningModel: SPOT` in the allocation policy for 60-91% discount. Cloud Batch handles preemption: tasks interrupted by preemption are retried automatically on new VMs (up to `maxRetryCount`). Suitable for fault-tolerant batch workloads.

### Local SSD
Attach ephemeral NVMe Local SSDs for high-throughput scratch space. Specify `localSsds` in the allocation policy. Data is lost when the VM is deleted but provides much higher I/O than persistent disks during the job.

### GPU Support
Specify `accelerators` (e.g., NVIDIA A100, V100, T4) in the allocation policy. GPU drivers can be installed via container image or startup script. Required for ML preprocessing and inference batch jobs.

### Network
- Default: external IP, public internet access
- Private: no external IP, access resources via Cloud NAT or VPC routing

---

## Job Structure (JSON/YAML)

```json
{
  "taskGroups": [
    {
      "taskCount": 100,
      "parallelism": 10,
      "taskSpec": {
        "runnables": [
          {
            "container": {
              "imageUri": "us-central1-docker.pkg.dev/my-project/my-repo/my-batch:latest",
              "commands": ["/app/process"],
              "args": ["--input", "gs://my-bucket/inputs/$(BATCH_TASK_INDEX).json",
                       "--output", "gs://my-bucket/outputs/$(BATCH_TASK_INDEX).json"]
            }
          }
        ],
        "computeResource": {
          "cpuMilli": 2000,
          "memoryMib": 4096
        },
        "maxRetryCount": 3,
        "maxRunDuration": "1800s"
      }
    }
  ],
  "allocationPolicy": {
    "instances": [
      {
        "policy": {
          "machineType": "n2-standard-4",
          "provisioningModel": "SPOT",
          "disks": [
            {
              "newDisk": {
                "type": "pd-ssd",
                "sizeGb": 100
              },
              "deviceName": "data-disk"
            }
          ]
        }
      }
    ],
    "location": {
      "allowedLocations": ["regions/us-central1"]
    },
    "serviceAccount": {
      "email": "my-batch-sa@my-project.iam.gserviceaccount.com"
    }
  },
  "logsPolicy": {
    "destination": "CLOUD_LOGGING"
  }
}
```

---

## Integration with GCP Services

### Cloud Storage
- **Inputs**: pass GCS URIs as task arguments (`gs://bucket/input-$(BATCH_TASK_INDEX).json`). Mount GCS buckets as FUSE filesystems via `gcsfuse` in the container.
- **Outputs**: write results to GCS from within the task container. GCS is the primary output mechanism.
- **Scripts**: reference startup scripts hosted in GCS via `gcsPath` in the runnable script definition.

### Cloud Logging
Set `logsPolicy.destination = CLOUD_LOGGING` to stream stdout/stderr from all task containers to Cloud Logging. Each log entry is tagged with job name, task group index, and task index. Filter in Cloud Logging:
```
resource.type="batch.googleapis.com/Job" AND labels.job_name="my-batch-job"
```

### Pub/Sub Notifications
Configure `notifications` in the job spec to publish job state changes (QUEUED, RUNNING, SUCCEEDED, FAILED) to a Pub/Sub topic. Enables downstream event-driven workflows.

### Cloud Monitoring
Cloud Batch emits metrics to Cloud Monitoring:
- `batch.googleapis.com/job/task_count` — tasks by state
- `batch.googleapis.com/job/running_task_count` — currently running tasks
- Use these for dashboards and alerting on job progress.

---

## Use Cases

| Use Case | Description |
|---|---|
| ML data preprocessing | Parallelize feature extraction, image resizing, or tokenization across large datasets stored in GCS |
| Model training jobs | Distributed training with GPU nodes; each task handles a shard of training data |
| Video transcoding | Transcode each video file in a GCS bucket in parallel, output to another bucket |
| Genomic processing | Run bioinformatics tools (BWA, GATK) per sample in parallel on Spot VMs |
| Financial batch calculations | End-of-day risk calculation or settlement processing over thousands of accounts |
| ETL pipeline steps | Heavy transformation steps not suitable for Dataflow (arbitrary binaries, no Apache Beam) |
| Log analysis | Process compressed log files from GCS in parallel, output aggregated reports |

---

## Cloud Batch vs Dataflow

| Signal | Cloud Batch | Dataflow |
|---|---|---|
| Programming model | Any container or script; arbitrary code | Apache Beam pipelines (Java/Python/Go) |
| Streaming support | No (batch only) | Yes (streaming + batch unified model) |
| Data processing paradigm | Task-parallel (each task processes a partition) | Data-parallel (transforms applied to PCollections) |
| Pre-existing Beam pipelines | N/A | Yes |
| Custom binaries/tools | Yes (any executable in a container) | Limited (must fit into Beam transforms) |
| Auto-scaling during job | Fixed parallelism per job | Dynamic work rebalancing |
| Shuffle | Manual (task assigns its own partition) | Managed Dataflow shuffle |
| Best for | Arbitrary batch workloads, HPC, ML training | Streaming ETL, Beam pipelines, log processing |

---

## Important Patterns & Constraints

- **Task idempotency**: tasks may be retried on preemption or failure. Design task code to be idempotent (safe to run multiple times with the same input).
- **`BATCH_TASK_INDEX` for input partitioning**: use the task index to select the appropriate input partition (e.g., line range in a file, object at index N in a list).
- **Service account required**: the job's `allocationPolicy.serviceAccount` must have permissions to access Cloud Storage, pull container images from Artifact Registry, and write to Cloud Logging.
- **Artifact Registry for images**: use Artifact Registry (not Docker Hub) for private container images to avoid rate limiting and ensure GCP-native IAM access control.
- **Max task count**: up to 1 million tasks per job. For larger workloads, use multiple jobs.
- **Max parallelism**: up to 5,000 simultaneous VMs per job. Subject to project CPU quota.
- **Max task duration**: up to 7 days per task (`maxRunDuration`).
- **Spot VM preemption handling**: set `maxRetryCount` to allow automatic retry on preemption. Use `SPOT_TASK_FAILED` in exit codes to distinguish preemption from application errors.
- **Container image size**: large images slow down task startup; use multi-stage builds and keep images lean. Pre-pull by using a startup script or smaller base image.
- **No persistent inter-task state**: tasks share nothing by default. Coordinate via Cloud Storage or Firestore if tasks need to share progress or results.
- **Log lag**: Cloud Logging from batch tasks may have a few seconds of lag; do not kill a job immediately after it finishes and check logs immediately.
