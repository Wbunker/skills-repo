# Connectivity & Integration

## iCal Calendar Sync

The simplest multi-platform sync option. Prevents double bookings when listing on multiple OTAs (Airbnb, Booking.com, direct site, etc.).

**How it works:**
- **Export** your Vrbo/Expedia calendar as an iCal feed URL
- **Import** that URL into other platforms (and vice versa)
- Blocked dates on one platform propagate to others

**Limitation:** iCal sync has a delay of **15–30 minutes** — it is not real-time. For high-volume properties or multiple platforms, a channel manager is more reliable.

**Setup:** Found in Calendar settings > Calendar Sync or Import/Export Calendar.

---

## VRBO Connectivity Partner Program

For campgrounds managing **multiple cabins** or wanting automated rate/availability sync, connecting via a certified Property Management System (PMS) or Channel Manager is the recommended path.

**Onboarding:** vrbo.com/p/onboard

**Results:** Connected property managers see an average **6% year-over-year increase in net booking value** (Expedia Group data).

### Software Categories

| Category | What It Does |
|----------|-------------|
| **Property Management System (PMS)** | Manages rates, availability, reservations, payments, guest communications, owner statements |
| **Channel Manager** | Distributes inventory to multiple OTAs; syncs content and pricing |

### Certified Connectivity Partners

Popular certified integrations for vacation rental managers:

| Software | Type |
|----------|------|
| Track | PMS |
| OwnerRez | PMS |
| Hostfully | PMS |
| Escapia | PMS |
| Streamline | PMS |
| Lodgix | PMS |
| HostAway | PMS + Channel Manager |
| Rentals United | Channel Manager |
| Bluetent | Channel Manager |
| Avantio | PMS + Channel Manager |
| Ciirus | PMS |
| iTrip | Franchise PMS |

**Tier levels:** Elite/Preferred partner tiers rated on integration quality, reliability, and host outcomes.

---

## EG Connectivity Hub (API — Software Providers Only)

**URL:** developers.expediagroup.com/supply/lodging

GraphQL-based APIs available to **approved software providers** (not individual property managers directly):

| API | Function |
|-----|----------|
| Messaging API | Retrieve and send guest messages |
| Compliance API | Retrieve/update regulatory info |
| Property Status API | On-demand property status and details |
| Reservation Retrieval API | Pull reservations programmatically |
| Reservation Update API | Modify reservations via GraphQL |

**Note:** Individual cabin owners cannot build directly to these APIs. They access the capabilities through an approved connectivity partner's software.

PCI compliance certification is required for all integrations.

---

## Choosing the Right Integration Level

| Scenario | Recommended Approach |
|----------|---------------------|
| 1–5 cabins, single platform | Native Vrbo dashboard only |
| 1–5 cabins, multiple OTAs | iCal sync |
| 5–15 cabins | PMS with Vrbo connectivity |
| 15+ cabins or complex pricing | PMS + Channel Manager |
| Software developer building a tool | EG Connectivity Hub API |
