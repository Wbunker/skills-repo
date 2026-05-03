# DeepSeek with Claude Code CLI

Claude Code uses the Anthropic SDK internally. DeepSeek exposes an Anthropic-compatible endpoint at `https://api.deepseek.com/anthropic`, so Claude Code can be pointed at DeepSeek with no code changes — just environment variables.

## Table of Contents
- [Quick Setup](#quick-setup)
- [All Environment Variables](#all-environment-variables)
- [Switching Between DeepSeek and Anthropic](#switching-between-deepseek-and-anthropic)
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
