# LinkedIn API Reference

## Table of Contents
1. [Authentication (OAuth 2.0)](#authentication-oauth-20)
2. [API Structure & Versioning](#api-structure--versioning)
3. [API Products & Access Tiers](#api-products--access-tiers)
4. [Rate Limits](#rate-limits)
5. [What You Can Do](#what-you-can-do)
6. [What You Cannot Do](#what-you-cannot-do)
7. [Key Endpoints](#key-endpoints)
8. [Data Retention Rules](#data-retention-rules)
9. [Recent Changes (2025–2026)](#recent-changes-20252026)

---

## Authentication (OAuth 2.0)

LinkedIn uses OAuth 2.0 exclusively. No API key-only access.

### 3-Legged OAuth (member authorization)
Use when acting on behalf of a specific user.

1. Redirect user to: `https://www.linkedin.com/oauth/v2/authorization`
2. User grants consent → you receive an authorization code
3. Exchange code for access token at: `https://www.linkedin.com/oauth/v2/accessToken`
4. Access tokens expire after **60 days**
5. **No refresh tokens** — users must re-authenticate after expiration

### 2-Legged OAuth (application authorization)
Use for non-member-specific resources (company pages, marketing APIs).

### Key Scopes

| Scope | Access Level | Notes |
|---|---|---|
| `r_liteprofile` | Auto-approved | Basic profile (name, photo, headline) |
| `r_emailaddress` | Auto-approved | Email address |
| `w_member_social` | Partner required | Post on behalf of a user |
| `w_organization_social` | Partner required | Post on behalf of a company page |
| `rw_ads` | Partner required | Ad campaign management |
| `r_member_profileAnalytics` | Partner only | Follower/analytics data |
| `r_compliance` | Partner only | Member activity for archiving/compliance |

Scopes are requested in the OAuth URL dynamically. Your app's Products tab in the Developer Portal controls which scopes you can request.

---

## API Structure & Versioning

Built on LinkedIn's proprietary **Rest.li framework** (RESTful microservices). Both RESTful and GraphQL endpoints available. API v1 was retired December 2023 — v2 is current.

**Monthly versioned endpoints:** Format `YYYYMM` (e.g., `202603` = March 2026). Pass in header: `LinkedIn-Version: 202603`

- Guaranteed stability for at least 1 year per version
- Versions sunset on a rolling monthly basis
- Always target the latest version in new builds

---

## API Products & Access Tiers

Access is tiered — most useful products require Partner Program approval:

| Product | Access Level | Capability |
|---|---|---|
| Sign In with LinkedIn (OpenID Connect) | Self-serve | User authentication |
| Share on LinkedIn | Self-serve | Post text/images/video for users |
| Profile API | Partner | Read full member profile data |
| Community Management API | Partner | Create/manage posts, carousels, polls, comments, video for orgs |
| Company Admin API | Partner | Manage company pages |
| Marketing Developer Platform (MDP) | Vetted Partner | Full ad campaign management, targeting, analytics |
| Job Posting API | Partner | Post and manage job listings |
| Lead Sync API | Partner | Webhook sync for lead gen form submissions |
| Sales Navigator Application Platform (SNAP) | Partner | Embed Sales Navigator in external apps |
| Recruiter System Connect | Partner | ATS ↔ LinkedIn Recruiter integration |

**Self-Serve Program limits:** 100,000 daily API calls, max 100,000 lifetime users.
**Vetted Partner Programs:** Higher limits, stricter compliance monitoring.

**Developer Portal:** `developer.linkedin.com` — create an app, request Products, configure OAuth redirect URIs.

---

## Rate Limits

| Endpoint | Limit |
|---|---|
| Profile API | ~100 requests/day per app |
| UGC Posts API | ~50 posts/day |
| Company Admin API | ~500 requests/day |
| Ads API | ~100 requests/minute |

Limits are both **application-level** (total calls/24 hours) and **member-level** (calls per user).

**HTTP 429** = rate limit exceeded.

**Headers to monitor:**
- `X-Restli-Quota-Remaining` — live remaining quota
- `X-Restli-Quota-Reset` — when quota resets

Email alerts fire at 75% quota consumption.

---

## What You Can Do

- Authenticate users via Sign In with LinkedIn
- Read basic profile data (name, photo, headline, email)
- Create posts, carousels, polls, and videos on behalf of users or organizations (partner access required)
- Manage ad campaigns: create, update, target, and retrieve analytics
- Retrieve organic and sponsored post performance analytics
- Sync lead gen form submissions via webhooks
- Post and manage job listings
- Manage LinkedIn Events (create and update before event starts)
- Retrieve follower counts and post analytics for creators and company pages
- Integrate Sales Navigator into external CRM/sales tools (SNAP partners)
- Connect ATS to LinkedIn Recruiter (Recruiter System Connect partners)

**2025–2026 Community Management API additions:**
- Video thumbnails and captions
- Carousel posts
- Member video analytics (`GET /memberCreatorVideoAnalytics`)
- Member follower statistics
- Member post statistics

---

## What You Cannot Do

- Scrape, crawl, or spider LinkedIn content outside the API
- Sell, rent, lease, or sublicense member profile data or social activity data
- Use the API for lead generation, prospecting, or CRM enrichment without approved Partner status
- Combine LinkedIn data with unauthorized external data sources
- Automate posts without user consent and proper OAuth flow
- Create fake accounts or manage multiple clients from a single account
- Make employment, credit, insurance, or housing eligibility decisions using LinkedIn data

**GDPR note:** Violations can result in fines up to €20M or 4% of global revenue. LinkedIn data is subject to GDPR for EU members regardless of your location.

---

## Key Endpoints

```
# Authentication
POST https://www.linkedin.com/oauth/v2/accessToken

# User profile (lite)
GET https://api.linkedin.com/v2/userinfo

# Create a text post (UGC Posts)
POST https://api.linkedin.com/v2/ugcPosts

# Create an organization post
POST https://api.linkedin.com/rest/posts
Header: LinkedIn-Version: 202603

# Upload media (images/video)
POST https://api.linkedin.com/rest/images?action=initializeUpload
POST https://api.linkedin.com/rest/videos?action=initializeUpload

# Get organization follower count
GET https://api.linkedin.com/v2/networkSizes/{organizationUrn}

# Post analytics (member)
GET https://api.linkedin.com/rest/memberCreatorPostAnalytics

# Video analytics (member)
GET https://api.linkedin.com/rest/memberCreatorVideoAnalytics

# Ad campaigns
GET https://api.linkedin.com/rest/adCampaigns
POST https://api.linkedin.com/rest/adCampaigns

# Lead gen form responses (webhook-based as of July 2025)
POST https://api.linkedin.com/rest/leadWebhookSubmissions  # webhook endpoint
```

---

## Data Retention Rules

| Data Type | Maximum Retention |
|---|---|
| Profile data | 24 hours |
| Social activity data | 48 hours |
| Organization social activity | 6 weeks |
| Authenticated organization data | 6 months |

All user data must be deleted within **10 days** of API access suspension.

---

## Recent Changes (2025–2026)

| Date | Change |
|---|---|
| March 2026 | Company Intelligence API: added `paidQualifiedLeads` and `conversions` fields |
| March 2026 | Ads Targeting Facets API: added `buyerGroups` facet for B2B audience targeting |
| March 2026 | Lead Sync webhook validation now required |
| February 2026 | Videos API: added `templateName` and `linkbackContext` fields |
| February 2026 | Ads API: added `MAX_QUALIFIED_LEAD` optimization target |
| January 2026 | Ad Analytics API: added event and video watch time metrics |
| December 2025 | OAuth: added Google and Apple sign-in support |
| July 2025 | Legacy Lead Sync APIs (`/adForms`, `/adFormResponses`) sunset — replaced by webhook-based Lead Sync API |
| December 2023 | API v1 retired — v2 is current |

**Live audio events** are deprecated in the API (use video events instead).
