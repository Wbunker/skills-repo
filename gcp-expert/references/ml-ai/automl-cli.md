# AutoML — CLI Reference

AutoML training on Vertex AI uses three main resource types: Datasets, Training Pipelines, and Models. After training, models use the same Endpoint resources as custom-trained models (see vertex-ai-cli.md for endpoint commands).

---

## Datasets

### Create Datasets

```bash
# Create an image dataset
gcloud ai datasets create \
  --display-name="my-image-dataset" \
  --region=us-central1 \
  --metadata-schema-uri=gs://google-cloud-aiplatform/schema/dataset/metadata/image_1.0.0.yaml \
  --project=PROJECT_ID

# Create a tabular dataset
gcloud ai datasets create \
  --display-name="my-tabular-dataset" \
  --region=us-central1 \
  --metadata-schema-uri=gs://google-cloud-aiplatform/schema/dataset/metadata/tabular_1.0.0.yaml \
  --project=PROJECT_ID

# Create a text dataset
gcloud ai datasets create \
  --display-name="my-text-dataset" \
  --region=us-central1 \
  --metadata-schema-uri=gs://google-cloud-aiplatform/schema/dataset/metadata/text_1.0.0.yaml \
  --project=PROJECT_ID

# Create a video dataset
gcloud ai datasets create \
  --display-name="my-video-dataset" \
  --region=us-central1 \
  --metadata-schema-uri=gs://google-cloud-aiplatform/schema/dataset/metadata/video_1.0.0.yaml \
  --project=PROJECT_ID

# Create a time series dataset (for forecasting)
gcloud ai datasets create \
  --display-name="my-timeseries-dataset" \
  --region=us-central1 \
  --metadata-schema-uri=gs://google-cloud-aiplatform/schema/dataset/metadata/time_series_1.0.0.yaml \
  --project=PROJECT_ID
```

### List and Describe Datasets

```bash
# List all datasets in a region
gcloud ai datasets list \
  --region=us-central1 \
  --project=PROJECT_ID

# Filter by display name
gcloud ai datasets list \
  --region=us-central1 \
  --filter="displayName:my-image" \
  --format="table(name,displayName,createTime,metadataSchemaUri)" \
  --project=PROJECT_ID

# Describe a dataset
gcloud ai datasets describe DATASET_ID \
  --region=us-central1 \
  --project=PROJECT_ID
```

### Import Data into Datasets

```bash
# Import image data (CSV file in GCS with paths and labels)
# CSV format: gs://bucket/image.jpg,label_name
gcloud ai datasets import-data DATASET_ID \
  --region=us-central1 \
  --import-schema-uri=gs://google-cloud-aiplatform/schema/dataset/ioformat/image_classification_single_label_io_format_1.0.0.yaml \
  --gcs-source=gs://my-bucket/image-labels.csv \
  --project=PROJECT_ID

# Import image data for object detection
# CSV format: gs://bucket/image.jpg,label,x_min,y_min,x_max,y_max (normalized 0-1)
gcloud ai datasets import-data DATASET_ID \
  --region=us-central1 \
  --import-schema-uri=gs://google-cloud-aiplatform/schema/dataset/ioformat/image_bounding_box_io_format_1.0.0.yaml \
  --gcs-source=gs://my-bucket/detection-labels.csv \
  --project=PROJECT_ID

# Import tabular data from Cloud Storage (CSV)
gcloud ai datasets import-data DATASET_ID \
  --region=us-central1 \
  --import-schema-uri=gs://google-cloud-aiplatform/schema/dataset/ioformat/tabular_io_format_1.0.0.yaml \
  --gcs-source=gs://my-bucket/tabular-data.csv \
  --project=PROJECT_ID

# Import tabular data from BigQuery
gcloud ai datasets import-data DATASET_ID \
  --region=us-central1 \
  --import-schema-uri=gs://google-cloud-aiplatform/schema/dataset/ioformat/tabular_io_format_1.0.0.yaml \
  --bigquery-source=bq://PROJECT_ID.my_dataset.my_table \
  --project=PROJECT_ID

# Import text classification data
# JSON Lines format: {"textGcsUri": "gs://bucket/doc.txt", "classificationAnnotation": {"displayName": "POSITIVE"}}
gcloud ai datasets import-data DATASET_ID \
  --region=us-central1 \
  --import-schema-uri=gs://google-cloud-aiplatform/schema/dataset/ioformat/text_classification_single_label_io_format_1.0.0.yaml \
  --gcs-source=gs://my-bucket/text-labels.jsonl \
  --project=PROJECT_ID

# Import text NER (entity extraction) data
gcloud ai datasets import-data DATASET_ID \
  --region=us-central1 \
  --import-schema-uri=gs://google-cloud-aiplatform/schema/dataset/ioformat/text_extraction_io_format_1.0.0.yaml \
  --gcs-source=gs://my-bucket/ner-annotations.jsonl \
  --project=PROJECT_ID
```

### Delete Datasets

```bash
# Delete a dataset (does not delete the underlying data in GCS/BigQuery)
gcloud ai datasets delete DATASET_ID \
  --region=us-central1 \
  --project=PROJECT_ID
```

---

## Training Pipelines (AutoML Training)

AutoML training is launched via **Training Pipelines**, not Custom Jobs. The pipeline orchestrates the full AutoML process.

### Image Classification

```bash
# Launch AutoML image classification training
gcloud ai training-pipelines create \
  --display-name="automl-image-classification" \
  --region=us-central1 \
  --training-task-definition=gs://google-cloud-aiplatform/schema/trainingjob/definition/automl_image_classification_1.0.0.yaml \
  --training-task-inputs='{"modelType": "CLOUD", "budgetMilliNodeHours": 8000, "disableEarlyStopping": false}' \
  --dataset-id=DATASET_ID \
  --model-display-name=my-image-classifier \
  --project=PROJECT_ID
# modelType options: CLOUD (server), MOBILE_TF_LOW_LATENCY_V1 (TFLite), MOBILE_TF_VERSATILE_V1, MOBILE_TF_HIGH_ACCURACY_V1

# Launch AutoML image classification for mobile/edge export
gcloud ai training-pipelines create \
  --display-name="automl-image-cls-mobile" \
  --region=us-central1 \
  --training-task-definition=gs://google-cloud-aiplatform/schema/trainingjob/definition/automl_image_classification_1.0.0.yaml \
  --training-task-inputs='{"modelType": "MOBILE_TF_LOW_LATENCY_V1", "budgetMilliNodeHours": 8000}' \
  --dataset-id=DATASET_ID \
  --model-display-name=my-mobile-classifier \
  --project=PROJECT_ID
```

### Image Object Detection

```bash
gcloud ai training-pipelines create \
  --display-name="automl-object-detection" \
  --region=us-central1 \
  --training-task-definition=gs://google-cloud-aiplatform/schema/trainingjob/definition/automl_image_object_detection_1.0.0.yaml \
  --training-task-inputs='{"modelType": "CLOUD_HIGH_ACCURACY_1", "budgetMilliNodeHours": 20000, "disableEarlyStopping": false}' \
  --dataset-id=DATASET_ID \
  --model-display-name=my-object-detector \
  --project=PROJECT_ID
# modelType: CLOUD_HIGH_ACCURACY_1, CLOUD_LOW_LATENCY_1, MOBILE_TF_LOW_LATENCY_V1, MOBILE_TF_VERSATILE_V1
```

### Tabular Classification

```bash
gcloud ai training-pipelines create \
  --display-name="automl-tabular-classification" \
  --region=us-central1 \
  --training-task-definition=gs://google-cloud-aiplatform/schema/trainingjob/definition/automl_tabular_classification_1.0.0.yaml \
  --training-task-inputs='{
    "targetColumn": "churn",
    "predictionType": "classification",
    "trainBudgetMilliNodeHours": 8000,
    "disableEarlyStopping": false,
    "optimizationObjective": "maximize-au-roc"
  }' \
  --dataset-id=DATASET_ID \
  --model-display-name=my-churn-classifier \
  --project=PROJECT_ID
# optimizationObjective: maximize-au-roc, minimize-log-loss, maximize-au-prc, maximize-precision-at-recall, maximize-recall-at-precision

# Tabular regression
gcloud ai training-pipelines create \
  --display-name="automl-tabular-regression" \
  --region=us-central1 \
  --training-task-definition=gs://google-cloud-aiplatform/schema/trainingjob/definition/automl_tabular_regression_1.0.0.yaml \
  --training-task-inputs='{
    "targetColumn": "price",
    "predictionType": "regression",
    "trainBudgetMilliNodeHours": 8000,
    "optimizationObjective": "minimize-rmse"
  }' \
  --dataset-id=DATASET_ID \
  --model-display-name=my-price-predictor \
  --project=PROJECT_ID
# optimizationObjective: minimize-rmse, minimize-mae, minimize-rmsle
```

### Text Classification

```bash
gcloud ai training-pipelines create \
  --display-name="automl-text-classification" \
  --region=us-central1 \
  --training-task-definition=gs://google-cloud-aiplatform/schema/trainingjob/definition/automl_text_classification_1.0.0.yaml \
  --training-task-inputs='{"multiLabel": false}' \
  --dataset-id=DATASET_ID \
  --model-display-name=my-text-classifier \
  --project=PROJECT_ID

# Multi-label text classification
gcloud ai training-pipelines create \
  --display-name="automl-text-multilabel" \
  --region=us-central1 \
  --training-task-definition=gs://google-cloud-aiplatform/schema/trainingjob/definition/automl_text_classification_1.0.0.yaml \
  --training-task-inputs='{"multiLabel": true}' \
  --dataset-id=DATASET_ID \
  --model-display-name=my-multilabel-classifier \
  --project=PROJECT_ID
```

### Text Entity Extraction (NER)

```bash
gcloud ai training-pipelines create \
  --display-name="automl-text-ner" \
  --region=us-central1 \
  --training-task-definition=gs://google-cloud-aiplatform/schema/trainingjob/definition/automl_text_extraction_1.0.0.yaml \
  --training-task-inputs='{}' \
  --dataset-id=DATASET_ID \
  --model-display-name=my-ner-model \
  --project=PROJECT_ID
```

### Text Sentiment Analysis

```bash
gcloud ai training-pipelines create \
  --display-name="automl-text-sentiment" \
  --region=us-central1 \
  --training-task-definition=gs://google-cloud-aiplatform/schema/trainingjob/definition/automl_text_sentiment_1.0.0.yaml \
  --training-task-inputs='{"sentimentMax": 4}' \
  --dataset-id=DATASET_ID \
  --model-display-name=my-sentiment-model \
  --project=PROJECT_ID
# sentimentMax: max sentiment score (0 to sentimentMax scale)
```

### Video Classification

```bash
gcloud ai training-pipelines create \
  --display-name="automl-video-classification" \
  --region=us-central1 \
  --training-task-definition=gs://google-cloud-aiplatform/schema/trainingjob/definition/automl_video_classification_1.0.0.yaml \
  --training-task-inputs='{}' \
  --dataset-id=DATASET_ID \
  --model-display-name=my-video-classifier \
  --project=PROJECT_ID
```

---

## Managing Training Pipelines

```bash
# List all training pipelines
gcloud ai training-pipelines list \
  --region=us-central1 \
  --project=PROJECT_ID

# List only running pipelines
gcloud ai training-pipelines list \
  --region=us-central1 \
  --filter="state=PIPELINE_STATE_RUNNING" \
  --project=PROJECT_ID

# Describe a training pipeline (shows current state, model ID when done)
gcloud ai training-pipelines describe TRAINING_PIPELINE_ID \
  --region=us-central1 \
  --project=PROJECT_ID

# Get just the trained model ID (once pipeline is complete)
gcloud ai training-pipelines describe TRAINING_PIPELINE_ID \
  --region=us-central1 \
  --format="value(modelToUpload.name)" \
  --project=PROJECT_ID

# Cancel a running training pipeline
gcloud ai training-pipelines cancel TRAINING_PIPELINE_ID \
  --region=us-central1 \
  --project=PROJECT_ID

# Delete a training pipeline record
gcloud ai training-pipelines delete TRAINING_PIPELINE_ID \
  --region=us-central1 \
  --project=PROJECT_ID
```

---

## Post-Training: Deploy AutoML Model

After training completes, the model appears in the Model Registry and can be deployed to an endpoint identically to custom-trained models:

```bash
# Create an endpoint
gcloud ai endpoints create \
  --display-name="automl-endpoint" \
  --region=us-central1 \
  --project=PROJECT_ID

# Deploy the AutoML model to the endpoint
gcloud ai endpoints deploy-model ENDPOINT_ID \
  --region=us-central1 \
  --model=MODEL_ID \
  --display-name="automl-deployed" \
  --machine-type=n1-standard-4 \
  --min-replica-count=1 \
  --max-replica-count=3 \
  --traffic-split=0=100 \
  --project=PROJECT_ID

# Send a prediction to the deployed AutoML model
gcloud ai endpoints predict ENDPOINT_ID \
  --region=us-central1 \
  --json-request='{"instances": [{"feature1": 1.0, "feature2": "category_A"}]}' \
  --project=PROJECT_ID
```

---

## Export AutoML Models (for Edge Deployment)

```bash
# Export an AutoML Vision model to TFLite (for mobile deployment)
gcloud ai models export MODEL_ID \
  --region=us-central1 \
  --output-path=gs://my-bucket/exported-models/ \
  --export-format-id=tflite \
  --project=PROJECT_ID

# Export to TF SavedModel format
gcloud ai models export MODEL_ID \
  --region=us-central1 \
  --output-path=gs://my-bucket/exported-models/ \
  --export-format-id=tf-saved-model \
  --project=PROJECT_ID

# Export to Edge TPU (Coral)
gcloud ai models export MODEL_ID \
  --region=us-central1 \
  --output-path=gs://my-bucket/exported-models/ \
  --export-format-id=edgetpu-tflite \
  --project=PROJECT_ID

# List available export formats for a model
gcloud ai models describe MODEL_ID \
  --region=us-central1 \
  --format="value(supportedExportFormats)" \
  --project=PROJECT_ID
```
