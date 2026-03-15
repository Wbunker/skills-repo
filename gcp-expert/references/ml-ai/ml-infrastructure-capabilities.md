# ML Infrastructure — Capabilities

## TPU (Tensor Processing Unit)

### Overview
Google's custom AI accelerators designed specifically for matrix multiplication-heavy workloads (neural network training and inference). TPUs provide significantly higher FLOPS per dollar than GPUs for TensorFlow and JAX workloads and are the infrastructure underlying Google's own AI models (Gemini, PaLM, Bard).

### TPU Generations

| Generation | Architecture | Peak Performance | Best for |
|---|---|---|---|
| **TPU v4** | 3D torus interconnect | 275 TFLOPS (BF16) per chip | Large model training; established generation |
| **TPU v5e** | Efficiency-optimized | 197 TFLOPS (BF16) per chip | Cost-efficient inference and fine-tuning |
| **TPU v5p** | Performance-optimized | 459 TFLOPS (BF16) per chip | Maximum training throughput for large models |
| **TPU v6e (Trillium)** | Latest generation | ~4x v5e performance | State-of-the-art training; Gemini-class workloads |

### TPU Pod Slices
Large-scale TPU training uses **pod slices** — subsets of a TPU Pod (the full interconnected cluster):
- v4 pod: up to 4,096 chips in a 3D torus
- Common slice sizes: 8, 16, 32, 64, 128, 256, 512, 1024, 2048, 4096 chips
- Chips within a slice communicate via high-bandwidth inter-chip interconnect (ICI), not networking
- Pod slices are specified as shapes: `v4-8` (8 chips), `v4-64` (64 chips), `v4-512` (512 chips)

### TPU VMs vs TPU Nodes

| | TPU VM (recommended) | TPU Node (legacy) |
|---|---|---|
| Access | Direct SSH to the TPU host VM | API-only; no direct SSH |
| API | `gcloud compute tpus tpu-vm` | `gcloud compute tpus` |
| Customization | Install any software on the VM | Limited to pre-built Docker containers |
| Performance | Slightly better (fewer network hops) | Slightly higher network latency |
| Use when | All new workloads | Legacy workflows only |

### Framework support
- **JAX**: best performance on TPUs; XLA compilation; `jax.device_count()` returns TPU chip count
- **TensorFlow 2.x**: native TPU support via `tf.distribute.TPUStrategy`
- **PyTorch**: supported via `torch_xla` library (XLA backend for PyTorch)
- **PaddlePaddle**: XLA support

### Queued Resources
For large TPU allocations, use the Queued Resources API to request TPU capacity that is fulfilled when available, rather than failing immediately if capacity is not available.

---

## GPUs on Compute Engine and Vertex AI

### GPU Types

| GPU | Memory | Architecture | Peak FP16/BF16 | Use case |
|---|---|---|---|---|
| **NVIDIA T4** | 16 GB GDDR6 | Turing | 65 TFLOPS | Inference, cost-efficient training |
| **NVIDIA V100** | 16/32 GB HBM2 | Volta | 125 TFLOPS | General training; NLP, CV |
| **NVIDIA A100 40GB** | 40 GB HBM2e | Ampere | 312 TFLOPS | Large model training |
| **NVIDIA A100 80GB** | 80 GB HBM2e | Ampere | 312 TFLOPS | Very large models requiring >40GB VRAM |
| **NVIDIA H100 80GB SXM** | 80 GB HBM3 | Hopper | 989 TFLOPS | Largest-scale training; best H100 performance |
| **NVIDIA H100 80GB PCIe** | 80 GB HBM3 | Hopper | 800 TFLOPS | High-performance inference and training |
| **NVIDIA L4** | 24 GB GDDR6 | Ada Lovelace | 242 TFLOPS (INT8) | Inference-optimized; video, multimodal |
| **NVIDIA L40S** | 48 GB GDDR6 | Ada Lovelace | 362 TFLOPS | Large inference models; generative AI serving |

### GPU Instance Families

| Instance Family | GPU Config | Total GPU Memory | Use case |
|---|---|---|---|
| `n1-standard-*` + accelerator | 1-8x T4, V100 | Up to 128 GB | General training and inference |
| `a2-highgpu-1g` | 1x A100 80GB | 80 GB | Single-GPU LLM inference |
| `a2-highgpu-2g` | 2x A100 80GB | 160 GB | Medium model training |
| `a2-highgpu-4g` | 4x A100 80GB | 320 GB | Large model training |
| `a2-highgpu-8g` | 8x A100 80GB | 640 GB | Very large model training |
| `a2-megagpu-16g` | 16x A100 40GB | 640 GB | Ultra-large model training |
| `a3-highgpu-8g` | 8x H100 80GB SXM | 640 GB | State-of-the-art LLM training |
| `a3-megagpu-8g` | 8x H100 80GB HBM3e | 640 GB | Maximum H100 performance |
| `g2-standard-*` | 1-16x L4 | Up to 384 GB | Inference; video; multimodal |

### NVLink and GPUDirect RDMA
- **NVLink**: high-bandwidth GPU-to-GPU interconnect within a node; A100 and H100 nodes have NVLink for all-reduce operations
- **GPUDirect RDMA**: A3 instances support GPU-to-GPU communication across nodes via RDMA over InfiniBand/RoCE; eliminates CPU from inter-node gradient synchronization; critical for multi-node training at scale
- **A3 clusters**: dedicated high-performance fabric for H100 workloads; request via Compute Engine reservations

### Maintenance policy
GPU instances must set `--maintenance-policy=TERMINATE` (not `MIGRATE`); live migration is not supported for GPU VMs.

---

## Hyperdisk ML

Hyperdisk ML is a block storage type optimized for **reading large ML model checkpoints and serving artifacts** at high throughput:

### Key characteristics
- **Throughput**: up to 1,200 MB/s per GB provisioned (far exceeds Persistent Disk SSD)
- **Read-scale mode**: a single Hyperdisk ML volume in `READ_ONLY_MANY` access mode can be **simultaneously attached to up to 1,000 VMs** — enabling fleet-scale model serving where thousands of inference VMs all read from one disk
- **Use case**: loading large LLM checkpoints (70B+ parameters) into GPU/TPU memory at startup; dramatically reduces cold-start time for model serving
- **Write mode**: also supports `READ_WRITE_SINGLE` for writing checkpoints during training
- **Zonal resource**: create in the same zone as the VMs that will attach it

### Typical workflow for model serving
1. Training job writes model checkpoint to Hyperdisk ML in `READ_WRITE_SINGLE` mode.
2. Training completes; switch disk to `READ_ONLY_MANY` mode.
3. Spin up serving fleet of GPU VMs; all attach the same Hyperdisk ML volume.
4. Model loads from local block device at high throughput; latency is seconds rather than minutes.
5. Scale the serving fleet up/down; new VMs attach the existing disk immediately.

---

## Deep Learning VM Images

Pre-configured Compute Engine VM images with CUDA, cuDNN, and ML framework pre-installed:

### Available image families

| Image Family | Framework | CUDA | GPU-enabled |
|---|---|---|---|
| `pytorch-latest-gpu` | PyTorch (latest) | Latest | Yes |
| `pytorch-2-2-gpu` | PyTorch 2.2 | 12.x | Yes |
| `tf2-latest-gpu` | TensorFlow 2 (latest) | Latest | Yes |
| `tf2-ent-2-13-cu121` | TF 2.13 (Enterprise) | 12.1 | Yes |
| `common-cpu-notebooks` | Common frameworks | None | No |
| `jax-latest-gpu` | JAX (latest) | Latest | Yes |
| `deeplearning-common-gpu` | Multiple frameworks | Latest | Yes |

All deep learning images: project `deeplearning-platform-release`.

### Features
- NVIDIA driver pre-installed
- CUDA and cuDNN pre-installed
- Jupyter and JupyterLab pre-installed
- Common ML libraries (NumPy, SciPy, scikit-learn, Pandas, Matplotlib)
- Docker with GPU support
- Startup scripts for package installation on first boot

---

## Vertex AI Workbench

Managed JupyterLab notebooks with Vertex AI integration:

### Instance types
- **User-managed notebooks**: more control; you manage software dependencies; access via SSH
- **Managed runtime** (default for new Workbench instances): Google manages the runtime; automatic updates; simpler

### Hardware configurations
- Machine types: `n1-standard-4` up to `n1-highmem-96`
- GPUs: T4, V100, A100 40GB, A100 80GB
- TPU support: attach Cloud TPU VMs to Workbench instances
- Boot disk: 150 GB standard; customizable
- Data disk: optional; persists across shutdowns

### Key features
- **Persistent storage**: data survives instance shutdowns (unlike ephemeral VMs)
- **Git integration**: built-in Git panel; branch, commit, push from JupyterLab
- **Vertex AI integration**: submit training jobs, access datasets, deploy models directly from notebooks
- **BigQuery connector**: query BigQuery tables directly in notebooks with `%%bigquery` magic
- **Scheduled execution**: run notebooks on a schedule via Cloud Scheduler (via `gcloud notebooks execute`)
- **Managed runtimes**: automatically updated; no maintenance burden

---

## Colab Enterprise

Google Colaboratory for enterprise workloads, integrated with GCP:

### Differences from public Colab
- **Compute**: backed by Vertex AI managed runtimes (T4, A100, TPUs)
- **Security**: runs within your GCP project; no data leaves your VPC; integrates with VPC SC
- **Data access**: direct access to BigQuery, Cloud Storage, Secret Manager within your project
- **Collaboration**: real-time collaboration (like Google Docs) with teammates in your org
- **No free tier limits**: no runtime disconnects; sessions run as long as needed
- **CMEK**: encrypt notebook storage with your own KMS key

### Runtime types available
- CPU: `n1-standard-4`
- GPU: T4 (16 GB), A100 40 GB, A100 80 GB
- TPU: v2-8, v3-8 (via Cloud TPU)

---

## Best Practices for ML Infrastructure

1. **Use Queued Resources API for large TPU allocations**: TPU pod slices >256 chips may not be immediately available; queued resources allow you to request capacity without failing immediately.
2. **Use NVLink-enabled A100/H100 instances for multi-GPU training**: inter-GPU bandwidth is the primary bottleneck for large model training; NVLink provides 600 GB/s vs PCIe's 64 GB/s.
3. **Pre-build and cache Docker containers**: don't install packages at training startup; build a container with all dependencies and push to Artifact Registry; training startup time drops from minutes to seconds.
4. **Use Spot/Preemptible VMs for long training jobs with checkpointing**: 60-70% cost savings for preemptible instances; implement checkpoint-on-preemption signal handling.
5. **Use Hyperdisk ML for multi-replica model serving**: one disk → 1,000 VMs is dramatically more cost-effective than Object Storage (Cloud Storage) loading at startup.
6. **Profile before scaling**: use NVIDIA Nsight or PyTorch Profiler to identify bottlenecks (compute-bound vs memory-bound vs IO-bound) before adding more GPUs/TPUs.
7. **Use Deep Learning VM images as base**: don't install CUDA manually; base your custom Docker containers on `gcr.io/deeplearning-platform-release/base-gpu.py310` to get a correctly configured CUDA environment.
8. **Shut down Workbench instances when not in use**: GPU-attached Workbench instances are expensive at idle; use scheduled auto-shutdown or implement monitoring to alert on idle GPU utilization.
9. **Use Colab Enterprise for team data exploration**: faster to set up than Workbench for ad-hoc analysis; direct BigQuery and GCS access without credential configuration.
10. **Enable CMEK on Vertex AI training jobs for regulated data**: training jobs that process PII or regulated data must use CMEK to ensure data at rest (in training artifacts and logs) is protected with customer-managed keys.
