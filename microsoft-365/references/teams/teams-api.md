# Microsoft Teams API (Microsoft Graph)

Access Teams channels, chats, messages, and online meetings via Microsoft Graph.

## Permissions

### Channel Messages

| Scenario | Delegated | Application |
|----------|-----------|-------------|
| Read channel messages | `ChannelMessage.Read.All` | `ChannelMessage.Read.All` |
| Send channel messages | `ChannelMessage.Send` | — (no app-only send to channels) |
| Read all teams | `Team.ReadBasic.All` | `Team.ReadBasic.All` |
| Create/manage teams | `Team.Create` | `Team.Create` |
| Manage channels | `Channel.ReadBasic.All` | `Channel.ReadBasic.All` |
| Create channels | `ChannelMember.ReadWrite.All` | `ChannelMember.ReadWrite.All` |

### Chat Messages

| Scenario | Delegated | Application |
|----------|-----------|-------------|
| Read user's chats | `Chat.Read` | `Chat.Read.All` |
| Read + write chats | `Chat.ReadWrite` | `Chat.ReadWrite.All` |
| Send chat messages | `ChatMessage.Send` | — |
| Read all chat messages | — | `Chat.Read.All` |

### Online Meetings

| Scenario | Delegated | Application |
|----------|-----------|-------------|
| Create meetings | `OnlineMeetings.ReadWrite` | `OnlineMeetings.ReadWrite.All` |
| Read meetings | `OnlineMeetings.Read` | `OnlineMeetings.Read.All` |

**Important**: Application permissions cannot send messages to channels or chats directly.
Use delegated permissions (with a signed-in user) for sending messages.

## List Joined Teams

```python
from msgraph import GraphServiceClient

async def list_my_teams(graph_client):
    teams = await graph_client.me.joined_teams.get()
    return teams.value
    # team.id, team.display_name, team.description, team.web_url
```

## List Channels in a Team

```python
async def list_channels(graph_client, team_id):
    channels = await graph_client.teams.by_team_id(team_id).channels.get()
    return channels.value
    # channel.id, channel.display_name, channel.description
    # channel.membership_type: 'standard', 'private', 'shared'
```

## Get a Specific Channel

```python
async def get_channel(graph_client, team_id, channel_id):
    channel = await graph_client.teams.by_team_id(team_id).channels.by_channel_id(
        channel_id
    ).get()
    return channel
```

## Send a Message to a Channel

```python
from msgraph.generated.models.chat_message import ChatMessage
from msgraph.generated.models.item_body import ItemBody
from msgraph.generated.models.body_type import BodyType

async def send_channel_message(graph_client, team_id, channel_id, message_text, use_html=False):
    message = ChatMessage(
        body=ItemBody(
            content_type=BodyType.Html if use_html else BodyType.Text,
            content=message_text,
        )
    )
    sent = await graph_client.teams.by_team_id(team_id).channels.by_channel_id(
        channel_id
    ).messages.post(message)
    return sent
```

### Send with @Mentions

```python
from msgraph.generated.models.chat_message_mention import ChatMessageMention
from msgraph.generated.models.chat_message_mentioned_identity_set import ChatMessageMentionedIdentitySet
from msgraph.generated.models.identity import Identity

message = ChatMessage(
    body=ItemBody(
        content_type=BodyType.Html,
        content='<at id="0">Alice</at> please review this.',
    ),
    mentions=[
        ChatMessageMention(
            id=0,  # Must match the number in <at id="N">
            mention_text="Alice",
            mentioned=ChatMessageMentionedIdentitySet(
                user=Identity(
                    id="USER_ID_OF_ALICE",
                    display_name="Alice",
                    additional_data={
                        "@odata.type": "#microsoft.graph.teamworkUserIdentity"
                    },
                )
            ),
        )
    ],
)
```

## Reply to a Channel Message

```python
from msgraph.generated.models.chat_message import ChatMessage
from msgraph.generated.models.item_body import ItemBody

async def reply_to_message(graph_client, team_id, channel_id, message_id, reply_text):
    reply = ChatMessage(
        body=ItemBody(content_type=BodyType.Text, content=reply_text)
    )
    sent = await graph_client.teams.by_team_id(team_id).channels.by_channel_id(
        channel_id
    ).messages.by_chat_message_id(message_id).replies.post(reply)
    return sent
```

## List Channel Messages

```python
from msgraph.generated.teams.item.channels.item.messages.messages_request_builder import (
    MessagesRequestBuilder,
)
from kiota_abstractions.base_request_configuration import RequestConfiguration

async def list_channel_messages(graph_client, team_id, channel_id, top=20):
    query_params = MessagesRequestBuilder.MessagesRequestBuilderGetQueryParameters(
        top=top,
    )
    config = RequestConfiguration(query_parameters=query_params)
    messages = await graph_client.teams.by_team_id(team_id).channels.by_channel_id(
        channel_id
    ).messages.get(request_configuration=config)
    return messages.value
```

**Throttling note**: Teams channel message polling is limited to once per day per resource.
Use change notifications (webhooks) for near-real-time updates.

## Create a New Channel

```python
from msgraph.generated.models.channel import Channel
from msgraph.generated.models.channel_membership_type import ChannelMembershipType

async def create_channel(graph_client, team_id, display_name, description="", is_private=False):
    channel = Channel(
        display_name=display_name,
        description=description,
        membership_type=(
            ChannelMembershipType.Private if is_private else ChannelMembershipType.Standard
        ),
    )
    created = await graph_client.teams.by_team_id(team_id).channels.post(channel)
    return created
```

## Chats (Direct Messages and Group Chats)

### List My Chats

```python
async def list_chats(graph_client):
    chats = await graph_client.me.chats.get()
    return chats.value
    # chat.id, chat.chat_type ('oneOnOne', 'group', 'meeting')
    # chat.topic (for group chats)
```

### Get Messages in a Chat

```python
async def get_chat_messages(graph_client, chat_id, top=20):
    messages = await graph_client.me.chats.by_chat_id(chat_id).messages.get()
    return messages.value
```

### Send a Message in a Chat

```python
async def send_chat_message(graph_client, chat_id, message_text):
    message = ChatMessage(
        body=ItemBody(content_type=BodyType.Text, content=message_text)
    )
    sent = await graph_client.me.chats.by_chat_id(chat_id).messages.post(message)
    return sent
```

### Create a 1:1 Chat

```python
from msgraph.generated.models.chat import Chat
from msgraph.generated.models.chat_type import ChatType
from msgraph.generated.models.aad_user_conversation_member import AadUserConversationMember

async def create_one_on_one_chat(graph_client, other_user_id):
    chat = Chat(
        chat_type=ChatType.OneOnOne,
        members=[
            AadUserConversationMember(
                odata_type="#microsoft.graph.aadUserConversationMember",
                roles=["owner"],
                additional_data={
                    "user@odata.bind": f"https://graph.microsoft.com/v1.0/users('{other_user_id}')"
                },
            ),
            AadUserConversationMember(
                odata_type="#microsoft.graph.aadUserConversationMember",
                roles=["owner"],
                additional_data={
                    "user@odata.bind": "https://graph.microsoft.com/v1.0/users('me')"
                },
            ),
        ],
    )
    created = await graph_client.chats.post(chat)
    return created
```

## Online Meetings

### Create an Online Meeting

```python
from msgraph.generated.models.online_meeting import OnlineMeeting
from msgraph.generated.models.date_time_time_zone import DateTimeTimeZone
from msgraph.generated.models.meeting_participants import MeetingParticipants
from msgraph.generated.models.meeting_participant_info import MeetingParticipantInfo
from msgraph.generated.models.identity_set import IdentitySet
from msgraph.generated.models.identity import Identity

async def create_teams_meeting(graph_client, subject, start_dt, end_dt, attendee_emails=None):
    """
    start_dt, end_dt: datetime objects or ISO 8601 strings
    """
    meeting = OnlineMeeting(
        subject=subject,
        start_date_time=start_dt,  # datetime object or string
        end_date_time=end_dt,
    )
    created = await graph_client.me.online_meetings.post(meeting)
    return created
    # created.join_url       — URL to join the meeting
    # created.join_web_url   — Browser join URL
    # created.id             — Meeting ID
    # created.join_information.content  — HTML with join link
```

### Get Meeting Details

```python
meeting = await graph_client.me.online_meetings.by_online_meeting_id(meeting_id).get()
print(meeting.join_url)
print(meeting.join_information.content)  # HTML with call details
```

### List Online Meetings

```python
meetings = await graph_client.me.online_meetings.get()
```

## Teams Membership

### List Team Members

```python
async def list_team_members(graph_client, team_id):
    members = await graph_client.teams.by_team_id(team_id).members.get()
    return members.value
    # member.id, member.display_name, member.email, member.roles

```

### Add a Member to a Team

```python
from msgraph.generated.models.aad_user_conversation_member import AadUserConversationMember

async def add_team_member(graph_client, team_id, user_id, role="member"):
    """role: 'owner' or 'member'"""
    member = AadUserConversationMember(
        odata_type="#microsoft.graph.aadUserConversationMember",
        roles=["owner"] if role == "owner" else [],
        additional_data={
            "user@odata.bind": f"https://graph.microsoft.com/v1.0/users('{user_id}')"
        },
    )
    await graph_client.teams.by_team_id(team_id).members.post(member)
```

## Create a Team

```python
from msgraph.generated.models.team import Team
from msgraph.generated.models.team_fun_settings import TeamFunSettings
from msgraph.generated.models.team_member_settings import TeamMemberSettings

async def create_team(graph_client, display_name, description):
    team = Team(
        display_name=display_name,
        description=description,
        members=[
            AadUserConversationMember(
                odata_type="#microsoft.graph.aadUserConversationMember",
                roles=["owner"],
                additional_data={
                    "user@odata.bind": "https://graph.microsoft.com/v1.0/users('OWNER_USER_ID')"
                },
            )
        ],
        additional_data={
            "template@odata.bind": "https://graph.microsoft.com/v1.0/teamsTemplates('standard')"
        },
    )
    # Team creation is async — returns a 202 Accepted with operation URL
    created = await graph_client.teams.post(team)
    return created
```

## Throttling Limits (Teams-Specific)

| Resource | Limit |
|----------|-------|
| Calls API | 50,000 req/15s per app per tenant |
| Presence | 10,000 req/30s per app per tenant |
| Polling messages | Once per day per resource |
| Call records | 1,500 req/20s per app per tenant |

**Best practice**: Use webhooks (change notifications) instead of polling for new messages.

## Rich Text / Adaptive Cards

Teams messages support HTML content and Adaptive Cards:

```python
# HTML message
message = ChatMessage(
    body=ItemBody(
        content_type=BodyType.Html,
        content="<h2>Status Update</h2><ul><li>Item 1</li><li>Item 2</li></ul>",
    )
)

# Adaptive Card (send via Teams Bot Framework or Power Automate for full support)
# Graph API channel messages support basic HTML only
```
