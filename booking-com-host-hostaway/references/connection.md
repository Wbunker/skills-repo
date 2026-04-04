# Booking.com Connection with Hostaway — Detailed Guide

## Prerequisites

1. Active Booking.com partner account at `partner.booking.com`
2. Property already live and reviewed on Booking.com
3. All rate plans in Booking.com Extranet set to **XML-enabled** (not read-only) — Hostaway cannot push rates/availability to read-only plans
4. Determine your payment model: Channel Collect or Property Collect (see `references/payments.md`)

---

## Step-by-Step Connection

1. **In Hostaway** → Channel Manager → Booking.com → Add Channel
2. Enter Booking.com Hotel ID and authorize the connection
3. Go to **Channel Manager → Listing Mapping**
4. Map each Hostaway listing to the corresponding Booking.com property/room type
   - Default markup is 100% (no markup) — adjust if you want channel-specific pricing
5. Verify rate plan mapping — each Hostaway rate plan should map to a corresponding XML-enabled plan in Booking.com
6. Trigger a **manual sync** and check the Booking.com Extranet to confirm rates and availability are current
7. Review reservation import — Hostaway imports ongoing and future reservations automatically; past check-ins are not imported

---

## XML Rate Plan Requirement (Critical)

Every rate plan that Hostaway manages must be **XML-enabled** in the Booking.com Extranet. Rate plans set to "read-only" cannot receive updates from Hostaway.

**To check/fix in Extranet:**
- Rates & Availability → Rate Plans → click each plan → ensure "XML" or "Channel Manager" is selected (not "Manual/Read-only")

Symptoms of read-only rate plans: rates not updating, availability stuck, sync appearing to work but Booking.com showing stale data.

---

## Room Mapping Best Practices

- Map one Hostaway listing to **one** Booking.com room type
- Mapping one room type to multiple Booking.com room types causes overbooking risk
- When you map or unmap a listing, Booking.com resets minimum stay settings to empty — reconfigure minimum stays after any remapping

---

## Switching or Reconnecting

If reconnecting after a gap or switching from manual management:
1. Audit all active rate plans in Extranet — set all to XML-enabled
2. Reconnect in Hostaway and remap listings
3. Trigger full manual sync
4. Cross-check Extranet and Hostaway calendars for discrepancies
5. Add any missing reservations as direct bookings in Hostaway to block the calendar

---

## Multiple Properties

Each Booking.com property ID maps independently to a Hostaway listing. Manage all under Channel Manager → Listing Mapping. Verify each mapping individually after connection.

---

## Sync Timing

- Changes take up to **5 minutes** to process and appear in Booking.com after a sync
- Real-time for reservations flowing in (Booking.com → Hostaway)
- Use Extranet as the source of truth to verify sync has applied
