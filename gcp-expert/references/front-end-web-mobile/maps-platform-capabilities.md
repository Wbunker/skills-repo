# Google Maps Platform — Capabilities

## Overview

**Google Maps Platform** provides geospatial APIs for maps, routing, places, and geolocation. It is a separate product from Google Cloud with its own pricing, API key management, and billing.

**Key products:**
- Maps: display interactive or static maps
- Routes: calculate directions, distances, travel times
- Places: search, discover, and get details about locations
- Environment APIs: solar, air quality, pollen

---

## Maps APIs

### Maps JavaScript API

The primary web-based mapping API for interactive maps in browsers.

**Features:**
- Interactive map rendering (zoom, pan, rotate, tilt)
- Custom markers and InfoWindows
- Polygon/polyline/circle overlays
- Data layer for GeoJSON rendering
- Street View integration
- Map types: roadmap, satellite, hybrid, terrain
- Map styling (JSON styles to customize colors, labels)
- Drawing tools (draw on map)
- Traffic layer, transit layer, bicycling layer
- Heatmaps (Visualization library)
- Directions renderer (draw routes on map)
- Distance matrix display

**Getting started:**
```html
<script src="https://maps.googleapis.com/maps/api/js?key=YOUR_API_KEY&callback=initMap" async defer></script>
```

**Libraries:** (loaded with `&libraries=` parameter)
- `places` — Places Autocomplete, Place Search
- `visualization` — Heatmaps
- `drawing` — Drawing tools
- `geometry` — Computational geometry functions

### Maps SDK for Android / iOS

Native SDKs for embedding interactive maps in mobile apps.
- Offline maps (Google Maps SDK does not support true offline; use Mapbox for offline)
- ARCore integration for augmented reality navigation
- Navigation SDK: turn-by-turn navigation, available separately

### Maps Static API

Returns a static PNG image of a map given parameters (center, zoom, size, markers, paths).
- Use for: email embeds, server-side image generation, PDF reports
- No JavaScript required; simple HTTP GET request
- Max image size: 640x640 pixels (2048x2048 with premium plan)

### Street View Static API

Returns a panoramic Street View image for a given location or panorama ID.
- Use for: property descriptions, location previews, embedded street-level imagery

### Photorealistic 3D Tiles

- 3D mesh tiles of the real world (buildings, terrain)
- Integrate with Cesium.js for 3D visualization in the browser
- Use for: urban planning, architecture visualization, immersive experiences

---

## Routes APIs

### Routes API (Recommended)

The modern replacement for the Directions API and Distance Matrix API:

**Compute Routes** (single route):
- Origin, destination, waypoints
- Travel modes: DRIVE, WALK, BICYCLE, TWO_WHEELER, TRANSIT
- Departure time (for real-time or predicted traffic)
- Route modifiers: avoid tolls, highways, ferries, indoor
- Route preference: FUEL_EFFICIENT, SHORTER_DISTANCE, FEWER_TRANSFERS
- Returns: polyline, distance, duration, toll information, fuel consumption estimate

**Compute Route Matrix** (multi-origin/destination):
- Up to 625 elements (origin × destination pairs) per request
- Returns travel time and distance for each origin-destination pair
- Use for: delivery optimization, service area analysis

**Key improvements over legacy Directions API:**
- Faster response times
- More detailed route metadata (tolls breakdown, eco-routing)
- Field masks (request only needed fields to reduce latency and cost)

### Directions API (Legacy)

Still functional; use Routes API for new development. Key features:
- Step-by-step directions with HTML instructions
- Multiple routes (alternatives: true)
- Waypoint optimization (find optimal order for multiple stops)
- Transit routes with transit departure/arrival times

### Distance Matrix API (Legacy)

Compute travel time/distance for multiple origins × destinations. Use Routes API Compute Route Matrix for new development.

### Route Optimization API (Fleet Routing)

Solve vehicle routing problems (VRP):
- Assign deliveries/visits to a fleet of vehicles
- Minimize total travel time, distance, or number of vehicles
- Constraints: time windows, vehicle capacity, max route duration, skills
- Supports hundreds of vehicles and thousands of shipments
- Asynchronous API for large problems

---

## Places APIs

### Places API (New)

The updated Places API with improved data quality and pricing:

**Text Search**: search for places by query (e.g., "restaurants near downtown Austin")
**Nearby Search**: search for places within a radius of a location
**Place Details**: get full details (address, phone, hours, reviews, photos) for a Place ID
**Place Autocomplete**: type-ahead suggestions as user types an address or place name

**Place IDs:**
- Unique stable identifier for each place
- Use Place IDs (not addresses) to reference places in your data
- Place IDs are stable; addresses change but Place IDs remain consistent

### Geocoding API

**Geocoding**: convert address string → latitude/longitude coordinates
**Reverse geocoding**: convert lat/lng → formatted address and place components

Use cases:
- Validate and standardize addresses from user input
- Convert addresses in databases to coordinates for mapping
- Determine the street address of a GPS coordinate

### Address Validation API

Enhanced address validation:
- Confirm address existence and deliverability (USPS data for US addresses)
- Identify missing components (missing apartment number)
- Provide standardized USPS address (for US)
- Returns verdict: `CONFIRMED`, `UNCONFIRMED_BUT_PLAUSIBLE`, `UNCONFIRMED_AND_SUSPICIOUS`

### Geolocation API

Determine device location using cell tower and Wi-Fi data (without GPS):
- Server-side API; send Wi-Fi access point BSSIDs and cell tower information
- Returns estimated latitude/longitude and accuracy radius
- Use when GPS is unavailable or for faster location acquisition

### Air Quality API

Real-time and forecast air quality data:
- Current air quality index (AQI) for a location
- Hourly forecast (24-hour, 96-hour)
- Pollutant breakdown (PM2.5, PM10, O3, NO2, CO, SO2)
- Health recommendations

### Solar API

Solar panel feasibility analysis for rooftops:
- Solar potential for a building's rooftop
- Optimal panel placement and coverage
- Annual energy production estimates
- Financial analysis (savings vs cost)
- Use for: solar marketplace apps, energy audit tools

### Pollen API

Daily pollen count data:
- Tree, grass, and weed pollen counts
- 5-day forecast
- Plant species breakdown by location
- Use for: health apps, outdoor activity planners

---

## Pricing and Quotas

### Free Monthly Credit

- $200 USD free monthly credit per billing account
- Applies across all Maps Platform products
- Most small/medium apps stay within free tier

### Key Pricing SKUs

| API | SKU | Price (per 1000) | Free tier units/month |
|---|---|---|---|
| Maps JavaScript API | Dynamic Maps | $7.00 | ~28,000 map loads |
| Routes API | Compute Routes | $5.00 | 40,000 route requests |
| Routes API | Compute Route Matrix | $10.00 | 20,000 elements |
| Places API | Text Search | $17.00 | ~11,000 requests |
| Places API | Place Details | $17.00 | ~11,000 requests |
| Place Autocomplete | Per session | $2.83/session | ~70,000 sessions |
| Geocoding API | Geocoding | $5.00 | 40,000 requests |
| Address Validation | Validation | $2.50 | 80,000 requests |

Note: prices change; always check [Google Maps Platform pricing](https://mapsplatform.google.com/pricing/) for current rates.

### Quotas and Rate Limits

- Default QPS limits apply per API; request increases via Google Maps Platform Console
- Monthly usage caps can be set to prevent unexpected charges

---

## API Key Security

Best practices for Maps Platform API keys:

**Restrict by application type:**
- **Browser (HTTP referrer restriction)**: `https://yourdomain.com/*` — for Maps JavaScript API
- **Server (IP address restriction)**: your server's IP — for server-side APIs
- **Android app (SHA-1 + package name)**: for Maps SDK for Android
- **iOS app (bundle ID)**: for Maps SDK for iOS

**Restrict by API:**
- Only enable the specific APIs each key needs
- Never use an unrestricted key in production

**Separate keys per environment:**
- Different API keys for development, staging, production
- Different keys for web, Android, iOS, server-side

**Monitor usage:**
- Set up billing alerts for unexpected spike in usage
- Monitor per-API usage in Maps Platform Console
