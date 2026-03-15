# AWS Custom Silicon — Capabilities Reference

For CLI commands, see [aws-silicon-cli.md](aws-silicon-cli.md).

## AWS Graviton

**Purpose**: AWS-designed Arm64 processors delivering better price-performance than comparable x86 instances for most cloud workloads — combining lower cost, reduced energy consumption, and competitive throughput for the majority of Linux-based workloads.

### Processor Generations

| Generation | Instance Families | Key Specs / Improvement |
|---|---|---|
| **Graviton** (original) | A1 | First-gen Arm64 in EC2; 45% cost savings vs comparable x86 |
| **Graviton2** | M6g, C6g, R6g, T4g, X2gd, Im4gn, Is4gen | Up to 40% better price-performance vs x86 gen; 7× perf vs Graviton1 |
| **Graviton3** | M7g, C7g, R7g, Hpc7g | Up to 25% better performance vs Graviton2; 3× ML performance; DDR5 memory |
| **Graviton4** | M8g, C8g, R8g | Up to 30% better performance vs Graviton3; up to 192 vCPUs; up to 3 TB RAM |

### Cost and Energy Efficiency

| Metric | Advantage |
|---|---|
| **Price** | Up to 20% less than comparable x86 EC2 instances |
| **Energy** | Up to 60% less energy than comparable EC2 x86 instances for equivalent performance |
| **Adoption** | Over 90,000 AWS customers use Graviton-based instances |

### Graviton4 Details (M8g / C8g / R8g)

- Up to 192 vCPUs per instance (largest Graviton instance ever)
- Up to 3 TB RAM (R8g high-memory)
- 30% better performance than Graviton3 across compute-intensive workloads
- DDR5 memory bandwidth improvements; enhanced cryptographic acceleration
- Available in C8g (compute-optimized), M8g (general purpose), R8g (memory-optimized)

### Services Supporting Graviton (Beyond EC2)

| Service | Graviton Support |
|---|---|
| **Amazon RDS** | Graviton2/3 DB instances (MySQL, PostgreSQL, MariaDB) |
| **Amazon Aurora** | Graviton2/3 for Aurora MySQL and Aurora PostgreSQL |
| **Amazon ElastiCache** | Graviton2/3 cache nodes (Redis, Memcached) |
| **AWS Lambda** | arm64 architecture option; up to 34% better price-performance |
| **AWS Fargate** | arm64 task CPU architecture |
| **Amazon EKS** | Managed node groups with Graviton instance types |
| **Amazon ECS** | Tasks and services on Graviton EC2 or Fargate |
| **Amazon EMR** | Graviton2/3 EC2 instances in EMR clusters |
| **Amazon OpenSearch** | Graviton2/3 data node instance types |
| **AWS CodeBuild** | arm1.* compute types backed by Graviton |

### Workload Fit Guide

**Benefits most from Graviton**:
- Web and application servers (nginx, Apache, Node.js, Django, Rails)
- Microservices and containerized workloads
- JVM-based applications (Java, Kotlin, Scala) — JVM is heavily Arm64-optimized
- Databases (PostgreSQL, MySQL, MariaDB, Redis) on Graviton RDS/ElastiCache
- Data processing pipelines (Spark on EMR)
- CI/CD build workloads (CodeBuild arm1, GitHub Actions self-hosted Arm64)

**May not benefit (or requires extra effort)**:
- x86-only legacy commercial software with no Arm64 build
- Some Windows workloads (Windows on Graviton is not supported)
- Software with hard-coded x86 SIMD intrinsics (SSE/AVX) without Arm64 equivalents
- Workloads requiring x86-specific hardware virtualization features

### Migration Guide

| Step | Details |
|---|---|
| **1. Compile for Arm64** | Use `--target aarch64-linux-gnu` or build on Graviton; most Linux distributions publish Arm64 packages |
| **2. Multi-arch containers** | Build with `docker buildx build --platform linux/amd64,linux/arm64`; tag image manifests for both architectures |
| **3. Validate dependencies** | Check third-party binaries and native extensions (Python C extensions, Node.js native modules) for Arm64 availability |
| **4. Test performance** | Benchmarks may differ from x86 — run application-level tests, not just synthetic benchmarks |
| **5. Use Graviton Savings Dashboard** | AWS Cost Explorer Graviton Savings Dashboard shows eligible resources and projected savings |

### Graviton Savings Dashboard

Access via **AWS Cost Explorer → Graviton Savings Dashboard**:
- Identifies EC2, Lambda, Fargate, and RDS resources still running on x86 that have Graviton equivalents
- Projects monthly and annual savings if migrated
- Shows migration readiness signals per resource

---

## AWS Trainium

**Purpose**: AWS-designed ML training accelerator chips (available as EC2 Trn1/Trn2/Trn3 instances) delivering high performance and cost efficiency for training large-scale deep learning models — up to 50% lower training cost than comparable GPU-based instances (p4d/p5).

### Chip Generations and Instance Families

| Instance | Chip | Key Specs | Best For |
|---|---|---|---|
| **trn1.2xlarge** | Trainium1 | 2 Trainium chips; 32 GB HBM | Single-node training / fine-tuning smaller models |
| **trn1.32xlarge** | Trainium1 | 16 Trainium chips; 512 GB HBM; NeuronLink interconnect | Large-scale LLM pre-training, distributed training |
| **trn2.48xlarge** | Trainium2 | 16 Trainium2 chips; 4× performance vs Trn1 | Frontier model training on a single node |
| **trn2u.48xlarge** (UltraServer) | Trainium2 | 64 Trainium2 chips; ultra-high bandwidth interconnect | Largest single-system training (frontier LLMs) |
| **Trn3** (3nm process) | Trainium3 | 2.52 PFLOPs; 144 GB HBM3e per chip; 4.4× vs Trn2 UltraServer | Cutting-edge GenAI / foundation model training |

### Trn2 UltraServer Topology

- 64 Trainium2 chips connected via purpose-built ultra-high bandwidth chip-to-chip interconnect
- Equivalent to a rack-scale training node in a single logical system
- No InfiniBand required within the UltraServer; bandwidth exceeds typical multi-node NVLink or EFA topologies
- Enables training models too large to fit on a standard multi-node cluster with conventional interconnects

### AWS Neuron SDK

The Neuron SDK is the shared software stack for Trainium and Inferentia:

| Component | Tool / Package | Description |
|---|---|---|
| **Neuron Compiler** | `neuronx-cc` / `torch-neuronx` | Compiles PyTorch/JAX computation graphs to NEFF (Neuron Executable File Format) |
| **Neuron Runtime** | `neuron-rtd` | Manages chip scheduling, memory allocation, and execution of compiled NEFF artifacts |
| **Neuron Monitor** | `neuron-monitor` | Exports NeuronCore utilization, memory, and throughput metrics to CloudWatch |
| **Neuron Profiler** | `neuron-profile` | Flame-graph style profiler for identifying bottlenecks in compiled models |
| **Neuron Tools** | `neuron-ls`, `neuron-top` | List attached Neuron devices; real-time utilization dashboard |

### Supported Frameworks

| Framework | Package | Notes |
|---|---|---|
| **PyTorch** | `torch-neuronx` | `torch.compile()` integration; XLA backend; minimal code changes from standard PyTorch |
| **JAX** | `jax-neuronx` | XLA compilation path; gradient checkpointing supported |
| **TensorFlow** | `tensorflow-neuron` | Graph-mode compilation via `tfn.trace()` |
| **Hugging Face** | `optimum-neuron` | One-line model export for Transformers; `NeuronTrainer` for fine-tuning |

### Distributed Training Support

| Technique | Details |
|---|---|
| **Tensor Parallelism** | Split individual layers (attention, FFN) across multiple NeuronCores/chips |
| **Data Parallelism** | Standard DDP; each chip processes a data shard; gradients all-reduced via NeuronLink/EFA |
| **Pipeline Parallelism** | Split model stages across chips; supported via `neuronx-distributed` library |
| **ZeRO-style sharding** | Model state partitioned across chips to fit very large models |

### EKS / ECS Integration

- **Neuron Device Plugin for Kubernetes**: exposes Neuron devices as `aws.amazon.com/neuron` resources; install via `kubectl apply`
- **Neuron Scheduler Extension**: bin-packing scheduler for multi-chip allocations
- ECS: Neuron runtime available in ECS-optimized Deep Learning AMI; task definitions request Neuron resourceRequirements

### Cost vs GPU Comparison (Training)

| | Trainium (trn1.32xlarge) | GPU (p4d.24xlarge) |
|---|---|---|
| Chips/GPUs | 16 Trainium1 chips | 8× NVIDIA A100 |
| On-demand price (approx.) | ~$21.50/hr | ~$32.77/hr |
| Relative cost for LLM training | Up to 50% lower total cost | Baseline |
| Framework ecosystem | Neuron SDK (PyTorch/JAX) | CUDA, cuDNN, NCCL |

### Use Cases

- Pre-training large language models (LLaMA, Mistral, GPT-style)
- Fine-tuning transformer models (LoRA, QLoRA, full fine-tune)
- Distributed training with tensor + data parallelism
- Research and experimentation at scale with lower compute cost

---

## AWS Inferentia

**Purpose**: AWS-designed ML inference accelerator chips (available as EC2 Inf1/Inf2 instances) delivering high throughput and low latency for serving trained deep learning models at significantly reduced cost versus GPU-based inference (g4dn/g5).

### Chip Generations and Instance Families

| Instance | Chip | Key Specs | Best For |
|---|---|---|---|
| **inf1.xlarge** | Inferentia1 | 1 chip; NeuronCore v1 | Dev/test, small model serving |
| **inf1.2xlarge** | Inferentia1 | 1 chip; enhanced networking | Single-model production endpoint |
| **inf1.6xlarge** | Inferentia1 | 4 chips; 32 GB HBM | Multi-model serving, batch inference |
| **inf1.24xlarge** | Inferentia1 | 16 chips; 128 GB total HBM | High-throughput inference fleet |
| **inf2.xlarge** | Inferentia2 | 1 chip; NeuronCore v2 | Low-latency single model endpoint |
| **inf2.8xlarge** | Inferentia2 | 1 chip; 32 GB HBM | Cost-efficient large model single-chip |
| **inf2.24xlarge** | Inferentia2 | 6 chips; 192 GB HBM | Multi-model, pipeline-parallel serving |
| **inf2.48xlarge** | Inferentia2 | 12 chips; 384 GB HBM; 4× throughput vs Inf1 | Largest LLM inference, lowest latency |

### Inferentia2 Performance Highlights

- 190 TFLOPS FP16 per chip (2 NeuronCores v2 per chip)
- Up to 10× lower latency vs Inferentia1
- 50% better performance-per-watt vs comparable GPU inference instances
- Sub-10ms latency for standard transformer model sizes
- Supports FP32, FP16, BF16, INT8, configurable FP8

### Neuron SDK — Inference Workflow

| Step | Tool / Library | Description |
|---|---|---|
| **1. Trace** | `torch_neuronx.trace()` | Capture the PyTorch model's computation graph |
| **2. Compile** | `neuronx-cc` | Compile traced graph to NEFF format; outputs `.neff` artifact |
| **3. Save** | `torch.jit.save()` | Serialize compiled model for deployment |
| **4. Load & Serve** | TorchServe / Triton / SageMaker | Load compiled model; serve inference requests |
| **5. Monitor** | `neuron-monitor`, CloudWatch | Track NeuronCore utilization, memory usage, and throughput |

### SageMaker Integration

- **ml.inf1.\*** instance types: inf1.xlarge → inf1.24xlarge for SageMaker real-time endpoints
- **ml.inf2.\*** instance types: inf2.xlarge → inf2.48xlarge for SageMaker real-time and async endpoints
- Neuron SDK pre-installed in AWS Deep Learning Containers for SageMaker
- `optimum-neuron` supports one-command model export for popular Hugging Face models

### Supported Model Types

| Category | Examples |
|---|---|
| **Transformer encoder** | BERT, RoBERTa, DistilBERT (text classification, NER, embeddings) |
| **Transformer decoder (LLM)** | GPT-2, LLaMA, Mistral, Falcon (text generation) |
| **Diffusion models** | Stable Diffusion (image generation) |
| **CNNs** | ResNet, EfficientNet, YOLO (image classification, object detection) |
| **RNNs** | LSTM, GRU (sequence models) |

### Cost vs GPU Comparison (Inference)

| | Inferentia2 (inf2.48xlarge) | GPU (g5.48xlarge) | GPU (g4dn.12xlarge) |
|---|---|---|---|
| Accelerators | 12× Inferentia2 | 8× NVIDIA A10G | 4× NVIDIA T4 |
| HBM | 384 GB | 192 GB | 64 GB |
| On-demand price (approx.) | ~$12.98/hr | ~$16.29/hr | ~$3.91/hr |
| Throughput advantage | Up to 4× vs Inf1 | Baseline (A10G) | — |

### Key Patterns

- Compile once, deploy many: compiled NEFF artifacts are reusable across same-family instances
- Model sharding: pipeline parallelism splits large LLMs across multiple NeuronCores for sub-10ms latency
- Continuous batching: maximizes token throughput for LLM serving
- Multi-model serving: multiple compiled models loaded on separate NeuronCores simultaneously

---

## AWS Nitro System

**Purpose**: A custom hardware and software stack that offloads virtualization, networking, storage, and security functions from the host CPU to dedicated ASICs and a lightweight hypervisor — enabling near bare-metal performance for customer workloads and a fundamentally enhanced security posture.

### Core Components

| Component | Description |
|---|---|
| **Nitro Card for VPC** | Dedicated ASIC handling all VPC networking (packet processing, security groups, routing); frees host CPU entirely |
| **Nitro Card for EBS** | Dedicated ASIC for EBS I/O; provides EBS-optimized performance without consuming instance CPU bandwidth |
| **Nitro Card for Instance Storage** | Dedicated ASIC for NVMe local instance storage on storage-optimized instances (I-family, D-family) |
| **Nitro Security Chip** | Hardware root of trust; cryptographically verifies and attests firmware integrity at boot; immutable once deployed |
| **Nitro Hypervisor** | Lightweight KVM-based hypervisor; consumes <2% of host CPU (vs 30%+ for traditional Xen-based hypervisors); provides memory and CPU isolation |
| **Nitro Enclaves** | Isolated, hardened EC2 sub-environment for processing sensitive data; no persistent storage, no interactive access, no external networking |

### What Nitro Enables

| Capability | How Nitro Makes It Possible |
|---|---|
| **Near bare-metal performance** | All hypervisor functions offloaded to dedicated ASICs; host CPU fully available to guest |
| **Bare-metal instances** | `*.metal` instance types: no hypervisor overhead; direct hardware access |
| **Enhanced networking (ENA)** | Elastic Network Adapter backed by Nitro Card; up to 100 Gbps instance bandwidth |
| **EBS-optimized by default** | All Nitro instances have dedicated EBS throughput via Nitro Card for EBS |
| **SR-IOV** | Single Root I/O Virtualization exposed via Nitro Cards for maximum network performance |
| **Dedicated Hosts** | Physical host isolation for compliance; Nitro tracks and enforces per-host instance placement |
| **Enhanced security** | Nitro Security Chip ensures firmware cannot be modified; cryptographic attestation of boot chain |

### Nitro Enclaves

Nitro Enclaves are isolated compute environments within an EC2 instance designed for processing highly sensitive data.

#### Key Properties

| Property | Details |
|---|---|
| **Isolation** | No persistent storage, no interactive access (SSH), no external networking |
| **Communication** | vsock only — a virtual socket between parent EC2 instance and enclave |
| **Attestation** | Enclave generates a cryptographically signed attestation document containing its code measurements |
| **KMS integration** | KMS `kms:Decrypt` policy can condition access on enclave attestation (PCR values); only attested enclaves can decrypt data |
| **Image format** | Enclave Image File (EIF) — signed, immutable image built from Docker image using `nitro-cli build-enclave` |

#### Nitro Enclaves Use Cases

- ML inference on sensitive data (PHI, PII) without exposing data to the parent OS
- Digital rights management (DRM) — cryptographic key operations in isolated environment
- HIPAA / PCI workloads requiring hardware-attested data isolation
- Cryptographic attestation workflows — proving code identity to external services via signed attestation documents
- Secure multi-party computation where data must not be visible even to the instance operator

#### Nitro Enclaves Concepts

```
Parent EC2 Instance
  │
  ├── vsock (virtio socket)
  │       │
  │       └── Nitro Enclave (isolated VM)
  │               • No network interfaces (except vsock)
  │               • No persistent disk
  │               • No SSH / console access
  │               • Runs EIF image
  │               • Produces attestation document (signed by AWS Nitro Attestation PKI)
  │
  └── KMS: kms:Decrypt conditioned on kms:RecipientAttestation:PCR0 == <expected enclave hash>
```

### Nitro System Coverage

All current-generation EC2 instance families run on the Nitro System. First-generation instance families (t1, m1, m2, c1, cc2, cg1) remain on the older Xen-based hypervisor.

---

## AWS Aquila (Custom Network Card)

**Purpose**: AWS-designed custom network card that enables ENA Express — ultra-low latency networking using the SRD (Scalable Reliable Datagram) protocol — delivering higher single-flow bandwidth and dramatically improved tail latency compared to standard ENA.

### Core Technology: SRD Protocol

| Property | Details |
|---|---|
| **Protocol** | Scalable Reliable Datagram (SRD) — AWS-proprietary transport protocol |
| **Multipathing** | Per-packet multipathing across multiple physical paths simultaneously |
| **Head-of-line blocking** | Eliminated — packets route around congestion; no single slow path blocks a flow |
| **Packet loss handling** | SRD handles selective retransmission at the network level; no application-layer retransmit delay |
| **Congestion control** | Fine-grained per-path congestion feedback; optimized for data center fabric |

### ENA Express Capabilities

| Metric | Standard ENA | ENA Express (via Aquila) |
|---|---|---|
| **Single-flow bandwidth** | Up to 10 Gbps | Up to 25 Gbps |
| **Tail latency (p99)** | Higher; affected by retransmits | Significantly reduced via SRD multipath |
| **Multi-flow aggregate** | Up to 100 Gbps (instance total) | Up to 100 Gbps (instance total) |
| **Packet loss behavior** | TCP retransmit adds latency | SRD handles transparently at transport layer |

### ENA vs ENA Express vs EFA

| | ENA | ENA Express | EFA |
|---|---|---|---|
| **Protocol** | TCP/IP | SRD | SRD + libfabric (OS-bypass) |
| **API** | Standard sockets | Standard sockets | libfabric / MPI (custom app changes required) |
| **Single-flow BW** | Up to 10 Gbps | Up to 25 Gbps | Up to 400 Gbps (EFA v3) |
| **Latency** | Lowest standard | Lower tail latency | Lowest (OS-bypass) |
| **Use case** | General compute | Web/app servers, distributed ML | HPC, tightly-coupled MPI, large-scale ML training |
| **Setup** | Default | Enable per ENI | EFA-enabled instance + placement group |

### Supported Instance Types (ENA Express / Aquila)

ENA Express is supported on instances with the Aquila network card:
- C6gn, C6in, C7gn — compute-optimized with enhanced networking
- Hpc7g — HPC Graviton3 instances
- Additional select instance families with 100 Gbps+ networking capability

### Key Patterns

- ENA Express is enabled **per ENI** (Elastic Network Interface), not per instance; both communicating instances must have ENA Express enabled
- Ideal for: distributed ML training (collective operations benefit from reduced tail latency), HPC workloads, high-volume microservice meshes
- ENA Express does not require application changes — standard TCP sockets benefit automatically
- For MPI-based HPC workloads requiring OS-bypass, use EFA instead of (or in addition to) ENA Express
