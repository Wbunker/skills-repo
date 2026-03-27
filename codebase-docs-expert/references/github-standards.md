# GitHub Repository Documentation Standards
## README Anatomy, Community Health Files, GitHub Surfaces, and Repo Structure

---

## Files GitHub Surfaces Automatically

GitHub provides special treatment to certain files — rendering them prominently or linking to them in key workflows:

| File / Path | Where GitHub Uses It |
|-------------|---------------------|
| `README.md` (root, `.github/`, or `docs/`) | Rendered on the repository homepage |
| `CONTRIBUTING.md` | Linked in the "new issue" and "new PR" flows |
| `CODE_OF_CONDUCT.md` | Surfaced in the Community Standards checklist |
| `SECURITY.md` | Displayed in the "Security" tab |
| `LICENSE` | Displayed prominently with SPDX identifier |
| `.github/ISSUE_TEMPLATE/` | Templates offered when opening a new issue |
| `.github/PULL_REQUEST_TEMPLATE.md` | Pre-fills new PR description |
| `.github/CODEOWNERS` | Enables automatic reviewer assignment |
| `CITATION.cff` | Provides citation information for academic/research projects |

### The `.github/` Directory

The `.github/` directory is the conventional home for GitHub-specific configuration:

```
.github/
├── ISSUE_TEMPLATE/
│   ├── bug_report.md
│   ├── feature_request.md
│   └── config.yml          ← disable blank issues, add external links
├── PULL_REQUEST_TEMPLATE.md
├── CODEOWNERS
├── workflows/              ← GitHub Actions
│   ├── ci.yml
│   └── release.yml
└── copilot-instructions.md ← Copilot AI context (optional)
```

### Organization-Wide Defaults

Create a `.github` repository in your GitHub organization to define default community health files that apply to all repos with no overrides:

```
<org>/.github/
├── CODE_OF_CONDUCT.md
├── CONTRIBUTING.md
├── SECURITY.md
└── ISSUE_TEMPLATE/
    └── bug_report.md
```

Individual repos can override any of these files by adding their own. This is the right mechanism for enforcing consistent standards at scale without copy-pasting files across repos.

---

## README Anatomy

The README is the first thing every visitor sees. It must answer "what is this?" in seconds and provide a clear path to the next thing each type of visitor needs.

### Recommended Structure

```markdown
# Project Name

One-sentence description of what this project does and for whom.

[Badges: build status, version, license, coverage] ← optional

[Screenshot or animated GIF] ← dramatically improves comprehension for UI projects

## Why

What problem does this solve? Why should someone use it?
(2–4 sentences; skip for internal tools where the audience already knows)

## Quickstart

The minimum steps to get something running. Concrete commands.

```bash
npm install
npm run dev
# → Server running at http://localhost:3000
```

## Installation

Detailed setup if quickstart is insufficient.

## Usage

Concrete examples. Show, don't tell.

```python
from mylib import Client
client = Client(api_key="...")
result = client.process("hello world")
```

## Configuration

Key configuration options. Link to full reference if large.

## Documentation

Links to architecture docs, API reference, tutorials, guides.

## Contributing

Brief note pointing to CONTRIBUTING.md.

## License

SPDX identifier and link to LICENSE file.
```

### README Constraints

- GitHub truncates README display at **500 KiB**
- Keep the README focused — use it as a **navigation hub**, not a documentation dump
- Move detailed content to `docs/` with links from the README
- **Mobile readers**: structure for scanning, not reading. Most visitors read READMEs on mobile.

### What NOT to Put in the README

- Your entire API reference
- Long tutorials (link to them instead)
- Changelog history (link to CHANGELOG.md)
- Detailed architecture (link to ARCHITECTURE.md)
- Content only relevant to contributors (link to CONTRIBUTING.md)

---

## CONTRIBUTING.md

The CONTRIBUTING.md tells potential contributors how to engage with your project. GitHub links to it automatically in the new issue and new PR flows.

### Minimum Content

```markdown
# Contributing

## How to report a bug
[Link to issue template or describe process]

## How to suggest a feature
[Process for feature requests]

## Development setup
1. Fork and clone the repo
2. `npm install`
3. `npm test` — all tests should pass
4. Create a branch: `git checkout -b feat/my-feature`

## Submitting a pull request
- One feature or fix per PR
- Tests required for new functionality
- Update docs if you change behavior
- Reference any related issues

## Code style
[Describe or link to style guide; mention linter commands]

## Review process
[How long to expect; what's required for merge]
```

---

## SECURITY.md

GitHub displays SECURITY.md in the Security tab and creates a private disclosure channel. This file is critical for any public project.

### Minimum Content

```markdown
# Security Policy

## Supported Versions

| Version | Supported |
|---------|-----------|
| 2.x     | Yes       |
| 1.x     | No        |

## Reporting a Vulnerability

**Do not open a public GitHub issue for security vulnerabilities.**

Email security@example.com with:
- Description of the vulnerability
- Steps to reproduce
- Potential impact

We will respond within 48 hours and keep you updated on our progress.
```

---

## CHANGELOG.md

Following [Keep a Changelog](https://keepachangelog.com/) format enables parsing by tools and humans alike.

```markdown
# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

## [2.1.0] - 2024-03-15

### Added
- New `retry` option for API calls

### Changed
- `Client.connect()` now accepts a timeout parameter

### Fixed
- Memory leak when connection fails (#123)

### Deprecated
- `Client.connect_legacy()` — will be removed in 3.0

## [2.0.0] - 2024-01-10
...
```

**Categories:** Added, Changed, Deprecated, Removed, Fixed, Security

---

## Issue Templates

Issue templates dramatically improve the quality of bug reports and feature requests.

### Bug Report Template (`.github/ISSUE_TEMPLATE/bug_report.md`)

```markdown
---
name: Bug report
about: Create a report to help us improve
labels: bug
---

## Describe the bug
A clear description of what the bug is.

## To Reproduce
1. ...
2. ...
3. See error

## Expected behavior
What you expected to happen.

## Environment
- OS: [e.g. macOS 14]
- Version: [e.g. 2.1.0]
- [Any other relevant context]

## Logs / screenshots
```

### Feature Request Template

```markdown
---
name: Feature request
about: Suggest an idea for this project
labels: enhancement
---

## Problem
What problem would this feature solve? Who experiences it?

## Proposed solution
What would you like to happen?

## Alternatives considered
What alternatives have you considered?

## Additional context
```

### Disabling Blank Issues

Add `.github/ISSUE_TEMPLATE/config.yml`:

```yaml
blank_issues_enabled: false
contact_links:
  - name: Security vulnerability
    url: https://github.com/org/repo/security/advisories/new
    about: Please report security vulnerabilities through GitHub's private disclosure
```

---

## CODEOWNERS

CODEOWNERS enables automatic reviewer assignment and protects critical paths.

```
# Default owner for everything
*                   @org/team-core

# Backend services
/backend/           @alice @bob
/backend/auth/      @alice  # auth requires Alice specifically

# Frontend
/frontend/          @carol @dave

# Infrastructure
/infra/             @ops-team

# Documentation (anyone can review, but tag docs team)
/docs/              @org/team-docs
```

Paths match using the same pattern syntax as `.gitignore`. CODEOWNERS is evaluated from bottom to top — the last matching rule wins.

---

## Pull Request Template

`.github/PULL_REQUEST_TEMPLATE.md` pre-fills new PR descriptions.

```markdown
## Summary
<!-- What does this PR do? Link to issue if applicable. -->

## Changes
<!-- Brief list of what changed -->

## Testing
<!-- How was this tested? What new tests were added? -->
- [ ] Unit tests added/updated
- [ ] Integration tests pass
- [ ] Manual test steps documented

## Documentation
- [ ] CHANGELOG.md updated
- [ ] Docs updated if behavior changed

## Screenshots (if UI change)
```

---

## Wikis vs. `docs/` vs. GitHub Pages

| Option | Best For | Trade-offs |
|--------|---------|-----------|
| `docs/` in repo | Docs that should be reviewed alongside code changes | Requires static site generator for rich output; must be committed |
| GitHub Wiki | Supplemental reference, community edits | Not version-controlled with code; hard to review in PRs; can't use CODEOWNERS |
| GitHub Pages | Public-facing project sites, generated API docs | Requires build pipeline; adds CI complexity |

**Recommendation for most projects:** Use `docs/` for everything that should be reviewed alongside code changes. Set up GitHub Pages to publish generated output from `docs/` if you need a public-facing site.

### `docs/` Directory Structure

```
docs/
├── ARCHITECTURE.md           ← System component map
├── decisions/                ← ADRs
│   ├── 0001-use-event-sourcing.md
│   └── 0002-prefer-dynamodb.md
├── api/                      ← API reference (may be generated)
│   └── openapi.yaml
├── guides/                   ← How-to guides
│   ├── deployment.md
│   └── local-development.md
├── runbook.md                ← Operations guide
└── onboarding.md             ← New engineer guide
```

---

## Repository Health Checklist

GitHub's community standards checklist (visible in the Insights tab → Community Standards) tracks:

- [ ] Description
- [ ] README.md
- [ ] Code of conduct
- [ ] Contributing guide
- [ ] License
- [ ] Security policy
- [ ] Issue templates
- [ ] Pull request template

A complete checklist signals a well-maintained project to potential contributors and users.
