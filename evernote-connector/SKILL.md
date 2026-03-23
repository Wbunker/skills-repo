---
name: evernote-connector
description: Interact with Evernote on behalf of the user — create, read, update, delete, and search notes; list notebooks and tags. Use when the user asks to save something to Evernote, look up notes, create a note, search their notes, or manage notebooks/tags. Requires EVERNOTE_TOKEN environment variable (developer token or OAuth access token).
---

# Evernote Connector

Interact with the user's Evernote account via the `scripts/evernote.py` CLI.

## Setup (one-time)

```bash
pip install evernote3
export EVERNOTE_TOKEN="S=s###:U=..."          # developer token or OAuth access token
export EVERNOTE_NOTE_STORE_URL="https://www.evernote.com/edam/note/sXXX"  # from OAuth; omit if using developer token with auto-discovery
```

If `EVERNOTE_TOKEN` is not set, tell the user to obtain a developer token from `https://www.evernote.com/api/DeveloperToken.action` or complete OAuth and provide the access token + NoteStore URL.

The script lives at `scripts/evernote.py` relative to this skill's directory. Use its absolute path when running it.

## Common Operations

### List notebooks
```bash
python3 scripts/evernote.py list-notebooks
# Output: GUID<tab>Name
```

### Search notes
```bash
python3 scripts/evernote.py search "meeting notes" --max 10
python3 scripts/evernote.py search "notebook:Work tag:urgent"
```

### List notes in a notebook
```bash
python3 scripts/evernote.py list-notes --notebook NOTEBOOK_GUID --max 20
python3 scripts/evernote.py list-notes --query "project alpha"
```

### Read a note
```bash
python3 scripts/evernote.py get-note NOTE_GUID
python3 scripts/evernote.py get-note NOTE_GUID --text-only   # plain text only
```

### Create a note
```bash
python3 scripts/evernote.py create-note --title "My Note" --body "Plain text content"
python3 scripts/evernote.py create-note --title "My Note" --body "Content" --notebook NOTEBOOK_GUID --tags "work,urgent"
python3 scripts/evernote.py create-note --title "My Note" --enml-file body.enml  # for rich ENML content
```

### Update a note
```bash
python3 scripts/evernote.py update-note NOTE_GUID --title "New Title" --body "New content"
python3 scripts/evernote.py update-note NOTE_GUID --tags "tag1,tag2"  # replaces all tags
```

### Delete a note (moves to trash)
```bash
python3 scripts/evernote.py delete-note NOTE_GUID
```

### List tags
```bash
python3 scripts/evernote.py list-tags
# Output: GUID<tab>Name
```

## Workflow: Finding Then Acting on a Note

When the user says "find my note about X and update it":
1. `search "X"` to find candidates
2. `get-note GUID` to confirm it's the right note
3. `update-note GUID --body "..."` to update

## ENML (Note Format)

Notes are stored in ENML (XML). The script auto-converts plain text `--body` to valid ENML. For rich formatting, write ENML manually and pass via `--enml-file`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE en-note SYSTEM "http://xml.evernote.com/pub/enml2.dtd">
<en-note>
  <h1>Title</h1>
  <p>Paragraph text</p>
  <ul><li>List item</li></ul>
</en-note>
```

## Search Query Syntax

| Example | Meaning |
|---------|---------|
| `meeting` | Contains "meeting" |
| `notebook:Work` | In notebook named "Work" |
| `tag:urgent` | Has tag "urgent" |
| `intitle:budget` | "budget" in title |
| `created:20240101` | Created on/after Jan 1, 2024 |
| `-draft` | Does not contain "draft" |

## Error Handling

- **RATE_LIMIT_REACHED**: Wait `rateLimitDuration` seconds before retrying
- **PERMISSION_DENIED on expunge**: Use `delete-note` (trash) instead — permanent deletion is blocked for third-party apps
- **Not found**: Verify GUID is correct; note may be in trash (`inactive=True` in filter)
- **Auth errors**: Check `EVERNOTE_TOKEN` is set and not expired (tokens expire after ~1 year)

## Reference

For full API details, data types, OAuth flow, and advanced usage: `references/api_reference.md`
