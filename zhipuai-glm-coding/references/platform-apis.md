---
name: zhipuai-glm-platform-apis
description: Z.ai platform APIs beyond the GLM Coding Plan — Vision/VLM models (GLM-4.6V, GLM-5V-Turbo, GLM-OCR), image generation (CogView-4, GLM-Image), speech recognition (GLM-ASR-2512), video generation (CogVideoX-3, Vidu), and Agent Services (Translation, Slide/Poster). All billed pay-as-you-go via the same API key. Use when building multimodal pipelines, document processing, image/video generation, or managed agent workflows.
type: reference
---

# Z.ai Platform APIs — Beyond the Coding Plan

All APIs below are billed **pay-as-you-go** using your Z.ai API key. They are separate from the Coding Plan quota — usage does not count against your 5-hour prompt budget.

Base endpoint: `https://api.z.ai/api/paas/v4/`

---

## Vision / VLM Models

### GLM-4.6V

Multimodal chat model. Accepts images, video, documents, and text in a single request.

- **Context:** 128K tokens
- **Variants:** `glm-4.6v` (full) · `glm-4.6v-flashx` (fast, cheap) · `glm-4.6v-flash` (free)
- **Native multimodal tool use** — images can be passed directly as tool parameters without text conversion
- **Key capabilities:** Frontend code from screenshots, 150-page document analysis, 1-hour video understanding, multi-image comparison

```python
from zai import ZaiClient

client = ZaiClient(api_key="your-key")
response = client.chat.completions.create(
    model="glm-4.6v",
    messages=[{"role": "user", "content": [
        {"type": "image_url", "image_url": {"url": "https://example.com/screenshot.png"}},
        {"type": "text",      "text": "Generate the React component that matches this UI screenshot."}
    ]}]
)
```

**Use in coding workflows:** Pass error screenshots, UI mockups, or architecture diagrams directly. The free `glm-4.6v-flash` variant is useful for high-volume screenshot analysis in CI pipelines.

---

### GLM-5V-Turbo

Vision model specialized for GUI automation and visual programming tasks. Released April 2026.

- **Key strength:** GUI task execution — understands button states, form fields, navigation flows
- **Use cases:** Automated UI testing, desktop automation agents, converting design mockups to code

---

### GLM-OCR

Dedicated OCR model. Converts PDFs, scanned documents, and images into structured text.

- **Size:** 0.9B parameters (fast, cheap)
- **Output formats:** Markdown, JSON, or LaTeX
- **Preserves:** Tables, formulas, document structure
- **Pricing:** $0.03 per million tokens (flat, input + output)

```python
response = client.chat.completions.create(
    model="glm-ocr",
    messages=[{"role": "user", "content": [
        {"type": "image_url", "image_url": {"url": "https://example.com/invoice.pdf"}},
        {"type": "text",      "text": "Extract all line items as JSON."}
    ]}]
)
```

**Use cases:** Extracting API specs from PDFs, parsing legacy documentation, processing scanned tickets or invoices in development workflows.

---

## Image Generation

### CogView-4

Text-to-image generation. Bilingual (English + Chinese), supports any resolution.

- **Pricing:** $0.01 per image
- **Model ID:** `cogView-4-250304`
- **Benchmark:** #1 on DPG-Bench for semantic understanding and instruction following
- **Strength:** Generates readable text within images (logos, diagrams, UI mockups with labels)

```python
response = client.images.generations(
    model="cogView-4-250304",
    prompt="A dark-mode dashboard UI showing a time-series chart with a sidebar nav",
    size="1024x1024"
)
image_url = response.data[0].url
```

```bash
curl -X POST https://api.z.ai/api/paas/v4/images/generations \
  -H "Authorization: Bearer $ZAI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"cogView-4-250304","prompt":"...","size":"1920x1080"}'
```

**Async generation:** For large images, use the async endpoint (`/images/generations/async`) and poll `/images/status/{id}`.

---

### GLM-Image

Alternative image model optimized for stable, accurate text rendering.

- **Pricing:** $0.015 per image
- **Strength:** More reliable for technical diagrams with text labels

---

## Audio / Speech

### GLM-ASR-2512

Speech-to-text (automatic speech recognition).

- **Pricing:** $0.0024 per minute
- **Accuracy:** 0.0717 character error rate
- **Endpoint:** `https://api.z.ai/api/paas/v4/audio/transcriptions`

```python
with open("meeting.mp3", "rb") as audio_file:
    transcript = client.audio.transcriptions.create(
        model="glm-asr-2512",
        file=audio_file
    )
print(transcript.text)
```

**Use cases:** Transcribing voice requirements into tickets, processing recorded standup notes, audio-to-code workflows.

---

## Video Generation

All video generation is async — submit a job, poll for the result.

| Model | Input | Price | Notes |
|-------|-------|-------|-------|
| **CogVideoX-3** | Text or image | ~$0.2–0.4/video | Open-source lineage, strong motion consistency |
| **Vidu Q1** | Text or image | ~$0.2–0.4/video | Cinematic quality |
| **Vidu 2** | Text, image, or video | ~$0.2–0.4/video | Highest quality; video-to-video supported |

Endpoint: `POST /v4/videos/generations` → `GET /v4/videos/status/{id}`

Primarily useful for product demos, documentation videos, or UI prototype animations rather than day-to-day coding workflows.

---

## Agent Services

Managed agents that handle multi-step tasks internally. Billed per token consumed by the agent pipeline.

### Translation Agent

Full-document translation with context awareness.

- **Pricing:** $3 per million tokens
- **Strength:** Maintains technical terminology, code comments, and document structure

```python
response = client.chat.completions.create(
    model="translation",   # agent model ID
    messages=[{"role": "user", "content": "Translate this API documentation to Spanish: ..."}]
)
```

### Slide / Poster Agent (Beta)

Generates professional slides or posters from text descriptions.

- **Pricing:** $0.7 per million tokens (beta)
- **Use case:** Auto-generating architecture diagrams, sprint retrospective slides, API documentation presentations

---

## PAYG API vs. Coding Plan — When to Use Each

| Use PAYG API when | Use Coding Plan when |
|-------------------|---------------------|
| Building a product that calls GLM directly | Using Claude Code / Cline / Roo Code interactively |
| Calling vision, image, audio, or video APIs | Doing day-to-day coding assistance |
| Volume is unpredictable or low | Volume is high and predictable |
| Needing free-tier models (GLM-4.7-Flash) | Needing Coding Plan MCP tools (Web Search, Vision MCP) |
| Integrating into a CI/CD pipeline | Working in an IDE-integrated agent |

Both use the **same API key**. PAYG charges to your account balance; Coding Plan uses your subscription quota.

---

## PAYG Text Model Pricing (Selected)

| Model | Input ($/M) | Output ($/M) | Notes |
|-------|------------|-------------|-------|
| GLM-4.7-Flash | **FREE** | **FREE** | Good for high-volume, low-stakes calls |
| GLM-4.5-Flash | **FREE** | **FREE** | Lightweight free tier |
| GLM-4.7-FlashX | $0.07 | — | Budget paid tier |
| GLM-4.5-X | $2.2 | — | Premium reasoning variant |

Free models are rate-limited but usable for development, testing, and non-critical pipelines. They do not consume Coding Plan quota.
