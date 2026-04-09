Show the current state of the wiki pipeline.

No arguments required.

## Your job

Read these files and produce a concise status report:

1. **wiki/raw/processed_ids.json** — parse it:
   - `last_fetch` timestamp
   - Total processed entries
   - Count of skipped (noise) vs saved
   - Oldest and newest email date in the saved set

2. **wiki/log.md** — show last 10 entries:
   ```bash
   grep "^## \[" wiki/log.md | tail -10
   ```

3. **wiki/notes/** — count articles and summarize by domain:
   - Read frontmatter tags from each .md file
   - Count per top-level domain tag
   - Flag any with `review_needed: true`

4. **wiki/index.md** — count total entries per domain section

## Report format

```
Wiki Status — [today's date]

PIPELINE
  Last fetch    : [date/time or never]
  Emails saved  : N (N skipped as noise)
  Date range    : [oldest] to [newest]

WIKI
  Total articles: N
  By domain:
    business/    : N articles
    person/      : N articles
    idea/        : N articles
    reference/   : N articles
  Needs review   : N articles (list them if any)

RECENT ACTIVITY (last 10 log entries)
  [paste grep output]

NEXT STEPS
  [suggest: run /wiki:ingest if last fetch > 7 days ago,
            run /wiki:consolidate if last consolidation > 7 days ago,
            review flagged articles if any]
```
