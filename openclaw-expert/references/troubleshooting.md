# Troubleshooting

Common problems, error diagnosis, upgrade issues, and recovery patterns.

## Table of Contents

- [Installation & Startup](#installation--startup)
- [Gateway & Networking](#gateway--networking)
- [Memory & Context](#memory--context)
- [Cron Jobs](#cron-jobs)
- [Agent Crashes](#agent-crashes)
- [Upgrade Issues](#upgrade-issues)
- [Performance](#performance)
- [Recovery Patterns](#recovery-patterns)

---

## Installation & Startup

### Install script fails

```bash
# Check prerequisites
node --version   # Need Node.js 18+
python3 --version

# Manual install if curl fails
git clone https://github.com/openclaw/openclaw.git
cd openclaw && ./install.sh

# Permission issues
chmod +x /usr/local/bin/openclaw
```

### "Config file not found"

```bash
# Verify config location
ls ~/.openclaw/openclaw.json

# Reinitialize if missing
openclaw onboard

# Custom config location
OPENCLAW_HOME=/custom/path openclaw serve
```

### Service won't start

```bash
# Check logs
journalctl -u openclaw -n 50 --no-pager

# Common causes:
# 1. Port already in use
lsof -i :18789
# 2. Invalid JSON in config
python3 -c "import json; json.load(open('$HOME/.openclaw/openclaw.json'))"
# 3. Missing API key
echo $ANTHROPIC_API_KEY
```

## Gateway & Networking

### "Connection refused" on gateway

```bash
# Is the service running?
systemctl status openclaw
# or: docker ps | grep openclaw

# Is it listening on the right interface?
ss -tlnp | grep 18789

# If bound to 127.0.0.1 (correct), you need SSH tunnel for remote access
ssh -L 18789:127.0.0.1:18789 user@your-vps
```

### "Unauthorized" errors

```bash
# Check auth token matches
grep -A2 '"auth"' ~/.openclaw/openclaw.json

# Test with curl
curl -H "Authorization: Bearer your-token" http://127.0.0.1:18789/health
```

### chatCompletions endpoint not working

```json
// Verify this is in openclaw.json
{
  "gateway": {
    "http": {
      "endpoints": {
        "chatCompletions": {
          "enabled": true   // Must be explicitly enabled
        }
      }
    }
  }
}
```

```bash
# Restart after config change
systemctl restart openclaw

# Test endpoint
curl -X POST http://127.0.0.1:18789/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"messages":[{"role":"user","content":"hello"}]}'
```

## Memory & Context

### Agent "forgets" between sessions

**Cause**: Memory files not configured or not loading.

```bash
# Check memory files exist
ls ~/.openclaw/MEMORY.md
ls ~/.openclaw/SOUL.md

# Verify memory is enabled in config
grep -A3 '"memory"' ~/.openclaw/openclaw.json
```

Ensure `SOUL.md` and `MEMORY.md` are in the workspace root or configured path.

### MEMORY.md too large (context overflow)

**Symptoms**: Agent performance degrades, responses become incoherent.

```bash
# Check file size
wc -l ~/.openclaw/MEMORY.md

# Should be < 200 lines
# If larger, run compaction:
```

```yaml
# Manual compaction prompt
prompt: >
  MEMORY.md has grown too large. Consolidate:
  1) Remove outdated entries
  2) Merge duplicate information
  3) Archive details to memory/ subdirectory
  4) Keep MEMORY.md under 200 lines
```

### Context window exhaustion

**Symptoms**: Agent stops mid-task, drops context, hallucinated responses.

**Fixes**:
1. Reduce SOUL.md to 40-60 lines
2. Only load today's + yesterday's daily logs
3. Don't auto-load reference files — use on-demand
4. Split large tasks into smaller, sequential steps

## Cron Jobs

### Jobs not running

```bash
# Check cron system is enabled
grep '"cron"' ~/.openclaw/openclaw.json

# Check job syntax
openclaw cron list
openclaw cron test "morning-brief"   # Dry run

# Check timezone
grep '"timezone"' ~/.openclaw/openclaw.json
# Verify with: date
```

### Jobs running but no output

```bash
# Check where output is being saved
# Review the prompt — does it specify output location?

# Check permissions on output directories
ls -la ~/.openclaw/reports/
ls -la ~/.openclaw/memory/

# Test the prompt manually
openclaw run --prompt "Your cron prompt here"
```

### Overlapping job execution

**Symptom**: Same job runs multiple times concurrently.

**Fix**: Add mutex/cooldown logic:
```yaml
- name: "expensive-job"
  schedule: "0 */2 * * *"
  maxConcurrent: 1              # Only one instance at a time
  timeout: 1800                  # Kill if running > 30 min
  prompt: "..."
```

## Agent Crashes

### Agent unresponsive

```bash
# Check if process is running
ps aux | grep openclaw

# Check resource usage
docker stats openclaw   # Docker
htop                    # VPS

# Restart
systemctl restart openclaw
# or: docker restart openclaw
```

### Agent in error loop

**Symptom**: Agent repeatedly fails the same action.

**Fixes**:
1. Check the AGENTS.md for conflicting rules
2. Review recent memory files for corrupt state
3. Clear the problematic task/state file
4. Restart with a clean BOOT.md recovery

### BOOT.md recovery

```markdown
# Boot Recovery

On restart after a crash:
1. Check: What was I doing before the crash? (Read today's daily log)
2. Assess: Is the interrupted task still valid?
3. If yes: Resume from the last completed step
4. If no: Log the abandoned task and proceed to next priority
5. Run HEARTBEAT.md to verify all systems healthy
```

## Upgrade Issues

### Version upgrade fails

```bash
# Back up before upgrading
tar czf openclaw-pre-upgrade.tar.gz ~/.openclaw/

# Standard upgrade
openclaw update

# If update command fails
curl -fsSL https://openclaw.ai/install.sh | bash

# After upgrade, verify
openclaw --version
openclaw status
```

### Config format changed after upgrade

```bash
# Check for migration notes
openclaw migrate --dry-run

# Apply migrations
openclaw migrate

# If auto-migration fails, check release notes for manual steps
```

### Breaking changes between versions

| Upgrade | Common breakage | Fix |
|---------|----------------|-----|
| 0.7 → 0.8 | Gateway config restructured | Run `openclaw migrate` |
| 0.8 → 0.9 | Cron format changed | Update YAML syntax |
| Any major | Plugins/skills may break | Re-test all cron jobs |

**General upgrade strategy**:
1. Read release notes
2. Back up everything
3. Upgrade on staging/test first
4. Run all cron jobs in dry-run mode
5. Verify memory files load correctly
6. Then upgrade production

## Performance

### Slow responses

| Cause | Diagnosis | Fix |
|-------|-----------|-----|
| Context too large | Check SOUL.md + MEMORY.md line count | Compact memory files |
| VPS under-resourced | `htop` shows high CPU/memory | Upgrade VPS or reduce agents |
| API rate limited | Check API provider dashboard | Add retry/backoff, stagger crons |
| Network latency | `curl -o /dev/null -w "%{time_total}" [url]` | Use closer region VPS |

### High API costs

1. **Audit model usage**: Switch routine tasks from Opus to Sonnet
2. **Reduce cron frequency**: Does error-check need to run every 5 min?
3. **Batch operations**: Combine related checks into single prompts
4. **Add cap gates**: Set daily/weekly spending limits
5. **Monitor with self-monitor job**: Track costs hourly

## Recovery Patterns

### Full state recovery

```bash
# From backup
tar xzf openclaw-backup.tar.gz -C ~/

# Verify files
ls ~/.openclaw/SOUL.md ~/.openclaw/MEMORY.md ~/.openclaw/openclaw.json

# Restart
systemctl restart openclaw
```

### Corrupt memory recovery

```bash
# Check git history if version-controlled
cd ~/.openclaw && git log --oneline MEMORY.md

# Restore from backup
cp /backups/latest/MEMORY.md ~/.openclaw/

# If no backup, recreate from daily logs
# Use manual prompt:
openclaw run --prompt "Reconstruct MEMORY.md from the last 7 daily logs in memory/"
```

### Self-healing pattern

```yaml
- name: "self-heal"
  schedule: "*/30 * * * *"
  prompt: >
    Quick health check: 1) Am I responsive? (you reading this = yes)
    2) Check memory files are valid 3) Check last 3 cron jobs ran
    4) Check disk space > 20% free. If anything is wrong,
    attempt to fix it. If can't fix, alert via Telegram.
```
