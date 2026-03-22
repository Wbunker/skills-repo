"""
Gmail Send Email Script
Supports: plain text, HTML, attachments, drafts, replies.
"""
import base64
import os
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email import encoders
from pathlib import Path
from typing import Optional

from googleapiclient.errors import HttpError


def _make_raw(msg) -> dict:
    """Encode a MIME message as base64url for Gmail API."""
    return {'raw': base64.urlsafe_b64encode(msg.as_bytes()).decode()}


def send_text(service, to: str, subject: str, body: str,
              cc: str = None, bcc: str = None, reply_to: str = None) -> dict:
    """
    Send a plain text email.

    Returns: sent message resource {id, threadId, labelIds}
    """
    msg = MIMEText(body, 'plain')
    msg['To'] = to
    msg['Subject'] = subject
    if cc:
        msg['Cc'] = cc
    if bcc:
        msg['Bcc'] = bcc
    if reply_to:
        msg['Reply-To'] = reply_to

    return service.users().messages().send(
        userId='me', body=_make_raw(msg)
    ).execute()


def send_html(service, to: str, subject: str, html_body: str,
              plain_body: str = None, cc: str = None, bcc: str = None) -> dict:
    """
    Send an HTML email with optional plain text fallback.

    Args:
        plain_body: Plain text fallback. If None, strips HTML tags as fallback.
    """
    msg = MIMEMultipart('alternative')
    msg['To'] = to
    msg['Subject'] = subject
    if cc:
        msg['Cc'] = cc
    if bcc:
        msg['Bcc'] = bcc

    # Plain text first (lower preference, email clients prefer the last part)
    if plain_body is None:
        import re
        plain_body = re.sub('<[^>]+>', '', html_body).strip()
    msg.attach(MIMEText(plain_body, 'plain'))
    msg.attach(MIMEText(html_body, 'html'))

    return service.users().messages().send(
        userId='me', body=_make_raw(msg)
    ).execute()


def send_with_attachments(
    service,
    to: str,
    subject: str,
    html_body: str,
    attachment_paths: list[str],
    plain_body: str = None,
    cc: str = None
) -> dict:
    """
    Send an HTML email with file attachments.

    Args:
        attachment_paths: List of file paths to attach.
    """
    msg = MIMEMultipart('mixed')
    msg['To'] = to
    msg['Subject'] = subject
    if cc:
        msg['Cc'] = cc

    # Body section
    alternative = MIMEMultipart('alternative')
    if plain_body:
        alternative.attach(MIMEText(plain_body, 'plain'))
    alternative.attach(MIMEText(html_body, 'html'))
    msg.attach(alternative)

    # Attachments
    for filepath in attachment_paths:
        path = Path(filepath)
        if not path.exists():
            raise FileNotFoundError(f"Attachment not found: {filepath}")

        with open(path, 'rb') as f:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(f.read())

        encoders.encode_base64(part)
        part.add_header(
            'Content-Disposition',
            f'attachment; filename="{path.name}"'
        )
        msg.attach(part)

    return service.users().messages().send(
        userId='me', body=_make_raw(msg)
    ).execute()


def send_reply(
    service,
    to: str,
    subject: str,
    body: str,
    thread_id: str,
    in_reply_to: str,
    references: str = None,
    html: bool = False
) -> dict:
    """
    Send a reply within an existing thread.

    Args:
        thread_id: The threadId of the thread to reply in.
        in_reply_to: The Message-ID header of the message being replied to.
        references: Space-separated Message-IDs for the References header.
        html: If True, treat body as HTML.
    """
    mime_type = 'html' if html else 'plain'
    msg = MIMEText(body, mime_type)
    msg['To'] = to
    msg['Subject'] = subject if subject.startswith('Re:') else f'Re: {subject}'
    msg['In-Reply-To'] = in_reply_to
    msg['References'] = f"{references} {in_reply_to}".strip() if references else in_reply_to

    body_dict = _make_raw(msg)
    body_dict['threadId'] = thread_id

    return service.users().messages().send(
        userId='me', body=body_dict
    ).execute()


def create_draft(service, to: str, subject: str, html_body: str,
                  plain_body: str = None, attachment_paths: list[str] = None) -> dict:
    """
    Create a draft (does not send).

    Returns: draft resource {id, message: {id, threadId}}
    """
    if attachment_paths:
        msg = MIMEMultipart('mixed')
        msg['To'] = to
        msg['Subject'] = subject
        alt = MIMEMultipart('alternative')
        if plain_body:
            alt.attach(MIMEText(plain_body, 'plain'))
        alt.attach(MIMEText(html_body, 'html'))
        msg.attach(alt)

        for filepath in attachment_paths:
            path = Path(filepath)
            with open(path, 'rb') as f:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(f.read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f'attachment; filename="{path.name}"')
            msg.attach(part)
    else:
        msg = MIMEMultipart('alternative')
        msg['To'] = to
        msg['Subject'] = subject
        if plain_body:
            msg.attach(MIMEText(plain_body, 'plain'))
        msg.attach(MIMEText(html_body, 'html'))

    return service.users().drafts().create(
        userId='me',
        body={'message': _make_raw(msg)}
    ).execute()


def send_draft(service, draft_id: str) -> dict:
    """Send an existing draft."""
    return service.users().drafts().send(
        userId='me',
        body={'id': draft_id}
    ).execute()


def get_reply_headers(service, message_id: str) -> tuple[str, str, str]:
    """
    Get headers needed to reply to a message.

    Returns: (to, subject, in_reply_to, references) tuple
    """
    msg = service.users().messages().get(
        userId='me', id=message_id, format='metadata',
        metadataHeaders=['From', 'Subject', 'Message-ID', 'References']
    ).execute()

    headers = {h['name']: h['value'] for h in msg['payload']['headers']}
    return (
        headers.get('From', ''),
        headers.get('Subject', ''),
        headers.get('Message-ID', ''),
        headers.get('References', ''),
        msg['threadId']
    )


if __name__ == '__main__':
    from auth import get_service

    service = get_service()

    # Example: send a simple HTML email
    result = send_html(
        service,
        to='recipient@example.com',
        subject='Test from Gmail API',
        html_body='<h1>Hello!</h1><p>This was sent via the Gmail API.</p>',
        plain_body='Hello! This was sent via the Gmail API.'
    )
    print(f"Sent! Message ID: {result['id']}")
    print(f"Thread ID: {result['threadId']}")
