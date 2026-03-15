# AWS Ground Station — CLI Reference

For service concepts, see [ground-station-capabilities.md](ground-station-capabilities.md).

---

## Ground Stations and Satellites

```bash
# --- List available ground station locations ---
aws groundstation list-ground-stations

aws groundstation get-ground-station \
  --ground-station-id a1b2c3d4-e5f6-7890-abcd-ef1234567890

# --- List registered satellites ---
aws groundstation list-satellites

aws groundstation get-satellite \
  --satellite-id a1b2c3d4-e5f6-7890-abcd-ef1234567890
```

---

## Contacts

```bash
# --- List available contact windows (does not reserve) ---
aws groundstation list-contacts \
  --status-list AVAILABLE \
  --satellite-arn "arn:aws:groundstation:us-east-2:123456789012:satellite/a1b2c3d4-e5f6-7890-abcd-ef1234567890" \
  --mission-profile-arn "arn:aws:groundstation:us-east-2:123456789012:mission-profile/mp-a1b2c3d4e5f67890" \
  --ground-station "arn:aws:groundstation:us-east-2:123456789012:groundstation/gs-a1b2c3d4e5f67890" \
  --start-time "2024-03-15T00:00:00Z" \
  --end-time "2024-03-16T00:00:00Z"

# --- Reserve a specific contact window ---
aws groundstation reserve-contact \
  --satellite-arn "arn:aws:groundstation:us-east-2:123456789012:satellite/a1b2c3d4-e5f6-7890-abcd-ef1234567890" \
  --mission-profile-arn "arn:aws:groundstation:us-east-2:123456789012:mission-profile/mp-a1b2c3d4e5f67890" \
  --ground-station "arn:aws:groundstation:us-east-2:123456789012:groundstation/gs-a1b2c3d4e5f67890" \
  --start-time "2024-03-15T14:30:00Z" \
  --end-time "2024-03-15T14:40:00Z"
  # Returns contactId

# --- List contacts (with status filter) ---
aws groundstation list-contacts \
  --status-list SCHEDULED PASS FAILED_TO_SCHEDULE \
  --start-time "2024-03-01T00:00:00Z" \
  --end-time "2024-03-31T23:59:59Z"

aws groundstation list-contacts \
  --status-list COMPLETED \
  --satellite-arn "arn:aws:groundstation:us-east-2:123456789012:satellite/a1b2c3d4-e5f6-7890-abcd-ef1234567890" \
  --start-time "2024-03-01T00:00:00Z" \
  --end-time "2024-03-31T23:59:59Z"

# --- Describe a specific contact ---
aws groundstation describe-contact \
  --contact-id a1b2c3d4-e5f6-7890-abcd-ef1234567890

# --- Cancel a reserved contact ---
aws groundstation cancel-contact \
  --contact-id a1b2c3d4-e5f6-7890-abcd-ef1234567890
```

---

## Mission Profiles

```bash
# --- Create a mission profile ---
aws groundstation create-mission-profile \
  --name "EarthObservationDownlink" \
  --dataflow-edges '[
    [
      "arn:aws:groundstation:us-east-2:123456789012:config/antenna-downlink/cfg-downlink1a2b",
      "arn:aws:groundstation:us-east-2:123456789012:config/dataflow-endpoint/cfg-endpoint1a2b"
    ]
  ]' \
  --minimum-viable-contact-duration-seconds 60 \
  --tracking-config-arn "arn:aws:groundstation:us-east-2:123456789012:config/tracking/cfg-tracking1a2b" \
  --contact-pre-pass-duration-seconds 120 \
  --contact-post-pass-duration-seconds 60

# For a two-way (uplink + downlink) mission profile
aws groundstation create-mission-profile \
  --name "CommandAndControl" \
  --dataflow-edges '[
    [
      "arn:aws:groundstation:us-east-2:123456789012:config/antenna-downlink/cfg-downlink1a2b",
      "arn:aws:groundstation:us-east-2:123456789012:config/dataflow-endpoint/cfg-endpoint1a2b"
    ],
    [
      "arn:aws:groundstation:us-east-2:123456789012:config/dataflow-endpoint/cfg-endpoint3c4d",
      "arn:aws:groundstation:us-east-2:123456789012:config/antenna-uplink/cfg-uplink1a2b"
    ]
  ]' \
  --minimum-viable-contact-duration-seconds 30 \
  --tracking-config-arn "arn:aws:groundstation:us-east-2:123456789012:config/tracking/cfg-tracking1a2b"

# --- List / describe mission profiles ---
aws groundstation list-mission-profiles

aws groundstation get-mission-profile \
  --mission-profile-id mp-a1b2c3d4e5f67890

# --- Update a mission profile ---
aws groundstation update-mission-profile \
  --mission-profile-id mp-a1b2c3d4e5f67890 \
  --minimum-viable-contact-duration-seconds 90 \
  --contact-pre-pass-duration-seconds 180

# --- Delete a mission profile ---
aws groundstation delete-mission-profile \
  --mission-profile-id mp-a1b2c3d4e5f67890
```

---

## Configs

```bash
# --- Create an antenna downlink config ---
aws groundstation create-config \
  --name "XBandDownlinkConfig" \
  --config-data '{
    "antennaDownlinkConfig": {
      "spectrumConfig": {
        "bandwidth": {"units": "MHz", "value": 30},
        "centerFrequency": {"units": "MHz", "value": 8160},
        "polarization": "RIGHT_HAND"
      }
    }
  }'

# --- Create an antenna downlink demod/decode config ---
aws groundstation create-config \
  --name "XBandDemodDecodeConfig" \
  --config-data '{
    "antennaDownlinkDemodDecodeConfig": {
      "spectrumConfig": {
        "bandwidth": {"units": "MHz", "value": 30},
        "centerFrequency": {"units": "MHz", "value": 8160},
        "polarization": "RIGHT_HAND"
      },
      "demodulationConfig": {
        "unvalidatedJSON": "{\"type\":\"OQPSK\",\"sampleRateKsps\":30000}"
      },
      "decodeConfig": {
        "unvalidatedJSON": "{\"type\":\"BPSK_TURBO\",\"codeRate\":\"1/2\"}"
      }
    }
  }'

# --- Create an antenna uplink config ---
aws groundstation create-config \
  --name "SBandUplinkConfig" \
  --config-data '{
    "antennaUplinkConfig": {
      "spectrumConfig": {
        "centerFrequency": {"units": "MHz", "value": 2067.5},
        "polarization": "LEFT_HAND"
      },
      "targetEirp": {"units": "dBW", "value": 20.0},
      "transmitDisabled": false
    }
  }'

# --- Create a tracking config ---
aws groundstation create-config \
  --name "AutoTrackConfig" \
  --config-data '{
    "trackingConfig": {
      "autotrack": "REQUIRED"
    }
  }'

# Preferred autotrack (falls back to TLE if signal not acquired)
aws groundstation create-config \
  --name "PreferredAutoTrackConfig" \
  --config-data '{
    "trackingConfig": {
      "autotrack": "PREFERRED"
    }
  }'

# --- Create a dataflow endpoint config ---
aws groundstation create-config \
  --name "AgentEndpointConfig" \
  --config-data '{
    "dataflowEndpointConfig": {
      "dataflowEndpointName": "DownlinkEndpoint",
      "dataflowEndpointRegion": "us-east-2"
    }
  }'

# --- Create an uplink echo config ---
aws groundstation create-config \
  --name "UplinkEchoConfig" \
  --config-data '{
    "uplinkEchoConfig": {
      "antennaUplinkConfigArn": "arn:aws:groundstation:us-east-2:123456789012:config/antenna-uplink/cfg-uplink1a2b",
      "enabled": true
    }
  }'

# --- List / describe configs ---
aws groundstation list-configs

aws groundstation get-config \
  --config-id cfg-a1b2c3d4e5f67890 \
  --config-type antenna-downlink   # antenna-downlink | antenna-downlink-demod-decode | antenna-uplink | dataflow-endpoint | tracking | uplink-echo

# --- Update a config ---
aws groundstation update-config \
  --config-id cfg-a1b2c3d4e5f67890 \
  --config-type antenna-downlink \
  --name "XBandDownlinkConfig-Updated" \
  --config-data '{
    "antennaDownlinkConfig": {
      "spectrumConfig": {
        "bandwidth": {"units": "MHz", "value": 40},
        "centerFrequency": {"units": "MHz", "value": 8160},
        "polarization": "RIGHT_HAND"
      }
    }
  }'

# --- Delete a config ---
aws groundstation delete-config \
  --config-id cfg-a1b2c3d4e5f67890 \
  --config-type antenna-downlink
```

---

## Dataflow Endpoint Groups

```bash
# --- Create a dataflow endpoint group (references the Ground Station agent) ---
aws groundstation create-dataflow-endpoint-group \
  --endpoint-details '[
    {
      "endpoint": {
        "address": {
          "name": "10.0.1.100",
          "port": 55888
        },
        "name": "DownlinkEndpoint",
        "status": "created"
      },
      "securityDetails": {
        "roleArn": "arn:aws:iam::123456789012:role/GroundStationAgentRole",
        "securityGroupIds": ["sg-0abcdef1234567890"],
        "subnetIds": ["subnet-0abcdef1234567890"]
      }
    }
  ]' \
  --contact-pre-pass-duration-seconds 120 \
  --contact-post-pass-duration-seconds 60

# --- List / describe dataflow endpoint groups ---
aws groundstation list-dataflow-endpoint-groups

aws groundstation get-dataflow-endpoint-group \
  --dataflow-endpoint-group-id dfeg-a1b2c3d4e5f67890

# --- Delete a dataflow endpoint group ---
aws groundstation delete-dataflow-endpoint-group \
  --dataflow-endpoint-group-id dfeg-a1b2c3d4e5f67890
```

---

## Ephemeris

```bash
# --- Create a TLE ephemeris (customer-provided, higher accuracy than auto-fetched TLE) ---
aws groundstation create-ephemeris \
  --satellite-id "a1b2c3d4-e5f6-7890-abcd-ef1234567890" \
  --name "MySatellite-TLE-2024-03-15" \
  --priority 10 \
  --enabled \
  --ephemeris '{
    "tle": {
      "tle-data": [
        {
          "tle-line-1": "1 25544U 98067A   24075.50000000  .00002182  00000-0  42000-4 0  9993",
          "tle-line-2": "2 25544  51.6416  89.1254 0006063  83.1987  26.9783 15.49589782443577"
        }
      ]
    }
  }'

# --- Create an OEM ephemeris ---
aws groundstation create-ephemeris \
  --satellite-id "a1b2c3d4-e5f6-7890-abcd-ef1234567890" \
  --name "MySatellite-OEM-Precise" \
  --priority 20 \
  --enabled \
  --ephemeris '{
    "oem": {
      "oemData": {
        "s3Object": {
          "bucket": "my-ephemeris-bucket",
          "key": "ephemeris/satellite-oem-2024-03-15.oem",
          "version": "abc123"
        }
      }
    }
  }'

# --- List / describe ephemeris ---
aws groundstation list-ephemerides \
  --satellite-id "a1b2c3d4-e5f6-7890-abcd-ef1234567890" \
  --status-list ENABLED DISABLED \
  --start-time "2024-03-01T00:00:00Z" \
  --end-time "2024-04-01T00:00:00Z"

aws groundstation describe-ephemeris \
  --ephemeris-id eph-a1b2c3d4e5f67890

# --- Enable / disable ephemeris ---
aws groundstation update-ephemeris \
  --ephemeris-id eph-a1b2c3d4e5f67890 \
  --enabled \
  --priority 15

aws groundstation update-ephemeris \
  --ephemeris-id eph-a1b2c3d4e5f67890 \
  --no-enabled

# --- Delete ephemeris ---
aws groundstation delete-ephemeris \
  --ephemeris-id eph-a1b2c3d4e5f67890
```

---

## Tags

```bash
# --- List tags for a resource ---
aws groundstation list-tags-for-resource \
  --resource-arn "arn:aws:groundstation:us-east-2:123456789012:mission-profile/mp-a1b2c3d4e5f67890"

# --- Tag a resource ---
aws groundstation tag-resource \
  --resource-arn "arn:aws:groundstation:us-east-2:123456789012:mission-profile/mp-a1b2c3d4e5f67890" \
  --tags '{"Project": "EarthObservation", "Environment": "Production"}'

# --- Untag a resource ---
aws groundstation untag-resource \
  --resource-arn "arn:aws:groundstation:us-east-2:123456789012:mission-profile/mp-a1b2c3d4e5f67890" \
  --tag-keys '["Project"]'
```
