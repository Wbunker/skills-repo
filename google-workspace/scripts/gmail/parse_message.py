"""
Gmail Message Parser
Full MIME message parsing: headers, body text, HTML, attachments, inline images.
"""
import base64
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class Attachment:
    filename: str
    mime_type: str
    attachment_id: str  # Use with messages.attachments.get()
    size: int
    data: Optional[bytes] = None  # Populated after download


@dataclass
class ParsedMessage:
    id: str
    thread_id: str
    label_ids: list[str]
    snippet: str
    internal_date_ms: int

    # Headers
    subject: str
    from_: str
    to: str
    cc: str
    bcc: str
    date: str
    message_id: str       # RFC 2822 Message-ID header
    in_reply_to: str
    references: str

    # Body
    plain_text: str
    html_body: str

    # Attachments
    attachments: list[Attachment] = field(default_factory=list)
    inline_images: list[Attachment] = field(default_factory=list)

    @property
    def has_attachments(self) -> bool:
        return len(self.attachments) > 0

    @property
    def body(self) -> str:
        """Return plain text body, falling back to stripped HTML."""
        if self.plain_text:
            return self.plain_text
        if self.html_body:
            import re
            return re.sub(r'<[^>]+>', '', self.html_body).strip()
        return self.snippet


def decode_b64(data: str) -> str:
    """Decode base64url encoded string to UTF-8 text."""
    # Gmail uses URL-safe base64, padding may be missing
    padded = data + '==' * (4 - len(data) % 4 if len(data) % 4 else 0)
    return base64.urlsafe_b64decode(padded).decode('utf-8', errors='replace')


def decode_b64_bytes(data: str) -> bytes:
    """Decode base64url encoded string to raw bytes."""
    padded = data + '==' * (4 - len(data) % 4 if len(data) % 4 else 0)
    return base64.urlsafe_b64decode(padded)


def _extract_parts(payload: dict, plain_parts: list, html_parts: list,
                   attachment_parts: list, inline_parts: list):
    """Recursively walk MIME tree and collect parts by type."""
    mime_type = payload.get('mimeType', '')
    body = payload.get('body', {})
    headers = {h['name'].lower(): h['value'] for h in payload.get('headers', [])}
    filename = payload.get('filename', '')
    content_disposition = headers.get('content-disposition', '')
    content_id = headers.get('content-id', '')

    if 'parts' in payload:
        # Multipart: recurse into parts
        for part in payload['parts']:
            _extract_parts(part, plain_parts, html_parts, attachment_parts, inline_parts)
    elif mime_type == 'text/plain' and not filename:
        if body.get('data'):
            plain_parts.append(decode_b64(body['data']))
    elif mime_type == 'text/html' and not filename:
        if body.get('data'):
            html_parts.append(decode_b64(body['data']))
    elif body.get('attachmentId'):
        # It's an attachment (either real or inline image)
        att = Attachment(
            filename=filename or f'attachment_{len(attachment_parts)}',
            mime_type=mime_type,
            attachment_id=body['attachmentId'],
            size=body.get('size', 0)
        )
        if content_disposition.startswith('inline') or content_id:
            inline_parts.append(att)
        else:
            attachment_parts.append(att)
    elif body.get('data') and filename:
        # Small attachment with inline data (uncommon)
        att = Attachment(
            filename=filename,
            mime_type=mime_type,
            attachment_id='',
            size=body.get('size', 0),
            data=decode_b64_bytes(body['data'])
        )
        attachment_parts.append(att)


def parse_message(msg: dict) -> ParsedMessage:
    """
    Parse a full Gmail message object into a structured ParsedMessage.

    Args:
        msg: Message dict from messages.get(format='full').execute()
    """
    payload = msg.get('payload', {})
    headers = {h['name']: h['value'] for h in payload.get('headers', [])}

    plain_parts: list[str] = []
    html_parts: list[str] = []
    attachment_parts: list[Attachment] = []
    inline_parts: list[Attachment] = []

    _extract_parts(payload, plain_parts, html_parts, attachment_parts, inline_parts)

    return ParsedMessage(
        id=msg['id'],
        thread_id=msg.get('threadId', ''),
        label_ids=msg.get('labelIds', []),
        snippet=msg.get('snippet', ''),
        internal_date_ms=int(msg.get('internalDate', 0)),

        subject=headers.get('Subject', ''),
        from_=headers.get('From', ''),
        to=headers.get('To', ''),
        cc=headers.get('Cc', ''),
        bcc=headers.get('Bcc', ''),
        date=headers.get('Date', ''),
        message_id=headers.get('Message-ID', ''),
        in_reply_to=headers.get('In-Reply-To', ''),
        references=headers.get('References', ''),

        plain_text='\n'.join(plain_parts),
        html_body='\n'.join(html_parts),
        attachments=attachment_parts,
        inline_images=inline_parts,
    )


def download_attachment(service, message_id: str, attachment: Attachment,
                         save_dir: str = '.') -> str:
    """
    Download an attachment to disk.

    Returns: Path to saved file.
    """
    if attachment.data:
        # Already has data (small inline attachment)
        filepath = os.path.join(save_dir, attachment.filename)
        Path(filepath).write_bytes(attachment.data)
        return filepath

    # Fetch from API
    att_data = service.users().messages().attachments().get(
        userId='me',
        messageId=message_id,
        id=attachment.attachment_id
    ).execute()

    file_data = decode_b64_bytes(att_data['data'])
    filepath = os.path.join(save_dir, attachment.filename)
    Path(filepath).write_bytes(file_data)
    attachment.data = file_data  # Cache it

    return filepath


def download_all_attachments(service, message_id: str, parsed: ParsedMessage,
                              save_dir: str = '.') -> list[str]:
    """Download all attachments from a parsed message. Returns list of file paths."""
    os.makedirs(save_dir, exist_ok=True)
    paths = []
    for att in parsed.attachments:
        path = download_attachment(service, message_id, att, save_dir)
        paths.append(path)
        print(f"  Downloaded: {path} ({att.size:,} bytes)")
    return paths


def extract_email_address(from_header: str) -> str:
    """Extract plain email address from 'Name <email@example.com>' format."""
    import re
    match = re.search(r'<([^>]+)>', from_header)
    if match:
        return match.group(1)
    return from_header.strip()


def message_to_dict(parsed: ParsedMessage) -> dict:
    """Convert ParsedMessage to a plain dict (for JSON serialization)."""
    return {
        'id': parsed.id,
        'threadId': parsed.thread_id,
        'subject': parsed.subject,
        'from': parsed.from_,
        'to': parsed.to,
        'date': parsed.date,
        'body': parsed.body,
        'hasAttachments': parsed.has_attachments,
        'attachments': [
            {'filename': a.filename, 'mimeType': a.mime_type, 'size': a.size}
            for a in parsed.attachments
        ],
        'labels': parsed.label_ids,
    }


if __name__ == '__main__':
    from auth import get_service
    from list_messages import list_message_ids

    service = get_service()

    # Parse the 3 most recent inbox messages
    stubs = list_message_ids(service, query='in:inbox', max_results=3)

    for stub in stubs:
        raw = service.users().messages().get(
            userId='me', id=stub['id'], format='full'
        ).execute()

        msg = parse_message(raw)
        print(f"\n{'='*60}")
        print(f"Subject: {msg.subject}")
        print(f"From: {msg.from_}")
        print(f"Date: {msg.date}")
        print(f"Labels: {', '.join(msg.label_ids)}")
        if msg.attachments:
            print(f"Attachments: {[a.filename for a in msg.attachments]}")
        print(f"Body preview: {msg.body[:200]}...")
