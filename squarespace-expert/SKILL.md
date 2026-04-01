---
name: squarespace-expert
description: >
  Expert guide for managing and building websites on Squarespace. Use when the user wants
  to build, edit, or manage a Squarespace site, configure commerce/store features, set up
  marketing (email campaigns, SEO, social), manage domains, or use the Squarespace Commerce
  API to programmatically manage products, orders, inventory, transactions, profiles, and
  webhooks. Also covers developer features like custom CSS, code injection, template
  development, and Acuity Scheduling integration.
---

# Squarespace Expert

Squarespace is an all-in-one platform covering site building, ecommerce, marketing,
scheduling, and a REST Commerce API. Navigate by topic — load the relevant reference file
when you need detail.

## Reference Files

| File | When to load |
|---|---|
| [references/site-building.md](references/site-building.md) | Pages, design, layout, navigation, SEO, domains, blogging, memberships |
| [references/commerce.md](references/commerce.md) | Products, inventory, orders, payments, shipping, taxes, discounts, gift cards |
| [references/marketing.md](references/marketing.md) | Email campaigns, social media, analytics, promotions, Acuity Scheduling |
| [references/api.md](references/api.md) | Commerce API — authentication, all endpoints, webhooks, rate limits, error handling |
| [references/developer.md](references/developer.md) | Custom CSS, code injection, template development, Git, JSON data, extensions |

## Quick Orientation

**Plan tiers** (affects API access and features):
- **Personal/Basic** — No API; core site building only
- **Core / Plus / Advanced** — API access for orders, forms, inventory, transactions
- **Commerce Basic / Advanced** — Full commerce + reduced transaction fees

**Two API generations co-exist:**
- `https://api.squarespace.com/v2/commerce/` — Products API (newer)
- `https://api.squarespace.com/1.0/` — Orders, Inventory, Transactions, Profiles, Webhooks

**Auth at a glance:**
- API Key: Admin → Settings → Developer Tools; `Authorization: Bearer <key>`
- OAuth 2.0: For multi-site apps; access tokens expire in 30 min; refresh tokens expire in 7 days (one-time use)

Load [references/api.md](references/api.md) for full endpoint reference and integration details.
