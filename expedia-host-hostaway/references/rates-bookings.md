# Rates, Availability, Bookings & Payments

## Rate Sync

- Rates set in **Hostaway** push to Expedia in real-time via API
- Only **standalone (parent) rate plans** sync — do not use derived/child/package rates
- Minimum stay rules sync from Hostaway to Expedia
- Channel-specific markups can be configured in Hostaway channel settings

### Rate Plan Warning
If you have derived rate plans active, the Expedia channel will not receive calendar or pricing updates. Switch to standalone rate plans before connecting.

---

## Availability Sync

- Calendar availability syncs in real-time (API connection, not iCal)
- iCal sync only pushes reservation blocks, not rates — avoid iCal if using Hostaway
- Blocks from other channels (Airbnb, Booking.com, etc.) propagate to Expedia instantly via Hostaway

---

## Booking Flow

1. Guest books on Expedia.com or affiliated site — **instant book, no host pre-approval**
2. Reservation appears in **Hostaway inbox** and **Expedia Partner Central**
3. Calendar auto-blocks across all connected channels
4. Automated messages trigger per Hostaway message templates

---

## Guest Communication

- Expedia Messaging API is enabled in Hostaway — messages go through the **unified inbox**
- Hosts should respond through Hostaway; messages sync back to Expedia
- Do not communicate outside the Expedia platform until after check-in (policy requirement)

---

## Payment

- Expedia **collects payment from the guest** directly
- Host receives payout **1–2 days after check-in**
- Monthly invoice from Expedia for commission owed on completed bookings
- No upfront fees; pay-per-booking model

---

## Cancellation Policies

### Guest-Initiated Cancellations
- Expedia offers a **24-hour free cancellation** window for guests on most properties
- After 24 hours, your policy applies (set in EPC)
- If you retain any portion of a cancelled booking, you're charged commission on the amount kept

### Host Cancellation
- Host-initiated cancellations carry penalties and damage your Guest Experience score
- Repeat cancellations risk delisting
- Expedia has a Partner-Initiated Cancellation Policy — penalties increase with frequency

### Available Cancellation Policy Types (set in EPC)
- Non-refundable
- Free cancellation up to X days before check-in
- Partial refund policies

**Tip**: Flexible cancellation policies improve search visibility per Expedia's own data.

---

## Pricing Strategy Tips

- Use Hostaway's dynamic pricing integrations (PriceLabs, Wheelhouse, Beyond) — rates push to Expedia automatically
- Competitive rates improve "Offer Strength" score and search ranking
- Expedia's **Accelerator** tool in EPC lets you temporarily increase your commission to boost search placement during soft periods
- **Rev+** (EPC tool) provides market rate benchmarking
