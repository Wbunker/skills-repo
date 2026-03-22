# Outlook Mail API (Microsoft Graph)

Access Outlook/Exchange Online mail via Microsoft Graph.

## Permissions

| Scenario | Delegated | Application |
|----------|-----------|-------------|
| Read mail | `Mail.Read` | `Mail.Read` (reads all users' mail) |
| Read + write mail | `Mail.ReadWrite` | `Mail.ReadWrite.All` |
| Send mail | `Mail.Send` | `Mail.Send.All` |
| Read shared mailboxes | `Mail.Read.Shared` | — |

**Note**: Application permissions grant access to ALL users in the tenant. Always
use delegated permissions when a user context is available.

## Base Endpoints

```
GET  /me/messages                         # List inbox messages (delegated)
GET  /users/{user-id}/messages            # List a user's messages (app-only)
GET  /me/mailFolders                      # List mail folders
GET  /me/mailFolders/{folder-id}/messages # Messages in a folder
```

## List Messages

```python
import asyncio
from msgraph import GraphServiceClient
from msgraph.generated.users.item.messages.messages_request_builder import (
    MessagesRequestBuilder,
)
from kiota_abstractions.base_request_configuration import RequestConfiguration

async def list_messages(graph_client, top=10, folder="inbox"):
    query_params = MessagesRequestBuilder.MessagesRequestBuilderGetQueryParameters(
        select=["id", "subject", "sender", "receivedDateTime", "isRead", "bodyPreview"],
        top=top,
        order_by=["receivedDateTime DESC"],
        filter=f"parentFolderId eq 'inbox'",
    )
    config = RequestConfiguration(query_parameters=query_params)
    messages = await graph_client.me.messages.get(request_configuration=config)
    return messages.value
```

### Well-Known Folder Names

Use these as folder IDs directly (no lookup needed):

| Name | Description |
|------|-------------|
| `inbox` | Inbox |
| `sentitems` | Sent Items |
| `drafts` | Drafts |
| `deleteditems` | Deleted Items |
| `junkemail` | Junk Email |
| `archive` | Archive |
| `outbox` | Outbox |

```
GET /me/mailFolders('SentItems')/messages?$select=sender,subject
```

## Search / Filter Messages

### OData Filter Examples

```
# Unread messages
$filter=isRead eq false

# From a specific sender
$filter=from/emailAddress/address eq 'sender@example.com'

# High importance
$filter=importance eq 'high'

# Subject contains (note: startsWith supported, contains requires $search)
$filter=startswith(subject, 'Invoice')

# Received after a date
$filter=receivedDateTime ge 2024-01-01T00:00:00Z

# Has attachments
$filter=hasAttachments eq true

# Combine filters
$filter=isRead eq false and importance eq 'high'
```

### Full-Text Search

```
GET /me/messages?$search="project proposal"
GET /me/messages?$search="from:boss@company.com"
GET /me/messages?$search="subject:quarterly report"
```

## Read a Single Message

```python
async def get_message(graph_client, message_id):
    message = await graph_client.me.messages.by_message_id(message_id).get()
    return message

# Access properties
# message.subject
# message.body.content          (HTML or text)
# message.body.content_type     ('html' or 'text')
# message.sender.email_address.address
# message.received_date_time
# message.is_read
# message.has_attachments
# message.conversation_id
# message.internet_message_id
```

## Send an Email

```python
from msgraph.generated.models.message import Message
from msgraph.generated.models.item_body import ItemBody
from msgraph.generated.models.body_type import BodyType
from msgraph.generated.models.recipient import Recipient
from msgraph.generated.models.email_address import EmailAddress
from msgraph.generated.users.item.send_mail.send_mail_post_request_body import (
    SendMailPostRequestBody,
)

async def send_email(graph_client, to_address, subject, body_html):
    message = Message(
        subject=subject,
        body=ItemBody(
            content_type=BodyType.Html,
            content=body_html,
        ),
        to_recipients=[
            Recipient(
                email_address=EmailAddress(address=to_address)
            )
        ],
    )
    request_body = SendMailPostRequestBody(
        message=message,
        save_to_sent_items=True,
    )
    await graph_client.me.send_mail.post(request_body)
```

### Send with CC, BCC, and Reply-To

```python
message = Message(
    subject="Quarterly Report",
    body=ItemBody(content_type=BodyType.Html, content="<b>See attached.</b>"),
    to_recipients=[
        Recipient(email_address=EmailAddress(address="alice@example.com")),
        Recipient(email_address=EmailAddress(address="bob@example.com")),
    ],
    cc_recipients=[
        Recipient(email_address=EmailAddress(address="manager@example.com")),
    ],
    bcc_recipients=[
        Recipient(email_address=EmailAddress(address="archive@example.com")),
    ],
    reply_to=[
        Recipient(email_address=EmailAddress(
            address="noreply@example.com",
            name="No Reply",
        )),
    ],
    importance="high",  # 'low', 'normal', 'high'
)
```

## Reply to a Message

```python
from msgraph.generated.users.item.messages.item.reply.reply_post_request_body import (
    ReplyPostRequestBody,
)

async def reply_to_message(graph_client, message_id, reply_text):
    request_body = ReplyPostRequestBody(
        comment=reply_text,
    )
    await graph_client.me.messages.by_message_id(message_id).reply.post(request_body)
```

## Forward a Message

```python
from msgraph.generated.users.item.messages.item.forward.forward_post_request_body import (
    ForwardPostRequestBody,
)

async def forward_message(graph_client, message_id, to_address, comment):
    request_body = ForwardPostRequestBody(
        to_recipients=[
            Recipient(email_address=EmailAddress(address=to_address))
        ],
        comment=comment,
    )
    await graph_client.me.messages.by_message_id(message_id).forward.post(request_body)
```

## Create and Send a Draft

```python
# 1. Create draft
from msgraph.generated.models.message import Message

draft = Message(
    subject="Draft subject",
    body=ItemBody(content_type=BodyType.Text, content="Draft body"),
    to_recipients=[
        Recipient(email_address=EmailAddress(address="recipient@example.com"))
    ],
    is_draft=True,
)
created_draft = await graph_client.me.messages.post(draft)

# 2. Update draft if needed
# await graph_client.me.messages.by_message_id(created_draft.id).patch(updated_draft)

# 3. Send the draft
await graph_client.me.messages.by_message_id(created_draft.id).send.post()
```

## Download Attachments

```python
async def get_attachments(graph_client, message_id):
    attachments = await graph_client.me.messages.by_message_id(
        message_id
    ).attachments.get()
    return attachments.value

async def download_attachment(graph_client, message_id, attachment_id, save_path):
    attachment = await graph_client.me.messages.by_message_id(
        message_id
    ).attachments.by_attachment_id(attachment_id).get()

    # attachment.content_bytes is a bytes-like object (base64 decoded by SDK)
    with open(save_path, "wb") as f:
        f.write(attachment.content_bytes)
```

## Add Attachment When Sending

```python
from msgraph.generated.models.file_attachment import FileAttachment
import base64

with open("report.pdf", "rb") as f:
    file_bytes = f.read()

message = Message(
    subject="See attached report",
    body=ItemBody(content_type=BodyType.Text, content="Please find the report attached."),
    to_recipients=[
        Recipient(email_address=EmailAddress(address="recipient@example.com"))
    ],
    attachments=[
        FileAttachment(
            odata_type="#microsoft.graph.fileAttachment",
            name="report.pdf",
            content_type="application/pdf",
            content_bytes=file_bytes,
        )
    ],
)
request_body = SendMailPostRequestBody(message=message, save_to_sent_items=True)
await graph_client.me.send_mail.post(request_body)
```

**Note**: For attachments > 3 MB, use the upload session API instead.

## Move and Copy Messages

```python
from msgraph.generated.users.item.messages.item.move.move_post_request_body import (
    MovePostRequestBody,
)

# Move to folder by well-known name
await graph_client.me.messages.by_message_id(message_id).move.post(
    MovePostRequestBody(destination_id="deleteditems")
)

# Copy to folder
from msgraph.generated.users.item.messages.item.copy.copy_post_request_body import (
    CopyPostRequestBody,
)
await graph_client.me.messages.by_message_id(message_id).copy.post(
    CopyPostRequestBody(destination_id="archive")
)
```

## Mark as Read / Update Message

```python
from msgraph.generated.models.message import Message

await graph_client.me.messages.by_message_id(message_id).patch(
    Message(is_read=True)
)

# Flag a message
from msgraph.generated.models.follow_up_flag import FollowUpFlag
from msgraph.generated.models.follow_up_flag_status import FollowUpFlagStatus

await graph_client.me.messages.by_message_id(message_id).patch(
    Message(flag=FollowUpFlag(flag_status=FollowUpFlagStatus.Flagged))
)
```

## Delete a Message

```python
await graph_client.me.messages.by_message_id(message_id).delete()
```

## Paginate Through All Messages

```python
async def get_all_messages(graph_client, folder="inbox", page_size=50):
    all_messages = []

    query_params = MessagesRequestBuilder.MessagesRequestBuilderGetQueryParameters(
        select=["id", "subject", "sender", "receivedDateTime", "isRead"],
        top=page_size,
        order_by=["receivedDateTime DESC"],
    )
    config = RequestConfiguration(query_parameters=query_params)
    page = await graph_client.me.mail_folders.by_mail_folder_id(folder).messages.get(
        request_configuration=config
    )

    while page:
        all_messages.extend(page.value)
        if page.odata_next_link:
            # Fetch next page using the nextLink URL
            page = await graph_client.me.mail_folders.by_mail_folder_id(
                folder
            ).messages.with_url(page.odata_next_link).get()
        else:
            break

    return all_messages
```

## Mailbox Settings

```python
# Get mailbox settings (timezone, auto-reply, working hours)
settings = await graph_client.me.mailbox_settings.get()
# settings.time_zone
# settings.automatic_replies_setting.status  ('disabled', 'alwaysEnabled', 'scheduled')

# Update auto-reply
from msgraph.generated.models.mailbox_settings import MailboxSettings
from msgraph.generated.models.automatic_replies_setting import AutomaticRepliesSetting

await graph_client.me.mailbox_settings.patch(
    MailboxSettings(
        automatic_replies_setting=AutomaticRepliesSetting(
            status="alwaysEnabled",
            external_reply_message="I am out of office.",
            internal_reply_message="I am out of office.",
        )
    )
)
```

## Inbox Rules (Message Rules)

```python
# List rules
rules = await graph_client.me.mail_folders.by_mail_folder_id("inbox").message_rules.get()

# Create a rule to move emails from a sender to a folder
from msgraph.generated.models.message_rule import MessageRule
from msgraph.generated.models.message_rule_predicates import MessageRulePredicates
from msgraph.generated.models.message_rule_actions import MessageRuleActions

rule = MessageRule(
    display_name="Move newsletters",
    sequence=1,
    is_enabled=True,
    conditions=MessageRulePredicates(
        sender_contains=["newsletter@example.com"],
    ),
    actions=MessageRuleActions(
        move_to_folder="FOLDER_ID_HERE",
    ),
)
await graph_client.me.mail_folders.by_mail_folder_id("inbox").message_rules.post(rule)
```

## OData Query Parameters for Messages

| Parameter | Example | Notes |
|-----------|---------|-------|
| `$select` | `subject,sender,receivedDateTime` | Reduce payload |
| `$filter` | `isRead eq false` | Filter messages |
| `$search` | `"quarterly report"` | Full-text search |
| `$orderby` | `receivedDateTime DESC` | Sort order |
| `$top` | `25` | Page size (default 10, max 1000) |
| `$skip` | `25` | Skip N items |
| `$expand` | `attachments` | Include related resources |

## Throttling

- Graph applies rate limits per app and tenant
- HTTP 429 returned when throttled
- `Retry-After` header specifies seconds to wait
- The SDK handles retries automatically
- Use `$select` to reduce response size and avoid quota issues
- Use `$filter` rather than client-side filtering
