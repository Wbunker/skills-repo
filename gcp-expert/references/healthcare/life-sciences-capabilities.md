# Life Sciences & Genomics — Capabilities

## Cloud Life Sciences API

The **Cloud Life Sciences API** (formerly Google Genomics API) enables execution of scalable genomics and bioinformatics pipelines on Google Cloud. It provisions ephemeral Compute Engine VMs, runs containerized tools, and automatically cleans up after pipeline completion.

### Core Concepts

**Pipeline**: a JSON-defined computational workflow; specifies:
- Docker container image (from Artifact Registry, Docker Hub, or any registry)
- Commands to execute inside the container
- Input files (from Cloud Storage)
- Output files (to Cloud Storage)
- VM configuration (machine type, disk size, zones, GPU requirements)
- Environment variables

**Worker VM**: ephemeral Compute Engine VM provisioned for a single pipeline run; automatically deleted after completion (success or failure).

**Action**: a single step within a pipeline; multiple actions can run sequentially or in parallel within a pipeline run.

**Operation**: a long-running operation representing a pipeline run; poll for completion; contains logs and error details.

### Common Bioinformatics Tools Supported

Any Docker container can be used. Commonly used containers:
- **GATK (Genome Analysis Toolkit)**: variant calling; best practices pipelines
- **BWA / BWA-MEM2**: DNA sequence alignment
- **STAR**: RNA-seq alignment
- **FastQC**: sequencing quality control
- **Trimmomatic**: read trimming and quality filtering
- **Samtools**: SAM/BAM manipulation (sort, index, stats)
- **PICARD**: duplicate marking, metrics collection
- **DeepVariant**: Google's ML-based variant caller
- **ANNOVAR**: variant annotation
- **MultiQC**: aggregate QC reports

### Secondary Analysis Pipeline Example

Typical whole-genome sequencing (WGS) pipeline stages:
1. **Quality control**: FastQC on raw FASTQ files
2. **Alignment**: BWA-MEM → SAM/BAM output
3. **Sort and index**: Samtools sort + index → sorted BAM
4. **Mark duplicates**: PICARD MarkDuplicates → deduplicated BAM
5. **Base quality score recalibration (BQSR)**: GATK BaseRecalibrator + ApplyBQSR
6. **Variant calling**: GATK HaplotypeCaller → GVCF → GenomicsDBImport → GenotypeGVCFs → VCF
7. **Variant annotation**: ANNOVAR or VEP
8. **QC reporting**: MultiQC aggregate report

Total compute: ~$10-50 per WGS sample depending on machine type and disk configuration.

### Pipeline JSON Structure

```json
{
  "pipeline": {
    "actions": [
      {
        "imageUri": "us-docker.pkg.dev/my-project/bio/bwa:0.7.17",
        "commands": [
          "bwa", "mem", "-t", "16",
          "/gcs/reference/hg38.fa",
          "/gcs/input/sample_R1.fastq.gz",
          "/gcs/input/sample_R2.fastq.gz",
          "-o", "/gcs/output/aligned.sam"
        ],
        "mounts": [
          {"disk": "reference", "path": "/gcs/reference", "readOnly": true},
          {"disk": "input", "path": "/gcs/input", "readOnly": true},
          {"disk": "output", "path": "/gcs/output"}
        ]
      }
    ],
    "resources": {
      "virtualMachine": {
        "machineType": "n2-standard-32",
        "bootDiskSizeGb": 50,
        "disks": [
          {"name": "reference", "sizeGb": 100, "type": "pd-ssd"},
          {"name": "input", "sizeGb": 200, "type": "pd-ssd"},
          {"name": "output", "sizeGb": 300, "type": "pd-ssd"}
        ],
        "zones": ["us-central1-a", "us-central1-b"],
        "preemptible": true
      }
    },
    "environment": {
      "SAMPLE_ID": "SAMPLE-001"
    }
  },
  "labels": {
    "sample": "SAMPLE-001",
    "pipeline": "wgs-alignment"
  }
}
```

### Cost Optimization for Genomics Pipelines

- **Preemptible/Spot VMs**: use `"preemptible": true` for fault-tolerant pipeline stages; saves ~70% on compute
- **Parallelization**: run multiple samples concurrently; Life Sciences API handles provisioning
- **PD-SSD vs PD-balanced**: use SSD for I/O-intensive tools (alignment, sorting); standard for archival
- **gcsfuse vs direct GCS**: pipeline actions can use GCS FUSE mounts (automatic) for seamless GCS access from container file paths
- **Localization/delocalization**: Life Sciences handles copying input from GCS to local disk and output from local disk to GCS; explicit localization actions needed for large files

---

## Vertex AI for Healthcare

### Med-PaLM 2

**Med-PaLM 2** is Google's large language model fine-tuned on medical knowledge:
- Trained on medical datasets, textbooks, and clinical notes
- Demonstrates physician-level performance on US Medical Licensing Examination (USMLE) questions
- **Use cases**: clinical documentation assistance, patient question answering, medical knowledge retrieval, clinical note summarization
- Access via **Vertex AI Model Garden** (requires allowlisting; HIPAA BAA required for PHI use)
- **Important**: Med-PaLM 2 is an AI assistant, not a diagnostic tool; clinical validation required before deployment in patient care settings

### Chest X-ray AI (CXR Foundation)

- Foundation model for chest radiograph analysis
- Pre-trained on millions of chest X-ray images
- **Fine-tuning**: adapt to specific clinical tasks with relatively few labeled examples
- **Tasks**: pneumonia detection, cardiomegaly classification, pathology localization, report generation
- Access via Vertex AI as a foundation model

### Pathology AI

- Foundation model for digital pathology (whole-slide images)
- Patch-level feature extraction from H&E stained slides
- Fine-tune for: cancer grading, cell counting, tissue segmentation
- Integrates with DICOM store (WSI stored in Cloud Healthcare API DICOM format)

### FDA-Cleared AI Models

Some Google-developed healthcare AI models have FDA clearance:
- Verify current clearance status at fda.gov (clearances change over time)
- FDA-cleared models have specific indications for use and intended population
- Separate from research/exploratory models in Vertex AI Model Garden

### Vertex AI for Custom Healthcare ML

Standard Vertex AI capabilities applied to healthcare data:

| Use Case | Vertex AI Capability |
|---|---|
| Clinical NLP | AutoML text classification, fine-tune Gemini on clinical notes |
| Radiology AI | AutoML image classification on medical images |
| Genomics ML | Vertex AI custom training with TensorFlow/PyTorch on variant data |
| EHR prediction | Vertex AI tabular classification (readmission risk, sepsis prediction) |
| Drug discovery | Vertex AI custom training on molecular data, AlphaFold integration |

---

## Genomics Data on GCP

### Storage Tiers for Genomics Data

| Data Type | Recommended Storage | Format |
|---|---|---|
| Raw sequencing reads | Cloud Storage (Nearline for archival) | FASTQ.gz (compressed) |
| Aligned reads | Cloud Storage (Standard for active, Coldline for archive) | BAM/CRAM (indexed) |
| Variants | Cloud Storage + BigQuery | VCF (raw), Parquet (for BigQuery import) |
| Reference genomes | Cloud Storage (regional, frequently accessed) | FASTA + BWA index files |

### BigQuery for Variant Databases

Public genomics datasets available in BigQuery:
- **gnomAD** (Genome Aggregation Database): allele frequencies from 140,000+ genomes
- **ClinVar**: variant-disease associations from NCBI
- **1000 Genomes Project**: population-level variant data
- **UK Biobank**: large-scale biobank data (restricted access)

Query variant populations without downloading massive VCF files:
```sql
-- Example: find variants in BRCA1 with population frequency > 1%
SELECT
  reference_bases, alternate_bases, AF
FROM `bigquery-public-data.gnomAD.v2_1_1_exomes__chr17`
WHERE
  start_position BETWEEN 43044295 AND 43125483  -- BRCA1 coordinates (GRCh38)
  AND AF > 0.01
ORDER BY AF DESC
LIMIT 100
```

### Bigtable for Genomics Key Lookups

Use Bigtable for fast, low-latency lookups of genomic data by variant key or gene:
- Row key: `{chromosome}#{position}#{ref}#{alt}` for variant lookups
- Row key: `{gene_symbol}#{variant_type}` for gene-level queries
- Column family: `clinical_significance`, `population_frequencies`, `functional_predictions`
- Millisecond-latency point reads; scales to billions of variants

### AlloyDB / Cloud SQL for Clinical Databases

- Patient-level databases linking clinical data to genomic data
- Join variant calls to patient phenotype and treatment data
- AlloyDB for high-performance analytics on clinical data (columnar engine)
- Cloud SQL PostgreSQL with `pg_genomics` extension for variant storage
