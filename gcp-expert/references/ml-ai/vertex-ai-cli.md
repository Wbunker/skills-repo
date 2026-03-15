# Vertex AI Platform — CLI Reference

All `gcloud ai` commands require `--region` (Vertex AI is regional). Set a default:
```bash
gcloud config set ai/region us-central1
```

---

## Custom Training Jobs

```bash
# Create a custom training job using a pre-built container
gcloud ai custom-jobs create \
  --display-name="my-training-job" \
  --region=us-central1 \
  --worker-pool-spec=machine-type=n1-standard-8,accelerator-type=NVIDIA_TESLA_T4,accelerator-count=1,container-image-uri=us-docker.pkg.dev/vertex-ai/training/pytorch-gpu.2-2:latest \
  --args="--epochs=50,--learning-rate=0.001,--output-dir=gs://my-bucket/models/" \
  --project=PROJECT_ID

# Create a training job from a config YAML file
# config.yaml:
# displayName: my-training-job
# jobSpec:
#   workerPoolSpecs:
#     - machineSpec:
#         machineType: n1-standard-8
#         acceleratorType: NVIDIA_TESLA_T4
#         acceleratorCount: 1
#       replicaCount: 1
#       containerSpec:
#         imageUri: us-central1-docker.pkg.dev/my-project/my-repo/trainer:latest
#         args:
#           - --epochs=100
#           - --output-dir=gs://my-bucket/output/
#   baseOutputDirectory:
#     outputUriPrefix: gs://my-bucket/output/
gcloud ai custom-jobs create \
  --region=us-central1 \
  --config=config.yaml \
  --project=PROJECT_ID

# Create a distributed training job (multi-GPU, multi-node)
gcloud ai custom-jobs create \
  --display-name="distributed-training" \
  --region=us-central1 \
  --config=distributed-config.yaml \
  --project=PROJECT_ID
# distributed-config.yaml:
# jobSpec:
#   workerPoolSpecs:
#     - machineSpec:
#         machineType: a2-highgpu-8g
#       replicaCount: 1
#       containerSpec:
#         imageUri: gcr.io/my-project/my-trainer:latest
#     - machineSpec:
#         machineType: a2-highgpu-8g
#       replicaCount: 3
#       containerSpec:
#         imageUri: gcr.io/my-project/my-trainer:latest

# List custom training jobs
gcloud ai custom-jobs list \
  --region=us-central1 \
  --project=PROJECT_ID

# List with filter (running jobs only)
gcloud ai custom-jobs list \
  --region=us-central1 \
  --filter="state=JOB_STATE_RUNNING" \
  --project=PROJECT_ID

# Describe a training job
gcloud ai custom-jobs describe CUSTOM_JOB_ID \
  --region=us-central1 \
  --project=PROJECT_ID

# Stream logs from a running training job
gcloud ai custom-jobs stream-logs CUSTOM_JOB_ID \
  --region=us-central1 \
  --project=PROJECT_ID

# Cancel a running training job
gcloud ai custom-jobs cancel CUSTOM_JOB_ID \
  --region=us-central1 \
  --project=PROJECT_ID

# Delete a training job record
gcloud ai custom-jobs delete CUSTOM_JOB_ID \
  --region=us-central1 \
  --project=PROJECT_ID
```

---

## Hyperparameter Tuning Jobs

```bash
# Create a hyperparameter tuning job
# hp-config.yaml:
# displayName: hp-tuning-job
# studySpec:
#   metrics:
#     - metricId: val_accuracy
#       goal: MAXIMIZE
#   parameters:
#     - parameterId: learning_rate
#       doubleValueSpec:
#         minValue: 0.0001
#         maxValue: 0.1
#       scaleType: LOG_SCALE
#     - parameterId: batch_size
#       discreteValueSpec:
#         values: [16, 32, 64, 128]
# maxTrialCount: 20
# parallelTrialCount: 4
# trialJobSpec:
#   workerPoolSpecs:
#     - machineSpec:
#         machineType: n1-standard-4
#         acceleratorType: NVIDIA_TESLA_T4
#         acceleratorCount: 1
#       replicaCount: 1
#       containerSpec:
#         imageUri: us-central1-docker.pkg.dev/my-project/my-repo/trainer:latest
gcloud ai hp-tuning-jobs create \
  --display-name="my-hp-job" \
  --region=us-central1 \
  --config=hp-config.yaml \
  --project=PROJECT_ID

# List hyperparameter tuning jobs
gcloud ai hp-tuning-jobs list \
  --region=us-central1 \
  --project=PROJECT_ID

# Describe a HP tuning job (shows all trial results)
gcloud ai hp-tuning-jobs describe HP_JOB_ID \
  --region=us-central1 \
  --project=PROJECT_ID

# Cancel a HP tuning job
gcloud ai hp-tuning-jobs cancel HP_JOB_ID \
  --region=us-central1 \
  --project=PROJECT_ID
```

---

## Models

```bash
# List all models in a region
gcloud ai models list \
  --region=us-central1 \
  --project=PROJECT_ID

# List models with filter
gcloud ai models list \
  --region=us-central1 \
  --filter="displayName:my-classifier" \
  --format="table(name,displayName,createTime,versionId)" \
  --project=PROJECT_ID

# Describe a model (shows all versions)
gcloud ai models describe MODEL_ID \
  --region=us-central1 \
  --project=PROJECT_ID

# Upload a model artifact to the registry
gcloud ai models upload \
  --display-name="my-sklearn-classifier" \
  --region=us-central1 \
  --container-image-uri=us-docker.pkg.dev/vertex-ai/prediction/sklearn.1-3:latest \
  --artifact-uri=gs://my-bucket/model-artifacts/ \
  --container-predict-route=/predict \
  --container-health-route=/health \
  --project=PROJECT_ID

# Upload a TensorFlow SavedModel
gcloud ai models upload \
  --display-name="my-tf-model" \
  --region=us-central1 \
  --container-image-uri=us-docker.pkg.dev/vertex-ai/prediction/tf2-cpu.2-13:latest \
  --artifact-uri=gs://my-bucket/saved-model/ \
  --project=PROJECT_ID

# Upload a PyTorch model with a custom serving container
gcloud ai models upload \
  --display-name="my-pytorch-model" \
  --region=us-central1 \
  --container-image-uri=us-central1-docker.pkg.dev/my-project/my-repo/my-server:latest \
  --artifact-uri=gs://my-bucket/pytorch-model/ \
  --container-ports=8080 \
  --container-predict-route=/predict \
  --container-health-route=/health \
  --project=PROJECT_ID

# Copy a model to another project/region
gcloud ai models copy \
  --source-model=projects/SOURCE_PROJECT/locations/us-central1/models/MODEL_ID \
  --destination-model-display-name=my-model-copy \
  --region=us-east1 \
  --project=DEST_PROJECT

# Delete a model
gcloud ai models delete MODEL_ID \
  --region=us-central1 \
  --project=PROJECT_ID

# Delete a specific model version
gcloud ai models delete MODEL_ID \
  --region=us-central1 \
  --version=VERSION_ID \
  --project=PROJECT_ID
```

---

## Endpoints

```bash
# Create an endpoint
gcloud ai endpoints create \
  --display-name="my-prediction-endpoint" \
  --region=us-central1 \
  --project=PROJECT_ID

# List endpoints
gcloud ai endpoints list \
  --region=us-central1 \
  --project=PROJECT_ID

# Describe an endpoint
gcloud ai endpoints describe ENDPOINT_ID \
  --region=us-central1 \
  --project=PROJECT_ID

# Deploy a model to an endpoint (with autoscaling: min 1, max 5 replicas)
gcloud ai endpoints deploy-model ENDPOINT_ID \
  --region=us-central1 \
  --model=MODEL_ID \
  --display-name="my-deployed-model" \
  --machine-type=n1-standard-4 \
  --min-replica-count=1 \
  --max-replica-count=5 \
  --traffic-split=0=100 \
  --project=PROJECT_ID

# Deploy with GPU
gcloud ai endpoints deploy-model ENDPOINT_ID \
  --region=us-central1 \
  --model=MODEL_ID \
  --display-name="gpu-deployed-model" \
  --machine-type=n1-standard-4 \
  --accelerator=count=1,type=nvidia-tesla-t4 \
  --min-replica-count=1 \
  --max-replica-count=3 \
  --traffic-split=0=100 \
  --project=PROJECT_ID

# Update traffic split between deployed models (A/B testing)
# Assumes two deployed model IDs already on the endpoint
gcloud ai endpoints update-traffic-split ENDPOINT_ID \
  --region=us-central1 \
  --traffic-split=DEPLOYED_MODEL_ID_A=80,DEPLOYED_MODEL_ID_B=20 \
  --project=PROJECT_ID

# Undeploy a model from an endpoint (stops serving that version)
gcloud ai endpoints undeploy-model ENDPOINT_ID \
  --region=us-central1 \
  --deployed-model-id=DEPLOYED_MODEL_ID \
  --project=PROJECT_ID

# Delete an endpoint (must undeploy all models first)
gcloud ai endpoints delete ENDPOINT_ID \
  --region=us-central1 \
  --project=PROJECT_ID

# Send an online prediction request
gcloud ai endpoints predict ENDPOINT_ID \
  --region=us-central1 \
  --json-request=request.json \
  --project=PROJECT_ID
# request.json: {"instances": [{"feature1": 1.0, "feature2": "value"}]}

# Send a raw prediction (inline JSON)
gcloud ai endpoints predict ENDPOINT_ID \
  --region=us-central1 \
  --json-request='{"instances": [[1.0, 2.0, 3.0]]}' \
  --project=PROJECT_ID

# Explain a prediction (if explanation is configured)
gcloud ai endpoints explain ENDPOINT_ID \
  --region=us-central1 \
  --json-request=request.json \
  --project=PROJECT_ID
```

---

## Batch Prediction Jobs

```bash
# Create a batch prediction job (BigQuery input → BigQuery output)
gcloud ai batch-prediction-jobs create \
  --display-name="batch-predict-job" \
  --region=us-central1 \
  --model=MODEL_ID \
  --bigquery-source=bq://PROJECT_ID.my_dataset.input_table \
  --bigquery-destination-prefix=bq://PROJECT_ID.predictions_dataset \
  --machine-type=n1-standard-4 \
  --starting-replica-count=5 \
  --max-replica-count=10 \
  --project=PROJECT_ID

# Create a batch prediction job (Cloud Storage JSON Lines input → GCS output)
gcloud ai batch-prediction-jobs create \
  --display-name="batch-predict-gcs" \
  --region=us-central1 \
  --model=MODEL_ID \
  --gcs-source=gs://my-bucket/input/instances.jsonl \
  --gcs-destination-prefix=gs://my-bucket/predictions/ \
  --machine-type=n1-standard-4 \
  --project=PROJECT_ID

# List batch prediction jobs
gcloud ai batch-prediction-jobs list \
  --region=us-central1 \
  --project=PROJECT_ID

# Describe a batch prediction job
gcloud ai batch-prediction-jobs describe BATCH_JOB_ID \
  --region=us-central1 \
  --project=PROJECT_ID

# Cancel a batch prediction job
gcloud ai batch-prediction-jobs cancel BATCH_JOB_ID \
  --region=us-central1 \
  --project=PROJECT_ID

# Delete a batch prediction job
gcloud ai batch-prediction-jobs delete BATCH_JOB_ID \
  --region=us-central1 \
  --project=PROJECT_ID
```

---

## Feature Store

```bash
# Create a Feature Store (legacy API; use FeatureOnlineStore for new workloads)
gcloud ai feature-stores create my-feature-store \
  --region=us-central1 \
  --project=PROJECT_ID

# List feature stores
gcloud ai feature-stores list \
  --region=us-central1 \
  --project=PROJECT_ID

# Describe a feature store
gcloud ai feature-stores describe my-feature-store \
  --region=us-central1 \
  --project=PROJECT_ID

# Create an entity type within a feature store
gcloud ai feature-stores entity-types create user-entity-type \
  --feature-store=my-feature-store \
  --region=us-central1 \
  --description="User-level features" \
  --project=PROJECT_ID

# Create features for an entity type
gcloud ai feature-stores entity-types features create age \
  --entity-type=user-entity-type \
  --feature-store=my-feature-store \
  --region=us-central1 \
  --value-type=INT64 \
  --description="User age in years" \
  --project=PROJECT_ID

gcloud ai feature-stores entity-types features create purchase_count_30d \
  --entity-type=user-entity-type \
  --feature-store=my-feature-store \
  --region=us-central1 \
  --value-type=INT64 \
  --project=PROJECT_ID

# List features in an entity type
gcloud ai feature-stores entity-types features list \
  --entity-type=user-entity-type \
  --feature-store=my-feature-store \
  --region=us-central1 \
  --project=PROJECT_ID

# Create a Feature Group (new API)
gcloud ai feature-groups create user-features \
  --region=us-central1 \
  --big-query-source=bq://PROJECT_ID.features_dataset.user_features \
  --project=PROJECT_ID

# Create a Feature (within a Feature Group)
gcloud ai feature-groups features create user_age \
  --feature-group=user-features \
  --region=us-central1 \
  --project=PROJECT_ID

# Create a Feature Online Store (Bigtable-backed for low-latency serving)
gcloud ai feature-online-stores create my-online-store \
  --region=us-central1 \
  --bigtable-min-node-count=1 \
  --bigtable-max-node-count=5 \
  --project=PROJECT_ID

# Create a Feature View (links Feature Group to Online Store)
gcloud ai feature-online-stores feature-views create user-view \
  --feature-online-store=my-online-store \
  --region=us-central1 \
  --feature-registry-source=feature_groups=[user-features],feature_group_query_string="user_age,purchase_count_30d" \
  --sync-config-cron="0 */6 * * *" \
  --project=PROJECT_ID

# Sync a feature view (trigger manual sync)
gcloud ai feature-online-stores feature-views sync user-view \
  --feature-online-store=my-online-store \
  --region=us-central1 \
  --project=PROJECT_ID
```

---

## TensorBoard

```bash
# Create a managed TensorBoard instance
gcloud ai tensorboards create \
  --display-name="my-tensorboard" \
  --region=us-central1 \
  --project=PROJECT_ID

# List TensorBoard instances
gcloud ai tensorboards list \
  --region=us-central1 \
  --project=PROJECT_ID

# Describe a TensorBoard instance
gcloud ai tensorboards describe TENSORBOARD_ID \
  --region=us-central1 \
  --project=PROJECT_ID

# Create an experiment within a TensorBoard
gcloud ai tensorboards experiments create my-experiment \
  --tensorboard=TENSORBOARD_ID \
  --display-name="Training Run 1" \
  --region=us-central1 \
  --project=PROJECT_ID

# Delete a TensorBoard instance
gcloud ai tensorboards delete TENSORBOARD_ID \
  --region=us-central1 \
  --project=PROJECT_ID
```

---

## Vector Search (Matching Engine / Index)

```bash
# Create an ANN index (from embeddings in Cloud Storage)
# Each line in the input file: {"id": "item_1", "embedding": [0.1, 0.2, ...]}
gcloud ai indexes create \
  --display-name="my-embedding-index" \
  --region=us-central1 \
  --metadata-file=index-metadata.json \
  --project=PROJECT_ID
# index-metadata.json:
# {
#   "contentsDeltaUri": "gs://my-bucket/embeddings/",
#   "config": {
#     "dimensions": 768,
#     "approximateNeighborsCount": 10,
#     "distanceMeasureType": "DOT_PRODUCT_DISTANCE",
#     "algorithm_config": {
#       "treeAhConfig": {"leafNodeEmbeddingCount": 500}
#     }
#   }
# }

# List indexes
gcloud ai indexes list \
  --region=us-central1 \
  --project=PROJECT_ID

# Describe an index
gcloud ai indexes describe INDEX_ID \
  --region=us-central1 \
  --project=PROJECT_ID

# Create an Index Endpoint (the serving endpoint for vector search)
gcloud ai index-endpoints create \
  --display-name="my-index-endpoint" \
  --region=us-central1 \
  --project=PROJECT_ID

# Deploy an index to an endpoint
gcloud ai index-endpoints deploy-index INDEX_ENDPOINT_ID \
  --region=us-central1 \
  --index=INDEX_ID \
  --deployed-index-id=my-deployed-index \
  --display-name="My Deployed Index" \
  --min-replica-count=2 \
  --max-replica-count=10 \
  --project=PROJECT_ID

# List index endpoints
gcloud ai index-endpoints list \
  --region=us-central1 \
  --project=PROJECT_ID

# Undeploy an index from an endpoint
gcloud ai index-endpoints undeploy-index INDEX_ENDPOINT_ID \
  --region=us-central1 \
  --deployed-index-id=my-deployed-index \
  --project=PROJECT_ID

# Delete an index endpoint
gcloud ai index-endpoints delete INDEX_ENDPOINT_ID \
  --region=us-central1 \
  --project=PROJECT_ID

# Delete an index
gcloud ai indexes delete INDEX_ID \
  --region=us-central1 \
  --project=PROJECT_ID
```

---

## Workbench Instances

```bash
# Create a Vertex AI Workbench instance (managed JupyterLab)
gcloud workbench instances create my-notebook \
  --location=us-central1-a \
  --machine-type=n1-standard-4 \
  --vm-image-project=deeplearning-platform-release \
  --vm-image-family=common-cpu-notebooks \
  --project=PROJECT_ID

# Create a GPU-accelerated Workbench instance
gcloud workbench instances create my-gpu-notebook \
  --location=us-central1-a \
  --machine-type=n1-standard-8 \
  --accelerator-type=NVIDIA_TESLA_T4 \
  --accelerator-core-count=1 \
  --vm-image-project=deeplearning-platform-release \
  --vm-image-family=pytorch-latest-gpu \
  --boot-disk-size=200 \
  --data-disk-size=500 \
  --project=PROJECT_ID

# List Workbench instances
gcloud workbench instances list \
  --location=us-central1-a \
  --project=PROJECT_ID

# Describe a Workbench instance
gcloud workbench instances describe my-notebook \
  --location=us-central1-a \
  --project=PROJECT_ID

# Start a stopped instance
gcloud workbench instances start my-notebook \
  --location=us-central1-a \
  --project=PROJECT_ID

# Stop a running instance
gcloud workbench instances stop my-notebook \
  --location=us-central1-a \
  --project=PROJECT_ID

# Reset (restart) a Workbench instance
gcloud workbench instances reset my-notebook \
  --location=us-central1-a \
  --project=PROJECT_ID

# Delete a Workbench instance
gcloud workbench instances delete my-notebook \
  --location=us-central1-a \
  --project=PROJECT_ID

# Get the direct URL to open JupyterLab
gcloud workbench instances describe my-notebook \
  --location=us-central1-a \
  --format="value(proxyUri)" \
  --project=PROJECT_ID
```
