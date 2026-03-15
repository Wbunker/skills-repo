# AWS AppSync & Location Service — Capabilities Reference

For CLI commands, see [appsync-location-cli.md](appsync-location-cli.md).

> **Note**: AppSync is also referenced in the Serverless & Integration domain ([appsync-mq-appflow-capabilities.md](../serverless-integration/appsync-mq-appflow-capabilities.md)) for general GraphQL API architecture patterns. This file focuses on AppSync features relevant to front-end/mobile applications, plus Amazon Location Service.

---

## AWS AppSync

**Purpose**: Fully managed GraphQL and Pub/Sub API service. Lets front-end and mobile applications interact with multiple data sources through a single strongly-typed API endpoint with built-in real-time and offline capabilities.

### API Types

| API Type | Description | Use case |
|---|---|---|
| **GraphQL API** | Standard GraphQL with queries, mutations, subscriptions | Full-stack apps needing typed schema and real-time |
| **Merged API** | Combines multiple AppSync source APIs into one endpoint | Microservices / team-based schema ownership |
| **Events API** | Pub/Sub without a GraphQL schema; publish/subscribe to named channels | Simple real-time event broadcasting, chat, notifications |

### Data Sources

| Source | Operations |
|---|---|
| **Amazon DynamoDB** | GetItem, PutItem, UpdateItem, DeleteItem, Query, Scan, BatchGetItem, TransactWriteItems |
| **AWS Lambda** | Invoke any Lambda function; full request/response control |
| **Amazon RDS (Aurora Serverless v1/v2)** | SQL via RDS Data API |
| **HTTP endpoint** | Any HTTP/HTTPS endpoint (REST or other) |
| **Amazon OpenSearch Service** | Full-text search and aggregation queries |
| **Amazon EventBridge** | Put events to an EventBridge event bus |
| **None** | Local resolver; transforms data without a backend call (useful for subscriptions triggered by client mutations) |

### Resolvers

| Type | Description | Use case |
|---|---|---|
| **Unit resolver** | Single data source mapping; request/response mapping | Simple CRUD: `getItem`, `putItem` |
| **Pipeline resolver** | Chains multiple functions in sequence; each function has its own data source | Multi-step logic: validate → authorize → write → notify |
| **Direct Lambda resolver** | Lambda receives full AppSync request context | Complex business logic, fan-out, non-DynamoDB backends |

Resolvers are written in:
- **JavaScript (APPSYNC_JS runtime)** — recommended; full JavaScript with `@aws-appsync/utils` helpers
- **Apache Velocity Template Language (VTL)** — legacy; still supported

### Pipeline Functions

Reusable resolver components that can be shared across multiple pipeline resolvers:
- Each function has its own data source, request handler, and response handler
- Executed in order; output of one function becomes input to the next
- Defined independently from resolvers and reused across query/mutation types

### Subscriptions (Real-Time)

- Clients subscribe to mutation operations via WebSocket (managed by AppSync)
- Protocol: `graphql-ws` (recommended) or legacy `graphql-transport-ws`
- AppSync triggers subscription notifications when the subscribed mutation executes
- **Enhanced subscriptions**: Server-side subscription filters — clients receive only events matching their filter expression; reduces noise and improves performance
- Subscription connection requires authentication (same modes as queries/mutations)
- Keep-alive ping/pong maintained automatically

### AppSync Events API (Pub/Sub without GraphQL)

- Create named **channel namespaces** (e.g., `/chat/room1`)
- Publishers POST events to a channel via HTTP or WebSocket
- Subscribers connect via WebSocket and receive all events on a channel
- No schema, no types — raw JSON event payloads
- Authorization: API key, IAM, Cognito, Lambda, OIDC
- Use case: live dashboards, chat, broadcasting scores/prices, IoT telemetry display

### Authorization Modes

| Mode | Description |
|---|---|
| **API key** | Static key in `x-api-key` header; suitable for public read-only APIs or development |
| **Amazon Cognito User Pools** | Validates Cognito JWT; per-type/per-field access control with `@auth` directive and group claims |
| **IAM (SigV4)** | Signed AWS requests; for server-to-server, Lambda-to-AppSync, and Amplify unauthenticated access |
| **OpenID Connect (OIDC)** | Validates JWT from any OIDC-compliant identity provider (Auth0, Okta, etc.) |
| **Lambda** | Custom authorization logic; Lambda returns `isAuthorized: true/false` and optional TTL-cached decision |

Multiple authorization modes can be active simultaneously — set a default and override per type/field using the `@auth` directive in the schema.

### Schema Directives (AppSync + Amplify Data)

| Directive | Description |
|---|---|
| `@model` | Auto-generate DynamoDB table + CRUD resolvers (Amplify Data) |
| `@auth` | Define authorization rules per type or field |
| `@hasOne` / `@hasMany` / `@belongsTo` | Define relationships; AppSync generates resolver logic |
| `@index` | Add DynamoDB GSI for custom query patterns |
| `@function` | Connect a field resolver to a Lambda function |
| `@http` | Connect a field resolver to an HTTP data source |
| `@predictions` | Chain AI/ML predictions (Amazon Rekognition, Translate, etc.) |
| `@searchable` | Stream model data to OpenSearch for full-text search |

### Server-Side Caching

- Enable per-API; configurable TTL (1–3,600 seconds)
- Cache behavior: `FULL_REQUEST_CACHING` (cache by full query + variables) or `PER_RESOLVER_CACHING` (opt-in per resolver with `cachingConfig`)
- Cache instance sizes: `SMALL`, `MEDIUM`, `LARGE`, `XLARGE`, `LARGE_2X`, `LARGE_4X`, `LARGE_8X`, `LARGE_12X`
- Cache keys configurable: include query variables and/or authorization headers
- Flush entire cache or a specific cache key via API/console

### Conflict Detection and Resolution (Offline Sync / DataStore)

Used by AWS Amplify DataStore for offline-first mobile and web applications:

| Strategy | Description |
|---|---|
| **Optimistic concurrency** | Each item has a `_version` field; AppSync rejects writes where version doesn't match (client must re-read and retry) |
| **Auto merge** | AppSync merges non-conflicting field-level changes; conflict if same field modified |
| **Lambda** | Custom resolution logic; Lambda receives server/client versions, returns winning item |
| **None (last-write-wins)** | No conflict check; latest write overwrites |

### Merged APIs (Schema Composition)

- **Source APIs**: independent AppSync APIs owned by different teams/services
- **Merged API**: single endpoint aggregating all source API schemas
- Merge type: `AUTO_MERGE` (automatic on source change) or `MANUAL_MERGE` (explicit merge trigger)
- Enables micro-frontend architecture: each squad manages their own AppSync API; consumers use the merged endpoint

### Monitoring and Observability

- CloudWatch Metrics: `4XXError`, `5XXError`, `Latency`, `ConnectSuccess`, `DisconnectSuccess`, `SubscribeSuccess`
- CloudWatch Logs: per-API logging at `ERROR` or `ALL` level (request/response, resolver execution)
- X-Ray tracing: enable per-API for distributed tracing through resolvers to data sources

---

## Amazon Location Service

**Purpose**: Add location data (maps, geocoding, routing, geofencing, device tracking) to applications without sharing data with third-party providers. Data stays within AWS.

### Core Capabilities

| Capability | Description |
|---|---|
| **Maps** | Render interactive maps in web and mobile apps |
| **Places** | Search for addresses, points of interest; geocode and reverse-geocode |
| **Routes** | Calculate directions and travel time; matrix routing; snap GPS traces to roads |
| **Geofences** | Define polygon areas; detect device entry/exit events |
| **Trackers** | Ingest and store device positions; link to geofences for entry/exit triggers |

### Maps

- **Map resources**: create named map resources backed by a data provider
- **Data providers**: Esri, HERE, Grab (Southeast Asia), Open Data (free; no provider restrictions)
- **Style names** (examples): `VectorEsriNavigation`, `VectorHereExplore`, `RasterHereSatellite`, `VectorOpenDataStandardLight`
- **Rendering**: MapLibre GL JS (web), MapLibre GL Native (iOS/Android), AWS Amplify Geo library
- **Tile and glyph endpoints** served directly from Location Service; no external CDN calls required
- **Map tiles** available over HTTPS; authenticated via SigV4 or API key

### Places (Geocoding & Search)

| Operation | Description |
|---|---|
| **SearchPlaceIndexForText** | Free-text search (e.g., "coffee near Pike Place Market") |
| **SearchPlaceIndexForPosition** | Reverse geocode: lat/lon → address |
| **GetPlace** | Look up a specific place by its Place ID |
| **SearchPlaceIndexForSuggestions** | Autocomplete / typeahead suggestions as user types |

- Data providers: Esri, HERE, Grab
- **Filtering**: by country (`FilterCountries`), bias position (`BiasPosition`), bounding box (`FilterBBox`)
- **Categories**: filter by place category (food, hotel, gas station, etc.) — provider-dependent

### Routes

| Operation | Description |
|---|---|
| **CalculateRoute** | Point-to-point directions; returns legs, steps, distance, duration |
| **CalculateRouteMatrix** | O×D matrix of travel times/distances between multiple origins and destinations |
| **SearchForSuggestionsRoute (snap to roads)** | Snap a series of GPS coordinates to the nearest road network |

Route options:
- Travel modes: `Car`, `Truck`, `Walking`
- Avoid: `Tolls`, `Ferries`
- Truck dimensions/weight for commercial routing (HERE provider)
- Departure time for traffic-aware routing

### Geofences

- **Geofence collection**: named container for geofences
- **Geofence**: polygon (GeoJSON) or circle defining an area of interest
- **Batch operations**: `BatchPutGeofence`, `BatchDeleteGeofence` for bulk management
- Up to 10,000 geofences per collection (soft limit, can be raised)
- No limit enforcement by service itself — evaluation happens via Trackers

### Trackers

- **Tracker**: named resource that ingests and stores device positions (lat/lon + timestamp + optional metadata)
- **BatchUpdateDevicePosition**: ingest up to 10 positions per device per batch
- **GetDevicePosition**: latest position for a specific device
- **GetDevicePositionHistory**: historical positions within a time range
- **ListDevicePositions**: latest position for all devices in a tracker

**Position filtering** (reduces storage and EventBridge noise):

| Filter | Description |
|---|---|
| **TimeBased** | Accept position only if enough time has elapsed since last accepted |
| **DistanceBased** | Accept position only if device moved enough distance |
| **AccuracyBased** | Accept position only if new position is more accurate |

**Tracker → Geofence linking**: link a tracker to one or more geofence collections; Location Service evaluates positions against geofences automatically.

### EventBridge Integration

When a device position triggers a geofence event:
- EventBridge event published to default event bus
- Event detail type: `ENTER` or `EXIT`
- Payload includes: tracker name, device ID, geofence collection, geofence ID, sample time, position
- Downstream actions: notify user (SNS), update database (Lambda), trigger workflow (Step Functions)

### Authentication

| Method | Use case |
|---|---|
| **IAM (SigV4)** | Server-side or Amplify authenticated users (via Cognito Identity Pool) |
| **API keys** | Unauthenticated map tile rendering in web apps; embedded public maps |
| **Amazon Cognito** | End-user authentication; use Identity Pool to vend scoped IAM credentials |

API keys:
- Created per map/place index/route calculator resource
- Set expiry date (up to 3 years)
- Restrict by allowed actions, allowed referer domains, allowed IP ranges

### Amplify Geo Integration

Amplify Gen 2 wraps Location Service for front-end developers:

```typescript
// amplify/geo/resource.ts
import { defineGeo } from '@aws-amplify/backend';
export const geo = defineGeo({
  maps: { default: 'myMap', additional: ['satelliteMap'] },
  searchIndices: { default: 'myPlaceIndex' },
});
```

- Amplify Geo library: `Geo.searchByText()`, `Geo.searchByCoordinates()`, `Geo.getAvailableMaps()`
- MapLibre GL component: `<MapView>` React component in `@aws-amplify/ui-react-geo`

### Pricing Model

| Resource | Billing unit |
|---|---|
| Maps | Per map tile requested |
| Places | Per geocoding / search request |
| Routes | Per route calculation |
| Geofences | Per geofence evaluation (position × geofence collections linked) |
| Trackers | Per device position stored |
