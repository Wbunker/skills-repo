# ONU Registration on OLT3610

> See also: `olt3610-expert` skill for full OLT CLI reference. This file focuses on the ONU-side of registration and the OLT commands specific to TA1910-4GVC-W onboarding.

## How XPON Registration Works

The ONU registration process is OLT-initiated and automatic once the ONU is fiber-connected and the SN is bound on the OLT:

1. ONU powers on and sends SN discovery upstream
2. OLT receives SN and compares against bound ONUs
3. If matched: OLT assigns ONU-ID, completes ranging, exchanges passwords
4. ONU comes online (PON LED goes solid green)
5. OLT pushes OMCI config to ONU (VLANs, service mappings)

## Step 1 — Find the ONU Serial Number

The SN is on a label on the bottom or back of the unit (format: 8 hex bytes, e.g., `4244434DF79D0F8C`).

Alternative: connect ONU to OLT fiber and check OLT discovery list before binding:

```bash
Switch# show gpon onu
```

Unbound ONUs appear with SN but no assigned ONU-ID.

## Step 2 — Bind ONU SN on OLT3610

```bash
Switch# config
Switch_config# interface gpon 0/<port>          # port = 0–7 (which PON port serves this cabin)
Switch_config_gpon0/X# gpon onu-authen-method sn
Switch_config_gpon0/X# gpon bind-onu sn <SN>    # e.g., gpon bind-onu sn 4244434DF79D0F8C
Switch_config_gpon0/X# exit
Switch_config# wr all
```

> Replace `<port>` with the PON port number serving the cabin's fiber run. Check the fiber plant diagram to confirm which splitter leg maps to which PON port.

## Step 3 — Verify ONU is Online

```bash
Switch# show gpon onu
Switch# show gpon onu detail <ONU-ID>
```

Confirm:
- State: `Active` or `Online`
- ONU-ID assigned
- Optical Rx power within acceptable range (typical: −8 to −28 dBm)

## Step 4 — Configure ONU Service VLAN on OLT (OMCI)

For each ONU, the OLT pushes service configuration via OMCI. Typical for cabin internet service:

```bash
Switch_config# interface gpon 0/<port>
Switch_config_gpon0/X# onu <ONU-ID> service-port <service-port-id> gemport <gemport-id> vlan <vlan-id>
Switch_config_gpon0/X# exit
Switch_config# wr all
```

For Pecan Grove, typical VLAN assignments:
- Internet service VLAN: per the network design (e.g., VLAN 100 for cabin internet)
- VoIP VLAN: if POTS ports in use (e.g., VLAN 200)

Consult the network design document or check existing ONU configs for the VLAN scheme in use:

```bash
Switch# show gpon onu service-port <ONU-ID>
```

## Step 5 — Verify ONU Web UI is Reachable

After registration, connect a laptop to any LAN port on the ONU:
- Set laptop to DHCP (ONU serves 192.168.123.x by default)
- Browse to `http://192.168.123.1`
- Login: `admin` / `super&123`

If web UI is unreachable after successful PON registration, see troubleshooting.md → "Web UI Not Accessible".

## LOID-Based Authentication (Alternative)

Some deployments use LOID (Logical ONU ID) instead of SN. Configure on OLT:

```bash
Switch_config_gpon0/X# gpon onu-authen-method loid
Switch_config_gpon0/X# gpon bind-onu loid <LOID-string> password <password>
```

And on the ONU web UI: **Advanced → PON Settings → LOID** — enter matching LOID and password.

## OLT-Side Bandwidth Profiles

Set upstream/downstream bandwidth limits per ONU (optional but recommended for fair use):

```bash
Switch_config# gpon profile dba <profile-name>
Switch_config_dba# type 4 max 50000         # 50 Mbps max guaranteed bandwidth
Switch_config_dba# exit
Switch_config# interface gpon 0/<port>
Switch_config_gpon0/X# onu <ONU-ID> dba-profile <profile-name>
```

## OMCI — Remote ONU Management from OLT

Once registered, the OLT can push configuration to the ONU via OMCI without touching the ONU web UI:

```bash
# Check OMCI connection status
Switch# show gpon onu omci <ONU-ID>

# Push WiFi SSID/password via OMCI (if supported by ONU firmware)
# Check FS AmpCon-PON for batch OMCI configuration across all 16 ONUs
```

## TR-069 Remote Provisioning

The ONU supports TR-069 for ACS-based management. Configure on ONU web UI:
**Advanced → TR-069** → enter ACS URL, username, password

This allows remote config push (SSID, passwords, WAN mode) from a central server without visiting each cabin.

## AmpCon-PON Batch Management

FS AmpCon-PON NMS can manage all 16 ONUs simultaneously:
- Batch firmware upgrades
- Centralized fault detection and alarms
- ONU topology view
- Bulk configuration delivery

Reference: `olt3610-expert` skill → Management Interfaces section

## ONU Registration Reference
FS ONU onboarding guide: https://www.fs.com/blog/guide-to-easily-onboarding-configuring-onu-case-of-fs-oltonu-4517.html
