# Facebook Ads & Marketing

## Table of Contents
1. [Ads Manager Overview](#ads-manager-overview)
2. [Campaign Structure](#campaign-structure)
3. [Objectives](#objectives)
4. [Targeting & Audiences](#targeting--audiences)
5. [Ad Formats & Specs](#ad-formats--specs)
6. [Budgets & Bidding](#budgets--bidding)
7. [Pixels & Tracking](#pixels--tracking)
8. [Reporting & Optimization](#reporting--optimization)
9. [Facebook Marketing Strategy](#facebook-marketing-strategy)

---

## Ads Manager Overview

All Facebook/Instagram ad campaigns are managed at **adsmanager.facebook.com**.

**Prerequisites:**
- A Facebook Page (required to run most ad types)
- A verified payment method on the Ad Account
- Business Manager/Meta Business Suite account (recommended for teams)

---

## Campaign Structure

Meta Ads follow a 3-tier hierarchy:

```
Campaign (objective + budget type)
└── Ad Set (audience + placement + schedule + budget)
    └── Ad (creative: images, video, copy, CTA)
```

- **Campaign**: Sets the overall goal (objective) and optionally a Campaign Budget Optimization (CBO) budget
- **Ad Set**: Defines WHO sees the ad (audience), WHERE (placements), WHEN (schedule), and HOW MUCH (budget if not CBO)
- **Ad**: The actual creative users see — copy, visuals, headline, CTA button

---

## Objectives

Choose the objective that matches your business goal:

| Objective | Best for |
|---|---|
| **Awareness** | Brand reach, video views, store location awareness |
| **Traffic** | Drive clicks to website, app, Messenger, WhatsApp |
| **Engagement** | Post likes/comments, Page likes, event responses, video views |
| **Leads** | Instant forms, Messenger leads, website lead forms |
| **App Promotion** | App installs and in-app events |
| **Sales** | Website purchases, catalog sales, in-store sales |

**Advantage+ Shopping Campaigns (ASC):** Meta's AI-driven automated campaign type for eCommerce — combines prospecting and retargeting, minimal manual targeting needed. Often outperforms manual setups for established advertisers with conversion history.

---

## Targeting & Audiences

### Core Audiences (Manual Targeting)
- **Location**: Country, state, city, ZIP code, radius
- **Age**: 18–65+
- **Gender**: All, Men, Women
- **Detailed Targeting**: Interests, behaviors, demographics
  - Examples: "Small business owners," "Frequent international travelers," "Engaged shoppers"
- **Languages**

### Custom Audiences (Your Own Data)
Upload or connect your own customer data:
- **Customer List**: Upload CSV of emails/phones → Meta matches to accounts
- **Website**: People who visited your site (requires Pixel)
- **App Activity**: People who took actions in your app
- **Video**: People who watched a % of your video
- **Lead Form**: People who opened/completed your lead form
- **Instagram/Facebook**: Page engagers, followers, event responders

### Lookalike Audiences
- Create from any Custom Audience as a "seed"
- Choose size: 1% (most similar) to 10% (broadest) of a country's population
- 1% Lookalike of purchasers is typically highest-performing cold audience

### Advantage+ Audience
Meta's AI targeting — provide optional suggestions, Meta finds best audience automatically. Recommended for campaigns with sufficient conversion data (50+ conversions/week).

### Targeting Tips
- Avoid over-narrowing — let Meta's algorithm have room (audience size >500K generally)
- Detailed Targeting Expansion is on by default and usually helps
- For retargeting: 180-day website visitors, engaged IG/FB followers
- For prospecting: Lookalikes 1–3% or broad Advantage+ Audience

---

## Ad Formats & Specs

### Image Ad
- Ratio: 1:1 (square) or 4:5 (portrait) recommended
- Size: 1080×1080px (square), 1080×1350px (portrait)
- File type: JPG or PNG
- Text: Primary text (125 chars shown), Headline (27 chars), Description (27 chars)

### Video Ad
- Ratio: 4:5 (portrait) or 1:1 for feed; 9:16 for Stories/Reels
- Length: 1 sec – 241 min (feed); up to 60 sec for Stories
- Recommended: 15–30 sec for best completion rates
- Always design for sound-off (add captions)

### Carousel Ad
- 2–10 cards; each with its own image/video, headline, link
- Best for: showcasing multiple products, telling a sequential story
- Each card: 1080×1080px; headline 40 chars

### Collection Ad
- Cover image/video + 4 product images below
- Opens a full-screen Instant Experience on tap
- Best for: mobile shopping, product discovery

### Stories & Reels Ads
- Ratio: 9:16 (full screen vertical)
- Size: 1080×1920px
- Leave safe zones: top 14% and bottom 20% free of text/logos
- Up to 15 sec for Stories; up to 60 sec for Reels ads

### Lead Ad (Instant Form)
- Pre-fills user data (name, email, phone) from their Facebook profile
- Custom questions: multiple choice, short answer, appointment scheduling
- Lower friction than sending to website — higher volume but potentially lower quality leads
- Connect to CRM via Zapier, Webhooks, or native integrations

---

## Budgets & Bidding

### Budget Types
- **Daily Budget**: Spend up to X per day; Meta may spend ±25% on any given day
- **Lifetime Budget**: Total spend over the campaign's full run; Meta paces automatically

### Budget Level
- **Campaign Budget Optimization (CBO)**: Set budget at campaign level — Meta distributes across ad sets automatically
- **Ad Set Budget**: Control spend per ad set manually

### Bidding Strategies
| Strategy | Use case |
|---|---|
| **Highest Volume** (default) | Maximize results within budget |
| **Cost per Result Goal** | Target a specific average CPA |
| **Bid Cap** | Never bid above a set amount per auction |
| **ROAS Goal** | Target a minimum return on ad spend |

### General Budget Guidance
- Test phase: $5–$20/day per ad set for 7 days to gather data
- Scale winners: Increase budget 20% every 2–3 days to avoid reset
- For conversions: Aim for 50 conversions/week per ad set for algorithm stability

---

## Pixels & Tracking

### Meta Pixel
JavaScript code placed on your website to track visitor actions and match them to Facebook accounts.

**Key events to track:**
- `PageView` (on every page)
- `ViewContent` (product pages)
- `AddToCart`
- `InitiateCheckout`
- `Purchase` (with value parameter)
- `Lead`
- `CompleteRegistration`

**Install:** Events Manager → Data Sources → Add → Web → Install Pixel → Copy base code to `<head>`

### Conversions API (CAPI)
Server-side event tracking that supplements the Pixel — bypasses browser ad blockers and iOS privacy restrictions.

- Send events directly from your server to Meta's API
- Best practice: send the same events via both Pixel + CAPI with a unique `event_id` for deduplication
- Set up via: Events Manager → Data Sources → Settings → Set up Conversions API

### Event Manager
Centralized hub to manage Pixels, Conversions API datasets, and offline event sets.

**Conversion Count breakdown (2026 addition):** New breakdown in Ads Manager to analyze which conversion counting method (first-click, last-click) is attributing results.

---

## Reporting & Optimization

### Key Metrics
| Metric | Definition |
|---|---|
| **Reach** | Unique people who saw your ad |
| **Impressions** | Total times ad was shown |
| **Frequency** | Impressions ÷ Reach (aim for 1.5–3 for awareness, lower for conversions) |
| **CTR (Link)** | Link clicks ÷ Impressions |
| **CPC (Link)** | Cost per link click |
| **CPM** | Cost per 1,000 impressions |
| **ROAS** | Revenue ÷ Ad Spend |
| **CPA** | Cost per result/conversion |

### Optimization Tips
- Check results after 7 days minimum (Meta's learning phase)
- Pause ad sets with CPA >2× target after 50+ impressions
- Refresh creative every 4–6 weeks to combat ad fatigue (rising frequency + falling CTR)
- A/B test one variable at a time (audience OR creative OR placement)
- Use **Breakdown** → **Placement** to see which placements perform best

### Audiences Overlap Tool
Check if your ad sets target overlapping audiences — overlap causes self-competition and inflated CPMs.

---

## Facebook Marketing Strategy

### Content Mix (Organic)
- 70% value/educational content
- 20% community/engagement content
- 10% promotional content

### Content Format Priority (2026 reach)
1. Reels (highest reach, reaches non-followers)
2. Stories (time-sensitive, high engagement rate)
3. Video posts
4. Link posts
5. Image posts
6. Text-only posts (lowest reach)

### Posting Frequency
- Pages: 3–5x/week minimum
- Stories: 1–3 daily
- Reels: 3–5x/week for growth

### Organic + Paid Integration
- Boost top-performing organic posts as ads (fast and proven creative)
- Build Retargeting audiences from organic video viewers
- Use Page engagers as Custom Audience seeds for Lookalikes
- Run Lead Gen campaigns to build email list → remarket via Customer List Custom Audience
