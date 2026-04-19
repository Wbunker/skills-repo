# Setup and Architecture

## Requirements

- Node.js 20 or later (required globally even for non-JS projects)
- Claude Code CLI installed and authenticated
- OS: Windows, macOS, or Linux
- Optional: PM2 (for daemon background mode), puppeteer-core (for Design QC screenshots)

## Installation

```bash
npm install -g openwolf
cd your-project
openwolf init
```

`openwolf init` performs these steps:
1. Scans the project directory tree (respecting exclude patterns)
2. Creates the `.wolf/` directory at the project root
3. Generates `anatomy.md` with one-line descriptions and token estimates for each file
4. Creates `cerebrum.md`, `memory.md`, `buglog.json`, `token-ledger.json`, and `config.json` with defaults
5. Creates `identity.md` (project name, AI role, constraints) and `OPENWOLF.md` (session instructions)
6. Writes six hook scripts to `.wolf/hooks/`
7. Registers all six hooks in `.claude/settings.json`

After init, use Claude Code normally — hooks fire invisibly on every action.

## Data Flow

```
Claude Code action
    │
    ├── SessionStart ──► session-start.js
    │       Loads cerebrum.md + anatomy.md into context, initializes session tracker
    │
    ├── PreToolUse (Read) ──► pre-read.js
    │       Surfaces anatomy entry for the file, warns if already read this session
    │
    ├── PostToolUse (Read) ──► post-read.js
    │       Estimates token count from file size, records to session tracker
    │
    ├── PreToolUse (Write) ──► pre-write.js
    │       Checks cerebrum.md Do-Not-Repeat list, surfaces matching rules
    │
    ├── PostToolUse (Write) ──► post-write.js
    │       Updates anatomy entry for the modified file, appends to memory.md
    │
    └── Stop ──► stop.js
            Writes session summary (reads, writes, tokens, savings) to token-ledger.json
```

## Hook Registration

Hooks are entries in `.claude/settings.json` under the `hooks` key. `openwolf init` writes entries like:

```json
{
  "hooks": {
    "SessionStart": [
      { "command": "node .wolf/hooks/session-start.js" }
    ],
    "PreToolUse": [
      { "matcher": "Read",  "command": "node .wolf/hooks/pre-read.js"  },
      { "matcher": "Write", "command": "node .wolf/hooks/pre-write.js" }
    ],
    "PostToolUse": [
      { "matcher": "Read",  "command": "node .wolf/hooks/post-read.js"  },
      { "matcher": "Write", "command": "node .wolf/hooks/post-write.js" }
    ],
    "Stop": [
      { "command": "node .wolf/hooks/stop.js" }
    ]
  }
}
```

If `.claude/settings.json` already exists, `openwolf init` merges the hook entries rather than overwriting.

## Token Estimation Methodology

OpenWolf estimates token counts using character-to-token ratios rather than calling the tokenizer API:

| File Type | Characters per Token |
|-----------|---------------------|
| Code      | 3.5                 |
| Prose     | 4.0                 |
| Mixed     | 3.75                |

Accuracy is within approximately 15% of actual API token counts. Estimates are used for anatomy.md entries, session tracking, and the token-ledger — not billed to the API.

## How Token Savings Accumulate

Three mechanisms produce the measured 65.8% average reduction:

1. **Anatomy short-circuit** — Claude sees the one-line description and token estimate before a Read. If the description is sufficient, Claude skips the full read entirely (anatomy cache hit).
2. **Repeated-read warning** — pre-read.js detects files already read this session and surfaces that fact, nudging Claude to use its in-context copy instead of re-reading.
3. **Cerebrum pre-write check** — pre-write.js reduces correction cycles by reminding Claude of known patterns before it generates incorrect code.

Baseline comparison measured in one large project: ~2.5M tokens (bare Claude CLI) vs ~425K tokens (with OpenWolf hooks).
