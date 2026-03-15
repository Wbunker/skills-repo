# AWS Batch — Capabilities Reference

For CLI commands, see [batch-cli.md](batch-cli.md).

## AWS Batch

**Purpose**: Fully managed batch computing service that provisions and scales EC2 (or Fargate) compute resources, dynamically schedules batch jobs, and optimizes for throughput and cost.

### Core Concepts

| Concept | Description |
|---|---|
| **Job** | Unit of work submitted to a job queue; runs as a containerized task (ECS or EKS) |
| **Job definition** | Template for a job: container image, vCPU/memory, IAM role, timeout, retry strategy, mount points |
| **Job queue** | Ordered queue jobs wait in; associated with one or more compute environments by priority |
| **Compute environment** | Pool of compute resources (EC2 or Fargate) that processes jobs from queues |
| **Scheduling policy** | Fair-share scheduling configuration; controls how jobs share compute across job queues |

### Compute Environment Types

| Type | Description |
|---|---|
| **Managed (EC2)** | AWS provisions and scales EC2 instances automatically; supports Spot and On-Demand |
| **Managed (Fargate)** | AWS provisions Fargate tasks; no EC2 to manage; simpler ops |
| **Unmanaged** | You provision and manage EC2 instances; register them to the compute environment |

### Job Types

| Type | Description |
|---|---|
| **Single job** | Standard containerized job with vCPU/memory requirements |
| **Array job** | One submission creates N child jobs; each child gets an `AWS_BATCH_JOB_ARRAY_INDEX`; useful for parameter sweeps |
| **Multi-node parallel (MNP)** | Multiple nodes work together on one job; one main node + N child nodes; requires EFA-capable instances for MPI workloads |

### Scheduling

- Jobs in a queue are processed in FIFO order by default
- **Fair-share scheduling**: Distribute compute equitably across multiple job queues/users using share identifiers and weights
- **Job dependencies**: `dependsOn` field creates directed acyclic graph (DAG) of job execution order
- **Priority**: Multiple compute environments per queue with ordered priorities

### Key Constraints

- Batch uses ECS or EKS under the hood; containers must be in ECR or another registry
- Multi-node parallel jobs require a placement group (cluster) for low-latency networking
- Fargate compute environments do not support GPU or multi-node parallel jobs
