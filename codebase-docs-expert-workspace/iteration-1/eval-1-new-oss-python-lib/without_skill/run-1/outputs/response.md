# Documentation for a New Open Source Python Library

## Overview

For a new OSS Python library at the `src/` + `setup.py` stage, you need documentation that serves three audiences: users, contributors, and AI tooling. The order below is roughly "highest ROI first" — each layer builds on the previous one.

---

## Phase 1: Foundation (Do These First)

### 1. README.md

The single most important file. It is the first thing everyone reads — humans and AI tools alike.

**Minimum viable content:**
- One-sentence description of what the library does
- Installation instructions (`pip install ...`)
- A short "Getting started" code example showing the most common use case
- Link to full docs (even if docs don't exist yet, note "coming soon")
- License badge

**Why first:** GitHub, PyPI, and AI tools all surface the README as the primary entry point. A sparse README signals an abandoned or unreliable project.

---

### 2. LICENSE

Pick a license (MIT, Apache 2.0, or GPL) and add the `LICENSE` file. Without it, the code is legally all-rights-reserved by default, which blocks contributors and corporate adopters.

**Why second:** Blocks contribution entirely if missing.

---

### 3. CONTRIBUTING.md

Tells contributors how to get started, how to submit changes, and what the process looks like.

**Minimum viable content:**
- How to set up a local development environment (clone, create venv, `pip install -e .[dev]`)
- How to run tests (`pytest`, `tox`, etc.)
- Branch and PR conventions (e.g., "one feature per PR", "squash merges")
- Code style and linting requirements (e.g., `black`, `ruff`, `mypy`)
- How to report bugs vs. propose features

**Why third:** Without this, well-meaning contributors hit friction and give up. It also sets expectations, reducing low-quality PRs.

---

## Phase 2: Machine-Readable Structure (Especially for AI Tooling)

### 4. CLAUDE.md (or equivalent AI context file)

If you want AI tools like Claude to understand your codebase, a `CLAUDE.md` at the repo root is the canonical way to do this for Claude Code. Other tools have analogous files (e.g., `.cursorrules` for Cursor).

**What to put in it:**
- Project purpose in one paragraph — what problem does this library solve?
- Directory layout with one-line descriptions of each folder and key file
- Key architectural decisions (e.g., "parsers are implemented as subclasses of `BaseParser`")
- Development commands: how to install, test, lint, build docs
- Any non-obvious conventions (e.g., "log format plugins go in `src/parsers/`")
- What NOT to do (gotchas, anti-patterns specific to this codebase)

**Example structure for your case:**
```
## Project
Python library for parsing structured log files.

## Layout
src/
  logparse/
    __init__.py       - Public API surface
    core.py           - BaseParser and shared parsing logic
    formats/          - One module per log format (JSON logs, syslog, etc.)
    utils.py          - Shared helpers
tests/
setup.py              - Package metadata

## Key Concepts
- All parsers extend BaseParser (src/logparse/core.py)
- Parsers are registered via the PARSER_REGISTRY dict
- Parse results are always LogRecord dataclass instances

## Dev Commands
pip install -e .[dev]   # install with dev dependencies
pytest                  # run tests
ruff check src/         # lint
mypy src/               # type check
```

**Why this matters for AI:** Claude Code loads `CLAUDE.md` automatically when opening a project. The more precise your descriptions of architecture and conventions, the more accurate AI-generated code suggestions will be. Vague or missing context leads to AI suggestions that fight your codebase structure.

---

### 5. Inline docstrings (public API)

Write docstrings for every public function, class, and method. Use Google style or NumPy style — pick one and be consistent.

**Minimum for each public symbol:**
- One-line summary
- `Args:` with types and descriptions
- `Returns:` description
- `Raises:` if relevant
- A short example in `Examples:` if the usage is non-obvious

**Why this phase:** Docstrings feed into auto-generated API docs, are surfaced by IDEs, and are read directly by AI tools when they inspect your code. They are the lowest-overhead way to document behavior close to the source of truth.

---

## Phase 3: Contributor Support

### 6. CHANGELOG.md (or use GitHub Releases)

Even at v0.1, start a changelog. Use [Keep a Changelog](https://keepachangelog.com/) format.

**Why:** Shows the project is alive. Contributors and users track it to understand what changed between versions.

---

### 7. Issue and PR templates (.github/)

Create `.github/ISSUE_TEMPLATE/bug_report.md` and `.github/PULL_REQUEST_TEMPLATE.md`.

**Bug report template minimum:**
- Describe the bug
- Steps to reproduce
- Expected vs. actual behavior
- Python version, OS, library version

**PR template minimum:**
- What does this PR do?
- How was it tested?
- Checklist: tests added, docs updated, changelog entry

**Why:** Dramatically reduces the back-and-forth on issues and PRs. Keeps quality consistent as the contributor base grows.

---

### 8. Code of Conduct

Add `CODE_OF_CONDUCT.md`. The [Contributor Covenant](https://www.contributor-covenant.org/) is the standard boilerplate. Copy-paste it; do not write your own.

**Why:** Expected by GitHub's community health checklist. Signals that the project is welcoming and well-maintained.

---

## Phase 4: User-Facing Docs (Once API Stabilizes)

### 9. API Reference docs

Generate from docstrings using `sphinx` + `autodoc`, or `mkdocs` + `mkdocstrings`. Host on Read the Docs or GitHub Pages.

Do this after your public API is reasonably stable — rewriting generated docs every release is expensive.

---

### 10. How-to guides and tutorials

Narrative documentation covering:
- "How to parse a syslog file"
- "How to write a custom parser plugin"
- "How to integrate with logging frameworks"

These are separate from the API reference and docstrings. Use the [Diátaxis framework](https://diataxis.fr/) to keep tutorials, how-tos, explanations, and reference clearly separated.

---

## Summary Table

| Priority | File/Dir | Audience | Effort |
|----------|----------|----------|--------|
| 1 | README.md | Everyone | Low |
| 2 | LICENSE | Contributors, legal | Trivial |
| 3 | CONTRIBUTING.md | Contributors | Low |
| 4 | CLAUDE.md | AI tools, devs | Low |
| 5 | Inline docstrings | Users, AI, IDEs | Medium |
| 6 | CHANGELOG.md | Users, contributors | Low (ongoing) |
| 7 | .github/ templates | Contributors | Low |
| 8 | CODE_OF_CONDUCT.md | Contributors | Trivial |
| 9 | API reference site | Users | Medium (after API stabilizes) |
| 10 | Guides/tutorials | Users | High (later) |

---

## One Practical Note on AI Tooling

The combination of a thorough `CLAUDE.md` + accurate docstrings on your public API surface is the highest-leverage investment for making AI assistants useful on your codebase. Architecture context in `CLAUDE.md` prevents AI from generating code that is structurally incompatible with your design. Docstrings close to the code keep the context accurate as the code evolves. Relying solely on one or the other leaves gaps.
