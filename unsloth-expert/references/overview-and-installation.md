# Unsloth: Overview & Installation

## What Is Unsloth

Unsloth is a framework for training and running open LLMs locally with hand-optimized CUDA kernels that dramatically reduce memory usage and increase training speed. It ships two interfaces:

- **Unsloth Studio** — local browser-based no-code GUI (Windows/Linux/macOS/WSL)
- **Unsloth Core** — Python library for programmatic fine-tuning

Supports 500+ models including text, vision, audio, and embedding architectures.

Dual-licensed: Apache 2.0 (core library) and AGPL-3.0 (Studio UI).

---

## Performance Claims

| Metric | Claim |
|--------|-------|
| Training speed | ~2x faster vs standard HuggingFace + FA2 |
| VRAM reduction (general) | ~70% less |
| VRAM reduction (GRPO/RL) | ~80% less |
| MoE training | 12x faster |
| Context length (RL) | 7x longer |
| Accuracy loss | None claimed |

These gains come from custom Triton/CUDA kernels for attention, cross-entropy loss, RoPE embeddings, and other operations, plus intelligent gradient checkpointing.

---

## Supported Hardware

**Unsloth Studio (full training support):**
- NVIDIA: RTX 30/40/50 series, Blackwell, DGX Spark
- macOS: Chat and Data Recipes (MLX-based training coming)
- AMD/Intel: Chat only in Studio; full training via Unsloth Core
- CPU: Chat and Data Recipes only

**Unsloth Core:**
- Linux, Windows (WSL), Windows native
- NVIDIA GPUs with CUDA 12.4+
- Intel GPUs (experimental)
- CPU-only (inference, limited training)

**Minimum practical VRAM for training:**
- 8GB VRAM: Gemma-4-E2B (4-bit), Llama 3.2 1B/3B, Qwen2.5-3B
- 16GB VRAM: Llama 3.1 8B (4-bit QLoRA), Mistral 7B
- 24GB VRAM: Llama 3.1 8B (16-bit LoRA), Mistral 22B (4-bit)
- 40GB+ VRAM: 70B models (4-bit QLoRA)

---

## Installation

### One-Line Installer (Recommended for Unsloth Studio)

**macOS, Linux, WSL:**
```bash
curl -fsSL https://unsloth.ai/install.sh | sh
```

**Windows PowerShell:**
```powershell
irm https://unsloth.ai/install.ps1 | iex
```

These installers set up the full environment and make the `unsloth` CLI available.

### Unsloth Core via pip (for notebook/script usage)

```bash
# Auto-detect torch backend (recommended)
uv pip install unsloth --torch-backend=auto

# Or with explicit CUDA version (CUDA 12.1)
pip install "unsloth[cu121-torch230]"

# CUDA 12.1, latest torch:
pip install "unsloth[cu121]"

# CUDA 12.3:
pip install "unsloth[cu123]"

# CPU-only:
pip install "unsloth[cpu]"

# From GitHub (dev/latest):
pip install git+https://github.com/unslothai/unsloth.git
```

### pip with Dependencies (full install for CUDA 12.1)

```bash
pip install torch==2.3.0 torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
pip install "unsloth[cu121-torch230]" xformers trl peft accelerate bitsandbytes
```

### conda Install

```bash
conda create --name unsloth_env python=3.11 -y
conda activate unsloth_env

# Install PyTorch first
conda install pytorch-cuda=12.1 pytorch cudatoolkit xformers -c pytorch -c nvidia -c xformers -y

# Then unsloth
pip install "unsloth[colab-new]"
pip install --upgrade trl peft accelerate bitsandbytes
```

### Docker

```bash
# Pull official image
docker pull unsloth/unsloth

# Run with GPU support
docker run --gpus all -p 8000:8000 unsloth/unsloth

# Access at http://localhost:8000
```

Note: Docker supports Windows, WSL, Linux. macOS Docker support coming.

### Google Colab

```python
# Typically already available; upgrade to latest:
%%capture
!pip install --upgrade --force-reinstall --no-cache-dir --no-deps unsloth unsloth_zoo
```

---

## Updating Unsloth

```bash
# Via CLI
unsloth studio update

# Via pip
pip install --upgrade --force-reinstall --no-cache-dir --no-deps unsloth unsloth_zoo
```

---

## Platform Prerequisites

**Linux / WSL:**
- Ubuntu 20.04+ (64-bit)
- NVIDIA GPU drivers + CUDA 12.4+
- Python 3.11–3.13
- Git

**Windows:**
- Windows 10/11 (64-bit)
- NVIDIA GPU with drivers
- App Installer (`winget`)
- Git, Python 3.11–3.13

**macOS:**
- macOS 12 Monterey or newer
- Homebrew, Git, cmake, openssl
- Python 3.11–3.13
