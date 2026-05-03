# DeepSeek with Claude Code CLI

Claude Code uses the Anthropic SDK internally. DeepSeek exposes an Anthropic-compatible endpoint at `https://api.deepseek.com/anthropic`, so Claude Code can be pointed at DeepSeek with no code changes — just environment variables.

## Table of Contents
- [Quick Setup](#quick-setup)
- [All Environment Variables](#all-environment-variables)
- [Switching Between DeepSeek and Anthropic](#switching-between-deepseek-and-anthropic)
- [Primitives Compatibility: Skills, Commands, Agents, Hooks](#primitives-compatibility-skills-commands-agents-hooks)
- [What Works / What Doesn't](#what-works--what-doesnt)
- [Gotchas](#gotchas)

---

## Quick Setup

**Linux / macOS — add to `~/.zshrc` or `~/.bashrc`:**
```bash
export ANTHROPIC_BASE_URL="https://api.deepseek.com/anthropic"
export ANTHROPIC_AUTH_TOKEN="sk-YOUR_DEEPSEEK_KEY"
export ANTHROPIC_API_KEY=""                          # must be empty string, NOT unset

export ANTHROPIC_MODEL="deepseek-v4-pro"
export ANTHROPIC_DEFAULT_OPUS_MODEL="deepseek-v4-pro"
export ANTHROPIC_DEFAULT_SONNET_MODEL="deepseek-v4-pro"
export ANTHROPIC_DEFAULT_HAIKU_MODEL="deepseek-v4-flash"
export CLAUDE_CODE_SUBAGENT_MODEL="deepseek-v4-flash"
export CLAUDE_CODE_EFFORT_LEVEL="max"
```

**Windows PowerShell:**
```powershell
$env:ANTHROPIC_BASE_URL      = "https://api.deepseek.com/anthropic"
$env:ANTHROPIC_AUTH_TOKEN    = "sk-YOUR_DEEPSEEK_KEY"
$env:ANTHROPIC_API_KEY       = ""
$env:ANTHROPIC_MODEL                  = "deepseek-v4-pro"
$env:ANTHROPIC_DEFAULT_OPUS_MODEL     = "deepseek-v4-pro"
$env:ANTHROPIC_DEFAULT_SONNET_MODEL   = "deepseek-v4-pro"
$env:ANTHROPIC_DEFAULT_HAIKU_MODEL    = "deepseek-v4-flash"
$env:CLAUDE_CODE_SUBAGENT_MODEL       = "deepseek-v4-flash"
$env:CLAUDE_CODE_EFFORT_LEVEL         = "max"
```

**Reload and run:**
```bash
source ~/.zshrc
claude
```

---

## All Environment Variables

| Variable | Recommended Value | Purpose |
|----------|------------------|---------|
| `ANTHROPIC_BASE_URL` | `https://api.deepseek.com/anthropic` | Route to DeepSeek's Anthropic-compatible endpoint |
| `ANTHROPIC_AUTH_TOKEN` | Your DeepSeek API key | Authentication (DeepSeek key, not Anthropic key) |
| `ANTHROPIC_API_KEY` | `""` (empty string) | Must be empty — if set/non-empty Claude Code ignores `ANTHROPIC_BASE_URL` |
| `ANTHROPIC_MODEL` | `deepseek-v4-pro` | Default model for most tasks |
| `ANTHROPIC_DEFAULT_OPUS_MODEL` | `deepseek-v4-pro` | Mapped when Claude Code would use Opus |
| `ANTHROPIC_DEFAULT_SONNET_MODEL` | `deepseek-v4-pro` | Mapped when Claude Code would use Sonnet |
| `ANTHROPIC_DEFAULT_HAIKU_MODEL` | `deepseek-v4-flash` | Mapped when Claude Code would use Haiku |
| `CLAUDE_CODE_SUBAGENT_MODEL` | `deepseek-v4-flash` | Model used for subagent tasks (cheaper) |
| `CLAUDE_CODE_EFFORT_LEVEL` | `max` | Enables maximum thinking effort |

**Why map all three model tiers?**  
Claude Code internally requests specific model tiers (Opus for heavy tasks, Haiku for lightweight ones). Without the mapping variables, it will try to send those Claude model names to DeepSeek, which will silently fall back to `deepseek-v4-flash` for any unrecognized name. Explicit mapping ensures the right DeepSeek model handles each tier.

---

## Switching Between DeepSeek and Anthropic

**Shell function for easy toggling (add to `~/.zshrc`):**
```bash
function use-deepseek() {
  export ANTHROPIC_BASE_URL="https://api.deepseek.com/anthropic"
  export ANTHROPIC_AUTH_TOKEN="sk-YOUR_DEEPSEEK_KEY"
  export ANTHROPIC_API_KEY=""
  export ANTHROPIC_MODEL="deepseek-v4-pro"
  export ANTHROPIC_DEFAULT_OPUS_MODEL="deepseek-v4-pro"
  export ANTHROPIC_DEFAULT_SONNET_MODEL="deepseek-v4-pro"
  export ANTHROPIC_DEFAULT_HAIKU_MODEL="deepseek-v4-flash"
  export CLAUDE_CODE_SUBAGENT_MODEL="deepseek-v4-flash"
  export CLAUDE_CODE_EFFORT_LEVEL="max"
  echo "Claude Code → DeepSeek V4"
}

function use-anthropic() {
  unset ANTHROPIC_BASE_URL ANTHROPIC_AUTH_TOKEN
  unset ANTHROPIC_MODEL ANTHROPIC_DEFAULT_OPUS_MODEL
  unset ANTHROPIC_DEFAULT_SONNET_MODEL ANTHROPIC_DEFAULT_HAIKU_MODEL
  unset CLAUDE_CODE_SUBAGENT_MODEL CLAUDE_CODE_EFFORT_LEVEL
  export ANTHROPIC_API_KEY="sk-ant-YOUR_ANTHROPIC_KEY"
  echo "Claude Code → Anthropic (Claude)"
}
```

---

## Primitives Compatibility: Skills, Commands, Agents, Hooks

### Skills (`SKILL.md` files) — No changes needed

Skills are markdown loaded into context. DeepSeek reads and follows them identically to Claude. No Anthropic-specific features are required. All existing skills work as-is.

### Commands — No changes needed (unless `model:` is set)

Command frontmatter supports a `model:` field. If a command specifies a Claude model name, DeepSeek **silently remaps it to `deepseek-v4-flash`** with no error. Either remove the `model:` field (env vars control the model globally) or use a DeepSeek model name:

```yaml
---
description: My command
model: deepseek-v4-pro     # ✓ explicit DeepSeek model
# model: claude-opus-4-6  # ✗ silently becomes deepseek-v4-flash
---
```

### Agents (`.claude/agents/*.md`) — Safe if `model:` is correct

Agent instructions are text — fully portable. Tool use in agents works. The only risk is the `model:` frontmatter field:

```yaml
---
name: my-agent
description: Does X
model: deepseek-v4-pro        # ✓ use this
# model: claude-sonnet-4-5   # ✗ silently remaps to deepseek-v4-flash
# model: sonnet               # ✗ shorthand also remaps silently
# model: inherit              # ✓ safe — inherits from parent/env vars
---
```

**Model name remapping table** — what DeepSeek does with Claude names:

| Value in `model:` field | What DeepSeek actually uses |
|------------------------|----------------------------|
| `deepseek-v4-pro` | deepseek-v4-pro ✓ |
| `deepseek-v4-flash` | deepseek-v4-flash ✓ |
| `inherit` | Parent model (from env vars) ✓ |
| `claude-opus-4-6` | deepseek-v4-flash ⚠ silent remap |
| `claude-sonnet-4-5` | deepseek-v4-flash ⚠ silent remap |
| `claude-haiku-4-5` | deepseek-v4-flash ⚠ silent remap |
| `sonnet` | deepseek-v4-flash ⚠ silent remap |
| `haiku` | deepseek-v4-flash ⚠ silent remap |
| `opus` | deepseek-v4-flash ⚠ silent remap |

**Rule:** When running under DeepSeek, any unrecognized model name silently becomes `deepseek-v4-flash`. There is no error or warning. Audit agent files for `model:` fields before switching.

### Hooks — No changes needed

Hooks execute as shell commands on the Claude Code harness — they never touch the model API. Fully portable across any backend.

### MCP tools — No changes needed

Claude Code dispatches MCP tools as regular function calls. DeepSeek handles these correctly. What DeepSeek doesn't support is the native Anthropic API `mcp_servers` parameter — but Claude Code doesn't use that path. Your existing MCP tool integrations (browser automation, etc.) work unchanged.

### Compatibility summary

| Primitive | Compatible? | Action |
|-----------|------------|--------|
| Skills / SKILL.md | ✅ Yes | None |
| Commands (no `model:` field) | ✅ Yes | None |
| Commands (with `model: claude-*`) | ⚠️ Silent remap | Use DeepSeek name or remove field |
| Agents (no `model:` field) | ✅ Yes | None |
| Agents (`model: inherit`) | ✅ Yes | None |
| Agents (with `model: claude-*`) | ⚠️ Silent remap | Use DeepSeek name or remove field |
| Hooks | ✅ Yes | None |
| MCP tools (harness-dispatched) | ✅ Yes | None |
| Vision / image inputs in prompts | ❌ Fails | Not supported by DeepSeek |
| `computer_use` tool | ❌ Fails | Not supported |
| `cache_control` annotations | ⚠️ Ignored | DeepSeek auto-caches; no action needed |
| `disable_parallel_tool_use` | ⚠️ Ignored | Parallel tool use will occur |

---

## What Works / What Doesn't

DeepSeek's Anthropic-compatible endpoint supports most of what Claude Code needs, but not everything Claude supports natively.

### Supported
- Text messages (system, user, assistant turns)
- Tool definitions and tool use (Claude Code is heavily tool-dependent — this works)
- Thinking mode (`CLAUDE_CODE_EFFORT_LEVEL=max` enables it)
- Streaming responses
- `max_tokens`, `temperature`, `top_p`, `stop_sequences`, `stream`
- `tool_choice`: none, auto, any, specific tool

### Not Supported
| Feature | Impact |
|---------|--------|
| `anthropic-beta` header | Ignored — beta features unavailable |
| `anthropic-version` header | Ignored |
| `cache_control` (prompt caching) | Not supported — DeepSeek has its own auto-caching |
| `top_k` parameter | Ignored |
| Image inputs | Not supported — tasks needing screenshots will fail |
| Document content blocks | Not supported |
| MCP server tool types | Not supported |
| Web search tool | Not supported |
| Computer use tool | Not supported |
| `budget_tokens` in thinking | Ignored (effort level controls reasoning depth instead) |

**Practical implication:** Claude Code's core coding workflow (file read/edit, bash, search) is tool-use-based and works fine. Features that rely on vision (screenshot analysis) or computer use will not work.

---

## Gotchas

- `ANTHROPIC_API_KEY` must be set to `""` (empty string), **not** left unset. An unset key causes Claude Code to fall back to Anthropic's servers and reject the DeepSeek key.
- The base URL is `https://api.deepseek.com/anthropic` — **not** `https://api.deepseek.com`. The Anthropic-format endpoint is a different path than the OpenAI-format endpoint.
- Unknown model names (e.g., if you accidentally pass `claude-sonnet-4-5`) are **silently remapped to deepseek-v4-flash** — no error, just wrong model. Always set all the `ANTHROPIC_DEFAULT_*` variables.
- `anthropic-beta` headers are ignored, so extended thinking via the beta header won't work — use `CLAUDE_CODE_EFFORT_LEVEL=max` instead.
- DeepSeek does not support `cache_control` blocks (Anthropic's explicit prompt caching). Context caching happens automatically on DeepSeek's side based on prompt prefixes.
- If Claude Code shows auth errors, verify your DeepSeek key is in `ANTHROPIC_AUTH_TOKEN`, not `ANTHROPIC_API_KEY`.
