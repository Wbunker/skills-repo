# Authentication & Access Control — AC-1004

## Authentication Methods Summary

| Method | Best for |
|---|---|
| WPA2/WPA3-PSK | Staff/internal networks with a shared password |
| Multi-PSK | Multiple user groups on one SSID with individual passwords |
| 802.1X + RADIUS | Enterprise authentication with per-user credentials |
| Captive Portal (Web Auth) | Guest networks — browser-based login page |
| MAC Auth Bypass | Trusted devices that skip the portal (printers, IoT) |
| Local user database | Small-scale 802.1X or portal auth without external RADIUS |

---

## SSID / WLAN Configuration

```bash
# Create a WLAN (SSID)
Switch_config# wlan <WLAN-ID>
Switch_config_wlan<ID># ssid <SSID-NAME>
Switch_config_wlan<ID># security wpa2-psk
Switch_config_wlan<ID># passphrase <PASSWORD>
Switch_config_wlan<ID># no shutdown
Switch_config_wlan<ID># exit

# Create WPA3 SSID
Switch_config_wlan<ID># security wpa3-psk
Switch_config_wlan<ID># passphrase <PASSWORD>
```

Map the WLAN to a VLAN on the APs (see [vlan-config.md](vlan-config.md)).

---

## Captive Portal / Web Authentication

Used for guest Wi-Fi at Pecan Grove — guests connect to the SSID and are redirected to a login/acceptance page before gaining internet access.

### Web UI Setup
1. **Config → WLAN** → Select guest SSID → Security → Web Authentication
2. Set portal page URL or use the built-in local portal
3. Optionally configure session timeout and idle timeout
4. Enable MAC Auth Bypass for devices that should skip the portal

### CLI Setup
```bash
Switch_config# wlan <WLAN-ID>
Switch_config_wlan<ID># security web-auth
Switch_config_wlan<ID># web-auth portal-url <URL>      # optional custom portal
Switch_config_wlan<ID># web-auth session-timeout <seconds>
Switch_config_wlan<ID># exit
```

### Local portal page
The AC-1004 hosts a built-in captive portal page. Customize via Web UI: Config → Web Auth → Portal Page.

---

## RADIUS Authentication (802.1X or Portal)

```bash
# Define RADIUS server
Switch_config# radius-server host <RADIUS-IP> key <SHARED-SECRET>
Switch_config# radius-server host <RADIUS-IP> auth-port 1812 acct-port 1813

# Apply to WLAN (802.1X)
Switch_config# wlan <WLAN-ID>
Switch_config_wlan<ID># security 802.1x
Switch_config_wlan<ID># radius-server <RADIUS-IP>
Switch_config_wlan<ID># exit

# Verify RADIUS stats
Switch# show radius statistics
```

---

## MAC Authentication Bypass (MAB)

Allows specific devices (printers, smart TVs, IoT) to bypass the captive portal based on their MAC address.

```bash
# Add MAC to local whitelist
Switch_config# mac-auth-bypass mac-address <MAC-ADDRESS> vlan <VLAN-ID>
```

Or configure MAC auth against RADIUS — the MAC address is sent as both the username and password to the RADIUS server.

---

## Multi-PSK

Assign different passwords to different user groups on the same SSID (e.g., residents vs. staff vs. maintenance).

Configure via Web UI: Config → WLAN → select SSID → Security → Multi-PSK → Add entries.

---

## Per-User Bandwidth Control

Limit upload and download speeds per connected client — important for fair use on a shared RV park network.

### Web UI
Config → WLAN → select SSID → Bandwidth Control → set upstream/downstream rate limits (kbps or Mbps)

### CLI
```bash
Switch_config# wlan <WLAN-ID>
Switch_config_wlan<ID># bandwidth-limit upstream <kbps>
Switch_config_wlan<ID># bandwidth-limit downstream <kbps>
Switch_config_wlan<ID># exit
Switch_config# wr
```

---

## Client / Device Isolation

Prevents wireless clients on the same SSID from communicating with each other — recommended for guest networks at Pecan Grove to protect resident devices.

```bash
Switch_config# wlan <WLAN-ID>
Switch_config_wlan<ID># client-isolation enable
Switch_config_wlan<ID># exit
```

Web UI: Config → WLAN → select SSID → Client Isolation → Enable

---

## MAC Blacklist / Whitelist

Block specific devices from connecting, or restrict an SSID to approved devices only.

Web UI: Config → WLAN → select SSID → MAC Filter → Add entries
- **Blacklist:** Deny listed MACs
- **Whitelist:** Only allow listed MACs

---

## Restricting / Disconnecting a User

Web UI: Monitor → Wireless Clients → select client → Kick/Block
- **Kick:** Disconnects the client (can reconnect)
- **Block:** Adds to blacklist, preventing reconnection

```bash
# Disconnect a client by MAC
Switch_config# wireless client disassociate mac-address <MAC-ADDRESS>
```
