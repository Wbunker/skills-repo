# VLAN & Bandwidth Configuration — OLT3610-08GP4S

## Overview

- [VLAN Configuration](#vlan-configuration)
- [Port Modes](#port-modes)
- [DBA Profiles & Bandwidth](#dba-profiles--bandwidth)
- [GEM Ports & T-CONTs](#gem-ports--t-conts)
- [QoS & Storm Control](#qos--storm-control)

---

## VLAN Configuration

```bash
# Create a VLAN
Switch_config# vlan <VLAN-ID>
Switch_config_vlan<ID># name <NAME>
Switch_config_vlan<ID># exit

# Assign access port (untagged, single VLAN)
Switch_config# interface gigabitethernet 0/X
Switch_config_ge0/X# switchport mode access
Switch_config_ge0/X# switchport access vlan <VLAN-ID>

# Assign trunk port (tagged, multiple VLANs)
Switch_config# interface gigabitethernet 0/X
Switch_config_ge0/X# switchport mode trunk
Switch_config_ge0/X# switchport trunk allowed vlan <VLAN-LIST>
Switch_config_ge0/X# switchport trunk native vlan <PVID>

# Show VLAN assignments
Switch# show vlan
Switch# show interface switchport
```

---

## Port Modes

| Mode | Use Case |
|---|---|
| **Access** | Single untagged VLAN per port; typical for end-user uplinks |
| **Trunk** | Multiple tagged VLANs; use for uplinks to routers/switches |
| **VLAN translation tunnel** | Translate customer VLAN tags to service provider VLANs (QinQ) |
| **VLAN tunnel uplink** | Uplink side of a VLAN tunnel setup |

**Untagged packets** are automatically assigned to the port's PVID (default VLAN).

---

## DBA Profiles & Bandwidth

**DBA (Dynamic Bandwidth Allocation)** controls upstream bandwidth across all ONUs on a PON port per ITU-T G.984 standards.

### DBA Profile Types

| Type | Behavior |
|---|---|
| **Fixed (T1)** | Guaranteed fixed bandwidth; always allocated regardless of demand |
| **Assured (T2)** | Minimum guaranteed bandwidth; unused capacity shared |
| **Non-assured (T3)** | Best-effort; allocated only when PON port has spare capacity |
| **Best-effort (T4)** | Lowest priority; whatever's left |

### Create a DBA Profile

```bash
Switch_config# gpon dba-profile add profile-id <ID> type <TYPE> fix <kbps> assure <kbps> max <kbps>
```

Example — 25 Mbps guaranteed, 50 Mbps max:
```bash
Switch_config# gpon dba-profile add profile-id 10 type 3 fix 0 assure 25000 max 50000
```

### Assign DBA Profile to T-CONT

```bash
Switch_config# interface gpon 0/X
Switch_config_gpon0/X# tcont <TCONT-ID> dba-profile <PROFILE-ID>
```

### Show DBA Profiles

```bash
Switch# show gpon dba-profile
Switch# show gpon tcont interface gpon 0/X
```

---

## GEM Ports & T-CONTs

**GPON bearer hierarchy:**
```
ONU ──> T-CONT (upstream bandwidth container)
         └──> GEM Port (service bearer, tagged by port ID)
               └──> Service (VLAN, voice, video)
```

- **T-CONT**: Upstream bandwidth unit; bound to a DBA profile; one or more per ONU
- **GEM Port**: Carries a specific service; mapped to a T-CONT; identified by GEM Port ID
- **Line Profile**: Defines T-CONT/DBA bindings and GEM port to service mappings per ONU type

```bash
# Show GEM ports on a PON port
Switch# show gpon gem-port interface gpon 0/X

# Show line profiles
Switch# show gpon line-profile
```

---

## QoS & Storm Control

```bash
# Enable storm control on an interface (broadcast)
Switch_config# interface gigabitethernet 0/X
Switch_config_ge0/X# storm-control broadcast level <percent>

# Port isolation (prevent inter-port communication on same VLAN)
Switch_config# port-isolation

# Show QoS policy maps
Switch# show policy-map
Switch# show mls qos
```

**Key QoS features:**
- DBA ensures fair upstream bandwidth sharing across all subscribers
- SLA enforcement per subscriber via T-CONT/DBA profile binding
- Priority queuing on downlink to ONUs
- Storm suppression prevents broadcast storms from impacting the PON
