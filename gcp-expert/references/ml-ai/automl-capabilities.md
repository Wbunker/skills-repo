# AutoML — Capabilities

## Purpose

AutoML enables training custom machine learning models without writing ML code. You provide labeled training data; AutoML handles algorithm selection, feature engineering, neural architecture search, and hyperparameter optimization automatically. All AutoML products are now unified under the Vertex AI platform, using the same Dataset, Model, Endpoint, and Pipeline resources.

---

## AutoML Products Overview

| Product | Task Types | Input Data | Output |
|---|---|---|---|
| **AutoML Tables** | Classification, Regression | Tabular CSV/BigQuery | Structured predictions |
| **AutoML Vision** | Image Classification, Object Detection, Image Segmentation | Images (JPEG, PNG, BMP, GIF) | Labels, bounding boxes, masks |
| **AutoML Natural Language** | Text Classification, Entity Extraction, Sentiment Analysis | Text files | Labels, entities, sentiment scores |
| **AutoML Video Intelligence** | Video Classification, Object Tracking, Action Recognition | Videos (MP4, AVI, MOV) | Labels with temporal segments |
| **AutoML Translation** | Custom machine translation | Sentence pairs (source → target) | Translated text |

---

## AutoML Tables (Tabular Data)

### Use cases
- Customer churn prediction
- Fraud detection
- Price prediction
- Demand forecasting
- Lead scoring

### Supported data formats
- CSV files in Cloud Storage
- BigQuery tables/views
- Max columns: 1,000; max rows: 100 million; max file size: 100 GB

### Feature types (auto-detected)
- Numeric (float, integer)
- Categorical (string with <500 distinct values)
- Text (free-form string)
- Timestamp
- Array (repeated numeric/categorical)

### Training targets
- **Classification**: predict a category (binary or multi-class); metrics: AUC ROC, AUC PR, accuracy, F1
- **Regression**: predict a continuous value; metrics: RMSE, MAE, RMSLE, R²

### Training budget
- Specify training node-hours (1–72); more hours = more architecture search = potentially better model
- Early stopping: AutoML stops early if no improvement in the last few hours

### Explainability
AutoML Tables provides feature importance scores (global and per-prediction) showing which features most influenced the model's output. Based on Shapley values.

### Data split
- AutoML automatically splits data 80/10/10 (train/validation/test) by default
- Manual split: provide a `split_column` with values `TRAIN`, `VALIDATION`, `TEST`
- Timestamp split: use a timestamp column to prevent data leakage (train on older data, test on newer)

---

## AutoML Vision

### Image Classification
- **Multi-label**: one image can have multiple classes
- **Single-label**: one image → one class
- Minimum: 10 labeled images per class (100+ recommended)
- Max classes: 5,000
- Max images: 1 million
- Supports import from Cloud Storage (CSV with gs:// paths and labels) or manually labeled in Vertex AI Data Labeling

### Object Detection
- Draw bounding boxes around objects in training images
- Model outputs bounding box coordinates and class labels with confidence scores
- Minimum: 10 bounding boxes per label (50+ recommended)
- Output: `[x_min, y_min, x_max, y_max, label, confidence]`
- Edge models available: export to TFLite, Edge TPU, TF.js for on-device deployment

### Image Segmentation
- Pixel-level instance or semantic segmentation
- More data-intensive than classification or detection

### Export formats
- Cloud prediction (deployed endpoint)
- TFLite (mobile/edge)
- Edge TPU (Coral devices)
- TF.js (browser)
- Docker container (self-hosted)

---

## AutoML Natural Language

### Text Classification
- Assign labels to entire text documents or sub-sections
- Minimum: 10 examples per label (100+ recommended)
- Max classes: 5,000
- Max document size: 128 KB per document
- Supports multi-label classification

### Entity Extraction
- Train a custom Named Entity Recognition (NER) model
- Annotate spans of text with entity types (e.g., PRODUCT, PRICE, DATE, PERSON)
- Minimum: 50 annotated values per entity type
- Output: entity type, text span, offset, confidence score

### Sentiment Analysis
- Custom sentiment scoring on a defined scale (e.g., 0–4 for product review sentiment)
- Unlike the pre-built Sentiment API, AutoML lets you define your own sentiment classes and meanings
- Minimum: 100 examples per sentiment class

---

## AutoML Video Intelligence

### Video Classification
- Classify entire video clips or temporal segments
- Minimum: 500 training videos per label (1,000+ recommended for segment classification)
- Supports: video-level labels, shot-level labels, frame-level labels

### Object Tracking
- Track objects across video frames with bounding boxes
- Minimum: 1,000 bounding box annotations per label
- Use case: retail foot traffic analysis, vehicle tracking in surveillance

### Action Recognition
- Identify human actions in video clips
- Minimum: 200 video clips per action class

---

## AutoML Translation

### Use case
Domain-specific machine translation where generic NMT (Google Translate) quality is insufficient. Examples: legal documents, medical terminology, product catalogs with proprietary vocabulary.

### Data requirements
- Sentence pairs: `(source_language_text, target_language_text)`
- Minimum: 10,000 sentence pairs (50,000+ for significant quality improvement)
- Format: TMX files or tab-separated text files in Cloud Storage
- Pre-trained NMT model is fine-tuned on your data

### Supported language pairs
Any combination of Google Translate's supported 100+ languages.

---

## Data Labeling Service

When labeled training data is not available, Vertex AI Data Labeling Service (formerly Google Cloud Data Labeling) provides access to human labelers:
- Image annotation (bounding boxes, classification, segmentation)
- Text annotation (entity labeling, sentiment)
- Video annotation (action labels, bounding boxes)
- Submit annotation jobs specifying labeling instructions and data in Cloud Storage
- Results returned in AutoML-compatible format

---

## AutoML vs Custom Training

| Criteria | AutoML | Custom Training |
|---|---|---|
| ML expertise required | None | Medium to high |
| Training time | Hours to days (budget-based) | Minutes to days |
| Customization | Limited (data + some config) | Full (architecture, loss function, preprocessing) |
| Best accuracy | Good for most standard tasks | Better for novel architectures or large-scale |
| Explainability | Built-in (Tables, Vision) | Implement with Vertex Explainable AI |
| Production readiness | Immediate (deploy to endpoint) | Requires serving container setup |
| Cost | Predictable (node-hours) | Variable (hardware × duration) |
| Use when | Rapid prototyping, non-ML teams, standard tasks | State-of-the-art required, large scale, research |

---

## Vertex AI Dataset Types

AutoML training always starts by creating a **Vertex AI Dataset** resource:

| Dataset Type | `--metadata-schema-uri` value | AutoML Task |
|---|---|---|
| Image | `gs://google-cloud-aiplatform/schema/dataset/metadata/image_1.0.0.yaml` | Classification, detection, segmentation |
| Text | `gs://google-cloud-aiplatform/schema/dataset/metadata/text_1.0.0.yaml` | Classification, extraction, sentiment |
| Tabular | `gs://google-cloud-aiplatform/schema/dataset/metadata/tabular_1.0.0.yaml` | Classification, regression |
| Video | `gs://google-cloud-aiplatform/schema/dataset/metadata/video_1.0.0.yaml` | Classification, tracking, action |
| Time series | `gs://google-cloud-aiplatform/schema/dataset/metadata/time_series_1.0.0.yaml` | Forecasting |

---

## Best Practices

1. **Quality over quantity for labeled data**: 1,000 high-quality, accurately labeled examples outperform 10,000 noisy ones.
2. **Use timestamp split for tabular data** with time-dependent features to prevent target leakage from future data appearing in the training set.
3. **Monitor class imbalance**: AutoML handles some imbalance, but very skewed datasets (100:1 ratio) still hurt performance; use oversampling or adjust class weights.
4. **Start with AutoML, graduate to custom if needed**: use AutoML to establish a baseline quickly; if the baseline meets requirements, skip custom training entirely.
5. **Export Vision models for edge deployment** when inference must happen on-device (mobile apps, IoT cameras); AutoML Vision supports TFLite and Edge TPU export.
6. **Use the Human Labeling Service for high-stakes labeling** tasks; inconsistent labels are the most common cause of poor AutoML performance.
7. **Review model evaluation carefully before deployment**: AutoML provides per-class precision/recall and confusion matrices; deploy only after reviewing that metrics meet your business thresholds.
8. **Budget training time proportionally**: for tabular data, 8–16 node-hours typically finds a good model; more hours diminish returns; start with 8 and increase only if evaluation is insufficient.
9. **Pin to stable model versions** in production: specify the model version ID in your endpoint deployment to prevent automatic updates from changing predictions unexpectedly.
10. **Use Vertex AI Pipelines to automate AutoML retraining**: schedule monthly retraining pipelines with fresh data to counteract model drift.
