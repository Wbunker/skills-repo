# Troubleshooting — OLT3610-08GP4S

## Quick Diagnosis Index

- [ONU Not Registering](#onu-not-registering)
- [ONU Online but No Internet](#onu-online-but-no-internet)
- [Optical Power Issues](#optical-power-issues)
- [Rogue ONU Detection](#rogue-onu-detection)
- [Intermittent ONU Drops](#intermittent-onu-drops)
- [OLT Unreachable / Management Loss](#olt-unreachable--management-loss)
- [High Latency / Slow Speeds](#high-latency--slow-speeds)

---

## ONU Not Registering

**Symptoms:** ONU shows `OFFLINE` or never appears in `show gpon onu`

**Step 1 — Check optical power:**
```bash
Switch# show gpon onu optical-info interface gpon 0/X
```
- ONU RX must be **-8 to -27 dBm**
- Below -27 dBm: check fiber connectors, splitter ratios, cable integrity
- Above -8 dBm: add optical attenuator between splitter and ONU

**Step 2 — Check if OLT sees ONU in discovery (unbound):**
```bash
Switch# show gpon onu interface gpon 0/X
```
Look for status `DISCOVER` — ONU is seen but not bound.

**Step 3 — Verify SN binding:**
```bash
Switch# show running-config interface gpon 0/X
```
Confirm `gpon bind-onu sn <SERIAL>` is present. If not, bind it:
```bash
Switch_config# interface gpon 0/X
Switch_config_gpon0/X# gpon onu-authen-method sn
Switch_config_gpon0/X# gpon bind-onu sn <SERIAL_NUMBER>
Switch_config_gpon0/X# exit
Switch_config# wr all
```

**Step 4 — Check PON port state:**
```bash
Switch# show interface gpon 0/X
```
Port must be `up`. If `administratively down`: `no shutdown`

---

## ONU Online but No Internet

1. Verify VLAN config — ONU must be on correct service VLAN
2. Check GEM port mapping and T-CONT DBA profile assignment
3. Verify uplink port VLAN trunking to router/ISP handoff
4. Ping test from OLT: `Switch# ping <gateway-IP>`
5. Check MAC address table for expected entries: `Switch# show mac-address-table`

---

## Optical Power Issues

**Critical range:** ONU RX power = **-8 to -27 dBm**

| Reading | Cause | Fix |
|---|---|---|
| > -8 dBm | Too much signal (fiber too short, no attenuation) | Add optical attenuator |
| -8 to -27 dBm | Normal | No action needed |
| -27 to -30 dBm | Marginal — clean connectors | Clean fiber connectors (IEC 61300-3-35) |
| < -30 dBm | Too weak | Check fiber break, splitter ratio, connector quality |

```bash
Switch# show gpon onu optical-info interface gpon 0/X
```

---

## Rogue ONU Detection

A rogue ONU emits continuous laser light (long-light fault), disrupting all other ONUs on the same PON port.

**Symptoms:**
- Multiple ONUs on one PON port go offline simultaneously
- OLT generates "abnormal long-light" alarm

**Detection:**
```bash
Switch# show alarm
```
Look for long-light or rogue ONU alarms.

**Isolation — binary search method:**
1. Identify the affected PON port from alarms
2. Disconnect one splitter branch at a time; monitor if alarms clear
3. Reconnect branches until rogue branch is identified
4. Within that branch, disconnect ONUs one at a time
5. Replace the identified rogue ONU

**OLT auto-detection:** The OLT3610-08GP4S automatically detects abnormal long-light emissions and raises alarms — check AmpCon-PON or SNMP trap log first.

---

## Intermittent ONU Drops

**Check for optical margin degradation:**
```bash
Switch# show gpon onu optical-info interface gpon 0/X
```
Watch for power levels approaching -27 dBm limit.

**Common causes:**
- Dirty or bent fiber connectors — clean with IEC-compliant kit
- Mechanical stress on fiber (tight bends, pinches)
- Splitter degradation (rare)
- Temperature extremes at outdoor ONUs
- Partial fiber break (fluctuates with temperature)

**Check error counters:**
```bash
Switch# show interface gpon 0/X
```
Look for increasing CRC errors, FEC errors, or packet loss counters.

---

## OLT Unreachable / Management Loss

**Out-of-band (MGMT port):**
- Connect PC directly to MGMT port with matching subnet
- Serial console: 9600 bps, 8N1 as fallback

**In-band management:**
- Verify uplink port is `up/up`: `Switch# show interface`
- Verify IP is assigned: `Switch# show running-config interface <uplink-port>`
- Check routing/firewall between management PC and OLT

**Console recovery:**
1. Connect via USB/serial console (9600 8N1)
2. Restore config or reset if needed

---

## High Latency / Slow Speeds

**Per-subscriber bandwidth:**
1. Check DBA profile assigned to ONU's T-CONT
2. Verify max bandwidth in DBA profile matches subscription tier
3. `Switch# show gpon dba-profile` and `show gpon tcont interface gpon 0/X`

**PON port oversubscription:**
- Max per-port: 2.5 Gbps downstream / 1.25 Gbps upstream
- `Switch# show interface gpon 0/X` — check utilization
- If consistently at capacity, rebalance ONUs across PON ports

**Uplink saturation:**
- `Switch# show interface gigabitethernet 0/X` or `show interface xgigabitethernet 0/X`
- If 10G uplinks are saturated, coordinate upstream bandwidth with ISP

**AmpCon-PON monitoring:**
- Real-time bandwidth, CPU, and memory graphs per device and per ONU
- Historical trending for capacity planning
