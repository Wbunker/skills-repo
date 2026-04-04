# Rates, Bookings, Payments & Cancellation Policies

## Rate Sync

- Rates set in **Hostaway** push to VRBO in real-time via API
- Minimum stay rules sync from Hostaway
- Additional fees (cleaning, pet, boat) sync from Hostaway — commission applies to these too
- Taxes configured in Hostaway sync to VRBO
- Dynamic pricing tools (PriceLabs, Wheelhouse, Beyond) integrated with Hostaway push rates to VRBO automatically

---

## Booking Types

Configure per listing in VRBO owner dashboard:

**Instant Book (recommended)**
- Guest books immediately, no host approval needed
- Stronger search ranking than request-to-book
- Reservation syncs to Hostaway immediately

**Request-to-Book**
- Host has 24 hours to accept or decline
- Declining requests negatively impacts acceptance rate and ranking
- Only use if property requires screening (large groups, events, etc.)

---

## Payment Flow (via Stripe)

VRBO does not collect payments. Flow:
1. Guest books → payment details captured by VRBO/Hostaway
2. Hostaway Auto-Payments charges guest via your **Stripe** account at the configured time
3. Stripe pays out to host per your Stripe payout schedule (typically 2 business days after charge)

**Stripe is required.** Set up before connecting VRBO. Enable Auto-Payments and Guest Invoicing in Hostaway for VRBO reservations.

---

## Commissions (Pay-Per-Booking)

As of August 28, 2025, all new hosts use pay-per-booking only:

| Fee | Rate | Applied To |
|---|---|---|
| Booking fee | 5% | Rental amount + additional fees (cleaning, pet, etc.) |
| Payment processing | 3% | Total payment including taxes and refundable deposits |
| **Total** | **8%** | |

**Guest service fee**: VRBO charges guests separately (6–15% of booking cost). This is on top of your nightly rate and does not affect host payout.

**Legacy subscription** ($499–$699/yr): Only available to hosts who already have an active subscription. Discontinued for new hosts.

---

## Cancellation Policies

Six options — select in VRBO owner dashboard per listing:

| Policy | Full Refund | Partial Refund (50%) | No Refund |
|---|---|---|---|
| **Relaxed** | Cancel 14+ days out | 7–14 days out | <7 days |
| **Moderate** | Cancel 30+ days out | <30 days | — |
| **Firm** | Cancel 60+ days out | 30–60 days out | <30 days |
| **Strict** | Cancel 60+ days out | — | <60 days |
| **No Refund** | — | — | Always |
| **Custom** | Host-defined | Host-defined | — |

VRBO recommends **Moderate** as the default balance of host protection and booking conversion.

**Seasonal policies**: VRBO allows custom cancellation policies for specific date ranges.

### Host-Initiated Cancellations
Cancelling on guests carries financial penalties and severely damages your ranking. Keep host-initiated cancellations at or below 1% to maintain/achieve Premier Host status.

### Extenuating Circumstances Policy (June 2024)
VRBO's Extenuating Circumstances Policy can override your selected policy and require full guest refunds. Hosts are responsible for the lost revenue in these cases. This policy activates for qualifying emergencies (natural disasters, etc.).

---

## Refund Handling in Hostaway

When processing a cancellation for a VRBO booking:
1. Cancel the reservation in VRBO owner dashboard (or Hostaway if supported)
2. Process the refund via Stripe in Hostaway — Hostaway reverses the charge per your policy
3. VRBO notifies the guest of the refund per the applicable policy

If Hostaway processed the original charge, the refund must also go through Hostaway/Stripe.
