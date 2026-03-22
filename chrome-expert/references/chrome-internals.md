# Chrome Internal URLs & Settings

## chrome:// Pages

| URL | Purpose |
|-----|---------|
| `chrome://settings` | Main settings page |
| `chrome://settings/privacy` | Privacy and security settings |
| `chrome://settings/passwords` | Password manager |
| `chrome://settings/cookies` | Cookie and site data settings |
| `chrome://settings/content` | Site permissions (camera, mic, notifications, etc.) |
| `chrome://settings/privacySandbox` | Privacy Sandbox controls |
| `chrome://flags` | Experimental features (requires restart after change) |
| `chrome://extensions` | Installed extensions manager |
| `chrome://extensions/shortcuts` | Extension keyboard shortcuts |
| `chrome://inspect` | Remote debugging targets (pages, workers, extensions) |
| `chrome://net-internals` | Network diagnostics, DNS cache, HSTS, sockets |
| `chrome://net-internals/#dns` | DNS cache viewer and flush |
| `chrome://net-internals/#hsts` | HSTS preload list query/delete |
| `chrome://webrtc-internals` | WebRTC connection debugging |
| `chrome://gpu` | GPU info, feature status, driver details |
| `chrome://tracing` | Full browser performance tracing (Perfetto) |
| `chrome://version` | Chrome version, revision, command line, paths |
| `chrome://policy` | Enterprise policies applied to this browser |
| `chrome://quota-internals` | Storage quota info per origin |
| `chrome://site-data` | Cookies and storage per site |
| `chrome://memory-internals` | Memory usage breakdown |
| `chrome://histograms` | Internal metrics histograms |
| `chrome://crash` | Intentionally crash the tab (for testing crash reporting) |
| `chrome://dino` | Offline dinosaur game |
| `chrome://components` | Updatable browser components (CRLSets, etc.) |
| `chrome://downloads` | Downloads page |
| `chrome://bookmarks` | Bookmark manager |
| `chrome://history` | Browsing history |
| `chrome://apps` | Installed web apps |
| `chrome://new-tab-page` | New tab page internals |
| `chrome://serviceworker-internals` | All registered service workers |
| `chrome://blob-internals` | Blob URL registry |
| `chrome://indexeddb-internals` | IndexedDB internals |
| `chrome://media-internals` | Media player debugging |
| `chrome://safe-browsing` | Safe Browsing status |
| `chrome://sandbox` | Sandbox status |
| `chrome://signin-internals` | Sign-in and sync debugging |

## chrome://flags — Experimental Features

Flags allow enabling/disabling experimental features before they're fully launched.

- Each flag has: name, description, current state (Default/Enabled/Disabled)
- Changes require a **browser restart**
- Flags may disappear when features ship or are removed

**Useful flags for developers:**

| Flag | Purpose |
|------|---------|
| `#enable-experimental-web-platform-features` | Enable all experimental web platform APIs |
| `#privacy-sandbox-ads-apis` | Enable Privacy Sandbox APIs |
| `#enable-site-per-process` | Site isolation (on by default) |
| `#allow-insecure-localhost` | Skip SSL errors for localhost |
| `#enable-quic` | HTTP/3 via QUIC |
| `#force-dark-mode` | Force dark mode on all pages |
| `#smoothscrolling` | Smooth scrolling animation |

**Search:** Use the search box at top of `chrome://flags` to find by keyword.

**Reset all:** "Reset all" button at top restores all flags to Default.

## Enterprise Policies (chrome://policy)

Policies are enforced by admins via Group Policy (Windows), MDM, or `managed preferences` (Mac/Linux).

```json
// /etc/opt/chrome/policies/managed/policy.json (Linux)
{
  "ExtensionInstallForcelist": ["extension-id;update-url"],
  "DefaultCookiesSetting": 1,
  "HomepageLocation": "https://intranet.example.com"
}
```

View active policies at `chrome://policy`. Policies override user settings.

## Command-Line Flags

Launch Chrome with flags for development/automation:

```bash
google-chrome \
  --remote-debugging-port=9222 \
  --disable-web-security \          # CORS disabled (dev only)
  --user-data-dir=/tmp/chrome-dev \ # separate profile
  --allow-running-insecure-content \
  --ignore-certificate-errors \     # skip SSL errors
  --disable-extensions \
  --incognito \
  --start-maximized \
  --window-size=1920,1080 \
  --proxy-server=socks5://localhost:1080 \
  --disable-background-networking \
  --no-first-run \
  --no-default-browser-check \
  https://example.com
```

**Never use `--disable-web-security` in production or shared profiles.**

## User Data Directory Structure

Default locations:
- **macOS:** `~/Library/Application Support/Google/Chrome/`
- **Linux:** `~/.config/google-chrome/`
- **Windows:** `%LOCALAPPDATA%\Google\Chrome\User Data\`

Key directories/files:
```
Default/
  Preferences          # User settings JSON
  Cookies              # SQLite cookie database
  History              # SQLite browsing history
  Local Storage/       # localStorage per origin
  IndexedDB/           # IndexedDB data
  Cache/               # HTTP cache
  Extensions/          # Installed extension data
  Extension State/     # Extension state (chrome.storage.local)
  Sync Data/           # Chrome sync data
  Local Extension Settings/  # chrome.storage.local data
```

## Site Isolation

Each site runs in its own renderer process, preventing cross-site data leakage (Spectre mitigation).

- Enabled by default on desktop Chrome
- Cross-origin iframes get separate processes
- `chrome://process-internals/` — view process assignments per site

Related flags:
- `#enable-site-per-process` — full site isolation (default on)
- `#enable-strict-extension-isolation` — extensions in own process

## Performance Settings

| Setting | Location |
|---------|----------|
| Memory Saver | `chrome://settings/performance` — discard inactive tabs |
| Energy Saver | `chrome://settings/performance` — reduce background activity |
| Preload pages | `chrome://settings/cookies` — prefetch links |
| Hardware acceleration | `chrome://settings/system` |
