# TA1910-4GVC-W Cabin Deployment — Pecan Grove (16 Units)

## Deployment Overview

| Item | Value |
|---|---|
| Total ONUs | 16 (cabins + office/house) |
| One per | Each cabin, office, owner's house |
| Upstream | FS OLT3610-08GP4S (8 PON ports, up to 128 ONUs total) |
| Topology | OLT → PLC splitter → fiber drop → ONU per structure |
| WiFi per structure | Built-in dual-band (2.4G + 5G); no AC-1004 controller involvement |
| IP isolation | Each ONU is its own NAT router — cabin guests are isolated from each other |

## PON Port Assignment (OLT3610)

OLT3610 has 8 PON ports (0–7). With 16 ONUs per-cabin, use a 1:32 splitter or two 1:16 splitters per PON port:

```
Suggested layout:
  PON port 0 → 1:16 splitter → Cabins 01–08  (or subset)
  PON port 1 → 1:16 splitter → Cabins 09–16
  PON port 2 → Office + House (direct or small splitter)
  PON ports 3–7 → spare / expansion
```

Adjust based on actual fiber plant layout and splitter ratio installed at Pecan Grove.

## ONU Naming Convention

Use a consistent naming scheme for OLT binding and web UI hostnames:

| Unit | ONU label | Hostname | SSID |
|---|---|---|---|
| Cabin 01 | ONU-CAB-01 | ta1910-cab-01 | PecanGrove-Cabin-01 |
| Cabin 02 | ONU-CAB-02 | ta1910-cab-02 | PecanGrove-Cabin-02 |
| ... | ... | ... | ... |
| Cabin 15 | ONU-CAB-15 | ta1910-cab-15 | PecanGrove-Cabin-15 |
| Office | ONU-OFFICE | ta1910-office | PecanGrove-Office |
| House | ONU-HOUSE | ta1910-house | PecanGrove-House |

Set hostname: ONU web UI → **Advanced → System Management → Hostname**

## Per-Cabin Network Isolation

Each ONU runs routing mode with NAT. This means:
- Cabin guests get IPs in 192.168.123.0/24 on their ONU's LAN
- All 16 ONUs default to the same LAN subnet — this is **fine** since NAT prevents cross-cabin routing
- Cabin A guests cannot reach Cabin B devices (different NAT domains)
- All cabins share the same upstream OLT PON bandwidth pool

**To prevent cross-cabin management conflicts:**
- Keep default LAN IP (192.168.123.1) on all ONUs — no need to change since subnets are isolated
- If any cabin needs L2 bridging (transparent mode), ensure that cabin's VLAN is isolated on OLT

## WiFi Strategy — Per-Cabin SSIDs

Unlike the campus APs (AP-T565/AP-N505) managed by AC-1004, cabin WiFi is:
- **Standalone** — each ONU manages its own WiFi, no controller
- **Per-cabin SSID** — guests see and connect to their specific cabin's network
- **Not roaming** — guests moving cabin-to-cabin get new SSID/password (intended)

**SSID format:** `PecanGrove-Cabin-<NN>` with unique per-cabin WPA2 password.

**Passphrase strategy options:**
1. Same password across all cabins (simple but less secure — guests can access other cabin SSIDs)
2. Unique password per cabin (recommended — rotate on each guest checkout)
3. Password posted in cabin on welcome card

## WiFi Channel Planning (16 Cabins)

Cabins are separate structures with walls/distance between them — inter-cabin interference is lower than a shared building.

**2.4 GHz:** Use channels 1, 6, 11 in rotation. Adjacent cabins (< 30m apart) should be on different channels:
```
Cabins 01, 04, 07, 10, 13 → Ch 1
Cabins 02, 05, 08, 11, 14 → Ch 6
Cabins 03, 06, 09, 12, 15 → Ch 11
Office, House → Ch 1 or 6
```

**5 GHz:** Auto channel selection is fine for cabin deployment — distance between structures means less co-channel interference. Or manually assign from 36/40/44/48/149/153/157/161.

## Provisioning Checklist (Per Cabin)

Complete these steps for each of the 16 ONUs:

- [ ] Record ONU serial number from label
- [ ] Connect fiber drop cable to PON port (SC/APC)
- [ ] Connect power adapter; verify PWR LED green
- [ ] Wait for PON LED to go solid green (ONU registered on OLT)
- [ ] If PON LED doesn't go solid within 3 min: bind SN on OLT3610 (see olt-registration.md)
- [ ] Connect laptop to LAN1; browse to `http://192.168.123.1`
- [ ] Login admin/super&123; change admin password immediately
- [ ] Set hostname (Advanced → System Management)
- [ ] Configure WAN: routing mode, correct VLAN ID (match OLT service config)
- [ ] Configure SSID: `PecanGrove-Cabin-<NN>`, WPA2-PSK, cabin passphrase
- [ ] Set NTP server: pool.ntp.org
- [ ] Back up config: Advanced → Config Backup → download
- [ ] Test: connect phone/laptop to cabin WiFi → confirm internet access
- [ ] Label ONU with cabin number, SN, and management IP

## Bandwidth Management

Each ONU shares the PON port's upstream bandwidth with other ONUs on the same splitter. OLT3610 DBA (Dynamic Bandwidth Allocation) distributes bandwidth fairly.

**To set per-ONU bandwidth caps on OLT3610:**
See `olt3610-expert` → references/vlan-bandwidth.md → "DBA Profiles"

Recommended starter profile for cabin internet:
- Guaranteed downstream: 10 Mbps
- Max downstream: 50 Mbps
- Guaranteed upstream: 5 Mbps
- Max upstream: 20 Mbps

Adjust based on total backhaul capacity and guest expectations.

## Firmware Consistency

All 16 ONUs should run the same firmware version. Use FS AmpCon-PON for batch upgrades:
- AmpCon-PON → ONU Management → Firmware → Batch Upgrade → select all TA1910-4GVC-W units

Or upgrade individually: ONU web UI → Advanced → Firmware Upgrade → upload `.bin`

Check current firmware: ONU web UI → Status → Device Information → Software Version
