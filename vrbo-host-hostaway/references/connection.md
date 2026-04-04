# VRBO Connection with Hostaway — Detailed Guide

## Step 0: Connect Stripe First (Required)

VRBO no longer collects payments on behalf of hosts. You must connect a **Stripe** account (or Braintree) to Hostaway before connecting VRBO. Without it, VRBO bookings will not result in payment.

In Hostaway: **Settings → Payments → Stripe → Connect**

Hostaway will show a banner warning on the VRBO setup screen if Stripe is not connected.

Also ensure **Guest Invoicing** and **Auto-Payments** are configured in Hostaway so guests are charged automatically on VRBO reservations.

---

## Account Type: PPM vs IPM

Before connecting, determine your VRBO account type:

| Type | Description | Setup Flow |
|---|---|---|
| **PPM** (Property Partner Model) | VRBO account not currently connected to any channel manager | Standard export flow from Hostaway |
| **IPM** (Integration Partner Model) | Previously connected to another channel manager | Must disconnect old CM from VRBO first, then connect Hostaway |

If switching from another CM (IPM): contact VRBO support to confirm the old connection is fully removed before proceeding.

---

## Step-by-Step: API Connection (New VRBO Account / PPM)

1. **In Hostaway** → Channel Manager → VRBO → Add Channel
2. Enter your VRBO credentials / authorize Hostaway access
3. **Export your listing** from Hostaway to VRBO — this creates the API connection
   - Hostaway pushes listing content, amenities, photos, rates, and availability to VRBO
4. Confirm the VRBO property ID is mapped to the correct Hostaway listing
5. Configure rate plans (see below)
6. Enable **Auto-Payments** in Hostaway for VRBO reservations
7. Do a test manual sync to verify rates and availability are live on VRBO

---

## iCal as a Temporary Bridge

If you need VRBO live while the API connection is being set up:
1. In VRBO → get your iCal export URL
2. In Hostaway → add as iCal import for that listing
3. In Hostaway → get your iCal export URL
4. In VRBO → add Hostaway iCal as external calendar

**Remove iCal links once the API connection is established.** Running both simultaneously causes sync conflicts and double-blocking.

iCal sync delay: Hostaway imports every 30 minutes; VRBO updates every 60 minutes. Not suitable for production long-term.

---

## Migrating from iCal to API (Vrbo iCal → API)

1. Ensure Stripe is connected in Hostaway
2. Connect VRBO via API in Hostaway Channel Manager
3. Export listing to create API link
4. Remove old iCal calendar links from both VRBO and Hostaway
5. Verify sync is working via manual push

---

## Multiple VRBO Accounts

Hostaway supports connecting multiple VRBO accounts. Each must be connected separately under Channel Manager. Manage per-listing mapping individually.

---

## Rate Plan Configuration

- All standard rate plans sync from Hostaway to VRBO
- Minimum stay rules sync automatically
- Additional fees (cleaning fee, pet fee) sync from Hostaway
- Taxes configured in Hostaway sync to VRBO

---

## Verifying Connection Health

- Trigger a **manual sync** from Hostaway after setup
- Check the VRBO listing to confirm rates, availability, and content are current
- Create a test reservation (or have a trusted person do so) to verify Auto-Payments fire correctly
