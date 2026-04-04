# Troubleshooting Booking.com + Hostaway

## Rates/Availability Not Updating in Booking.com

**Most common cause: Rate plans set to read-only in Extranet.**

Fix:
1. Log into Booking.com Extranet → Rates & Availability → Rate Plans
2. Click each rate plan → confirm it is set to XML / Channel Manager enabled (not Manual/Read-only)
3. Trigger manual sync from Hostaway
4. Wait up to 5 minutes and verify in Extranet

If rate plans are correct but sync still fails, check the connection status in Hostaway Channel Manager → Booking.com.

---

## Overbooking

**Causes:**
- One Hostaway listing mapped to multiple Booking.com room types
- Auto-replenishment on closed rooms: a cancellation reopened availability and a new guest booked
- Sync delay during a system outage
- Non-XML (read-only) rate plans receiving manual bookings outside the channel manager

**Fix:**
- Audit room mapping: 1 Hostaway listing → 1 Booking.com room type only
- If auto-replenishment caused the overbooking — this is expected behavior; the feature re-opened a cancelled unit
- To disable auto-replenishment: Extranet → Rates & Availability → toggle off auto-replenishment
- After resolving, trigger manual sync and block the calendar immediately

**For repeated overbookings:** Contact Booking.com partner support to audit your channel manager connection.

---

## Minimum Stay Reset After Remapping

**Cause:** Booking.com resets minimum stay to empty whenever a listing is mapped or unmapped in Hostaway.

**Fix:** After any mapping change, immediately go to Booking.com Extranet → Rates & Availability → Minimum Stay and reconfigure all minimum stay rules.

---

## Extranet and Hostaway Out of Sync

Extranet always reflects the live state of your Booking.com listing. If Hostaway and Extranet show different data:
1. Trigger a manual sync from Hostaway
2. Wait 5 minutes and recheck Extranet
3. If still mismatched: check for read-only rate plans, connection health in Hostaway
4. Check Hostaway's channel manager logs for sync errors

---

## VCC (Virtual Credit Card) Issues

**VCC not visible in Hostaway:**
- Check the reservation's payment section for "Paid online" status
- Confirm VCC Payments Clarity Package is enabled in your Booking.com account

**VCC charge failing:**
- Verify the activation date — VCCs cannot be charged before activation
- Verify the VCC hasn't expired or been voided
- Ensure card details (number, expiry, CVC) are entered correctly

**VCC expired / missed 12-month window:**
- Booking.com will not reissue the VCC
- Contact Booking.com partner finance support — recovery is not guaranteed

---

## Guest Messages Not Syncing

- Messages for Booking.com reservations should flow through Hostaway unified inbox via Messaging API
- If messages are missing: check Booking.com Messaging API is enabled in Hostaway channel settings
- Automated messages that contain external links or off-platform contact info may be blocked by Booking.com

---

## Listing Not Live / Under Review

Booking.com reviews all new listings before going live. If a listing is stuck in review:
1. Verify all required fields are complete in Extranet (address, rates, policies, at least one photo)
2. Confirm property type is accepted
3. Contact Booking.com partner support if review exceeds 3–5 business days

---

## Commission Invoice Discrepancies

If an invoice seems incorrect:
- Use the review window (until 2nd or 5th of month) to mark no-shows or correct pricing errors
- After the window closes, disputes must be filed through Booking.com Extranet → Finance → Invoice disputes
