# AP-T565 RV Park Deployment — Pecan Grove (27 Units)

## Deployment Overview

| Item | Value |
|---|---|
| Total APs | 27 × AP-T565 |
| Mounting | Pole-mounted, ~4–6 m height |
| Coverage per AP | ~100 m radius (open air), ~40–60 m practical in RV site density |
| Controller | FS AC-1004 (max 64 APs — 27 fits comfortably) |
| PoE source | AC-1004 (4 ports) + supplemental PoE switches |
| Management | Fit mode via AC-1004 (primary); Airware cloud (optional) |

## Site Layout Principles

- **One AP per 4–6 RV sites** is typical for dense RV parks; adjust based on actual site density
- Place poles at row endpoints or midpoints to serve 2–3 rows of sites
- Ensure line-of-sight between AP and RV site — large Class A/Class C RVs (up to 13 ft tall) will shadow 2.4GHz more than 5GHz
- Avoid mounting directly above hookup pedestals (electrical interference) — offset 3–5 m laterally

## Channel Plan

### 2.4 GHz (3 non-overlapping channels)
Use only channels **1, 6, 11**. With 27 APs, each channel is used ~9 times. Adjacent APs should be on different channels.

```
Channel assignment pattern (row-by-row or zone-based):
Zone A → Ch 1
Zone B → Ch 6
Zone C → Ch 11
Zone D → Ch 1  (repeat)
...
```

### 5 GHz (up to 24 non-overlapping 20 MHz channels in UNII-1/2/2e/3)
Recommended channels (US): **36, 40, 44, 48, 149, 153, 157, 161**
With 27 APs, 8-channel rotation gives good reuse distance.

```
Preferred outdoor channels (avoid DFS for simplicity):
UNII-1: 36, 40, 44, 48
UNII-3: 149, 153, 157, 161
```

Avoid DFS channels (52–144) in outdoor deployments unless interference is severe — radar avoidance causes random channel changes.

### Channel Width
- 2.4 GHz: **20 MHz** (do not use 40 MHz — too much co-channel interference in dense deployment)
- 5 GHz: **40 MHz** recommended; use **80 MHz** only in low-density zones where reuse distance is adequate

## TX Power Recommendations

| Band | Setting | Rationale |
|---|---|---|
| 2.4 GHz | 17–20 dBm | Reduce co-channel interference; RV sites are small |
| 5 GHz | 20–23 dBm | Balance coverage and co-channel; 5 GHz attenuates faster |

Avoid max TX power (28 dBm) in dense deployment — "cell breathing" strategy: lower power = smaller cells = less co-channel overlap.

## Adopting APs into AC-1004

### Prerequisites
- Each AP powered via PoE 802.3at on a port reachable to AC-1004
- AC-1004 and APs on same L2 VLAN, or DHCP option 43 configured to point APs to controller IP

### Adoption Steps
1. Power AP via PoE — wait ~2 minutes for boot
2. AP sends CAPWAP discovery to broadcast and/or DHCP option 43 IP
3. On AC-1004: **Wireless** → **AP Management** → **Unmanaged APs** tab
4. Click **Adopt** next to the AP — AP downloads config profile and reboots into Fit mode
5. AP appears in **Managed APs** list with green status within 60–90 seconds
6. Assign AP to correct **AP Group** (e.g., "RVPark-Outdoor") for bulk SSID/radio config

### AP Groups (recommended structure)
```
AP Group: RVPark-Outdoor
  - SSID: PecanGrove-Guest (WPA2/WPA3, captive portal)
  - SSID: PecanGrove-Staff (WPA2-Enterprise or PSK)
  - Radio 2.4G: Ch auto (or manual per zone), 20 MHz, 18 dBm
  - Radio 5G: Ch auto (or manual per zone), 40 MHz, 22 dBm
  - Roaming: 802.11k/v enabled
```

## Roaming Configuration

AP-T565 supports **802.11k** (neighbor reports), **802.11v** (BSS transition management), and **802.11w** (management frame protection). Enable all three for seamless RV guest roaming.

In Fit mode, configure on AC-1004:
- Enable Fast BSS Transition (802.11r) for WPA2-Enterprise; optional for PSK
- Set roaming threshold: RSSI −70 dBm trigger (typical for RV park walking/driving scenarios)
- Enable **Band Steering** to push capable clients to 5 GHz

## Guest Network Design

Typical Pecan Grove guest network structure:

```
SSID: PecanGrove-WiFi
  Security: WPA2/WPA3 transition mode (PSK or open + captive portal)
  VLAN: Guest VLAN (isolated from staff/management)
  Bandwidth limit: 10–25 Mbps per client (configurable on AC-1004)
  Client isolation: Enabled (prevent guest-to-guest traffic)
  Schedule: Always-on (or time-limited for quiet hours if desired)
```

## PoE Switch Layout

AC-1004 provides 4× PoE ports. For 27 APs you need additional PoE switches:

```
AC-1004 (4 PoE ports) → 4 APs direct
PoE Switch #1 (24-port, 802.3at) → 12 APs (rows A-C)
PoE Switch #2 (24-port, 802.3at) → 11 APs (rows D-F)
```

Use managed PoE switches — enables per-port PoE reset to reboot stuck APs remotely.

## Outdoor Cable & Weatherproofing Checklist

- [ ] Outdoor-rated shielded Cat6 (UV/gel-filled) for all pole runs
- [ ] Conduit from pole base to distribution point
- [ ] Weatherproof RJ45 boot on each AP port connection
- [ ] Self-fusing silicone tape wrap on all outdoor connectors
- [ ] Cable drip loops at AP entry point (prevent water ingress via capillary action)
- [ ] Lightning arrestors on Ethernet runs >30 m between buildings/poles
- [ ] Ground all metal pole mounts to site ground bus
