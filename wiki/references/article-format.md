# Wiki Article Format & Conventions

This reference defines how articles are written and organized in wbunker-wiki.
The format is plain Markdown — no proprietary tooling required.

---

## Article Structure

Every article in `notes/` follows this template:

```markdown
---
title: Article Title
aliases: [alternate name, short name]
tags: [domain/subtag]
created: YYYY-MM-DD
updated: YYYY-MM-DD
sources: [raw/filename.md, ...]
---

# Article Title

One-sentence summary of what this article covers.

## [Content sections — vary by article type]

## Related
- [[Other Article]]
- [[Another Article]]
```

### Frontmatter Fields

| Field | Required | Notes |
|-------|----------|-------|
| `title` | ✅ | Canonical name for the article |
| `aliases` | Optional | Alternate names — used for cross-linking |
| `tags` | ✅ | One or more `domain/subtag` tags (see taxonomy below) |
| `created` | ✅ | `YYYY-MM-DD` |
| `updated` | ✅ | Update on every edit |
| `sources` | ✅ | List of raw source files that informed this article |

---

## Tag Taxonomy

Use nested `domain/subtag` format. Every article gets at least one tag.

| Tag | Scope |
|-----|-------|
| `person/family` | Family members |
| `person/friend` | Personal friends |
| `person/business` | Business contacts, partners |
| `business/camp-bunker` | Camp Bunker LLC |
| `business/bunker-rent` | Bunker Rent LLC |
| `business/bunker-farms` | Bunker Farms |
| `business/bunker-consulting` | Bunker Consulting |
| `business/svgs` | Silicon Valley Growth Fund |
| `business/catfish` | Catfish Dot.Com |
| `investment` | Personal investments, SPACs |
| `idea` | Ideas, concepts, research threads |
| `ai/company` | AI labs, companies, startups (OpenAI, Anthropic, etc.) |
| `ai/model` | Specific AI models (GPT-4o, Claude Sonnet 4, Gemini 2.5, etc.) |
| `ai/person` | AI researchers, founders, executives |
| `ai/research` | Papers, benchmarks, datasets, techniques |
| `ai/product` | AI developer tools (Claude Code, Codex, Copilot, etc.) |
| `reference` | How-to guides, technical reference |

---

## Cross-Linking with Wikilinks

Use `[[Article Title]]` to link between articles. This works in any Markdown editor
that supports wikilinks (Obsidian, VS Code with extensions, GitHub wiki, etc.).

```markdown
[[OpenAI]] announced that [[Sam Altman]] would lead the new [[OpenAI Codex]] effort.
```

**Rules:**
- If a named entity has an article, link it — link aggressively
- Use `[[Article Title|display text]]` when the display text should differ from the title
- `[[Article#Heading]]` to link to a specific section
- Add all linked articles to the `## Related` section at the bottom

---

## Operations

### Ingest (adding new knowledge)
1. Save the raw source to `raw/` with filename `YYYY-MM-DD-title.md`
2. Read the source and identify entities (people, companies, products, ideas)
3. Write or update articles in `notes/` — one concept per article
4. Update `index.md` if new articles were created
5. Cross-link related articles
6. Append to `log.md`: `## [YYYY-MM-DD] ingest | Source Title`

### Query (answering questions)
1. Read `index.md` to find relevant articles
2. Read those articles
3. Synthesize answer with `[[wikilinks]]` to sources
4. If the answer is reusable, offer to file it as a new article

### Lint (periodic health check)
- Orphan articles (nothing links to them) — add links or delete
- Stale claims superseded by newer sources — update
- Important concepts mentioned but lacking articles — stub them
- Articles missing `sources` frontmatter — flag for review

---

## Index Maintenance

`index.md` is the master catalog — every article in `notes/` must appear here
under its domain section with a one-line summary. Update on every ingest.

---

## Log Format

`log.md` is append-only. Each entry:
```
## [YYYY-MM-DD] <operation> | <title>
```
Operations: `ingest`, `query`, `lint`, `create`, `update`

Check recent activity: `grep "^## \[" wiki/log.md | tail -10`

---

## Style Guide

- **Third person** for person/business articles: "Will Bunker is..."
- **First person** only for Will's own goals/self-knowledge articles
- **One concept per article** — split if an article is covering two distinct things
- **Prefer updating** existing articles over creating new ones for small additions
- **Short stubs are fine** — a 3-line article with a news timeline is better than no article
