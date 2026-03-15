# Dataproc — CLI Reference

---

## Clusters

```bash
# Create a standard cluster (basic)
gcloud dataproc clusters create my-cluster \
  --region=us-central1 \
  --zone=us-central1-a \
  --master-machine-type=n2-standard-4 \
  --master-boot-disk-size=500GB \
  --num-workers=3 \
  --worker-machine-type=n2-standard-8 \
  --worker-boot-disk-size=500GB \
  --image-version=2.1-debian11 \
  --project=my-project

# Create cluster with optional components and Cloud Storage connector
gcloud dataproc clusters create analytics-cluster \
  --region=us-central1 \
  --master-machine-type=n2-standard-4 \
  --num-workers=5 \
  --worker-machine-type=n2-standard-8 \
  --image-version=2.1-debian11 \
  --optional-components=JUPYTER,FLINK \
  --enable-component-gateway \
  --bucket=my-staging-bucket \
  --temp-bucket=my-temp-bucket \
  --properties="spark:spark.executor.memory=6g,spark:spark.driver.memory=4g" \
  --initialization-actions=gs://my-bucket/init-scripts/install-packages.sh \
  --project=my-project

# Create High Availability cluster (3 masters)
gcloud dataproc clusters create ha-cluster \
  --region=us-central1 \
  --num-masters=3 \
  --master-machine-type=n2-standard-8 \
  --num-workers=10 \
  --worker-machine-type=n2-standard-16 \
  --image-version=2.1-debian11 \
  --project=my-project

# Create cluster with preemptible secondary workers
gcloud dataproc clusters create cost-efficient-cluster \
  --region=us-central1 \
  --master-machine-type=n2-standard-4 \
  --num-workers=4 \
  --worker-machine-type=n2-standard-8 \
  --num-secondary-workers=8 \
  --secondary-worker-type=spot \
  --image-version=2.1-debian11 \
  --project=my-project

# Create cluster with Kerberos (security)
gcloud dataproc clusters create secure-cluster \
  --region=us-central1 \
  --master-machine-type=n2-standard-4 \
  --num-workers=3 \
  --worker-machine-type=n2-standard-8 \
  --image-version=2.1-debian11 \
  --enable-kerberos \
  --kerberos-root-principal-password-uri=gs://my-bucket/kerberos/password.encrypted \
  --kerberos-kms-key=projects/my-project/locations/us-central1/keyRings/my-ring/cryptoKeys/my-key \
  --project=my-project

# Create cluster in private VPC (no external IPs)
gcloud dataproc clusters create private-cluster \
  --region=us-central1 \
  --master-machine-type=n2-standard-4 \
  --num-workers=3 \
  --worker-machine-type=n2-standard-8 \
  --no-address \
  --subnet=projects/my-project/regions/us-central1/subnetworks/my-subnet \
  --image-version=2.1-debian11 \
  --project=my-project

# Create cluster with Dataproc Metastore
gcloud dataproc clusters create metastore-cluster \
  --region=us-central1 \
  --master-machine-type=n2-standard-4 \
  --num-workers=3 \
  --worker-machine-type=n2-standard-8 \
  --image-version=2.1-debian11 \
  --dataproc-metastore=projects/my-project/locations/us-central1/services/my-metastore \
  --project=my-project

# Create cluster with autoscaling policy
gcloud dataproc clusters create autoscaling-cluster \
  --region=us-central1 \
  --master-machine-type=n2-standard-4 \
  --num-workers=2 \
  --worker-machine-type=n2-standard-8 \
  --autoscaling-policy=my-autoscaling-policy \
  --image-version=2.1-debian11 \
  --project=my-project

# Describe a cluster
gcloud dataproc clusters describe my-cluster \
  --region=us-central1 \
  --project=my-project

# List clusters
gcloud dataproc clusters list \
  --region=us-central1 \
  --project=my-project

# List clusters across all regions
gcloud dataproc clusters list --region=global --project=my-project

# Update cluster: resize workers
gcloud dataproc clusters update my-cluster \
  --region=us-central1 \
  --num-workers=10 \
  --project=my-project

# Update cluster: add secondary workers
gcloud dataproc clusters update my-cluster \
  --region=us-central1 \
  --num-secondary-workers=5 \
  --project=my-project

# Update cluster: apply new autoscaling policy
gcloud dataproc clusters update my-cluster \
  --region=us-central1 \
  --autoscaling-policy=new-policy \
  --project=my-project

# Diagnose cluster (collects logs for support)
gcloud dataproc clusters diagnose my-cluster \
  --region=us-central1 \
  --project=my-project

# Delete cluster
gcloud dataproc clusters delete my-cluster \
  --region=us-central1 \
  --project=my-project
```

---

## Jobs

```bash
# Submit a PySpark job
gcloud dataproc jobs submit pyspark gs://my-bucket/scripts/my_job.py \
  --cluster=my-cluster \
  --region=us-central1 \
  -- --input=gs://my-bucket/input/ --output=gs://my-bucket/output/

# Submit a Spark job (JAR)
gcloud dataproc jobs submit spark \
  --cluster=my-cluster \
  --region=us-central1 \
  --class=com.example.MyMainClass \
  --jars=gs://my-bucket/jars/my-app.jar,gs://my-bucket/jars/dependency.jar \
  -- --arg1=value1 --arg2=value2

# Submit a Spark SQL job (from file)
gcloud dataproc jobs submit spark-sql \
  --cluster=my-cluster \
  --region=us-central1 \
  --file=gs://my-bucket/queries/my_query.sql \
  -- --hiveconf hive.mapred.supports.subdirectories=true

# Submit a Hive job
gcloud dataproc jobs submit hive \
  --cluster=my-cluster \
  --region=us-central1 \
  --file=gs://my-bucket/hive/create_tables.hql

# Submit a Hive query inline
gcloud dataproc jobs submit hive \
  --cluster=my-cluster \
  --region=us-central1 \
  --execute="SELECT COUNT(*) FROM my_table WHERE dt='2024-01-01'"

# Submit a Hadoop MapReduce job
gcloud dataproc jobs submit hadoop \
  --cluster=my-cluster \
  --region=us-central1 \
  --class=org.apache.hadoop.examples.WordCount \
  --jars=file:///usr/lib/hadoop-mapreduce/hadoop-mapreduce-examples.jar \
  -- gs://my-bucket/input/text/ gs://my-bucket/output/wordcount/

# Submit a Pig job
gcloud dataproc jobs submit pig \
  --cluster=my-cluster \
  --region=us-central1 \
  --file=gs://my-bucket/pig/my_script.pig

# Submit a Presto/Trino query
gcloud dataproc jobs submit presto \
  --cluster=my-cluster \
  --region=us-central1 \
  --execute="SELECT * FROM hive.default.my_table LIMIT 10"

# Submit a Flink job
gcloud dataproc jobs submit flink \
  --cluster=my-cluster \
  --region=us-central1 \
  --jar=gs://my-bucket/jars/my-flink-job.jar \
  --class=com.example.FlinkJob

# Describe a job
gcloud dataproc jobs describe JOB_ID \
  --region=us-central1 \
  --project=my-project

# List jobs for a cluster
gcloud dataproc jobs list \
  --cluster=my-cluster \
  --region=us-central1 \
  --project=my-project

# List jobs by state
gcloud dataproc jobs list \
  --region=us-central1 \
  --state-filter=RUNNING \
  --project=my-project

# Wait for a job to complete (blocks; returns exit code)
gcloud dataproc jobs wait JOB_ID \
  --region=us-central1 \
  --project=my-project

# Cancel a job
gcloud dataproc jobs cancel JOB_ID \
  --region=us-central1 \
  --project=my-project

# Kill a job (force cancel)
gcloud dataproc jobs kill JOB_ID \
  --region=us-central1 \
  --project=my-project
```

---

## Workflow Templates

```bash
# Create an empty workflow template
gcloud dataproc workflow-templates create my-workflow \
  --region=us-central1 \
  --project=my-project

# Add a managed cluster to the workflow
gcloud dataproc workflow-templates set-managed-cluster my-workflow \
  --region=us-central1 \
  --cluster-name=wf-cluster \
  --master-machine-type=n2-standard-4 \
  --worker-machine-type=n2-standard-8 \
  --num-workers=3 \
  --image-version=2.1-debian11

# Add jobs to the workflow (with step IDs and dependencies)
gcloud dataproc workflow-templates add-job pyspark \
  --workflow-template=my-workflow \
  --region=us-central1 \
  --step-id=ingest \
  -- gs://my-bucket/scripts/ingest.py \
  -- --date=2024-01-01

gcloud dataproc workflow-templates add-job pyspark \
  --workflow-template=my-workflow \
  --region=us-central1 \
  --step-id=transform \
  --start-after=ingest \
  -- gs://my-bucket/scripts/transform.py

gcloud dataproc workflow-templates add-job spark-sql \
  --workflow-template=my-workflow \
  --region=us-central1 \
  --step-id=aggregate \
  --start-after=transform \
  --file=gs://my-bucket/queries/aggregate.sql

# List workflow templates
gcloud dataproc workflow-templates list \
  --region=us-central1 \
  --project=my-project

# Describe a workflow template (shows jobs and DAG)
gcloud dataproc workflow-templates describe my-workflow \
  --region=us-central1 \
  --project=my-project

# Instantiate (run) a workflow template
gcloud dataproc workflow-templates instantiate my-workflow \
  --region=us-central1 \
  --project=my-project

# Instantiate with parameters
gcloud dataproc workflow-templates instantiate my-workflow \
  --region=us-central1 \
  --parameters=DATE=2024-01-01,ENV=production \
  --project=my-project

# Delete a workflow template
gcloud dataproc workflow-templates delete my-workflow \
  --region=us-central1 \
  --project=my-project
```

---

## Autoscaling Policies

```bash
# Create autoscaling policy from YAML file
cat > autoscaling-policy.yaml << 'EOF'
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
    scaleUpFactor: 1.0
    scaleDownFactor: 1.0
    scaleUpMinWorkerFraction: 0.0
    scaleDownMinWorkerFraction: 0.0
    gracefulDecommissionTimeout: 1h
EOF

gcloud dataproc autoscaling-policies import my-autoscaling-policy \
  --region=us-central1 \
  --source=autoscaling-policy.yaml \
  --project=my-project

# List autoscaling policies
gcloud dataproc autoscaling-policies list \
  --region=us-central1 \
  --project=my-project

# Describe an autoscaling policy
gcloud dataproc autoscaling-policies describe my-autoscaling-policy \
  --region=us-central1 \
  --project=my-project

# Delete an autoscaling policy
gcloud dataproc autoscaling-policies delete my-autoscaling-policy \
  --region=us-central1 \
  --project=my-project
```

---

## Dataproc Serverless Batches

```bash
# Submit a Serverless PySpark batch job
gcloud dataproc batches submit pyspark gs://my-bucket/scripts/my_job.py \
  --region=us-central1 \
  --deps-bucket=gs://my-bucket/deps/ \
  --version=2.1 \
  --project=my-project \
  -- --input=gs://my-bucket/input/ --output=gs://my-bucket/output/

# Submit Serverless Spark job (JAR)
gcloud dataproc batches submit spark \
  --region=us-central1 \
  --deps-bucket=gs://my-bucket/deps/ \
  --class=com.example.MyMainClass \
  --jars=gs://my-bucket/jars/my-app.jar \
  --version=2.1 \
  --project=my-project

# Submit Serverless PySpark with custom container image
gcloud dataproc batches submit pyspark gs://my-bucket/scripts/my_job.py \
  --region=us-central1 \
  --container-image=us-central1-docker.pkg.dev/my-project/dataproc/my-custom-image:latest \
  --project=my-project

# Submit Serverless Spark SQL
gcloud dataproc batches submit spark-sql \
  --region=us-central1 \
  --deps-bucket=gs://my-bucket/deps/ \
  --file=gs://my-bucket/queries/my_query.sql \
  --project=my-project

# Submit Serverless SparkR
gcloud dataproc batches submit spark-r gs://my-bucket/scripts/my_script.R \
  --region=us-central1 \
  --deps-bucket=gs://my-bucket/deps/ \
  --project=my-project

# List Serverless batch jobs
gcloud dataproc batches list \
  --region=us-central1 \
  --project=my-project

# Describe a Serverless batch job
gcloud dataproc batches describe BATCH_ID \
  --region=us-central1 \
  --project=my-project

# Cancel a Serverless batch job
gcloud dataproc batches cancel BATCH_ID \
  --region=us-central1 \
  --project=my-project

# Delete a completed Serverless batch job record
gcloud dataproc batches delete BATCH_ID \
  --region=us-central1 \
  --project=my-project
```

---

## Dataproc Metastore

```bash
# Create a Dataproc Metastore service
gcloud metastore services create my-metastore \
  --location=us-central1 \
  --tier=DEVELOPER \
  --hive-metastore-version=3.1.2 \
  --project=my-project

# Create Enterprise tier metastore with CMEK
gcloud metastore services create prod-metastore \
  --location=us-central1 \
  --tier=ENTERPRISE \
  --hive-metastore-version=3.1.2 \
  --network=my-vpc \
  --kms-key=projects/my-project/locations/us-central1/keyRings/my-ring/cryptoKeys/my-key \
  --project=my-project

# List metastore services
gcloud metastore services list \
  --location=us-central1 \
  --project=my-project

# Describe a metastore service
gcloud metastore services describe my-metastore \
  --location=us-central1 \
  --project=my-project

# Delete a metastore service
gcloud metastore services delete my-metastore \
  --location=us-central1 \
  --project=my-project
```

---

## IAM for Dataproc

```bash
# Grant Dataproc Editor role
gcloud projects add-iam-policy-binding my-project \
  --member="serviceAccount:dataproc-sa@my-project.iam.gserviceaccount.com" \
  --role="roles/dataproc.editor"

# Grant Dataproc Worker role to the cluster's service account
gcloud projects add-iam-policy-binding my-project \
  --member="serviceAccount:dataproc-sa@my-project.iam.gserviceaccount.com" \
  --role="roles/dataproc.worker"

# Key IAM roles:
# roles/dataproc.admin   - full control of all Dataproc resources
# roles/dataproc.editor  - create, update, delete clusters and jobs
# roles/dataproc.viewer  - read-only access
# roles/dataproc.worker  - service account role for cluster VMs (access GCS, Logging, Monitoring)
```
