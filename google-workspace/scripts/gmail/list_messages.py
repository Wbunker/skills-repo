"""
Gmail List & Search Messages Script
Handles pagination, metadata extraction, and batch fetching.
"""
from typing import Optional, Generator
from googleapiclient.errors import HttpError


def list_message_ids(
    service,
    query: str = '',
    label_ids: list[str] = None,
    max_results: int = None,
    include_spam_trash: bool = False
) -> list[dict]:
    """
    List message IDs matching a query. Returns [{id, threadId}] stubs.

    Handles pagination automatically. For large result sets, use
    iter_message_ids() to avoid loading all IDs into memory.

    Args:
        query: Gmail search query (see references/search-operators.md)
        label_ids: Filter to messages with ALL these labels
        max_results: Cap total results. None = fetch all.
        include_spam_trash: Include SPAM and TRASH folders.
    """
    messages = []
    page_token = None

    while True:
        kwargs = {
            'userId': 'me',
            'includeSpamTrash': include_spam_trash,
        }
        if query:
            kwargs['q'] = query
        if label_ids:
            kwargs['labelIds'] = label_ids
        if page_token:
            kwargs['pageToken'] = page_token

        # Clamp maxResults per-request to API max (500)
        if max_results is not None:
            remaining = max_results - len(messages)
            kwargs['maxResults'] = min(remaining, 500)
        else:
            kwargs['maxResults'] = 500

        results = service.users().messages().list(**kwargs).execute()
        batch = results.get('messages', [])
        messages.extend(batch)

        if max_results and len(messages) >= max_results:
            messages = messages[:max_results]
            break

        page_token = results.get('nextPageToken')
        if not page_token:
            break

    return messages


def iter_message_ids(
    service,
    query: str = '',
    label_ids: list[str] = None,
    include_spam_trash: bool = False
) -> Generator[dict, None, None]:
    """
    Generator that yields message ID stubs one page at a time.
    Memory-efficient for very large result sets.
    """
    page_token = None

    while True:
        kwargs = {
            'userId': 'me',
            'maxResults': 500,
            'includeSpamTrash': include_spam_trash,
        }
        if query:
            kwargs['q'] = query
        if label_ids:
            kwargs['labelIds'] = label_ids
        if page_token:
            kwargs['pageToken'] = page_token

        results = service.users().messages().list(**kwargs).execute()

        for msg in results.get('messages', []):
            yield msg

        page_token = results.get('nextPageToken')
        if not page_token:
            break


def get_message(service, message_id: str, format: str = 'full',
                metadata_headers: list[str] = None) -> Optional[dict]:
    """
    Fetch a single message. Returns None if not found.

    Args:
        format: 'full' | 'metadata' | 'minimal' | 'raw'
        metadata_headers: Only with format='metadata'. Specific headers to include.
    """
    try:
        kwargs = {'userId': 'me', 'id': message_id, 'format': format}
        if metadata_headers and format == 'metadata':
            kwargs['metadataHeaders'] = metadata_headers
        return service.users().messages().get(**kwargs).execute()
    except HttpError as e:
        if e.status_code == 404:
            return None
        raise


def get_headers(msg: dict) -> dict:
    """Extract headers from a message as a flat dict."""
    return {h['name']: h['value'] for h in msg.get('payload', {}).get('headers', [])}


def batch_get_messages(
    service,
    message_ids: list[str],
    format: str = 'metadata',
    metadata_headers: list[str] = None,
    batch_size: int = 100
) -> dict[str, dict]:
    """
    Fetch multiple messages efficiently using BatchHttpRequest.

    Args:
        message_ids: List of message IDs to fetch.
        format: Message format for all requests.
        batch_size: Number of requests per batch (max 100).

    Returns:
        Dict mapping message_id -> message object.
    """
    results = {}
    errors = {}

    def make_callback(mid):
        def callback(request_id, response, exception):
            if exception:
                errors[mid] = exception
            else:
                results[mid] = response
        return callback

    # Process in chunks of batch_size
    for i in range(0, len(message_ids), batch_size):
        chunk = message_ids[i:i + batch_size]
        batch = service.new_batch_http_request()

        for mid in chunk:
            kwargs = {'userId': 'me', 'id': mid, 'format': format}
            if metadata_headers and format == 'metadata':
                kwargs['metadataHeaders'] = metadata_headers

            batch.add(
                service.users().messages().get(**kwargs),
                callback=make_callback(mid),
                request_id=mid
            )

        batch.execute()

    if errors:
        print(f"Warning: {len(errors)} messages failed to fetch: {list(errors.keys())[:5]}...")

    return results


def search_with_content(
    service,
    query: str,
    max_results: int = 50,
    format: str = 'full'
) -> list[dict]:
    """
    Search and immediately fetch full message content.
    Combines list + batch_get for efficiency.

    Returns: List of full message objects.
    """
    stubs = list_message_ids(service, query=query, max_results=max_results)
    if not stubs:
        return []

    ids = [s['id'] for s in stubs]
    messages_dict = batch_get_messages(service, ids, format=format)
    return list(messages_dict.values())


def iter_pages(service, initial_request):
    """
    Generic page iterator using the list_next() helper.
    Works with any resource that supports pagination (messages, threads, labels, etc.)

    Usage:
        request = service.users().messages().list(userId='me', q='is:unread')
        for response in iter_pages(service, request):
            for msg in response.get('messages', []):
                process(msg)
    """
    request = initial_request
    while request is not None:
        response = request.execute()
        yield response
        # list_next() checks for nextPageToken and rebuilds the request; returns None if done
        request = service.users().messages().list_next(
            previous_request=request,
            previous_response=response
        )


def get_thread_messages(service, thread_id: str, format: str = 'full') -> list[dict]:
    """Fetch all messages in a thread."""
    thread = service.users().threads().get(
        userId='me', id=thread_id, format=format
    ).execute()
    return thread.get('messages', [])


def count_messages(service, query: str = '') -> int:
    """
    Count messages matching a query without fetching content.
    Uses resultSizeEstimate (approximate for large counts).
    """
    kwargs = {'userId': 'me', 'maxResults': 1}
    if query:
        kwargs['q'] = query
    results = service.users().messages().list(**kwargs).execute()
    return results.get('resultSizeEstimate', 0)


if __name__ == '__main__':
    from auth import get_service

    service = get_service()

    # Example: list unread inbox messages and print subjects
    print("=== Unread inbox messages ===")
    messages = search_with_content(
        service,
        query='in:inbox is:unread',
        max_results=10,
        format='metadata'
    )

    for msg in messages:
        headers = get_headers(msg)
        print(f"  [{msg['id'][:8]}] {headers.get('Subject', '(no subject)')} - from {headers.get('From', '?')}")

    print(f"\nTotal unread estimate: {count_messages(service, 'is:unread')}")
