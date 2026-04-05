---
name: skill types taxonomy
description: The 9 recurring categories of skills with examples, for planning what kind of skill to build
type: reference
---

# Skill Types Taxonomy

From Anthropic's internal catalog of hundreds of skills in active use. Most good skills fit cleanly into one category; confusing ones straddle several. Use this when planning a new skill to clarify scope and identify what's missing in an org's skill library.

## 1. Library & API Reference

Explains how to correctly use a library, CLI, or SDK — internal or third-party. Includes reference code snippets and a gotchas list for known failure modes.

**Examples:** `billing-lib` (internal edge cases), `internal-platform-cli` (subcommands with examples), `frontend-design` (design system taste, avoiding Inter/purple gradients)

---

## 2. Product Verification

Describes how to test or verify that code is working, paired with external tools (Playwright, tmux, etc.). Verification skills are high-leverage — one engineer spending a week on excellent verification skills pays outsized returns.

**Techniques:** record a video of Claude's output, enforce programmatic assertions at each step via scripts.

**Examples:** `signup-flow-driver` (signup → email verify → onboarding, headless browser with state assertions), `checkout-verifier` (Stripe test cards, invoice state), `tmux-cli-driver` (interactive CLI testing with TTY)

---

## 3. Data Fetching & Analysis

Connects to data and monitoring stacks. Includes libraries with credentials, dashboard IDs, and instructions for common query patterns.

**Examples:** `funnel-query` (which events to join for signup → activation → paid), `cohort-compare` (retention/conversion with significance testing), `grafana` (datasource UIDs, cluster names, problem → dashboard lookup)

---

## 4. Business Process & Team Automation

Automates repetitive workflows into one command. Often depends on other skills or MCPs. Storing results in log files helps the model stay consistent across repeated runs.

**Examples:** `standup-post` (ticket tracker + GitHub + Slack history → formatted standup), `create-<ticket>-ticket` (schema enforcement + post-creation workflow), `weekly-recap` (merged PRs + closed tickets + deploys)

---

## 5. Code Scaffolding & Templates

Generates framework boilerplate for a specific function in the codebase. Especially useful when scaffolding has natural-language requirements that can't be covered by code alone.

**Examples:** `new-<framework>-workflow` (service/workflow with your annotations), `new-migration` (migration template + gotchas), `create-app` (new internal app with auth, logging, deploy pre-wired)

---

## 6. Code Quality & Review

Enforces org-specific code quality and review. Can use deterministic scripts for maximum robustness. Good candidates for auto-running via hooks or GitHub Actions.

**Examples:** `adversarial-review` (fresh-eyes subagent that critiques, implements, iterates), `code-style` (styles Claude doesn't do well by default), `testing-practices` (how to write tests, what to test)

---

## 7. CI/CD & Deployment

Helps fetch, push, and deploy code. Often references other skills to collect data.

**Examples:** `babysit-pr` (monitors PR → retries flaky CI → resolves conflicts → enables auto-merge), `deploy-<service>` (build → smoke test → gradual rollout → auto-rollback), `cherry-pick-prod` (isolated worktree → cherry-pick → conflict resolution → PR)

---

## 8. Runbooks

Takes a symptom (Slack thread, alert, error signature) → multi-tool investigation → structured report.

**Examples:** `<service>-debugging` (symptoms → tools → query patterns), `oncall-runner` (fetch alert → check usual suspects → format finding), `log-correlator` (request ID → logs from every system that touched it)

---

## 9. Infrastructure Operations

Routine maintenance and operational procedures, especially ones involving destructive actions that benefit from guardrails.

**Examples:** `<resource>-orphans` (find orphans → Slack post → soak period → user confirms → cascading cleanup), `dependency-management` (org approval workflow), `cost-investigation` (why did storage/egress bill spike)
