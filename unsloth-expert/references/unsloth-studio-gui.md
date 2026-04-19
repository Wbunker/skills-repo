# Unsloth Studio GUI

## What Is Unsloth Studio

Unsloth Studio is a local, browser-based no-code interface for:
- Downloading and running 500+ models (chat, inference)
- Fine-tuning models with SFT, DPO, GRPO
- Creating datasets from PDFs, CSVs, DOCX files (Data Recipes)
- Exporting models to GGUF, Safetensors, LoRA formats
- 100% offline — no data leaves your machine

Licensed under AGPL-3.0.

---

## Installation

### macOS / Linux / WSL

```bash
curl -fsSL https://unsloth.ai/install.sh | sh
```

### Windows (PowerShell)

```powershell
irm https://unsloth.ai/install.ps1 | iex
```

These scripts install all dependencies (Python environment, CUDA, PyTorch, Unsloth) and make the `unsloth` CLI available.

### Manual / Local Install (Alternative)

```bash
# Linux/Mac
git clone https://github.com/unslothai/unsloth
cd unsloth
./install.sh --local

# Windows PowerShell
git clone https://github.com/unslothai/unsloth.git
cd unsloth
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\install.ps1 --local
```

### Docker

```bash
docker pull unsloth/unsloth
docker run --gpus all -p 8000:8000 unsloth/unsloth
# Access: http://localhost:8000
```

---

## Launching the Studio

```bash
# Standard launch on all interfaces, port 8888
unsloth studio -H 0.0.0.0 -p 8888
```

Then open `http://localhost:8888` in any browser.

**Options:**
```bash
unsloth studio              # Default (localhost only)
unsloth studio -p 9999      # Custom port
unsloth studio -H 0.0.0.0   # Expose to network (allows remote access)
```

### First Launch
1. Create a password to secure your local instance
2. Sign in with that password on future launches
3. Optional onboarding wizard — choose model, dataset, settings (skippable)

---

## Platform Requirements

| Platform | Training | Chat | Notes |
|----------|----------|------|-------|
| NVIDIA GPU (Linux/WSL) | Full | Yes | CUDA 12.4+ required |
| NVIDIA GPU (Windows) | Full | Yes | Windows 10/11 64-bit |
| Apple Silicon (Mac) | Coming soon | Yes | MLX training in development |
| AMD GPU | Unsloth Core only | Studio chat | Use Core Python API |
| Intel GPU | Unsloth Core only | Studio chat | |
| CPU only | No | Yes | Slow inference |

**Minimum GPU:** NVIDIA RTX 3060 (12GB VRAM) for most small models.
**Supported GPUs:** RTX 30/40/50 series, Blackwell, DGX Spark.

---

## Studio Workflow

### 1. Choose a Model
- Browse the built-in catalog (500+ models)
- Filter by size, type (text/vision/code), and VRAM requirement
- Download GGUF or full-precision versions
- Models are cached locally after first download

### 2. Chat / Inference
- Load any downloaded model for immediate chat
- Adjust temperature, max tokens, system prompt
- Supports streaming output

### 3. Fine-Tuning Workflow
1. **Select model** — pick base or instruct model
2. **Load dataset** — from HuggingFace ID, file upload (CSV/JSONL), or create with Data Recipes
3. **Configure training** — sliders for rank, alpha, learning rate, batch size, epochs
4. **Start training** — live loss chart and GPU usage monitor
5. **Export** — when done, choose output format

### 4. Data Recipes (Auto Dataset Creation)
- Upload PDFs, CSVs, DOCX, or paste text
- Visual node-based graph editor for pipeline building
- Auto-generates instruction pairs or conversation format
- Preview and validate before full processing
- Export to HuggingFace datasets or local JSONL

### 5. Export Model
- **LoRA only** — smallest file, ~100MB
- **Merged Safetensors (16-bit)** — full merged model
- **GGUF** — select quantization (q4_k_m recommended)
- **Push to HuggingFace** — direct upload from GUI
- **Push to Ollama** — generates Modelfile and registers model

---

## Updating Studio

```bash
# Via CLI
unsloth studio update

# Or re-run original install script
curl -fsSL https://unsloth.ai/install.sh | sh
```

---

## Studio vs Core — When to Use Which

| Scenario | Use |
|----------|-----|
| Quick experiments, no coding | Studio GUI |
| Reproducible pipelines / CI | Core Python API |
| Custom reward functions (GRPO) | Core Python API |
| Multi-GPU training | Core Python API (Studio support coming) |
| Windows user, new to ML | Studio GUI |
| AMD / Intel GPU | Core Python API |
| Notebook (Colab, Kaggle) | Core Python API |
