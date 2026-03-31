# ONU Stick Registration on OLT3610

> See also: `olt3610-expert` skill for full OLT CLI reference. This file covers the OLT3610 commands specific to registering SFP ONU sticks.

## How Stick Registration Works

The SFP ONU stick behaves identically to a standalone ONU from the OLT's perspective. Registration flow:

1. Stick inserted into host SFP port and powered on
2. SC/APC fiber pigtail connected to PON splitter/distribution fiber
3. Stick transmits SN upstream to OLT
4. OLT3610 matches SN against bound ONUs
5. If matched: ranging completes, stick comes online (PON link established)
6. OLT pushes OMCI service config (VLANs, bandwidth profile)

## Step 1 — Get the Stick SN

**From the stick CLI:**
```bash
ssh ONTUSER@192.168.1.10
sfp_i2c -i8
```

**From the stick label:** SN printed on the SFP body (format: 12 hex chars or 4-char vendor prefix + 8 hex)

**From OLT discovery (if not yet bound):**
```bash
# On OLT3610 — shows all ONUs attempting to register, including unbound
Switch# show gpon onu
```
Unbound sticks appear with SN but no ONU-ID assigned.

## Step 2 — Bind SN on OLT3610

```bash
Switch# config
Switch_config# interface gpon 0/<port>          # PON port serving this fiber run
Switch_config_gpon0/X# gpon onu-authen-method sn
Switch_config_gpon0/X# gpon bind-onu sn <SN>    # e.g., gpon bind-onu sn 48575443AABBCCDD
Switch_config_gpon0/X# exit
Switch_config# wr all
```

> The SN entered here must exactly match `sfp_i2c -i8` output from the stick. Both are case-insensitive hex, but confirm format.

## Step 3 — Verify Stick is Online

```bash
Switch# show gpon onu
Switch# show gpon onu detail <ONU-ID>
```

Confirm:
- State: `Active` or `Online`
- ONU-ID assigned
- RX power: between −8 and −28 dBm

**Check optical signal quality:**
```bash
Switch# show gpon onu optical-info <ONU-ID>
```

## Step 4 — Configure Service VLAN on OLT

Map the stick's ONU-ID to a service VLAN for internet/data forwarding:

```bash
Switch_config# interface gpon 0/<port>
Switch_config_gpon0/X# onu <ONU-ID> service-port <service-port-id> gemport <gemport-id> vlan <vlan-id>
Switch_config_gpon0/X# exit
Switch_config# wr all
```

Typical Pecan Grove service VLAN — check existing ONU configs for the pattern in use:
```bash
Switch# show gpon onu service-port <ONU-ID>
```

## Step 5 — Verify Traffic

From the host device where the stick is installed:
- The SFP interface should now have a link
- Traffic should pass through the GPON uplink
- Check host device's SFP interface: `show interface` (on switches) or `ip link show` (Linux hosts)

## PLOAM Password Authentication (if OLT uses password auth)

If the OLT3610 is configured for password-based ONU authentication:

```bash
# On OLT:
Switch_config_gpon0/X# gpon onu-authen-method password
Switch_config_gpon0/X# gpon bind-onu sn <SN> password <password>

# On stick — must match:
sfp_i2c -i11 -s "<password>"
```

## LOID Authentication (if OLT uses LOID)

```bash
# On OLT:
Switch_config_gpon0/X# gpon onu-authen-method loid
Switch_config_gpon0/X# gpon bind-onu loid <LOID> password <LOID-password>

# On stick:
sfp_i2c -i9 -s "<LOID>"
sfp_i2c -i10 -s "<LOID-password>"
```

## Bandwidth Profile (DBA)

Assign a DBA profile to the stick's ONU-ID on the OLT to enforce fair bandwidth allocation:

```bash
Switch_config_gpon0/X# onu <ONU-ID> dba-profile <profile-name>
```

See `olt3610-expert` → references/vlan-bandwidth.md → "DBA Profiles" for profile creation.

## Removing / Replacing a Stick

To replace a failed stick with a new unit that has a different SN:

```bash
# Remove old binding
Switch_config_gpon0/X# no gpon bind-onu sn <OLD-SN>

# Bind new stick
Switch_config_gpon0/X# gpon bind-onu sn <NEW-SN>
Switch_config# wr all
```

> If replacing with the same physical stick (re-seated), no OLT changes needed — it will re-register automatically on next power-up.
