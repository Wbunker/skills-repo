"""
Google Workspace API Authentication Helper

Supports: OAuth 2.0 user flow (desktop/CLI/web) and service account delegation.
Works with Gmail, Sheets, Docs, Slides, Drive, Calendar, and other Workspace APIs.

Usage:
    from auth import get_service, get_all_services

    # Single service
    sheets = get_service('sheets', 'v4', scopes=['https://www.googleapis.com/auth/spreadsheets'])

    # Multiple services from shared credentials (one auth prompt)
    services = get_all_services('alice@example.com')  # or get_all_services() for OAuth
"""
import json
import os
from pathlib import Path
from typing import Optional

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google.oauth2 import service_account


# ---------------------------------------------------------------------------
# Scope presets
# ---------------------------------------------------------------------------

SCOPES_GMAIL_READONLY = ['https://www.googleapis.com/auth/gmail.readonly']
SCOPES_GMAIL_SEND     = ['https://www.googleapis.com/auth/gmail.send']
SCOPES_GMAIL_MODIFY   = ['https://www.googleapis.com/auth/gmail.modify']
SCOPES_GMAIL_FULL     = ['https://mail.google.com/']

SCOPES_SHEETS_READONLY = ['https://www.googleapis.com/auth/spreadsheets.readonly']
SCOPES_SHEETS          = ['https://www.googleapis.com/auth/spreadsheets']

SCOPES_DOCS_READONLY = ['https://www.googleapis.com/auth/documents.readonly']
SCOPES_DOCS          = ['https://www.googleapis.com/auth/documents']

SCOPES_SLIDES_READONLY = ['https://www.googleapis.com/auth/presentations.readonly']
SCOPES_SLIDES          = ['https://www.googleapis.com/auth/presentations']

SCOPES_DRIVE_READONLY = ['https://www.googleapis.com/auth/drive.readonly']
SCOPES_DRIVE_FILE     = ['https://www.googleapis.com/auth/drive.file']
SCOPES_DRIVE          = ['https://www.googleapis.com/auth/drive']

# All Workspace services — use when building multiple services at once
SCOPES_ALL = [
    'https://www.googleapis.com/auth/gmail.modify',
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/documents',
    'https://www.googleapis.com/auth/presentations',
    'https://www.googleapis.com/auth/drive',
]

# Service name → (name, version) for build()
SERVICE_VERSIONS = {
    'gmail':    ('gmail',    'v1'),
    'sheets':   ('sheets',   'v4'),
    'docs':     ('docs',     'v1'),
    'slides':   ('slides',   'v1'),
    'drive':    ('drive',    'v3'),
    'calendar': ('calendar', 'v3'),
    'admin':    ('admin',    'directory_v1'),
}


# ---------------------------------------------------------------------------
# OAuth 2.0 user flow
# ---------------------------------------------------------------------------

def get_credentials(
    scopes: list[str],
    credentials_file: str = 'credentials.json',
    token_file: str = 'token.json',
) -> Credentials:
    """
    Get OAuth 2.0 credentials, opening browser on first run.
    Caches tokens in token_file for subsequent runs.

    Args:
        scopes: OAuth scopes to request.
        credentials_file: Path to OAuth client credentials JSON from Google Cloud.
        token_file: Path to save/load cached tokens.

    Returns:
        Valid Credentials object.
    """
    creds = None

    if os.path.exists(token_file):
        creds = Credentials.from_authorized_user_file(token_file, scopes)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(credentials_file):
                raise FileNotFoundError(
                    f"'{credentials_file}' not found. "
                    "Download from Google Cloud Console > APIs & Services > Credentials."
                )
            flow = InstalledAppFlow.from_client_secrets_file(credentials_file, scopes)
            creds = flow.run_local_server(
                port=0,
                access_type='offline',
                prompt='consent',
            )
        Path(token_file).write_text(creds.to_json())

    return creds


def get_credentials_headless(
    scopes: list[str],
    credentials_file: str = 'credentials.json',
    token_file: str = 'token.json',
) -> Credentials:
    """
    Get credentials in headless environments (SSH, servers).
    Prints a URL for the user to visit manually.
    """
    creds = None

    if os.path.exists(token_file):
        creds = Credentials.from_authorized_user_file(token_file, scopes)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(credentials_file, scopes)
            creds = flow.run_console()
        Path(token_file).write_text(creds.to_json())

    return creds


def get_credentials_from_env(
    scopes: list[str],
    env_var: str = 'GOOGLE_TOKEN_JSON',
) -> Credentials:
    """
    Load credentials from an environment variable (for deployment).
    Set env_var to the contents of your token.json file.
    """
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
    return creds


def get_service(
    service_name: str,
    version: str,
    scopes: list[str],
    credentials_file: str = 'credentials.json',
    token_file: str = 'token.json',
):
    """
    Get an authenticated API service resource via OAuth user flow.

    Args:
        service_name: API name ('gmail', 'sheets', 'docs', 'slides', 'drive', etc.)
        version: API version ('v1', 'v4', 'v3', etc.)
        scopes: OAuth scopes required.
        credentials_file: Path to OAuth client credentials JSON.
        token_file: Path to save/load cached tokens.

    Returns:
        Authenticated service resource.

    Example:
        sheets = get_service('sheets', 'v4', SCOPES_SHEETS)
        gmail  = get_service('gmail', 'v1', SCOPES_GMAIL_MODIFY)
    """
    creds = get_credentials(scopes, credentials_file, token_file)
    return build(service_name, version, credentials=creds)


def get_all_services(
    credentials_file: str = 'credentials.json',
    token_file: str = 'token.json',
    scopes: list[str] = None,
) -> dict:
    """
    Get all major Workspace services with a single OAuth prompt.

    Returns:
        Dict with keys: 'gmail', 'sheets', 'docs', 'slides', 'drive'
    """
    if scopes is None:
        scopes = SCOPES_ALL
    creds = get_credentials(scopes, credentials_file, token_file)
    return {
        'gmail':  build('gmail',  'v1', credentials=creds),
        'sheets': build('sheets', 'v4', credentials=creds),
        'docs':   build('docs',   'v1', credentials=creds),
        'slides': build('slides', 'v1', credentials=creds),
        'drive':  build('drive',  'v3', credentials=creds),
    }


# ---------------------------------------------------------------------------
# Service account delegation (Google Workspace domains only)
# ---------------------------------------------------------------------------

def get_delegated_service(
    service_name: str,
    version: str,
    scopes: list[str],
    impersonate_email: str,
    service_account_file: str = 'service-account.json',
):
    """
    Get an API service using service account domain-wide delegation.

    Requires:
        - Service account with domain-wide delegation enabled
        - Google Workspace Admin has granted the service account the required scopes

    Args:
        service_name: API name ('gmail', 'sheets', etc.)
        version: API version.
        scopes: OAuth scopes (must be granted in Admin console).
        impersonate_email: Email of the Workspace user to impersonate.
        service_account_file: Path to service account JSON key.

    Returns:
        Authenticated service acting as impersonate_email.
    """
    credentials = service_account.Credentials.from_service_account_file(
        service_account_file,
        scopes=scopes
    )
    delegated = credentials.with_subject(impersonate_email)
    return build(service_name, version, credentials=delegated)


def get_all_delegated_services(
    impersonate_email: str,
    service_account_file: str = 'service-account.json',
    scopes: list[str] = None,
) -> dict:
    """
    Get all major Workspace services via service account delegation.

    Args:
        impersonate_email: Email of Workspace user to impersonate.

    Returns:
        Dict with keys: 'gmail', 'sheets', 'docs', 'slides', 'drive'
    """
    if scopes is None:
        scopes = SCOPES_ALL

    credentials = service_account.Credentials.from_service_account_file(
        service_account_file,
        scopes=scopes
    )
    delegated = credentials.with_subject(impersonate_email)

    return {
        'gmail':  build('gmail',  'v1', credentials=delegated),
        'sheets': build('sheets', 'v4', credentials=delegated),
        'docs':   build('docs',   'v1', credentials=delegated),
        'slides': build('slides', 'v1', credentials=delegated),
        'drive':  build('drive',  'v3', credentials=delegated),
    }


def get_delegated_service_from_env(
    service_name: str,
    version: str,
    scopes: list[str],
    impersonate_email: str,
    env_var: str = 'SERVICE_ACCOUNT_JSON',
):
    """
    Get delegated service from service account JSON stored in an environment variable.
    """
    sa_json = os.environ.get(env_var)
    if not sa_json:
        raise EnvironmentError(f"Environment variable '{env_var}' not set.")
    info = json.loads(sa_json)
    credentials = service_account.Credentials.from_service_account_info(info, scopes=scopes)
    delegated = credentials.with_subject(impersonate_email)
    return build(service_name, version, credentials=delegated)


# ---------------------------------------------------------------------------
# Quick test
# ---------------------------------------------------------------------------

if __name__ == '__main__':
    import sys

    mode = sys.argv[1] if len(sys.argv) > 1 else 'oauth'

    if mode == 'oauth':
        services = get_all_services()
        profile = services['gmail'].users().getProfile(userId='me').execute()
        print(f"Gmail: {profile['emailAddress']}")
        print("Sheets, Docs, Slides, Drive services also initialized.")

    elif mode == 'delegate':
        if len(sys.argv) < 3:
            print("Usage: python auth.py delegate user@yourcompany.com")
            sys.exit(1)
        email = sys.argv[2]
        services = get_all_delegated_services(email)
        profile = services['gmail'].users().getProfile(userId='me').execute()
        print(f"Delegated as: {profile['emailAddress']}")
