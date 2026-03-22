"""
Gmail Authentication Helper
Supports: OAuth 2.0 user flow (desktop/CLI) and service account delegation.

For multi-service auth (Gmail + Sheets + Drive, etc.), use scripts/auth.py instead.
"""
import os
import json
from pathlib import Path

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google.oauth2 import service_account


# Common scope combinations
SCOPES_READONLY = ['https://www.googleapis.com/auth/gmail.readonly']
SCOPES_SEND_ONLY = ['https://www.googleapis.com/auth/gmail.send']
SCOPES_COMPOSE = ['https://www.googleapis.com/auth/gmail.compose']
SCOPES_MODIFY = ['https://www.googleapis.com/auth/gmail.modify']
SCOPES_FULL = ['https://mail.google.com/']
SCOPES_SETTINGS = [
    'https://www.googleapis.com/auth/gmail.modify',
    'https://www.googleapis.com/auth/gmail.settings.basic',
    'https://www.googleapis.com/auth/gmail.settings.sharing',
]


def get_service(
    scopes=None,
    credentials_file='credentials.json',
    token_file='token.json'
):
    """
    Get authenticated Gmail service via OAuth 2.0 user flow.

    First run opens browser for user consent. Subsequent runs use cached token.

    Args:
        scopes: List of OAuth scopes. Defaults to gmail.modify.
        credentials_file: Path to OAuth client credentials JSON from Google Cloud.
        token_file: Path to save/load cached tokens.

    Returns:
        Authenticated Gmail service resource.
    """
    if scopes is None:
        scopes = SCOPES_MODIFY

    creds = None

    if os.path.exists(token_file):
        creds = Credentials.from_authorized_user_file(token_file, scopes)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(credentials_file):
                raise FileNotFoundError(
                    f"credentials.json not found at '{credentials_file}'. "
                    "Download it from Google Cloud Console > APIs & Services > Credentials."
                )
            flow = InstalledAppFlow.from_client_secrets_file(credentials_file, scopes)
            creds = flow.run_local_server(port=0)

        Path(token_file).write_text(creds.to_json())

    return build('gmail', 'v1', credentials=creds)


def get_service_headless(
    scopes=None,
    credentials_file='credentials.json',
    token_file='token.json'
):
    """
    Get authenticated Gmail service in headless environments (no browser).

    Prints a URL for the user to visit manually, then waits for the auth code.
    Use this for SSH sessions or servers.
    """
    if scopes is None:
        scopes = SCOPES_MODIFY

    creds = None

    if os.path.exists(token_file):
        creds = Credentials.from_authorized_user_file(token_file, scopes)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(credentials_file, scopes)
            creds = flow.run_console()  # Prints URL, accepts pasted code

        Path(token_file).write_text(creds.to_json())

    return build('gmail', 'v1', credentials=creds)


def get_service_from_env(scopes=None, env_var='GMAIL_TOKEN_JSON'):
    """
    Get Gmail service from token JSON stored in environment variable.

    Useful for deployment environments (Docker, CI/CD, cloud functions).

    Args:
        env_var: Name of environment variable containing token JSON string.
    """
    if scopes is None:
        scopes = SCOPES_MODIFY

    token_json = os.environ.get(env_var)
    if not token_json:
        raise EnvironmentError(
            f"Environment variable '{env_var}' not set. "
            "Set it to the contents of your token.json file."
        )

    info = json.loads(token_json)
    creds = Credentials.from_authorized_user_info(info, scopes)

    if creds.expired and creds.refresh_token:
        creds.refresh(Request())

    return build('gmail', 'v1', credentials=creds)


def get_service_service_account(
    service_account_file: str,
    impersonate_email: str,
    scopes=None
):
    """
    Get Gmail service using service account with domain-wide delegation.

    Requires:
        - Service account with domain-wide delegation enabled in Google Workspace
        - Admin has granted the service account's client ID the required scopes

    Args:
        service_account_file: Path to service account JSON key file.
        impersonate_email: Email of the Workspace user to impersonate.
        scopes: OAuth scopes. Defaults to gmail.modify.

    Returns:
        Gmail service acting as impersonate_email.
    """
    if scopes is None:
        scopes = SCOPES_MODIFY

    credentials = service_account.Credentials.from_service_account_file(
        service_account_file,
        scopes=scopes
    )
    delegated = credentials.with_subject(impersonate_email)

    return build('gmail', 'v1', credentials=delegated)


def get_service_from_dict(token_dict: dict, scopes=None):
    """
    Get Gmail service from a credentials dictionary (e.g., from a database).

    Args:
        token_dict: Dictionary matching the structure of token.json.
        scopes: OAuth scopes.
    """
    if scopes is None:
        scopes = SCOPES_MODIFY

    creds = Credentials.from_authorized_user_info(token_dict, scopes)

    if creds.expired and creds.refresh_token:
        creds.refresh(Request())

    return build('gmail', 'v1', credentials=creds)


if __name__ == '__main__':
    # Quick test: print authenticated user's email
    service = get_service()
    profile = service.users().getProfile(userId='me').execute()
    print(f"Authenticated as: {profile['emailAddress']}")
    print(f"Total messages: {profile['messagesTotal']}")
    print(f"History ID: {profile['historyId']}")
