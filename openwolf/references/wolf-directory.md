# .wolf/ Directory Reference

## Core Principle

Markdown is the source of truth for human-readable state. JSON is for machine-readable state only. Edit markdown files freely; do not hand-edit JSON state files (`buglog.json`, `token-ledger.json`, `cron-state.json`) unless you know the schema.

## Directory Layout

```
.wolf/
├── anatomy.md              # File index — descriptions + token estimates
├── cerebrum.md             # Learning memory — preferences, conventions, Do-Not-Repeat
├── memory.md               # Chronological session action log
├── identity.md             # Project name, AI role, constraints
├── OPENWOLF.md             # Per-session instructions loaded by session-start.js
├── config.json             # OpenWolf configuration
├── buglog.json             # Structured bug fix memory
├── token-ledger.json       # Lifetime token usage and session history
├── cron-manifest.json      # Scheduled task definitions
├── cron-state.json         # Cron execution state and dead-letter queue
├── suggestions.json        # AI-generated improvement suggestions
├── designqc-report.json    # Design QC capture metadata
├── reframe-frameworks.md   # UI framework knowledge base (12 frameworks)
├── hooks/
│   ├── session-start.js
│   ├── pre-read.js
│   ├── pre-write.js
│   ├── post-read.js
│   ├── post-write.js
│   └── stop.js
└── designqc-captures/      # JPEG screenshots from openwolf designqc
```

---

## File Details

### anatomy.md

**Purpose:** Project file map. One entry per tracked file with a one-line description and token estimate.

**Format (per entry):**
```
## src/server.ts
Express HTTP server config — ~520 tokens
```

**When updated:** Incrementally by `post-write.js` after every write. Full rescan via `openwolf scan` or automatically every 6 hours by the daemon. Generated fresh by `openwolf init`.

**How it saves tokens:** pre-read.js shows the entry to Claude before a Read. If the description is enough, Claude skips the full read (cache hit). Anatomy hits are tracked in the token ledger.

**Manual edits:** Safe — improve descriptions to make them more useful. Descriptions are used verbatim by the hook.

---

### cerebrum.md

**Purpose:** Persistent learning memory across sessions. Stores corrections, preferences, architecture decisions, and a Do-Not-Repeat list.

**Four sections:**
```markdown
## User Preferences
[coding style, formatting, naming conventions]

## Key Learnings
[project-specific conventions Claude has internalized]

## Do-Not-Repeat
[mistakes with dates and tags — enforced by pre-write.js]

## Decision Log
[technical decisions with rationale]
```

**When updated:** Claude writes to it when you correct it or express a preference. The pre-write hook checks the Do-Not-Repeat section before every write. Weekly AI reflection (via cron) reviews and prunes stale entries.

**Compliance rate:** ~85–90% (not deterministic — depends on Claude following the instruction).

**Manual edits:** Encouraged. Add conventions directly. Remove stale Do-Not-Repeat entries that no longer apply.

---

### memory.md

**Purpose:** Chronological, append-only log of reads and writes within each session.

**Format:** Timestamped entries showing which files were read/written and estimated token costs.

**When updated:** `post-read.js` and `post-write.js` append entries. `session-start.js` writes a session header.

**Use:** Audit trail. Useful for reviewing what Claude touched in a session without replaying the conversation.

---

### identity.md

**Purpose:** Defines the project name, AI agent role, and constraints. Loaded each session.

**When updated:** Set during `openwolf init`. Edit manually to change the agent persona or add project-level constraints.

---

### OPENWOLF.md

**Purpose:** Master instruction file loaded by `session-start.js` at the start of every Claude Code session. Tells Claude how to use the `.wolf/` system — how to read anatomy, update cerebrum, consult buglog, etc.

**When updated:** Managed by OpenWolf. Manual edits persist unless overwritten by `openwolf update`.

---

### config.json

**Purpose:** OpenWolf configuration. See **cli-and-config.md** for full schema.

---

### buglog.json

**Purpose:** Structured bug fix database. Stores error messages, root causes, fix descriptions, and tags.

**Schema per entry:**
```json
{
  "id": "bug-001",
  "error": "Cannot read properties of undefined",
  "rootCause": "Missing null check in response handler",
  "fix": "Added optional chaining: response?.data",
  "tags": ["null-check", "api"],
  "date": "2026-03-15"
}
```

**When updated:** Claude appends entries when resolving bugs (if it follows the instruction). Searchable via `openwolf bug search <term>`.

**Pre-session behavior:** `session-start.js` loads buglog summary so Claude can recognize previously solved errors.

---

### token-ledger.json

**Purpose:** Lifetime token usage statistics broken down by session.

**Tracks per session:**
- Files read and written
- Anatomy cache hits and misses
- Repeated reads blocked
- Estimated tokens consumed
- Estimated tokens saved

**When updated:** `stop.js` writes the session summary when Claude Code stops.

---

### reframe-frameworks.md

**Purpose:** Curated knowledge base covering 12 UI frameworks (shadcn/ui, Aceternity, Magic UI, DaisyUI, HeroUI, Chakra UI, Flowbite, Preline, Park UI, Origin UI, Headless UI, Cult UI) with comparisons and migration prompts.

**Use:** Loaded when discussing UI framework selection or migration. Not loaded by default hooks — reference manually when needed.
