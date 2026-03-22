# Gmail Search Operators

Gmail query syntax for the `q` parameter in `messages.list()` and `threads.list()`.

> **Important:** The `gmail.metadata` scope **cannot** use the `q` search parameter. If you need to search, use `gmail.readonly` or `gmail.modify` scope.

## Table of Contents
1. [Sender / Recipient](#sender--recipient)
2. [Subject & Body](#subject--body)
3. [Date & Time](#date--time)
4. [Labels & Categories](#labels--categories)
5. [Attachments](#attachments)
6. [Status & Properties](#status--properties)
7. [Size](#size)
8. [Combining Operators](#combining-operators)
9. [Common Query Patterns](#common-query-patterns)

---

## Sender / Recipient

| Operator | Description | Example |
|----------|-------------|---------|
| `from:` | Sender address or name | `from:boss@company.com` |
| `to:` | Recipient (To field) | `to:team@company.com` |
| `cc:` | CC recipient | `cc:manager@company.com` |
| `bcc:` | BCC recipient (sent only) | `bcc:archive@company.com` |
| `deliveredto:` | Actual delivery address | `deliveredto:alias@gmail.com` |

```python
# Multiple senders (OR)
q='from:alice@example.com OR from:bob@example.com'

# Sent to domain
q='to:@company.com'

# From anyone to me specifically (useful for aliases)
q='deliveredto:myalias@gmail.com'
```

---

## Subject & Body

| Operator | Description | Example |
|----------|-------------|---------|
| `subject:` | Subject line contains | `subject:invoice` |
| `subject:"..."` | Exact subject phrase | `subject:"meeting notes"` |
| `{word}` | Word in subject or body | `invoice` |
| `"{phrase}"` | Exact phrase anywhere | `"project alpha"` |
| `-word` | Exclude word | `-unsubscribe` |
| `filename:` | Attachment filename | `filename:report.pdf` |

```python
# Subject phrase
q='subject:"weekly digest"'

# Body search (implicit)
q='"urgent action required"'

# Subject contains word
q='subject:invoice -subject:paid'
```

---

## Date & Time

| Operator | Description | Example |
|----------|-------------|---------|
| `after:` | After date (inclusive) | `after:2024/01/01` |
| `before:` | Before date (exclusive) | `before:2024/02/01` |
| `newer_than:` | Relative: newer than N d/m/y | `newer_than:7d` |
| `older_than:` | Relative: older than N d/m/y | `older_than:1y` |

Date format: `YYYY/MM/DD`
Relative units: `d` (days), `m` (months), `y` (years)

```python
# Last 30 days
q='newer_than:30d'

# January 2024
q='after:2024/01/01 before:2024/02/01'

# More than 1 year old
q='older_than:1y'

# Specific week
q='after:2024/03/04 before:2024/03/11'
```

---

## Labels & Categories

| Operator | Description | Example |
|----------|-------------|---------|
| `label:` | Has user label | `label:work` |
| `in:inbox` | In inbox | `in:inbox` |
| `in:sent` | In sent | `in:sent` |
| `in:drafts` | Is a draft | `in:drafts` |
| `in:trash` | In trash | `in:trash` |
| `in:spam` | In spam | `in:spam` |
| `in:starred` | Is starred | `in:starred` |
| `in:anywhere` | All mail including spam/trash | `in:anywhere` |
| `category:` | Gmail category tab | `category:promotions` |
| `is:important` | Marked important | `is:important` |

Categories: `primary`, `social`, `promotions`, `updates`, `forums`

```python
# Unread in inbox
q='in:inbox is:unread'

# Starred and important
q='is:starred is:important'

# Promotions category, last 7 days
q='category:promotions newer_than:7d'

# Custom label
q='label:project-alpha'

# Label with spaces (use hyphens or quotes)
q='label:my-project'
q='label:"my project"'
```

---

## Attachments

| Operator | Description | Example |
|----------|-------------|---------|
| `has:attachment` | Has any attachment | `has:attachment` |
| `filename:` | Specific filename | `filename:resume.pdf` |
| `filename:*.ext` | By extension | `filename:*.xlsx` |
| `has:drive` | Has Google Drive attachment | `has:drive` |
| `has:document` | Has Google Doc | `has:document` |
| `has:spreadsheet` | Has Google Sheet | `has:spreadsheet` |
| `has:presentation` | Has Google Slides | `has:presentation` |
| `has:youtube` | Has YouTube link | `has:youtube` |

```python
# PDFs only
q='filename:*.pdf'

# Any Office doc
q='filename:*.docx OR filename:*.xlsx OR filename:*.pptx'

# Large attachments
q='has:attachment larger:5M'

# Drive files shared with me
q='has:drive'
```

---

## Status & Properties

| Operator | Description | Example |
|----------|-------------|---------|
| `is:read` | Already read | `is:read` |
| `is:unread` | Unread | `is:unread` |
| `is:starred` | Starred | `is:starred` |
| `is:snoozed` | Snoozed | `is:snoozed` |
| `is:muted` | Muted thread | `is:muted` |
| `has:userlabels` | Has any user-created label | `has:userlabels` |
| `has:nouserlabels` | No user labels | `has:nouserlabels` |
| `rfc822msgid:` | Exact Message-ID header | `rfc822msgid:<abc@mail.example.com>` |

```python
# Unread and starred
q='is:unread is:starred'

# Read messages in inbox (to find old emails)
q='in:inbox is:read older_than:30d'

# Find specific message by Message-ID
q='rfc822msgid:<CAFoo123@mail.gmail.com>'
```

---

## Size

| Operator | Description | Example |
|----------|-------------|---------|
| `larger:` | Larger than size | `larger:10M` |
| `smaller:` | Smaller than size | `smaller:1M` |
| `size:` | Exact size (rarely useful) | `size:1000` |

Units: bytes (no suffix), `K`/`KB` (kilobytes), `M`/`MB` (megabytes)

```python
# Large emails wasting storage
q='larger:25M'

# Small emails (likely text-only)
q='smaller:10K'

# Medium with attachments
q='has:attachment larger:1M smaller:10M'
```

---

## Combining Operators

| Syntax | Meaning |
|--------|---------|
| `term1 term2` | AND (implicit) |
| `term1 OR term2` | OR (must be uppercase) |
| `{term1 term2}` | OR (alternative syntax) |
| `-term` | NOT |
| `(term1 term2)` | Grouping |

```python
# AND (implicit)
q='from:alice@example.com is:unread'

# OR
q='from:alice@example.com OR from:bob@example.com'

# NOT
q='is:unread -from:newsletter@example.com'

# Complex: unread from specific domain, not spam, last 7 days
q='from:@important-client.com is:unread -in:spam newer_than:7d'

# Grouping with parentheses
q='(from:alice@example.com OR from:bob@example.com) subject:project has:attachment'
```

---

## Common Query Patterns

```python
# === Inbox management ===
unread_inbox = 'in:inbox is:unread'
important_unread = 'is:important is:unread'
needs_reply = 'in:inbox is:unread -from:me'
old_unread = 'in:inbox is:unread older_than:7d'

# === Finding emails ===
from_boss = 'from:boss@company.com newer_than:30d'
with_invoice = 'subject:invoice (has:attachment OR has:drive)'
from_domain = 'from:@partner-company.com'
about_project = '(subject:alpha OR "project alpha") -in:spam'

# === Cleanup ===
large_old = 'larger:10M older_than:1y'
old_promotions = 'category:promotions older_than:30d'
read_and_old = 'in:inbox is:read older_than:6m -is:starred'
newsletters = 'unsubscribe older_than:1m -is:starred'

# === Thread finding ===
active_threads = 'in:inbox newer_than:7d'
my_replies = 'in:sent newer_than:30d subject:"Re:"'

# === Audit / compliance ===
forwarded = 'has:attachment in:sent'
external_sent = 'in:sent -to:@company.com newer_than:30d'
```

### Building dynamic queries

```python
from datetime import datetime, timedelta

def date_range_query(days_back: int, days_end: int = 0) -> str:
    end = datetime.now() - timedelta(days=days_end)
    start = datetime.now() - timedelta(days=days_back)
    return f'after:{start.strftime("%Y/%m/%d")} before:{end.strftime("%Y/%m/%d")}'

def from_any(*senders: str) -> str:
    return ' OR '.join(f'from:{s}' for s in senders)

def with_labels(*label_names: str) -> str:
    return ' '.join(f'label:{name}' for name in label_names)

# Usage
q = f'{from_any("alice@co.com", "bob@co.com")} is:unread {date_range_query(30)}'
```
