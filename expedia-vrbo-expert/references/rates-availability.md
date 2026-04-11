# Rates & Availability

## Calendar Management

The **Rates & Availability** section (also **Calendar** tab) is where pricing and open dates are managed.

### Base Rate
A single nightly rate automatically applied to all future dates. Setting a base rate is required — it fills any dates without a specific override.

### Seasonal / Date-Range Overrides
Override the base rate for specific date ranges (holidays, peak season, shoulder season). Overrides take priority over the base rate.

### Booking Window
Configure:
- **How far ahead** guests can book (e.g., up to 12 months in advance)
- **How close to check-in** bookings remain open (e.g., must book at least 2 days out)

### Minimum Stay Requirements
Set minimum nights by date range. Example: 3-night minimum on summer weekends, 1-night minimum off-season.

---

## Standard Discounts

| Discount Type | Threshold | Notes |
|--------------|-----------|-------|
| Weekly | 7+ night stays | Applied automatically when booking qualifies |
| Monthly | 28+ night stays | Applied automatically when booking qualifies |

---

## Fees

All fees are shown to guests during checkout.

| Fee Type | Notes |
|----------|-------|
| Cleaning fee | Flat fee per booking |
| Pet fee | Per stay or per night |
| Extra guest charges | Triggered above a guest count threshold |
| Custom fees | Any other fee (early check-in, etc.) |

### Damage / Security Deposit
Set a deposit amount visible to guests in house rules and at checkout. Not charged automatically — managed manually or via the platform's damage protection process.

### Tax Automation
Integrate with **Avalara MyLodge Tax** within Partner Central to automate lodging tax calculation and filing.

---

## Payment Terms

Choose either:
- **Full payment at booking** — guest pays 100% upfront
- **Deposit model** — partial amount due at booking, balance due closer to check-in

Configure the deposit amount and balance-due timing in payment settings.

---

## Rate Plans (3-Tier Hierarchy)

```
Property
  └── Room Type  (e.g., "Lakefront Cabin," "Standard Cabin")
        └── Rate Plan  (e.g., "Refundable," "Non-Refundable," "Member Rate")
```

Each **Room Type** can have multiple Rate Plans simultaneously. Each Rate Plan defines:
- Name and internal code
- Cancellation/change policy
- Base compensation (commission rate)
- Additional guest fees
- Refundability setting

### Common Rate Plan Combinations

| Plan | Typical Discount | Use Case |
|------|-----------------|----------|
| Refundable (standard) | None | Default offering |
| Non-Refundable | 10–15% off | Last-minute inventory or slow periods |
| Members Only | 15–20% off | One Key loyalty member targeting |
| Package (bundled) | Varies | Flight+cabin bundles; longer stays |

---

## Bulk Inventory Update Tool

For updating rates or availability across multiple dates or multiple units at once. Accessible from the Rates & Availability section. Use this instead of making individual date edits when applying seasonal rate changes across the entire cabin inventory.
