"""
Gmail Push Notifications & Incremental History Sync
Handles watch registration, notification processing, and history-based sync.
"""
import json
import time
import base64
from datetime import datetime
from googleapiclient.errors import HttpError


class GmailWatcher:
    """
    Manages Gmail push notifications via Cloud Pub/Sub.

    Usage:
        watcher = GmailWatcher(service, topic_name='projects/my-proj/topics/gmail')
        watcher.start_watch(label_ids=['INBOX'])

        # In your Pub/Sub callback:
        changes = watcher.process_notification(history_id)
    """

    def __init__(self, service, topic_name: str, state_file: str = 'gmail_watch_state.json'):
        """
        Args:
            service: Authenticated Gmail service.
            topic_name: Pub/Sub topic name (projects/{project}/topics/{topic}).
            state_file: File to persist historyId and expiration between runs.
        """
        self.service = service
        self.topic_name = topic_name
        self.state_file = state_file
        self._state = self._load_state()

    def _load_state(self) -> dict:
        try:
            with open(self.state_file) as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def _save_state(self):
        with open(self.state_file, 'w') as f:
            json.dump(self._state, f, indent=2)

    @property
    def history_id(self) -> str:
        return self._state.get('historyId')

    @property
    def expiration_ms(self) -> int:
        return self._state.get('expiration', 0)

    @property
    def is_watch_expired(self) -> bool:
        """True if watch has expired or will expire within 24 hours."""
        if not self.expiration_ms:
            return True
        buffer_ms = 24 * 60 * 60 * 1000  # 24 hours
        return time.time() * 1000 >= (self.expiration_ms - buffer_ms)

    def start_watch(self, label_ids: list[str] = None,
                     label_filter: str = 'include') -> dict:
        """
        Register or renew Gmail push notification watch.

        Args:
            label_ids: Labels to watch. None = all mail.
            label_filter: 'include' (watch these) | 'exclude' (watch all except these).

        Returns:
            Watch response {historyId, expiration}.
        """
        body = {
            'topicName': self.topic_name,
            'labelFilterAction': label_filter
        }
        if label_ids:
            body['labelIds'] = label_ids

        result = self.service.users().watch(userId='me', body=body).execute()

        # Save initial historyId if we don't have one yet
        if not self._state.get('historyId'):
            self._state['historyId'] = result['historyId']

        self._state['expiration'] = int(result['expiration'])
        self._save_state()

        expires_dt = datetime.fromtimestamp(int(result['expiration']) / 1000)
        print(f"Watch registered. Expires: {expires_dt.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"historyId: {result['historyId']}")

        return result

    def stop_watch(self):
        """Stop receiving push notifications."""
        self.service.users().stop(userId='me').execute()
        print("Watch stopped.")

    def renew_if_needed(self, label_ids: list[str] = None) -> bool:
        """Renew watch if expired or expiring soon. Returns True if renewed."""
        if self.is_watch_expired:
            print("Renewing watch...")
            self.start_watch(label_ids=label_ids)
            return True
        return False

    def process_notification(self, new_history_id: str,
                               label_id: str = None) -> dict:
        """
        Process a Pub/Sub notification by fetching history changes.

        Args:
            new_history_id: historyId from the Pub/Sub notification.
            label_id: Optional label filter for history (e.g., 'INBOX').

        Returns:
            Dict with 'new_messages', 'deleted', 'label_changes' lists.
            Returns None if full sync is needed (history gap).
        """
        if not self.history_id:
            print("No historyId stored. Performing full sync.")
            return None

        changes = {
            'new_messages': [],
            'deleted': [],
            'label_changes': [],
            'latest_history_id': self.history_id
        }

        page_token = None

        while True:
            kwargs = {
                'userId': 'me',
                'startHistoryId': self.history_id,
                'historyTypes': ['messageAdded', 'messageDeleted', 'labelAdded', 'labelRemoved'],
                'maxResults': 500
            }
            if label_id:
                kwargs['labelId'] = label_id
            if page_token:
                kwargs['pageToken'] = page_token

            try:
                results = self.service.users().history().list(**kwargs).execute()
            except HttpError as e:
                if e.status_code == 404:
                    print(f"History not available (historyId {self.history_id} expired). Full sync needed.")
                    return None
                raise

            history = results.get('history', [])

            for record in history:
                history_id = record.get('id', self.history_id)
                if history_id > changes['latest_history_id']:
                    changes['latest_history_id'] = history_id

                for item in record.get('messagesAdded', []):
                    msg = item['message']
                    changes['new_messages'].append({
                        'id': msg['id'],
                        'threadId': msg.get('threadId', ''),
                        'labelIds': msg.get('labelIds', [])
                    })

                for item in record.get('messagesDeleted', []):
                    changes['deleted'].append(item['message']['id'])

                for item in record.get('labelsAdded', []):
                    changes['label_changes'].append({
                        'messageId': item['message']['id'],
                        'action': 'add',
                        'labels': item.get('labelIds', [])
                    })

                for item in record.get('labelsRemoved', []):
                    changes['label_changes'].append({
                        'messageId': item['message']['id'],
                        'action': 'remove',
                        'labels': item.get('labelIds', [])
                    })

            page_token = results.get('nextPageToken')
            if not page_token:
                break

        # Update stored historyId
        self._state['historyId'] = changes['latest_history_id']
        self._save_state()

        return changes

    def full_sync(self, label_id: str = 'INBOX') -> tuple[list[dict], str]:
        """
        Perform full mailbox sync. Use after history gap or initial setup.

        Returns:
            (list of message stubs, current historyId)
        """
        from list_messages import list_message_ids

        print(f"Starting full sync of {label_id}...")
        messages = list_message_ids(
            self.service,
            label_ids=[label_id] if label_id else None
        )

        profile = self.service.users().getProfile(userId='me').execute()
        history_id = profile['historyId']

        self._state['historyId'] = history_id
        self._save_state()

        print(f"Full sync complete: {len(messages)} messages, historyId={history_id}")
        return messages, history_id


def decode_pubsub_notification(data: str) -> dict:
    """
    Decode a Pub/Sub message data field.

    Args:
        data: Base64-encoded string from Pub/Sub message.data

    Returns:
        {'emailAddress': '...', 'historyId': '...'}
    """
    decoded = base64.b64decode(data).decode('utf-8')
    return json.loads(decoded)


def handle_pubsub_push(request_body: dict, watcher: GmailWatcher,
                        on_new_message=None, on_deleted=None) -> bool:
    """
    Handle a Pub/Sub push HTTP request.

    Args:
        request_body: Parsed JSON from POST request body.
        watcher: GmailWatcher instance.
        on_new_message: Callback(message_stub) for new messages.
        on_deleted: Callback(message_id) for deleted messages.

    Returns:
        True if processed successfully (return 200), False otherwise.
    """
    try:
        pubsub_message = request_body.get('message', {})
        data = pubsub_message.get('data', '')
        if not data:
            return False

        notification = decode_pubsub_notification(data)
        history_id = notification.get('historyId', '')
        email = notification.get('emailAddress', '')

        print(f"Notification: {email} historyId={history_id}")

        changes = watcher.process_notification(history_id, label_id='INBOX')

        if changes is None:
            # Need full sync
            watcher.full_sync()
            return True

        print(f"Changes: +{len(changes['new_messages'])} new, "
              f"-{len(changes['deleted'])} deleted, "
              f"~{len(changes['label_changes'])} label changes")

        if on_new_message:
            for msg_stub in changes['new_messages']:
                if 'INBOX' in msg_stub.get('labelIds', []):
                    on_new_message(msg_stub)

        if on_deleted:
            for msg_id in changes['deleted']:
                on_deleted(msg_id)

        return True

    except Exception as e:
        print(f"Error processing notification: {e}")
        return False


# Flask integration example
def create_flask_handler(watcher: GmailWatcher):
    """
    Create a Flask route handler for Pub/Sub push notifications.

    Usage:
        app = Flask(__name__)
        app.route('/pubsub/push', methods=['POST'])(
            create_flask_handler(watcher)
        )
    """
    def handler():
        from flask import request, jsonify

        body = request.get_json(silent=True)
        if not body:
            return 'Bad Request', 400

        def on_new_message(stub):
            print(f"New message in inbox: {stub['id']}")
            # Fetch full message, process, notify, etc.

        success = handle_pubsub_push(body, watcher, on_new_message=on_new_message)
        return jsonify({'ok': success}), 200 if success else 500

    return handler


if __name__ == '__main__':
    from auth import get_service

    service = get_service()

    watcher = GmailWatcher(
        service,
        topic_name='projects/your-project/topics/gmail-notifications'
    )

    # Start watching (replace with your topic name)
    result = watcher.start_watch(label_ids=['INBOX'])
    print(f"Watching. historyId: {watcher.history_id}")
