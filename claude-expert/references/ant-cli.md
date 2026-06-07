# ant CLI

Official command-line client for the Claude API (`ant`). Every API resource is exposed as a
subcommand — `ant messages create`, `ant models list`, `ant beta:agents create`,
`ant beta:sessions:events list`, etc. Versus `curl`, it builds request bodies from typed flags or
piped YAML (no hand-written JSON), inlines files into fields with `@path`, reshapes responses with
`--transform` (built-in GJSON — no `jq`), and auto-paginates list endpoints.

Use this when the user wants to call the Claude API, manage Managed Agents, or version-control API
resources from the terminal/CI without writing SDK code.

Docs: https://platform.claude.com/docs/en/api/sdks/cli · per-endpoint flags: `ant <cmd> --help`.

## Table of Contents

- [Install](#install)
- [Authentication](#authentication)
- [Profiles & workspaces](#profiles--workspaces)
- [Command structure & global flags](#command-structure--global-flags)
- [Output formats](#output-formats)
- [Transform output (GJSON)](#transform-output-gjson)
- [Passing request bodies](#passing-request-bodies)
- [Messages & models](#messages--models)
- [Managed Agents end-to-end](#managed-agents-end-to-end)
- [Version-controlling resources](#version-controlling-resources)
- [Scripting, errors, debug, completion](#scripting-errors-debug-completion)
- [Claude Code integration](#claude-code-integration)
- [Gotchas](#gotchas)

## Install

```bash
# macOS (Homebrew)
brew install anthropics/tap/ant

# Linux / WSL — download the versioned release binary from GitHub releases
VERSION=1.10.0
OS=$(uname -s | tr '[:upper:]' '[:lower:]')
ARCH=$(uname -m | sed -e 's/x86_64/amd64/' -e 's/aarch64/arm64/')
curl -fsSL "https://github.com/anthropics/anthropic-cli/releases/download/v${VERSION}/ant_${VERSION}_${OS}_${ARCH}.tar.gz" \
  | sudo tar -xz -C /usr/local/bin ant

# From source (Go 1.25+) — binary lands in $(go env GOPATH)/bin
go install github.com/anthropics/anthropic-cli/cmd/ant@latest
export PATH="$PATH:$(go env GOPATH)/bin"   # if not already on PATH

ant --version
```

Releases: https://github.com/anthropics/anthropic-cli/releases

## Authentication

Two mechanisms. **Interactive login** (OAuth, no API key to manage) for local dev; **API key**
(`ANTHROPIC_API_KEY`) for scripts/CI. For non-interactive workloads (CI, servers, containers)
Anthropic recommends Workload Identity Federation over interactive login.

```bash
# Interactive OAuth login — opens a browser, stores creds under $ANTHROPIC_CONFIG_DIR
ant auth login
ant auth login --no-browser            # remote host: prints URL, paste code back
ant auth login --workspace-id wrkspc_01...   # bind to a workspace, skip the picker
ant auth login --profile <name>        # create/login a named profile

ant auth status                        # which credential source + workspace + profile won
ant auth logout                        # remove stored creds (current profile)
ant auth logout --all                  # clear every profile
```

```bash
# API key (alternative) — overrides any profile while set
export ANTHROPIC_API_KEY=sk-ant-api03-...     # key from platform.claude.com/settings/keys
ant --api-key sk-ant-... messages create ...  # override for a single invocation
```

Point at a different host with `ANTHROPIC_BASE_URL` or `--base-url`.

## Profiles & workspaces

An interactive-login token is bound to a single workspace. To use more than one, log in under
separate named profiles and switch:

```bash
ant profile list
ant profile activate other-ws                 # set default for subsequent commands
ant --profile other-ws models list            # one command only
ANTHROPIC_PROFILE=other-ws ant models list     # env-var equivalent
ant profile get  --profile other-ws
ant profile set workspace_id wrkspc_01... --profile other-ws   # rebind needs a fresh login
```

Writable `profile set` keys: `workspace_id`, `base_url`, `organization_id`, `scope`, `client_id`,
`console_url`. **Profiles are only consulted when no API key is set** — `ANTHROPIC_API_KEY`
overrides every profile, so unset it before switching profiles.

## Command structure & global flags

`ant <resource>[:<subresource>] <action> [flags]` — nested resources use colons. Beta resources
(agents, sessions, deployments, environments, skills) live under the `beta:` prefix and
**auto-send the correct `anthropic-beta` header**; use `--beta <header>` only to override the
version.

| Flag | Description |
|---|---|
| `--profile` | Named profile for this invocation (= `ANTHROPIC_PROFILE`) |
| `--format` | `auto`, `json`, `jsonl`, `yaml`, `pretty`, `raw`, `explore` |
| `--transform` | Filter/reshape the response with a GJSON path |
| `-r`, `--raw-output` | Print string results without surrounding quotes (like `jq -r`) |
| `--base-url` | Override the API base URL |
| `--api-key` | Override the API key for this invocation |
| `--debug` | Print full HTTP request + response to stderr (keys redacted) |
| `--format-error`, `--transform-error` | Same as above, applied to error responses |
| `--beta` | Override the auto-set beta header |

## Output formats

`auto` (default) pretty-prints JSON for create/modify commands. **List and retrieve commands open
the interactive explorer TUI by default when connected to a terminal**, and emit pretty JSON when
piped. Override with `--format`:

```bash
ant models retrieve --model-id claude-opus-4-8 --format yaml
ant models list --format jsonl       # one compact JSON object per line (streams into head/grep)
ant models list --format explore     # interactive TUI: arrows expand/collapse, / search, q quit
```

List endpoints auto-paginate; in `jsonl`/`yaml` each item is emitted separately.

## Transform output (GJSON)

`--transform` reshapes responses before printing, using a
[GJSON path](https://github.com/tidwall/gjson/blob/master/SYNTAX.md). On list endpoints it runs
against **each item**, not the envelope:

```bash
ant beta:agents list --transform "{id,name,model}" --format jsonl
```

Capture a single scalar (e.g. a new resource ID) by pairing `--transform` with `--raw-output`:

```bash
AGENT_ID=$(ant beta:agents create --name "My Agent" --model '{id: claude-sonnet-4-6}' \
  --transform id --raw-output)
```

`--raw-output` (strips JSON quotes from string results) is distinct from `--format raw` (raw
response bytes, no auto-pagination, transform applies to the pagination envelope).

## Passing request bodies

- **Flags** for scalars and short structured values. Structured flags accept relaxed YAML
  (unquoted keys) or strict JSON: `--message '{role: user, content: "Hello, Claude"}'`.
- **Repeatable flags** build arrays — each `--tool` / `--event` appends one element.
- **Stdin** (JSON or YAML) supplies the full body; stdin fields **merge with flags, flags win**.
  Heredocs work for multi-line YAML (quote the delimiter `<<'YAML'` to disable expansion).
- **`@path` file references** inline a file's contents into a string field: `--system @prompt.txt`.
  Inside structured values, quote the path: `data: "@./scan.pdf"`. Binary is base64-encoded
  automatically; force with `@file://` (text) or `@data://` (base64). Escape a literal `@` as `\@`.

## Messages & models

```bash
ant messages create \
  --model claude-opus-4-8 \
  --max-tokens 1024 \
  --message '{role: user, content: "Hello, Claude"}'

ant models list
ant models retrieve --model-id claude-opus-4-8 --format yaml
```

## Managed Agents end-to-end

Four concepts: agent → environment → session → events (see [managed-agents.md](managed-agents.md)).
Full terminal deploy:

```bash
# 1. Agent (model + system prompt + tools). Save the returned id.
ant beta:agents create \
  --name "Coding Assistant" \
  --model '{id: claude-opus-4-8}' \
  --system "You are a helpful coding assistant. Write clean, well-documented code." \
  --tool '{type: agent_toolset_20260401}'

# 2. Environment (sandbox config). Save the returned id.
ant beta:environments create \
  --name "quickstart-env" \
  --config '{type: cloud, networking: {type: unrestricted}}'

# 3. Session (references agent + environment by id). --agent takes the bare id string.
ant beta:sessions create \
  --agent agent_011... \
  --environment-id env_01... \
  --title "Quickstart session"

# 4. Send a user message, then read or stream events.
ant beta:sessions:events send \
  --session-id session_01... \
  --event '{type: user.message, content: [{type: text, text: "Generate the first 20 Fibonacci numbers to fibonacci.txt"}]}'

# Read the transcript (--format auto overrides the default explorer for list commands):
ant beta:sessions:events list --session-id session_01... \
  --transform 'content.0.text' --format auto --raw-output

# Or watch live as events arrive:
ant beta:sessions:events stream --session-id session_01...
```

`agent_toolset_20260401` enables the full built-in toolset (bash, file ops, web search/fetch, …).
`networking: {type: unrestricted}` lets the agent reach external services; lock down for
production. The agent goes idle (`session.status_idle`) when finished.

## Version-controlling resources

Define agents/environments as YAML, check them into the repo, and sync from CI. Create reads from
stdin; **update needs the id (and `--version` for agents) as flags**:

```yaml
# summarizer.agent.yaml
name: Summarizer
model: claude-sonnet-4-6
system: |
  You are a helpful assistant that writes concise summaries.
tools:
  - type: agent_toolset_20260401
```

```bash
ant beta:agents create < summarizer.agent.yaml
ant beta:agents update --agent-id agent_011... --version 1 < summarizer.agent.yaml
ant beta:environments update --environment-id env_01... < summarizer.environment.yaml
```

## Scripting, errors, debug, completion

```bash
# Chain list output into a follow-up command
FIRST=$(ant beta:agents list --transform id --raw-output | head -1)
ant beta:agents:versions list --agent-id "$FIRST" --transform "{version,created_at}" --format jsonl

# Inspect errors (--raw-output does NOT apply to errors; use --format-error yaml for a scalar)
ant beta:agents retrieve --agent-id bogus --transform-error error.message --format-error yaml 2>&1

# See the exact HTTP request/response (keys redacted)
ant --debug beta:agents list

# Shell completion (bash/zsh/fish/powershell)
ant @completion zsh > "${fpath[1]}/_ant"
```

## Claude Code integration

Claude Code knows out of the box how to use `ant` (via its `/claude-api` skill) — with the CLI
installed and authenticated you can ask it to "list my recent agent sessions and summarize which
errored" or "pull events for session X and tell me where the agent got stuck"; it shells out to
`ant`, parses the structured output, and reasons over it. For a guided Managed Agents setup, run
`/claude-api managed-agents-onboard` in Claude Code.

## Gotchas

- **API key overrides profiles** — if `ANTHROPIC_API_KEY` is set, every `--profile` /
  `ant profile activate` is ignored and the key's workspace is used. Unset it to use profiles.
- **List/retrieve open the explorer TUI by default in a terminal** — in scripts or when you need
  parseable output interactively, pass `--format auto`/`json`/`jsonl`/`yaml`, or it blocks waiting
  for keyboard input.
- **`--raw-output` ≠ `--format raw`** — the first strips quotes from string results; the second
  dumps raw response bytes and applies `--transform` to the pagination envelope, not per item.
- **`agent_toolset_20260401` is dated** — the toolset type carries a date suffix that advances
  with releases; match it to the beta version the API expects.
- **Updates need explicit version** — `ant beta:agents update` requires `--version` (optimistic
  locking); a stale version fails. Get the current one from `retrieve`.
- **`profile set workspace_id` doesn't rebind credentials** — it records the target; run
  `ant auth login` again under that profile to mint a token for the new workspace.
- **`ant auth status` reports, it doesn't health-check** — don't script against its exit status.
