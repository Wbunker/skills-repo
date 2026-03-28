# Documentation Plan: New Open Source Python Library

You are at **Phase 2: Open Source Launch** in the documentation lifecycle. You have working code and want contributors and AI tools to be able to engage effectively. Here is what to create and in what order.

---

## Priority Order

### Wave 1 — Do This Before Announcing (Critical)

These are the minimum viable set. Without them, contributors cannot engage and GitHub will flag your project as incomplete in its Community Standards checklist.

**1. README.md**

The entry point for every visitor. Structure it as a navigation hub, not a documentation dump:

```
# logparse

One-sentence description: what it parses, for whom.

## Quickstart
pip install logparse

from logparse import LogParser
parser = LogParser()
records = parser.parse("2024-01-15 ERROR Failed to connect: timeout")
```

Include: what it does, installation, a minimal usage example, link to docs/. Do not put your entire API reference here — link to it instead.

**2. LICENSE**

Pick an SPDX-identified license (MIT, Apache-2.0, etc.) and add the file. GitHub surfaces this prominently. Without it, nobody can legally use your library.

**3. CLAUDE.md** (and/or AGENTS.md)

Since you are using AI tools, this is critical. A minimal CLAUDE.md for a Python library looks like:

```markdown
## Stack
- Python 3.11+, no required external dependencies
- Testing: pytest
- Type checking: mypy
- Linting: ruff

## Commands
- Install dev: `pip install -e ".[dev]"`
- Test: `pytest tests/ -v`
- Test single: `pytest tests/test_parser.py -v`
- Type check: `mypy src/`
- Lint: `ruff check src/`
- All checks: `make ci`

## Structure
- `src/logparse/` — library source
- `tests/` — pytest test suite
- `docs/` — documentation

## Conventions
- All public functions must have type annotations
- All public functions must have docstrings
- Parser classes must implement the `BaseParser` interface (see src/logparse/base.py)
```

Keep it under 150 lines. Only document things that deviate from standard Python conventions or that Claude would get wrong without the hint.

---

### Wave 2 — Before First External Contributors (High Priority)

**4. CONTRIBUTING.md**

GitHub links to this automatically when someone opens an issue or PR. Include:
- How to set up a dev environment (exact commands)
- How to run the test suite
- How to submit a bug report vs. feature request
- PR requirements (tests required, docs updated if behavior changes)
- Code style (point to your linter config; don't restate PEP 8)

**5. SECURITY.md**

Tells security researchers how to report vulnerabilities privately. GitHub displays this in the Security tab. Critical for any public package. Minimum content: supported versions table, private disclosure email or GitHub private advisory link, response time commitment.

**6. CODE_OF_CONDUCT.md**

The Contributor Covenant (https://www.contributor-covenant.org/) is the standard. Copy it verbatim. This signals that your project is welcoming and is required for GitHub's Community Standards checklist.

**7. CHANGELOG.md**

Start it now, even if you only have an `[Unreleased]` section. Use the Keep a Changelog format (Added / Changed / Deprecated / Removed / Fixed / Security). Update it with every release.

---

### Wave 3 — As the Codebase Grows (High Value)

**8. Module-level docstrings on every .py file**

This is the most direct way to make your codebase understandable to AI tools. When Claude opens a file, the first thing it reads is the module docstring. Each file should state its purpose, main exports, and relationships to adjacent modules:

```python
"""
Core log record parser.

Parses structured log lines into LogRecord objects.
Supports Common Log Format (CLF), JSON logs, and custom patterns.

Main entry point: LogParser.parse(line) -> LogRecord
See also:
  - logparse/formats.py — format definitions
  - logparse/models.py — LogRecord dataclass
"""
```

**9. Type annotations on all public functions**

Type annotations are documentation that tools can verify. Without them, AI tools and human contributors must read the full implementation to understand what a function accepts and returns:

```python
# Before — AI must read the full body to understand this
def parse(self, line, strict=False):
    ...

# After — interface is immediately clear
def parse(self, line: str, strict: bool = False) -> LogRecord:
    ...
```

**10. ARCHITECTURE.md** (or `docs/ARCHITECTURE.md`)

Once you have more than ~5 modules, write a brief component map. Describe what each module does and how they relate. Include a text-based data flow diagram. This prevents AI tools from generating code that misunderstands the structure.

For a log parsing library this might be very short (5–10 modules), but it is still valuable:

```markdown
## Components

| Module | Responsibility |
|--------|---------------|
| `logparse/parser.py` | Entry point; dispatches to format-specific parsers |
| `logparse/formats.py` | Format definitions (CLF, JSON, syslog, custom) |
| `logparse/models.py` | LogRecord dataclass and related types |
| `logparse/errors.py` | Custom exception hierarchy |

## Data Flow
raw string → parser.py → format detection → format-specific parser → LogRecord
```

---

### Wave 4 — When Users Start Asking Questions (Medium Priority)

**11. `.github/ISSUE_TEMPLATE/` (bug report + feature request)**

Issue templates improve the quality of incoming reports dramatically. Add a bug report template that requires OS, Python version, library version, and a minimal reproducing example.

**12. `.github/PULL_REQUEST_TEMPLATE.md`**

Pre-fills PR descriptions to prompt contributors to describe their change, list what they tested, and confirm they updated CHANGELOG.md.

**13. How-to guides in `docs/guides/`**

When the same question appears more than twice in issues, write a how-to guide. Examples for a log parser:
- "How to add a custom log format"
- "How to parse multi-line log entries"
- "How to integrate with Python's logging module"

These are Diataxis **how-to guides**: assume competence, give steps, skip the backstory.

**14. API reference**

Generate it from your docstrings using Sphinx + autodoc or pdoc. Host it on GitHub Pages or ReadTheDocs. Link to it from your README. This is especially valuable for AI tools because it provides a searchable, structured description of every public interface.

---

## Summary Table

| Document | Wave | Why It Matters for Contributors | Why It Matters for AI |
|----------|------|--------------------------------|----------------------|
| README.md | 1 | Entry point; orientation | First file loaded; sets context |
| LICENSE | 1 | Legal requirement to contribute | N/A |
| CLAUDE.md | 1 | — | Loads project context every session |
| CONTRIBUTING.md | 2 | Tells them exactly how to contribute | Dev setup commands |
| SECURITY.md | 2 | Safe disclosure path | N/A |
| CODE_OF_CONDUCT.md | 2 | Signals welcoming project | N/A |
| CHANGELOG.md | 2 | Shows project is maintained | N/A |
| Module docstrings | 3 | Orient new contributors to each file | Loaded automatically when file is opened |
| Type annotations | 3 | Clarifies interfaces | AI understands structure without reading implementations |
| ARCHITECTURE.md | 3 | System map for new contributors | Prevents AI from generating wrong-layer code |
| Issue templates | 4 | Better bug reports | N/A |
| PR template | 4 | Consistent PR quality | N/A |
| How-to guides | 4 | Solve recurring questions | Reference material for specific tasks |
| API reference | 4 | Comprehensive interface docs | Structured lookup without reading source |

---

## One Anti-Pattern to Avoid

Do not put everything in the README. A common mistake is writing a 3,000-word README that combines installation instructions, conceptual explanation, full API reference, and contributor guide in one file. Nobody reads it, and AI tools load all of it into context on every session even when most of it is irrelevant.

Use the README as a **navigation hub**: brief description, quickstart, then links to `docs/` for everything else.
