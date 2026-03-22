"""
Send messages to Microsoft Teams channels and chats via Microsoft Graph.

Requirements:
    pip install msgraph-sdk azure-identity python-dotenv

Permissions needed:
    - Send to channels (delegated only): ChannelMessage.Send + Team.ReadBasic.All
    - Send to chats (delegated only): Chat.ReadWrite
    - Read teams/channels: Team.ReadBasic.All, Channel.ReadBasic.All

Note: Application permissions CANNOT send messages to channels or chats.
You must use delegated permissions (signed-in user context).
"""

import asyncio
import os
from msgraph import GraphServiceClient
from msgraph.generated.models.chat_message import ChatMessage
from msgraph.generated.models.item_body import ItemBody
from msgraph.generated.models.body_type import BodyType
from msgraph.generated.models.chat import Chat
from msgraph.generated.models.chat_type import ChatType
from msgraph.generated.models.aad_user_conversation_member import AadUserConversationMember


async def list_my_teams(graph_client: GraphServiceClient) -> list:
    """List all teams the signed-in user is a member of."""
    teams = await graph_client.me.joined_teams.get()
    return teams.value or []


async def list_channels(graph_client: GraphServiceClient, team_id: str) -> list:
    """List all channels in a team."""
    channels = await graph_client.teams.by_team_id(team_id).channels.get()
    return channels.value or []


async def find_team_and_channel(
    graph_client: GraphServiceClient,
    team_name: str,
    channel_name: str,
) -> tuple[str, str]:
    """
    Find team and channel IDs by display name.

    Returns:
        (team_id, channel_id) tuple
    Raises:
        ValueError if not found
    """
    teams = await list_my_teams(graph_client)
    team = next(
        (t for t in teams if t.display_name.lower() == team_name.lower()),
        None,
    )
    if not team:
        available = [t.display_name for t in teams]
        raise ValueError(f"Team '{team_name}' not found. Available: {available}")

    channels = await list_channels(graph_client, team.id)
    channel = next(
        (c for c in channels if c.display_name.lower() == channel_name.lower()),
        None,
    )
    if not channel:
        available = [c.display_name for c in channels]
        raise ValueError(
            f"Channel '{channel_name}' not found in team '{team_name}'. Available: {available}"
        )

    return team.id, channel.id


async def send_channel_message(
    graph_client: GraphServiceClient,
    team_id: str,
    channel_id: str,
    message: str,
    html: bool = False,
) -> object:
    """
    Send a message to a Teams channel.

    Args:
        team_id: Team ID
        channel_id: Channel ID
        message: Message text (plain text or HTML)
        html: If True, renders message as HTML

    Returns:
        Sent ChatMessage object
    """
    chat_message = ChatMessage(
        body=ItemBody(
            content_type=BodyType.Html if html else BodyType.Text,
            content=message,
        )
    )

    sent = await graph_client.teams.by_team_id(team_id).channels.by_channel_id(
        channel_id
    ).messages.post(chat_message)

    print(f"Message sent to channel (ID: {sent.id})")
    return sent


async def send_channel_message_by_name(
    graph_client: GraphServiceClient,
    team_name: str,
    channel_name: str,
    message: str,
    html: bool = False,
) -> object:
    """
    Send a message to a Teams channel by team and channel display name.

    This is a convenience wrapper that looks up IDs for you.
    For repeated sends, use send_channel_message with IDs directly.
    """
    team_id, channel_id = await find_team_and_channel(
        graph_client, team_name, channel_name
    )
    return await send_channel_message(graph_client, team_id, channel_id, message, html)


async def reply_to_message(
    graph_client: GraphServiceClient,
    team_id: str,
    channel_id: str,
    message_id: str,
    reply: str,
    html: bool = False,
) -> object:
    """Reply to an existing channel message (creates a thread reply)."""
    chat_message = ChatMessage(
        body=ItemBody(
            content_type=BodyType.Html if html else BodyType.Text,
            content=reply,
        )
    )

    sent = await graph_client.teams.by_team_id(team_id).channels.by_channel_id(
        channel_id
    ).messages.by_chat_message_id(message_id).replies.post(chat_message)

    print(f"Reply sent (ID: {sent.id})")
    return sent


async def list_my_chats(graph_client: GraphServiceClient) -> list:
    """List all chats (DMs and group chats) for the signed-in user."""
    chats = await graph_client.me.chats.get()
    return chats.value or []


async def send_chat_message(
    graph_client: GraphServiceClient,
    chat_id: str,
    message: str,
    html: bool = False,
) -> object:
    """
    Send a message to an existing chat (DM or group chat).

    Args:
        chat_id: Chat ID (from list_my_chats)
        message: Message text
        html: Render as HTML
    """
    chat_message = ChatMessage(
        body=ItemBody(
            content_type=BodyType.Html if html else BodyType.Text,
            content=message,
        )
    )

    sent = await graph_client.me.chats.by_chat_id(chat_id).messages.post(chat_message)
    print(f"Chat message sent (ID: {sent.id})")
    return sent


async def create_and_send_direct_message(
    graph_client: GraphServiceClient,
    recipient_user_id: str,
    message: str,
    my_user_id: str = None,
) -> object:
    """
    Create a 1:1 chat with a user (if it doesn't exist) and send a message.

    Args:
        recipient_user_id: The recipient's Azure AD user ID or UPN
        message: Message to send
        my_user_id: The current user's ID (fetched from /me if not provided)

    Returns:
        Sent ChatMessage
    """
    if not my_user_id:
        me = await graph_client.me.get()
        my_user_id = me.id

    # Create or find existing 1:1 chat
    chat = Chat(
        chat_type=ChatType.OneOnOne,
        members=[
            AadUserConversationMember(
                odata_type="#microsoft.graph.aadUserConversationMember",
                roles=["owner"],
                additional_data={
                    "user@odata.bind": (
                        f"https://graph.microsoft.com/v1.0/users('{recipient_user_id}')"
                    )
                },
            ),
            AadUserConversationMember(
                odata_type="#microsoft.graph.aadUserConversationMember",
                roles=["owner"],
                additional_data={
                    "user@odata.bind": (
                        f"https://graph.microsoft.com/v1.0/users('{my_user_id}')"
                    )
                },
            ),
        ],
    )

    created_chat = await graph_client.chats.post(chat)
    return await send_chat_message(graph_client, created_chat.id, message)


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
        scopes = [
            "Team.ReadBasic.All",
            "Channel.ReadBasic.All",
            "ChannelMessage.Send",
            "Chat.ReadWrite",
        ]
        graph = GraphServiceClient(credential, scopes)

        # List my teams
        print("=== My Teams ===")
        teams = await list_my_teams(graph)
        for team in teams[:10]:
            print(f"  {team.display_name} (ID: {team.id})")

        if teams:
            # List channels in first team
            team_id = teams[0].id
            print(f"\n=== Channels in '{teams[0].display_name}' ===")
            channels = await list_channels(graph, team_id)
            for ch in channels:
                print(f"  #{ch.display_name} (ID: {ch.id})")

            if channels:
                # Send a test message to General channel
                general = next(
                    (c for c in channels if c.display_name.lower() == "general"),
                    channels[0],
                )
                print(f"\nSending to #{general.display_name}...")
                await send_channel_message(
                    graph,
                    team_id=team_id,
                    channel_id=general.id,
                    message="Hello from the Microsoft Graph API! 🤖",
                )

        # Send HTML message with formatting
        # await send_channel_message(
        #     graph,
        #     team_id="TEAM_ID",
        #     channel_id="CHANNEL_ID",
        #     message="<h2>Status Update</h2><p><b>Status:</b> ✅ Complete</p>",
        #     html=True,
        # )

    asyncio.run(main())
