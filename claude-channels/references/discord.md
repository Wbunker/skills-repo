# Discord Channel Setup

## Table of Contents
- [How Discord bots differ from Telegram bots](#how-discord-bots-differ-from-telegram-bots)
- [Step-by-step setup](#step-by-step-setup)
- [Bot permissions explained](#bot-permissions-explained)
- [Gateway vs webhooks](#gateway-vs-webhooks)
- [Bot limitations to know](#bot-limitations-to-know)

---

## How Discord bots differ from Telegram bots

Discord bots are registered through the **Discord Developer Portal** (`discord.com/developers/applications`), which serves the same role as Telegram's BotFather — but as a web interface rather than a chat bot.

Key differences from Telegram:

| | Telegram | Discord |
|---|---|---|
| Registration interface | `@BotFather` in Telegram chat | Discord Developer Portal (web UI) |
| Token type | Single bot token | Bot token (under Bot tab) |
| Auth credential format | `<user_id>:<secret>` | Opaque token string |
| Connection model | Long polling (HTTP) | Gateway (WebSocket) |
| Server presence | Bot sent to individual users | Bot "joined" to a server (guild) |
| Permissions | Privacy mode on/off | Granular permission bitfield + OAuth2 scopes |

The biggest architectural difference: Discord uses a persistent **WebSocket Gateway** rather than HTTP polling. Claude Code's Discord plugin manages this connection for you.

---

## Step-by-step setup

### 1. Create an application in the Developer Portal

1. Go to `discord.com/developers/applications`
2. Click **New Application** — enter a name (this is the app name, not the bot username)
3. Navigate to the **Bot** tab in the left sidebar
4. Click **Add Bot** → confirm

This creates a bot user associated with the application. The bot username defaults to the application name.

### 2. Get the bot token

On the Bot tab:
1. Under **Token**, click **Reset Token** (or **Copy** if visible)
2. Copy the token — you will not be able to view it again after leaving the page
3. Store it securely; this is the full credential for the bot

**Important**: The token shown here is what you paste into Claude Code's plugin, not the Application ID or Client Secret.

### 3. Set required permissions and intents

On the Bot tab, enable these **Privileged Gateway Intents** as needed:
- **Message Content Intent** — required for the bot to read message content in servers (not just DMs)
- **Server Members Intent** — only if you need member information
- **Presence Intent** — only if you need online status

Without Message Content Intent, the bot can receive events but cannot read what messages say.

### 4. Invite the bot to your server

1. Go to the **OAuth2 → URL Generator** tab
2. Under **Scopes**, select: `bot`
3. Under **Bot Permissions**, select at minimum:
   - `Read Messages/View Channels`
   - `Send Messages`
   - `Read Message History`
4. Copy the generated URL, open it in a browser, select your server, authorize

The bot now appears in your server's member list (offline until Claude Code connects).

### 5. Install and configure the plugin

```
/plugin install discord@claude-plugins-official
```

When prompted, enter your bot token.

### 6. Start Claude Code with channels enabled

```
claude --channels
```

A pairing code is output to the terminal.

### 7. Pair your Discord account

Send the pairing code to your bot — either in a DM or in a server channel the bot can read. This locks the bot to your specific Discord user ID.

---

## Bot permissions explained

Discord uses a **permission bitfield** — each permission is a bit flag, and the bot's effective permissions in a channel are computed from: server-level role permissions, channel-level overwrites, and the bot's assigned roles.

For Claude Code's typical use:

| Permission | Why needed |
|---|---|
| `Read Messages / View Channels` | See channels and receive events |
| `Send Messages` | Reply to your messages |
| `Read Message History` | Access prior context in a channel |
| `Attach Files` | Send file output (logs, diffs, etc.) |
| `Embed Links` | Send formatted embeds |

You can always add more permissions later via the OAuth2 URL Generator and re-inviting the bot (it updates permissions without removing and re-adding in most cases).

---

## Gateway vs webhooks

Discord uses a **WebSocket Gateway** as its primary real-time connection model — different from Telegram's long polling or webhook pattern.

The Gateway flow:
```
Claude Code plugin → WebSocket connect to Discord Gateway
Discord → sends events (MESSAGE_CREATE, etc.) as they happen
Claude Code → processes events, sends responses via REST API
```

The connection is persistent (unlike HTTP polling) but initiated outbound from your machine — no public endpoint required, same as Telegram long polling.

Discord also supports **Incoming Webhooks** (a separate concept) for posting messages into a channel without a bot user. These are not relevant for the Channels feature, which uses a full bot connection.

---

## Bot limitations to know

**DMs vs server messages**: By default, bots can receive DMs from any user who shares a server with them. For the pairing flow, a DM to the bot works cleanly.

**Message Content Intent**: Without this privileged intent enabled, bots in servers with 100+ members cannot read message content — they receive an empty string. Enable it in the Developer Portal and in Discord's verification process if your server grows.

**Slash commands vs message commands**: Discord has moved toward slash commands (`/`) as the primary interaction model. The Channels plugin communicates via regular messages (the pairing code flow), but if you want to add slash command triggers in the future, they require registering application commands via the API.

**Rate limits**: Discord enforces per-route, per-bot, and global rate limits. For typical Claude Code use (responding to single messages), you're unlikely to hit them. Bulk operations (sending many messages rapidly) can trigger a temporary ban.

**Server count**: Bots in 100+ servers require Discord verification. For personal or team use you're nowhere near this.

**Bot vs user token**: Never use a user account token (your personal Discord login) in place of a bot token. Discord's ToS prohibits user-token automation and accounts can be banned for it.
