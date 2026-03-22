"""
Gmail Batch Operations
Efficient bulk read, modify, and delete using BatchHttpRequest.
Max 100 requests per batch.
"""
import time
import random
from googleapiclient.errors import HttpError


def batch_modify_messages(
    service,
    message_ids: list[str],
    add_labels: list[str] = None,
    remove_labels: list[str] = None,
    batch_size: int = 100
) -> tuple[int, list[str]]:
    """
    Apply label changes to many messages efficiently.

    Args:
        add_labels: Label IDs to add.
        remove_labels: Label IDs to remove.
        batch_size: Requests per batch (max 100).

    Returns:
        (success_count, failed_ids)

    Example - mark 500 messages as read:
        batch_modify_messages(service, ids, remove_labels=['UNREAD'])
    """
    if not add_labels and not remove_labels:
        raise ValueError("Must specify add_labels or remove_labels")

    body = {}
    if add_labels:
        body['addLabelIds'] = add_labels
    if remove_labels:
        body['removeLabelIds'] = remove_labels

    # Use batchModify for large sets (more efficient than individual requests)
    success_count = 0
    failed_ids = []

    for i in range(0, len(message_ids), 1000):  # batchModify handles up to 1000 IDs
        chunk = message_ids[i:i + 1000]
        try:
            service.users().messages().batchModify(
                userId='me',
                body={'ids': chunk, **body}
            ).execute()
            success_count += len(chunk)
        except HttpError as e:
            # Fall back to individual batch requests
            print(f"batchModify failed ({e.status_code}), falling back to individual requests")
            s, f = _individual_batch_modify(service, chunk, body, batch_size)
            success_count += s
            failed_ids.extend(f)

    return success_count, failed_ids


def _individual_batch_modify(service, message_ids, body, batch_size):
    """Fallback: modify messages one at a time in a BatchHttpRequest."""
    success_count = 0
    failed_ids = []

    for i in range(0, len(message_ids), batch_size):
        chunk = message_ids[i:i + batch_size]
        batch_results = {'success': 0, 'failed': []}

        def make_callback(mid):
            def callback(request_id, response, exception):
                if exception:
                    batch_results['failed'].append(mid)
                else:
                    batch_results['success'] += 1
            return callback

        batch = service.new_batch_http_request()
        for mid in chunk:
            batch.add(
                service.users().messages().modify(
                    userId='me', id=mid, body=body
                ),
                callback=make_callback(mid)
            )
        batch.execute()

        success_count += batch_results['success']
        failed_ids.extend(batch_results['failed'])

    return success_count, failed_ids


def batch_delete_messages(
    service,
    message_ids: list[str],
    chunk_size: int = 1000
) -> tuple[int, list[str]]:
    """
    Permanently delete many messages.

    WARNING: This is irreversible. Consider batch_trash_messages() instead.

    Args:
        chunk_size: IDs per batchDelete call (max 1000).
    """
    success_count = 0
    failed_ids = []

    for i in range(0, len(message_ids), chunk_size):
        chunk = message_ids[i:i + chunk_size]
        try:
            service.users().messages().batchDelete(
                userId='me',
                body={'ids': chunk}
            ).execute()
            success_count += len(chunk)
        except HttpError as e:
            print(f"batchDelete chunk {i//chunk_size} failed: {e.status_code}")
            failed_ids.extend(chunk)

    return success_count, failed_ids


def batch_trash_messages(service, message_ids: list[str], batch_size: int = 100):
    """
    Move many messages to trash (reversible, unlike delete).
    """
    return batch_modify_messages(
        service, message_ids,
        add_labels=['TRASH'],
        remove_labels=['INBOX']
    )


def batch_get_messages(
    service,
    message_ids: list[str],
    format: str = 'metadata',
    metadata_headers: list[str] = None,
    batch_size: int = 100
) -> tuple[dict[str, dict], dict[str, Exception]]:
    """
    Fetch many messages in parallel batches.

    Returns:
        (results dict {id -> message}, errors dict {id -> exception})
    """
    all_results = {}
    all_errors = {}

    for i in range(0, len(message_ids), batch_size):
        chunk = message_ids[i:i + batch_size]
        chunk_results = {}
        chunk_errors = {}

        def make_callback(mid):
            def callback(request_id, response, exception):
                if exception:
                    chunk_errors[mid] = exception
                else:
                    chunk_results[mid] = response
            return callback

        batch = service.new_batch_http_request()
        for mid in chunk:
            kwargs = {'userId': 'me', 'id': mid, 'format': format}
            if metadata_headers and format == 'metadata':
                kwargs['metadataHeaders'] = metadata_headers
            batch.add(
                service.users().messages().get(**kwargs),
                callback=make_callback(mid)
            )

        batch.execute()
        all_results.update(chunk_results)
        all_errors.update(chunk_errors)

    return all_results, all_errors


def archive_messages(service, message_ids: list[str]) -> tuple[int, list[str]]:
    """Archive messages (remove from inbox without deleting)."""
    return batch_modify_messages(
        service, message_ids,
        remove_labels=['INBOX']
    )


def mark_read(service, message_ids: list[str]) -> tuple[int, list[str]]:
    """Mark messages as read."""
    return batch_modify_messages(
        service, message_ids,
        remove_labels=['UNREAD']
    )


def mark_unread(service, message_ids: list[str]) -> tuple[int, list[str]]:
    """Mark messages as unread."""
    return batch_modify_messages(
        service, message_ids,
        add_labels=['UNREAD']
    )


def apply_label(service, message_ids: list[str], label_id: str) -> tuple[int, list[str]]:
    """Apply a label to many messages."""
    return batch_modify_messages(service, message_ids, add_labels=[label_id])


def remove_label(service, message_ids: list[str], label_id: str) -> tuple[int, list[str]]:
    """Remove a label from many messages."""
    return batch_modify_messages(service, message_ids, remove_labels=[label_id])


def cleanup_old_messages(
    service,
    query: str,
    action: str = 'trash',
    dry_run: bool = True,
    max_messages: int = 5000
) -> int:
    """
    Clean up messages matching a query.

    Args:
        query: Gmail search query.
        action: 'trash' | 'delete' | 'archive' | 'mark_read'
        dry_run: If True, only count matching messages without acting.
        max_messages: Safety cap on messages to process.

    Returns:
        Number of messages processed.
    """
    from list_messages import list_message_ids

    print(f"Searching for: {query}")
    stubs = list_message_ids(service, query=query, max_results=max_messages)
    message_ids = [s['id'] for s in stubs]

    print(f"Found {len(message_ids)} messages")
    if dry_run:
        print("DRY RUN - no changes made. Set dry_run=False to apply.")
        return len(message_ids)

    if not message_ids:
        return 0

    if action == 'trash':
        count, failed = batch_trash_messages(service, message_ids)
    elif action == 'delete':
        count, failed = batch_delete_messages(service, message_ids)
    elif action == 'archive':
        count, failed = archive_messages(service, message_ids)
    elif action == 'mark_read':
        count, failed = mark_read(service, message_ids)
    else:
        raise ValueError(f"Unknown action: {action}")

    print(f"Processed: {count}, Failed: {len(failed)}")
    return count


if __name__ == '__main__':
    from auth import get_service

    service = get_service()

    # Dry run: find old promotions
    cleanup_old_messages(
        service,
        query='category:promotions older_than:30d',
        action='trash',
        dry_run=True
    )
