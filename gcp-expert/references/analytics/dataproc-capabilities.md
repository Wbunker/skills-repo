# Dataproc — Capabilities

## Purpose

Managed Hadoop, Spark, Flink, Hive, Pig, and Presto clusters for big data processing. Dataproc is ideal for lifting and shifting existing Spark/Hadoop workloads to GCP, running Spark ML pipelines, and managing Hive workloads. Compared to Dataflow, Dataproc requires more cluster management but supports the full Spark/Hadoop ecosystem without code rewrites.

---

## Cluster Types

| Type | Description | Use Case |
|---|---|---|
| Standard | Persistent cluster with 1 master + N workers | Long-running or frequently-used clusters |
| Single Node | 1 VM acting as master and worker | Development, testing, small workloads |
| High Availability | 3 masters + N workers | Production workloads requiring master fault tolerance |
| Dataproc Serverless | No cluster; submit Spark batch/streaming jobs directly | Cost-efficient; no cluster management overhead |
| Dataproc on GKE | Spark jobs run on existing GKE cluster | Consolidate infrastructure; share node pool resources |

---

## Core Concepts

| Concept | Description |
|---|---|
| Cluster | Group of master + worker VMs running Hadoop YARN and HDFS (or Cloud Storage connector) |
| Master node | NameNode, ResourceManager, YARN HistoryServer; 1 (standard) or 3 (HA) |
| Worker node | DataNode, NodeManager; primary workers (standard VMs) + secondary (preemptible or Spot) |
| Preemptible worker | Lower-cost secondary worker using preemptible VMs; for non-critical batch work |
| Spot worker | Secondary worker using Spot VMs (successor to preemptible); significant cost savings |
| Job | Workload submitted to cluster: Hadoop MapReduce, Spark, PySpark, SparkR, SparkSQL, Hive, Pig, Presto/Trino, Flink |
| Initialization action | Shell script executed on all nodes at cluster creation; install packages, configure services |
| Custom image | Pre-built VM image with additional software; faster cluster startup than init actions |
| Component | Optional software pre-installed on cluster (Jupyter, Zeppelin, Flink, Ranger, Solr, etc.) |
| Workflow template | Reusable, parameterized DAG of Dataproc jobs; supports managed cluster creation |
| Autoscaling policy | Rules for scaling secondary workers based on YARN pending memory/vCores |
| Image version | Defines pre-installed versions of Hadoop, Spark, Hive, Pig, etc. (e.g., 2.1-debian12) |

---

## Image Versions

| Image Version | Hadoop | Spark | Notes |
|---|---|---|---|
| 2.2 | 3.3 | 3.5 | Current recommended (Debian 12 or Rocky Linux 9) |
| 2.1 | 3.3 | 3.3 | Widely used in production |
| 2.0 | 3.2 | 3.1 | Older; consider upgrading |
| 1.5 | 2.10 | 2.4 | Legacy; Hadoop 2 ecosystem |

**Specify version at creation**: `--image-version=2.1-debian11`

**Preview/custom versions**: `--image-version=2.2-debian12`

---

## Dataproc Serverless for Spark

- Submit Spark batch and streaming jobs without managing any cluster infrastructure
- Dataproc Serverless auto-provisions compute, scales during job execution, and tears down after completion
- Pay only for resources used during job execution (per-second billing)
- Supports: PySpark, Spark (Scala/Java), SparkR, Spark SQL batch jobs; Spark Structured Streaming
- Custom container images supported for dependency management
- **Limitations**: subset of Spark configurations; no Hadoop or non-Spark frameworks; longer cold start than pre-warmed clusters
- Sessions (interactive): Jupyter notebooks backed by Serverless Spark via Vertex AI Workbench integration

```bash
# Submit Serverless Spark job
gcloud dataproc batches submit pyspark gs://my-bucket/scripts/my_job.py \
  --region=us-central1 \
  --deps-bucket=gs://my-bucket/deps/ \
  --version=2.1 \
  -- --input=gs://my-bucket/input/ --output=gs://my-bucket/output/
```

---

## Dataproc on GKE

- Run Dataproc Spark workloads on GKE node pools
- Spark driver and executors run as Kubernetes pods
- Share GKE cluster infrastructure with other workloads
- Benefits: avoid dedicated cluster overhead; Kubernetes-native operations
- **Setup**: create GKE cluster, create Dataproc virtual cluster pointing to GKE, submit jobs

---

## Storage Integration

- **Cloud Storage as HDFS**: `gs://` paths work natively in place of `hdfs://`; preferred for persistent storage
- **BigQuery connector**: `com.google.cloud.spark.bigquery` (Spark) or `com.google.cloud.hadoop.io.bigquery` (Hadoop MapReduce); read/write BigQuery tables directly
- **Bigtable connector**: `com.google.cloud.bigtable.hadoop.HBaseAdapter`; use Bigtable as HBase
- **Pub/Sub connector**: Spark Structured Streaming can consume from Pub/Sub
- **HDFS on cluster**: available but ephemeral; data lost when cluster deleted; use Cloud Storage instead

---

## Autoscaling

```yaml
# Example autoscaling policy YAML
workerConfig:
  minInstances: 2
  maxInstances: 20
  weight: 1
secondaryWorkerConfig:
  maxInstances: 50
  weight: 1
basicAlgorithm:
  cooldownPeriod: 2m
  yarnConfig:
    scaleUpFactor: 1.0      # fraction of pending containers to scale up
    scaleDownFactor: 1.0    # fraction of idle workers to scale down
    scaleUpMinWorkerFraction: 0.0
    scaleDownMinWorkerFraction: 0.0
    gracefulDecommissionTimeout: 1h
```

- Scaling based on YARN `pendingMemory` and `availableMemory` metrics
- Secondary (preemptible/Spot) workers scale up/down; primary workers remain stable
- `gracefulDecommissionTimeout`: wait for in-progress tasks before removing a worker

---

## Dataproc Metastore

- Managed Apache Hive Metastore service (not a Dataproc cluster feature — standalone managed service)
- Used as shared metadata catalog for Dataproc, Dataflow, and BigQuery
- Avoids running a Hive Metastore on a Dataproc cluster
- Supports: Hive Metastore 3.1.2; BigLake Metastore (unified metadata for BigQuery + open format tables)
- **Integration**: reference in Dataproc cluster creation with `--dataproc-metastore` flag

---

## Components (Optional Software)

Enable at cluster creation with `--optional-components=`:

| Component | Description |
|---|---|
| `JUPYTER` | JupyterLab for interactive notebooks |
| `ZEPPELIN` | Apache Zeppelin notebook |
| `FLINK` | Apache Flink on YARN |
| `RANGER` | Apache Ranger for access control |
| `SOLR` | Apache Solr search platform |
| `HUDI` | Apache Hudi (for incremental data processing on Cloud Storage) |
| `DELTA` | Delta Lake (open-source storage layer) |
| `TRINO` | Trino (formerly PrestoSQL) distributed query engine |

---

## Workflow Templates

- Define a DAG of Dataproc jobs with dependencies
- Parameterized with template parameters
- Create a managed cluster for the workflow, or target existing clusters
- Instantiate on-demand or on a schedule via Cloud Scheduler

---

## Monitoring and Logging

- Cluster and job metrics in Cloud Monitoring namespace `dataproc.googleapis.com`
- YARN UI accessible via web interfaces (SSH tunnel or Cloud IAP)
- Spark History Server available at cluster web UI
- Job output and driver logs in Cloud Logging; also in GCS staging bucket
- `gcloud dataproc jobs wait JOB_ID` blocks until job completes (useful in scripts)

---

## Security

- Kerberos: enable `--enable-kerberos` for strong auth within cluster
- VPC configuration: `--network` / `--subnetwork`; private clusters with `--no-address`
- Service account: `--service-account` for GCP API access
- Shielded VMs: `--shielded-secure-boot`, `--shielded-vtpm`, `--shielded-integrity-monitoring`
- Dataproc Personal Cluster Authentication: user-level Kerberos principal mapping to Google identities
- CMEK: encrypt cluster VM disks and GCS staging bucket with Cloud KMS keys

---

## When to Use Dataproc vs Dataflow

Use **Dataproc** when:
- You have existing Spark, Hadoop, Hive, or Pig code to migrate
- You need the full Apache Spark ecosystem (MLlib, GraphX, Spark Streaming)
- You're running interactive Spark queries via notebooks
- You need HBase access patterns (via Bigtable connector)
- The team is familiar with Hadoop/Spark operations

Use **Dataflow** when:
- Building new streaming pipelines from scratch
- You want fully serverless, zero-management infrastructure
- Unified batch + streaming in one code base (Apache Beam)
- Lower operational overhead is more important than framework flexibility
