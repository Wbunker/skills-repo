---
name: booking-com-host-hostaway
description: >
  Expert guide for vacation rental hosts using Hostaway who want to connect, manage, and
  optimize their listings on Booking.com. Use when a host asks about: connecting Booking.com
  to Hostaway, setting up or mapping listings, syncing rates/availability/content/reviews,
  understanding Booking.com's payment models (Channel Collect vs Property Collect), virtual
  credit cards (VCC), commissions and monthly invoices, cancellation policies, Genius program,
  Preferred Partner program, improving content score or search ranking, handling overbookings,
  troubleshooting extranet/channel manager sync issues, or any Booking.com question from the
  host's perspective within Hostaway.
---

# Booking.com for Hosts via Hostaway

## What Makes Booking.com Different

Booking.com is the largest OTA globally by volume, heavily weighted toward international and urban travelers. Key distinctions from Airbnb, VRBO, and Expedia:

- **All bookings are instant** — no request-to-book option; guests book automatically
- **Two payment models**: host chooses Channel Collect (Booking.com collects via VCC) or Property Collect (host collects directly)
- **Monthly billing for commissions** — one invoice per month, not per booking
- **Content syncs FROM Hostaway** — descriptions, amenities, policies all push via API (like VRBO, unlike Expedia)
- **Reviews sync two-way** — Hostaway can receive and respond to Booking.com reviews

---

## Connection Overview

### Prerequisites
- Booking.com partner account (register at `partner.booking.com`)
- All rate plans in Booking.com Extranet must be set to **XML-enabled** (not read-only) — critical for sync
- Property must be live on Booking.com before mapping in Hostaway

### Connection Steps
1. In Hostaway → Channel Manager → Booking.com → Connect
2. Authorize with Booking.com credentials
3. Map each Hostaway listing to its Booking.com property ID (Channel Manager → Listing Mapping)
4. Verify all rate plans are XML-enabled in the Booking.com Extranet
5. Trigger manual sync; verify rates/availability are live in Extranet

See `references/connection.md` for detailed steps, rate plan setup, and room mapping guidance.

---

## What Syncs via Hostaway

| Data | Syncs | Direction |
|---|---|---|
| Rates | ✅ Yes | Hostaway → Booking.com |
| Availability / calendar | ✅ Yes | Hostaway → Booking.com |
| Content (amenities, policies, descriptions) | ✅ Yes | Hostaway → Booking.com |
| Reservations | ✅ Yes (real-time) | Booking.com → Hostaway |
| Guest messages | ✅ Yes | Bidirectional (unified inbox) |
| Reviews | ✅ Yes | Bidirectional |
| Photos | ✅ Yes | Hostaway → Booking.com |

---

## Payment Models

Booking.com offers two models — choose per property in the Extranet:

**Channel Collect (Payments by Booking.com)**
Booking.com collects from the guest and issues the host a **Virtual Credit Card (VCC)** per booking. Host charges the VCC like a regular credit card to receive funds. VCCs must be charged within 12 months of checkout.

**Property Collect (Hotel Collect)**
Host collects payment directly from the guest at or before check-in. Booking.com only invoices the commission.

See `references/payments.md` for full VCC details, Auto-payments in Hostaway, and billing cycle.

---

## Commission

- **Standard rate**: 10–25% per booking; typically **~15%** for vacation rentals
- Applied to: nightly rate + additional fees (cleaning, pets, etc.) — **excluding taxes**
- **Monthly invoice**: issued 3rd–6th of each month for prior month's checkouts
- Brief review window (until 2nd or 5th) to adjust no-shows or pricing before invoice finalizes
- No signup fees; pay-per-booking model

Optional programs that increase commission in exchange for visibility — see `references/programs.md`.

---

## Booking Flow

- Guest books instantly on Booking.com or affiliated sites
- Reservation appears in Hostaway inbox in real-time
- Calendar blocks across all connected channels automatically
- Automated Hostaway messages fire per templates
- Payment collected per chosen model (VCC or direct)

---

## Reference Files

| File | Load when… |
|---|---|
| `references/connection.md` | Step-by-step setup, XML rate plan requirement, room mapping, listing import |
| `references/listings.md` | Content score, photo standards, amenities, description best practices |
| `references/payments.md` | Channel Collect vs Property Collect, VCC mechanics, Auto-payments, monthly billing |
| `references/rates-bookings.md` | Rate plan types, cancellation policies, minimum stay, markup settings |
| `references/programs.md` | Genius program, Preferred Partner, Preferred Plus — tradeoffs and eligibility |
| `references/troubleshooting.md` | Sync issues, overbookings, XML rate errors, extranet conflicts, messaging issues |
| `references/optimization.md` | Content score, ranking factors, review strategy, launch checklist |
