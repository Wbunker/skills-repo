Weekly wiki consolidation — lint, groom, and strengthen the wiki.

Run this once a week (or on demand) after several ingest cycles have accumulated.

Arguments: $ARGUMENTS (optional --dry-run to preview without writing)

## Your job

You are the wiki consolidation agent. Work through these passes in order.

---

### Pass 1 — Orphan check (Haiku agent, background)

Launch a background **Haiku** agent with this task:
> Read wiki/index.md to get all article filenames. Read each article in wiki/notes/ and extract all [[wikilinks]] mentioned. Find articles that have zero inbound links from other articles — these are orphans. Also find [[wikilinks]] that point to articles that don't exist yet — these are stubs needed. Return JSON: {orphans: ["filename"], missing_stubs: ["Article Name"]}

---

### Pass 2 — Staleness check (Haiku agent, background, parallel with Pass 1)

Launch a background **Haiku** agent with this task:
> Read wiki/log.md to find the last ingest date per domain. Read each article in wiki/notes/ and check its frontmatter `updated` date. Flag articles whose `updated` date is more than 60 days older than the most recent ingest for their domain — these may have stale content. Return JSON: {stale: [{file, updated, domain, last_ingest_for_domain}]}

Wait for both Pass 1 and Pass 2 agents to complete.

---

### Pass 3 — Stub creation (Sonnet)

For each item in `missing_stubs`:
- Create a minimal stub article in wiki/notes/ with correct frontmatter (title, tags based on name, created date, updated date, empty sources)
- Add a one-line entry to wiki/index.md under the appropriate domain

---

### Pass 4 — Orphan resolution (Sonnet)

For each orphan article:
- Read the article
- Read wiki/index.md to find related articles
- Add an appropriate [[wikilink]] from at least one related article to the orphan, or if the orphan is truly irrelevant, note it for review

---

### Pass 5 — Stale article review (Sonnet)

For stale articles (> 60 days since update relative to domain ingest activity):
- Re-read the article
- Check if the facts are still likely current given what you know
- Add a `review_needed: true` frontmatter flag if the content looks potentially outdated
- Do NOT change content — just flag it for review

---

### Pass 6 — Index integrity (Sonnet)

- Read wiki/index.md
- Read wiki/notes/ directory listing
- Ensure every article in notes/ has an entry in index.md
- Ensure every entry in index.md has a corresponding file in notes/
- Fix any gaps

---

### Pass 7 — Log and report

Append to wiki/log.md:
```
## [YYYY-MM-DD] lint | Weekly consolidation

- Orphans found: N (resolved: N)
- Missing stubs created: N
- Stale articles flagged: N
- Index gaps fixed: N
- Total articles: N
```

If --dry-run was passed: print the report but do NOT write any files. Show what would change.

Report:
- Summary counts for each pass
- List of any stale articles flagged for review
- List of new stubs created
- Any articles that couldn't be auto-resolved (need attention)
