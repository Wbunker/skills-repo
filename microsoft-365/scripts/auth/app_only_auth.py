"""
App-only (client credentials) authentication for Microsoft Graph.

Use this for background automation, scripts, and daemon applications
that run without a signed-in user.

Requirements:
    pip install msgraph-sdk azure-identity python-dotenv

Azure App Registration Requirements:
    - Application (not delegated) permissions granted
    - Admin consent granted
    - Client secret or certificate configured
"""

import os
from azure.identity import ClientSecretCredential, CertificateCredential
from msgraph import GraphServiceClient


def get_graph_client_with_secret(
    tenant_id: str = None,
    client_id: str = None,
    client_secret: str = None,
) -> GraphServiceClient:
    """
    Create a Graph client using client secret credentials.

    Reads from environment variables if parameters not provided:
        AZURE_TENANT_ID, AZURE_CLIENT_ID, AZURE_CLIENT_SECRET

    Returns:
        GraphServiceClient ready to use
    """
    tenant_id = tenant_id or os.environ["AZURE_TENANT_ID"]
    client_id = client_id or os.environ["AZURE_CLIENT_ID"]
    client_secret = client_secret or os.environ["AZURE_CLIENT_SECRET"]

    credential = ClientSecretCredential(
        tenant_id=tenant_id,
        client_id=client_id,
        client_secret=client_secret,
    )

    # For app-only, scope must always be .default
    scopes = ["https://graph.microsoft.com/.default"]
    return GraphServiceClient(credential, scopes)


def get_graph_client_with_certificate(
    tenant_id: str = None,
    client_id: str = None,
    certificate_path: str = None,
) -> GraphServiceClient:
    """
    Create a Graph client using a certificate (more secure than client secret).

    Reads from environment variables if parameters not provided:
        AZURE_TENANT_ID, AZURE_CLIENT_ID, AZURE_CERTIFICATE_PATH

    The certificate_path should point to a PEM file containing both
    the certificate and private key.
    """
    tenant_id = tenant_id or os.environ["AZURE_TENANT_ID"]
    client_id = client_id or os.environ["AZURE_CLIENT_ID"]
    certificate_path = certificate_path or os.environ["AZURE_CERTIFICATE_PATH"]

    credential = CertificateCredential(
        tenant_id=tenant_id,
        client_id=client_id,
        certificate_path=certificate_path,
    )

    scopes = ["https://graph.microsoft.com/.default"]
    return GraphServiceClient(credential, scopes)


async def verify_auth(graph_client: GraphServiceClient) -> dict:
    """
    Verify authentication by calling /organization.
    Returns organization info if successful.
    """
    org = await graph_client.organization.get()
    if org and org.value:
        return {
            "tenant_id": org.value[0].id,
            "display_name": org.value[0].display_name,
        }
    return {}


# --- Example Usage ---
if __name__ == "__main__":
    import asyncio
    from dotenv import load_dotenv

    load_dotenv()

    async def main():
        # Create client (reads from .env)
        graph = get_graph_client_with_secret()

        # Verify it works
        org_info = await verify_auth(graph)
        print(f"Authenticated to tenant: {org_info.get('display_name')}")

        # Example: List all users (requires User.Read.All application permission)
        users = await graph.users.get()
        print(f"Found {len(users.value)} users")
        for user in users.value[:5]:
            print(f"  - {user.display_name} ({user.mail})")

    asyncio.run(main())
