# Troubleshooting VRBO + Hostaway

## Messaging Issues

### 1. Messages Not Syncing (iCal Connection)
**Cause**: iCal connection does not support messaging — only calendar blocks sync.
**Fix**: Upgrade to API connection. All messaging requires API.

### 2. Expedia-Sourced VRBO Reservations: Messages Go to Email
**Cause**: Some reservations originate on Expedia.com but appear in VRBO. VRBO's API restriction means messages for these bookings are delivered by **email**, not the VRBO messaging inbox.
**Fix**: 
- Identify the reservation source in Hostaway
- Craft messages knowing they will arrive as email to the guest
- Ask guests to reply to email or provide alternative contact

### 3. Hyperlinks Not Clickable in Messages
**Cause**: VRBO's messaging API does not support hyperlinked URLs.
**Fix**: Guests must copy/paste links. For guest portals or rental agreements, send the plain URL in text form. To get specific links whitelisted, contact VRBO integrations team with real examples.

### 4. External Links Blocked in Automated Messages
**Cause**: VRBO blocks external URLs in automated messages sent for unconfirmed/quote-hold bookings.
**Fix**: Contact VRBO integrations team to whitelist your Hostaway-related links; provide examples of blocked links to expedite.

### 5. Automated Messages Not Firing
Common causes:
- Message template contains disallowed content (off-platform contact info, external links)
- iCal connection (automated messages only work via API)
- Message sent outside the allowed window

See Hostaway support: "What causes automated message failures in Hostaway"

---

## Sync Issues

### Rates/Availability Not Updating on VRBO
**Check**:
1. API connection is active (not iCal-only)
2. No conflicting iCal link still active — remove all iCal links once API is live
3. Trigger a **manual sync** from Hostaway → listing → Channel Manager tab → Sync Now

**iCal delay reminder**: If iCal is still attached, Hostaway syncs every 30 min, VRBO reads every 60 min — up to 90 min total lag.

### Content Not Updating on VRBO
**Cause**: Content sync requires API. On iCal, only calendar blocks sync.
**Fix**: Ensure API connection is active. After updating content in Hostaway, trigger manual sync.

### Double Booking After Switching from iCal to API
**Cause**: Old iCal links still active alongside API connection — causing double calendar sources.
**Fix**: Remove all iCal calendar links from both VRBO and Hostaway immediately after API connection is confirmed.

---

## Listing Not Showing / Inactive on VRBO

Common causes:
- Identity verification incomplete (government ID required since 2025)
- Stripe not connected — VRBO may suspend listing if payment setup is invalid
- Listing flagged by VRBO for policy violation or content issue
- API connection not fully established (export step incomplete)

**Check**:
1. VRBO owner dashboard for any alerts or action required
2. Hostaway Channel Manager → VRBO → connection status
3. Stripe connection in Hostaway settings

See Hostaway support: "Why are my Hostaway Listings Not Appearing or Inactive on Vrbo?"

---

## Payment Issues

### Guest Not Charged / Payment Not Received
**Cause**: Stripe not connected or Auto-Payments not configured.
**Fix**:
1. Verify Stripe is connected in Hostaway Settings → Payments
2. Verify Auto-Payments is enabled for VRBO in Hostaway
3. Verify Guest Invoicing is set up

### Stripe Charge Failed
- Check Stripe dashboard for failed charges
- Guest's card may have been declined — Hostaway will typically retry
- Contact guest through VRBO messaging to resolve payment

---

## Request-to-Book: Missed Acceptance Window
**Cause**: Host did not accept/decline within 24 hours.
**Impact**: Booking auto-declines; counts against acceptance rate; damages Premier Host eligibility.
**Prevention**: Enable Instant Book for all listings where possible. If Request-to-Book is required, set Hostaway notifications to ensure prompt action.
