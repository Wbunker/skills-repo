---
name: claude-channels
description: Configure and use Claude Code's Channels feature — connecting Claude Code to external event sources so it can be triggered and respond remotely without the user at the terminal. Use when setting up Telegram or Discord bot integration, wiring CI/monitoring webhooks, or designing always-on background agents that react to external events. Covers BotFather bot setup, bot tokens, long polling mechanics, the --dangerously-skip-permissions tradeoff, and harness patterns for CI triage, monitoring, and async task notification.
---

# Claude Channels

**Status: research preview.** Requires Claude Code 2.1.80+, Bun runtime.

Channels turns Claude Code into a background agent that external systems push events into — Telegram messages, Discord messages, CI webhooks, monitoring alerts. Claude maintains session context across those events. You don't need to be at the terminal.

## Prerequisites

1. Claude Code 2.1.80 or later
2. Bun runtime — install this first, it's the step most people miss:
   ```
   curl -fsSL https://bun.sh/install | bash
   ```

## Quick start (Telegram)

```
/plugin install telegram@claude-plugins-official
# Configure with your bot token when prompted
# Restart Claude Code with: claude --channels
# Send the pairing code to your bot in Telegram
```

To get a bot token: open Telegram, message `@BotFather`, run `/newbot`. See [telegram.md](references/telegram.md) for the full walkthrough and an explanation of what BotFather actually creates.

## Quick start (Discord)

```
/plugin install discord@claude-plugins-official
# Configure with your token from the Discord Developer Portal
# Restart with: claude --channels
```

See [discord.md](references/discord.md) for the Developer Portal walkthrough.

## Critical permission tradeoff

Channels has one fundamental constraint: **Claude Code's approval prompts require physical terminal presence**. Any operation that needs user approval — file writes, shell commands — pauses the session and waits.

| Mode | Remote autonomy | Oversight |
|---|---|---|
| Default | Blocks on every approval | Full human-in-the-loop |
| `--dangerously-skip-permissions` | Fully autonomous | No per-operation approval |

For tightly scoped tasks (read logs, investigate, report back) the default is fine. For autonomous agents that write files or run commands, you must use `--dangerously-skip-permissions`. See [security-and-permissions.md](references/security-and-permissions.md) for the full tradeoff analysis.

## Local testing

Use `fakechat` demo mode to test the push/response loop locally before connecting any external service:
```
claude --channels --fakechat
```

## Teams and Enterprise

Channels is **off by default** for Teams and Enterprise orgs. An admin must explicitly enable it before users can configure channel integrations.

## Reference files

| File | When to read |
|---|---|
| [telegram.md](references/telegram.md) | Setting up Telegram: BotFather, bot tokens, long polling, bot limitations |
| [discord.md](references/discord.md) | Setting up Discord: Developer Portal, bot permissions, invite flow |
| [custom-channels.md](references/custom-channels.md) | Wiring CI webhooks, monitoring alerts, custom event sources |
| [security-and-permissions.md](references/security-and-permissions.md) | Security model, --dangerously-skip-permissions tradeoff, Teams/Enterprise |
| [harness-patterns.md](references/harness-patterns.md) | CI triage, monitoring triage, async task notification — concrete patterns |

## Gotchas

- Install Bun before attempting any plugin install — the plugin runtime depends on it
- A Telegram user must message your bot first before it can initiate conversation (Telegram's design)
- Privacy Mode is on by default in Telegram groups — the bot only sees commands directed at it, not all traffic
- Long polling and webhooks are mutually exclusive in the Telegram Bot API — the plugin uses long polling; don't set a webhook on the same token
- Bot tokens are the sole authentication credential; treat them like passwords (anyone with the token controls the bot)
- The `--channels` flag must be present on restart for Claude Code to begin polling; it does not auto-enable
