# Troubleshooting Expedia + Hostaway

## Reservation Freeze

### What It Is
A **Reservation Freeze** occurs when an Expedia customer support agent modifies a reservation on the guest's behalf (cancel, shorten, extend) and the API does not notify Hostaway of the change. The reservation in Hostaway becomes out of sync with the actual status in Expedia.

**Common triggers**: Guest calls Hotels.com/Expedia support to cancel or change dates → agent makes the change in Expedia's system → Hostaway does not receive the status update.

### How to Resolve
1. In Hostaway → open the affected reservation
2. Go to **Guest Information** tab
3. Find the "Frozen reservation" toggle next to the Expedia channel name
4. Enable the **Frozen reservation** switch → Save
5. Manually edit the reservation in Hostaway to match the actual status in EPC
   - Update dates if shortened/extended
   - Cancel in Hostaway if the guest cancelled

This prevents Hostaway from overwriting your manual changes with stale API data.

### Prevention
- Monitor EPC regularly for reservation changes that may not have synced
- If you notice a discrepancy, freeze before editing

---

## Rate/Availability Sync Issues

| Symptom | Likely Cause | Fix |
|---|---|---|
| Rates not updating on Expedia | Child/derived rate plan active | Switch to standalone rate plan |
| Calendar not blocking after booking | Rate plan sync broken | Check rate plan type; trigger manual sync |
| Double booking | Initial connection didn't import all reservations | Add missing reservations as direct bookings |
| Old rates showing | Sync delay | Trigger manual sync from Hostaway |

**Manual sync**: In Hostaway, go to the listing → Channel Manager tab → Sync Now for Expedia.

To verify sync is working: Check EPC rates/availability after triggering a manual sync from Hostaway.

---

## Content Not Showing on Expedia

**Cause**: Hosts sometimes update photos/descriptions in Hostaway expecting them to push to Expedia. They do not — Expedia content is managed entirely in EPC.

**Fix**: Log in to EPC → update the listing content directly there.

---

## Channel Manager Option Not in EPC

**Symptom**: You can't find the "Channel Manager" option under Connectivity in EPC.

**Fix**: Contact Expedia partner support and ask them to enable Channel Manager access for your property. This is a known issue for some account types.

---

## Missing Reservations After Initial Connection

**Cause**: Expedia's API only exports reservations created within 30 days of the connection date for future check-ins, and not all of those are guaranteed.

**Fix**: 
1. Log in to EPC and review all upcoming reservations
2. Cross-reference with Hostaway
3. For any missing: create a **Direct Booking** in Hostaway with the correct dates to block the calendar

---

## Guest Messages Not Appearing in Hostaway

**Cause**: Messaging API not enabled or a known API issue.

**Fix**: 
- Verify Expedia Messaging API is enabled in Hostaway channel settings
- Check Hostaway support article: "Expedia: Guest Messaging"
- For VRBO messaging issues, see: "Common Messaging Issues with Vrbo on Hostaway"

---

## Automated Messages Failing

Hostaway automated messages (templates) may fail for Expedia/VRBO bookings if:
- Message contains disallowed content (contact info, external links before booking)
- Sent outside the allowed messaging window
- API connectivity issue

See Hostaway support: "What causes automated message failures in Hostaway"
