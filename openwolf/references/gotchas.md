# Gotchas

## Licensing

**AGPL-3.0 license.** Derivative works must be released as open source under the same license. If embedding OpenWolf hooks or `.wolf/` tooling inside a commercial closed-source product, review license obligations before shipping. Projects that merely *use* OpenWolf as a development tool (not distributed with the product) are generally unaffected.

---

## Claude Code Exclusivity

OpenWolf hooks register in `.claude/settings.json` and use Claude Code's lifecycle events. They do not work with:
- Cursor
- Windsurf
- GitHub Copilot
- Any other AI coding tool

If a team uses mixed tooling, only the Claude Code sessions benefit from OpenWolf's token savings.

---

## Node.js Required for All Stacks

Hooks are Node.js scripts. Node.js 20+ must be installed globally even if the project is Python, Ruby, Go, or any other non-JS stack. This is an additional dependency for non-JS teams.

---

## Cerebrum Compliance Is Not Deterministic

cerebrum.md rules are enforced by Claude following instructions, not by code. Pre-write.js surfaces the Do-Not-Repeat list, but whether Claude adheres is probabilistic (~85–90% compliance rate). Do not rely on cerebrum enforcement for security or correctness-critical rules — use actual code linting/testing for those.

---

## Token Estimates Are Approximate

Token counts in anatomy.md and the token ledger use character-to-token ratio heuristics, not the actual API tokenizer. Accuracy is within ~15%. The ledger is useful for trends and relative comparisons, not for reconciling against Anthropic billing.

---

## Stale Anatomy After Bulk File Changes

anatomy.md is updated incrementally by `post-write.js` (one file at a time after writes). If you:
- Rename files outside Claude (e.g., via git, shell commands)
- Delete files
- Add many files via `git checkout`, `npm install` without exclusions, or a build step

...then anatomy.md will be stale. Run `openwolf scan` manually, or wait for the daemon's 6-hour rescan. Use `openwolf scan --check` in CI to detect staleness.

---

## Large Directories Must Be Excluded

`node_modules`, `.next`, `dist`, `build`, and similar generated directories can contain thousands of files. If not excluded, `openwolf init` and `openwolf scan` will be slow and anatomy.md will be enormous, degrading performance. Default exclude list covers common cases, but add project-specific generated directories to `config.json`.

---

## Hook Registration Is Lost If settings.json Is Reset

If `.claude/settings.json` is deleted or overwritten (e.g., another tool reinitializes it, or you reset Claude Code settings), the six hooks are unregistered. Symptoms: no anatomy hints, no repeated-read warnings. Fix: run `openwolf init` again — it re-registers hooks and is safe to run on an existing `.wolf/` directory (does not reset memory files).

---

## Hooks Do Not Fire on Non-Read/Write Tools

Only `Read` and `Write` tool calls are intercepted. OpenWolf does not intercept:
- `Bash` command execution
- `Edit` (partial file writes) — though the result may trigger PostToolUse/Write depending on Claude Code version
- File moves/renames via shell
- MCP tool calls

Token usage from bash execution is not tracked in the ledger.

---

## Early-Stage Project Maturity

OpenWolf is a relatively new project (single primary contributor, ~220 GitHub stars at initial review). File formats and hook APIs may change across versions. After `npm update -g openwolf`, run `openwolf update` to refresh hook scripts in all projects. Check the GitHub changelog before updating in active projects.

---

## Dashboard Requires Running Daemon or Foreground Process

`openwolf dashboard` starts a web server at port 18791. In CI environments or remote servers without port forwarding this is inaccessible. For persistent access, enable the daemon with PM2 (`daemon.usePM2: true` in config.json).

---

## OPENWOLF.md Can Be Overwritten by openwolf update

`OPENWOLF.md` (session instruction file) is managed by OpenWolf. If you make custom edits to it, `openwolf update` may overwrite them. Store project-specific instructions in `identity.md` or `cerebrum.md` instead — those are not touched by updates.

---

## Performance Claims Are Averages, Not Guarantees

- 65.8% average token reduction is measured across 20 projects, 132 sessions
- The ~80% reduction figure is from a single large project
- Projects with few repeated reads (e.g., short focused sessions, small codebases) will see smaller gains
- Projects with massive codebases and frequent cross-file navigation benefit most
