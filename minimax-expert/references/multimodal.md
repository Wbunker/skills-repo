# MiniMax Multimodal APIs

MiniMax offers four multimodal capability areas beyond text: **Speech**, **Video** (Hailuo), **Music**, and **Image**.

> Note: These are separate API endpoints — not available via the text chat endpoint. Image input to the chat/completions API is not yet supported.

## Speech (Text-to-Speech)

Models: `speech-2.8`, `speech-2.6`

Features:
- 40+ language support
- Voice Cloning: 5-second rapid cloning from a short audio sample
- Multi-language cloning from single sample
- Voice Design: generate custom voice characters

Pricing (pay-as-you-go):
- T2A: $60–$100 / 1M characters
- Voice Cloning: $1.50 per voice
- Voice Design: $3.00 per voice

Token Plan unlocks:
- Starter: not included
- Plus ($20/mo): 4,000 speech chars/day
- Max ($50/mo): 11,000 speech chars/day
- Ultra-Highspeed ($150/mo): 50,000 speech chars/day

## Video Generation (Hailuo)

Models: `hailuo-2.3`, `hailuo-2.3-fast`, `hailuo-02`

Features:
- Text-to-video and image-to-video
- Rate limit: 5 RPM

Pricing (pay-as-you-go):
- Hailuo 2.3 Fast: $0.19–$0.33 per video
- Hailuo 2.3 / 02: $0.10–$0.56 per video

Token Plan unlocks:
- Max ($50/mo): 2 videos/day
- Max-Highspeed ($80/mo): 3 videos/day
- Ultra-Highspeed ($150/mo): 5 videos/day

## Music Generation

Models: `music-2.6`

Features:
- Generate music tracks up to 5 minutes
- Lyrics generation included
- 120 RPM, 20 simultaneous connections

Pricing (pay-as-you-go):
- Music: $0.03–$0.15 per 5-minute track
- Lyrics: $0.01 per song

Token Plan: all tiers include 100 songs/day (≤5 min each, limited free)

## Image Generation

Model: `image-01`

Features:
- Text-to-image and image-to-image
- MCP API-vlm for visual language model queries
- Rate limit: 10 RPM

Pricing (pay-as-you-go):
- Image generation: $0.0035 per image
- MCP API-vlm: $0.06 per request

Token Plan unlocks:
- Starter: not included
- Plus ($20/mo): 50 images/day
- Max ($50/mo): 120 images/day
- Ultra-Highspeed ($150/mo): 800 images/day

## MCP Integration

MiniMax provides an official MCP server with:
- Web search
- Image understanding (vlm)

Documented integrations: Claude Code, Cursor, Cline, Zed, and 15+ other coding tools.

## Important Limitations

- Image inputs to the **text chat API** are not yet supported (as of 2026-05)
- Video rate limits (5 RPM) mean generation is not suitable for real-time applications
- Voice cloning requires a short audio sample — not text-only
