"""
Dropbox OAuth2 Authentication Helper

Handles: browser-based OAuth2 flow, token persistence, auto-refresh via refresh token.

Usage:
    # First-time setup (opens browser)
    python auth.py

    # Get a client in your own scripts
    from auth import get_client
    dbx = get_client()
"""
import json
import os
import sys
from pathlib import Path

import dropbox
from dropbox import DropboxOAuth2FlowNoRedirect

# ---------------------------------------------------------------------------
# Configuration — override with env vars or edit directly
# ---------------------------------------------------------------------------

APP_KEY    = os.environ.get('DROPBOX_APP_KEY',    '')
APP_SECRET = os.environ.get('DROPBOX_APP_SECRET', '')

# Where to save tokens (relative to this script, or override with env var)
TOKEN_FILE = os.environ.get('DROPBOX_TOKEN_FILE',
                             str(Path(__file__).parent / '.dropbox_tokens.json'))

# Scopes your app needs — must match what's enabled in the App Console
DEFAULT_SCOPES = [
    'account_info.read',
    'files.metadata.read',
    'files.metadata.write',
    'files.content.read',
    'files.content.write',
    'sharing.read',
    'sharing.write',
]


# ---------------------------------------------------------------------------
# Token persistence
# ---------------------------------------------------------------------------

def _save_tokens(access_token: str, refresh_token: str = None, account_id: str = None):
    data = {'access_token': access_token}
    if refresh_token:
        data['refresh_token'] = refresh_token
    if account_id:
        data['account_id'] = account_id
    with open(TOKEN_FILE, 'w') as f:
        json.dump(data, f, indent=2)
    # Restrict permissions
    os.chmod(TOKEN_FILE, 0o600)
    print(f"Tokens saved to {TOKEN_FILE}")


def _load_tokens() -> dict:
    if not os.path.exists(TOKEN_FILE):
        return {}
    with open(TOKEN_FILE) as f:
        return json.load(f)


# ---------------------------------------------------------------------------
# Auth flow
# ---------------------------------------------------------------------------

def run_auth_flow(app_key: str = APP_KEY, app_secret: str = APP_SECRET,
                   scopes: list = None) -> dict:
    """
    Run the OAuth2 authorization code flow (no-redirect / CLI version).
    Opens a browser URL for the user to authorize, then saves tokens.

    Returns:
        dict with access_token, refresh_token, account_id
    """
    if not app_key or not app_secret:
        print("ERROR: Set DROPBOX_APP_KEY and DROPBOX_APP_SECRET environment variables,")
        print("       or edit APP_KEY / APP_SECRET at the top of this file.")
        sys.exit(1)

    auth_flow = DropboxOAuth2FlowNoRedirect(
        consumer_key=app_key,
        consumer_secret=app_secret,
        token_access_type='offline',    # Request a refresh token
        scope=scopes or DEFAULT_SCOPES,
    )

    authorize_url = auth_flow.start()

    print("\n=== Dropbox Authorization ===")
    print(f"1. Visit this URL:\n\n   {authorize_url}\n")
    print("2. Click 'Allow' (you may need to log in first)")
    print("3. Copy the authorization code shown")
    auth_code = input("\nPaste the authorization code here: ").strip()

    if not auth_code:
        print("No code entered. Aborting.")
        sys.exit(1)

    try:
        oauth_result = auth_flow.finish(auth_code)
    except Exception as e:
        print(f"Authorization failed: {e}")
        sys.exit(1)

    _save_tokens(
        access_token=oauth_result.access_token,
        refresh_token=oauth_result.refresh_token,
        account_id=oauth_result.account_id,
    )

    return {
        'access_token': oauth_result.access_token,
        'refresh_token': oauth_result.refresh_token,
        'account_id': oauth_result.account_id,
    }


# ---------------------------------------------------------------------------
# Client factory
# ---------------------------------------------------------------------------

def get_client(app_key: str = APP_KEY, app_secret: str = APP_SECRET) -> dropbox.Dropbox:
    """
    Get an authenticated Dropbox client.

    - If refresh_token is stored: builds client with auto-refresh (preferred).
    - If only access_token is stored: uses it directly (may expire).
    - If no tokens: runs the OAuth flow to get them.

    Args:
        app_key: Dropbox app key (for refresh token flow).
        app_secret: Dropbox app secret (for refresh token flow).

    Returns:
        Authenticated dropbox.Dropbox client.

    Example:
        from auth import get_client
        dbx = get_client()
        print(dbx.users_get_current_account().email)
    """
    tokens = _load_tokens()

    if not tokens:
        print("No tokens found. Starting OAuth flow...")
        tokens = run_auth_flow(app_key, app_secret)

    if tokens.get('refresh_token') and app_key and app_secret:
        # Preferred: SDK handles token refresh automatically
        return dropbox.Dropbox(
            oauth2_refresh_token=tokens['refresh_token'],
            app_key=app_key,
            app_secret=app_secret,
        )
    elif tokens.get('access_token'):
        # Fallback: direct access token (may expire after ~4 hours)
        return dropbox.Dropbox(oauth2_access_token=tokens['access_token'])
    else:
        print("Token file is invalid. Re-running OAuth flow...")
        tokens = run_auth_flow(app_key, app_secret)
        return dropbox.Dropbox(
            oauth2_refresh_token=tokens['refresh_token'],
            app_key=app_key,
            app_secret=app_secret,
        )


def logout():
    """Revoke the stored token and delete the token file."""
    tokens = _load_tokens()
    if tokens.get('access_token'):
        try:
            dbx = dropbox.Dropbox(tokens['access_token'])
            dbx.auth_token_revoke()
            print("Token revoked.")
        except Exception as e:
            print(f"Warning: could not revoke token: {e}")

    if os.path.exists(TOKEN_FILE):
        os.remove(TOKEN_FILE)
        print(f"Deleted {TOKEN_FILE}")


# ---------------------------------------------------------------------------
# Quick test
# ---------------------------------------------------------------------------

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'logout':
        logout()
        sys.exit(0)

    dbx = get_client()
    account = dbx.users_get_current_account()
    usage = dbx.users_get_space_usage()

    print(f"\n✓ Authenticated as: {account.email} ({account.display_name})")
    print(f"  Account ID: {account.account_id}")
    print(f"  Account type: {account.account_type._tag}")

    used_gb = usage.used / (1024**3)
    if usage.allocation.is_individual():
        alloc = usage.allocation.get_individual()
        total_gb = alloc.allocated / (1024**3)
        print(f"  Storage: {used_gb:.2f} GB / {total_gb:.2f} GB used")
    else:
        print(f"  Storage used: {used_gb:.2f} GB (team allocation)")
