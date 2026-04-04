---
name: expedia-host-hostaway
description: >
  Expert guide for vacation rental hosts using Hostaway who want to connect, manage, and
  optimize their listings on Expedia Group channels. Use when a host asks about: connecting
  Expedia to Hostaway, setting up listings on Expedia or VRBO via Hostaway, syncing rates
  and availability, understanding Expedia commissions or fees, handling bookings and guest
  messages from Expedia, troubleshooting sync issues or reservation freeze, improving
  Expedia content score or listing visibility, or any question about Expedia Group channels
  (Expedia.com, Hotels.com, Orbitz, Travelocity, Hotwire) from the host's perspective
  within Hostaway.
---

# Expedia Group for Hosts via Hostaway

## What Expedia Group Covers

Connecting Expedia in Hostaway gives exposure across the Expedia Group marketplace: **Expedia.com, Hotels.com, Orbitz, Travelocity, Hotwire**, and 200+ affiliated booking sites globally. Expedia primarily targets hotel/travel-bundle guests; **VRBO is the vacation-rental-focused channel** within the same corporate group.

**Critical distinction:** Expedia and VRBO are separate integrations in Hostaway — they do not share a connection. If your properties are short-term vacation rentals, Expedia may redirect you toward VRBO during onboarding. See `references/vrbo.md` for VRBO-specific guidance.

---

## Connecting Expedia via Hostaway

### Prerequisites
- Active Hostaway account with listings already created
- Property registered in **Expedia Partner Central** (EPC) at `partner.expediagroup.com`
- Channel Manager option enabled in EPC (if missing, contact Expedia to enable it)

### Connection Steps
1. In **Expedia Partner Central** → Connectivity Settings → set Hostaway as your channel manager for both:
   - Receiving reservations
   - Updating rates and availability
2. In **Hostaway** → Channel Manager → Expedia → Connect
3. Map each Hostaway listing to its corresponding Expedia property ID

See `references/connection.md` for detailed step-by-step with gotchas.

### Key Limitations (read before connecting)
- **Listings cannot be exported from Hostaway to Expedia** — create and maintain all listing content (photos, descriptions, amenities, guest capacity) directly in EPC
- Only **standalone (parent) rate plans** sync — derived/child rate plans do not sync
- On initial connection, Expedia only exports reservations made within **30 days** of connection date; manually add any missing ones as direct bookings in Hostaway to block your calendar

---

## What Syncs via Hostaway

| Data | Syncs | Managed In |
|---|---|---|
| Rates | ✅ Yes | Hostaway |
| Availability / calendar | ✅ Yes | Hostaway |
| Reservations | ✅ Yes (real-time) | Hostaway inbox |
| Guest messages | ✅ Yes (Messaging API) | Hostaway unified inbox |
| Photos | ❌ No | Expedia Partner Central |
| Descriptions | ❌ No | Expedia Partner Central |
| Amenities | ❌ No | Expedia Partner Central |
| Max guests | ❌ No | Expedia Partner Central |

---

## Booking Flow

- Expedia is **instant book** — guests book without host pre-approval
- Host receives notification in Hostaway inbox and EPC
- **Payment**: Expedia collects from guest and transfers to host **1–2 days after check-in**
- Guest communication flows through Hostaway unified inbox (Messaging API enabled)
- Cancellations made by Expedia customer support agents can trigger a **Reservation Freeze** — see `references/troubleshooting.md`

---

## Commissions

| Channel | Fee Structure |
|---|---|
| Expedia.com | ~15–18% per booking (varies by location/property type; range 10–30%) |
| VRBO | 8% per booking (5% booking + 3% payment processing) OR $499–$699/yr + 3% processing |

No signup or subscription fees for Expedia.com. Monthly invoice for fees owed. If a guest cancels and you retain part of the payment, you're charged a fee on the amount kept.

---

## Reference Files

| File | Load when… |
|---|---|
| `references/connection.md` | Detailed connection setup, mapping, rate plan configuration |
| `references/listings.md` | Content requirements, photos, amenities, content score |
| `references/rates-bookings.md` | Rate sync, availability, booking handling, payments, cancellation policies |
| `references/vrbo.md` | VRBO-specific setup and differences from Expedia |
| `references/troubleshooting.md` | Reservation freeze, sync errors, common issues |
| `references/optimization.md` | Content score, search visibility, best practices |
