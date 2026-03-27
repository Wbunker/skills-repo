# Documentation as Code
## Tooling, Automation, CI/CD for Docs, and Generated API Documentation

---

## What Is Documentation as Code?

Documentation as code means applying software engineering practices to documentation:
- **Version control**: docs live in git alongside the code they describe
- **Code review**: doc changes are reviewed in PRs like code changes
- **CI/CD**: docs are built, validated, and published automatically on merge
- **Testing**: code examples in docs are run as tests; broken examples fail CI
- **Tooling**: linters, link checkers, and generators enforce quality automatically

The alternative — docs in a separate wiki, Google Doc, or Confluence page — produces documentation that drifts from code and is never reviewed alongside the changes that should trigger updates.

---

## Why Colocate Docs with Code

**Drift prevention**: When a code change is reviewed in a PR, the docs diff is visible alongside it. Reviewers catch outdated docs before merge — not six months later when a user files a bug.

**Discoverability for AI tools**: Docs near the code they describe are more likely to be in the AI's context when it's working on that code. A `README.md` in `backend/auth/` is read by Claude when navigating auth code; a Confluence page is not.

**Accountability**: CODEOWNERS can require doc reviewers for `docs/` changes. PR templates can include a doc update checklist item.

**Search and grep**: Developers can search docs with the same tools they use to search code.

---

## Setting Up Docs-as-Code

### Step 1: Move Docs Into the Repository

```
your-project/
├── docs/
│   ├── ARCHITECTURE.md
│   ├── decisions/           ← ADRs
│   ├── guides/              ← How-to guides
│   └── api/                 ← API reference (may be generated)
├── README.md
├── CONTRIBUTING.md
├── CHANGELOG.md
└── SECURITY.md
```

### Step 2: Enforce Doc Updates in PRs

Add to `.github/PULL_REQUEST_TEMPLATE.md`:
```markdown
## Documentation
- [ ] CHANGELOG.md updated (for user-facing changes)
- [ ] Docs updated if public API or behavior changed
- [ ] New ADR added if significant architectural decision was made
```

Add to CODEOWNERS:
```
/docs/                @your-docs-team
/docs/api/            @your-api-team @your-docs-team
```

### Step 3: Automate Validation in CI

See the CI pipeline section below for link checking, linting, and example testing.

---

## Documentation Generators

Generate reference docs automatically from code annotations to keep documentation synchronized with the actual implementation.

### By Language

| Language | Tool | Output |
|----------|------|--------|
| Java | Javadoc | HTML; standard Java convention |
| Java | Dokka | Kotlin/Java; modern HTML |
| Python | Sphinx + autodoc | HTML, PDF, ePub from docstrings |
| Python | pdoc | Minimal HTML from docstrings |
| TypeScript/JS | TypeDoc | HTML from JSDoc/TSDoc annotations |
| TypeScript/JS | JSDoc | HTML from `/** ... */` comment blocks |
| Go | godoc / pkg.go.dev | HTML from `// Package ...` comments |
| Rust | rustdoc | HTML from `///` doc comments |
| Any REST API | OpenAPI / Swagger | Interactive HTML docs, client SDKs |

### OpenAPI: The Gold Standard for REST APIs

Define your API spec in `docs/api/openapi.yaml` (or generate it from annotations). OpenAPI gives you:
- Interactive docs (Swagger UI, Redoc)
- Client SDK generation in any language
- Request/response validation
- Mock server generation for development

**Frameworks that generate OpenAPI automatically:**
- FastAPI (Python) — decorators → OpenAPI spec
- Spring Boot + springdoc-openapi (Java) — annotations → OpenAPI spec
- Hono, Zod + Fastify (TypeScript) — schema → OpenAPI spec

Example: Spring Boot generates an OpenAPI spec at `/v3/api-docs` with `springdoc-openapi` added as a dependency — no separate YAML to maintain.

### Automated Publishing with GitHub Actions

```yaml
# .github/workflows/docs.yml
name: Publish Docs

on:
  push:
    branches: [main]

jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Build API docs
        run: |
          npm ci
          npm run docs:build   # e.g., typedoc --out docs/api src/

      - name: Deploy to GitHub Pages
        uses: peaceiris/actions-gh-pages@v3
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./docs/api
```

---

## CI Pipeline for Documentation Quality

### Link Checking

Broken links in documentation are a common source of user frustration and erode trust. Check them in CI.

```yaml
# Using lychee (fast, supports GitHub, handles rate limits)
- name: Check links
  uses: lycheeverse/lychee-action@v1
  with:
    args: --verbose --no-progress 'docs/**/*.md' 'README.md'
    fail: true
```

Or with `markdown-link-check`:
```yaml
- name: Check Markdown links
  uses: gaurav-nelson/github-action-markdown-link-check@v1
  with:
    use-quiet-mode: 'yes'
    config-file: '.github/markdown-link-check.json'
```

### Documentation Linting with Vale

Vale enforces a style guide as part of CI — catching passive voice, ambiguous terms, inconsistent terminology, and violations of your preferred style guide.

```bash
# Install
brew install vale   # macOS
pip install vale    # any

# .vale.ini
StylesPath = .vale/styles
MinAlertLevel = warning

[*.md]
BasedOnStyles = Vale, Google
```

```yaml
# GitHub Actions
- name: Lint docs with Vale
  uses: errata-ai/vale-action@reviewdog
  with:
    files: docs/
```

Vale ships with styles for Google, Microsoft, Red Hat, and others. You can extend or write your own rules.

### Spell Checking

```yaml
- name: Spell check
  uses: crate-ci/typos-action@master   # fast Rust-based spell checker
```

### Testing Code Examples

Code examples in docs that don't run are worse than no examples — they mislead both humans and AI tools.

**Python (doctest)**:
```python
def add(a: int, b: int) -> int:
    """
    Add two numbers.

    >>> add(2, 3)
    5
    >>> add(-1, 1)
    0
    """
    return a + b
```
Run with `python -m doctest module.py` or `pytest --doctest-modules`.

**Markdown code blocks with language tags** can be tested using `mdx-mermaid`, `runme`, or custom scripts:
```bash
# Extract and run all ```bash blocks in docs/
grep -A 100 '```bash' docs/guides/quickstart.md | grep -B 100 '```' | bash
```

---

## Documentation Site Generators

When you need more than rendered GitHub Markdown:

| Tool | Best For | Notes |
|------|---------|-------|
| **MkDocs + Material** | Simple, beautiful Markdown sites | Python ecosystem popular; great search |
| **Docusaurus** | Versioned docs, React-based | Popular for OSS projects with multiple versions |
| **Hugo** | Fast static sites | Good for large doc sets |
| **Sphinx** | Python projects, complex cross-referencing | De facto Python standard |
| **Mintlify** | Developer-focused, AI-integrated | Modern; GitHub Action for auto-deploy |
| **Nextra** | Next.js-based | Good for teams already on Vercel |
| **Read the Docs** | Hosting + CI for Sphinx/MkDocs | Free for open source |

### Minimal MkDocs Setup

```yaml
# mkdocs.yml
site_name: My Project
theme:
  name: material

nav:
  - Home: index.md
  - Architecture: ARCHITECTURE.md
  - Guides:
    - Local Development: guides/local-development.md
    - Deployment: guides/deployment.md
  - API Reference: api/reference.md
```

```bash
pip install mkdocs-material
mkdocs serve   # local preview
mkdocs build   # produce site/ directory
```

---

## Repomix: Packaging a Codebase for AI

[Repomix](https://repomix.com/) packs your entire codebase (code + docs) into a single AI-friendly file. Useful when you need an AI to reason about the whole system at once.

```bash
npx repomix                      # pack entire repo to repomix-output.txt
npx repomix --output repo.xml    # XML format (better structure preservation)
npx repomix --include "docs/**"  # docs only
```

The output can be fed directly to Claude (or any LLM) for:
- Large refactors spanning many files
- Architecture analysis
- Documentation generation ("read this codebase and generate an ARCHITECTURE.md")
- Onboarding document drafting

**`repomix.config.json`** — configure what to include/exclude:
```json
{
  "output": {
    "filePath": "repo-context.xml",
    "style": "xml"
  },
  "ignore": {
    "useGitignore": true,
    "customPatterns": ["*.lock", "dist/", "*.min.js"]
  }
}
```

---

## `llms.txt` Convention

An emerging convention (analogous to `robots.txt`) for making a website's content AI-accessible. Maintained at `yoursite.com/llms.txt`.

```markdown
# My Project Documentation

## Core docs
- [Architecture](https://docs.example.com/architecture): System overview
- [API Reference](https://docs.example.com/api): REST API

## Guides
- [Quickstart](https://docs.example.com/quickstart)
- [Deployment](https://docs.example.com/deploy)
```

Not yet universal, but gaining adoption for public documentation sites.

---

## Documentation Maintenance Practices

### Freshness Monitoring

- Track undocumented public APIs with your doc generator's coverage report
- Add a CI step that fails if new public methods lack docstrings (e.g., `pydocstyle`, `checkstyle`)
- Schedule a quarterly "doc review" issue to audit staleness

### Ownership

```
# CODEOWNERS — docs have mandatory reviewers
/docs/              @org/tech-writers @org/team-leads
/docs/api/          @backend-team
/docs/decisions/    @tech-leads
```

### Definition of Done

Add to your team's definition of done:
- [ ] New/changed public API has docstring
- [ ] CHANGELOG.md updated for user-facing changes
- [ ] Docs updated if behavior changed
- [ ] New ADR written if significant architectural decision was made
- [ ] README updated if project structure or commands changed
