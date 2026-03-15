# AWS Ground Station — Capabilities Reference

For CLI commands, see [ground-station-cli.md](ground-station-cli.md).

---

## AWS Ground Station

**Purpose**: Fully managed ground station service for communicating with satellites. Provides antenna time for satellite contact scheduling, uplink/downlink operations, and data processing — without requiring you to build or manage ground station infrastructure.

### Core Concepts

| Concept | Description |
|---|---|
| **Ground Station** | A physical antenna facility operated by AWS. 12+ globally distributed locations providing coverage over diverse orbital paths. |
| **Satellite** | A registered satellite object in Ground Station. Identified by NORAD catalog ID; provides orbital TLE (Two-Line Element) data for contact window calculation. |
| **Contact** | A scheduled time window during which an antenna at a ground station communicates with a satellite (AOS to LOS). |
| **AOS (Acquisition of Signal)** | The moment the satellite rises above the antenna's horizon and contact begins. |
| **LOS (Loss of Signal)** | The moment the satellite drops below the horizon and contact ends. |
| **Mission Profile** | A reusable configuration that defines how a contact executes: dataflow graph, tracking configuration, and execution role. |
| **Dataflow Endpoint Group** | A set of endpoint configurations that define where data flows during a contact (e.g., an EC2 instance running the Ground Station agent, or an S3 bucket). |
| **Config** | A named, reusable configuration object used within a mission profile. Types: antenna uplink, antenna downlink, tracking, uplink echo, dataflow endpoint. |

---

## Global Ground Station Network

AWS operates 12+ globally distributed ground stations:

| Region | Locations |
|---|---|
| US East | Fairbanks (Alaska), Cape Canaveral (Florida) |
| US West | Punta Arenas (Chile), Oregon |
| Europe | Dublin (Ireland), Frankfurt (Germany), Stockholm (Sweden) |
| Middle East | Bahrain |
| Asia Pacific | Seoul (Korea), Sydney (Australia), Singapore |

Multi-antenna coverage enables continuous contact windows for polar-orbiting and LEO satellites.

---

## Contact Scheduling

### Reserved Contacts

- Reserve specific contact windows in advance (guaranteed antenna time)
- Specify satellite, ground station location, and time window
- Reserved contacts are billed even if cancelled less than 24 hours before the window

### On-Demand Contacts

- Request contact time without advance reservation
- Subject to availability
- Suitable for lower-priority operations

### Contact Window Calculation

Ground Station computes available windows based on:
- Satellite orbital parameters (TLE data — auto-refreshed from Space-Track.org)
- Ground station antenna elevation constraints
- Contact duration (minimum and maximum)
- Time range to search within

---

## Frequencies Supported

| Band | Downlink Range | Use case |
|---|---|---|
| **S-band** | 2.025–2.120 GHz (uplink), 2.200–2.290 GHz (downlink) | Telemetry, tracking, command (TT&C); Earth observation metadata |
| **X-band** | 8.025–8.400 GHz (downlink) | High-resolution Earth observation imagery; weather data |
| **UHF** | Selected frequencies | Legacy telemetry |

### Wideband DigIF

AWS Ground Station supports a **Wideband Digital Intermediate Frequency (DigIF)** stream for high-throughput downlinks:
- Delivers raw IQ samples directly to the Ground Station agent on an EC2 instance
- Enables custom demodulation and decoding pipeline on-EC2
- Supports bandwidths up to 100 MHz

---

## Agent-Based Architecture

The Ground Station **agent** is software running on an EC2 instance (within the customer VPC) that:
1. Connects to the Ground Station service at the start of a contact
2. Receives decoded data streams (or raw DigIF samples) from the antenna
3. Forwards data to downstream applications (S3, Kinesis, custom processing)
4. Sends uplink commands to the antenna for transmission to the satellite

### Dataflow Pipeline

```
Antenna ──(RF)──> Ground Station Infrastructure
                           │
                    (Demodulation + Decoding in Ground Station)
                           │
                    Ground Station Agent (on EC2 in VPC)
                           │
                    ┌──────┴──────┐
                    │             │
                   S3          Custom App
                (archive)     (real-time processing)
```

For Wideband DigIF:
```
Antenna ──(RF)──> Ground Station Infrastructure ──(raw IQ)──> Agent on EC2 ──> Custom demod/decode
```

---

## Mission Profiles

A mission profile is a reusable template that encapsulates:

| Component | Description |
|---|---|
| **Dataflow edges** | Directed graph: source config → destination config (e.g., antenna downlink → dataflow endpoint) |
| **Tracking config** | Specifies how the antenna tracks the satellite (autotrack or unvalidated TLE) |
| **Contact pre-pass duration** | How many seconds before AOS the antenna begins positioning |
| **Contact post-pass duration** | How many seconds after LOS the contact remains active |
| **Minimum viable contact duration** | Minimum useful contact window length; shorter windows are filtered out |
| **Execution role ARN** | IAM role assumed during contact execution; must have permissions to write to S3 or EC2 within the dataflow |

---

## Configuration Types

| Config Type | Description |
|---|---|
| **AntennaDownlinkConfig** | Specifies receive frequency, bandwidth, polarization, and demodulation/decoding for downlink |
| **AntennaDownlinkDemodDecodeConfig** | Extended downlink config with explicit demodulation and decoding parameters |
| **AntennaUplinkConfig** | Specifies transmit frequency, EIRP, polarization, and modulation for uplink |
| **TrackingConfig** | Autotrack (antenna follows satellite by signal strength) or unvalidated TLE (antenna follows predicted orbital track) |
| **UplinkEchoConfig** | Loopback verification; echoes uplink signal back to the dataflow endpoint for validation |
| **DataflowEndpointConfig** | References a dataflow endpoint group; specifies the Ground Station agent IP/port |

---

## Ephemeris

Ground Station can use **customer-provided ephemeris data** (higher accuracy than public TLE) for contact window computation and antenna pointing:

- Supported formats: **TLE** (Two-Line Element) and **OEM** (Orbit Ephemeris Message, CCSDS format)
- Customer ephemeris takes priority over auto-fetched public TLE when enabled
- Useful for newly launched satellites or classified orbits where TLE accuracy is insufficient

---

## Pricing Model

| Resource | Pricing basis |
|---|---|
| **Reserved antenna time** | Per minute of reserved contact window (billed whether or not satellite establishes link) |
| **On-demand contacts** | Per minute, at a premium over reserved pricing |
| **Data downlink** | Included in per-minute contact pricing (no separate data transfer fee for Ground Station) |

---

## Important Limits & Quotas

| Resource | Limit |
|---|---|
| Contacts per account per day | 50 (adjustable) |
| Mission profiles per account | 100 (adjustable) |
| Configs per account | 1,000 (adjustable) |
| Dataflow endpoint groups per account | 100 (adjustable) |
| Concurrent contacts | 5 (adjustable) |
| Advance reservation window | Up to 28 days |
