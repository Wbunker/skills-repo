# Gemma Multimodal Capabilities

## Capability Matrix by Variant

| Variant | Images | Video | Audio | Video+Audio |
|---------|--------|-------|-------|-------------|
| gemma-4-e2b | No | No | Yes (≤30s) | Yes |
| gemma-4-e4b | No | No | Yes (≤30s) | Yes |
| gemma-4-12b | Yes | No | No | No |
| gemma-4-26b-a3b | Yes | Yes (≤60s) | No | No |
| gemma-4-26b-a4b | Yes | Yes (≤60s) | No | No |
| gemma-4-31b | Yes | Yes (≤60s) | No | No |
| gemma-3-27b | Yes | No | No | No |

Video is sampled at **1 fps**. No audio extraction from video for 26B/31B variants.

---

## Image Input

### Google AI Studio / Vertex AI

```python
from google import genai
from google.genai import types
import base64
from pathlib import Path

client = genai.Client(api_key="YOUR_API_KEY")

# From file
image_bytes = Path("image.jpg").read_bytes()
image_part = types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg")

response = client.models.generate_content(
    model="gemma-4-26b-a4b",
    contents=[
        types.Content(parts=[
            image_part,
            types.Part(text="Describe this image in detail.")
        ])
    ]
)
print(response.text)
```

### HuggingFace transformers

```python
from transformers import AutoProcessor, AutoModelForImageTextToText
from PIL import Image
import torch

model_id = "google/gemma-4-27b-it"
processor = AutoProcessor.from_pretrained(model_id)
model = AutoModelForImageTextToText.from_pretrained(
    model_id,
    device_map="auto",
    torch_dtype=torch.bfloat16,
)

image = Image.open("image.jpg")
messages = [
    {
        "role": "user",
        "content": [
            {"type": "image"},
            {"type": "text", "text": "What do you see in this image?"}
        ]
    }
]

inputs = processor.apply_chat_template(
    messages,
    add_generation_prompt=True,
    tokenize=True,
    return_dict=True,
    return_tensors="pt",
    images=[image],
).to("cuda")

outputs = model.generate(**inputs, max_new_tokens=512)
result = processor.decode(outputs[0][inputs["input_ids"].shape[1]:], skip_special_tokens=True)
print(result)
```

### Supported Image Formats
- JPEG, PNG, WebP, HEIC, HEIF
- Max resolution: No hard limit, but very large images are downscaled internally
- Multiple images per prompt supported

---

## Video Input (26B / 31B only)

```python
from google import genai
from google.genai import types

client = genai.Client(api_key="YOUR_API_KEY")

# Upload video file first
video_file = client.files.upload(path="video.mp4")

response = client.models.generate_content(
    model="gemma-4-26b-a4b",
    contents=[
        types.Content(parts=[
            types.Part.from_uri(file_uri=video_file.uri, mime_type="video/mp4"),
            types.Part(text="Summarize what happens in this video.")
        ])
    ]
)
```

**Limits**: Max 60 seconds, 1 fps sampling, no audio extraction.

---

## Audio Input (E2B / E4B only)

```python
from google import genai
from google.genai import types
from pathlib import Path

client = genai.Client(api_key="YOUR_API_KEY")

audio_bytes = Path("audio.wav").read_bytes()
audio_part = types.Part.from_bytes(data=audio_bytes, mime_type="audio/wav")

response = client.models.generate_content(
    model="gemma-4-e4b",
    contents=[
        types.Content(parts=[
            audio_part,
            types.Part(text="Transcribe and summarize this audio.")
        ])
    ]
)
```

**Limit**: Max 30 seconds of audio per request.

---

## Video with Audio (E2B / E4B only)

```python
response = client.models.generate_content(
    model="gemma-4-e2b",
    contents=[...],
    config=types.GenerateContentConfig(
        # Enable audio extraction from video
        # (available only for E2B/E4B)
    )
)
```

Use `load_audio_from_video=True` in the config when available — documentation may vary by SDK version.

---

## Local Multimodal Inference

Multimodal support in local frameworks varies:

| Framework | Image | Video | Audio |
|-----------|-------|-------|-------|
| Ollama | Yes (recent versions) | No | No |
| llama.cpp | Yes (GGUF with vision) | No | No |
| LM Studio | Yes | No | No |
| vLLM | Yes (experimental) | No | No |
| HuggingFace transformers | Yes | No | No |

For video and audio, use the Google AI Studio API — local inference frameworks do not yet support these modalities for Gemma 4.

---

## Vision Quality Notes

- **26B A4B**: Strong at complex visual reasoning, document analysis, chart interpretation
- **E4B**: Capable for on-device tasks but underperforms 26B on visual tasks requiring detailed understanding
- **E2B**: Limited visual capability — suited for simple classification tasks, not complex scene understanding
- **RAG + vision**: The model may rely on visual internal knowledge even when document context is provided. Explicitly instruct the model to use the provided image as its primary source

---

## Gotchas

- E-series (E2B/E4B) do **not** support image input — audio/video only
- 26B/31B do **not** support audio input — image/video only
- Video sampling at 1 fps means fast actions may be missed; consider extracting key frames manually
- Local llama.cpp vision requires a specific GGUF file built with vision encoder — not all GGUF exports include it
