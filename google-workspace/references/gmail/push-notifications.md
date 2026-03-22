# Gmail Push Notifications & Incremental Sync

## Table of Contents
1. [Overview](#overview)
2. [Setup: Cloud Pub/Sub](#setup-cloud-pubsub)
3. [Register Watch](#register-watch)
4. [Receiving Notifications](#receiving-notifications)
5. [Processing with History API](#processing-with-history-api)
6. [Full Sync Pattern](#full-sync-pattern)
7. [Renewing Watch](#renewing-watch)

---

## Overview

Gmail push notifications use **Google Cloud Pub/Sub** to notify your application when mailbox state changes. The flow:

1. Your app registers a **watch** on a Gmail mailbox → Gmail returns `historyId`
2. Gmail publishes a notification to your Pub/Sub topic when anything changes
3. Notification contains: `emailAddress` + `historyId` (the new state)
4. Your app calls `history.list(startHistoryId=<last_known>)` to get what changed
5. Process changes (new messages, label changes, deletions)

**Why not polling?** The History API + Pub/Sub avoids the need to poll and miss changes, and is far more efficient than repeatedly calling `messages.list`.

---

## Setup: Cloud Pub/Sub

### 1. Create Pub/Sub topic

```bash
# Using gcloud CLI
gcloud pubsub topics create gmail-notifications

# Grant Gmail permission to publish to the topic
gcloud pubsub topics add-iam-policy-binding gmail-notifications \
  --member="serviceAccount:gmail-api-push@system.gserviceaccount.com" \
  --role="roles/pubsub.publisher"
```

```python
# Using Python client
from google.cloud import pubsub_v1

project_id = 'your-gcp-project'
topic_id = 'gmail-notifications'

publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path(project_id, topic_id)

# Create topic
publisher.create_topic(request={"name": topic_path})

# Grant Gmail service account publish rights
from google.iam.v1 import iam_policy_pb2

policy = publisher.get_iam_policy(request={"resource": topic_path})
policy.bindings.add(
    role="roles/pubsub.publisher",
    members=["serviceAccount:gmail-api-push@system.gserviceaccount.com"]
)
publisher.set_iam_policy(request={"resource": topic_path, "policy": policy})
```

### 2. Create subscription

For **push** (HTTP webhook):
```bash
gcloud pubsub subscriptions create gmail-sub \
  --topic=gmail-notifications \
  --push-endpoint=https://your-app.example.com/pubsub/push \
  --ack-deadline=60
```

For **pull** (polling your subscription):
```bash
gcloud pubsub subscriptions create gmail-sub-pull \
  --topic=gmail-notifications \
  --ack-deadline=60
```

---

## Register Watch

```python
def register_watch(service, user_id='me', topic_name=None,
                   label_ids=None, label_filter='include'):
    """
    Register Gmail push notifications.

    Args:
        topic_name: Full Pub/Sub topic: 'projects/PROJECT/topics/TOPIC'
        label_ids: Labels to watch (None = all mail)
        label_filter: 'include' (watch these labels) | 'exclude' (watch all except these)

    Returns:
        dict with historyId (save this!) and expiration timestamp (ms)
    """
    body = {
        'topicName': topic_name,
        'labelFilterAction': label_filter
    }
    if label_ids:
        body['labelIds'] = label_ids

    result = service.users().watch(userId=user_id, body=body).execute()

    print(f"Watch registered. historyId: {result['historyId']}")
    print(f"Expires: {result['expiration']} ms (renew before this!)")

    return result

# Watch inbox only
result = register_watch(
    service,
    topic_name='projects/my-project/topics/gmail-notifications',
    label_ids=['INBOX'],
    label_filter='include'
)

# Save this historyId — it's your starting point for incremental sync
saved_history_id = result['historyId']
```

**Watch expires after ~7 days.** Must renew before expiration or you'll miss changes.

---

## Receiving Notifications

### Push subscription (webhook)

Pub/Sub delivers HTTP POST to your endpoint. Body is base64-encoded JSON:

```python
import base64, json
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/pubsub/push', methods=['POST'])
def pubsub_push():
    envelope = request.get_json()
    if not envelope:
        return 'Bad Request', 400

    pubsub_message = envelope.get('message', {})
    data = pubsub_message.get('data', '')

    # Decode the Pub/Sub message data
    notification = json.loads(base64.b64decode(data).decode('utf-8'))

    email_address = notification.get('emailAddress')
    history_id = notification.get('historyId')

    print(f"Notification for {email_address}: historyId={history_id}")

    # Process the change (see below)
    process_gmail_change(email_address, history_id)

    # Acknowledge the message (return 200)
    return jsonify({'status': 'ok'}), 200
```

### Pull subscription

```python
from google.cloud import pubsub_v1

subscriber = pubsub_v1.SubscriberClient()
subscription_path = subscriber.subscription_path('my-project', 'gmail-sub-pull')

def pull_notifications():
    response = subscriber.pull(
        request={'subscription': subscription_path, 'max_messages': 10}
    )

    for received_message in response.received_messages:
        data = json.loads(received_message.message.data.decode('utf-8'))
        email = data.get('emailAddress')
        history_id = data.get('historyId')

        process_gmail_change(email, history_id)

        # Acknowledge
        subscriber.acknowledge(
            request={
                'subscription': subscription_path,
                'ack_ids': [received_message.ack_id]
            }
        )
```

---

## Processing with History API

After receiving a notification, use the History API to get what actually changed:

```python
def process_gmail_change(service, start_history_id: str,
                          label_id: str = None) -> str:
    """
    Fetch all changes since start_history_id.

    Returns the latest historyId to save for next time.
    """
    all_history = []
    page_token = None
    latest_history_id = start_history_id

    while True:
        kwargs = {
            'userId': 'me',
            'startHistoryId': start_history_id,
            'historyTypes': ['messageAdded', 'messageDeleted', 'labelAdded', 'labelRemoved'],
            'maxResults': 500
        }
        if label_id:
            kwargs['labelId'] = label_id
        if page_token:
            kwargs['pageToken'] = page_token

        try:
            results = service.users().history().list(**kwargs).execute()
        except HttpError as e:
            if e.status_code == 404:
                # History expired or invalid — do a full sync
                print("History not available, full sync required")
                return None  # Signal to caller to do full sync
            raise

        history = results.get('history', [])
        all_history.extend(history)

        # Track latest historyId
        if history:
            latest_history_id = history[-1]['id']

        page_token = results.get('nextPageToken')
        if not page_token:
            break

    # Process changes
    new_messages = []
    deleted_message_ids = []
    label_changes = []

    for record in all_history:
        for item in record.get('messagesAdded', []):
            msg = item['message']
            # Only care about inbox additions
            if 'INBOX' in msg.get('labelIds', []):
                new_messages.append(msg['id'])

        for item in record.get('messagesDeleted', []):
            deleted_message_ids.append(item['message']['id'])

        for item in record.get('labelsAdded', []):
            label_changes.append({
                'messageId': item['message']['id'],
                'action': 'add',
                'labels': item['labelIds']
            })

        for item in record.get('labelsRemoved', []):
            label_changes.append({
                'messageId': item['message']['id'],
                'action': 'remove',
                'labels': item['labelIds']
            })

    print(f"New messages: {len(new_messages)}")
    print(f"Deleted: {len(deleted_message_ids)}")
    print(f"Label changes: {len(label_changes)}")

    return latest_history_id  # Save this for next notification

# Usage in notification handler
def handle_notification(email_address, new_history_id):
    global saved_history_id

    latest_id = process_gmail_change(
        service=get_service_for_user(email_address),
        start_history_id=saved_history_id,
        label_id='INBOX'
    )

    if latest_id:
        saved_history_id = latest_id
    else:
        # Full sync needed
        do_full_sync(email_address)
```

---

## Full Sync Pattern

When history is unavailable (initial sync, or 404 from History API):

```python
def full_sync(service, label_id='INBOX') -> str:
    """
    Perform full sync of inbox. Returns current historyId.
    Use this for initial load or after history gap.
    """
    messages = []
    page_token = None

    while True:
        kwargs = {
            'userId': 'me',
            'maxResults': 500,
            'labelIds': [label_id] if label_id else None
        }
        if page_token:
            kwargs['pageToken'] = page_token

        results = service.users().messages().list(**kwargs).execute()
        messages.extend(results.get('messages', []))
        page_token = results.get('nextPageToken')

        if not page_token:
            break

    # Fetch current historyId from profile
    profile = service.users().getProfile(userId='me').execute()
    current_history_id = profile['historyId']

    print(f"Full sync: {len(messages)} messages, historyId={current_history_id}")
    return messages, current_history_id
```

---

## Renewing Watch

Watches expire after approximately 7 days. Renew proactively:

```python
import time
from datetime import datetime, timedelta

def should_renew_watch(expiration_ms: int, buffer_hours: int = 24) -> bool:
    """Check if watch needs renewal (within buffer_hours of expiration)."""
    expiration_dt = datetime.fromtimestamp(expiration_ms / 1000)
    renewal_threshold = expiration_dt - timedelta(hours=buffer_hours)
    return datetime.now() >= renewal_threshold

def renew_watch_if_needed(service, topic_name: str, current_expiration: int,
                           label_ids=None) -> dict:
    if should_renew_watch(current_expiration):
        print("Renewing watch...")
        result = register_watch(service, topic_name=topic_name, label_ids=label_ids)
        return result
    return None

# In a scheduled job (run daily)
def daily_maintenance(service, watch_config: dict) -> dict:
    result = renew_watch_if_needed(
        service,
        topic_name=watch_config['topic_name'],
        current_expiration=watch_config['expiration'],
        label_ids=watch_config.get('label_ids')
    )
    if result:
        watch_config.update(result)
    return watch_config
```

### Cloud Scheduler setup for renewal

```bash
# Renew watch every 6 days via Cloud Scheduler + Cloud Run/Functions
gcloud scheduler jobs create http renew-gmail-watch \
  --schedule="0 0 */6 * *" \
  --uri="https://your-app.example.com/api/renew-watch" \
  --http-method=POST \
  --time-zone="America/Los_Angeles"
```

### Stop watching

```python
service.users().stop(userId='me').execute()
```
