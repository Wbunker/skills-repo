# MiniMax Pricing Reference

## Token Plan (Flat Monthly Subscriptions)

The Token Plan offers fixed monthly fees with request quotas — no per-token billing. Ideal for always-on agents or consistent daily usage.

| Tier | Monthly | Annual | Key Limits |
|---|---|---|---|
| **Starter** | $10/mo | $100/yr | 1,500 M2.7 requests / 5 hrs |
| **Plus** | $20/mo | $200/yr | 4,500 M2.7 req/5hrs; 4,000 speech chars/day; 50 images/day |
| **Max** | $50/mo | $500/yr | 15,000 M2.7 req/5hrs; 11,000 speech chars/day; 120 images/day; 2 videos/day |
| **Plus-Highspeed** | $40/mo | — | 4,500 M2.7-highspeed req/5hrs; 9,000 speech chars/day; 100 images/day |
| **Max-Highspeed** | $80/mo | — | 15,000 highspeed req/5hrs; 19,000 speech chars/day; 200 images/day; 3 videos/day |
| **Ultra-Highspeed** | $150/mo | — | 30,000 highspeed req/5hrs; 50,000 speech chars/day; 800 images/day; 5 videos/day |

Annual billing saves ~17%.

**Important Token Plan notes:**
- Rate limits are per **5-hour window**, not per month
- Speech and image generation features only unlock at **Plus tier and above**
- All tiers include Music-2.6 at 100 songs/day (≤5 min each, limited free tier)
- The Starter $10/mo plan is a good fit for an always-on personal agent (e.g., OpenClaw + MiniMax setup)

## Pay-As-You-Go Pricing

### Text Models

| Model | Input $/M | Output $/M | Cache Read $/M | Cache Write $/M |
|---|---|---|---|---|
| MiniMax-M2.7 | $0.30 | $1.20 | ~$0.059 | ~$0.375 |
| MiniMax-M2.7-highspeed | $0.60 | $2.40 | — | — |
| MiniMax-M2.5 | $0.30 | $1.20 | ~$0.06 | — |
| MiniMax-M2.5-highspeed | $0.60 | $2.40 | — | — |
| MiniMax-M2-her | $0.30 | $1.20 | — | — |

### Multimodal

| API | Pricing |
|---|---|
| Text-to-Speech | $60–$100 / 1M characters |
| Voice Cloning | $1.50 per voice |
| Voice Design | $3.00 per voice |
| Hailuo 2.3 Fast (video) | $0.19–$0.33 per video |
| Hailuo 2.3 / 02 (video) | $0.10–$0.56 per video |
| Music (all models) | $0.03–$0.15 per 5-min track |
| Image (image-01) | $0.0035 per image |
| Lyrics | $0.01 per song |
| MCP API-vlm | $0.06 per request |

## API Rate Limits (Pay-As-You-Go)

| API | Requests/min | Tokens/min |
|---|---|---|
| Text (all models) | 500 RPM | 20,000,000 TPM |
| Speech (T2A) | 60 RPM | 20,000 TPM |
| Voice Cloning | 60 RPM | — |
| Voice Design | 20 RPM | — |
| Video (all Hailuo) | 5 RPM | — |
| Image (image-01) | 10 RPM | 60 TPM |
| Music (all) | 120 RPM | 20 connections |

To raise rate limits: contact `api@minimax.io`

## Cost Comparison

Running M2.7 at 1,500 requests/day with average ~1,000 tokens output each:
- Pay-as-you-go: ~$1.80/day = ~$54/month
- Token Plan Starter: $10/month (capped at 1,500 req / 5 hrs)

For an always-on personal agent with moderate usage, the $10/month Starter plan is dramatically cheaper than pay-as-you-go.

## Pricing Docs

- Token Plan: `https://platform.minimax.io/docs/guides/pricing-token-plan`
- Pay-as-you-go: `https://platform.minimax.io/docs/guides/pricing-paygo`
- Rate Limits: `https://platform.minimax.io/docs/guides/rate-limits`
