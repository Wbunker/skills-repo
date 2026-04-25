# Hermes Agent Troubleshooting

## Diagnostic Commands

```bash
hermes doctor            # Full health check — run this first
hermes config check      # Find options missing after an update
hermes config migrate    # Interactively add missing options
hermes sessions list     # List all past sessions
hermes --continue        # Resume most recent session
```

---

## Common Issues

### "hermes: command not found" after install

```bash
source ~/.bashrc    # or ~/.zshrc
# If still missing, check:
echo $PATH
# Should include ~/.local/bin or wherever hermes was installed
```

### Model not responding / timeout

1. Run `hermes model` — verify provider and model ID are correct
2. Check your API key: `hermes config` — look for missing or wrong key
3. For local Ollama: confirm Ollama is running (`ollama serve`) and model is pulled
4. Increase timeout for slow providers:
   ```yaml
   providers:
     openrouter:
       request_timeout_seconds: 1800
   ```

### "Model context window too small"

Minimum 64K context required. Switch to a model with a larger window:
```bash
hermes model    # Select a 64K+ model
```

### Memory at capacity

The `memory` tool returns an error when full. The agent must consolidate or remove entries:
- Ask the agent: "Consolidate your memory — merge related entries and remove outdated ones"
- Or manually edit `~/.hermes/memories/MEMORY.md`

### Gateway not receiving messages

```bash
hermes gateway status         # Check if gateway process is running
hermes gateway start          # Start if not running
journalctl -u hermes-agent    # Check systemd service logs
cat ~/.hermes/logs/*.log       # Check gateway logs
```

For Telegram: verify bot token and user ID are correct. Test with a direct message to the bot.

### Context files not loading

Verify the file search order: `.hermes.md` → `AGENTS.md` → `CLAUDE.md` → `.cursorrules`

Only the first match in the project directory is loaded. Check that the file is in the correct directory and under 20,000 characters.

### Skills not triggering / agent not using a skill

Skills are indexed by name and description. The agent loads the full skill doc only when the task matches. If a skill isn't loading:
- Check `~/.hermes/skills/` — is the skill file present?
- Review the skill's description for trigger clarity
- Ask the agent directly: "Do you have a skill for X?"

### Docker backend issues

```bash
docker ps                     # Confirm container is running
docker logs hermes-container  # Check container logs
# If container exits immediately, check volume mounts and image availability
```

Ensure `shm_size` is sufficient if running browser automation inside the container.

### Cron jobs not executing

- Verify gateway is running (cron delivery requires an active gateway process)
- Check cron job syntax in `~/.hermes/cron/`
- Ask the agent to list configured cron jobs and verify the schedule

### Prompt injection blocked unexpectedly

If a legitimate context file (AGENTS.md, .cursorrules) is being blocked:
- Review the file for patterns that match injection detection (e.g., phrases like "ignore previous instructions")
- Rewrite ambiguous instructions to be clearly directive rather than override-style

### After `hermes config check` shows missing options

```bash
hermes config migrate    # Adds missing options interactively
# or
hermes setup             # Full re-run of setup wizard
```

---

## Upgrade Path

```bash
# Standard update
cd ~/.hermes  # or wherever hermes was cloned
git pull
hermes config check    # Find new options
hermes config migrate  # Add them
```

After major version updates, run `hermes doctor` to confirm everything is healthy.

---

## Session Recovery

If a session ends unexpectedly mid-task:

```bash
hermes --continue       # Resume from where it left off
hermes -c               # Short form
hermes sessions list    # See all sessions with IDs
```

Memory written during the session persists to disk even if the session crashed — MEMORY.md and USER.md changes survive.

---

## Log Locations

```
~/.hermes/logs/          # Gateway and error logs (secrets auto-redacted)
~/.hermes/state.db       # SQLite session archive (FTS5 searchable)
```

Logs are auto-redacted — API keys and tokens are scrubbed before writing.
