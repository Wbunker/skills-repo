# Playwright agent-cli (`playwright-cli`)

A shell tool that drives a **live browser one command at a time** — built for AI agents and
interactive automation, distinct from the `@playwright/test` runner. You don't write `*.spec.ts`;
you issue commands like `open`, `snapshot`, `fill`, `click`, and persist state with `state-save`.

A persistent **daemon** holds the browser process open, so each command is cheap (no per-command
startup). Concise CLI output and installable **skills** keep token usage low — agents discover
capabilities through skills instead of loading large tool schemas. Supports Chrome, Firefox,
WebKit, and Edge, plus multiple isolated **sessions** with separate state.

> Docs: <https://playwright.dev/agent-cli/introduction>

## Contents
- [What it is + install/run](#what-it-is--installrun)
- [Command model](#command-model)
- [Configuration](#configuration)
- [Element references via snapshot](#element-references-via-snapshot)
- [Navigation commands](#navigation-commands)
- [Interaction commands](#interaction-commands)
- [Keyboard & mouse commands](#keyboard--mouse-commands)
- [Vision mode (coordinate-based)](#vision-mode-coordinate-based)
- [Dialog commands](#dialog-commands)
- [Tabs / pages commands](#tabs--pages-commands)
- [Console & evaluate / run-code](#console--evaluate--run-code)
- [Verification & locator generation](#verification--locator-generation)
- [Network & mocking commands](#network--mocking-commands)
- [Tracing, video & step debugging](#tracing-video--step-debugging)
- [Screenshots & PDF](#screenshots--pdf)
- [Storage state — save login, skip it next time](#storage-state--save-login-skip-it-next-time)
- [Cookie / localStorage / sessionStorage commands](#cookie--localstorage--sessionstorage-commands)
- [Sessions, dashboard & attach](#sessions-dashboard--attach)
- [agent-cli vs the Playwright MCP server](#agent-cli-vs-the-playwright-mcp-server)
- [agent-cli vs test runner](#agent-cli-vs-test-runner)

## What it is + install/run

Requires **Node.js 20+** and a coding agent (Claude Code, Copilot, …).

```bash
# Global install
npm install -g @playwright/cli@latest
playwright-cli --help

# Or run ad-hoc via npx
npx playwright-cli --help

# Browsers (auto-downloaded on first use; explicit install if you prefer)
playwright-cli install-browser               # default (chromium)
playwright-cli install-browser firefox       # a specific browser
playwright-cli install-browser --with-deps   # with system dependencies

# Install the agent skills so the model can self-discover commands
playwright-cli install --skills
```

Route every command in an agent session to one named browser with an env var:
```bash
PLAYWRIGHT_CLI_SESSION=todo-app claude .
```

## Command model

```
playwright-cli <command> [arguments] [options]
```

```bash
playwright-cli open                                              # launch a browser
playwright-cli open https://example.com --headed --browser=firefox
playwright-cli goto https://demo.playwright.dev/todomvc          # navigate existing browser
```

Common global options: `--headed`, `--browser=<chromium|firefox|webkit|msedge>`, `--persistent`,
`--profile=<dir>`, `--config=<file>`, `--extension`, `--skills`, and `-s=<name>` to target a named
session.

## Configuration

Three layers, lowest priority first: **config file → env vars → command flags**.

**Defaults:** headless, Chromium, in-memory profile (state lost when the browser closes), action
timeout 5000 ms, navigation 60000 ms, expect 5000 ms, `testIdAttribute` `data-testid`.

**Config file** — JSON at `.playwright/cli.config.json` (or `--config=<file>`); inspect the resolved
config with `playwright-cli config-print`. Key fields:

```jsonc
{
  "browser": {
    "browserName": "chromium",            // | firefox | webkit
    "isolated": false,                      // true = in-memory profile
    "userDataDir": "./profile",
    "launchOptions": { "channel": "chrome", "headless": true, "args": [], "proxy": { "server": "…" } },
    "contextOptions": { "viewport": { "width": 1280, "height": 720 }, "locale": "en-US",
                        "storageState": "auth.json", "permissions": [], "serviceWorkers": "allow" },
    "cdpEndpoint": "http://localhost:9222", // attach instead of launch
    "initScript": ["./preload.js"]
  },
  "saveSession": false,                      // auto-record a trace of the whole session
  "saveVideo": { "width": 800, "height": 600 },
  "snapshot": { "mode": "full" },            // | none
  "outputDir": ".playwright-cli",
  "timeouts": { "action": 5000, "navigation": 60000, "expect": 5000 },
  "testIdAttribute": "data-testid",
  "secrets": { "TOKEN": "…" },               // or a dotenv file
  "codegen": "typescript"
}
```

**Env vars:** `PLAYWRIGHT_CLI_SESSION` sets the default session. The broader settings share the
`PLAYWRIGHT_MCP_*` family with the MCP server — e.g. `PLAYWRIGHT_MCP_BROWSER`,
`PLAYWRIGHT_MCP_HEADLESS`, `PLAYWRIGHT_MCP_USER_DATA_DIR`, `PLAYWRIGHT_MCP_STORAGE_STATE`,
`PLAYWRIGHT_MCP_VIEWPORT_SIZE` (`"1280x720"`), `PLAYWRIGHT_MCP_DEVICE`, `PLAYWRIGHT_MCP_PROXY_SERVER`,
`PLAYWRIGHT_MCP_SAVE_SESSION`, `PLAYWRIGHT_MCP_SAVE_VIDEO` (`"800x600"`), `PLAYWRIGHT_MCP_SECRETS_FILE`.

## Element references via snapshot

Interaction commands target elements by **reference** (`e3`, `e5`, `e7`, …) obtained from the
`snapshot` command, which prints the page's accessibility tree with a label for each interactive
element:

```bash
playwright-cli snapshot                         # prints page tree with element refs (e3, e5, …)
playwright-cli snapshot "#main"                 # scope to a CSS selector
playwright-cli snapshot e34                     # scope to a ref
playwright-cli snapshot --depth=4               # limit tree depth
playwright-cli snapshot --filename=after.yaml   # save to a file
playwright-cli fill e5 "Buy groceries" --submit # fill the input at ref e5 and submit
playwright-cli click e7                          # click the element at ref e7
```

Refs are **stable within a single snapshot** but invalidate after the page changes — take a fresh
`snapshot` after navigation/mutation. **Prefer refs over selectors:** a ref points at the exact
element the agent just saw. Only interactive elements (buttons, links, inputs) get refs.

Every command auto-emits a fresh snapshot of the new state; add `--raw` to a command to strip the
page info and return only its own output (easier to parse).

## Navigation commands

| Command | Purpose |
|---------|---------|
| `open [url]` | Launch browser, optionally navigate |
| `goto <url>` | Navigate to a URL |
| `go-back` / `go-forward` | History navigation |
| `reload` | Refresh the page |
| `close` / `close-all` | Close the browser / all sessions |

```bash
playwright-cli open https://example.com --headed
playwright-cli goto https://demo.playwright.dev/todomvc
playwright-cli go-back
playwright-cli reload
```

## Interaction commands

Targets accept a **ref** (`e15`), a **CSS selector** (`"#main > button.submit"`), or a
**Playwright locator** (`"getByRole('button', { name: 'Submit' })"`). Refs are preferred — see
[locators.md](locators.md) and [actions.md](actions.md) for the locator equivalents in the runner.

| Command | Syntax | Purpose |
|---------|--------|---------|
| `click` | `click <ref> [button]` | Click (optional `left`/`right`/`middle`) |
| `dblclick` | `dblclick <ref> [button]` | Double-click |
| `hover` | `hover <ref>` | Hover |
| `fill` | `fill <ref> <text> [--submit]` | Fill an input; `--submit` presses Enter |
| `type` | `type <text>` | Type into the focused element |
| `select` | `select <ref> <value>` | Choose a `<select>` option |
| `check` / `uncheck` | `check <ref>` / `uncheck <ref>` | Toggle a checkbox/radio |
| `drag` | `drag <startRef> <endRef>` | Drag one element onto another |
| `upload` | `upload <file>` | Set files on a file input |
| `resize` | `resize <width> <height>` | Resize the viewport |

```bash
playwright-cli snapshot
playwright-cli fill e3 "hello@example.com"
playwright-cli fill e5 "query" --submit
playwright-cli select e7 "United States"
playwright-cli check e10
playwright-cli upload /path/to/file.pdf
playwright-cli click e15
```

## Keyboard & mouse commands

| Command | Syntax | Purpose |
|---------|--------|---------|
| `press` | `press <key>` | Press a key or combo (`Control+a`, `Shift+Tab`) |
| `keydown` / `keyup` | `keydown <key>` / `keyup <key>` | Hold / release a key |
| `mousemove` | `mousemove <x> <y>` | Move the pointer |
| `mousedown` / `mouseup` | `mousedown [button]` / `mouseup [button]` | Press / release a button |
| `mousewheel` | `mousewheel <dx> <dy>` | Scroll by delta |

Common keys: `Enter Tab Escape Backspace Delete Space ArrowUp/Down/Left/Right Home End PageUp PageDown`.

```bash
playwright-cli press Enter
playwright-cli press Control+a          # select all
playwright-cli mousewheel 0 500         # scroll down
```

> Prefer snapshot refs over coordinate mouse commands for normal web UI — reserve `mouse*` for
> canvas apps and custom controls lacking accessibility info.

## Vision mode (coordinate-based)

For elements **not in the accessibility tree** — canvas/WebGL, maps, image editors, charts, custom
widgets — drive by pixel coordinates using a `screenshot` as the visual reference (the `mouse*`
commands above). This is the fallback when `snapshot` yields no usable ref.

```bash
playwright-cli screenshot --filename=canvas.png   # capture coordinates reference
playwright-cli mousemove 150 300                   # then act by pixel position
playwright-cli mousedown
playwright-cli mouseup
# drag:
playwright-cli mousemove 100 200 && playwright-cli mousedown
playwright-cli mousemove 400 200 && playwright-cli mouseup
```

For standard web apps the snapshot/ref approach is more reliable and token-efficient — vision mode is
a specialized fallback.

## Dialog commands

Native dialogs (`alert`/`confirm`/`prompt`) block the page — handle them before continuing.

| Command | Syntax | Purpose |
|---------|--------|---------|
| `dialog-accept` | `dialog-accept [prompt]` | Accept; optionally supply prompt text |
| `dialog-dismiss` | `dialog-dismiss` | Cancel the dialog |

```bash
playwright-cli dialog-accept "Alice"    # answer a prompt() dialog
playwright-cli dialog-dismiss
```

## Tabs / pages commands

| Command | Syntax | Purpose |
|---------|--------|---------|
| `tab-list` | `tab-list` | List all open tabs |
| `tab-new` | `tab-new [url]` | Open a new tab (blank or at a URL) |
| `tab-select` | `tab-select <index>` | Switch to a tab by index |
| `tab-close` | `tab-close [index]` | Close current tab, or one by index |

```bash
playwright-cli tab-new https://example.com
playwright-cli tab-list
playwright-cli tab-select 1
playwright-cli tab-close 2
```

## Console & evaluate / run-code

| Command | Syntax | Purpose |
|---------|--------|---------|
| `console` | `console [level] [--clear]` | Read console messages (`error`/`warning`/`debug`; default info+) |
| `eval` | `eval <expression> [ref]` | Evaluate JS on the page or a specific element |
| `run-code` | `run-code <code> [--filename=script.js]` | Run an arbitrary Playwright script with full API access |

```bash
playwright-cli console error
playwright-cli eval "() => document.title"
playwright-cli eval "(el) => el.getAttribute('data-id')" e15
playwright-cli run-code "async (page) => { await page.waitForSelector('.data-loaded'); }"
```

`run-code` is the escape hatch for waiting, permissions, and scraping — it receives the live
`page`. See [library-api.md](library-api.md) for the full `page` API surface.

## Verification & locator generation

Assertion commands (the CLI analog of web-first [assertions](assertions.md)) and locator generation:

| Command | Purpose |
|---------|---------|
| `verify-element-visible <ref\|selector>` | Assert an element is visible |
| `verify-text-visible <text>` | Assert text is present on the page |
| `verify-list-visible <ref>` | Assert a list and its items are visible |
| `verify-value <ref> <value>` | Assert an input's value |
| `generate-locator <ref>` | Emit a robust Playwright locator for an element (for porting into a `*.spec.ts`) |

```bash
playwright-cli verify-text-visible "Welcome back"
playwright-cli verify-value e5 "user@example.com"
playwright-cli generate-locator e7      # → getByRole('button', { name: 'Submit' })
```

## Network & mocking commands

Inspect traffic and stub responses without a test file. See [network.md](network.md) for the
runner's routing/HAR equivalents.

| Command | Syntax | Purpose |
|---------|--------|---------|
| `network` | `network [--filter=<p>] [--static] [--request-body] [--request-headers] [--clear]` | Inspect requests |
| `route` | `route <pattern> [options]` | Mock matching responses |
| `route-list` | `route-list` | List active routes |
| `unroute` | `unroute [pattern]` | Remove one route, or all if omitted |
| `network-state-set` | `network-state-set <offline\|online>` | Toggle connectivity |

`route` options: `--status=<code>`, `--body=<text>`, `--content-type=<type>`,
`--header=<name:value>`, `--remove-header=<names>`.

```bash
playwright-cli network --filter="api" --request-body
playwright-cli route "**/api/users" --body='[{"name":"Alice"}]' --content-type=application/json
playwright-cli route "**/api/data" --status=500
playwright-cli route-list
playwright-cli unroute "**/api/users"
playwright-cli network-state-set offline
```

## Tracing, video & step debugging

The **DevTools** capability — record a [trace](trace-viewer.md) or video, and step the daemon:

| Command | Purpose |
|---------|---------|
| `tracing-start` / `tracing-stop` | Record a Playwright trace (open with `npx playwright show-trace`) |
| `video-start [filename]` | Start a WebM recording (`--size=800x600`); default dir `.playwright-cli/` |
| `video-chapter <title>` | Insert a chapter marker (`--description="…"`, `--duration=2000` ms card) |
| `video-stop` | Stop and save the WebM |
| `pause-at <ref>` / `resume` / `step-over` | Pause/step the agent loop (pairs with `--debug=cli`, see [debugging.md](debugging.md)) |

```bash
playwright-cli tracing-start
# ... drive the page ...
playwright-cli tracing-stop --filename=trace.zip   # default: .playwright-cli/trace.zip
npx playwright show-trace .playwright-cli/trace.zip
```

Traces capture DOM snapshots, screenshots, network, and console at every step. To auto-record an
entire agent session without manual start/stop, pass `--save-session` to the command driving it.

## Screenshots & PDF

| Command | Syntax | Purpose |
|---------|--------|---------|
| `screenshot` | `screenshot [ref] [--filename=f] [--full-page]` | Capture viewport, element, or full page |
| `pdf` | `pdf [--filename=page.pdf]` | Export the page to PDF |

```bash
playwright-cli screenshot --full-page --filename=full-page.png
playwright-cli screenshot e15 --filename=button.png
playwright-cli pdf --filename=page.pdf
```

> `snapshot` (accessibility tree, above) is for *driving* the page; `screenshot` is for *seeing* it.

## Storage state — save login, skip it next time

The headline workflow: log in **once**, save the authenticated browser state to a file, then on
later runs **load** that file and jump straight past the login screen.

| Command | Purpose |
|---------|---------|
| `state-save [filename]` | Save storage state (cookies + localStorage) to a file (auto-named if omitted) |
| `state-load <filename>` | Restore storage state from a file |

**Full "save login, skip it next time" sequence:**
```bash
# First run — log in and capture the authenticated state
playwright-cli open https://app.example.com/login
playwright-cli fill e3 "user@example.com"
playwright-cli fill e5 "password123"
playwright-cli click e7
playwright-cli state-save auth.json

# Any later run — restore and go straight to an authenticated page (no login needed)
playwright-cli state-load auth.json
playwright-cli goto https://app.example.com/dashboard
```

After `state-save auth.json`, subsequent sessions `state-load auth.json` to restore cookies +
localStorage and skip the login flow entirely. This is the CLI equivalent of the test runner's
`storageState` ([auth.md](auth.md)) and codegen's `--save-storage` / `--load-storage`
([tooling.md](tooling.md#codegen-record-tests)).

> The state file holds live session secrets — keep it out of version control (e.g. `.gitignore` it),
> exactly like test `storageState` files.

## Cookie / localStorage / sessionStorage commands

Finer-grained state control when you don't want the whole snapshot:

| Group | Commands |
|-------|----------|
| Cookies | `cookie-list [--domain] [--path]`, `cookie-get <name>`, `cookie-set <name> <value>`, `cookie-delete <name>`, `cookie-clear` |
| localStorage | `localstorage-list`, `localstorage-get <key>`, `localstorage-set <key> <value>`, `localstorage-delete <key>`, `localstorage-clear` |
| sessionStorage | `sessionstorage-list`, `sessionstorage-get <key>`, `sessionstorage-set <key> <value>`, `sessionstorage-delete <key>`, `sessionstorage-clear` (cleared when the tab closes) |

`cookie-set` options: `--domain`, `--path`, `--expires`, `--http-only`, `--secure`, `--same-site`.

## Sessions, dashboard & attach

**Named sessions** are isolated browser instances (own cookies, storage, history). The `-s` flag
selects one; `--persistent`/`--profile` keep the profile on disk across restarts.

```bash
playwright-cli -s=example open https://example.com --persistent
playwright-cli -s=example open https://example.com --profile=./my-profile
playwright-cli list                    # active sessions
playwright-cli -s=example close        # terminate one session
playwright-cli close-all               # close all browsers
playwright-cli kill-all                # force-kill unresponsive browsers
playwright-cli -s=example delete-data  # remove stored profile data
```

**Dashboard** — observe and control every running session (live screencast, navigation, remote
input):
```bash
playwright-cli show
```

**Attach / bind to an existing browser** — drive a browser you launched yourself instead of letting
the CLI start one. This is how you bind a browser launched via the Playwright **library**
([library-api.md](library-api.md)): launch it with a CDP/remote endpoint, then `attach`. Pairs well
with [debugging.md](debugging.md) (`PWDEBUG`, Inspector) and [trace-viewer.md](trace-viewer.md).

```bash
playwright-cli attach --cdp=chrome                  # by channel (chrome, chrome-canary, msedge, …)
playwright-cli attach --cdp=http://localhost:9222   # CDP endpoint (browser started with --remote-debugging-port=9222)
playwright-cli attach --endpoint=ws://localhost:3000 # connect to a Playwright server
playwright-cli attach --extension                   # via the browser extension (Chrome by default)
playwright-cli attach --extension=msedge            # extension on a specific channel
playwright-cli attach --cdp=chrome -s=debug-session # attach into a named session
```

> Note: the docs describe binding to an existing/library-launched browser through the **`attach`**
> command (CDP/WS endpoint or extension). A dedicated `browser.bind` library API could not be
> confirmed in the agent-cli docs, so it is not documented here.

## agent-cli vs the Playwright MCP server

Both let an AI drive a browser, but the integration model differs. The CLI is shell-command based;
the [MCP server](https://github.com/microsoft/playwright-mcp) exposes structured tools the model calls.

| | `playwright-cli` (agent-cli) | Playwright MCP server |
|---|---|---|
| Model interaction | Agent runs **shell commands** | LLM calls **MCP tools** with structured params |
| Token cost | Lower — concise output, skills loaded on demand | Higher — tool schemas + snapshots in context |
| Best for | Coding agents (Claude Code, Copilot) in large codebases | Specialized agentic loops, exploratory automation |

Prefer the CLI when you're already in a coding agent that can run shell commands and want to keep
context lean; reach for the MCP server when the host only speaks MCP tool-calls.

## agent-cli vs test runner

| | `playwright-cli` (agent-cli) | `@playwright/test` |
|---|---|---|
| Unit of work | One shell command per step | `*.spec.ts` files |
| Element targeting | Refs from `snapshot` (`e3`, `e5`) | Locators (`getByRole`, …) |
| Save login | `state-save` / `state-load` | `storageState` + setup project |
| Best for | AI agents, ad-hoc/interactive automation | Repeatable test suites, CI |

Don't mix the two models — element refs (`e5`) belong to the CLI; locators belong to the runner.
