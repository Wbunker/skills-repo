# VLAN Configuration — AC-1004

## Overview

The AC-1004 supports up to **1,000 VLANs**. At Pecan Grove, VLANs segment traffic between residents, guests, staff, and management — keeping networks isolated for security and performance.

---

## Create a VLAN

```bash
Switch_config# vlan <VLAN-ID>
Switch_config_vlan<ID># name <DESCRIPTIVE-NAME>
Switch_config_vlan<ID># exit
Switch_config# wr

# Example
Switch_config# vlan 10
Switch_config_vlan10# name Residents
Switch_config_vlan10# exit
Switch_config# vlan 20
Switch_config_vlan20# name Guests
Switch_config_vlan20# exit
```

---

## WLAN-to-VLAN Mapping

Maps an SSID (WLAN ID) to a VLAN so wireless traffic is tagged correctly.

```bash
# Apply to all APs
Switch_config# ap-config all
Switch_config_apc# radio 1
Switch_config_apc_r1# wlan-vlan-map <WLAN-ID> <VLAN-ID>
Switch_config_apc_r1# exit
Switch_config_apc# exit

# Apply to a specific AP
Switch_config# ap-config ap-name <AP-NAME>
Switch_config_apc# radio 1
Switch_config_apc_r1# wlan-vlan-map <WLAN-ID> <VLAN-ID>
Switch_config_apc_r1# exit
```

**Example — map Resident SSID (WLAN 1) to VLAN 10:**
```bash
Switch_config# ap-config all
Switch_config_apc# radio 1
Switch_config_apc_r1# wlan-vlan-map 1 10
Switch_config_apc_r1# radio 2
Switch_config_apc_r2# wlan-vlan-map 1 10
Switch_config_apc_r2# exit
Switch_config_apc# exit
Switch_config# wr
```

---

## Uplink Port VLAN (Trunk to Router/Switch)

The AC-1004 service port connecting to the upstream router/switch must trunk all VLANs in use.

```bash
# Set uplink port to trunk mode
Switch_config# interface gigabitethernet 0/0
Switch_config_ge0/0# switchport mode trunk
Switch_config_ge0/0# switchport trunk allowed vlan <VLAN-LIST>   # e.g., 10,20,30,100
Switch_config_ge0/0# switchport trunk native vlan <MGMT-VLAN>
Switch_config_ge0/0# exit

# Show VLAN assignments
Switch# show vlan
Switch# show interface gigabitethernet 0/0 switchport
```

---

## Native VLAN Alignment

> **Critical:** The Native VLAN on the AC-1004 uplink port must match the Native VLAN on the upstream switch port. A mismatch causes management connectivity loss.

```bash
# Check current native VLAN
Switch# show interface switchport

# Set native VLAN on uplink
Switch_config_ge0/0# switchport trunk native vlan <VLAN-ID>
```

---

## Guest VLAN Isolation

For the guest network at Pecan Grove, use a dedicated VLAN combined with client isolation to prevent guests from reaching the management network or each other.

**Recommended setup:**
1. Create VLAN 20 (Guests)
2. Create WLAN for guest SSID with captive portal (see [auth-access.md](auth-access.md))
3. Map guest WLAN → VLAN 20
4. Enable client isolation on the guest WLAN
5. On upstream router: route VLAN 20 to internet only (no RFC 1918 access)

---

## Super VLAN / VLAN Aggregation

The AC-1004 supports Super VLAN (VLAN aggregation) for combining multiple subscriber VLANs under a single routed interface. Configure via Web UI: Config → VLAN → Super VLAN.

---

## ACL-Based Traffic Control

ACLs can be applied to VLANs to restrict specific traffic flows (block inter-VLAN routing, restrict ports, etc.).

```bash
# Create an ACL
Switch_config# ip access-list standard <ACL-NAME>
Switch_config_acl# permit <IP> <WILDCARD>
Switch_config_acl# deny any

# Apply ACL to a VLAN interface
Switch_config# interface vlan <VLAN-ID>
Switch_config_vlan<ID># ip access-group <ACL-NAME> in
```

---

## Common VLAN Layout for Pecan Grove

| VLAN | Name | Purpose |
|---|---|---|
| 1 | Management | AC-1004 management access |
| 10 | Residents | Resident Wi-Fi |
| 20 | Guests | Day visitor / guest portal |
| 30 | Staff | Staff/admin network |
| 100 | Uplink | WAN handoff to ISP router |

> Adjust IDs to match your actual network plan.
