# Gmail API Error Handling

## Table of Contents
1. [HttpError Basics](#httperror-basics)
2. [Error Code Reference](#error-code-reference)
3. [Rate Limits & Quotas](#rate-limits--quotas)
4. [Retry Strategy](#retry-strategy)
5. [Exponential Backoff Implementation](#exponential-backoff)
6. [Batch Error Handling](#batch-error-handling)
7. [Common Error Scenarios](#common-error-scenarios)

---

## HttpError Basics

All Gmail API errors raise `googleapiclient.errors.HttpError`:

```python
from googleapiclient.errors import HttpError

try:
    result = service.users().messages().get(userId='me', id='invalid_id').execute()
except HttpError as e:
    print(f"Status: {e.status_code}")     # e.g., 404
    print(f"Reason: {e.reason}")           # Short reason string
    print(f"Details: {e.error_details}")   # List of detail dicts
    # e.content contains raw JSON response body as bytes
    import json
    error_body = json.loads(e.content)
    print(error_body)  # {'error': {'code': 404, 'message': '...', 'errors': [...]}}
```

### Error response structure

```json
{
  "error": {
    "code": 404,
    "message": "Not Found",
    "errors": [
      {
        "message": "Not Found",
        "domain": "gmail",
        "reason": "notFound"
      }
    ]
  }
}
```

---

## Error Code Reference

| HTTP Code | Reason | Description | Action |
|-----------|--------|-------------|--------|
| 400 | `badRequest` | Invalid parameter or malformed request | Fix request parameters |
| 400 | `invalidArgument` | Invalid argument value | Check parameter values |
| 400 | `failedPrecondition` | Operation precondition not met | Check state before retrying |
| 401 | `authError` | Invalid or expired credentials | Refresh token, re-authenticate |
| 403 | `forbidden` | Insufficient permissions | Check scopes, check delegation |
| 403 | `domainPolicy` | Domain policy blocks operation | Contact Workspace admin |
| 403 | `userRateLimitExceeded` | Per-user rate limit hit | Backoff and retry |
| 403 | `rateLimitExceeded` | Project-wide rate limit | Backoff and retry |
| 404 | `notFound` | Resource not found | Verify ID exists |
| 409 | `conflict` | Resource already exists | Handle duplicate |
| 429 | `quotaExceeded` | Daily quota exhausted | Wait until quota resets (midnight PT) |
| 500 | `backendError` | Backend error | Retry with backoff |
| 503 | `backendError` | Service unavailable | Retry with backoff |

### Distinguishing 403 subtypes

```python
import json

def get_error_reason(e: HttpError) -> str:
    try:
        body = json.loads(e.content)
        errors = body.get('error', {}).get('errors', [])
        return errors[0].get('reason', '') if errors else ''
    except Exception:
        return ''

try:
    service.users().messages().list(userId='me').execute()
except HttpError as e:
    reason = get_error_reason(e)
    if e.status_code == 403:
        if reason in ('userRateLimitExceeded', 'rateLimitExceeded'):
            # Retry with backoff
            pass
        elif reason == 'forbidden':
            # Check OAuth scopes
            pass
        elif reason == 'domainPolicy':
            # Contact admin
            pass
```

---

## Rate Limits & Quotas

### Rate limit structure

| Limit | Value |
|-------|-------|
| Per-project | 1,200,000 quota units/minute |
| Per-user | 15,000 quota units/user/minute |

| Method | Quota Units |
|--------|-------------|
| `messages.send`, `drafts.send`, `watch` | 100 |
| `settings.delegates.create`, `settings.sendAs.create` | 100 |
| `messages.batchDelete`, `messages.batchModify` | 50 |
| `drafts.update` | 15 |
| `messages.delete`, `drafts.create`, `drafts.delete` | 10 |
| `threads.modify`, `threads.trash`, `threads.delete` | 10–20 |
| `messages.get`, `messages.list`, `drafts.get`, `drafts.list` | 5 |
| `labels.create`, `labels.delete`, `labels.update` | 5 |
| `labels.get`, `labels.list` | 1 |
| `users.getProfile`, `history.list` | 1–2 |

### Sending limits

- @gmail.com accounts: ~500 emails/day
- Google Workspace: varies by plan
- Per-user 429 limits cannot be increased via quota requests

### Burst behavior

Short bursts are tolerated; sustained rates approaching the per-user minute limit trigger 429/403 responses.

---

## Retry Strategy

### What to retry

| Error | Retry? | Strategy |
|-------|--------|----------|
| 429 | Yes | Exponential backoff |
| 403 `rateLimitExceeded` | Yes | Exponential backoff |
| 403 `userRateLimitExceeded` | Yes | Exponential backoff |
| 500, 503 | Yes | Exponential backoff |
| 401 | Yes (once) | Refresh token first |
| 404 | No | Fix the ID |
| 400 | No | Fix the request |
| 403 `forbidden` | No | Fix scopes |

---

## Exponential Backoff Implementation

```python
import time
import random
from googleapiclient.errors import HttpError

RETRYABLE_STATUS_CODES = {429, 500, 503}
RETRYABLE_REASONS = {'userRateLimitExceeded', 'rateLimitExceeded', 'backendError'}

def is_retryable(e: HttpError) -> bool:
    if e.status_code in RETRYABLE_STATUS_CODES:
        return True
    if e.status_code == 403:
        reason = get_error_reason(e)
        return reason in RETRYABLE_REASONS
    return False

def execute_with_backoff(request, max_retries: int = 5, base_delay: float = 1.0):
    """Execute a Gmail API request with exponential backoff."""
    for attempt in range(max_retries + 1):
        try:
            return request.execute()
        except HttpError as e:
            if attempt == max_retries or not is_retryable(e):
                raise

            # Exponential backoff with jitter
            delay = base_delay * (2 ** attempt) + random.uniform(0, 1)
            print(f"Rate limited (attempt {attempt+1}/{max_retries}). Retrying in {delay:.1f}s...")
            time.sleep(delay)

    raise RuntimeError("Max retries exceeded")  # Should not reach here

# Usage
result = execute_with_backoff(
    service.users().messages().list(userId='me', q='is:unread')
)
```

### Decorator approach

```python
import functools

def with_backoff(max_retries=5, base_delay=1.0):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except HttpError as e:
                    if attempt == max_retries or not is_retryable(e):
                        raise
                    delay = base_delay * (2 ** attempt) + random.uniform(0, 1)
                    time.sleep(delay)
        return wrapper
    return decorator

@with_backoff(max_retries=3)
def send_email(service, raw_message):
    return service.users().messages().send(
        userId='me', body={'raw': raw_message}
    ).execute()
```

---

## Batch Error Handling

Individual requests within a `BatchHttpRequest` can fail independently:

```python
from googleapiclient.http import BatchHttpRequest
from googleapiclient.errors import HttpError

results = {}
errors = {}

def callback(request_id, response, exception):
    if exception:
        errors[request_id] = exception
        if isinstance(exception, HttpError):
            print(f"Request {request_id} failed: {exception.status_code} {exception.reason}")
    else:
        results[request_id] = response

batch = service.new_batch_http_request(callback=callback)

message_ids = ['id1', 'id2', 'id3', 'invalid_id']
for msg_id in message_ids:
    batch.add(
        service.users().messages().get(userId='me', id=msg_id, format='metadata'),
        request_id=msg_id
    )

batch.execute()

print(f"Succeeded: {list(results.keys())}")
print(f"Failed: {list(errors.keys())}")
```

### Retry failed batch items

```python
def batch_get_with_retry(service, message_ids: list[str], max_retries=3) -> dict:
    """Get multiple messages, retrying failures."""
    results = {}
    failed_ids = list(message_ids)

    for attempt in range(max_retries):
        if not failed_ids:
            break

        batch_results = {}
        batch_errors = {}

        def callback(request_id, response, exception):
            if exception:
                batch_errors[request_id] = exception
            else:
                batch_results[request_id] = response

        batch = service.new_batch_http_request(callback=callback)
        for msg_id in failed_ids:
            batch.add(
                service.users().messages().get(userId='me', id=msg_id),
                request_id=msg_id
            )
        batch.execute()

        results.update(batch_results)
        failed_ids = [
            mid for mid, err in batch_errors.items()
            if isinstance(err, HttpError) and is_retryable(err)
        ]

        if failed_ids and attempt < max_retries - 1:
            delay = 2 ** attempt + random.uniform(0, 1)
            time.sleep(delay)

    return results
```

---

## Common Error Scenarios

### Token expired mid-operation

```python
from google.auth.exceptions import RefreshError

try:
    result = service.users().messages().list(userId='me').execute()
except HttpError as e:
    if e.status_code == 401:
        # Token expired — refresh and retry
        creds.refresh(Request())
        service = build('gmail', 'v1', credentials=creds)
        result = service.users().messages().list(userId='me').execute()
except RefreshError:
    # Refresh token invalid — user must re-authenticate
    print("Re-authentication required. Delete token.json and re-run.")
```

### Message not found (deleted or wrong ID)

```python
try:
    msg = service.users().messages().get(userId='me', id=message_id).execute()
except HttpError as e:
    if e.status_code == 404:
        print(f"Message {message_id} not found (may have been deleted)")
        msg = None
```

### Sending limits exceeded

```python
try:
    service.users().messages().send(userId='me', body={'raw': raw}).execute()
except HttpError as e:
    if e.status_code == 429:
        print("Daily sending limit exceeded. Try tomorrow.")
    elif e.status_code == 403:
        reason = get_error_reason(e)
        if reason == 'forbidden':
            print("Not allowed to send from this address. Check send-as permissions.")
```

### Large message (> 25 MB)

Gmail's message size limit is 25 MB (including attachments, base64 overhead). For large files, use Google Drive links instead.

```python
import sys

MAX_MESSAGE_SIZE = 25 * 1024 * 1024  # 25 MB

def check_message_size(raw_bytes: bytes) -> bool:
    # base64 adds ~33% overhead
    estimated_size = len(raw_bytes) * 4 / 3
    return estimated_size < MAX_MESSAGE_SIZE
```
