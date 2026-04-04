# WhatsApp Pricing, Messaging Tiers & Quality

## Table of Contents
1. [Pricing Model (July 2025+)](#pricing-model-july-2025)
2. [Message Categories & Rates](#message-categories--rates)
3. [Free Messaging Windows](#free-messaging-windows)
4. [Messaging Tiers](#messaging-tiers)
5. [Tier Auto-Upgrade Conditions](#tier-auto-upgrade-conditions)
6. [Phone Number Quality Rating](#phone-number-quality-rating)
7. [Business Verification](#business-verification)
8. [Official Business Account (Green Checkmark)](#official-business-account-green-checkmark)
9. [BSP vs. Direct Access — Cost Comparison](#bsp-vs-direct-access--cost-comparison)

---

## Pricing Model (July 2025+)

**Per-message pricing (PMP)** replaced per-conversation pricing effective **July 1, 2025**.

- Previously: 1 charge per 24-hour conversation window regardless of message count
- Now: each message sent is individually billed
- Exception: service messages (replies within customer-initiated 24-hour window) remain **free**

This rewards quality over quantity: sending one targeted message costs less than sending 5 messages in an engagement sequence.

---

## Message Categories & Rates

| Category | When Used | Cost |
|----------|----------|------|
| **Marketing** | Promotions, announcements, re-engagement, abandoned cart, product recommendations | Highest |
| **Utility** | Order confirmations, shipping updates, appointment reminders, payment receipts | ~80% cheaper than Marketing |
| **Authentication** | OTPs, verification codes, login links | Lowest |
| **Service** | Any reply within the 24-hour customer-initiated session window | **Free** |

### Sample Rates (approximate, 2026)

| Country | Marketing | Utility | Authentication |
|---------|-----------|---------|----------------|
| United States | $0.03–0.04 | ~$0.006 | ~$0.006 |
| India | $0.02 | $0.0025 | $0.0025 |
| Brazil | $0.10 | ~$0.02 | ~$0.01 |
| Germany | $0.22 | $0.10 | ~$0.05 |
| United Kingdom | $0.085 | ~$0.02 | ~$0.01 |

Rates vary significantly by country. Check Meta's current published rates for exact pricing. Volume discounts apply for utility and authentication messages above monthly thresholds (not available for marketing).

### Who Pays
- **Direct API access**: pay Meta at published rates; billed via credit card on file
- **Via BSP**: pay your BSP who bills Meta; BSPs typically add a markup
- Rates in your invoice reflect the country of the recipient's phone number, not your business location

---

## Free Messaging Windows

### 24-Hour Service Window
- Starts when a user sends you **any message**
- During this window: all messages you send are **free** (service category)
- You can send text, media, interactive messages — no template required
- Window resets with each new inbound message from that user
- After 24 hours: must use a template to re-engage (charges apply)

### 72-Hour Free Window (Click-to-WhatsApp)
- Triggered when a user clicks:
  - A **Click-to-WhatsApp** ad (Facebook or Instagram)
  - A **Facebook Page** CTA button that opens WhatsApp
  - An **Instagram profile** CTA that opens WhatsApp
- All message categories (including Marketing and Utility templates) are **free** for 72 hours from the click
- Best ROI entry point for marketing: ads drive users to WhatsApp, first 3 days are free
- After 72 hours: normal per-message pricing applies

---

## Messaging Tiers

Tiers control how many unique users you can send **business-initiated** messages to per 24-hour rolling window.

| Tier | Daily Limit | Default for |
|------|-------------|------------|
| Unverified / New | 250 unique users | New phone numbers |
| Tier 1 | 1,000 unique users | After initial usage |
| Tier 2 | 10,000 unique users | Auto-upgrade from Tier 1 |
| Tier 3 | 100,000 unique users | Auto-upgrade from Tier 2 |
| Tier 4 | Unlimited | Special approval |

**Key distinctions**:
- Tiers count **unique users per day**, not total messages
- Once a conversation is open, you can send unlimited messages within it without affecting tier limits
- Tier limits are **per phone number**, not per WABA
- Service messages (customer-initiated window) do not count against tier limits

---

## Tier Auto-Upgrade Conditions

To move from one tier to the next, you must **automatically** meet all three conditions:

1. **Volume**: send business-initiated messages to at least **50% of your current tier limit** within **7 consecutive days**
   - Tier 1 → Tier 2: send to ≥500 unique users/day for 7 days
   - Tier 2 → Tier 3: send to ≥5,000 unique users/day for 7 days
2. **Quality**: phone number quality rating must be **Medium (Yellow) or High (Green)**
3. **Business verification**: Meta Business Account must be verified

Upgrade happens automatically within **24–48 hours** of meeting criteria. No manual request needed.

**Downgrade**: if quality rating drops to Red and stays there for 7 days, tier can be **downgraded** to the previous tier. Quality recovery restores upgrade eligibility.

---

## Phone Number Quality Rating

Quality reflects user sentiment — blocks, reports, and negative feedback over a **rolling 7-day window**.

| Rating | Color | Meaning |
|--------|-------|---------|
| High | Green | Minimal blocks/reports; healthy |
| Medium | Yellow | Elevated blocks/reports; at risk |
| Low | Red | Excessive negative feedback; tier upgrades blocked |

**Consequences of Low (Red) rating**:
- Tier upgrades blocked
- After 7 days at Red: messaging limit may be **reduced** to the previous tier
- Continued low quality can result in further restrictions or WABA suspension

**How to protect quality**:
- Send only to users who explicitly opted in
- Keep marketing frequency low; don't blast daily
- Include opt-out mechanisms (Marketing Opt-Out button on templates)
- Personalize messages — generic blasts drive higher block rates
- Use utility category for transactional messages (users expect them; lower block rate)

**Monitor quality**: Business Manager → WhatsApp → Phone Numbers → quality column
Or subscribe to the `phone_number_quality_update` webhook field.

---

## Business Verification

Meta Business Verification unlocks higher trust and is required for tier upgrades beyond Tier 1 and for Official Business Account eligibility.

**Process**:
1. Go to Meta Business Manager → Business Settings → Security Center → Start Verification
2. Submit legal business name, business address, and supporting documentation (business registration, tax ID, utility bill, etc.)
3. Meta reviews in 1–5 business days
4. Once verified: a "Verified" badge appears on the Business Manager account

**Important**: Business Verification is separate from phone number OTP verification. You can have a verified phone number without a verified business.

---

## Official Business Account (Green Checkmark)

Displays a **green checkmark** next to the display name in WhatsApp for all users.

| Badge | Who Gets It | How |
|-------|------------|-----|
| Gray checkmark | Any approved display name | Automatic after Meta approves your display name |
| Green checkmark | Internationally recognized brands only | Must be manually approved by Meta |

**Gray checkmark** = Meta has confirmed the display name is associated with a real business. Most businesses get this automatically.

**Green checkmark (OBA)** requirements:
- Meta Business Account must be verified
- Brand must have significant, widespread public recognition (globally known brands)
- Apply via Meta Business Support (not self-service)
- Meta's decision is final; no guaranteed path for SMBs

**Practical note**: For most businesses, the gray checkmark is sufficient. It signals legitimacy to users. The green checkmark is realistically only for major global brands (airlines, banks, retailers, etc.).

---

## BSP vs. Direct Access — Cost Comparison

| Factor | Direct (Meta) | Via BSP |
|--------|--------------|---------|
| Setup complexity | Higher (self-serve Meta developer tools) | Lower (BSP handles setup) |
| Message cost | Meta's published rates | Meta rates + BSP markup (varies: $0.001–$0.005/msg extra) |
| Support | Meta documentation + community | BSP provides dedicated support |
| Tooling | Build your own dashboard/inbox | BSP provides UI, chatbot builder, analytics |
| Flexibility | Full control | BSP feature limitations may apply |
| Best for | Tech teams with engineering bandwidth | Businesses needing fast deployment or non-technical teams |

**Popular BSPs**: Twilio, 360dialog, Infobip, WATI, Vonage, Bird, Sinch, MessageBird, AiSensy, Zoko

**Recommendation**: if you have engineering resources, direct access gives full control and lower per-message cost. If you need speed to market, a BSP reduces setup time significantly.
