"""
Delegated (on-behalf-of-user) authentication for Microsoft Graph.

Use this when your script acts on behalf of a specific user,
reading/writing their own mail, calendar, files, contacts, etc.

Supports:
  - Azure CLI Credential: No app registration — equivalent to `gcloud auth login` (RECOMMENDED for local use)
  - Device Code Flow: User opens browser on any device to authenticate
  - Interactive Browser Flow: Opens browser on the local machine

Requirements:
    pip install msgraph-sdk azure-identity msal python-dotenv

For Azure CLI flow:
    brew install azure-cli && az login
    (No app registration, tenant ID, or client ID needed)

Azure App Registration Requirements (device code / interactive only):
    - Delegated permissions configured
    - "Allow public client flows" enabled (for device code)
    - Redirect URI configured as http://localhost for interactive browser
"""

import os
import json
import asyncio
from pathlib import Path
from azure.identity import AzureCliCredential, DeviceCodeCredential, InteractiveBrowserCredential
from msgraph import GraphServiceClient


def get_graph_client_cli() -> GraphServiceClient:
    """
    Authenticate using the Azure CLI session (az login).

    No app registration, tenant ID, or client ID required.
    Equivalent to gcloud auth application-default login for Google APIs.

    Prerequisites:
        brew install azure-cli
        az login

    Returns:
        Authenticated GraphServiceClient
    """
    credential = AzureCliCredential()
    return GraphServiceClient(credential, ["https://graph.microsoft.com/.default"])


# Default scopes for common operations — adjust as needed
DEFAULT_SCOPES = [
    "User.Read",
    "Mail.ReadWrite",
    "Mail.Send",
    "Calendars.ReadWrite",
    "Files.ReadWrite.All",
    "Contacts.ReadWrite",
    "Chat.ReadWrite",
]


def get_graph_client_device_code(
    tenant_id: str = None,
    client_id: str = None,
    scopes: list[str] = None,
) -> GraphServiceClient:
    """
    Authenticate via device code flow.

    The user will be prompted to visit https://microsoft.com/devicelogin
    and enter a code shown in the terminal. Works even on headless servers.

    Requirements in Azure App Registration:
        - Authentication > Advanced settings > Allow public client flows = Yes

    Args:
        tenant_id: Azure tenant ID (or 'common' for multi-tenant)
        client_id: Application (client) ID from app registration
        scopes: List of delegated permission scopes

    Returns:
        Authenticated GraphServiceClient
    """
    tenant_id = tenant_id or os.environ.get("AZURE_TENANT_ID", "common")
    client_id = client_id or os.environ["AZURE_CLIENT_ID"]
    scopes = scopes or DEFAULT_SCOPES

    credential = DeviceCodeCredential(
        tenant_id=tenant_id,
        client_id=client_id,
    )

    return GraphServiceClient(credential, scopes)


def get_graph_client_interactive(
    tenant_id: str = None,
    client_id: str = None,
    scopes: list[str] = None,
    redirect_uri: str = "http://localhost:8080",
) -> GraphServiceClient:
    """
    Authenticate via interactive browser flow.

    Opens the system browser automatically. Best for desktop use.

    Requirements in Azure App Registration:
        - Authentication > Add platform > Mobile and desktop applications
        - Redirect URI: http://localhost (or specific port)
    """
    tenant_id = tenant_id or os.environ.get("AZURE_TENANT_ID", "common")
    client_id = client_id or os.environ["AZURE_CLIENT_ID"]
    scopes = scopes or DEFAULT_SCOPES

    credential = InteractiveBrowserCredential(
        tenant_id=tenant_id,
        client_id=client_id,
        redirect_uri=redirect_uri,
    )

    return GraphServiceClient(credential, scopes)


async def get_current_user(graph_client: GraphServiceClient) -> dict:
    """Get the signed-in user's profile."""
    me = await graph_client.me.get()
    return {
        "id": me.id,
        "display_name": me.display_name,
        "email": me.mail or me.user_principal_name,
    }


# --- Example Usage ---
if __name__ == "__main__":
    from dotenv import load_dotenv

    load_dotenv()

    async def main():
        print("Authenticating via Azure CLI (az login)...\n")

        graph = get_graph_client_cli()

        # First API call triggers the auth prompt
        me = await get_current_user(graph)
        print(f"\nSigned in as: {me['display_name']} ({me['email']})")

        # Read inbox
        messages = await graph.me.messages.get()
        print(f"\nInbox messages (first 10):")
        for msg in (messages.value or [])[:10]:
            sender = msg.sender.email_address.address if msg.sender else "unknown"
            print(f"  [{'' if msg.is_read else 'UNREAD':<6}] {msg.subject[:50]!r} from {sender}")

        # List calendar events
        events = await graph.me.events.get()
        print(f"\nUpcoming events:")
        for event in (events.value or [])[:5]:
            print(f"  - {event.subject} at {event.start.date_time if event.start else 'unknown'}")

    asyncio.run(main())
