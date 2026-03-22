# Running Pig on GCP Dataproc
_Modern cloud execution — cluster setup, GCS paths, job submission, IAM, logging, cost optimization_

## Pig on Dataproc

Dataproc supports Pig as a native job type. Pig 0.17.0 is included in Dataproc images based on Hadoop 3.x.

| Dataproc Image | Pig Version | Hadoop | Notes |
|---------------|------------|--------|-------|
| 2.x (Debian/Rocky) | 0.17.0 | 3.x | Recommended |
| 1.5.x | 0.17.0 | 2.x | Legacy |

Check current: `gcloud dataproc clusters describe <name> --region=<region>`

## Create a Cluster

```bash
# Minimal cluster for Pig
gcloud dataproc clusters create pig-cluster \
  --region=us-central1 \
  --zone=us-central1-a \
  --master-machine-type=n2-standard-4 \
  --num-workers=2 \
  --worker-machine-type=n2-standard-4 \
  --image-version=2.1-debian11 \
  --optional-components=TEZ \
  --properties=pig:pig.exec.reducers.bytes.per.reducer=268435456 \
  --service-account=my-dataproc-sa@my-project.iam.gserviceaccount.com \
  --scopes=cloud-platform

# Single-node cluster for dev/testing
gcloud dataproc clusters create pig-dev \
  --region=us-central1 \
  --single-node \
  --master-machine-type=n2-standard-4 \
  --image-version=2.1-debian11
```

## Submit a Pig Job

```bash
# Submit a Pig script from GCS
gcloud dataproc jobs submit pig \
  --cluster=pig-cluster \
  --region=us-central1 \
  --file=gs://my-bucket/scripts/myscript.pig \
  -- -p DATE=2024-01-15 -p ENV=prod

# Submit inline Pig query
gcloud dataproc jobs submit pig \
  --cluster=pig-cluster \
  --region=us-central1 \
  --execute="data = LOAD 'gs://bucket/input/' USING PigStorage(',') AS (id:int); DUMP data;"

# With Tez engine
gcloud dataproc jobs submit pig \
  --cluster=pig-cluster \
  --region=us-central1 \
  --file=gs://my-bucket/scripts/myscript.pig \
  --properties=pig.exectype=tez \
  -- -p DATE=2024-01-15

# Monitor job
gcloud dataproc jobs describe <job-id> --region=us-central1

# Wait for completion
gcloud dataproc jobs wait <job-id> --region=us-central1
```

## GCS Integration

### Path Conventions

```pig
-- GCS path
data = LOAD 'gs://my-bucket/data/events/' USING PigStorage(',') AS (...);

-- With partition prefix
data = LOAD 'gs://my-bucket/data/events/dt=2024-01-15/' USING PigStorage(',') AS (...);

-- Glob pattern (Hadoop glob syntax)
data = LOAD 'gs://my-bucket/data/events/dt=2024-01-*/' USING PigStorage(',') AS (...);
multi = LOAD 'gs://my-bucket/data/{events,pageviews}/dt=2024-01-15/' USING PigStorage(',') AS (...);

-- Output
STORE result INTO 'gs://my-bucket/output/dt=2024-01-15/' USING PigStorage('\t');
```

### GCS Output Behavior

- Output directory must not exist before job (Pig fails if it does)
- GCS is eventually consistent for listing — Dataproc uses the GCS connector which handles this
- `_SUCCESS` marker file is written on successful completion

```bash
# Delete output before re-run
gsutil -m rm -r gs://my-bucket/output/dt=2024-01-15/
```

## IAM Configuration

### Service Account for Dataproc

```bash
# Create service account
gcloud iam service-accounts create dataproc-pig-sa \
  --display-name="Dataproc Pig Service Account"

# Grant GCS access (storage object admin on specific buckets)
gsutil iam ch serviceAccount:dataproc-pig-sa@PROJECT.iam.gserviceaccount.com:objectAdmin \
  gs://my-data-bucket

gsutil iam ch serviceAccount:dataproc-pig-sa@PROJECT.iam.gserviceaccount.com:objectAdmin \
  gs://my-output-bucket

# Grant Dataproc Worker role (required for cluster nodes)
gcloud projects add-iam-policy-binding PROJECT_ID \
  --member="serviceAccount:dataproc-pig-sa@PROJECT.iam.gserviceaccount.com" \
  --role="roles/dataproc.worker"
```

### Hive Metastore (Dataproc Metastore Service)

```bash
# Create a Dataproc Metastore instance
gcloud metastore services create my-metastore \
  --location=us-central1 \
  --hive-metastore-version=3.1.2

# Attach to Dataproc cluster
gcloud dataproc clusters create pig-cluster \
  --region=us-central1 \
  --dataproc-metastore=projects/PROJECT/locations/us-central1/services/my-metastore \
  ...
```

```pig
-- Then HCatLoader reads Dataproc Metastore tables
events = LOAD 'mydb.events' USING org.apache.hive.hcatalog.pig.HCatLoader();
```

## Logging and Debugging

### View Job Logs

```bash
# Stream job output
gcloud dataproc jobs wait <job-id> --region=us-central1

# Get driver output
gcloud dataproc jobs describe <job-id> --region=us-central1 --format="value(driverOutputResourceUri)"
# Returns gs://... path to log files

# Download logs
gsutil cp gs://dataproc-staging-REGION-PROJECT-RANDOM/google-cloud-dataproc-metainfo/<cluster-id>/jobs/<job-id>/driveroutput* ./logs/

# View in Cloud Logging (Stackdriver)
gcloud logging read "resource.type=cloud_dataproc_job AND resource.labels.job_id=<job-id>" \
  --format=json --limit=100
```

### Interactive Pig Shell

```bash
# SSH to master node
gcloud compute ssh <cluster-name>-m --zone=us-central1-a

# Start Pig
pig -x mapreduce
pig -x tez   # if Tez is enabled

# Run a script
pig -x mapreduce -f gs://bucket/scripts/myscript.pig -p DATE=2024-01-15
```

## Cluster Sizing Guidelines

| Data Size | Instance Type | Workers | Notes |
|-----------|--------------|---------|-------|
| Dev / < 5 GB | n2-standard-4 | 0 (single-node) | `--single-node` flag |
| 5–50 GB | n2-standard-4 | 2–4 | Standard cluster |
| 50–500 GB | n2-standard-8 | 5–15 | Consider preemptible workers |
| > 500 GB | n2-highmem-8 | 10–30 | Add preemptible secondary workers |

### Preemptible (Spot) Workers for Cost Savings

```bash
gcloud dataproc clusters create pig-cluster \
  --region=us-central1 \
  --num-workers=2 \
  --worker-machine-type=n2-standard-4 \
  --num-secondary-workers=6 \
  --secondary-worker-type=spot \
  --master-machine-type=n2-standard-4 \
  --image-version=2.1-debian11
```

## Cluster Configuration Tuning

```bash
# Pass properties at cluster creation
gcloud dataproc clusters create pig-cluster \
  --properties=\
"pig:pig.exec.reducers.bytes.per.reducer=268435456,\
pig:pig.exec.nocombiner=false,\
mapred:mapreduce.map.memory.mb=4096,\
mapred:mapreduce.reduce.memory.mb=8192,\
mapred:mapreduce.map.java.opts=-Xmx3276m,\
mapred:mapreduce.reduce.java.opts=-Xmx6553m" \
  ...
```

## Initialization Actions (Install Libraries)

```bash
# Upload a setup script to GCS
cat > setup_pig_libs.sh << 'EOF'
#!/bin/bash
gsutil cp gs://my-bucket/libs/myudfs.jar /usr/lib/pig/lib/
gsutil cp gs://my-bucket/libs/piggybank-0.17.0.jar /usr/lib/pig/lib/
EOF
gsutil cp setup_pig_libs.sh gs://my-bucket/init-actions/

# Reference in cluster creation
gcloud dataproc clusters create pig-cluster \
  --initialization-actions=gs://my-bucket/init-actions/setup_pig_libs.sh \
  --initialization-action-timeout=5m \
  ...
```

## Orchestration with GCP

### Cloud Composer (Airflow) — DataprocSubmitJobOperator

```python
from airflow.providers.google.cloud.operators.dataproc import DataprocSubmitJobOperator

pig_job = DataprocSubmitJobOperator(
    task_id='run_pig_etl',
    project_id='my-project',
    region='us-central1',
    job={
        'placement': {'cluster_name': 'pig-cluster'},
        'pig_job': {
            'query_file_uri': 'gs://my-bucket/scripts/etl.pig',
            'script_variables': {
                'DATE': '{{ ds }}',
                'ENV': 'prod',
            },
            'properties': {
                'pig.exectype': 'tez',
            },
        },
    },
)
```

### Cloud Workflows

```yaml
- submit_pig_job:
    call: http.post
    args:
      url: ${"https://dataproc.googleapis.com/v1/projects/" + project + "/regions/" + region + "/jobs:submit"}
      auth:
        type: OAuth2
      body:
        projectId: ${project}
        job:
          placement:
            clusterName: pig-cluster
          pigJob:
            queryFileUri: gs://my-bucket/scripts/etl.pig
            scriptVariables:
              DATE: ${date}
```

## Ephemeral Cluster Pattern (Recommended)

For cost efficiency, create and delete the cluster per job rather than keeping it running:

```bash
# 1. Create cluster
gcloud dataproc clusters create pig-job-$(date +%Y%m%d) \
  --region=us-central1 \
  --single-node \
  --image-version=2.1-debian11 \
  --max-age=2h \  # auto-delete after 2 hours
  ...

# 2. Submit job
gcloud dataproc jobs submit pig --cluster=pig-job-$(date +%Y%m%d) ...

# 3. Delete cluster
gcloud dataproc clusters delete pig-job-$(date +%Y%m%d) --region=us-central1 --quiet
```

Or use `--max-idle=10m` to auto-delete cluster after 10 minutes of idleness.
