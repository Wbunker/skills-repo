"""
Send emails via Outlook/Exchange using the Microsoft Graph API.

Requirements:
    pip install msgraph-sdk azure-identity python-dotenv

Permissions needed:
    - Delegated: Mail.Send
    - Application: Mail.Send.All (to send on behalf of a specific user)
"""

import asyncio
import os
from pathlib import Path
from msgraph import GraphServiceClient
from msgraph.generated.models.message import Message
from msgraph.generated.models.item_body import ItemBody
from msgraph.generated.models.body_type import BodyType
from msgraph.generated.models.recipient import Recipient
from msgraph.generated.models.email_address import EmailAddress
from msgraph.generated.models.file_attachment import FileAttachment
from msgraph.generated.users.item.send_mail.send_mail_post_request_body import (
    SendMailPostRequestBody,
)


async def send_plain_text_email(
    graph_client: GraphServiceClient,
    to: str | list[str],
    subject: str,
    body: str,
    cc: str | list[str] = None,
    bcc: str | list[str] = None,
    save_to_sent: bool = True,
) -> None:
    """
    Send a plain text email from the signed-in user (delegated)
    or from a specific user (app-only, use send_email_as_user below).

    Args:
        graph_client: Authenticated GraphServiceClient
        to: Recipient email(s) — string or list of strings
        subject: Email subject
        body: Plain text body
        cc: CC email(s)
        bcc: BCC email(s)
        save_to_sent: Whether to save to Sent Items
    """
    to_list = [to] if isinstance(to, str) else to
    cc_list = [cc] if isinstance(cc, str) else (cc or [])
    bcc_list = [bcc] if isinstance(bcc, str) else (bcc or [])

    def make_recipients(emails):
        return [
            Recipient(email_address=EmailAddress(address=email))
            for email in emails
        ]

    message = Message(
        subject=subject,
        body=ItemBody(
            content_type=BodyType.Text,
            content=body,
        ),
        to_recipients=make_recipients(to_list),
        cc_recipients=make_recipients(cc_list) if cc_list else None,
        bcc_recipients=make_recipients(bcc_list) if bcc_list else None,
    )

    request_body = SendMailPostRequestBody(
        message=message,
        save_to_sent_items=save_to_sent,
    )

    await graph_client.me.send_mail.post(request_body)
    print(f"Email sent to {', '.join(to_list)}")


async def send_html_email(
    graph_client: GraphServiceClient,
    to: str | list[str],
    subject: str,
    html_body: str,
    cc: str | list[str] = None,
    importance: str = "normal",
) -> None:
    """
    Send an HTML email.

    Args:
        importance: 'low', 'normal', or 'high'
    """
    to_list = [to] if isinstance(to, str) else to
    cc_list = [cc] if isinstance(cc, str) else (cc or [])

    message = Message(
        subject=subject,
        body=ItemBody(
            content_type=BodyType.Html,
            content=html_body,
        ),
        to_recipients=[
            Recipient(email_address=EmailAddress(address=email))
            for email in to_list
        ],
        cc_recipients=[
            Recipient(email_address=EmailAddress(address=email))
            for email in cc_list
        ] or None,
        importance=importance,
    )

    request_body = SendMailPostRequestBody(message=message, save_to_sent_items=True)
    await graph_client.me.send_mail.post(request_body)


async def send_email_with_attachments(
    graph_client: GraphServiceClient,
    to: str | list[str],
    subject: str,
    body: str,
    attachment_paths: list[str],
    html_body: bool = False,
) -> None:
    """
    Send email with file attachments.

    Note: For files > 3 MB, use the upload session attachment API instead.
    This method is for small attachments only.

    Args:
        attachment_paths: List of local file paths to attach
    """
    to_list = [to] if isinstance(to, str) else to

    # Build attachments
    attachments = []
    for path in attachment_paths:
        file_path = Path(path)
        if not file_path.exists():
            raise FileNotFoundError(f"Attachment not found: {path}")

        content = file_path.read_bytes()
        import mimetypes
        mime_type, _ = mimetypes.guess_type(str(file_path))
        mime_type = mime_type or "application/octet-stream"

        attachments.append(
            FileAttachment(
                odata_type="#microsoft.graph.fileAttachment",
                name=file_path.name,
                content_type=mime_type,
                content_bytes=content,
            )
        )

    message = Message(
        subject=subject,
        body=ItemBody(
            content_type=BodyType.Html if html_body else BodyType.Text,
            content=body,
        ),
        to_recipients=[
            Recipient(email_address=EmailAddress(address=email))
            for email in to_list
        ],
        attachments=attachments,
    )

    request_body = SendMailPostRequestBody(message=message, save_to_sent_items=True)
    await graph_client.me.send_mail.post(request_body)
    print(f"Email with {len(attachments)} attachment(s) sent to {', '.join(to_list)}")


async def send_email_as_user(
    graph_client: GraphServiceClient,
    user_id: str,
    to: str | list[str],
    subject: str,
    body: str,
) -> None:
    """
    Send email as a specific user (requires app-only with Mail.Send.All permission).

    Args:
        user_id: The user's ID or email (e.g., 'alice@contoso.com')
    """
    to_list = [to] if isinstance(to, str) else to

    message = Message(
        subject=subject,
        body=ItemBody(content_type=BodyType.Text, content=body),
        to_recipients=[
            Recipient(email_address=EmailAddress(address=email))
            for email in to_list
        ],
    )

    request_body = SendMailPostRequestBody(message=message, save_to_sent_items=True)
    await graph_client.users.by_user_id(user_id).send_mail.post(request_body)
    print(f"Email sent as {user_id} to {', '.join(to_list)}")


# --- Example Usage ---
if __name__ == "__main__":
    from dotenv import load_dotenv
    from azure.identity import DeviceCodeCredential

    load_dotenv()

    async def main():
        credential = DeviceCodeCredential(
            tenant_id=os.environ.get("AZURE_TENANT_ID", "common"),
            client_id=os.environ["AZURE_CLIENT_ID"],
        )
        graph = GraphServiceClient(credential, ["Mail.Send"])

        # Send a simple email
        await send_plain_text_email(
            graph,
            to="recipient@example.com",
            subject="Test from Graph API",
            body="Hello! This was sent via the Microsoft Graph API.",
        )

        # Send HTML email with importance
        await send_html_email(
            graph,
            to=["alice@example.com", "bob@example.com"],
            subject="Monthly Report",
            html_body="""
                <h2>Monthly Report</h2>
                <p>Please find the summary below:</p>
                <ul>
                    <li>Revenue: $1.2M</li>
                    <li>New customers: 42</li>
                </ul>
            """,
            importance="high",
        )

        # Send with attachments
        await send_email_with_attachments(
            graph,
            to="manager@example.com",
            subject="Q4 Report",
            body="Please find the Q4 report attached.",
            attachment_paths=["report.pdf", "data.xlsx"],
        )

    asyncio.run(main())
