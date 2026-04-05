# Obsidian Sync, Mobile, and Publish

## Table of Contents
1. [Obsidian Sync (official)](#obsidian-sync-official)
2. [Free sync alternatives](#free-sync-alternatives)
3. [iOS and iPadOS app](#ios-and-ipados-app)
4. [Android app](#android-app)
5. [Mobile-optimized workflows](#mobile-optimized-workflows)
6. [Obsidian Publish](#obsidian-publish)

---

## Obsidian Sync (official)

**Price:** $10/month (or $96/year with annual plan).
**What it does:** Syncs your vault across all devices with end-to-end encryption. Includes version history.

**Setup:**
1. Create an Obsidian account at obsidian.md
2. Settings → Sync → Connect → Create new remote vault or connect existing
3. On each device: log in and connect to the same remote vault

**Features:**
| Feature | Details |
|---------|---------|
| End-to-end encryption | Obsidian cannot read your data |
| Version history | Up to 12 months; restore previous versions of any note |
| Selective sync | Exclude specific folders (e.g., `_Attachments/` to save space) |
| Synced settings | Optionally sync themes, plugins, hotkeys across devices |
| Storage | 10 GB per vault |
| Vaults | Up to 5 remote vaults per account |
| Real-time | Near real-time sync; small delay on mobile |

**Selective sync for large vaults:** Settings → Sync → Excluded folders. Useful to exclude large attachment folders on mobile to save storage.

**Syncing plugins:** Settings → Sync → Vault configuration sync → toggle which config types to sync. Usually sync: core plugin settings, community plugin settings, themes, hotkeys. May want to not sync: community plugins themselves (reinstall on each device for correct platform builds).

**Conflict resolution:** If the same note is edited on two devices before sync, Obsidian creates a conflict copy. Check Settings → Sync → View sync log and look for `(conflicted copy)` notes.

---

## Free sync alternatives

### iCloud (Mac + iOS/iPadOS only)
**How:** Store vault in `~/Library/Mobile Documents/iCloud~md~obsidian/Documents/` on Mac — this is the default location when creating a vault from the iOS app.

**Pros:** Built into Apple ecosystem, no setup, free.
**Cons:** Mac + iOS only; can be slow to sync large vaults; occasional conflicts.

**Setup:** On iOS, create new vault → it saves to iCloud automatically. On Mac, open that iCloud folder as vault.

---

### Obsidian Git
**How:** Auto-commits vault to a Git repo on a schedule; syncs via GitHub/GitLab.

**Pros:** Free, versioned history, works on desktop (Mac/Windows/Linux).
**Cons:** Requires Git knowledge; mobile Git is clunky (use Working Copy app on iOS); not true real-time sync.

**Mobile Git workflow:**
- iOS: Use Working Copy app to pull/push changes, then open vault in Obsidian
- Requires manual sync step on mobile — not seamless

**Best for:** Power users comfortable with Git; people who want backup more than seamless sync.

---

### Syncthing
**How:** Open-source peer-to-peer sync. Runs on Mac, Windows, Linux, Android.

**Pros:** Free, no cloud storage required, direct device-to-device sync, no size limits.
**Cons:** Devices must be online simultaneously (or have a relay); iOS not officially supported; setup takes effort.

**Best for:** Desktop + Android users who want free sync.

---

### Dropbox / OneDrive / Google Drive
**How:** Store vault in synced cloud folder.

**Pros:** Free tiers available, familiar.
**Cons:** Not end-to-end encrypted; sync conflicts possible if both devices edit simultaneously; cloud services can see your notes.

**Caution:** Don't run Obsidian on a note while cloud sync is actively uploading — can cause corruption. Wait for sync to complete.

---

### Remotely Save plugin
Community plugin that uses S3, Dropbox, OneDrive, or WebDAV as a sync backend.

**Install:** "Remotely Save" (by fyears). Works on mobile. Good alternative to official Sync if you already pay for Dropbox/OneDrive.

---

## iOS and iPadOS app

**Download:** App Store → "Obsidian - Connected Notes"

**Feature parity vs desktop:** Mostly complete for note-taking. Some limitations:

| Feature | iOS status |
|---------|-----------|
| Core note editing | Full |
| Community plugins | Most work; some desktop-only plugins don't |
| Templater | Works with limitations (no shell commands) |
| Dataview | Full |
| Tasks plugin | Full |
| Canvas | Full |
| Split panes | Available on iPad; limited on iPhone |
| File browser | Full |
| Graph view | Full (slow on large vaults) |
| Hotkeys | Limited (keyboard required for most) |
| External keyboard shortcuts | Full support |
| File attachments from Files/Photos | Supported |
| Drag and drop | iPad only |
| Widgets | Available (quick open, recent notes) |
| Shortcuts (Apple Shortcuts) | Supported for basic actions |

**Toolbar customization (mobile):** Tap the `...` in the bottom toolbar → customize which actions appear. Add: toggle checkbox, bold, italic, link, new note, command palette.

**Quick capture on iOS:**
1. Use the share sheet: Share from Safari/Notes → Obsidian → append to note
2. Obsidian Shortcuts action: create a Shortcut that appends text to Inbox.md
3. QuickAdd plugin's capture command

**Performance:** Large vaults (1000+ notes) can be slow on older iPhones. Consider using selective sync to keep mobile vault smaller.

---

## Android app

**Download:** Google Play Store → "Obsidian"

**Sync options on Android:** Syncthing (best), Obsidian Sync (official), Remotely Save, Dropsync.

**Feature parity:** Similar to iOS. Full plugin support. Better file system access than iOS.

**File location:** On Android, vault is stored in device storage at a user-chosen path. Accessible via Files app or file manager.

---

## Mobile-optimized workflows

### Quick capture workflow
The most important mobile use case — capture a thought without friction.

1. Install QuickAdd plugin on desktop, configure a Capture action to append to `Inbox.md`
2. On mobile: tap the QuickAdd command from the bottom toolbar or command palette
3. Type the thought → tap confirm → it's in your Inbox
4. Total time: 5 seconds

**Even faster with iOS Shortcuts:** Create a Shortcut that:
1. Asks "What do you want to capture?" (Ask for Input)
2. Appends the text + timestamp to `Inbox.md` using the Obsidian URI scheme
3. Add to home screen as an icon — one tap, type, done

**URI scheme for iOS Shortcuts:**
```
obsidian://new?vault=VAULT_NAME&file=Inbox&append=true&content=TEXT
```

### Mobile daily note
- Set Calendar plugin to open daily note on launch
- Keep mobile daily note template minimal (title + top 3 priorities + notes section)
- Elaborate notes on desktop; use mobile for quick entries

### Voice capture
iOS: Use the dictation key on keyboard to voice-to-text directly into Obsidian. Works for quick notes and journaling.

### Reading on mobile
- Use Reading View for distraction-free reading of long notes
- Adjust font size: Settings → Editor → Font size
- Enable "Readable line length" for better readability on wide screens

---

## Obsidian Publish

**Price:** $20/month (or $192/year).
**What it does:** Hosts selected vault notes as a public website.

**Setup:**
1. Enable Publish in Settings → Core Plugins
2. Open Publish dialog (ribbon icon or command)
3. Select notes to publish (individual notes or folders)
4. Choose a site name (yoursite.obsidian.site subdomain free; custom domain available)

**Features:**
| Feature | Details |
|---------|---------|
| Custom domain | Point your own domain to the Publish site |
| Navigation | Auto-generated sidebar from folder structure |
| Graph view | Interactive graph on the published site |
| Search | Full-text search of published notes |
| Backlinks | Show backlinks on each page |
| Themes | Use your vault theme or default |
| Custom CSS | Upload CSS snippets for styling |
| Password protection | Protect entire site or individual notes |
| Analytics | Basic page view stats |
| Selective publishing | Publish exactly which notes you choose |

**Controlling what's published:**
- Only notes you explicitly select are published
- Set `publish: true` in frontmatter to auto-include
- Set `publish: false` to explicitly exclude a note even if its folder is selected

**Use cases:**
- Digital garden / public notes
- Personal website / blog
- Documentation for a project
- Portfolio of writing
- Public knowledge base

**Not suitable for:** Private notes, large media files (storage limits), dynamic content (Dataview queries don't render on Publish).

**Alternatives to Obsidian Publish:**
- **Quartz** (free, self-hosted, open source — most popular alternative)
- **Jekyll/Hugo with GitHub Pages** (free, more technical)
- **MkDocs** (good for documentation sites)
- **Digital Garden plugin** (publish to Netlify/Vercel, free)
