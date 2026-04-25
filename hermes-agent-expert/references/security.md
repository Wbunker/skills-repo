# Hermes Agent Security

## Command Approval System

Three modes controlling dangerous command execution:

| Mode | Behavior |
|---|---|
| `manual` (default) | Always prompt user before dangerous commands |
| `smart` | Auxiliary LLM assesses risk; auto-approves low-risk, auto-denies high-risk, escalates ambiguous |
| `off` | No safety checks |

```yaml
approvals:
  mode: manual
```

**Fail-closed:** Approval requests timeout after 60 seconds — unanswered = denied.

**YOLO mode** bypasses approval entirely:
- CLI flag: `--yolo`
- Slash command: `/yolo`
- Env var: `HERMES_YOLO_MODE=1`

### Dangerous Command Patterns (always require approval in non-container backends)

- Recursive deletion: `rm -r`
- Unsafe permissions: `chmod 777`
- Filesystem formatting: `mkfs`
- SQL destructive ops: `DROP TABLE`, `TRUNCATE`
- System file overwrites: `> /etc/`
- Pipe attacks: `curl | sh`
- Interpreter execution flags

**Exception:** When running in `docker`, `singularity`, `modal`, or `daytona` backends, dangerous command checks are **skipped** — the container is the security boundary.

---

## Docker Hardening

Hermes applies hardened Docker defaults:

```bash
--cap-drop ALL
--cap-add DAC_OVERRIDE,CHOWN,FOWNER
--security-opt no-new-privileges
--pids-limit 256
--tmpfs /tmp,/var/tmp,/run:size=100m,noexec
```

Resource limits (configurable):
```yaml
terminal:
  container_cpu: 1
  container_memory: 5120    # MB (default 5GB)
  container_persistent: true
```

---

## Gateway Authorization

Multi-layered check order (first match wins):

1. Platform-specific allow-all flag (avoid in production)
2. DM pairing approved list
3. Platform-specific allowlists (user IDs)
4. Global allowlists
5. Global allow-all setting
6. **Default: deny**

### DM Pairing

The recommended way to authorize new users:
- Issues an 8-character code with 1-hour TTL
- Rate-limited: 1 request per user per 10 minutes
- 5 failed approval attempts → 1-hour lockout

```yaml
privacy:
  unauthorized_dm_behavior: pair   # pair (issue code) or ignore
```

**Production rule:** Always use explicit user allowlists. Never set `GATEWAY_ALLOW_ALL_USERS=true`.

---

## Credential Protection

### Environment Variable Filtering

`execute_code` and `terminal` tools block env vars with these substrings in their names:
`KEY`, `TOKEN`, `SECRET`, `PASSWORD`, `CREDENTIAL`, `PASSWD`, `AUTH`

To allow a specific credential through for a legitimate skill:
```yaml
# In the skill's declaration
required_environment_variables:
  - GITHUB_TOKEN
```

### MCP Subprocess Isolation

Only these safe variables pass to MCP servers: `PATH`, `HOME`, `USER`, `LANG`, `SHELL`, `TMPDIR`, `XDG_*`

Explicitly configured vars in `env:` config block are exceptions.

### Credential File Mounting

Skills can declare `required_credential_files` — files are mounted **read-only** into containers (not copied).

---

## Prompt Injection Protection

Context files (AGENTS.md, .cursorrules, external web content) are scanned before injection:

- Instructions to disregard prior guidance
- Hidden suspicious HTML comments
- Credential exfiltration patterns
- Invisible Unicode characters (zero-width, homoglyphs)

Matched content is blocked before it reaches the model.

---

## SSRF Protection

URL-capable tools validate addresses against blocked ranges:
- RFC 1918 private networks (10.x, 172.16-31.x, 192.168.x)
- Loopback (127.x, ::1)
- Link-local (169.254.x)
- Cloud metadata endpoints (169.254.169.254, etc.)
- Reserved addresses

DNS failures are treated as blocked (fail-closed).

---

## Tirith Integration

Pre-execution scanning layer that detects:
- Homograph URL spoofing
- Pipe-to-interpreter patterns (`curl | bash`)
- Terminal injection attacks

```yaml
security:
  tirith_enabled: true
  tirith_path: "tirith"
  tirith_timeout: 5
  tirith_fail_open: true    # Allow execution if Tirith is unavailable
```

---

## Supply Chain: Hermes vs OpenClaw

OpenClaw's ClawHub marketplace had 1,184 confirmed malicious skills (~1 in 5 at peak), with 138 CVEs over 63 days in early 2026 (including a CVSS 9.9 privilege escalation).

Hermes's approach:
- Agent generates skills internally from **observed successes in your environment**
- No pulling executable code from public registries authored by anonymous contributors
- Community skills from agentskills.io are **scanned and quarantined** before activation
- Audit log at `.hub/audit.log`

---

## Production Security Checklist

- [ ] Use `docker`, `modal`, or `daytona` backend (never `local` for gateway)
- [ ] Set explicit user allowlists — never `GATEWAY_ALLOW_ALL_USERS=true`
- [ ] Use DM pairing for new user onboarding
- [ ] Run Hermes as non-root user
- [ ] Set `security.redact_secrets: true`
- [ ] `chmod 600 ~/.hermes/.env`
- [ ] Enable `tirith_enabled: true`
- [ ] Configure `website_blocklist` for internal domains
- [ ] Monitor `~/.hermes/logs/` for anomalies
- [ ] Periodically audit gateway allowlists
