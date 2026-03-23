# Amazon Appstore: Monetization

## Revenue Share

### Standard Rate
Amazon pays developers **70% of the List Price** for mobile/TV apps and Alexa Skills (standard 70/30 split).

### Small Business Accelerator Program
Developers earning **under $1 million USD annually** from Amazon Appstore receive:
- **80% revenue share** (up from 70%)
- **AWS credits equal to 10% of app revenue** on Amazon devices

The enhanced 80/20 rate applies to all revenue earned while under the $1M threshold. Once you exceed $1M in a calendar year, the standard 70% rate applies to additional revenue.

### Movies & TV In-App Products
80% of the List Price (same as Small Business Accelerator rate, but applies regardless of revenue level).

### PC Games & PC Software
The greater of: (i) 70% of Retail Price, or (ii) 20% of List Price.

### Revenue Share Reference
Full terms: https://developer.amazon.com/support/legal/da

---

## App Pricing Models

### Free Apps
- No upfront cost to users
- Can include IAP for additional content/features
- DRM is optional (no monetary risk if app is shared)

### Paid Apps
- Minimum price: $0.99 USD (€0.69, £0.59, AUD/CAD $0.99)
- Maximum price: $999.99 USD
- Prices set per marketplace
- DRM is recommended to prevent unauthorized sharing of paid apps

### Free Apps with In-App Purchasing
The most common model for games and productivity apps. IAP API handles content protection.

---

## In-App Purchasing (IAP)

### SDK Options

| SDK | Use Case |
|-----|----------|
| **Appstore SDK** | Preferred; full feature support; required for new implementations |
| **Appstore Billing Compatibility SDK** | For apps migrating from Google Play Billing Library; mirrors Google's API surface |

**Important**: All IAP items must be created and submitted in the Developer Console **before** app approval. Amazon will not test your app until both the app binary and IAP catalog items are submitted.

### Purchase Types

| Type | Description | Can Repurchase? |
|------|-------------|-----------------|
| **Consumable** | Limited-use goods (extra lives, in-game currency, power-ups) | Yes — can be purchased multiple times |
| **Entitlement** | Permanent one-time unlock (feature, content, ad removal) | No — permanent grant |
| **Subscription** | Time-limited access to premium content or features; auto-renews | Yes — renews automatically |

### SKU Requirements
- Unique identifier per item
- Up to 150 characters
- Allowed characters: letters, numbers, underscores, periods, dashes
- Must be configured in Developer Console before use

### Delivery Models

| Model | Description |
|-------|-------------|
| **Instantly available** | Content already in the app; unlocks upon purchase |
| **Deliverable content** | New content downloads from your server after purchase (common for subscriptions) |
| **Pending purchases** | Requires additional verification before granting access (consumables and entitlements only) |

---

## Subscriptions

### Standard Subscriptions
- Auto-renewing access for a defined period
- Available across all devices registered to the customer's Amazon account
- Free trial periods extend **beyond** the subscription term (e.g., 14-day trial + monthly subscription)
- Trials are one-time per product — cannot be repeated even if partially used
- Customers can disable auto-renewal but cannot cancel mid-period for pro-rated refunds

**Price change behavior:**
- Lowering price: affects both new and existing subscribers at next renewal
- Raising price: affects only new subscribers; existing subscribers keep old price until they change plans

**Auto-renewal**: The IAP API does not expose whether a specific user has auto-renewal enabled or disabled.

### Tiered Subscriptions
For select partners (requires Amazon representative to activate in Developer Console):
- Up to 5 distinct tiers per subscription product
- Each tier must have at least one term (pricing + duration combination)
- Customers can move between any tier freely (no hierarchy restrictions)
- Changes can be immediate or deferred to renewal
- Requires Appstore SDK version 3.0.7 or later

### Quick Subscribe
A streamlined subscription flow that reduces friction at sign-up:
- Overview: https://developer.amazon.com/docs/in-app-purchasing/quick-subscribe-overview.html
- Supports one-click account information sharing

---

## Receipt Verification Service (RVS)

Server-side transaction verification to prevent fraud:
- Validates that a purchase receipt is authentic
- Available in both sandbox (for testing) and production environments
- RVS Cloud Sandbox allows testing without real purchases

Documentation: https://developer.amazon.com/docs/in-app-purchasing/rvs-overview.html

---

## Real-Time Notifications (RTN)

Server-to-server notifications for subscription lifecycle events:
- Subscription renewals
- Cancellations
- Subscription status changes

Documentation: https://developer.amazon.com/docs/in-app-purchasing/real-time-notifications.html

---

## DRM (Digital Rights Management)

Amazon automatically wraps submitted apps with code that can enforce DRM.

| App Type | DRM Recommendation |
|----------|--------------------|
| Paid apps | Recommended — prevents unauthorized sharing of purchased apps |
| Free apps with IAP | Not needed — IAP API already protects purchased content |
| Free apps, no IAP | Optional — minimal risk |

**How DRM works:**
- When a user purchases a DRM-enabled app, the Appstore downloads a small entitlement token
- Token allows offline access; periodic internet connection required to refresh
- Prevents sharing of purchased app binaries

**Important limitation**: Amazon DRM is only available until a specified deprecation date for apps not using the Appstore SDK. After that date, apps requiring Amazon-managed DRM must integrate the Appstore SDK directly.

DRM documentation: https://developer.amazon.com/docs/in-app-purchasing/drm-overview.html

---

## Promotions

### Price Drop Campaigns
- Discount apps or IAP items (consumables and entitlements)
- Duration: 24 hours minimum, 27 consecutive days maximum
- Set percentage-based discounts globally or manually per marketplace
- Free to set up
- ROI analytics provided

### Retention Offer Campaigns
- Target subscribers considering cancellation
- Offer a temporary discount to retain subscription

Access: Developer Console → Promotions Console

Documentation: https://developer.amazon.com/docs/reports-promo/promo-overview.html

---

## Payment and Payouts

### Payment Schedule
- Mobile/TV apps: ~30 days after month-end
- PC Games/Software: ~45 days after month-end

### Minimum Payout Thresholds (USD)
- Direct Deposit/EFT: $0
- Wire Transfer: $100
- Check: $100

### VAT Treatment
List prices include VAT; taxes are excluded when calculating developer royalties.

---

## Testing IAP

**App Tester**: Local testing utility before publishing. Install on your Fire device to simulate purchases without real transactions.

**Live App Testing**: Invite real users to test in the production environment (including IAP flows).

IAP testing documentation: https://developer.amazon.com/docs/in-app-purchasing/iap-testing-overview.html
App Tester setup: https://developer.amazon.com/docs/in-app-purchasing/iap-install-and-configure-app-tester.html

---

## Migrating from Google Play Billing

Migration guide: https://developer.amazon.com/docs/in-app-purchasing/iap-migrate-from-google-iab-to-amazon-iap.html

The Appstore Billing Compatibility SDK mirrors the Google Play Billing Library API surface, reducing migration effort for existing Google Play apps.
