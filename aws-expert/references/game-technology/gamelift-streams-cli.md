# Amazon GameLift Streams — CLI Reference

For service concepts, see [gamelift-streams-capabilities.md](gamelift-streams-capabilities.md).

---

## Applications

```bash
# --- Create an application ---
aws gameliftstreams create-application \
  --description "MyGame Windows Client" \
  --executable-path "MyGame/Binaries/Win64/MyGame.exe" \
  --application-log-paths '["MyGame/Saved/Logs/"]' \
  --application-source-uri "s3://my-streams-bucket/builds/mygame-client-v3.2.zip"

# --- Get / list applications ---
aws gameliftstreams get-application --identifier app-1a2b3c4d-5678-90ab-cdef-EXAMPLE
aws gameliftstreams list-applications

# --- Update an application ---
aws gameliftstreams update-application \
  --identifier app-1a2b3c4d-5678-90ab-cdef-EXAMPLE \
  --description "MyGame Windows Client v3.3"

# --- Delete an application ---
aws gameliftstreams delete-application --identifier app-1a2b3c4d-5678-90ab-cdef-EXAMPLE
```

---

## Stream Groups

```bash
# --- Create a stream group ---
aws gameliftstreams create-stream-group \
  --description "NA West Stream Group" \
  --default-application-identifier app-1a2b3c4d-5678-90ab-cdef-EXAMPLE \
  --stream-class "gen5n.2xlarge" \
  --desired-capacity '{
    "MinimumDesiredSessions": 2,
    "MaximumDesiredSessions": 20
  }' \
  --locations '[
    {
      "LocationName": "us-west-2",
      "DesiredCapacity": {
        "MinimumDesiredSessions": 2,
        "MaximumDesiredSessions": 10
      }
    }
  ]'

# --- Get / list stream groups ---
aws gameliftstreams get-stream-group --identifier sg-1a2b3c4d-5678-90ab-cdef-EXAMPLE
aws gameliftstreams list-stream-groups

# --- Update stream group capacity ---
aws gameliftstreams update-stream-group \
  --identifier sg-1a2b3c4d-5678-90ab-cdef-EXAMPLE \
  --desired-capacity '{"MinimumDesiredSessions": 5, "MaximumDesiredSessions": 30}'

# --- Add locations to a stream group ---
aws gameliftstreams add-stream-group-locations \
  --identifier sg-1a2b3c4d-5678-90ab-cdef-EXAMPLE \
  --location-configurations '[{"LocationName": "us-east-1", "DesiredCapacity": {"MinimumDesiredSessions": 2, "MaximumDesiredSessions": 10}}]'

# --- Remove locations from a stream group ---
aws gameliftstreams remove-stream-group-locations \
  --identifier sg-1a2b3c4d-5678-90ab-cdef-EXAMPLE \
  --locations us-east-1

# --- Delete a stream group ---
aws gameliftstreams delete-stream-group --identifier sg-1a2b3c4d-5678-90ab-cdef-EXAMPLE
```

---

## Stream Sessions

```bash
# --- Create a stream session ---
aws gameliftstreams create-stream-session \
  --identifier sg-1a2b3c4d-5678-90ab-cdef-EXAMPLE \
  --application-identifier app-1a2b3c4d-5678-90ab-cdef-EXAMPLE \
  --user-id "player-uuid-9876" \
  --client-token "unique-idempotency-token-001"

# --- Get a stream session ---
aws gameliftstreams get-stream-session \
  --stream-group-identifier sg-1a2b3c4d-5678-90ab-cdef-EXAMPLE \
  --identifier session-1a2b3c4d-5678-90ab-cdef-EXAMPLE

# --- List stream sessions for a stream group ---
aws gameliftstreams list-stream-sessions \
  --identifier sg-1a2b3c4d-5678-90ab-cdef-EXAMPLE

# --- List stream sessions across the account ---
aws gameliftstreams list-stream-sessions-by-account

# --- Terminate a stream session ---
aws gameliftstreams terminate-stream-session \
  --stream-group-identifier sg-1a2b3c4d-5678-90ab-cdef-EXAMPLE \
  --identifier session-1a2b3c4d-5678-90ab-cdef-EXAMPLE
```
