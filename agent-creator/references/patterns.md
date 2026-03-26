# Agent Patterns

Common agent archetypes with real examples from this project.

---

## Pattern 1: Background Worker (Parallel Dispatch)

An agent that runs in the background, processes a single unit of work (one file, one task),
and reports a minimal result back to the orchestrator. Designed to be spawned in bulk.

**Key config**: `background: true`, `permissionMode: acceptEdits`, specific `tools`, preloaded `skills`

**Output contract**: Define a minimal one-line format for orchestrator mode and a full format for direct invocation.

```markdown
---
name: css-bug-squasher
description: Squashes page-specific CSS overrides... Use proactively when a page or component
  needs CSS cleanup. When called by the squash-css orchestrator command, reports back only a
  single DONE line to preserve orchestrator context.
tools: Read, Edit, Grep, Glob, Bash
model: sonnet
permissionMode: acceptEdits
background: true
skills:
  - css-bug-squashing
---

You are a CSS bug squasher for the ResultMaps Web UI 2 project...

## Input

You will be given a file path, e.g.: `app/(public)/oauth/login/page.tsx`

## Instructions

1. Read the target file
2. Grep for override candidates
3. Triage — classify as safe or override
4. Apply fixes
5. Verify build passes: `npm run build 2>&1 | tail -20`

## Output format

**When invoked by the orchestrator** (prompt contains "report back ONLY"):
\`\`\`
DONE: <file-path> — <N> fixes applied
\`\`\`

**When invoked directly**: Return the full FIXED/SKIPPED/BUILD report.
```

**Orchestrator side** (in the command that spawns this agent):
- Use `allowed-tools: Glob, Grep, Agent, Read`
- Dispatch all agents before waiting for any
- Instruct agents to "report back ONLY" the minimal line

---

## Pattern 2: Read-Only Specialist (Analysis/Research)

An agent that only reads and analyzes — never writes. Use `disallowedTools` as a safety
net, or simply omit `Write` and `Edit` from `tools`.

```markdown
---
name: code-reviewer
description: Reviews code for quality and best practices. Use proactively after code changes,
  before committing, or when asked to review a file or function.
tools: Read, Glob, Grep, Bash(git *)
model: sonnet
permissionMode: default
---

You are a senior code reviewer ensuring high standards of code quality and security.

When invoked:
1. Run `git diff HEAD~1` to see recent changes
2. Focus on modified files
3. Check for: security issues, logic errors, missing error handling, code smells
4. Report findings as CRITICAL / HIGH / MEDIUM / LOW with file:line references
```

---

## Pattern 3: Mechanical Fixer (Low-Judgment, High-Volume)

An agent that applies deterministic fixes across many files. Use a fast/cheap model
(`haiku`), `acceptEdits` permission, and tight tool restrictions.

**Key config**: `model: haiku`, `permissionMode: acceptEdits`, narrow `tools`

```markdown
---
name: python-flake8-fixer
description: Use this agent when you need to run flake8 linting on Python code and
  automatically fix the violations it identifies. Call when: writing or modifying Python
  code, preparing for a commit, receiving flake8 CI failures, or enforcing PEP 8 standards.
model: haiku
permissionMode: acceptEdits
color: green
---

You are an elite Python code quality specialist...

## Workflow

1. Run `pre-commit run --all-files flake8` to identify all violations
2. Categorize by type and severity
3. Fix in priority order: syntax errors → import issues → whitespace → line length
4. Re-run flake8 to verify zero violations
5. Report: total fixed, breakdown by type
```

---

## Pattern 4: Orchestrator Agent (Spawns Sub-Agents)

An agent that itself spawns other agents. Requires `Agent` (or `Agent(name1, name2)`) in `tools`.

```markdown
---
name: full-reviewer
description: Runs a complete multi-stage code review: security scan, then style check,
  then performance analysis. Use when preparing a release or reviewing a large PR.
tools: Read, Bash(git *), Agent(security-scanner, style-checker, perf-analyzer)
model: opus
---

You are a full-review orchestrator.

1. Run `git diff main...HEAD --name-only` to get the changed files
2. Dispatch `security-scanner` agent for security review
3. Dispatch `style-checker` agent for style/quality review
4. Dispatch `perf-analyzer` agent for performance review
5. Wait for all three results
6. Synthesize into a single prioritized report
```

---

## Pattern 5: Skill-Augmented Agent

An agent that explicitly preloads domain knowledge from one or more skills. Agents don't
inherit the parent conversation's loaded skills — you must declare them in `skills:`.

```markdown
---
name: feature-implementer
description: Implements a feature task from the spec, following project conventions.
  Invoked by speckit:implement for individual task execution.
tools: Read, Write, Edit, Glob, Grep, Bash
model: sonnet
permissionMode: acceptEdits
skills:
  - site-context
  - test-driven-development
---

You are implementing a specific feature task for the ResultMaps Web UI 2 project.

Your task details will be provided in the prompt. Follow these steps:

1. Read any files listed as "Modify" in the task before touching them
2. Invoke @test-driven-development before writing implementation code
3. Implement exactly what the task specifies — no more, no less
4. Run `npm run build` and `npm test` to verify
5. Report: files changed, tests added, build status
```

---

## Anti-Patterns to Avoid

- **No `background: true` on bulk workers** — orchestrator blocks waiting for each agent serially
- **No output contract** — agents for orchestrators must have a documented minimal response format to prevent context bloat
- **Using `opus` for mechanical tasks** — `haiku` or `sonnet` is sufficient for linting/formatting/search tasks; save `opus` for reasoning-heavy work
- **Broad tools on sensitive agents** — an agent with `Write` that's supposed to only read can corrupt files; be explicit
- **Forgetting `skills:`** — agents don't inherit parent skills; always declare needed skills explicitly
- **Over-broad `description`** — "Does everything" will cause Claude to delegate tasks that shouldn't go to this agent; be specific about what input this agent expects
- **Long-running agent without `maxTurns`** — add `maxTurns: N` for agents processing open-ended inputs to prevent runaway loops
