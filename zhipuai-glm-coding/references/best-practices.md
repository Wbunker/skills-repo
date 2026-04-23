---
name: zhipuai-glm-best-practices
description: Official DevPack best practices and memory mechanism guide for GLM Coding Plan — task structuring, session management, project-level configuration, memory architecture, and rule writing for long-running coding agents.
type: reference
---

# Z.ai GLM Coding Plan — Best Practices

From the official DevPack best-practice and memory mechanism documentation.

---

## Task Input Structure

For complex requests, provide four elements every time:

| Element | What to include |
|---------|----------------|
| **Goal** | Clear description of what to build or change |
| **Context** | Relevant files, errors, docs, or examples |
| **Constraints** | Coding standards, architecture rules, security requirements |
| **Done when** | Completion criteria — tests passing, expected behavior |

Vague prompts produce exploratory behavior; structured prompts produce targeted implementation.

---

## Plan Before Executing

For non-trivial tasks, ask the agent to produce a plan first:
> "Before writing any code, explore the codebase, identify all affected files, and describe your approach. I'll confirm before you proceed."

This catches scope mismatches early and prevents large incorrect diffs. The planning phase should include codebase exploration and approach confirmation.

---

## Project-Level Configuration Files

Put long-lived rules in files, not prompts:
- Temporary instructions → prompt
- Long-lived rules → `.claude/` or project config files

**Recommended structure:**
```
.claude/
├── project.md          # global shared context (arch, build commands, test workflow)
└── rules/
    ├── code-style.md   # formatting, naming conventions
    ├── testing.md      # test frameworks, coverage requirements
    ├── api-design.md   # endpoint patterns, error handling
    └── security.md     # auth rules, input validation
```

Keep `project.md` under ~200 lines. Split into topic files when it grows beyond that.

**Rule writing — be concrete:**

| Avoid | Prefer |
|-------|--------|
| "Keep the code clean" | "Use 2-space indentation in TypeScript; run `pnpm test` after any logic change" |
| "Handle errors properly" | "Wrap all external API calls in try/catch; log to stderr; return null on failure" |
| "Follow security best practices" | "Never log request bodies; validate all user input with zod schemas" |

Specific, verifiable rules produce consistent behavior. Abstract principles are ignored.

---

## Session Management

- Use **separate sessions for unrelated tasks** — mixing contexts degrades reasoning quality
- **Avoid very long sessions** — excessive history increases latency and noise
- **Start a new session** when switching branches or starting a fundamentally different task
- **Periodically compress** context by summarizing earlier conversation into a fresh prompt

Rules and long-term context should live in files (loaded at session start), not in conversation history. Conversation history is lost after compression; files are reloaded from disk.

---

## Full Development Loop

Involve the agent in the entire cycle, not just code generation:

```
Requirements → Plan → Code → Tests → Test execution → Lint/checks → Review
```

Give the agent permission to run your build/test commands so it can verify its own output. An agent that can't run tests will produce code that looks plausible but fails silently.

---

## MCP Integration for External Context

Connect the agent to external systems via MCP to eliminate context-switching:
- Issue trackers (JIRA, Linear) — agent can read ticket requirements directly
- CI/CD systems — agent can check build status
- Databases — agent can query schema or sample data
- Documentation — use Web Reader / Zread MCP for live doc access

See `mcp-tools.md` for configuration.

---

## Memory Architecture

Z.ai's memory guide distinguishes two types:

**Instruction memory** — written by humans, stable:
- Coding standards, naming conventions, safety rules
- Lives in `.claude/rules/` files
- Changes infrequently; reviewed deliberately

**Learning memory** — accumulated from experience:
- Past bug fixes, failure patterns, debugging sequences
- Personal preferences, project habits
- Captured in session notes or auto-memory

Keep these separate. If experience-based notes modify core rules, the rules become unpredictable.

### Memory layers

| Layer | Scope | Where |
|-------|-------|-------|
| Organization | Company-wide | Shared rules repo, imported via `@path` |
| Project | Team-shared | `.claude/project.md`, version-controlled |
| User | Individual | `~/.claude/` personal config |
| Local | Machine-specific | Dev ports, test accounts, local overrides |

### Importing rules

`CLAUDE.md` supports imports:
```markdown
@.claude/rules/code-style.md
@.claude/rules/testing.md
```

Teams can share a `frontend-react-rules` or `python-testing-rules` package imported by reference. Use symlinks in `.claude/rules/` to share across repos.

---

## Packaging Repeated Workflows as Skills

If you run the same prompt pattern more than a few times (PR review, log analysis, release notes, migration scripts), capture it as a Claude Code skill. Skills are token-efficient (loaded on demand), composable, and version-controllable.

Stable, well-tested skills can be scheduled or triggered automatically — the agent runs in the background without manual invocation.

---

## Memory Troubleshooting

| Issue | Fix |
|-------|-----|
| Rules not being followed | Run `/memory` to verify `.md` files are loaded; check for vague or conflicting rules |
| Unknown auto-memory contents | Run `/memory` to view the auto-memory directory |
| Files too large | Split into multiple topic files; use imports |
| Instructions lost after compression | Move to `.md` files — conversation is ephemeral, files persist |
