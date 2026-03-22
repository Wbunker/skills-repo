# Gmail Message Format

## Table of Contents
1. [Message Object Structure](#message-object)
2. [Payload and MIME Parts](#payload-and-mime)
3. [Extracting Body Text](#extracting-body)
4. [Attachment Handling](#attachments)
5. [Creating Messages](#creating-messages)
6. [Raw Format](#raw-format)

---

## Message Object Structure

A full message (`format='full'`) response:

```json
{
  "id": "18b1c2d3e4f5a6b7",
  "threadId": "18b1c2d3e4f5a6b7",
  "labelIds": ["INBOX", "UNREAD"],
  "snippet": "First 200 chars of message...",
  "historyId": "1234567",
  "internalDate": "1703001600000",  // Unix ms timestamp
  "sizeEstimate": 12345,
  "payload": {
    "mimeType": "multipart/alternative",
    "headers": [
      {"name": "From", "value": "Sender <sender@example.com>"},
      {"name": "To", "value": "recipient@example.com"},
      {"name": "Subject", "value": "Hello"},
      {"name": "Date", "value": "Mon, 19 Dec 2023 12:00:00 +0000"},
      {"name": "Message-ID", "value": "<abc123@mail.example.com>"},
      {"name": "Content-Type", "value": "multipart/alternative; boundary=\"boundary123\""}
    ],
    "body": {"size": 0},  // Empty for multipart
    "parts": [...]        // Sub-parts for multipart
  }
}
```

### Format options

| format | Returns | Quota units | Use case |
|--------|---------|-------------|----------|
| `full` | Complete payload with all parts | 5 | Reading message content |
| `metadata` | Headers only, no body | 5 | Subject/from/date only |
| `minimal` | Labels + IDs only | 5 | Checking labels |
| `raw` | Full RFC 2822 as base64url string | 5 | Archiving, forwarding as-is |

### Metadata format with header filtering

```python
# Only fetch specific headers (faster, less data)
msg = service.users().messages().get(
    userId='me',
    id=message_id,
    format='metadata',
    metadataHeaders=['From', 'To', 'Subject', 'Date']
).execute()
```

---

## Payload and MIME Parts

Gmail messages are MIME structures. The `payload` represents the top-level MIME entity.

### Common MIME structures

**Simple text email:**
```
mimeType: text/plain
body.data: <base64url encoded text>
```

**HTML email:**
```
mimeType: text/html
body.data: <base64url encoded HTML>
```

**Text + HTML (most common):**
```
mimeType: multipart/alternative
parts:
  [0] mimeType: text/plain, body.data: ...
  [1] mimeType: text/html,  body.data: ...
```

**Email with attachments:**
```
mimeType: multipart/mixed
parts:
  [0] mimeType: multipart/alternative
      parts:
        [0] text/plain
        [1] text/html
  [1] mimeType: application/pdf
      filename: "report.pdf"
      body.attachmentId: "ANGjdJ..."
```

**Inline images:**
```
mimeType: multipart/related
parts:
  [0] multipart/alternative (text + html)
  [1] image/png, headers: Content-ID: <image001>, Content-Disposition: inline
```

---

## Extracting Body Text

```python
import base64

def decode_body(data: str) -> str:
    """Decode base64url encoded body data."""
    return base64.urlsafe_b64decode(data + '==').decode('utf-8', errors='replace')

def get_body(payload: dict, prefer_html: bool = False) -> tuple[str, str]:
    """
    Recursively extract plain text and HTML body from message payload.
    Returns (plain_text, html_text).
    """
    plain = ''
    html = ''

    def extract(part):
        nonlocal plain, html
        mime = part.get('mimeType', '')
        body = part.get('body', {})
        data = body.get('data', '')

        if mime == 'text/plain' and data:
            plain = decode_body(data)
        elif mime == 'text/html' and data:
            html = decode_body(data)
        elif 'parts' in part:
            for subpart in part['parts']:
                extract(subpart)

    extract(payload)
    return plain, html

# Usage
msg = service.users().messages().get(userId='me', id=msg_id, format='full').execute()
plain, html = get_body(msg['payload'])
```

### Handling nested multipart

Some messages have deeply nested MIME structures (e.g., forwarded messages). The recursive approach above handles arbitrary depth. Watch for:
- `multipart/signed` — signed emails with signature as separate part
- `message/rfc822` — forwarded message as attachment
- `multipart/report` — delivery status notifications

---

## Attachments

### List attachments from a message

```python
def list_attachments(payload: dict) -> list[dict]:
    """Return list of {filename, mimeType, attachmentId, size}."""
    attachments = []

    def find_attachments(part):
        filename = part.get('filename', '')
        body = part.get('body', {})
        if filename and body.get('attachmentId'):
            attachments.append({
                'filename': filename,
                'mimeType': part.get('mimeType', ''),
                'attachmentId': body['attachmentId'],
                'size': body.get('size', 0)
            })
        for subpart in part.get('parts', []):
            find_attachments(subpart)

    find_attachments(payload)
    return attachments
```

### Download an attachment

```python
import base64, os

def download_attachment(service, user_id: str, message_id: str, attachment_id: str,
                         filename: str, save_dir: str = '.'):
    """Download and save an attachment."""
    attachment = service.users().messages().attachments().get(
        userId=user_id,
        messageId=message_id,
        id=attachment_id
    ).execute()

    data = attachment['data']
    file_data = base64.urlsafe_b64decode(data + '==')
    filepath = os.path.join(save_dir, filename)

    with open(filepath, 'wb') as f:
        f.write(file_data)

    return filepath

# Download all attachments from a message
msg = service.users().messages().get(userId='me', id=msg_id, format='full').execute()
attachments = list_attachments(msg['payload'])
for att in attachments:
    path = download_attachment(service, 'me', msg_id, att['attachmentId'], att['filename'])
    print(f"Saved: {path}")
```

---

## Creating Messages

### Plain text

```python
import base64
from email.mime.text import MIMEText

def create_plain_message(to: str, subject: str, body: str,
                          from_: str = None, reply_to: str = None) -> dict:
    msg = MIMEText(body, 'plain')
    msg['To'] = to
    msg['Subject'] = subject
    if from_:
        msg['From'] = from_
    if reply_to:
        msg['Reply-To'] = reply_to
    return {'raw': base64.urlsafe_b64encode(msg.as_bytes()).decode()}
```

### HTML with plain text fallback

```python
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def create_html_message(to: str, subject: str, html_body: str,
                         plain_body: str = None) -> dict:
    msg = MIMEMultipart('alternative')
    msg['To'] = to
    msg['Subject'] = subject

    if plain_body:
        msg.attach(MIMEText(plain_body, 'plain'))
    msg.attach(MIMEText(html_body, 'html'))

    return {'raw': base64.urlsafe_b64encode(msg.as_bytes()).decode()}
```

### With attachments

```python
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import os

def create_message_with_attachments(to: str, subject: str, html_body: str,
                                     attachment_paths: list[str]) -> dict:
    msg = MIMEMultipart('mixed')
    msg['To'] = to
    msg['Subject'] = subject

    # Body
    alternative = MIMEMultipart('alternative')
    alternative.attach(MIMEText(html_body, 'html'))
    msg.attach(alternative)

    # Attachments
    for filepath in attachment_paths:
        with open(filepath, 'rb') as f:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(f.read())
        encoders.encode_base64(part)
        part.add_header(
            'Content-Disposition',
            f'attachment; filename="{os.path.basename(filepath)}"'
        )
        msg.attach(part)

    return {'raw': base64.urlsafe_b64encode(msg.as_bytes()).decode()}
```

### Reply to a thread

```python
def create_reply(to: str, subject: str, body: str,
                  thread_id: str, in_reply_to: str, references: str) -> dict:
    msg = MIMEText(body, 'plain')
    msg['To'] = to
    msg['Subject'] = subject
    msg['In-Reply-To'] = in_reply_to    # Message-ID of message being replied to
    msg['References'] = references       # All prior Message-IDs in thread

    return {
        'raw': base64.urlsafe_b64encode(msg.as_bytes()).decode(),
        'threadId': thread_id  # Keeps message in same thread
    }

# To get in_reply_to and references from the original message:
orig = service.users().messages().get(userId='me', id=orig_id, format='metadata').execute()
headers = {h['name']: h['value'] for h in orig['payload']['headers']}
in_reply_to = headers.get('Message-ID', '')
references = headers.get('References', '') + ' ' + in_reply_to
```

---

## Raw Format

The `raw` format returns the entire RFC 2822 message as a base64url string.

```python
import base64, email

# Fetch raw
msg = service.users().messages().get(userId='me', id=msg_id, format='raw').execute()
raw_bytes = base64.urlsafe_b64decode(msg['raw'] + '==')

# Parse with Python's email library
email_msg = email.message_from_bytes(raw_bytes)
print(email_msg['From'])
print(email_msg['Subject'])
print(email_msg.get_payload(decode=True))  # For simple messages

# Useful for: archiving, re-sending, debugging exact wire format
```

### Insert (import) a raw message

```python
# Insert an existing RFC 2822 message into Gmail (e.g., migration)
with open('email.eml', 'rb') as f:
    raw = base64.urlsafe_b64encode(f.read()).decode()

service.users().messages().insert(
    userId='me',
    body={'raw': raw, 'labelIds': ['INBOX']}
).execute()

# Or use .import_() to apply filters and classification:
service.users().messages().import_(
    userId='me',
    body={'raw': raw},
    processForCalendar=False,
    internalDateSource='dateHeader'
).execute()
```
