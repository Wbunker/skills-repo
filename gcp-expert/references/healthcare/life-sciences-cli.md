# Life Sciences & Genomics — CLI Reference

## Enable Life Sciences API

```bash
# Enable Cloud Life Sciences API
gcloud services enable lifesciences.googleapis.com --project=my-project

# Also enable Cloud Storage (for pipeline I/O)
gcloud services enable storage.googleapis.com --project=my-project

# Verify
gcloud services list --enabled --filter="name:lifesciences" --project=my-project
```

---

## Life Sciences Operations

```bash
# List all operations (pipeline runs)
gcloud lifesciences operations list \
  --location=us-central1 \
  --project=my-project \
  --format="table(name,done,metadata.labels,metadata.startTime)"

# List running operations only
gcloud lifesciences operations list \
  --location=us-central1 \
  --filter="done=false" \
  --project=my-project

# Describe a specific operation (shows status, events, errors)
gcloud lifesciences operations describe OPERATION_ID \
  --location=us-central1 \
  --project=my-project

# Cancel a running operation
gcloud lifesciences operations cancel OPERATION_ID \
  --location=us-central1 \
  --project=my-project
```

---

## Run a Pipeline

The `gcloud lifesciences pipelines run` command submits a pipeline for execution.

```bash
# Simple pipeline: run FastQC quality control
cat > fastqc-pipeline.json << 'EOF'
{
  "pipeline": {
    "actions": [
      {
        "imageUri": "biocontainers/fastqc:v0.11.9_cv8",
        "commands": [
          "fastqc",
          "/gcs/input/sample_R1.fastq.gz",
          "/gcs/input/sample_R2.fastq.gz",
          "--outdir=/gcs/output/fastqc/",
          "--threads=4"
        ]
      }
    ],
    "resources": {
      "regions": ["us-central1"],
      "virtualMachine": {
        "machineType": "n2-standard-8",
        "bootDiskSizeGb": 100,
        "preemptible": true,
        "serviceAccount": {
          "email": "genomics-pipeline-sa@my-project.iam.gserviceaccount.com",
          "scopes": ["https://www.googleapis.com/auth/cloud-platform"]
        }
      }
    }
  },
  "labels": {
    "sample": "SAMPLE-001",
    "tool": "fastqc",
    "pipeline": "qc"
  }
}
EOF

gcloud lifesciences pipelines run \
  --pipeline-file=fastqc-pipeline.json \
  --inputs=INPUT_GCS=gs://my-genomics-bucket/raw/SAMPLE-001_R1.fastq.gz \
  --outputs=OUTPUT_GCS=gs://my-genomics-bucket/qc/SAMPLE-001/ \
  --logging=gs://my-genomics-bucket/logs/SAMPLE-001/fastqc.log \
  --location=us-central1 \
  --project=my-project
```

### Full Alignment Pipeline (BWA + Samtools)

```bash
cat > alignment-pipeline.json << 'EOF'
{
  "pipeline": {
    "actions": [
      {
        "imageUri": "us-docker.pkg.dev/my-project/genomics/bwa-samtools:0.7.17",
        "commands": ["/bin/bash", "-c",
          "bwa mem -t 32 /gcs/ref/hg38.fa /gcs/input/${SAMPLE}_R1.fastq.gz /gcs/input/${SAMPLE}_R2.fastq.gz | samtools sort -@8 -o /gcs/output/${SAMPLE}.sorted.bam && samtools index /gcs/output/${SAMPLE}.sorted.bam"
        ],
        "environment": {
          "SAMPLE": "SAMPLE-001"
        }
      }
    ],
    "resources": {
      "regions": ["us-central1"],
      "virtualMachine": {
        "machineType": "n2-standard-32",
        "bootDiskSizeGb": 50,
        "disks": [
          {"name": "ref-disk", "sizeGb": 150, "type": "pd-ssd"},
          {"name": "io-disk", "sizeGb": 500, "type": "pd-ssd"}
        ],
        "preemptible": false,
        "labels": {
          "pipeline": "wgs-alignment",
          "sample": "SAMPLE-001"
        }
      }
    }
  }
}
EOF

gcloud lifesciences pipelines run \
  --pipeline-file=alignment-pipeline.json \
  --logging=gs://my-genomics-bucket/logs/SAMPLE-001/alignment.log \
  --location=us-central1 \
  --project=my-project
```

### Monitor Pipeline Progress

```bash
# Get the operation ID from the run output and poll for completion
OPERATION_ID="projects/my-project/locations/us-central1/operations/12345678"

# Wait for completion (poll every 30 seconds)
while true; do
  STATUS=$(gcloud lifesciences operations describe "${OPERATION_ID}" \
    --location=us-central1 \
    --project=my-project \
    --format="value(done)" 2>/dev/null)

  if [ "${STATUS}" = "True" ]; then
    echo "Pipeline completed!"
    break
  fi

  echo "Pipeline still running... waiting 30s"
  sleep 30
done

# Check for errors
gcloud lifesciences operations describe "${OPERATION_ID}" \
  --location=us-central1 \
  --project=my-project \
  --format="json(error,done,metadata.events)"
```

---

## Set Up Genomics Pipeline Service Account

```bash
# Create service account for pipeline execution
gcloud iam service-accounts create genomics-pipeline-sa \
  --display-name="Genomics Pipeline Service Account" \
  --project=my-project

# Grant necessary permissions
# Storage access (read input, write output, write logs)
gcloud storage buckets add-iam-policy-binding gs://my-genomics-bucket \
  --member=serviceAccount:genomics-pipeline-sa@my-project.iam.gserviceaccount.com \
  --role=roles/storage.objectAdmin

# Life Sciences Worker role (needed for pipeline runner)
gcloud projects add-iam-policy-binding my-project \
  --member=serviceAccount:genomics-pipeline-sa@my-project.iam.gserviceaccount.com \
  --role=roles/lifesciences.workflowsRunner

# Compute instance creator (for spinning up worker VMs)
gcloud projects add-iam-policy-binding my-project \
  --member=serviceAccount:genomics-pipeline-sa@my-project.iam.gserviceaccount.com \
  --role=roles/compute.instanceAdmin.v1

# Allow pipeline SA to use Compute default SA (for worker VMs)
gcloud iam service-accounts add-iam-policy-binding \
  "$(gcloud projects describe my-project --format='value(projectNumber)')-compute@developer.gserviceaccount.com" \
  --member=serviceAccount:genomics-pipeline-sa@my-project.iam.gserviceaccount.com \
  --role=roles/iam.serviceAccountUser \
  --project=my-project
```

---

## Cloud Storage for Genomics Data

```bash
# Create genomics data bucket
gcloud storage buckets create gs://my-genomics-bucket \
  --location=us-central1 \
  --default-storage-class=STANDARD \
  --project=my-project

# Create directory structure
gcloud storage cp /dev/null gs://my-genomics-bucket/raw/.gitkeep
gcloud storage cp /dev/null gs://my-genomics-bucket/aligned/.gitkeep
gcloud storage cp /dev/null gs://my-genomics-bucket/variants/.gitkeep
gcloud storage cp /dev/null gs://my-genomics-bucket/qc/.gitkeep
gcloud storage cp /dev/null gs://my-genomics-bucket/reference/.gitkeep
gcloud storage cp /dev/null gs://my-genomics-bucket/logs/.gitkeep

# Upload reference genome (example)
gcloud storage cp /local/reference/hg38.fa gs://my-genomics-bucket/reference/
gcloud storage cp /local/reference/hg38.fa.bwt gs://my-genomics-bucket/reference/
gcloud storage cp /local/reference/hg38.fa.fai gs://my-genomics-bucket/reference/

# Set lifecycle policy: move old BAM files to Nearline after 90 days
cat > lifecycle-policy.json << 'EOF'
{
  "rule": [
    {
      "action": {"type": "SetStorageClass", "storageClass": "NEARLINE"},
      "condition": {
        "age": 90,
        "matchesPrefix": ["aligned/"],
        "matchesSuffix": [".bam", ".bam.bai"]
      }
    },
    {
      "action": {"type": "SetStorageClass", "storageClass": "COLDLINE"},
      "condition": {
        "age": 365,
        "matchesPrefix": ["raw/"],
        "matchesSuffix": [".fastq.gz"]
      }
    }
  ]
}
EOF

gcloud storage buckets update gs://my-genomics-bucket \
  --lifecycle-file=lifecycle-policy.json
```

---

## BigQuery for Variant Analysis

```bash
# Create a dataset for genomics analytics
bq --location=US mk --dataset \
  --description="Genomics variant analytics" \
  my-project:genomics_analytics

# Create a table for variant calls from a VCF pipeline
bq mk --table \
  --schema='sample_id:STRING,chromosome:STRING,position:INTEGER,reference_bases:STRING,alternate_bases:STRING,filter:STRING,qual:FLOAT,gt:STRING,dp:INTEGER,gq:INTEGER,af_gnomad:FLOAT,clinvar_sig:STRING' \
  --time_partitioning_field=chromosome \
  --clustering_fields=sample_id,chromosome \
  --description="Variant calls from WGS pipeline" \
  my-project:genomics_analytics.variant_calls

# Load VCF data from GCS (requires VCF-to-BQ conversion; use NDJSON intermediate)
# Example: after converting VCF to NDJSON with a pipeline step:
bq load \
  --source_format=NEWLINE_DELIMITED_JSON \
  my-project:genomics_analytics.variant_calls \
  gs://my-genomics-bucket/variants/SAMPLE-001/*.ndjson

# Query for pathogenic variants in cancer genes
bq query --use_legacy_sql=false \
  --project_id=my-project \
'SELECT
  sample_id,
  chromosome,
  position,
  reference_bases,
  alternate_bases,
  clinvar_sig,
  af_gnomad
FROM `my-project.genomics_analytics.variant_calls`
WHERE
  clinvar_sig IN ("Pathogenic", "Likely pathogenic")
  AND (af_gnomad IS NULL OR af_gnomad < 0.01)
ORDER BY clinvar_sig, chromosome, position'
```

---

## Bigtable for Variant Lookups

```bash
# Create Bigtable instance for variant database
gcloud bigtable instances create genomics-variants \
  --display-name="Genomics Variant Database" \
  --cluster-config=id=genomics-cluster,zone=us-central1-a,nodes=3 \
  --project=my-project

# Create table and column families
cbt -project=my-project -instance=genomics-variants \
  createtable variant_db

# Column families for variant data
cbt -project=my-project -instance=genomics-variants \
  createfamily variant_db population_freq

cbt -project=my-project -instance=genomics-variants \
  createfamily variant_db clinical

cbt -project=my-project -instance=genomics-variants \
  createfamily variant_db functional

# Set GC policy (keep latest 1 value per cell)
cbt -project=my-project -instance=genomics-variants \
  setgcpolicy variant_db population_freq maxversions=1

cbt -project=my-project -instance=genomics-variants \
  setgcpolicy variant_db clinical maxversions=1

# Write a variant record
# Row key: chr17#43044295#G#A (chromosome#position#ref#alt)
cbt -project=my-project -instance=genomics-variants \
  set variant_db "chr17#43044295#G#A" \
  "population_freq:af_gnomad=0.0001" \
  "population_freq:af_1kg=0.00008" \
  "clinical:clinvar_sig=Pathogenic" \
  "clinical:gene=BRCA1" \
  "functional:consequence=missense_variant"

# Lookup a specific variant
cbt -project=my-project -instance=genomics-variants \
  lookup variant_db "chr17#43044295#G#A"
```
