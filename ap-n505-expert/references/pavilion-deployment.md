# AP-N505 Pavilion Deployment — Pecan Grove (5 Units)

## Deployment Overview

| Item | Value |
|---|---|
| Total APs | 5 × AP-N505 |
| Location | Pecan Grove RV Park Pavilion (indoor) |
| Mounting | Ceiling-mounted (T-bar or solid ceiling) |
| Coverage per AP | ~15–20 m radius indoors (open hall), ~10–15 m in partitioned spaces |
| Controller | FS AC-1004 |
| PoE source | AC-1004 (4 ports, 802.3af sufficient) + 1 additional port for 5th AP |
| Management | Fit mode via AC-1004 (primary) |

## Pavilion Layout Principles

- **One AP per ~200–400 m² of open floor** for typical mixed-use indoor density
- Place APs centrally above high-activity zones (dining tables, seating areas, stage area)
- Avoid mounting directly above metal roof supports or HVAC ducts — signal shadowing
- With 5 APs in one building, channel reuse will be necessary — plan carefully to avoid co-channel interference

## Channel Plan

### 2.4 GHz (3 non-overlapping channels)
Use only channels **1, 6, 11**. With 5 APs, assign channels to minimize overlap between adjacent units:

```
Suggested assignment (example 5-AP pavilion grid):
  AP-1 (NW corner)     → Ch 1
  AP-2 (NE corner)     → Ch 6
  AP-3 (Center)        → Ch 11
  AP-4 (SW corner)     → Ch 1
  AP-5 (SE corner)     → Ch 6
```

Adjacent APs should never share a channel if they can hear each other (RSSI > −80 dBm).

### 5 GHz Channel Plan

Preferred channels (non-DFS, US):
```
UNII-1: 36, 40, 44, 48
UNII-3: 149, 153, 157, 161
```

With 5 APs, use 5 different channels from this set — good reuse distance indoors.

```
AP-1 → Ch 36
AP-2 → Ch 149
AP-3 → Ch 44
AP-4 → Ch 153
AP-5 → Ch 40
```

### 160 MHz Channel Configuration

The AP-N505 supports **160 MHz** channels on 5 GHz, enabling up to 2402 Mbps on that radio. This is the key performance differentiator vs. 80 MHz (1201 Mbps).

**When to use 160 MHz:**
- Only feasible with 2–3 APs maximum in a space — each 160 MHz block consumes most of the 5 GHz spectrum
- Best for low-density areas (< 20 clients total per AP) needing very high single-client throughput
- For the 5-AP pavilion with many simultaneous clients, **80 MHz is usually better** — more channel separation, less co-channel interference

**160 MHz channel pairs (US):**
```
Block 1: Ch 36+40+44+48 (combined as Ch 36/160)
Block 2: Ch 149+153+157+161 (combined as Ch 149/160)
```

Only 2 non-overlapping 160 MHz blocks available → max 2 APs can use 160 MHz simultaneously without co-channel interference.

**Recommendation for Pavilion:**
- Use **80 MHz** on all 5 APs for balanced performance and interference management
- OR use 160 MHz on 2 APs serving low-density zones; 80 MHz on remaining 3 APs

Configure channel width on AC-1004: **Wireless → AP Groups → Radio Policy → 5G Channel Width**

## TX Power Recommendations

| Band | Setting | Rationale |
|---|---|---|
| 2.4 GHz | 14–17 dBm | Indoor space — lower power reduces co-channel reach to neighbor APs |
| 5 GHz | 17–20 dBm | Balance coverage and inter-AP interference; indoor attenuation is high |

Max TX power is 20 dBm. In a small pavilion with 5 APs, use lower power to shrink cell size and reduce co-channel overlap.

## Adopting APs into AC-1004

### Prerequisites
- Each AP powered via 802.3af PoE (AC-1004 port or external switch)
- AP reachable by AC-1004 on same L2 subnet or via DHCP option 43

### Adoption Steps
1. Power AP via PoE — wait ~90 seconds for boot
2. AP sends CAPWAP discovery; AC-1004 responds
3. AC-1004 web UI → **Wireless → AP Management → Unmanaged APs**
4. Click **Adopt** — AP downloads config profile, reboots into Fit mode (~60 sec)
5. AP appears in **Managed APs** with green status
6. Assign to **AP Group: Pavilion-Indoor** for pavilion-specific radio/SSID profile

### Recommended AP Group for Pavilion

```
AP Group: Pavilion-Indoor
  SSIDs:
    - PecanGrove-WiFi    (WPA2/WPA3, guest access, captive portal or PSK)
    - PecanGrove-Staff   (WPA2-Enterprise or PSK, staff VLAN)
  Radio 2.4G:
    - Channel: manual per plan above
    - Width: 20 MHz
    - Power: 15 dBm
  Radio 5G:
    - Channel: manual per plan above
    - Width: 80 MHz (or 160 MHz for 2 low-density APs)
    - Power: 18 dBm
  Roaming:
    - 802.11k/v/w enabled
    - Band steering: enabled (push 5G-capable clients to 5G)
```

## Roaming in the Pavilion

With 5 APs in close proximity, fast roaming is critical — clients walk between tables and zones continuously.

Enable on AC-1004:
- **802.11k** (neighbor reports) — APs advertise neighbors to clients
- **802.11v** (BSS transition management) — AP steers client to better AP
- **802.11r** (fast BSS transition) — reduces roaming handoff from ~200ms to ~50ms
- Roaming RSSI trigger: −68 dBm (tighter than outdoor; indoor cells are smaller)

## Guest Network Design

```
SSID: PecanGrove-WiFi
  Security: WPA2/WPA3 transition (PSK or open + captive portal)
  VLAN: Guest VLAN (isolated)
  Bandwidth per client: 15–25 Mbps (cap for fair sharing)
  Client isolation: Enabled
  Max clients per SSID per AP: 50–75
```

## Wiring Checklist (Indoor Pavilion)

- [ ] Cat5e or Cat6 (plenum-rated if running through ceiling space)
- [ ] Max run length 100 m per drop
- [ ] 802.3af PoE switch or AC-1004 PoE port for each AP
- [ ] No 802.3at required — standard PoE is sufficient
- [ ] Cable secured to ceiling grid/joists (no hanging slack near HVAC)
- [ ] Test each run with cable tester before AP installation
