---
name: klydoclock-expert
description: Setup, configuration, troubleshooting, and daily use guidance for the Klydoclock — an animated analog clock display device. Use when the user needs help connecting Klydoclock to WiFi (especially Orbi or other mesh networks), getting it on a 2.4GHz network, configuring display settings, using the remote control, managing Klydo content, or diagnosing any Klydoclock problem.
---

# Klydoclock Expert

Klydoclock is a dual HD circular display that shows artist-created looping animations ("Klydos") with functioning analog clock hands overlaid on top. It requires a **2.4 GHz WiFi network** — the single most common setup problem.

## Quick Reference — Load by Task

| Task | Reference |
|------|-----------|
| First-time setup, powering on, initial WiFi connection | [setup.md](references/setup.md) |
| Connecting to Orbi, splitting 2.4/5 GHz, IoT SSID, mesh routers | [network-config.md](references/network-config.md) |
| Remote control buttons, settings menu, changing WiFi, display options | [remote-usage.md](references/remote-usage.md) |
| Klydos, collections, favorites, content cycling, subscription | [content-features.md](references/content-features.md) |
| Won't connect, freezes, remote not working, display issues | [troubleshooting.md](references/troubleshooting.md) |

## Critical Fact — 2.4 GHz Only

**Klydoclock only supports 2.4 GHz WiFi. It cannot connect to 5 GHz.**

Most modern mesh routers (including Orbi) broadcast a single combined SSID across both bands. Klydoclock fails or behaves unpredictably on these combined networks. The user **must** have a 2.4 GHz-only SSID visible before setup will succeed.

→ For Orbi-specific solutions: read **[network-config.md](references/network-config.md)** first.

## Device Basics

- **Display**: Dual circular HD screens, 60 FPS animated artwork + analog clock hands
- **Power**: USB-C, must remain plugged in at all times (not battery powered)
- **Control**: Bluetooth remote only — no mobile app yet (app "coming soon" per vendor)
- **Internet**: Required for first boot; optional after that (clock works offline, no new content)
- **Size**: 30 cm × 19 cm × 8 cm; bent plywood frame + powder-coated aluminum

## Gotchas

- Internet is **required on first boot** — content, time sync, and firmware download at setup. Offline first boot is not supported.
- No mobile app exists. All settings are changed via the physical Bluetooth remote using a scroll-wheel character picker — password entry is slow but works.
- Charge the remote before first use (USB-C, 5V–12V). Red LED = charging, solid blue = ready.
- After initial setup, Klydoclock works offline — it keeps accurate time but won't receive new Klydos or firmware updates.
- Time syncs via NTP over internet. The back knob manually corrects time when offline.
- This is **not** an alarm clock and has no alarm feature.
- Klydos library has ~400–500 animations in practice; vendor marketing claims 1500+ (the remainder are queued/future releases).
