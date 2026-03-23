---
name: amazon-appstore-expert
description: "Amazon Appstore developer expert. Use this skill when the user asks about publishing apps to the Amazon Appstore, Amazon developer account registration, app submission workflow, Fire TV app development, Fire OS compatibility, Amazon In-App Purchasing (IAP), Amazon app review process, app monetization on Amazon, Fire tablet app development, Amazon device targeting, Amazon developer console, app rejection and appeals, Amazon content policies, or comparing Amazon Appstore to Google Play. Triggers on: Amazon Appstore, Amazon developer, Fire TV app, Fire OS, Fire tablet app, Amazon IAP, Amazon in-app purchase, Amazon app submission, Kindle app, publish to Amazon, Amazon app review, Amazon app rejection."
---

# Amazon Appstore Expert

A comprehensive guide for developers publishing apps to the Amazon Appstore across Fire tablets, Fire TV, and Echo Show devices.

## Quick Reference

| Topic | Reference File |
|-------|---------------|
| Account registration, developer console, support | [account-and-console.md](references/account-and-console.md) |
| App submission workflow, assets, metadata | [submission.md](references/submission.md) |
| App review process, rejections, appeals | [review-process.md](references/review-process.md) |
| Monetization, IAP SDK, revenue share, subscriptions | [monetization.md](references/monetization.md) |
| Fire OS, Fire TV, device compatibility, technical specs | [technical.md](references/technical.md) |
| Content policies, IP, privacy, prohibited content | [policies.md](references/policies.md) |

## Core Concepts

### Amazon Appstore at a Glance

- **Reach**: 250+ million devices across 236+ countries and territories
- **Revenue share**: 80/20 (developer keeps 80%) for developers earning under $1M/year via Small Business Accelerator; standard rate is 70/30
- **Platform**: Fire OS is Android-based (AOSP fork) — existing Android apps can be ported with modifications to replace Google services with Amazon equivalents
- **No Google Play Services**: Apps must use Amazon SDKs for billing, push messaging, maps, and auth

### Key Developer URLs

| Resource | URL |
|----------|-----|
| Developer Console | https://developer.amazon.com/home.html |
| Documentation hub | https://developer.amazon.com/docs/apps-and-games/documentation.html |
| Community forums | https://community.amazondeveloper.com/ |
| Submit a support case | https://developer.amazon.com/support/cases/new |
| Policy center | https://developer.amazon.com/docs/policy-center/understanding-content-policy.html |
| IAP overview | https://developer.amazon.com/docs/in-app-purchasing/iap-overview.html |
| Fire TV docs | https://developer.amazon.com/docs/fire-tv/get-started-with-fire-tv.html |

## Common Tasks

### Register a developer account
Go to https://developer.amazon.com, click Sign In, and use an existing Amazon.com account or create one. Then complete the developer profile. See [account-and-console.md](references/account-and-console.md).

### Submit a new app
Four-step flow in the Developer Console: Upload binary → Target devices → Add Appstore details → Review and Submit. See [submission.md](references/submission.md) for required assets, dimensions, and metadata limits.

### Implement in-app purchases
Use the Appstore SDK (preferred) or the Appstore Billing Compatibility SDK (for Google Play Billing migrations). Three item types: consumables, entitlements, subscriptions. See [monetization.md](references/monetization.md).

### Port an Android app to Fire OS
Replace Google services with Amazon equivalents (Play Billing → Appstore SDK, FCM → A3L Messaging, Google Sign-In → A3L Auth). See [technical.md](references/technical.md) for the full replacement table.

### Build for Fire TV
Fire TV requires D-pad navigation, 10-foot UI design (14sp minimum body text), a 1280×720px app icon, and a 1920×1080px background image. See [technical.md](references/technical.md) and [submission.md](references/submission.md).

