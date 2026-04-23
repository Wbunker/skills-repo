# OpenAI Models (April 2026)

## GPT-4.1 Family — Current Recommended General-Purpose

Released April 14, 2025. Replaced GPT-4o as OpenAI's primary production recommendation.

| Model | Context Window | Input | Cached Input | Output | Batch Input | Batch Output |
|-------|---------------|-------|--------------|--------|-------------|--------------|
| **gpt-4.1** | 1,047,576 tokens (1M) | $2.00/M | $0.50/M | $8.00/M | — | — |
| **gpt-4.1-mini** | 1M | $0.40/M | — | $1.60/M | — | — |
| **gpt-4.1-nano** | 1M | $0.10/M | — | $0.40/M | — | — |

**Important:** Context >272K tokens incurs a 2x surcharge on input tokens.

**Key advantages over GPT-4o:**
- Larger context (1M vs 128K)
- Lower cost (gpt-4.1: $2/$8 vs gpt-4o: $2.50/$10)
- Better instruction following
- Better coding performance

**Capabilities:** Vision, function calling, structured outputs, prompt caching (gpt-4.1), streaming.

**Performance (gpt-4.1 benchmarks):**
- MMLU Pro: 80.6
- GPQA: 66.6
- LiveCodeBench: 45.7
- AIME: 43.7
- Output speed: ~108 tokens/second
- Time to first token: ~0.63s median

**When to use:**
- `gpt-4.1` — production workloads, long documents, complex coding tasks
- `gpt-4.1-mini` — balanced cost/performance, high-volume applications
- `gpt-4.1-nano` — highest volume, most cost-sensitive, lightweight tasks; cheapest capable model anywhere

---

## GPT-4o Family — Legacy (Still Available)

| Model | Context Window | Input | Cached Input | Output |
|-------|---------------|-------|--------------|--------|
| **gpt-4o** | 128K | $2.50/M | $0.25/M | $10.00/M |
| **gpt-4o-mini** | 128K | $0.15/M | $0.075/M | $0.60/M |

GPT-4o still widely deployed. GPT-4.1 outperforms it at lower cost with larger context. GPT-4o-mini remains useful for very cost-sensitive small-context tasks vs gpt-4.1-nano tradeoff.

---

## o-Series Reasoning Models

These models use internal chain-of-thought "thinking" before responding. Trade latency for accuracy on complex tasks.

| Model | Context | Input | Cached | Output | Notes |
|-------|---------|-------|--------|--------|-------|
| **o4-mini** | 200K | $1.10/M | $0.275/M | $4.40/M | Best cost/reasoning ratio |
| **o3** | 200K | $2.00/M | $0.50/M | $8.00/M | Best standard reasoning model |
| **o3-mini** | 200K | $0.50/M | — | $2.00/M | Lighter reasoning |
| **o1** | 200K | $15.00/M | — | $60.00/M | Earlier gen; largely superseded |
| **o1-mini** | 128K | $1.10/M | — | $4.40/M | Earlier small reasoning model |

**o3 key details:**
- 20% fewer major errors than o1 on real-world tasks
- "Thinks with images" — multimodal reasoning
- 10x more compute than o1
- Excels at: programming, business/consulting, creative ideation, complex math
- Performance keeps climbing with longer thinking time

**o4-mini key details:**
- 4x larger context than o3-mini (128K → 200K per search results; 200K per pricing)
- Faster than o3-mini at same reasoning effort
- Roughly 10x cheaper than o3 for both input and output
- First reasoning model with full tool support: web search, Python, file/image analysis, function calling, image generation
- Best choice for high-volume reasoning tasks

**When to use reasoning models:**
- Hard math / theorem proving
- Complex multi-step coding
- Scientific reasoning requiring deliberation
- Tasks where taking more time to think measurably improves accuracy
- When latency is acceptable

**When NOT to use reasoning models:**
- Simple Q&A, classification, summarization → use GPT-4.1
- Real-time/streaming applications requiring fast first token → use GPT-4.1
- Cost-sensitive high-volume → use GPT-4.1 mini or nano

**Hierarchy:** o3-pro > o3 > o4-mini > o3-mini > o1-mini

---

## Embeddings

| Model | Dimensions | Price |
|-------|-----------|-------|
| text-embedding-3-small | 1536 | $0.02/M tokens |
| text-embedding-3-large | 3072 | $0.13/M tokens |

text-embedding-3-large has higher accuracy; text-embedding-3-small is sufficient for most retrieval tasks.

---

## Image Generation

| Model/Size | Price |
|-----------|-------|
| DALL-E 3 Standard 1024×1024 | $0.040/image |
| DALL-E 3 HD 1024×1024 | $0.080/image |
| DALL-E 3 HD 1792×1024 or 1024×1792 | $0.120/image |
| gpt-image-1 (via Responses API image_generation tool) | Token-based |

---

## Audio / Speech

| Service | Price |
|---------|-------|
| Whisper (speech-to-text) | $0.006/minute |
| TTS (text-to-speech) | $5.00/M characters |
| TTS HD | $30.00/M characters |

---

## Batch API Pricing (50% off standard)

Responses within 24 hours.

| Model | Batch Input | Batch Output |
|-------|-------------|--------------|
| GPT-4o | $0.25/M | $5.00/M (half of $10) |
| GPT-4o-mini | $0.075/M | $0.30/M |
| o3 | $1.00/M | $8.00/M (half of $16) |
| o4-mini | $0.55/M | $2.20/M |

---

## Model Selection Quick Reference

| Need | Model |
|------|-------|
| Long documents (>128K) | gpt-4.1 |
| Best instruction following | gpt-4.1 |
| Cheapest capable | gpt-4.1-nano |
| Best cost/performance balance | gpt-4.1-mini |
| Hard math/science/coding | o3 |
| Reasoning at lower cost | o4-mini |
| Maximum intelligence | o3-pro |
| Legacy compatibility | gpt-4o |
| Embeddings (fast) | text-embedding-3-small |
| Embeddings (accurate) | text-embedding-3-large |
