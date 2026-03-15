# Google Maps Platform — CLI Reference

## Enable Maps Platform APIs

```bash
# Enable individual Maps Platform APIs
gcloud services enable maps-backend.googleapis.com \
  --project=my-project

gcloud services enable places-backend.googleapis.com \
  --project=my-project

gcloud services enable directions-backend.googleapis.com \
  --project=my-project

gcloud services enable distance-matrix-backend.googleapis.com \
  --project=my-project

gcloud services enable geocoding-backend.googleapis.com \
  --project=my-project

gcloud services enable geolocation.googleapis.com \
  --project=my-project

gcloud services enable routes.googleapis.com \
  --project=my-project

gcloud services enable routeoptimization.googleapis.com \
  --project=my-project

gcloud services enable addressvalidation.googleapis.com \
  --project=my-project

gcloud services enable airquality.googleapis.com \
  --project=my-project

gcloud services enable solar.googleapis.com \
  --project=my-project

# Enable all at once
gcloud services enable \
  maps-backend.googleapis.com \
  places-backend.googleapis.com \
  routes.googleapis.com \
  geocoding-backend.googleapis.com \
  --project=my-project

# List enabled Maps APIs
gcloud services list --enabled \
  --filter="name:(maps OR places OR directions OR geocoding OR routes OR geolocation OR addressvalidation)" \
  --project=my-project
```

---

## API Key Management

```bash
# Create an unrestricted API key (for initial testing only)
gcloud services api-keys create \
  --display-name="Maps Platform Key (dev)" \
  --project=my-project

# Create a browser-restricted key for Maps JavaScript API
gcloud services api-keys create \
  --display-name="Maps JS API Key (production)" \
  --restrictions-browser-key-allowed-referrers="https://app.example.com/*,https://www.example.com/*" \
  --restrictions-api-targets=service=maps-backend.googleapis.com \
  --project=my-project

# Create a server-restricted key for server-side geocoding/routing
gcloud services api-keys create \
  --display-name="Maps Server Key (production)" \
  --restrictions-server-key-allowed-ips="203.0.113.0/24,198.51.100.10" \
  --restrictions-api-targets=service=geocoding-backend.googleapis.com,service=routes.googleapis.com \
  --project=my-project

# Create a key restricted to Android app
gcloud services api-keys create \
  --display-name="Maps Android Key (production)" \
  --restrictions-android-key-allowed-application-sha1="AA:BB:CC:DD:EE:FF:00:11:22:33:44:55:66:77:88:99:AA:BB:CC:DD" \
  --restrictions-android-key-allowed-application-package-name="com.example.myapp" \
  --restrictions-api-targets=service=maps-backend.googleapis.com \
  --project=my-project

# Create a key restricted to iOS app
gcloud services api-keys create \
  --display-name="Maps iOS Key (production)" \
  --restrictions-ios-key-allowed-bundle-ids="com.example.myapp" \
  --restrictions-api-targets=service=maps-backend.googleapis.com \
  --project=my-project

# List all API keys
gcloud services api-keys list --project=my-project \
  --format="table(name,displayName,createTime,restrictions)"

# Describe a key (get key string)
gcloud services api-keys describe KEY_ID \
  --project=my-project

# Get the actual API key string
gcloud services api-keys get-key-string KEY_ID \
  --project=my-project

# Update key restrictions
gcloud services api-keys update KEY_ID \
  --display-name="Maps JS API Key (updated)" \
  --restrictions-browser-key-allowed-referrers="https://app.example.com/*,https://staging.example.com/*" \
  --project=my-project

# Delete an API key
gcloud services api-keys delete KEY_ID --project=my-project
```

---

## Maps Platform REST API Examples

Maps Platform APIs are used primarily via REST (not gcloud). Here are curl examples for common operations.

```bash
API_KEY="your-api-key-here"

# Geocoding API: address to coordinates
curl -s "https://maps.googleapis.com/maps/api/geocode/json?address=1600+Amphitheatre+Parkway,+Mountain+View,+CA&key=${API_KEY}" \
  | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['results'][0]['geometry']['location'])"

# Reverse Geocoding: coordinates to address
curl -s "https://maps.googleapis.com/maps/api/geocode/json?latlng=37.4221338,-122.0840170&key=${API_KEY}" \
  | python3 -m json.tool | grep '"formatted_address"'

# Routes API: compute a route (POST)
curl -s -X POST \
  -H "Content-Type: application/json" \
  -H "X-Goog-FieldMask: routes.duration,routes.distanceMeters,routes.polyline.encodedPolyline" \
  -d '{
    "origin": {"address": "Austin, TX"},
    "destination": {"address": "Houston, TX"},
    "travelMode": "DRIVE",
    "routingPreference": "TRAFFIC_AWARE",
    "departureTime": "2025-01-15T15:00:00Z"
  }' \
  "https://routes.googleapis.com/directions/v2:computeRoutes?key=${API_KEY}" \
  | python3 -m json.tool

# Routes API: compute route matrix (POST)
curl -s -X POST \
  -H "Content-Type: application/json" \
  -H "X-Goog-FieldMask: originIndex,destinationIndex,duration,distanceMeters,status" \
  -d '{
    "origins": [
      {"waypoint": {"address": "Chicago, IL"}},
      {"waypoint": {"address": "Milwaukee, WI"}}
    ],
    "destinations": [
      {"waypoint": {"address": "Indianapolis, IN"}},
      {"waypoint": {"address": "Detroit, MI"}}
    ],
    "travelMode": "DRIVE"
  }' \
  "https://routes.googleapis.com/distanceMatrix/v2:computeRouteMatrix?key=${API_KEY}" \
  | python3 -m json.tool

# Places API: text search
curl -s -X POST \
  -H "Content-Type: application/json" \
  -H "X-Goog-FieldMask: places.displayName,places.formattedAddress,places.location" \
  -d '{
    "textQuery": "pizza restaurants in Austin TX",
    "maxResultCount": 5
  }' \
  "https://places.googleapis.com/v1/places:searchText?key=${API_KEY}" \
  | python3 -m json.tool

# Places API: place details by Place ID
PLACE_ID="ChIJy3mhUO0VW4gRWFpJhpjXqlg"
curl -s \
  -H "X-Goog-FieldMask: id,displayName,formattedAddress,nationalPhoneNumber,businessStatus,currentOpeningHours" \
  "https://places.googleapis.com/v1/places/${PLACE_ID}?key=${API_KEY}" \
  | python3 -m json.tool

# Address Validation API
curl -s -X POST \
  -H "Content-Type: application/json" \
  -d '{
    "address": {
      "regionCode": "US",
      "addressLines": ["1600 Amphitheatre Pkwy", "Mountain View", "CA", "94043"]
    }
  }' \
  "https://addressvalidation.googleapis.com/v1:validateAddress?key=${API_KEY}" \
  | python3 -m json.tool

# Air Quality API: current conditions
curl -s -X POST \
  -H "Content-Type: application/json" \
  -d '{
    "location": {"latitude": 37.4221, "longitude": -122.0841},
    "includedCustomIndexes": [],
    "languageCode": "en"
  }' \
  "https://airquality.googleapis.com/v1/currentConditions:lookup?key=${API_KEY}" \
  | python3 -m json.tool
```

---

## Monitoring Maps Platform Usage

```bash
# View Maps Platform API usage metrics in Cloud Monitoring
# (Maps Platform billing is separate but APIs appear in Cloud Monitoring)

# List metric types for Maps APIs
gcloud monitoring metrics-scopes list \
  --project=my-project

# View API quotas
gcloud services quota list \
  --service=maps-backend.googleapis.com \
  --project=my-project

# Set a quota alert via Cloud Monitoring
gcloud alpha monitoring policies create \
  --policy-from-file=maps-quota-alert.json \
  --project=my-project

# Maps Platform usage dashboards are primarily in:
# Google Cloud Console → APIs & Services → Dashboard → Filter by "Maps"
# Google Maps Platform Console → maps.googleapis.com/console
echo "Use Maps Platform Console at console.cloud.google.com/apis for usage dashboards"
```
