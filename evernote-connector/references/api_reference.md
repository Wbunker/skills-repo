# Evernote API Reference

## Overview

The Evernote Cloud API is **Apache Thrift over HTTPS**, not REST. All calls go through the NoteStore Thrift client. The Python SDK (`evernote3`) wraps this. Direct `curl`-style calls are not possible without Thrift.

API version: 1.28 (maintenance mode as of 2024+, no new features expected)

## Authentication

### Developer Token (Recommended for Personal/Agent Use)

- Format: `S=s###:U=...`
- Set as `EVERNOTE_TOKEN` env var
- Grants full access to the token owner's account
- Request at: `https://www.evernote.com/api/DeveloperToken.action` (may require contacting Evernote support)

### OAuth 1.0 (Required for Multi-User Apps)

Not OAuth 2.0. Four-step flow:

1. **Get temp token**: `GET https://www.evernote.com/oauth` with consumer key/secret + HMAC-SHA1 signature
2. **User authorizes**: Redirect to `https://www.evernote.com/OAuth.action?oauth_token=TEMP`
3. **Exchange for access token**: `GET https://www.evernote.com/oauth` with temp token + verifier
4. **Use token**: Include in all NoteStore calls

OAuth response includes critical fields:
- `oauth_token` — access token
- `edam_noteStoreUrl` — per-user NoteStore URL (save this; don't hardcode)
- `edam_expires` — expiry (UNIX ms, default 1 year)
- `edam_userId`, `edam_shard`

Set `EVERNOTE_NOTE_STORE_URL` to the `edam_noteStoreUrl` value for the evernote.py script.

## NoteStore URL

The NoteStore URL is **per-user** and returned at OAuth time. Format: `https://www.evernote.com/edam/note/{shard}`. Never hardcode a shard; always use the returned URL.

## Note Content: ENML

Notes use **Evernote Markup Language** (ENML) — an XML subset of XHTML.

Required wrapper:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE en-note SYSTEM "http://xml.evernote.com/pub/enml2.dtd">
<en-note>
  <p>Your content here</p>
  <p>More content</p>
</en-note>
```

Rules:
- All content inside `<en-note>...</en-note>`
- HTML entities required: `&amp;` `&lt;` `&gt;` `&nbsp;`
- class/id attributes are stripped
- Valid XHTML tags only (no `<script>`, `<style>`, `<form>`)
- Use `<br/>` not `<br>`
- Attachments embedded as `<en-media>` elements

## Evernote Search Query Syntax (ENEX)

Use in `NoteFilter.words`:

| Query | Meaning |
|-------|---------|
| `word` | Notes containing word |
| `"exact phrase"` | Exact phrase match |
| `notebook:MyNotebook` | Notes in specific notebook |
| `tag:mytag` | Notes with tag |
| `intitle:keyword` | Word in title |
| `created:20240101` | Created on or after date |
| `updated:20240101` | Updated on or after date |
| `-word` | Exclude word |
| `any: word1 word2` | Match any term |

## NoteStore Methods (Key Operations)

### Notebooks
```python
note_store.listNotebooks(token)              # → [Notebook]
note_store.getNotebook(token, guid)          # → Notebook
note_store.getDefaultNotebook(token)         # → Notebook
note_store.createNotebook(token, notebook)   # → Notebook
note_store.updateNotebook(token, notebook)   # → int (USN)
```

### Notes
```python
note_store.findNotesMetadata(token, filter, offset, maxNotes, resultSpec)  # → NotesMetadataList
note_store.getNote(token, guid, withContent, withResourcesData, withResourcesRecognition, withResourcesAlternateData)  # → Note
note_store.createNote(token, note)           # → Note
note_store.updateNote(token, note)           # → Note
note_store.deleteNote(token, guid)           # → int (USN) — moves to trash
# expungeNote is BLOCKED for third-party apps (PERMISSION_DENIED)
```

### Tags
```python
note_store.listTags(token)                   # → [Tag]
note_store.createTag(token, tag)             # → Tag
note_store.updateTag(token, tag)             # → int (USN)
```

### Search
```python
note_store.findNotesMetadata(token, NoteFilter(words="query"), offset, maxNotes, resultSpec)
note_store.findRelated(token, relatedQuery, relatedResultSpec)  # contextual suggestions
```

### Sync
```python
note_store.getSyncState(token)               # → SyncState (update count, etc.)
note_store.getFilteredSyncChunk(token, afterUSN, maxEntries, filter)  # → SyncChunk
```

## Key Data Types

### Note
```python
Note(
  guid=str,              # read-only after creation
  title=str,             # required, 1-255 chars
  content=str,           # ENML string
  contentHash=bytes,     # read-only
  notebookGuid=str,      # omit = default notebook
  tagGuids=[str],        # or use tagNames
  tagNames=[str],        # set on create; read on get
  created=int,           # UNIX ms
  updated=int,           # UNIX ms
  deleted=int,           # UNIX ms if trashed
  active=bool,
  resources=[Resource],
)
```

### NoteFilter
```python
NoteFilter(
  order=int,             # NoteSortOrder constant
  ascending=bool,
  words=str,             # ENEX search query
  notebookGuid=str,
  tagGuids=[str],
  timeZone=str,
  inactive=bool,         # True = search trash
)
```

### NotesMetadataResultSpec
```python
NotesMetadataResultSpec(
  includeTitle=True,
  includeContentLength=False,
  includeCreated=True,
  includeUpdated=True,
  includeDeleted=False,
  includeUpdateSequenceNum=False,
  includeNotebookGuid=True,
  includeTagGuids=False,
  includeAttributes=False,
  includeLargestResourceMime=False,
  includeLargestResourceSize=False,
)
```

## Rate Limits

- Per API key, per user, per 1-hour window (no published numbers)
- Exceeding throws `EDAMSystemException` with `errorCode=RATE_LIMIT_REACHED`
- Exception includes `rateLimitDuration` (seconds to wait)
- Always respect `rateLimitDuration` before retrying

## Error Handling

```python
from evernote.edam.error.ttypes import EDAMUserException, EDAMSystemException, EDAMNotFoundException

try:
    note_store.getNote(...)
except EDAMUserException as e:
    print(f"User error: {e.errorCode} - {e.parameter}")
except EDAMSystemException as e:
    if e.errorCode == 19:  # RATE_LIMIT_REACHED
        print(f"Rate limited. Wait {e.rateLimitDuration}s")
    else:
        print(f"System error: {e.errorCode} - {e.message}")
except EDAMNotFoundException as e:
    print(f"Not found: {e.identifier} = {e.key}")
```

## Installation

```bash
pip install evernote3
# evernote3 is the Python 3 community fork (Nozbe)
# The official 'evernote' package is Python 2 only
```

## API Status (2024+)

- Acquired by Bending Spoons in 2022; API in maintenance mode
- No new API features planned; SDK repos are years out of date
- Sandbox (`sandbox.evernote.com`) is officially deprecated — use production
- Developer tokens may require contacting support@evernote.com directly
- `expunge*` methods always return `PERMISSION_DENIED` for third-party apps
- Basic-tier API keys cannot read note content — Full access key required
