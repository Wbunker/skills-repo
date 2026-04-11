# BMAD Method Reference

**GitHub:** https://github.com/bmad-code-org/BMAD-METHOD  
**Stars:** ~44k | **License:** MIT | **Latest:** v6.x  
**Full name:** Breakthrough Method for Agile AI-Driven Development

## Core Concept: Agent-as-Code

Agents are defined as structured YAML source files (`.agent.yaml`) compiled into Markdown for IDE consumption. Each agent is version-controllable with: persona definition, role identity, communication style, capability list, and an invokable menu. On activation, each agent follows a 9-step protocol ending with **HALT and WAIT** — no unsolicited generation.

## Persona System (12+ agents)

| Persona | Role |
|---|---|
| BMAD Master | Orchestration / routing |
| Analyst | Problem space exploration |
| Product Manager | PRD creation |
| Architect | System design |
| UX Designer | User experience |
| Scrum Master | Sprint management |
| Product Owner | Backlog prioritization |
| Developer | Implementation |
| QA Engineer | Test strategy |
| Tech Writer | Documentation |

Optional domain modules add game dev, creative, and enterprise personas.

## Four-Phase Workflow

| Phase | Outputs | Tracks |
|---|---|---|
| 1. Analysis | Product brief, research docs | All |
| 2. Planning | PRD, UX specifications | Standard, Enterprise |
| 3. Solutioning | Architecture doc, epics, stories | All |
| 4. Implementation | Working code, test coverage | All |

**Three tracks:**
- **Quick Flow** — bug fixes / small features (1–15 story scope, under 5 min setup)
- **Standard** — greenfield MVPs
- **Enterprise** — compliance-heavy or large-scale systems

Implementation readiness quality gate occurs between Solutioning and Implementation phases.

## Party Mode

Activate with `bmad-party-mode`. Multiple personas collaborate in a single session. The BMAD Master orchestrates, selecting which agents respond per message. Agents stay in character, agree/disagree, and build on each other's responses.

**Best for:** Major architectural trade-offs, brainstorming, retrospectives, post-mortems.  
**Not efficient for:** Routine single-perspective tasks.  
**Known issue:** "Lost-in-the-middle workflow failures" in long sessions (issue #1319 — Return Protocol fix proposed).

## Installation & Key Commands

```bash
# Install
npx bmad-method install
npx bmad-method@next install                    # prerelease
npx bmad-method install --directory /path --modules bmm --tools claude-code --yes

# In-IDE commands
bmad-help             # universal guidance
bmad-party-mode       # activate Party Mode
bmad-pm               # activate Product Manager persona
bmad-dev              # activate Developer persona
bmad-architect        # activate Architect persona
bmad-create-prd       # run PRD creation workflow
bmad-dev-story        # run story development workflow
bmad-code-review      # run code review workflow
```

**Requirements:** Node.js v20+, Python 3.10+, `uv` package manager.

## When to Use BMAD

- Greenfield product development with multiple stakeholders
- Need audit trails and compliance documentation
- Want role-based AI collaboration with defined artifact handoffs
- Full lifecycle coverage: idea → architecture → stories → code → QA
- Documentation must persist across sessions

**Skip for:** Quick one-off fixes, exploratory prototyping, when artifact overhead outweighs benefit.

## Gotchas

### Token and Cost Reality
- **80–100x token overhead vs. unassisted Claude.** Single `create-story` runs consume 80k–100k tokens during analysis. One user on the $100/mo Max plan hit daily rate limits. (Issue #1235, Discussion #267)
- **The TEA agent alone can consume 86% of a 200k context window** (571 KB / ~143k tokens), leaving only ~14% for actual task work. DEV and SM agents each consume another 10–11% on activation. (Issue #1343)
- **Estimated enterprise cost:** ~$847/month in API costs and ~230M tokens/week at scale, per one comparative analysis.

### Workflow Correctness Failures
- **Stories marked complete but feature is broken.** Agents mark acceptance criteria as met without functionally verifying them — a documented case had authentication broken while all stories were flagged done; team spent 9+ hours discovering it. (Issue #2003)
- **Code review enforces a minimum of 3 issues regardless of code quality.** The workflow validates `total_issues_found >= 3`, forcing the LLM to manufacture nitpicks on production-ready code. (Issue #1332)
- **Deferred work items are write-only.** `bmad-code-review` writes security fixes and critical bugs to `deferred-work.md`, but no workflow ever reads this file. After 10+ stories, a silent backlog of 30–40 items accumulates. (Issue #2199)
- **`quick-dev` silently drops parent-artifact requirements.** Functional requirements from parent epics/PRDs can be omitted during decomposition with no warning. (Issue #2167)
- **Quick Dev flow doesn't generate tests** even with explicit `CLAUDE.md` instructions demanding them. (Issue #2208)
- **Infinite review loops with no exit condition.** When shallow fixes are reopened by review agents, the system cycles back indefinitely. (Issue #2003)

### Agent Reliability
- **Dev agent ignores its own config files.** `devLoadAlwaysFiles` (coding-standards, tech-stack, source-tree) is inconsistently loaded — behavior is non-deterministic. (Issue #387)
- **Agent goal drift during investigation.** Documented case: Dev agent "became so engrossed in technical analysis that the main objective was forgotten." (Issue #446)
- **Data fabrication under timeout.** When a shell command timed out, the agent substituted wrong output and reported incorrect facts with no error surfaced. (Issue #446)
- **Installed Superpowers skills can intercept BMAD slash commands**, causing Claude to impersonate BMAD agents rather than executing the actual command. (Issue #1785)

### Brownfield / Existing Codebase
- **Context window exhaustion is almost guaranteed on brownfield projects.** Ingesting existing code competes directly with task context; architectural constraints are routinely "forgotten" mid-task. (Issue #1471)
- **No support for parallel feature work.** All artifacts assume a single monolithic project — story files have no feature tag, parallel feature development is structurally unsupported. (Issue #446)
- **Workflow deadlocks in story approval.** SM creates stories in "Draft" but has no `approve-story` command; PO cannot change story status; Dev refuses to work on Drafts. (Issue #446)

### Structural Design Limits
- **"10–15x the time" for small MVPs** with negligible quality benefit vs. traditional methods, per one practitioner. (Issue #2003)
- **Learning curve measured in months.** ~2 months to master vs. 1–2 days for comparable tools. Requires proficiency with CLI, YAML, and 6–7 agent personas.
- **The "accessible to non-technical users" claim fails in practice.** Non-technical users can't evaluate AI-generated code; technical users find code they didn't write hard to assess. The two target audiences are structurally incompatible. (Issue #2003)

### Version and Platform
- **v4 → v6 upgrade breaks in-progress projects** — directory renames, agent format changes, missing files. Only previous 2 alpha versions are supported for upgrade. (Issue #838)
- **Cursor caps at 8 custom agent slots** with 3 defaults pre-occupied, leaving only 5 — BMAD needs 7. Planning must move outside Cursor entirely.
- **Windows/WSL path and line-ending incompatibilities.** Hook scripts fail silently; `jq` dependency missing on Linux is not auto-installed.
- Large documents must use "sharded" structure (index.md + section files) — whole-file context mode degrades.
- Optional modules (BMGD, CIS, TEA) require network access at install time.
