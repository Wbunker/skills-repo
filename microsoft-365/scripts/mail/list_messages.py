"""
Search, list, read, and paginate Outlook messages via Microsoft Graph.

Requirements:
    pip install msgraph-sdk azure-identity python-dotenv

Permissions needed:
    - Delegated: Mail.Read or Mail.ReadWrite
    - Application: Mail.Read (reads all users' mail)
"""

import asyncio
import os
from msgraph import GraphServiceClient
from msgraph.generated.users.item.messages.messages_request_builder import (
    MessagesRequestBuilder,
)
from msgraph.generated.users.item.mail_folders.item.messages.messages_request_builder import (
    MessagesRequestBuilder as FolderMessagesRequestBuilder,
)
from kiota_abstractions.base_request_configuration import RequestConfiguration


COMMON_SELECT = [
    "id", "subject", "sender", "from", "toRecipients",
    "receivedDateTime", "isRead", "hasAttachments",
    "bodyPreview", "importance", "conversationId", "flag",
]


async def list_inbox_messages(
    graph_client: GraphServiceClient,
    top: int = 25,
    unread_only: bool = False,
) -> list:
    """
    List messages from the inbox.

    Args:
        top: Number of messages to return (max 1000 per page)
        unread_only: If True, only return unread messages

    Returns:
        List of message objects
    """
    filter_str = "isRead eq false" if unread_only else None

    query_params = MessagesRequestBuilder.MessagesRequestBuilderGetQueryParameters(
        select=COMMON_SELECT,
        top=top,
        order_by=["receivedDateTime DESC"],
        filter=filter_str,
    )
    config = RequestConfiguration(query_parameters=query_params)
    result = await graph_client.me.messages.get(request_configuration=config)
    return result.value or []


async def list_folder_messages(
    graph_client: GraphServiceClient,
    folder_name: str = "inbox",
    top: int = 25,
    filter_str: str = None,
) -> list:
    """
    List messages from a specific folder.

    Args:
        folder_name: Well-known name like 'inbox', 'sentitems', 'drafts',
                     'deleteditems', 'junkemail', 'archive'
                     OR a folder ID

    Returns:
        List of message objects
    """
    query_params = FolderMessagesRequestBuilder.MessagesRequestBuilderGetQueryParameters(
        select=COMMON_SELECT,
        top=top,
        order_by=["receivedDateTime DESC"],
        filter=filter_str,
    )
    config = RequestConfiguration(query_parameters=query_params)
    result = await graph_client.me.mail_folders.by_mail_folder_id(
        folder_name
    ).messages.get(request_configuration=config)
    return result.value or []


async def search_messages(
    graph_client: GraphServiceClient,
    query: str,
    top: int = 25,
) -> list:
    """
    Full-text search across messages.

    Args:
        query: Search query, e.g.:
               "quarterly report"
               "from:boss@company.com"
               "subject:invoice"
               "hasAttachments:true"

    Returns:
        List of matching message objects
    """
    query_params = MessagesRequestBuilder.MessagesRequestBuilderGetQueryParameters(
        search=f'"{query}"',
        select=COMMON_SELECT,
        top=top,
    )
    config = RequestConfiguration(query_parameters=query_params)
    result = await graph_client.me.messages.get(request_configuration=config)
    return result.value or []


async def filter_messages(
    graph_client: GraphServiceClient,
    filter_str: str,
    top: int = 25,
) -> list:
    """
    Filter messages using OData filter expressions.

    Args:
        filter_str: OData filter, e.g.:
                    "isRead eq false"
                    "importance eq 'high'"
                    "from/emailAddress/address eq 'boss@company.com'"
                    "hasAttachments eq true"
                    "receivedDateTime ge 2024-01-01T00:00:00Z"

    Returns:
        List of matching message objects
    """
    query_params = MessagesRequestBuilder.MessagesRequestBuilderGetQueryParameters(
        filter=filter_str,
        select=COMMON_SELECT,
        top=top,
        order_by=["receivedDateTime DESC"],
    )
    config = RequestConfiguration(query_parameters=query_params)
    result = await graph_client.me.messages.get(request_configuration=config)
    return result.value or []


async def get_all_messages_paginated(
    graph_client: GraphServiceClient,
    folder: str = "inbox",
    filter_str: str = None,
    page_size: int = 100,
    max_messages: int = None,
) -> list:
    """
    Paginate through all messages in a folder.

    Args:
        folder: Folder name or ID
        filter_str: Optional OData filter
        page_size: Messages per page (max 1000)
        max_messages: Stop after this many total messages (None = all)

    Returns:
        All matching messages
    """
    all_messages = []

    query_params = FolderMessagesRequestBuilder.MessagesRequestBuilderGetQueryParameters(
        select=COMMON_SELECT,
        top=page_size,
        filter=filter_str,
        order_by=["receivedDateTime DESC"],
    )
    config = RequestConfiguration(query_parameters=query_params)

    page = await graph_client.me.mail_folders.by_mail_folder_id(
        folder
    ).messages.get(request_configuration=config)

    while page:
        batch = page.value or []
        all_messages.extend(batch)

        if max_messages and len(all_messages) >= max_messages:
            all_messages = all_messages[:max_messages]
            break

        if page.odata_next_link:
            page = await graph_client.me.mail_folders.by_mail_folder_id(
                folder
            ).messages.with_url(page.odata_next_link).get()
        else:
            break

    return all_messages


async def get_message_with_body(
    graph_client: GraphServiceClient,
    message_id: str,
) -> object:
    """
    Get a single message including full body content.
    """
    message = await graph_client.me.messages.by_message_id(message_id).get()
    return message


async def get_message_attachments(
    graph_client: GraphServiceClient,
    message_id: str,
) -> list:
    """Get list of attachments for a message."""
    attachments = await graph_client.me.messages.by_message_id(
        message_id
    ).attachments.get()
    return attachments.value or []


def format_message_summary(message) -> str:
    """Format a message object into a readable summary string."""
    sender = "unknown"
    if message.sender and message.sender.email_address:
        sender = message.sender.email_address.address

    read_indicator = "  " if message.is_read else "* "
    attach_indicator = "[A] " if message.has_attachments else "    "
    importance = "[!] " if message.importance and message.importance.value == "high" else "    "

    subject = (message.subject or "(no subject)")[:60]
    date = ""
    if message.received_date_time:
        date = message.received_date_time.strftime("%Y-%m-%d %H:%M")

    return f"{read_indicator}{attach_indicator}{importance}{date}  {subject!r:<65}  {sender}"


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
        graph = GraphServiceClient(credential, ["Mail.Read"])

        print("=== Recent Inbox Messages ===")
        messages = await list_inbox_messages(graph, top=10)
        for msg in messages:
            print(format_message_summary(msg))

        print("\n=== Unread Messages ===")
        unread = await list_inbox_messages(graph, top=5, unread_only=True)
        for msg in unread:
            print(format_message_summary(msg))

        print("\n=== Search Results ===")
        results = await search_messages(graph, "invoice")
        for msg in results[:5]:
            print(format_message_summary(msg))

        print("\n=== High Importance Messages ===")
        important = await filter_messages(graph, "importance eq 'high'", top=5)
        for msg in important:
            print(format_message_summary(msg))

        # Read full body of first message
        if messages:
            full_msg = await get_message_with_body(graph, messages[0].id)
            print(f"\n=== Full Body of '{full_msg.subject}' ===")
            content = full_msg.body.content if full_msg.body else "(no body)"
            print(content[:500])

    asyncio.run(main())
