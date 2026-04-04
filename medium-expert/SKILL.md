---
name: medium-expert
description: >
  Expert guide for using Medium.com effectively as a writer, publisher, or developer.
  Use when someone asks about: writing and publishing on Medium, growing a Medium audience,
  the Medium Partner Program and how earnings work, getting Boosted, working with Medium
  publications (submitting, creating, editor/writer roles), the Boost Nomination Program,
  Medium's distribution algorithm, using Medium's official API (archived/limited) or the
  unofficial Medium API (mediumapi.com) to fetch articles/users/publications/tags programmatically,
  optimizing stories for monetization, understanding the Genius or referral features,
  cross-posting and canonical URLs, or any question about using Medium as a platform.
---

# Medium Expert

## What Medium Is

Medium is a subscription-based publishing platform (~1M+ paying members). Writers publish stories freely; monetization comes through the **Partner Program**, which pays based on how long paying members engage with your content.

Key platform concepts:
- **Stories** — individual articles; can be free or paywalled (members-only)
- **Publications** — curated collections run by editors; submitting to one expands your reach to its followers
- **Boost** — Medium's curation system that amplifies high-quality stories to a much wider audience
- **Tags** — primary discovery mechanism (max 5 per story)

---

## Quick Task Guide

| Task | Where to start |
|---|---|
| How Partner Program earnings work | `references/partner-program.md` |
| Getting Boosted | `references/boost-distribution.md` |
| Working with publications | `references/publications.md` |
| Writing & growth strategy | `references/optimization.md` |
| Official Medium API (posting programmatically) | `references/official-api.md` |
| Unofficial API (read data, research) | `references/unofficial-api.md` |

---

## API Landscape (Critical Context)

Two very different APIs exist for Medium:

**Official Medium API** (`api.medium.com/v1`)
- **Status: Archived. No longer supported.** No new OAuth2 integrations accepted.
- Still functional for: self-issued tokens, creating posts, listing publications
- Use for: programmatically publishing stories to your own account

**Unofficial Medium API** (`mediumapi.com` / RapidAPI)
- Third-party, actively maintained, 41 GET endpoints
- Use for: reading articles, researching users/publications/tags, content analysis
- Requires RapidAPI key; cannot write/publish

See `references/official-api.md` and `references/unofficial-api.md` for full details.

---

## Partner Program: How You Earn

Earnings come from **paying members** reading your stories. Three drivers (as of 2026):

1. **Member reading time** — primary signal; longer reads from members = more earnings
2. **Engagement** — claps, highlights, and replies from members boost earnings
3. **New member conversions** — one-time bonus when a non-member becomes a paying member after hitting your paywalled story (added Feb 2026)
4. **External traffic bonus** — 5% extra on reads from outside Medium (added Oct 2025)

Payout: monthly via Stripe, $10 minimum. Requires: $5/month Medium membership + at least 1 published story enrolled in Partner Program.

See `references/partner-program.md` for full earnings mechanics and strategy.

---

## Reference Files

| File | Load when… |
|---|---|
| `references/partner-program.md` | Earnings calculation, payout, membership conversion rewards, enrollment |
| `references/boost-distribution.md` | Boost criteria, how to get nominated, distribution tiers, algorithm |
| `references/publications.md` | Submitting stories, creating publications, editor/writer roles, Boost Nomination Program |
| `references/optimization.md` | Writing strategy, headline craft, tags, frequency, external traffic, growth |
| `references/official-api.md` | Official API endpoints, auth (self-issued tokens), post creation, known limitations |
| `references/unofficial-api.md` | All 41 unofficial API endpoints organized by category with parameters |
