# AWS AppSync & Location Service — CLI Reference

For service concepts, see [appsync-location-capabilities.md](appsync-location-capabilities.md).

> For broader AppSync patterns (MQ, AppFlow), see [../serverless-integration/appsync-mq-appflow-cli.md](../serverless-integration/appsync-mq-appflow-cli.md).

## AppSync — `aws appsync`

```bash
# --- GraphQL APIs ---
aws appsync create-graphql-api \
  --name MyAPI \
  --authentication-type AMAZON_COGNITO_USER_POOLS \
  --user-pool-config userPoolId=us-east-1_abc123,awsRegion=us-east-1,defaultAction=ALLOW \
  --additional-authentication-providers '[
    {"authenticationType":"API_KEY"},
    {"authenticationType":"AWS_IAM"}
  ]' \
  --xray-enabled \
  --log-config cloudWatchLogsRoleArn=arn:aws:iam::123456789012:role/appsync-logs,fieldLogLevel=ERROR

aws appsync list-graphql-apis
aws appsync get-graphql-api --api-id API_ID
aws appsync update-graphql-api --api-id API_ID --name NewName
aws appsync delete-graphql-api --api-id API_ID

# --- Schema ---
aws appsync start-schema-creation \
  --api-id API_ID \
  --definition fileb://schema.graphql

aws appsync get-schema-creation-status --api-id API_ID

aws appsync get-introspection-schema \
  --api-id API_ID \
  --format JSON \
  schema-output.json

# --- Data sources ---
# DynamoDB
aws appsync create-data-source \
  --api-id API_ID \
  --name TodosTable \
  --type AMAZON_DYNAMODB \
  --service-role-arn arn:aws:iam::123456789012:role/appsync-dynamodb-role \
  --dynamodb-config tableName=Todos,awsRegion=us-east-1,useCallerCredentials=false

# Lambda
aws appsync create-data-source \
  --api-id API_ID \
  --name TodoLambda \
  --type AWS_LAMBDA \
  --service-role-arn arn:aws:iam::123456789012:role/appsync-lambda-role \
  --lambda-config lambdaFunctionArn=arn:aws:lambda:us-east-1:123456789012:function:TodoResolver

# HTTP
aws appsync create-data-source \
  --api-id API_ID \
  --name ExternalAPI \
  --type HTTP \
  --http-config endpoint=https://api.example.com

# EventBridge
aws appsync create-data-source \
  --api-id API_ID \
  --name MyEventBus \
  --type AMAZON_EVENTBRIDGE \
  --event-bridge-config eventBusArn=arn:aws:events:us-east-1:123456789012:event-bus/MyBus

aws appsync list-data-sources --api-id API_ID
aws appsync get-data-source --api-id API_ID --name TodosTable
aws appsync delete-data-source --api-id API_ID --name TodosTable

# --- Resolvers ---
# Unit resolver (JS runtime)
aws appsync create-resolver \
  --api-id API_ID \
  --type-name Query \
  --field-name getTodo \
  --data-source-name TodosTable \
  --runtime name=APPSYNC_JS,runtimeVersion=1.0.0 \
  --code fileb://resolvers/getTodo.js

# Pipeline resolver
aws appsync create-resolver \
  --api-id API_ID \
  --type-name Mutation \
  --field-name createTodo \
  --kind PIPELINE \
  --pipeline-config functions=FUNC_ID_1,FUNC_ID_2 \
  --runtime name=APPSYNC_JS,runtimeVersion=1.0.0 \
  --code fileb://resolvers/createTodo.js

aws appsync list-resolvers --api-id API_ID --type-name Query
aws appsync get-resolver --api-id API_ID --type-name Query --field-name getTodo
aws appsync delete-resolver --api-id API_ID --type-name Query --field-name getTodo

# --- Pipeline functions ---
aws appsync create-function \
  --api-id API_ID \
  --name ValidateInput \
  --data-source-name TodosTable \
  --runtime name=APPSYNC_JS,runtimeVersion=1.0.0 \
  --code fileb://functions/validateInput.js

aws appsync list-functions --api-id API_ID
aws appsync get-function --api-id API_ID --function-id FUNC_ID
aws appsync update-function \
  --api-id API_ID \
  --function-id FUNC_ID \
  --name ValidateInput \
  --data-source-name TodosTable \
  --runtime name=APPSYNC_JS,runtimeVersion=1.0.0 \
  --code fileb://functions/validateInput-v2.js
aws appsync delete-function --api-id API_ID --function-id FUNC_ID

# --- API keys ---
aws appsync create-api-key \
  --api-id API_ID \
  --description "Public read key" \
  --expires 1798675200

aws appsync list-api-keys --api-id API_ID
aws appsync update-api-key --api-id API_ID --id KEY_ID --expires 1830211200
aws appsync delete-api-key --api-id API_ID --id KEY_ID

# --- Caching ---
aws appsync create-api-cache \
  --api-id API_ID \
  --ttl 300 \
  --api-caching-behavior PER_RESOLVER_CACHING \
  --type R4_LARGE \
  --at-rest-encryption-enabled \
  --transit-encryption-enabled

aws appsync get-api-cache --api-id API_ID
aws appsync update-api-cache --api-id API_ID --ttl 600 --type R4_XLARGE
aws appsync flush-api-cache --api-id API_ID
aws appsync delete-api-cache --api-id API_ID

# --- Custom domain names ---
aws appsync create-domain-name \
  --domain-name api.example.com \
  --certificate-arn arn:aws:acm:us-east-1:123456789012:certificate/abc-123

aws appsync associate-api \
  --domain-name api.example.com \
  --api-id API_ID

aws appsync list-domain-names
aws appsync get-domain-name --domain-name api.example.com
aws appsync disassociate-api --domain-name api.example.com
aws appsync delete-domain-name --domain-name api.example.com

# --- Merged APIs ---
aws appsync create-api \
  --event-config '{"authProviders":[{"authType":"API_KEY"}],"connectionAuthModes":[{"authType":"API_KEY"}],"defaultPublishAuthModes":[{"authType":"API_KEY"}],"defaultSubscribeAuthModes":[{"authType":"API_KEY"}]}'

aws appsync associate-merged-graphql-api \
  --source-api-identifier SOURCE_API_ID \
  --merged-api-identifier MERGED_API_ID \
  --source-api-association-config mergeType=AUTO_MERGE

aws appsync start-schema-merge \
  --association-id ASSOC_ID \
  --merged-api-identifier MERGED_API_ID

aws appsync get-source-api-association \
  --merged-api-identifier MERGED_API_ID \
  --association-id ASSOC_ID

aws appsync list-source-api-associations --api-id MERGED_API_ID
aws appsync list-merged-graphql-apis
aws appsync disassociate-merged-graphql-api --source-api-identifier SOURCE_API_ID --association-id ASSOC_ID

# --- AppSync Events API (channel namespaces) ---
aws appsync create-channel-namespace \
  --api-id EVENTS_API_ID \
  --name chat \
  --publish-auth-modes '[{"authType":"API_KEY"}]' \
  --subscribe-auth-modes '[{"authType":"AMAZON_COGNITO_USER_POOLS"}]'

aws appsync list-channel-namespaces --api-id EVENTS_API_ID
aws appsync get-channel-namespace --api-id EVENTS_API_ID --name chat
aws appsync update-channel-namespace \
  --api-id EVENTS_API_ID \
  --name chat \
  --publish-auth-modes '[{"authType":"AWS_IAM"}]'
aws appsync delete-channel-namespace --api-id EVENTS_API_ID --name chat

# --- Evaluate resolver code locally (before deploying) ---
aws appsync evaluate-code \
  --runtime name=APPSYNC_JS,runtimeVersion=1.0.0 \
  --code fileb://resolver.js \
  --context '{"arguments":{"id":"123"},"source":null,"identity":null}' \
  --function request

aws appsync evaluate-mapping-template \
  --template fileb://resolver.vtl \
  --context '{"arguments":{"id":"123"}}'

# --- Types ---
aws appsync list-types --api-id API_ID --format SDL
aws appsync get-type --api-id API_ID --type-name Todo --format JSON
aws appsync create-type \
  --api-id API_ID \
  --definition 'type Category { id: ID! name: String! }' \
  --format SDL
aws appsync delete-type --api-id API_ID --type-name Category
```

---

## Amazon Location Service — `aws location`

```bash
# --- Maps ---
aws location create-map \
  --map-name MyAppMap \
  --configuration style=VectorHereExplore \
  --pricing-plan RequestBasedUsage

aws location create-map \
  --map-name SatelliteMap \
  --configuration style=RasterHereSatellite \
  --pricing-plan RequestBasedUsage

aws location list-maps
aws location describe-map --map-name MyAppMap
aws location update-map --map-name MyAppMap --description "Primary navigation map"
aws location delete-map --map-name MyAppMap

# Get map tile (for manual testing or server-side rendering)
aws location get-map-tile \
  --map-name MyAppMap \
  --z 10 --x 512 --y 512 \
  tile.mvt

# Get map style descriptor
aws location get-map-style-descriptor --map-name MyAppMap style.json

# --- Place Indexes (Geocoding & Search) ---
aws location create-place-index \
  --index-name MyPlaceIndex \
  --data-source Here \
  --pricing-plan RequestBasedUsage \
  --data-source-config IntendedUse=SingleUse

aws location create-place-index \
  --index-name EsriPlaceIndex \
  --data-source Esri \
  --pricing-plan RequestBasedUsage

aws location list-place-indexes
aws location describe-place-index --index-name MyPlaceIndex
aws location delete-place-index --index-name MyPlaceIndex

# Search by text
aws location search-place-index-for-text \
  --index-name MyPlaceIndex \
  --text "Space Needle, Seattle" \
  --max-results 5

# Search with bias (near a point)
aws location search-place-index-for-text \
  --index-name MyPlaceIndex \
  --text "coffee" \
  --bias-position '[-122.3321, 47.6062]' \
  --max-results 10

# Search filtered by country
aws location search-place-index-for-text \
  --index-name MyPlaceIndex \
  --text "London" \
  --filter-countries '["GBR"]' \
  --max-results 5

# Reverse geocode (position → address)
aws location search-place-index-for-position \
  --index-name MyPlaceIndex \
  --position '[-122.3321, 47.6062]' \
  --max-results 3

# Autocomplete suggestions
aws location search-place-index-for-suggestions \
  --index-name MyPlaceIndex \
  --text "Pike Pl" \
  --bias-position '[-122.3321, 47.6062]' \
  --max-results 5

# Look up a specific place by ID
aws location get-place \
  --index-name MyPlaceIndex \
  --place-id PLACE_ID

# --- Route Calculators ---
aws location create-route-calculator \
  --calculator-name MyRouteCalc \
  --data-source Here \
  --pricing-plan RequestBasedUsage

aws location list-route-calculators
aws location describe-route-calculator --calculator-name MyRouteCalc
aws location delete-route-calculator --calculator-name MyRouteCalc

# Calculate a route
aws location calculate-route \
  --calculator-name MyRouteCalc \
  --departure-position '[-122.3321, 47.6062]' \
  --destination-position '[-122.4194, 37.7749]' \
  --travel-mode Car

# Route with options
aws location calculate-route \
  --calculator-name MyRouteCalc \
  --departure-position '[-122.3321, 47.6062]' \
  --destination-position '[-122.4194, 37.7749]' \
  --travel-mode Truck \
  --car-mode-options '{"AvoidTolls":true,"AvoidFerries":true}' \
  --include-leg-geometry

# Matrix routing (multiple origins to multiple destinations)
aws location calculate-route-matrix \
  --calculator-name MyRouteCalc \
  --departure-positions '[[-122.3321,47.6062],[-122.4,47.5]]' \
  --destination-positions '[[-122.4194,37.7749],[-118.2437,34.0522]]' \
  --travel-mode Car

# --- Geofence Collections ---
aws location create-geofence-collection \
  --collection-name MyGeofences \
  --pricing-plan RequestBasedUsage

aws location list-geofence-collections
aws location describe-geofence-collection --collection-name MyGeofences
aws location delete-geofence-collection --collection-name MyGeofences

# Put a single geofence (polygon)
aws location put-geofence \
  --collection-name MyGeofences \
  --geofence-id store-001 \
  --geometry Polygon='{
    "Rings": [[
      [-122.335, 47.610],
      [-122.325, 47.610],
      [-122.325, 47.600],
      [-122.335, 47.600],
      [-122.335, 47.610]
    ]]
  }'

# Batch create geofences
aws location batch-put-geofence \
  --collection-name MyGeofences \
  --entries '[
    {
      "GeofenceId": "zone-A",
      "Geometry": {
        "Polygon": {
          "Rings": [[[-122.34,47.61],[-122.32,47.61],[-122.32,47.59],[-122.34,47.59],[-122.34,47.61]]]
        }
      }
    }
  ]'

aws location get-geofence --collection-name MyGeofences --geofence-id store-001
aws location list-geofences --collection-name MyGeofences
aws location batch-delete-geofence --collection-name MyGeofences --geofence-ids store-001 zone-A

# --- Trackers ---
aws location create-tracker \
  --tracker-name MyDeviceTracker \
  --pricing-plan RequestBasedUsage \
  --position-filtering DistanceBased

aws location create-tracker \
  --tracker-name AccurateTracker \
  --pricing-plan RequestBasedUsage \
  --position-filtering AccuracyBased

aws location list-trackers
aws location describe-tracker --tracker-name MyDeviceTracker
aws location update-tracker \
  --tracker-name MyDeviceTracker \
  --position-filtering TimeBased
aws location delete-tracker --tracker-name MyDeviceTracker

# Associate tracker with geofence collection (enables entry/exit event detection)
aws location associate-tracker-consumer \
  --tracker-name MyDeviceTracker \
  --consumer-arn arn:aws:geo:us-east-1:123456789012:geofence-collection/MyGeofences

aws location list-tracker-consumers --tracker-name MyDeviceTracker
aws location disassociate-tracker-consumer \
  --tracker-name MyDeviceTracker \
  --consumer-arn arn:aws:geo:us-east-1:123456789012:geofence-collection/MyGeofences

# Update device positions
aws location batch-update-device-position \
  --tracker-name MyDeviceTracker \
  --updates '[
    {
      "DeviceId": "device-001",
      "Position": [-122.3321, 47.6062],
      "SampleTime": "2024-01-15T10:30:00Z",
      "PositionProperties": {"Speed": "45.5", "Heading": "90"}
    },
    {
      "DeviceId": "device-002",
      "Position": [-122.4194, 37.7749],
      "SampleTime": "2024-01-15T10:30:00Z"
    }
  ]'

# Get latest position for a device
aws location get-device-position \
  --tracker-name MyDeviceTracker \
  --device-id device-001

# Get position history for a device
aws location get-device-position-history \
  --tracker-name MyDeviceTracker \
  --device-id device-001 \
  --start-time-inclusive "2024-01-15T00:00:00Z" \
  --end-time-exclusive "2024-01-16T00:00:00Z"

# List latest positions for ALL devices in tracker
aws location list-device-positions \
  --tracker-name MyDeviceTracker

# Batch delete device history
aws location batch-delete-device-position-history \
  --tracker-name MyDeviceTracker \
  --device-ids device-001 device-002

# --- API Keys ---
aws location create-key \
  --key-name MyPublicMapKey \
  --restrictions '{
    "AllowActions": ["geo:GetMapTile","geo:GetMapStyleDescriptor","geo:GetMapGlyphs","geo:GetMapSprites"],
    "AllowResources": ["arn:aws:geo:us-east-1:123456789012:map/MyAppMap"],
    "AllowReferers": ["https://myapp.com/*","https://staging.myapp.com/*"]
  }' \
  --expire-time "2027-01-01T00:00:00Z"

aws location list-keys
aws location describe-key --key-name MyPublicMapKey
aws location update-key \
  --key-name MyPublicMapKey \
  --restrictions '{
    "AllowActions": ["geo:GetMapTile","geo:GetMapStyleDescriptor"],
    "AllowResources": ["arn:aws:geo:us-east-1:123456789012:map/MyAppMap"],
    "AllowReferers": ["https://myapp.com/*"]
  }'
aws location delete-key --key-name MyPublicMapKey

# --- Tags ---
aws location tag-resource \
  --resource-arn arn:aws:geo:us-east-1:123456789012:tracker/MyDeviceTracker \
  --tags Environment=production,App=fleet-tracker

aws location list-tags-for-resource \
  --resource-arn arn:aws:geo:us-east-1:123456789012:tracker/MyDeviceTracker

aws location untag-resource \
  --resource-arn arn:aws:geo:us-east-1:123456789012:tracker/MyDeviceTracker \
  --tag-keys Environment
```
