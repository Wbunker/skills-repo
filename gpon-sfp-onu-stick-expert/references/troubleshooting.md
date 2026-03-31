# GPON SFP ONU Stick Troubleshooting

## Quick Status Check

From OLT3610:
```bash
Switch# show gpon onu            # List all ONUs with state
Switch# show gpon onu optical-info <ONU-ID>   # RX power for specific stick
```

From stick CLI (if SSH accessible):
```bash
sfp_i2c -r                       # DOM: RX power, TX power, temp, voltage
sfp_i2c -i8                      # Confirm GPON SN
onu lanpsg 0                     # Confirm SFP interface speed mode
```

---

## No PON Registration (Stick Not Appearing on OLT)

**Symptom:** Stick inserted, fiber connected, but OLT shows no ONU online or attempting

**Step 1 — Verify fiber is connected:**
- SC/APC patch cord seated at both stick and wall outlet
- Connector type is SC/APC (green) — NOT SC/UPC (blue)
- No tight bends in fiber near the stick

**Step 2 — Check OLT for unbound discovery:**
```bash
Switch# show gpon onu
```
If stick SN appears as "unbound" or "discovering": bind it (see olt-registration.md → Step 2)

**Step 3 — Verify stick is powered:**
- Host SFP port must provide 3.3V power
- Some SFP ports require the host to explicitly enable power — check host device config
- Try a different SFP slot on the same host

**Step 4 — Check optical power (DOM):**
```bash
ssh ONTUSER@192.168.1.10
sfp_i2c -r      # Look at RX power field
```
- RX power below −28 dBm or `−40 dBm` (no signal): clean connector, check fiber path, verify splitter
- RX power `n/a` or `0`: stick may not be getting fiber signal at all

**Step 5 — Verify SN format matches OLT expectation:**
```bash
sfp_i2c -i8     # Read SN from stick
```
Compare against what's bound on OLT: `show gpon onu` — must match exactly (hex format)

**Step 6 — PLOAM mismatch:**
If OLT uses password auth and passwords don't match, stick appears in discovery but never activates:
```bash
sfp_i2c -i11    # Read PLOAM password on stick
# Must match: gpon bind-onu sn <SN> password <password> on OLT
```

---

## Host Device SFP Port Shows No Link

**Symptom:** Stick inserted but host device shows SFP port as down

1. **Speed mismatch:** Check stick speed mode vs host port capability:
   ```bash
   onu lanpsg 0   # 3=1G, 5=2.5G
   ```
   Host is 1G-only but stick set to 2.5G (mode 5) → set stick to `fw_setenv sgmii_mode 3`

2. **TX Fault signal issue:** The stick shares SFP pins with its serial console. This can cause persistent TX Fault status on some host switches, keeping the port down:
   - Workaround: `fw_setenv asc0 1` (disables serial console, clears TX Fault)
   - Trade-off: serial console no longer available after boot

3. **Host port power not enabled:** Some managed switches require per-port SFP enable — check host switch config

4. **Hot-plug timing:** Wait 60+ seconds after insertion before concluding port is down

---

## SSH Not Reachable (192.168.1.10 Unresponsive)

**Cause 1 — IP conflict or network mismatch:**
- If another device on the host's local network uses 192.168.1.10, there's a conflict
- Try SSHing from the host device directly (not through the network) — host and stick share a local management subnet

**Cause 2 — Wrong interface:**
- The stick's management IP is only reachable via the specific interface the stick is attached to
- On a Linux host: `ssh ONTUSER@192.168.1.10 -I <interface>` or add a route: `ip route add 192.168.1.0/24 dev <sfp-interface>`

**Cause 3 — Multiple sticks at same IP:**
- If multiple sticks default to 192.168.1.10 on the same management network, only one will respond
- Assign unique IPs per stick at initial provisioning (see deployment.md → "Management IP Plan")

**Cause 4 — Stick not booted / powered:**
- No SSH = stick not powered from SFP slot or still booting (boot takes ~30 seconds)

**Cause 5 — Firmware issue:**
- If SSH was working and suddenly stops: power cycle the stick (remove/re-insert from SFP slot)
- If still unresponsive: use serial console (see hardware.md → "Serial Console Access")

---

## Stick Loses PON Registration Intermittently

**Symptom:** OLT shows ONU going offline and online repeatedly

1. **Fiber connection quality:** Clean SC/APC connector on both stick and wall outlet; use connector cleaner pen
2. **Fiber bend radius:** Tight bend (< 30mm) near stick causes intermittent signal loss — re-route pigtail
3. **Optical power marginal:** Check DOM RX power — if near −27 to −28 dBm, marginal; check for splice loss in fiber run
4. **Host SFP slot contact:** Re-seat stick — remove and re-insert firmly
5. **Power instability from host port:** Verify host device firmware supports providing stable 3.3V to SFP

---

## Wrong GPON SN / Stick Won't Register After SN Change

If SN was changed on the stick but OLT still has the old SN bound:

**On OLT3610:**
```bash
Switch_config_gpon0/X# no gpon bind-onu sn <OLD-SN>
Switch_config_gpon0/X# gpon bind-onu sn <NEW-SN>
Switch_config# wr all
```

**On stick — verify new SN took effect:**
```bash
sfp_i2c -i8    # Should show new SN
```

If `set_serial_number` didn't persist: use the I2C method which writes directly to EEPROM:
```bash
sfp_i2c -i8 -s "NEWSERIAL123"
```

---

## Firmware Recovery

**Scenario:** Stick is unresponsive to SSH, serial console shows boot loop, or bad firmware flash.

**Method 1 — Web Serial API (no special hardware needed):**
- Available at: https://hack-gpon.org/ont-fs-com-gpon-onu-stick-with-mac/
- Requires browser with Web Serial API support (Chrome/Edge) and the rootLantiq.js tool
- Can flash new firmware over browser-based serial connection

**Method 2 — U-Boot serial recovery:**
1. Connect to serial console (SFP pins — see hardware.md)
2. Interrupt boot at `Hit any key to stop autoboot` (5-second window)
3. At U-Boot prompt, load new firmware via TFTP or YMODEM:
   ```
   tftp 0x80800000 firmware.img
   nand erase 0x200000 0x800000
   nand write 0x80800000 0x200000 0x800000
   boot
   ```

**Method 3 — Switch active image:**
The stick has dual firmware images. If active image is corrupt, boot from standby:
```bash
# In U-Boot:
fw_setenv committed_image 1   # switch to image 1 (or 0 if currently 1)
boot
```

**Firmware sources:**
- FS official firmware: https://www.fs.com/products_support.html (search GPON-ONU-34-20BI or GPON-SFP-ONT-MAC-I)
- Community firmware variants: https://hack-gpon.org/ont-fs-com-gpon-onu-stick-with-mac/

---

## Checking Stick Status From OLT (No SSH Needed)

When SSH is unavailable, the OLT3610 provides visibility into stick health:

```bash
# Registration state
Switch# show gpon onu detail <ONU-ID>

# Optical signal levels
Switch# show gpon onu optical-info <ONU-ID>

# Force re-registration (triggers OMCI reset)
Switch_config_gpon0/X# onu <ONU-ID> reset

# Check OMCI alarms
Switch# show gpon onu alarm <ONU-ID>
```

---

## FS Support & Resources

- Product page: https://www.fs.com/products/133619.html
- GPON-ONU-34-20BI config guide: https://resource.fs.com/mall/resource/gpon-onu-34-20bi-configuration-guide.pdf
- GPON-SFP-ONT-MAC-I config guide: https://resource.fs.com/mall/resource/gpon-sfp-ont-mac-i-configuration-guide.pdf
- Community wiki (detailed CLI reference): https://hack-gpon.org/ont-fs-com-gpon-onu-stick-with-mac/
- FS support portal: https://www.fs.com/products_support.html
