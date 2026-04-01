# Squarespace Commerce Reference

## Table of Contents
1. [Products](#products)
2. [Inventory](#inventory)
3. [Orders & Fulfillment](#orders--fulfillment)
4. [Payments](#payments)
5. [Shipping](#shipping)
6. [Taxes](#taxes)
7. [Discounts & Gift Cards](#discounts--gift-cards)
8. [Point of Sale](#point-of-sale)
9. [Commerce Marketing](#commerce-marketing)

---

## Products

**Product types:**
- **Physical** — tangible goods with optional shipping
- **Digital** — downloadable files (PDF, MP3, ZIP, etc.)
- **Service** — bookings and non-shippable offerings
- **Gift Card** — digital gift cards redeemable at checkout
- **Subscription** — recurring billing products
- **Custom merch** — via Printful print-on-demand integration

**Product management:**
- Add via Admin → Commerce → Inventory
- Variants: size, color, material — unlimited SKUs; multi-dimensional variants; per-variant images
- Drag-and-drop sorting in product list
- Product categories and subcategories (nested)
- Tags for filtering and organization
- Visibility scheduling (publish/hide by date)
- Related products: algorithmic cross-sell recommendations
- Customer reviews on product pages; import reviews from Etsy
- AI-generated product descriptions

**Product import:**
- Import via CSV from Shopify, Big Cartel, or Etsy

---

## Inventory

**Management:**
- Inventory dashboard: Admin → Commerce → Inventory
- Low stock alerts (configurable threshold)
- Track by variant
- Unlimited quantity option per SKU
- Mobile app for inventory updates

**Bulk operations:**
- CSV import/export for inventory levels
- API: adjust stock with `incrementOperations`, `decrementOperations`, `setFiniteOperations`, `setUnlimitedOperations`

---

## Orders & Fulfillment

**Order management:** Admin → Commerce → Orders
**Order statuses:** Pending → Fulfilled / Canceled

**Fulfillment actions:**
- Mark as fulfilled with or without tracking info
- Print packing slips
- Resend order confirmation emails
- Buy and print shipping labels (USPS, UPS) directly in Squarespace

**Order Status Page:** Customer-facing tracking page auto-generated per order

**Shipping carriers:**
- FedEx, USPS, UPS (carrier-calculated rates)
- Rate types: flat rate, weight-based, carrier-calculated
- Local pickup option (free, configurable)
- Estimated delivery date display

---

## Payments

**Supported processors:**

| Processor | Notes |
|---|---|
| Squarespace Payments | Built-in; US, UK, Canada, Ireland, France, Germany, Spain, Austria, Belgium, Finland |
| Stripe | Full integration |
| PayPal | Full integration |
| Apple Pay | Via Squarespace Payments or Stripe |
| Google Pay | Via Squarespace Payments only |
| Afterpay / Clearpay | Buy now, pay later |
| Klarna | Installments and financing |
| Link | Autofilled billing (Stripe) |
| ACH bank transfer | US only |
| Square | In-person POS only |

**Currencies:** 24+ currencies supported (ISO 4217)

**Note:** Cannot use the Commerce API to connect third-party payment processors — only Squarespace Payments, Square, Stripe, or PayPal are available.

**Transaction fees:**
- Commerce plans: 0% added transaction fees
- Lower Squarespace Payments rates on Plus and Advanced plans

**Squarespace Capital:** Fast financing for US/UK merchants based on sales history

---

## Shipping

**Setup:** Admin → Commerce → Shipping
**Options:**
- Flat rate (per order or per item)
- Weight-based rates
- Carrier-calculated rates (FedEx, USPS, UPS — requires carrier account)
- Free shipping (standalone or threshold-based)
- Local pickup

**Shipping profiles:** Assign different rates to product groups
**Shipping regions:** Define rates by country/region
**Estimated delivery:** Display delivery windows at checkout

---

## Taxes

**Setup:** Admin → Commerce → Taxes
**Options:**
- Automatic tax calculation (rates kept current by Squarespace)
- Manual tax rates by region
- VAT, HST, GST support
- Tax-inclusive vs. tax-exclusive pricing
- TaxJar integration for advanced compliance

**Accounting:** Xero integration via Admin → Commerce → Accounting

---

## Discounts & Gift Cards

**Discounts (Admin → Commerce → Discounts):**
- Percentage off, fixed amount off, free shipping
- Automatic discounts (no code needed) or coupon codes
- Conditions: minimum order, specific products/categories, customer groups
- Usage limits: per customer, total uses, date range
- Stacking rules

**Gift Cards:**
- Digital gift cards (sold as a product type)
- Online redemption at checkout
- No expiration by default
- Can be reloaded

---

## Point of Sale

**Requires:** iOS/Android Squarespace app + Square card reader (US only)
**Capabilities:**
- Accept in-person payments (credit/debit, contactless)
- Manage orders, customers, inventory from mobile
- Syncs with online store inventory

---

## Commerce Marketing

- Mailing list signup option at checkout (opt-in)
- Social sharing tools on product pages
- Sell on Instagram Shop and Facebook Shop (product catalog sync)
- Promotional banners and announcements (Admin → Marketing → Promotional Pop-Up)
- Pop-up overlays (sale announcements, email capture, discount offers)
- Donations: one-time and recurring (available as a product type)
