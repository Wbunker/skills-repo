# Dropbox Error Handling

## Table of Contents
1. [SDK Exception Types](#sdk-exception-types)
2. [HTTP Status Codes](#http-status-codes)
3. [Common API Errors](#common-api-errors)
4. [Rate Limits](#rate-limits)
5. [Retry with Exponential Backoff](#retry-with-exponential-backoff)
6. [Handling Specific Errors](#handling-specific-errors)

---

## SDK Exception Types

```python
import dropbox
from dropbox.exceptions import ApiError, AuthError, BadInputError, HttpError

try:
    dbx.files_get_metadata('/nonexistent/path')
except dropbox.exceptions.ApiError as e:
    # API returned a structured error
    print(e.error)          # Typed error object (e.g. GetMetadataError)
    print(e.user_message)   # Human-readable message if available
    print(e.request_id)     # For Dropbox support

except dropbox.exceptions.AuthError as e:
    # Authentication/authorization failure
    print(f"Auth error: {e.error}")

except dropbox.exceptions.BadInputError as e:
    # Malformed request (bad path, invalid arguments)
    print(f"Bad input: {e.message}")

except dropbox.exceptions.HttpError as e:
    # HTTP-level error (5xx, network issues)
    print(f"HTTP {e.status_code}: {e.body}")
```

### Exception hierarchy

```
Exception
└── dropbox.exceptions.DropboxException
    ├── dropbox.exceptions.ApiError         # Structured API errors (.error attribute)
    ├── dropbox.exceptions.AuthError        # 401 auth failures
    ├── dropbox.exceptions.BadInputError    # 400 malformed requests
    └── dropbox.exceptions.HttpError        # Raw HTTP errors (5xx, network)
```

---

## HTTP Status Codes

| Code | Meaning | Action |
|------|---------|--------|
| 200 | Success | — |
| 400 | Bad request / bad parameter | Fix the request |
| 401 | Invalid/expired access token | Refresh token, re-authenticate |
| 403 | No permission for this operation | Check scopes, app access type |
| 404 | Path not found | Verify the path exists |
| 409 | API-level error | Check `e.error` for specifics |
| 429 | Rate limited | Backoff, retry after `Retry-After` seconds |
| 500 | Server error | Retry with backoff |
| 503 | Service unavailable | Retry with backoff |

---

## Common API Errors

### Files errors

```python
from dropbox.files import (
    GetMetadataError, UploadError, DownloadError,
    DeleteError, CopyError, MoveError, ListFolderError,
    SearchError
)

# Check error type using .is_*() and .get_*() pattern
try:
    dbx.files_get_metadata('/path')
except ApiError as e:
    err = e.error
    if err.is_path():
        lookup = err.get_path()  # LookupError
        if lookup.is_not_found():
            print("File not found")
        elif lookup.is_not_file():
            print("Path is a folder, not a file")
        elif lookup.is_not_folder():
            print("Path is a file, not a folder")
        elif lookup.is_restricted_content():
            print("Content is restricted")

# Upload errors
try:
    dbx.files_upload(data, '/path/file.txt')
except ApiError as e:
    err = e.error
    if err.is_path():
        upload_err = err.get_path()
        if upload_err.is_conflict():
            print("File already exists (use WriteMode.overwrite)")
        elif upload_err.is_no_write_permission():
            print("No write permission to this path")
        elif upload_err.is_insufficient_space():
            print("Insufficient Dropbox space")
        elif upload_err.is_disallowed_name():
            print("Invalid filename")

# Download errors
try:
    dbx.files_download('/path/file.txt')
except ApiError as e:
    err = e.error
    if err.is_path():
        if err.get_path().is_not_found():
            print("File not found")
```

### Sharing errors

```python
from dropbox.sharing import CreateSharedLinkWithSettingsError

try:
    dbx.sharing_create_shared_link_with_settings('/path')
except ApiError as e:
    err = e.error
    if err.is_shared_link_already_exists():
        # Link already exists — retrieve it
        result = dbx.sharing_list_shared_links(path='/path', direct_only=True)
        url = result.links[0].url
    elif err.is_path():
        print("Path error — check the path exists")
    elif err.is_settings_error():
        settings_err = err.get_settings_error()
        if settings_err.is_invalid_settings():
            print("Invalid link settings")
        elif settings_err.is_not_authorized():
            print("Not authorized to use these settings (e.g., team-only visibility)")
```

### Auth errors

```python
from dropbox.auth import AuthError as DropboxAuthError

try:
    dbx.users_get_current_account()
except dropbox.exceptions.AuthError as e:
    err = e.error
    if err.is_invalid_access_token():
        print("Token is invalid or revoked — re-authenticate")
    elif err.is_expired_access_token():
        print("Token expired — refresh it")
    elif err.is_missing_scope():
        scope = err.get_missing_scope()
        print(f"Missing scope: {scope.required_scope}")
    elif err.is_user_suspended():
        print("User account is suspended")
```

---

## Rate Limits

Dropbox does not publish specific numeric rate limits. Key facts:

| Scenario | Response | Detail |
|----------|---------|--------|
| General rate limit | HTTP 429 | `Retry-After` header gives seconds to wait |
| Too many writes | HTTP 429 | reason: `too_many_write_operations` — parallel writes to same namespace |
| Data transport limit | HTTP 403 | Business plans; monthly cap; resets 1st of month |
| Development apps | — | Max 500 linked users; production approval required after 50 users |

```python
import time
import requests

def handle_rate_limit(response):
    """Handle 429 response from raw HTTP calls."""
    if response.status_code == 429:
        retry_after = int(response.headers.get('Retry-After', 1))
        print(f"Rate limited. Waiting {retry_after}s...")
        time.sleep(retry_after)
        return True
    return False
```

---

## Retry with Exponential Backoff

```python
import time
import random
import dropbox
from dropbox.exceptions import ApiError, HttpError

RETRYABLE_HTTP_CODES = {429, 500, 503}

def is_retryable(exc: Exception) -> tuple[bool, float]:
    """
    Returns (should_retry, wait_seconds).
    """
    if isinstance(exc, HttpError):
        if exc.status_code in RETRYABLE_HTTP_CODES:
            return True, 1.0
    if isinstance(exc, ApiError):
        # Some API errors are also retryable (server-side)
        pass
    # dropbox SDK sometimes wraps 429 as requests.exceptions.RetryError
    import requests
    if isinstance(exc, requests.exceptions.RetryError):
        return True, 2.0
    return False, 0.0


def with_retry(func, *args, max_retries=5, base_delay=1.0, **kwargs):
    """
    Call func(*args, **kwargs) with exponential backoff on retryable errors.

    Usage:
        metadata = with_retry(dbx.files_get_metadata, '/path/file.txt')
    """
    last_exc = None
    for attempt in range(max_retries + 1):
        try:
            return func(*args, **kwargs)
        except Exception as exc:
            retryable, hint_delay = is_retryable(exc)
            if not retryable or attempt == max_retries:
                raise

            # Respect Retry-After if available
            delay = hint_delay if hint_delay > 0 else base_delay * (2 ** attempt)
            delay += random.uniform(0, delay * 0.1)  # Jitter

            # Check for Retry-After header on HttpError
            if isinstance(exc, HttpError) and hasattr(exc, 'headers'):
                retry_after = exc.headers.get('Retry-After')
                if retry_after:
                    delay = float(retry_after)

            print(f"Attempt {attempt + 1}/{max_retries} failed: {exc}. "
                  f"Retrying in {delay:.1f}s...")
            time.sleep(delay)
            last_exc = exc

    raise last_exc


# Usage examples
metadata = with_retry(dbx.files_get_metadata, '/path/file.txt')
link = with_retry(dbx.sharing_create_shared_link_with_settings, '/path/file.pdf')
```

---

## Handling Specific Errors

### Upload: file conflict

```python
from dropbox.files import WriteMode

def upload_safe(dbx, data: bytes, path: str, strategy: str = 'overwrite') -> object:
    """Upload with configurable conflict handling."""
    if strategy == 'overwrite':
        return dbx.files_upload(data, path, mode=WriteMode.overwrite)
    elif strategy == 'rename':
        return dbx.files_upload(data, path, mode=WriteMode.add, autorename=True)
    elif strategy == 'skip':
        try:
            return dbx.files_upload(data, path, mode=WriteMode.add)
        except ApiError as e:
            if e.error.is_path() and e.error.get_path().is_conflict():
                return None  # Skip
            raise
    else:
        raise ValueError(f"Unknown strategy: {strategy}")
```

### Shared link already exists

```python
def get_or_create_link(dbx, path: str) -> str:
    """Get existing shared link or create a new one."""
    try:
        link = dbx.sharing_create_shared_link_with_settings(path)
        return link.url
    except ApiError as e:
        if e.error.is_shared_link_already_exists():
            result = dbx.sharing_list_shared_links(path=path, direct_only=True)
            if result.links:
                return result.links[0].url
        raise
```

### Path not found

```python
def safe_get_metadata(dbx, path: str):
    """Return None if path doesn't exist, raise on other errors."""
    try:
        return dbx.files_get_metadata(path)
    except ApiError as e:
        if e.error.is_path() and e.error.get_path().is_not_found():
            return None
        raise
```

### Token refresh

```python
def make_client(refresh_token: str, app_key: str, app_secret: str) -> dropbox.Dropbox:
    """
    Build client that auto-refreshes the access token.
    SDK handles refresh automatically with these params.
    """
    return dropbox.Dropbox(
        oauth2_refresh_token=refresh_token,
        app_key=app_key,
        app_secret=app_secret,
    )
```
