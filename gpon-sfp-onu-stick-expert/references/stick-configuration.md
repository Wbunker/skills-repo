# GPON SFP ONU Stick CLI Configuration Reference

## Table of Contents
1. [SSH Access](#ssh-access)
2. [GPON Serial Number](#gpon-serial-number)
3. [PLOAM Password](#ploam-password)
4. [LOID Authentication](#loid-authentication)
5. [OMCI Identity (Vendor/Equipment ID)](#omci-identity)
6. [Management IP & Gateway](#management-ip--gateway)
7. [Management MAC Address](#management-mac-address)
8. [SFP Host Interface Speed](#sfp-host-interface-speed)
9. [Reading Current Settings](#reading-current-settings)
10. [Persisting Changes](#persisting-changes)

---

## SSH Access

```bash
ssh ONTUSER@192.168.1.10
# Password: 7sp!lwUBz1
```

The stick's management interface is reachable from the host device it's inserted into. If the host has no route to 192.168.1.10, configure a static IP on the host's interface that connects to the stick (or temporarily add a route: `ip route add 192.168.1.0/24 dev <interface>`).

**Elevate to root:**
```bash
# Already root in most firmware variants — verify with:
whoami
```

---

## GPON Serial Number

The GPON SN identifies the stick to the OLT. Format: 8 hex bytes (4-byte vendor ID + 4-byte serial), e.g., `48575443XXXXXXXX`.

**Read current SN:**
```bash
sfp_i2c -i8
# or
cat /proc/gonst_sn   # if available
```

**Set SN (two equivalent methods):**
```bash
# Method 1 — high-level command
set_serial_number ABCD12345678

# Method 2 — direct I2C write
sfp_i2c -i8 -s "ABCD12345678"
```

> The SN written here must match exactly what is bound on the OLT3610 with `gpon bind-onu sn <SN>`. See olt-registration.md.

**SN format note:** Some OLTs expect the SN in ASCII-prefixed format (`HWTC` + 8 hex) while others expect raw hex. The OLT3610 typically uses raw hex — verify with `show gpon onu` on the OLT.

---

## PLOAM Password

The PLOAM password (up to 10 bytes) is used for OLT-level authentication alongside the SN. Many deployments leave it as all-zeros (default).

**Read current PLOAM password:**
```bash
sfp_i2c -i11
```

**Set PLOAM password:**
```bash
sfp_i2c -i11 -s "1234567890"     # up to 10 chars/bytes
```

**Set PLOAM to all-zeros (default/blank):**
```bash
sfp_i2c -i11 -s "\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
```

> If the OLT3610 uses SN-only authentication (`gpon onu-authen-method sn`), the PLOAM password is not checked. Only set this if OLT uses password authentication.

---

## LOID Authentication

LOID (Logical ONU ID) is an alternative to SN-based authentication used by some OLTs.

**Set LOID:**
```bash
sfp_i2c -i9 -s "my_loid_string"
```

**Set LOID password:**
```bash
sfp_i2c -i10 -s "loid_password"
```

> At Pecan Grove, the OLT3610 uses SN-based auth. LOID is only needed if the OLT is reconfigured to LOID mode.

---

## OMCI Identity

OMCI ME 256 (vendor) and ME 257 (equipment) identify the stick to OLT management systems. Changing these can be required for strict OLT compatibility or to emulate a known ONU model.

**Set Equipment ID (ME 257):**
```bash
sfp_i2c -i6 -s "EQUIPMENT_ID_HERE"    # up to 20 chars
```

**Set Vendor ID (ME 256):**
```bash
sfp_i2c -i7 -s "HWTC"                 # 4-char vendor code, e.g. HWTC = Huawei emulation
```

**Modify hardware version in MIB (for advanced OLT compatibility):**
```bash
sed 's/256 0 HWTC 0000000000000/256 0 HWTC YOUR_VERSION/' \
    /rom/etc/mibs/data_1g_8q.ini > /etc/mibs/data_1g_8q.ini
```

> The OLT3610 with FS firmware typically accepts the default OMCI values. Only change these if the OLT rejects registration with OMCI mismatch errors.

---

## Management IP & Gateway

**Read current settings:**
```bash
fw_printenv ipaddr
fw_printenv gatewayip
```

**Set new management IP:**
```bash
fw_setenv ipaddr 192.168.1.10        # change if 192.168.1.x conflicts with host network
fw_setenv gatewayip 192.168.1.1
```

**Recommended per-stick IP scheme at Pecan Grove:**
Assign each stick a unique management IP to avoid conflicts when multiple sticks are on the same management network. E.g., `192.168.1.11` through `192.168.1.41` for sticks 1–31.

Changes take effect after reboot: `reboot`

---

## Management MAC Address

```bash
# Set LCT (management) MAC
uci set network.lct.macaddr=00:06:B5:07:D6:XX
uci commit network.lct

# Set host (data) MAC
uci set network.host.macaddr=00:06:B5:07:D8:XX
uci commit network.host
```

> Changing MAC is rarely needed. Only required if host network equipment expects a specific MAC or if OLT OMCI provisions based on MAC.

---

## SFP Host Interface Speed

The stick's electrical interface to the host SFP slot can run at 1G (SGMII) or 2.5G (HSGMII).

**Check current mode:**
```bash
onu lanpsg 0
# Returns: 3 = 1G auto-neg | 4 = 1G fixed | 5 = 2.5G HSGMII
```

**Set to 1G (standard — use for most Pecan Grove hosts):**
```bash
fw_setenv sgmii_mode 3
reboot
```

**Set to 2.5G HSGMII (only if host SFP+ port supports multi-gig):**
```bash
fw_setenv sgmii_mode 5
reboot
```

> **Important:** If the host device's SFP port is 1G-only and the stick is set to HSGMII (5), the link will not come up. Default to `sgmii_mode 3`.

---

## Reading Current Settings

```bash
# All U-Boot environment variables (IP, mode settings, etc.)
fw_printenv

# SN
sfp_i2c -i8

# PLOAM password
sfp_i2c -i11

# LOID / LOID password
sfp_i2c -i9 && sfp_i2c -i10

# Vendor ID / Equipment ID
sfp_i2c -i7 && sfp_i2c -i6

# Link speed
onu lanpsg 0

# DOM diagnostics (optical power, temp, voltage)
sfp_i2c -r

# PON registration status
onu ploam_state_g  # or check via OLT: show gpon onu
```

---

## Persisting Changes

- `sfp_i2c` writes persist in flash automatically (EEPROM)
- `fw_setenv` writes persist in U-Boot env partition — survive reboots and firmware upgrades
- `uci` changes: run `uci commit` after each set, then `reboot`
- MIB file edits (`/etc/mibs/`) persist across reboots but NOT across firmware reflash — re-apply after firmware upgrade

**Safe reboot:**
```bash
reboot
```

---

## FS Official Config Guides
- GPON-ONU-34-20BI: https://resource.fs.com/mall/resource/gpon-onu-34-20bi-configuration-guide.pdf
- GPON-SFP-ONT-MAC-I: https://resource.fs.com/mall/resource/gpon-sfp-ont-mac-i-configuration-guide.pdf
- Community reference: https://hack-gpon.org/ont-fs-com-gpon-onu-stick-with-mac/
