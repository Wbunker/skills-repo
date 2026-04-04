---
name: vrbo-host-hostaway
description: >
  Expert guide for vacation rental hosts using Hostaway who want to connect, manage, and
  optimize their listings on VRBO. Use when a host asks about: connecting VRBO to Hostaway,
  iCal vs API integration, exporting listings from Hostaway to VRBO, setting up Stripe for
  VRBO payments, syncing rates/availability/content/messages, VRBO commissions or fee structure,
  handling VRBO bookings (instant book vs request-to-book), cancellation policies, Premier Host
  program requirements and benefits, troubleshooting sync or messaging issues, ranking higher
  on VRBO, or any VRBO-specific question from the host's perspective within Hostaway. Note:
  VRBO and Expedia are separate channels in Hostaway — use expedia-host-hostaway skill for
  Expedia.com questions.
---

# VRBO for Hosts via Hostaway

## VRBO vs. Expedia: Which Channel?

VRBO and Expedia.com are owned by the same parent company (Expedia Group) but are **completely separate integrations in Hostaway**. Connecting one does not connect the other.

| | VRBO | Expedia.com |
|---|---|---|
| Audience | Vacation rental guests (families, groups) | Hotel/bundle travelers |
| Content sync | ✅ Syncs FROM Hostaway via API | ❌ Must manage in Expedia Partner Central |
| Payments | Host collects via **Stripe** (connected to Hostaway) | Expedia collects, pays host 1–2 days post check-in |
| Commission | 8% per booking (5% + 3%) | 15–18% per booking |

---

## Critical Prerequisite: Stripe Setup

**Connect Stripe to Hostaway BEFORE connecting VRBO.** VRBO no longer processes payments — the host collects payment directly. Hostaway uses Stripe (or Braintree) to charge guests automatically via Auto-Payments.

If Stripe is not connected, you will not receive payment for VRBO reservations. Hostaway displays a banner warning on the VRBO configuration screen if Stripe is missing.

---

## iCal vs. API: Choose API

| | iCal | API (recommended) |
|---|---|---|
| Calendar sync | ✅ Yes (30–60 min delay) | ✅ Yes (real-time) |
| Rates sync | ❌ No | ✅ Yes |
| Content sync | ❌ No | ✅ Yes |
| Reservations | ✅ Yes (delayed) | ✅ Yes (real-time) |
| Guest messaging | ❌ No | ✅ Yes |
| Automated messages | ❌ No | ✅ Yes |

Use iCal only as a temporary bridge while API connection is being configured. Remove iCal links once API is live.

---

## Connection Overview

1. **Connect Stripe** to Hostaway (prerequisite)
2. Determine your account type: **PPM** (no existing channel manager) or **IPM** (switching from another CM)
3. In Hostaway → Channel Manager → VRBO → export listing to create the API connection
4. Map listings and configure rate plans

See `references/connection.md` for the full step-by-step with IPM/PPM flows.

---

## What Syncs via API

| Data | Syncs | Direction |
|---|---|---|
| Rates & pricing | ✅ Yes | Hostaway → VRBO |
| Availability / calendar | ✅ Yes | Hostaway → VRBO |
| Listing content (description, amenities) | ✅ Yes | Hostaway → VRBO |
| Photos | ✅ Yes | Hostaway → VRBO |
| Reservations | ✅ Yes | VRBO → Hostaway |
| Guest messages | ✅ Yes | Bidirectional (unified inbox) |
| Taxes & fees | ✅ Yes | Hostaway → VRBO |

---

## Booking Flow

- **Instant Book** (recommended) or **Request-to-Book** — configured per listing in VRBO
- Reservation appears in Hostaway unified inbox in real-time
- Guest is charged automatically via Stripe/Auto-Payments
- Host receives funds via Stripe payout schedule
- Guest messaging via Hostaway unified inbox

---

## Commissions

**Pay-per-booking (all new hosts as of Aug 28, 2025):**
- 5% booking fee (on rental amount + additional fees like cleaning, pet, boat)
- 3% payment processing fee (on total payment including taxes and refundable deposits)
- **Total: 8% per booking**

**Subscription model:** Discontinued for new hosts. Legacy hosts with active subscriptions can still renew ($499–$699/yr + 3% processing).

---

## Reference Files

| File | Load when… |
|---|---|
| `references/connection.md` | Step-by-step setup, IPM vs PPM, Stripe config, iCal-to-API migration |
| `references/listings.md` | Listing content, photo standards, amenities, what syncs from Hostaway |
| `references/rates-bookings.md` | Rate plans, availability, booking types, payments, cancellation policies |
| `references/premier-host.md` | Premier Host requirements, benefits, 2026 program changes |
| `references/troubleshooting.md` | Messaging issues, sync errors, listing not showing, common fixes |
| `references/optimization.md` | Ranking factors, instant book, calendar hygiene, review strategy |
