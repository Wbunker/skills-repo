# Hooks Reference

## Overview

OpenWolf registers six Node.js scripts as Claude Code lifecycle hooks via `.claude/settings.json`. All hooks are pure file I/O — no network calls, no AI inference, no npm dependencies beyond Node stdlib. Hooks warn Claude but never block operations. Each hook has a 5–10 second timeout; failure is silent (hook exits non-zero, Claude continues).

---

## Hook 1: session-start.js

| Property | Value |
|----------|-------|
| Event    | `SessionStart` |
| Fires    | Once, when Claude Code starts a new session |
| Script   | `.wolf/hooks/session-start.js` |

**Behavior:**
1. Reads `OPENWOLF.md` and emits its content to Claude's context (session instructions)
2. Reads `cerebrum.md` and emits it to Claude's context (persistent memory)
3. Reads the anatomy.md summary (or index) and emits it
4. Reads `buglog.json` summary and emits known error patterns
5. Initializes the in-memory session tracker (tracks files read this session)
6. Appends a session-start entry to `memory.md`

**Effect:** Claude begins every session with full knowledge of project conventions, the file index, and past bug fixes — without spending any Read tool calls.

---

## Hook 2: pre-read.js

| Property | Value |
|----------|-------|
| Event    | `PreToolUse` (matcher: `Read`) |
| Fires    | Before every file read |
| Script   | `.wolf/hooks/pre-read.js` |

**Behavior:**
1. Looks up the requested file path in `anatomy.md`
2. If found, emits: `"anatomy.md says <file> is '<description>' at ~<N> tokens"`
3. Checks if the file has already been read this session (via session tracker)
4. If repeated read detected, emits a warning: `"[OpenWolf] Already read <file> this session. Use in-context copy if possible."`

**Effect:** Claude can decide to skip the Read if the anatomy description is sufficient. Repeated-read warnings nudge Claude to reuse in-context content instead of re-reading.

**Does not block:** The Read proceeds regardless; the hook only injects informational text.

---

## Hook 3: pre-write.js

| Property | Value |
|----------|-------|
| Event    | `PreToolUse` (matcher: `Write`) |
| Fires    | Before every file write |
| Script   | `.wolf/hooks/pre-write.js` |

**Behavior:**
1. Reads the Do-Not-Repeat section of `cerebrum.md`
2. Scans for patterns relevant to the file being written (by path and content type)
3. Emits matching Do-Not-Repeat rules as a reminder before the write executes

**Effect:** Reduces correction cycles — Claude sees known mistake patterns before generating code, not after. Pre-write reminder compliance is ~85–90%.

**Does not block:** The Write proceeds regardless.

---

## Hook 4: post-read.js

| Property | Value |
|----------|-------|
| Event    | `PostToolUse` (matcher: `Read`) |
| Fires    | After every successful file read |
| Script   | `.wolf/hooks/post-read.js` |

**Behavior:**
1. Receives the file content (or file size) from the tool result
2. Estimates token count using character-to-token ratio (3.5 for code, 4.0 for prose, 3.75 mixed)
3. Records the read to the session tracker (path + estimated tokens)
4. Appends a log entry to `memory.md`

**Effect:** Builds the per-session read log used by pre-read.js for repeated-read detection. Feeds data into the session summary written by stop.js.

---

## Hook 5: post-write.js

| Property | Value |
|----------|-------|
| Event    | `PostToolUse` (matcher: `Write`) |
| Fires    | After every successful file write |
| Script   | `.wolf/hooks/post-write.js` |

**Behavior:**
1. Re-reads the modified file
2. Updates (or creates) the anatomy.md entry for that file with a fresh description and token estimate
3. Appends a write entry to `memory.md` (path, timestamp, estimated tokens)

**Effect:** Keeps anatomy.md current as files change. Prevents anatomy entries from going stale during a session.

**Atomic writes:** Uses write-then-rename to prevent anatomy.md corruption if interrupted.

---

## Hook 6: stop.js

| Property | Value |
|----------|-------|
| Event    | `Stop` |
| Fires    | When Claude Code ends a session |
| Script   | `.wolf/hooks/stop.js` |

**Behavior:**
1. Reads the session tracker (all reads, writes, repeated reads blocked, anatomy hits/misses)
2. Calculates estimated token savings vs. no-OpenWolf baseline
3. Appends a session entry to `token-ledger.json` with full statistics
4. Optionally emits a session summary to Claude's final output

**Session entry schema (token-ledger.json):**
```json
{
  "sessionId": "2026-04-11T14:30:00Z",
  "reads": 18,
  "writes": 7,
  "anatomyHits": 11,
  "anatomyMisses": 7,
  "repeatedReadsBlocked": 5,
  "estimatedTokensUsed": 42000,
  "estimatedTokensSaved": 31000
}
```

---

## Hook Failure Modes

| Scenario | Behavior |
|----------|----------|
| Hook script not found | Claude Code logs a warning; session continues without hook |
| Hook exits non-zero | Silently ignored; Claude Code continues the tool call |
| Hook timeout (5–10s) | Hook process killed; Claude Code continues |
| `.wolf/` directory missing | Hooks fail on file reads; use `openwolf init` to restore |
| Stale anatomy.md | pre-read.js serves stale descriptions; run `openwolf scan` to refresh |

## Debugging Hooks

Run a hook manually to test it:
```bash
node .wolf/hooks/pre-read.js
```

Check hook registration:
```bash
openwolf status
```

Re-register hooks if `.claude/settings.json` was reset:
```bash
openwolf init
```
`openwolf init` is idempotent — safe to run again on an existing project.
