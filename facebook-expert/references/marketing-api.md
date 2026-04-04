# Facebook Marketing API

## Table of Contents
1. [Overview](#overview)
2. [Setup & Authentication](#setup--authentication)
3. [Campaign Management](#campaign-management)
4. [Ads Insights API](#ads-insights-api)
5. [Audience Management API](#audience-management-api)
6. [Creative Management](#creative-management)
7. [Catalog & Commerce API](#catalog--commerce-api)

---

## Overview

The Marketing API is a collection of Graph API endpoints for managing ads programmatically across Meta technologies (Facebook, Instagram, Audience Network, Messenger).

**Base URL:** `https://graph.facebook.com/v{version}/`
**Reference:** developers.facebook.com/docs/marketing-api
**Current version:** v22.0

**Common use cases:**
- Automate campaign creation and management at scale
- Pull performance reports into custom dashboards or BI tools
- Sync product catalogs automatically
- Build ad management tools and DSPs

---

## Setup & Authentication

### Required Permissions
- `ads_management` — create, edit, delete campaigns/ad sets/ads (write access)
- `ads_read` — read ad performance data (read-only)
- `business_management` — manage Business Manager assets

### Ad Account ID Format
Ad accounts use a special format: `act_{ad-account-id}`

Example: `act_123456789`

### Getting Your Ad Account
```bash
GET /me/adaccounts?fields=id,name,currency,account_status
```

### Required Access Levels
- **Standard Access**: Up to 25 ad accounts; default for new apps
- **Advanced Access**: Unlimited ad accounts; requires Meta Business Verification

---

## Campaign Management

### Campaign Hierarchy
```
Ad Account (act_{id})
└── Campaign
    └── Ad Set
        └── Ad
```

### Create a Campaign
```bash
POST /act_{ad-account-id}/campaigns
```
**Parameters:**
```json
{
  "name": "My Campaign",
  "objective": "OUTCOME_SALES",
  "status": "PAUSED",
  "special_ad_categories": []
}
```

**Objectives (v16+):**
- `OUTCOME_AWARENESS`
- `OUTCOME_TRAFFIC`
- `OUTCOME_ENGAGEMENT`
- `OUTCOME_LEADS`
- `OUTCOME_APP_PROMOTION`
- `OUTCOME_SALES`

### Create an Ad Set
```bash
POST /act_{ad-account-id}/adsets
```
**Key parameters:**
```json
{
  "name": "My Ad Set",
  "campaign_id": "{campaign-id}",
  "daily_budget": 1000,
  "billing_event": "IMPRESSIONS",
  "optimization_goal": "LINK_CLICKS",
  "bid_strategy": "LOWEST_COST_WITHOUT_CAP",
  "targeting": {
    "geo_locations": { "countries": ["US"] },
    "age_min": 25,
    "age_max": 54,
    "genders": [1, 2]
  },
  "status": "PAUSED",
  "start_time": "2026-04-10T00:00:00-0700"
}
```

**Targeting spec options:**
- `geo_locations.countries`, `.cities`, `.zips`, `.regions`
- `age_min`, `age_max`
- `genders` (1=male, 2=female)
- `interests` — array of `{id, name}` objects
- `behaviors` — array of `{id, name}` objects
- `custom_audiences` — array of `{id}` for Custom Audience IDs
- `lookalike_audience` — Lookalike Audience ID

### Create an Ad Creative
```bash
POST /act_{ad-account-id}/adcreatives
```
```json
{
  "name": "My Creative",
  "object_story_spec": {
    "page_id": "{page-id}",
    "link_data": {
      "message": "Check out our sale!",
      "link": "https://example.com",
      "image_hash": "{image-hash}",
      "call_to_action": {
        "type": "SHOP_NOW",
        "value": { "link": "https://example.com" }
      }
    }
  }
}
```

**Uploading an image:**
```bash
POST /act_{ad-account-id}/adimages
```
Upload file as multipart/form-data; response returns `hash` to use in ad creative.

### Create an Ad
```bash
POST /act_{ad-account-id}/ads
```
```json
{
  "name": "My Ad",
  "adset_id": "{adset-id}",
  "creative": { "creative_id": "{creative-id}" },
  "status": "PAUSED"
}
```

### Reading Campaigns
```bash
GET /act_{ad-account-id}/campaigns?fields=id,name,objective,status,daily_budget
GET /act_{ad-account-id}/adsets?fields=id,name,status,daily_budget,targeting
GET /act_{ad-account-id}/ads?fields=id,name,status,adset_id,creative{id,name}
```

### Updating Status
```bash
POST /{campaign-id}
  body: status=ACTIVE  (or PAUSED, DELETED, ARCHIVED)
```

---

## Ads Insights API

Retrieve performance metrics for campaigns, ad sets, and ads.

### Basic Insights Request
```bash
GET /{object-id}/insights?fields=impressions,clicks,spend,reach&date_preset=last_7d
```

**Object ID** can be: ad account, campaign, ad set, or ad ID.

### Key Fields
```
impressions, reach, frequency
clicks, unique_clicks, ctr
spend, cpm, cpc
actions, action_values          (conversions and revenue)
video_thruplay_watched_actions  (video completions)
cost_per_action_type            (CPA by action type)
roas (via action_values / spend)
```

### Date Options
```
date_preset: today | yesterday | last_7d | last_14d | last_30d | last_90d
             this_month | last_month | this_year
             
# OR custom range:
time_range: {"since":"2026-03-01","until":"2026-03-31"}
```

### Breakdowns
```bash
GET /{object-id}/insights?fields=impressions,spend&breakdowns=age,gender
GET /{object-id}/insights?fields=impressions,spend&breakdowns=publisher_platform
```

**Available breakdowns:** `age`, `gender`, `country`, `region`, `impression_device`, `publisher_platform`, `platform_position`, `device_platform`, `product_id`

**2026 change:** Meta limited some attribution window breakdowns in January 2026 — check the changelog for affected metrics.

### Level Parameter
Pull aggregated insights at different levels:
```bash
GET /act_{ad-account-id}/insights?level=campaign&fields=campaign_name,impressions,spend
GET /act_{ad-account-id}/insights?level=adset&fields=adset_name,impressions,ctr
GET /act_{ad-account-id}/insights?level=ad&fields=ad_name,clicks,cpc
```

### Async Insights (Large Reports)
For large date ranges or many objects, use async jobs:
```bash
# Create async job
POST /{object-id}/insights
  body: fields=impressions,spend&level=ad&date_preset=last_90d&is_async=true

# Response: {"report_run_id": "..."}

# Poll until complete
GET /{report-run-id}?fields=async_status,async_percent_completion

# Fetch results when async_status = "Job Complete"
GET /{report-run-id}/insights
```

---

## Audience Management API

### Create a Custom Audience
```bash
POST /act_{ad-account-id}/customaudiences
```
```json
{
  "name": "Website Visitors 180d",
  "subtype": "WEBSITE",
  "description": "All website visitors last 180 days",
  "pixel_id": "{pixel-id}",
  "rule": {
    "inclusions": {
      "operator": "or",
      "rules": [{
        "event_sources": [{"id": "{pixel-id}", "type": "pixel"}],
        "retention_seconds": 15552000,
        "filter": {
          "operator": "and",
          "filters": [{"field": "event", "operator": "=", "value": "PageView"}]
        }
      }]
    }
  }
}
```

### Upload Customer List
```bash
POST /act_{ad-account-id}/customaudiences
  body: name, subtype=CUSTOM, customer_file_source=USER_PROVIDED_ONLY

# Then add users:
POST /{audience-id}/users
  body: payload with hashed email/phone data
```
Emails and phones must be hashed with SHA-256 before sending.

### Create Lookalike Audience
```bash
POST /act_{ad-account-id}/customaudiences
```
```json
{
  "name": "1% Lookalike of Purchasers",
  "subtype": "LOOKALIKE",
  "origin_audience_id": "{custom-audience-id}",
  "lookalike_spec": {
    "type": "similarity",
    "ratio": 0.01,
    "country": "US"
  }
}
```

### List Audiences
```bash
GET /act_{ad-account-id}/customaudiences?fields=id,name,subtype,approximate_count
```

---

## Creative Management

### List Page Posts Available as Ads
```bash
GET /{page-id}/promotable_posts?fields=id,message,story,full_picture
```

### Use Existing Page Post as Ad Creative
```bash
POST /act_{ad-account-id}/adcreatives
```
```json
{
  "name": "Boosted Post Creative",
  "object_story_id": "{page-id}_{post-id}"
}
```

### Dynamic Creative (A/B Testing Multiple Assets)
```bash
POST /act_{ad-account-id}/adcreatives
```
```json
{
  "name": "Dynamic Creative",
  "asset_feed_spec": {
    "images": [{"hash": "img1_hash"}, {"hash": "img2_hash"}],
    "titles": [{"text": "Headline A"}, {"text": "Headline B"}],
    "bodies": [{"text": "Body copy A"}, {"text": "Body copy B"}],
    "call_to_action_types": ["SHOP_NOW"],
    "link_urls": [{"website_url": "https://example.com"}]
  }
}
```
Meta automatically tests combinations and serves the best-performing mix.

---

## Catalog & Commerce API

### Create a Catalog
```bash
POST /me/owned_product_catalogs
  body: name="My Product Catalog"
```

### Upload a Product Feed
```bash
POST /{catalog-id}/product_feeds
  body: name, schedule (recurring or one-time), url of CSV/XML feed
```

### Add a Single Product
```bash
POST /{catalog-id}/products
```
```json
{
  "retailer_id": "SKU123",
  "name": "Blue Widget",
  "description": "A great blue widget",
  "availability": "in stock",
  "condition": "new",
  "price": 999,
  "currency": "USD",
  "image_url": "https://example.com/widget.jpg",
  "url": "https://example.com/product/widget"
}
```

### List Products
```bash
GET /{catalog-id}/products?fields=id,name,price,availability
```

### Dynamic Ads
Use a catalog for product retargeting or broad audience campaigns:
- In Ad Set: set `promoted_object` to `{"product_catalog_id": "{id}"}`
- Use `product_catalog_sales` as campaign objective (maps to `OUTCOME_SALES`)
- Dynamic ads automatically show users products they've viewed on your website
