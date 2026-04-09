Master wiki ingest orchestrator. Runs all configured sources for a date range.

Arguments: $ARGUMENTS
Supported flags: --from YYYY-MM-DD, --to YYYY-MM-DD
Default if no dates given: since each source's last ingest (tracked per source), or 7 days ago if never run.
Example: `--from 2026-03-01 --to 2026-03-31`

## Sources

- **Gmail** — `fetch_gmail.py` / `build_manifest.py` → classify → ingest
- **iMessage** — `fetch_imessages.py` → classify → ingest

## Your job

You are the master ingest orchestrator. Execute these phases in order.

---

### Phase 1 — Fetch both sources in parallel

Run both fetchers simultaneously (parallel Bash calls):

**Gmail:**
```bash
cd wiki/scripts
python3 fetch_gmail.py $ARGUMENTS
```
If Gmail manifest is empty, fall back to:
```bash
python3 build_manifest.py $ARGUMENTS
```

**iMessage:**
```bash
cd wiki/scripts
python3 fetch_imessages.py $ARGUMENTS
```

Collect both manifests. If both are empty, print a summary and stop.

---

### Phase 2 — Classify both manifests (parallel Haiku agents)

Launch two background **haiku** agents simultaneously — one per source.

**Gmail classify agent:**
> Read wiki/CLAUDE.md for the domain taxonomy. Then read each file in this manifest: [paste Gmail manifest]. For each email, assign: domain (from the tag taxonomy in CLAUDE.md), relevance (1=background noise, 2=useful context, 3=important decisions or facts), key_entities (names/orgs mentioned). Output a JSON array: [{id, file, domain, relevance, key_entities}]. Print only the JSON array, nothing else.

**iMessage classify agent:**
> Read wiki/CLAUDE.md for the domain taxonomy. Then read each file in this manifest: [paste iMessage manifest]. Each file is a conversation thread between the wiki owner and one or more contacts.
>
> For each thread, assign: domain, relevance, key_entities.
> relevance 2+ if the thread contains concrete plans, business/financial updates, decisions, facts about people/companies, or action items. Pure social chatter = relevance 1.
>
> Output a JSON array: [{chat_id, file, domain, relevance, key_entities}]. Print only the JSON array, nothing else.

Wait for both classify agents to complete. Parse both JSON outputs.

---

### Phase 3 — Ingest by domain (parallel Sonnet agents)

Merge the two classified result sets. Group all items (email + threads) by domain where relevance >= 2.

For each domain group, spawn a **single background Sonnet agent** that handles both emails and threads for that domain together:

> You are ingesting sources into the wiki for the domain: [DOMAIN].
>
> First read wiki/CLAUDE.md to understand article conventions, frontmatter format, and cross-linking rules.
> Then read wiki/index.md to see what articles already exist.
> Then read each of these source files: [list all files — emails and threads — for this domain].
>
> Sources may be:
> - Email files (raw/emails/*.md) — more formal, external-facing
> - iMessage threads (raw/imessages/*.md) — more candid, often contain informal decisions and opinions
>
> For each source, extract: decisions made, facts learned, people mentioned (name + role + relationship to wiki owner), projects/entities referenced, open questions or action items.
>
> Then update the wiki:
> - For each entity or person mentioned: find their existing article in wiki/notes/ and add what was learned, OR create a new stub article if none exists
> - For decisions or facts that span multiple entities: add to the most relevant article and cross-link
> - Keep articles focused — one entity or concept per article
> - Use [[wikilinks]] for every entity that has or should have its own article
> - Add or update frontmatter: tags, updated date, sources (add each source filename)
> - iMessage threads often have more candid assessments — capture these
>
> After updating articles, return a summary: which articles were updated, which were created, key facts extracted.

Run all domain agents in parallel.

Wait for all domain agents to complete and collect their summaries.

---

### Phase 4 — Update index and log

1. Read wiki/index.md. For any newly created articles not yet in the index, add them under the correct domain section with a one-line summary.

2. Append a single consolidated entry to wiki/log.md:
```
## [YYYY-MM-DD] ingest | Gmail + iMessage $ARGUMENTS

**Gmail**
- Fetched: N emails
- Classified relevance>=2: N

**iMessage**
- Fetched: N threads
- Classified relevance>=2: N

**Combined**
- Domains touched: [list]
- Articles updated: [list]
- Articles created: [list]
```

---

### Phase 5 — Report

Print a concise summary:
- Date range processed (per source — they may differ if last_ingest dates differ)
- Items fetched / ingested per source
- Articles updated and created (grouped by domain)
- Any notable facts or decisions extracted worth highlighting
