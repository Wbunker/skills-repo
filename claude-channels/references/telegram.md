# Telegram Channel Setup

## Table of Contents
- [What BotFather actually creates](#what-botfather-actually-creates)
- [Bot tokens explained](#bot-tokens-explained)
- [Step-by-step setup](#step-by-step-setup)
- [How long polling works](#how-long-polling-works)
- [Bot limitations to know](#bot-limitations-to-know)

---

## What BotFather actually creates

`@BotFather` is itself a Telegram bot — Telegram's official meta-bot for registering and managing bot accounts. It is the only way to create a bot on Telegram's infrastructure.

When you run `/newbot` in BotFather, two things happen:

1. **A new Telegram account is provisioned** on Telegram's servers with a special `is_bot = true` flag. This account gets a user ID, a display name, and a username (must end in `bot`, e.g. `myassistant_bot`). No phone number is required or involved.

2. **A bot token is generated and returned to you.** This is the credential you paste into Claude Code's plugin configuration.

This is meaningfully different from a regular user account:

| | Regular user | Bot account |
|---|---|---|
| Registration | Phone number + SMS/call verification | BotFather only, no phone |
| Authentication | Cryptographic DH key exchange → long-term `auth_key` | Token string in every HTTPS request |
| Protocol | MTProto (binary, encrypted, TCP) | Bot API (HTTPS/JSON) — Telegram handles protocol translation |
| Session model | Stateful session bound to device | Stateless — token is the full credential |

The practical consequence: you can run multiple Claude Code processes against the same bot token simultaneously (stateless auth makes this trivially safe), and revoking the token via BotFather is an instant kill switch.

---

## Bot tokens explained

Token format: `123456789:AAHdqTcvCH1vGWJxfSeofSAs0K5PALDsaw`

- The numeric prefix before the colon **is the bot's Telegram user ID**
- The string after the colon is the secret credential
- The token is embedded directly in every API request URL: `https://api.telegram.org/bot<token>/METHOD_NAME`
- It is stateless — no sessions, no cookies, no OAuth. Each HTTP request is independently authenticated by the token alone.

**Security**: Anyone possessing this token has full control of the bot account. Treat it like a password. Regenerate it via BotFather (`/revoke`) if compromised.

---

## Step-by-step setup

### 1. Create the bot via BotFather

1. Open Telegram, search for `@BotFather`, start a conversation
2. Send `/newbot`
3. Follow prompts: enter a display name, then a username (must end in `bot`)
4. BotFather returns your bot token — copy it

Optional BotFather configuration (run these commands with BotFather):
- `/setdescription` — text shown on the bot's profile page
- `/setabouttext` — text shown in the "About" section
- `/setuserpic` — bot profile photo
- `/setcommands` — register slash commands for autocomplete in chat

### 2. Install and configure the plugin

```
/plugin install telegram@claude-plugins-official
```

When prompted, enter your bot token.

### 3. Start Claude Code with channels enabled

```
claude --channels
```

Claude Code begins long polling the Bot API. A pairing code is output to the terminal.

### 4. Pair your Telegram account

Send the pairing code to your bot in Telegram. This locks the bot to your specific Telegram user ID — messages from any other account will be ignored.

### 5. Test

Send a message to your bot in Telegram. Claude Code should respond.

For local testing before this step, use `claude --channels --fakechat`.

---

## How long polling works

The Bot API offers two ways to receive updates: webhooks and long polling. Claude Code uses **long polling** because it runs locally with no public HTTPS endpoint.

The flow:

```
Claude Code → GET https://api.telegram.org/bot<token>/getUpdates?timeout=30&offset=N
                    ↑ Telegram holds the connection open (up to 30 seconds)
User sends message → Telegram returns the update as JSON
Claude Code processes → immediately issues next getUpdates call
```

The `offset` parameter is deduplication: setting `offset = last_update_id + 1` marks all prior updates as consumed. Telegram will not re-send them.

Key properties:
- Updates are buffered server-side for up to 24 hours if not retrieved
- If Claude Code is offline, messages queue up and deliver when polling resumes
- No inbound ports are opened on your machine — all connections are outbound to `api.telegram.org`
- Long polling and webhooks are **mutually exclusive** — don't register a webhook on the same token

---

## Bot limitations to know

These are Telegram's constraints on bot accounts, not Claude Code limitations:

**Initiating conversations**: A user must message the bot first before it can send them anything. The bot cannot cold-message arbitrary users.

**Group privacy mode**: On by default. In groups, the bot only sees:
- Commands explicitly addressed to it (`/command@botname`)
- Replies to its own messages
- Messages containing its @mention

It does not see general group traffic. Disable privacy mode via BotFather (`/setprivacy`) to change this — requires removing and re-adding the bot to the group.

**Other bots' messages**: Bots cannot read messages sent by other bots in groups, regardless of privacy mode. This is a Telegram-level restriction to prevent infinite loops.

**File limits** (Bot API defaults):
- Upload: 50 MB
- Download via `getFile`: 20 MB

**Rate limits**:
- 1 message/second per individual chat
- 20 messages/minute to any single group
- ~30 messages/second for broadcast scenarios

These limits apply to outgoing messages from Claude Code via the bot. Incoming messages from users are not rate-limited.
