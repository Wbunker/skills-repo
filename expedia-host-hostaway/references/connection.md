# Expedia Connection with Hostaway — Detailed Guide

## Step-by-Step Setup

### 1. Prepare Your Expedia Partner Central Account
- Log in at `partner.expediagroup.com`
- Navigate to **Connectivity** → **Channel Manager** settings
- If "Channel Manager" option is not visible in EPC, contact Expedia support and request it be enabled for your properties
- Set **Hostaway** as the provider for:
  - Receiving reservations
  - Updating rates and availability

### 2. Connect in Hostaway
- Go to **Channel Manager** → **Expedia** → **Connect**
- Enter your Expedia Property ID(s)
- Authorize the connection

### 3. Map Listings
- Map each Hostaway listing to the corresponding Expedia property ID
- Verify the mapping is correct before going live

### 4. Configure Rate Plans
- Only **standalone (parent) rate plans** are supported
- Do NOT use derived/child (package) rates — they will not sync and can cause errors
- Set up rates in Hostaway; they will push to Expedia automatically

### 5. Handle Initial Reservation Import
- Expedia only exports reservations from the **30 days prior to connection** for future check-ins
- This import is not guaranteed for all properties
- Manually review EPC for any reservations not imported and add them as **direct bookings** in Hostaway to block the calendar and prevent overbookings

### 6. Verify Sync
- Perform a **manual sync** from Hostaway after setup to push current rates and availability to Expedia
- Check EPC to confirm rates and availability are displaying correctly

---

## Rate Plan Configuration

- Only standalone (non-derived) rate plans sync
- Minimum stay rules set in Hostaway sync to Expedia
- Rate markups: Configure any channel-specific markups in Hostaway's channel settings before connecting

---

## Connectivity Settings Reference

In EPC, under Connectivity:
- **Reservation delivery**: Hostaway
- **Rates/Availability update**: Hostaway
- Both must be set to Hostaway or sync will be incomplete

---

## Common Connection Mistakes

| Mistake | Fix |
|---|---|
| Child/derived rate plans active | Switch to standalone rate plans only |
| Channel Manager not visible in EPC | Contact Expedia to enable it |
| Missing reservations after connect | Add as direct bookings manually in Hostaway |
| Content not showing correctly | Update all content directly in EPC, not Hostaway |
