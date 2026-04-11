# Expedia Partner Central (EPC) — Extranet Deep Reference

The EPC extranet lives at **apps.expediapartnercentral.com**. It is distinct from the Vrbo host dashboard and is the hotel-style interface used for lodging properties (including cabins and campgrounds listed as lodging rather than private residences). All changes here propagate across the Expedia Group marketplace: Expedia.com, Hotels.com, Orbitz, Travelocity, Ebookers, and others.

---

## 1. Dashboard Layout & Navigation

### Login
- URL: **www.expediapartnercentral.com** (redirects to apps.expediapartnercentral.com after login)
- Credentials: same email/password as the Expedia partner account
- Multi-property operators land on the **Multi Property Home Page** first, then select an individual property

### Home Screen (Dashboard)
The dashboard shows an at-a-glance overview:
- Upcoming arrivals and departures
- Current occupancy summary
- Recent booking activity
- Notifications (rate alerts, content score updates, messages)
- Quick-access tiles to core sections

### Primary Navigation (Left Sidebar)
EPC uses a **left-side navigation menu**. Main sections:

| Section | What It Contains |
|---------|-----------------|
| **Property** | Property Details, Policies, Amenities, Photos, Content Score |
| **Rooms and Rates** | Room Types and Rate Plans, Rates and Availability, Bulk Update |
| **Reservations** | Booking list, reservation detail, cancellation, virtual card |
| **Finance** (or Billing) | Invoices, payment requests, billing history |
| **Marketing** | Accelerator, Promotions/Campaigns, TravelAds link |
| **Reports** | Performance analytics, Rev+, Property Analytics |
| **Messages** | Guest inbox, templates, scheduled messages |
| **Help and Support** | Documentation, contact Expedia support |

Within each top-level section, submenus expand below it in the left sidebar.

---

## 2. Rooms & Rates Management

### Navigation Path
**Rooms and Rates** (left nav) → **Rooms, Rates, and Policies** (submenu)

### Room Types — Adding
1. Click **"Rooms and Rates"** in the left nav
2. Click **"Room types and rate plans"** in the submenu
3. Click the **"Add a room"** dropdown → select **"Create new"** (or "Copy existing" to duplicate an existing room type)
4. Fill in the room configuration form:
   - Room name and internal room code
   - Smoking policy
   - Bed types (king, queen, bunk, etc.)
   - Total max occupancy
   - Room amenities
   - Bathroom configuration
   - Parking policies
5. Click **"Create room type"** to save

### Room Types — Editing
1. Navigate to **Rooms, Rates, and Policies**
2. Find the room in the Active Rooms list
3. Click **"Edit"** link on the room row
4. Modify fields as needed
5. Click **"Save"**

### Deactivating a Room Type
Use the deactivation option on the room type row. Deactivated rooms no longer appear to guests.

### Rate Plan Types
Each room type can have multiple rate plans simultaneously. Rate plan types in EPC:

| Rate Plan | Notes |
|-----------|-------|
| **Standard (Refundable)** | Default offering; receives "Free Cancellation" / "Fully Refundable" badge in search |
| **Non-Refundable** | Typically 10–15% discount; guest forfeits full amount on cancellation |
| **Members Only Rate** | Exclusive to One Key loyalty members (Blue, Silver, Gold, Platinum tiers) |
| **Package Rate** | Bundled with flights and/or car rental |
| **Early Booking Rate** | Discount for advance reservations |
| **Last-Minute Rate** | Discount for bookings close to check-in |

Each rate plan defines: name, cancellation/refund policy, commission rate, additional guest fees, and refundability setting.

### Auto Rate Match (ARM)
EPC includes an **Auto Rate Match** feature that monitors competitor sites (Agoda, Booking.com) and automatically adjusts rates to maintain parity. Can be turned on or off per rate plan. Partners using ARM see ~15% more net room nights.

### Pricing Models Available
- **Per-night rate** — flat nightly rate, most common
- **Length-of-stay pricing** — different rates by stay length
- **Occupancy-based pricing** — rates vary by number of guests (requires API connectivity)

---

## 3. Availability & Inventory Management

### Navigation Path
**Rooms and Rates** → **Manage Rates and Availability** (or "Rates and Inventory")

### Availability Grid (Inventory Grid)
A date-by-room-type grid showing:
- Nightly rate for each date
- Open/closed status
- Active restrictions

You can edit individual cells directly in the grid for single-date changes.

### Bulk Update Tool
**Rooms and Rates** → **Rates and Inventory** → **Bulk Update**

Steps:
1. Select start date and end date (or pick individual days from the calendar preview)
2. Choose what to update: rate OR a restriction
3. Apply the change across all selected dates

Use for seasonal rate changes or applying restrictions across a date range.

### Availability Restrictions

| Restriction | Code | What It Does |
|------------|------|-------------|
| **Stop Sell** / Close Room | — | Closes the room to new bookings on that date; guests see no availability |
| **Closed to Arrival (CTA)** | CTA | Prevents check-in on that specific date; stays that span it are still OK |
| **Closed to Departure (CTD)** | CTD | Prevents check-out on that specific date |
| **Minimum Stay** | MinLOS | Minimum number of nights a booking must include |
| **Maximum Stay** | MaxLOS | Maximum number of nights per booking |

To close a room: check the **"Close Room"** checkbox on the target date in the calendar and save. To reopen: uncheck and save.

### Allotments / Base Allocation
If the property has a contracted **Base Allocation** with Expedia (a minimum number of rooms agreed to sell through the channel), Expedia will maintain that allotment even if the channel manager sends lower availability. Changes made in the EPC extranet apply only to the Expedia channel — changes made in a channel manager propagate based on the integration setup.

### Booking Window
Configure how far in advance guests can reserve and how close to the arrival date bookings remain open. Guests book on average ~73 days in advance.

---

## 4. Property Setup

### Navigation Path
**Property** (left nav) → subsections below

### Property Details
The main property information form. Sections include:
- Property name
- Property type (hotel, motel, bed & breakfast, cabin, lodge, etc.)
- Physical address and location details
- Star rating (if applicable)
- Number of units
- Chain affiliation (if any)
- Currency

### Check-In / Check-Out Configuration
- Set standard check-in time (e.g., 3:00 PM)
- Set standard check-out time (e.g., 11:00 AM)
- Express check-in options and instructions can be added here or via the Messages tool

### Amenities
Configured in the **Property Details** or **Amenities** subsection:

**Property Amenities** (campground/building-wide):
- Pool, hot tub, recreation area, laundry, parking, pet area, fire pits, camp store, playground

**Room Amenities** (per-cabin):
- TV, Wi-Fi, kitchen, dishwasher, fireplace, air conditioning, private deck, hot tub

Critical: an amenity not listed means the listing is invisible in filtered searches for that amenity.

### Policies
Configure under the **Policies** subsection (also accessible via Property Details):
- Cancellation policy (links to rate plan settings)
- Check-in age minimum
- Pet policy (allowed/not allowed, fees)
- Smoking policy
- Event and party rules
- Maximum occupancy
- House rules
- Fee schedule (resort fees, parking fees, cleaning fees)
- Deposit requirements

### Points of Interest
Add nearby attractions with optional distances. Used by the platform to populate the local area section of the listing page. ~90% of travelers want location context.

---

## 5. Content Management

### Navigation Path
**Property** → **Property Details** (contains Content Score and photo upload)

### Content Score
Scored **0–100**. Found by clicking **Property Details** in the left nav. Shows both the overall score and sub-scores:

| Sub-score | What It Evaluates |
|-----------|------------------|
| **Property Amenities** | Campground/building features listed |
| **Room Amenities** | In-unit features listed per room type |
| **Policies and Deposits** | Cancellation, fees, house rules completeness |
| **Photos** | Quantity, resolution, and coverage by category |

The platform provides specific improvement suggestions alongside each sub-score.

### Photo Management in EPC
EPC manages photos at two levels:
1. **Property-level photos** — exterior, grounds, common areas, campground facilities
2. **Room-type photos** — photos uploaded per room type (cabin interior, beds, bathroom)

**Specifications:**
- Minimum resolution: 1,000 px on the longest side
- High-resolution (recommended): 2,880 px+ on the longest side
- Recommended quantity: 4 photos per room type (including bathroom), plus property-wide shots
- Upload via browser in Property Details, or via the mobile app camera (with real-time Photo Score feedback)

**Impact:** Properties with 20+ high-quality images receive 136% more bookings. Unique per-room-type photos yield up to 11% higher conversion.

### Photo Score
A sub-tool within the Content Score that evaluates whether the gallery has the specific photo categories travelers want (e.g., bathroom, bedroom, kitchen, exterior). Gaps are identified with recommendations.

### Descriptions
Located in Property Details. Must be 400+ characters to meet minimum requirements. Write separate descriptions for:
- Property overview (the campground/grounds)
- Room type descriptions (written per cabin type in the Rooms and Rates section)

---

## 6. Promotions & Marketing

### Navigation Path
**Marketing** (left nav) → submenus for each tool

### Accelerator (Pay-Per-Stay Boost)
**Path:** Marketing → Accelerator → Create

Direct URL: `apps.expediapartnercentral.com/lodging/sponsoredcontent/sponsoredlisting/manage/`

**Setup steps:**
1. Click **"Create"** within Accelerator
2. Select target dates (specific range or always-on)
3. Set compensation rate (higher rate = more sort order boost)
4. Preview forecasted sort order impact before activating
5. Launch — no upfront cost; charged only on completed stays

**2025 features:**
- Target specific days of the week
- Target specific rate plan types (e.g., only packages)
- Apply block-out dates to prevent unnecessary boosting during peak periods
- Coaching recommendations with data-backed setup suggestions
- Sort simulation preview filtered by: traveler country, destination, length of stay, star/guest rating

**Results:** ~20% higher gross booking value and ~20% more net room nights.

### Promotions / Campaigns
**Path:** Marketing → Campaigns (or Promotions)

Pre-built promotion types:
- **Member Deals** — discounts for One Key loyalty members (Blue, Silver, Gold, Platinum tiers)
- **Non-Refundable Rate** — discount in exchange for no-refund policy
- **Package Deals** — bundle with flights and/or car rental
- **Early Booking** — discount for advance reservations
- **Last-Minute** — discount for bookings near check-in

To create a promotion: select the type, set the discount percentage, define the applicable room types and date ranges, and activate.

### TravelAds (Pay-Per-Click Sponsored Listings)
**Access:** Via the TravelAds platform at **travelads.expedia.com** — a separate portal from Partner Central, though accessible via a link in the Marketing tab.

**Setup controls:**
- Daily budget cap
- Bidding strategy
- Audience and destination targeting
- Custom ad images and copy (in addition to listing content)

Reaches 200+ Expedia Group websites. Complements Accelerator: Accelerator boosts organic ranking (pay-per-stay); TravelAds buys premium paid placements (pay-per-click).

### VIP Access Program
An invitation-only program for properties delivering consistently exceptional guest experiences. Benefits: increased search visibility, VIP badge on the listing, dedicated partner support.

---

## 7. Reservations

### Navigation Path
**Reservations** (left nav)

### Reservation List View
Shows all confirmed bookings with:
- Guest name
- Booking ID / confirmation number
- Check-in and check-out dates
- Room type booked
- Rate plan
- Total booking value
- Booking source (Expedia.com, Hotels.com, etc.)
- Payment method (Expedia Collect / Hotel Collect)

Filter by: date range, booking status, unit/room type.

### Reservation Detail View
Clicking a booking opens the detail screen showing:
- Full guest contact details
- Stay dates and room assignment
- Rate breakdown (nightly rate, taxes, fees, commission)
- Payment method — if **Expedia Collect**, the **virtual card details** are displayed here
- Cancellation policy in effect
- Guest communication history

### Virtual Card Access
For Expedia Collect bookings: the single-use Expedia Virtual Card (EVC) number, expiration date, and billing amount appear on the reservation detail page. The card is:
- Valid for charging only within 30 days of check-in (viewable up to 180 days post-checkout)
- Single-use; becomes invalid once charged
- Charged at guest check-out for room + taxes + contracted fees only (incidentals billed directly to guest)

### Modifying a Reservation
- Open the reservation detail
- Adjust check-in/check-out dates, rate, or room assignment
- For PMS-connected properties: make changes in the PMS; they sync to EPC automatically

### Guest-Requested Cancellation
1. Open the reservation in Reservations
2. Click **"Cancel Reservation"**
3. Choose: apply standard cancellation policy OR issue a custom refund amount
4. If a cancellation fee applies, it is charged to the guest's virtual card on the cancellation date

Partners cannot cancel on a guest's behalf; guests contact Expedia Customer Service. Partners can submit a cancellation/refund request through EPC if warranted.

### Host-Initiated Cancellation
Canceling a confirmed booking as the host triggers Expedia's **External Partner-Initiated Cancellation Policy**. Penalties include financial charges, search ranking reduction, and potential listing suspension. Always review the policy before initiating.

### No-Shows
Mark a guest as a no-show via the reservation detail page. This triggers reconciliation and fee processing per the applicable rate plan.

---

## 8. Finance / Payments

### Navigation Path
**Finance** (or **Billing**) in the left nav → submenus: **Billing & Payments**, **Invoices**

### Payment Models

| Model | How It Works |
|-------|-------------|
| **Expedia Collect** | Expedia collects from the guest at booking; issues a Virtual Card (EVC) to the property for charging at checkout |
| **Hotel Collect (HotelCollect)** | Property collects payment directly from the guest; Expedia provides guest credit card details for the property to charge |
| **Expedia Traveler Preference (ETP)** | Both models active simultaneously; guest chooses at booking |

### Setting Up Virtual Card Payments
Sign up for the Expedia Virtual Card through the **"Payments"** tab within EPC. Once enrolled, EVCs are issued per booking automatically.

### Invoices
**Path:** Finance → Billing & Payments → Invoices

Shows: invoice date, booking IDs included, amounts, commission deducted, net payout amount.

### Requesting Payment (Non-EVC Model)
For properties on the invoicing model:
1. Go to the left nav → **Payments** section
2. Click **"Request payment from Expedia Group"**
3. Select the date range for unpaid reservations
4. Mark the reservations to include
5. Submit — payment received within 30 days of invoice

### Payout Schedule (Non-EVC / Invoicing)
- Expedia reconciles arrivals at the end of each month
- Payment issued approximately 30 days after reconciliation
- Add 3–5 business days for bank processing
- Example: June 1–30 arrivals → reconciled July 1 → paid ~July 31 + 3–5 days

### Virtual Card Payout Timeline
- EVC charged at guest checkout
- Funds transfer to the property's bank account within **1–2 business days** of charging the card

### Reconciliation
After each stay, confirm actual stay vs. booked stay in the reservation detail. For no-shows and early departures, update the reservation before the billing cycle closes.

### Commission Structure
EPC commissions typically range **10–30%** of the booking value, depending on property type, location, rate plan, and market. Non-refundable rates and package rates may carry different commission structures.

---

## 9. Reports & Analytics

### Navigation Path
**Reports** (left nav) → submenus for different report types

### Property Analytics
A suite of performance reports tracking the property's position in the Expedia marketplace:

| Metric | What It Shows |
|--------|--------------|
| **Visibility** | Search impressions; how often the listing appeared |
| **Conversion** | Ratio of bookings to listing page views |
| **Guest Value** | Average room revenue vs. prior year and competitive set |
| **Occupancy Rate** | Booked nights vs. available nights |
| **ADR** | Average Daily Rate |
| **RevPAR** | Revenue per Available Room |
| **Booking Window** | How far in advance guests booked |

All metrics include year-over-year comparisons. Filter by date range, room type, or booking channel.

### Rev+ (Revenue Management Tool)
**Path:** Reports → Revenue Management (or accessed from the dashboard shortcut)

Free tool, no additional signup required. Provides a real-time view updated continuously:

| Rev+ Feature | Description |
|-------------|-------------|
| **Price Calendar** | Your rates vs. competitive set for next 90 days |
| **Market Demand Score** | Demand forecast based on Expedia Group booking data; updated daily |
| **Competitive Price Grid** | Competitor pricing trends over a selected period |
| **Daily Market Alerts** | Email/dashboard notifications when market pricing shifts significantly |
| **Occupancy & Compression** | Real-time local occupancy signals showing peak vs. soft dates |

**Competitive Set:** Define 5–19 competitor properties. Used for Rev+ benchmarking and analytics. Set up or update within the Rev+ or Performance section.

**Use case:** Review weekly. Dates where your rate is above market + low occupancy = prime Accelerator candidates. Dates where market demand is spiking = opportunity to raise rates.

### Offer Strength Score / Visibility Performance
**Path:** Property → Performance (or Visibility Performance page)

Two composite scores driving search rank:

| Score | Components |
|-------|-----------|
| **Offer Strength** | Content completeness + rate competitiveness + calendar openness |
| **Guest Experience** | Relocation rate + refund rate + review scores |

### Reporting: Billing Reports
Downloadable reports showing invoices, payments, and commission breakdowns. Accessible via the Finance → Invoices section.

---

## 10. Messages / Guest Communications

### Navigation Path
**Messages** (left nav)

### Inbox Features
- Threaded conversations per booking
- Filter by: unread/unanswered, stay dates, property (for multi-property accounts)
- Flag messages for follow-up
- Either party (host or guest) can initiate a conversation once a booking is confirmed

### Smart Templates
Pre-written message templates for common scenarios:
- Booking confirmation
- Pre-arrival (check-in instructions, access codes, parking)
- Mid-stay check-in
- Post-stay thank you

Create and save custom templates for recurring messages.

### Scheduled Messages
Set messages to auto-send at a defined time relative to check-in or check-out:
- Example: "Send check-in instructions 3 days before arrival"
- Example: "Send checkout reminder 1 day before departure"

### In-House Feedback
Expedia sends an automated email to guests on their **arrival day** requesting real-time feedback on:
- Check-in experience
- Property condition
- Location

Feedback arrives in the Messages section. Hosts can address issues proactively before checkout, reducing negative review risk.

### Post-Stay Reviews
Post-stay reviews appear in the dashboard and are notified via email/mobile app. Respond directly through the Messages or Reviews section. Responses are public.

### Mobile App
The **Expedia Group Partner Central** app (iOS and Android) provides full message management with push notifications for new messages. Mobile users respond ~20% faster than desktop-only users — important for response rate metrics.

### EPC vs Vrbo Messaging
Both portals use the same underlying messaging API. Third-party PMS and channel management tools (Hostaway, Guesty, AdvanceCM) can integrate via the Expedia Messaging API to handle EPC guest messages in a unified inbox alongside other OTA messages.

---

## 11. Account & Settings

### Navigation Path
Property selector (top of left nav or Multi Property Home Page) → **Administration** → **Users**

### Adding Team Members
1. Open the **Multi Property Home Page** (for multi-property accounts)
2. Select the property
3. Click **Administration**
4. Click **Users**
5. Click **"Invite user"**
6. Enter: First name, Last name, Email address
7. Click **"Next"** to proceed to role/permission assignment
8. Complete the invitation — the user receives an email invite to set up their access

### User Roles
EPC supports multiple user roles with different permission levels (exact role names vary; contact your Expedia market manager for current role definitions). Roles typically include: Admin/Owner, Manager, Front Desk/Limited.

### Notification Preferences
Accessible via account settings. Configure:
- Booking confirmation notifications
- Cancellation alerts
- Rev+ market alerts (daily email)
- Content score update notifications
- Messaging alerts (new guest messages)

### Connectivity / Channel Manager Settings
**Path:** Rooms and Rates → Expedia Connectivity Settings (in the left sidebar submenu)

Used to connect a channel manager or PMS:
1. Select your connectivity provider (e.g., Hostaway, OPERA, etc.)
2. Choose what the provider handles: rates/availability updates, reservation retrieval, or both
3. Click **"Save and continue"**

If connected via a channel manager/PMS, most inventory changes should be made in the PMS — changes made in EPC directly may be overwritten by the next sync.

---

## 12. EPC vs. Vrbo Host Dashboard — Key Differences

### Routing: Which Portal for What Property Type?
When registering a new property on Expedia Group:
- Select **"Lodging"** → stays in **EPC** (hotels, motels, B&Bs, cabins listed as lodging units)
- Select **"Private Residence"** → redirected to **Vrbo** to complete setup

A campground listing cabins as multi-unit lodging (with room types) uses EPC. A single private-home rental typically uses the Vrbo host dashboard. Some operators use both portals for different property types.

### Interface Design Differences

| Feature | EPC (Expedia Partner Central) | Vrbo Host Dashboard |
|---------|------------------------------|-------------------|
| **Interface style** | Hotel extranet; room-type + rate-plan model | Vacation rental host dashboard; per-listing model |
| **Room structure** | Room Types with multiple Rate Plans attached | Single listing per property; one calendar |
| **Availability model** | Allotment-based (rooms × nights) | Per-listing open/close |
| **Calendar name** | Rates and Availability / Inventory Grid | Calendar tab |
| **Revenue tool name** | **Rev+** | **MarketMaker** (same underlying tool, different name) |
| **Promotions access** | Marketing tab → Accelerator/Campaigns | Promotions tab |
| **Finance** | Finance / Billing & Payments / Invoices | Payments section |
| **Loyalty program** | One Key (Blue/Silver/Gold/Platinum) | One Key (same program) |
| **Content Score** | Found in Property Details | Found in listing editor |
| **Premier Host** | Not available in EPC | Vrbo-specific program |
| **VIP Access** | EPC-specific hotel quality program | Not available |
| **User roles** | Multi-user with Administration section | Simpler host-level access |
| **Mobile app** | "Expedia Group Partner Central" app | Same app covers both portals |

### Which System Is "Authoritative" for What

| Setting | Authoritative System |
|---------|---------------------|
| Room type structure and rate plans | EPC (Rooms and Rates) |
| Availability and rates | Whichever system the channel manager pushes to (EPC if not connected, or channel manager overrides) |
| Property-level amenities and policies | EPC (Property Details) |
| Listing photos | EPC manages hotel-side photos; Vrbo manages vacation rental photos independently |
| Guest reviews | Shared review pool across Expedia Group; visible in both portals |
| Guest messages | Portal-specific — EPC messages and Vrbo messages are separate inboxes unless unified via PMS integration |
| Finance / payouts | Portal-specific — EPC Finance tab for EPC bookings; Vrbo Payments for Vrbo bookings |
| Promotions | Each portal manages its own promotions independently |
| TravelAds | Separate platform (travelads.expedia.com); covers both |
| Premier Host status | Vrbo-only — EPC has VIP Access instead |

### Commission Comparison

| Platform | Commission Range |
|----------|----------------|
| **EPC (hotel-style)** | 10–30% of booking value |
| **Vrbo (pay-per-booking)** | ~8% (5% commission + 3% payment processing) |

EPC commissions are generally higher than Vrbo because EPC operates more like a full OTA channel agreement. The specific rate is negotiated during onboarding and can vary.

### What You Can Do in EPC That You Cannot Do in Vrbo Dashboard
- Manage multiple **room types** under one property listing (e.g., "Lakefront Cabin," "Standard Cabin," "Deluxe Cabin" as separate room types with separate rate plans)
- Set **allotments** (contracted minimum room counts)
- Access the **VIP Access** hotel quality program
- Set up **Expedia Traveler Preference (ETP)** — letting guests choose payment method at booking
- Full **Administration / multi-user** access management with role-based permissions
- Access **invoicing model** payment requests

### What You Can Do in Vrbo Dashboard That You Cannot Do in EPC
- Qualify for the **Premier Host** program
- Access the **Performance Milestones** achievement system
- Manage listings as **private residences** with per-listing calendar model
- Set up **damage deposits** (Vrbo model) rather than virtual card charging
- Configure **Avalara MyLodge Tax** automation (Vrbo-side integration)

---

## EPC-Specific Terminology Glossary

| Term | Definition |
|------|-----------|
| **EPC / Extranet** | Expedia Partner Central; the hotel-side management portal |
| **Room Type** | A category of unit (e.g., "Lakefront Cabin"); multiple rate plans attach to each |
| **Rate Plan** | A pricing configuration attached to a room type; defines rate, cancellation policy, refundability |
| **Allotment / Base Allocation** | Contracted minimum number of rooms Expedia can sell; floor below which channel manager updates are ignored |
| **CTA** | Closed to Arrival — no check-ins allowed on a specific date |
| **CTD** | Closed to Departure — no check-outs allowed on a specific date |
| **MinLOS** | Minimum Length of Stay restriction |
| **MaxLOS** | Maximum Length of Stay restriction |
| **Stop Sell** | Closes a room to new bookings (same as "Close Room" in EPC UI) |
| **EVC / Virtual Card** | Expedia Virtual Card; single-use credit card issued per Expedia Collect booking |
| **Expedia Collect** | Expedia collects from the guest; issues EVC to property |
| **Hotel Collect** | Property collects directly from the guest; Expedia provides guest card details |
| **ETP** | Expedia Traveler Preference; both Expedia Collect and Hotel Collect active simultaneously |
| **Rev+** | Free revenue management tool in EPC; competitor rates + demand forecasting |
| **Auto Rate Match (ARM)** | EPC feature that automatically adjusts rates to match Booking.com / Agoda |
| **Accelerator** | Pay-per-stay visibility boost tool in the Marketing tab |
| **TravelAds** | Pay-per-click sponsored listing ads; separate portal (travelads.expedia.com) |
| **Content Score** | 0–100 listing quality rating; sub-scores: Property Amenities, Room Amenities, Policies, Photos |
| **Offer Strength Score** | Composite score: content completeness + rate competitiveness + calendar openness |
| **VIP Access** | EPC hotel quality program for consistently high-performing properties |
| **One Key** | Expedia Group's unified loyalty program (tiers: Blue, Silver, Gold, Platinum) |
| **IPM** | Integrated Property Manager; property connected via PMS/channel manager API |
