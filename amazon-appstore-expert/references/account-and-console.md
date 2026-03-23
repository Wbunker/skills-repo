# Amazon Appstore: Account Registration & Developer Console

## Developer Account Registration

### How to Register

1. Go to https://developer.amazon.com
2. Click **Sign In** — you can use an existing Amazon.com account or create a new one
3. Amazon sends a One-Time Password (OTP) to your email for verification
4. Complete your developer profile with legal name, address, and business information

Registration URL: https://developer.amazon.com/apps-and-games

### Account Types

| Type | Use Case |
|------|----------|
| **Sole Proprietorship** | Individual developers, students, hobbyists managing apps independently |
| **Business Account** | Companies, nonprofits, partnerships, government organizations |

For a Business Account, you must provide:
- Legal business name exactly as it appears on your Business Registration document or equivalent government-authorized document
- Company website
- Legal business name (cannot be edited after submission)

### Required Information at Registration

- Full legal name (matching government-issued ID)
- Primary email address
- Country of residence
- Mailing address (used for verification, tax reporting, and royalty payments)
- Customer-facing business name (permanent — cannot be changed after initial submission)
- For business accounts: company website and legal business name

### Costs and Fees

There is **no registration fee** to create an Amazon developer account. Publishing apps to the Amazon Appstore is free. Amazon's revenue comes from the revenue share on paid apps and IAP transactions.

### Tax Information

You will need to provide tax information (W-9 for US developers, W-8BEN or W-8BEN-E for international developers) before receiving royalty payments.

---

## Account Permissions and Team Roles

Administrators can assign the following roles to team members:

| Role | Permissions |
|------|-------------|
| **Administrator** | Complete access to all account sections |
| **Developer** | Can submit and modify application files |
| **Marketer** | Can edit app content and access sales reports |
| **Analyst** | Access to sales reports only |
| **Tester** | Can access testing tools but cannot submit apps |

Manage roles at: Developer Console → Account Settings → User Permissions

---

## Two-Step Verification

Amazon requires Two-Step Verification (2SV) for developer accounts. FAQ: https://developer.amazon.com/docs/app-submission/faq-landing.html

---

## Developer Console Overview

Access the console at: https://developer.amazon.com/home.html

### Main Sections

- **My Apps** — Create new app listings, manage existing submissions, view app status
- **Reports** — Financial and performance analytics (see Analytics section below)
- **Promotions Console** — Set up price drop and retention offer campaigns
- **Account Settings** — Manage profile, payment info, tax information, team permissions
- **Support** — Submit and track support cases

### App Status States

| Status | Meaning |
|--------|---------|
| **Submitted** | App can no longer be edited; you may still cancel the review request |
| **Under Review** | Amazon is actively examining the app; cancellation still possible |
| **Pending** | Amazon has paused review and sent an email requesting action on specific issues |
| **Approved** | App passed testing; awaiting publication scheduling |
| **Live** | App is available in the Appstore |
| **Rejected** | App failed review; Amazon provides detailed failure reasons via email |

---

## Analytics and Reporting

Access via: Developer Console → My Reports → Overview

### Financial Reports

**Unit Sales Reports**
- Total units sold with estimated earnings
- Filterable by year, month, app, and marketplace
- Includes IAP and subscription metrics

**Earnings & Payments Reports**
- Approved earnings and actual payment disbursements
- Monthly reporting periods

### App Performance Reports

| Report Type | What It Tracks |
|-------------|----------------|
| **Acquisition Reports** | App discovery and installation patterns |
| **Engagement Reports** | User interaction and activity levels |
| **Monetization Reports** | Revenue, subscriptions, retention analytics |

### Additional Analytics Tools

**App Health Insights Dashboard**
- Crash rates and ANR (Application Not Responding) statistics
- Performance metrics across app versions

**User Reviews Analytics**
- Rating analysis and content trends
- Key performance indicators
- CSV export capability

**Download Center**
- CSV downloads for sales, earnings, payments, subscription, and feature reporting data

**Reporting API**
- Programmatic access to reporting data for integrated analytics solutions

### Payment Schedule

| App Type | Payment Timing |
|----------|---------------|
| Mobile/TV apps and Alexa Skills | ~30 days after month-end |
| PC Games and PC Software | ~45 days after month-end |

### Payment Methods and Thresholds

| Method | Minimum Balance (USD) |
|--------|----------------------|
| Direct Deposit / EFT | $0 |
| Wire Transfer | $100 |
| Check | $100 |

Payment currency depends on the developer's bank location.

---

## Developer Support

### Support Channels

| Channel | Description |
|---------|-------------|
| **DevAssistant** | AI-powered chatbot for instant documentation and troubleshooting access |
| **Documentation** | https://developer.amazon.com/docs/apps-and-games/documentation.html |
| **Community Forums** | https://community.amazondeveloper.com/ — organized by topic area |
| **Submit a Case** | https://developer.amazon.com/support/cases/new — for personalized support |
| **My Cases** | https://developer.amazon.com/support/cases — track existing requests |

### Support SLAs (from Developer Services Agreement)

Developers publishing on the Appstore are themselves required to provide support:
- **Critical issues**: Response within 24 hours
- **Standard requests**: Response within 5 business days

Amazon does not publicly document SLAs for its own developer support response times. For app review questions, if your app is still in review after **6 days**, you can use the Contact Us form to seek clarification.

### Community Structure

The developer community at community.amazondeveloper.com is organized into:
- Fire Devices & Appstore (development, announcements, Q&A)
- Vega Open Beta (new OS feedback)
- Amazon Music APIs
- Ring Developer Portal

---

## Promotions Console

Access: Developer Console → Promotions Console

### Available Promotion Types

**Price Drop Campaigns**
- Create discounts for apps and in-app items (consumables and entitlements)
- Minimum duration: 24 hours
- Maximum duration: 27 consecutive days
- Set percentage-based discounts or manually adjust prices per marketplace
- Can cover multiple apps or IAP items per campaign

**Retention Offer Campaigns**
- Specifically for in-app subscriptions
- Designed to retain customers who are considering cancellation
- Offers subscription discounts at the renewal decision point

### Campaign Features
- Free to set up (no cost beyond the discount itself)
- Global marketplace support with per-marketplace price control
- Performance analytics showing ROI per campaign
