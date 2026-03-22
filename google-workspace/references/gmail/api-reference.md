# Gmail API Complete Reference

Base URL: `https://gmail.googleapis.com/gmail/v1/users/{userId}/`

## Table of Contents
1. [Messages](#messages)
2. [Threads](#threads)
3. [Labels](#labels)
4. [Drafts](#drafts)
5. [History](#history)
6. [Profile](#profile)
7. [Watch / Push Notifications](#watch)
8. [Settings](#settings)

---

## Messages

### messages.list

```
GET /messages
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `q` | string | Gmail search query |
| `maxResults` | int | Max messages (default 100, max 500) |
| `pageToken` | string | Pagination token |
| `labelIds` | string[] | Filter to messages with ALL these labels |
| `includeSpamTrash` | bool | Include SPAM/TRASH (default false) |

```python
results = service.users().messages().list(
    userId='me',
    q='is:unread in:inbox',
    maxResults=100,
    labelIds=['INBOX'],
    includeSpamTrash=False
).execute()
# Returns: {messages: [{id, threadId}], nextPageToken, resultSizeEstimate}
```

### messages.get

```
GET /messages/{id}
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `id` | string | Message ID |
| `format` | string | `full` \| `metadata` \| `minimal` \| `raw` |
| `metadataHeaders` | string[] | Headers to include with `metadata` format |

```python
msg = service.users().messages().get(
    userId='me',
    id='18b1c2d3e4f5',
    format='full'
).execute()
```

### messages.send

```
POST /messages/send
```

```python
result = service.users().messages().send(
    userId='me',
    body={'raw': base64url_encoded_rfc2822}
).execute()
# Returns: {id, threadId, labelIds}
```

### messages.modify

```
POST /messages/{id}/modify
```

```python
service.users().messages().modify(
    userId='me',
    id=message_id,
    body={
        'addLabelIds': ['Label_123', 'STARRED'],
        'removeLabelIds': ['UNREAD', 'INBOX']
    }
).execute()
```

System labels: `INBOX`, `SENT`, `DRAFT`, `TRASH`, `SPAM`, `STARRED`, `IMPORTANT`, `UNREAD`, `CATEGORY_PERSONAL`, `CATEGORY_SOCIAL`, `CATEGORY_PROMOTIONS`, `CATEGORY_UPDATES`, `CATEGORY_FORUMS`

### messages.trash / untrash

```python
service.users().messages().trash(userId='me', id=message_id).execute()
service.users().messages().untrash(userId='me', id=message_id).execute()
```

### messages.delete

```
DELETE /messages/{id}
```

Permanently deletes. Requires `gmail.modify` or `mail.google.com` scope.

```python
service.users().messages().delete(userId='me', id=message_id).execute()
```

### messages.batchDelete

```
POST /messages/batchDelete
```

```python
service.users().messages().batchDelete(
    userId='me',
    body={'ids': ['id1', 'id2', 'id3']}
).execute()
# Returns empty body on success (204)
```

### messages.batchModify

```
POST /messages/batchModify
```

```python
service.users().messages().batchModify(
    userId='me',
    body={
        'ids': ['id1', 'id2', 'id3'],
        'addLabelIds': ['Label_123'],
        'removeLabelIds': ['UNREAD']
    }
).execute()
```

### messages.insert

Import a message directly into mailbox (bypasses sending infrastructure, no notifications).

```python
service.users().messages().insert(
    userId='me',
    body={'raw': base64url_msg, 'labelIds': ['INBOX']},
    internalDateSource='dateHeader',   # 'receivedTime' | 'dateHeader'
    deleted=False
).execute()
```

### messages.import_

Import with spam/filter processing. More like "receiving" a message.

```python
service.users().messages().import_(
    userId='me',
    body={'raw': base64url_msg},
    processForCalendar=True,
    deleted=False,
    neverMarkSpam=False,
    internalDateSource='dateHeader'
).execute()
```

### messages.attachments.get

```python
attachment = service.users().messages().attachments().get(
    userId='me',
    messageId=message_id,
    id=attachment_id
).execute()
# Returns: {size, data} where data is base64url encoded
file_data = base64.urlsafe_b64decode(attachment['data'] + '==')
```

---

## Threads

Threads group related messages. All messages in a thread share a `threadId`.

### threads.list

```python
results = service.users().threads().list(
    userId='me',
    q='subject:invoice',
    maxResults=50
).execute()
# Returns: {threads: [{id, snippet, historyId}], nextPageToken}
```

### threads.get

```python
thread = service.users().threads().get(
    userId='me',
    id=thread_id,
    format='full'  # 'full' | 'metadata' | 'minimal'
).execute()
# Returns: {id, historyId, messages: [message objects]}
```

### threads.modify

```python
service.users().threads().modify(
    userId='me',
    id=thread_id,
    body={
        'addLabelIds': ['STARRED'],
        'removeLabelIds': ['UNREAD']
    }
).execute()
```

### threads.trash / untrash / delete

```python
service.users().threads().trash(userId='me', id=thread_id).execute()
service.users().threads().untrash(userId='me', id=thread_id).execute()
service.users().threads().delete(userId='me', id=thread_id).execute()
```

---

## Labels

### System Labels (read-only, cannot be modified or deleted)

`INBOX`, `SENT`, `DRAFT`, `TRASH`, `SPAM`, `STARRED`, `IMPORTANT`, `UNREAD`
`CATEGORY_PERSONAL`, `CATEGORY_SOCIAL`, `CATEGORY_PROMOTIONS`, `CATEGORY_UPDATES`, `CATEGORY_FORUMS`

### labels.list

```python
results = service.users().labels().list(userId='me').execute()
labels = results.get('labels', [])
# Each: {id, name, type, messageListVisibility, labelListVisibility}
# type: 'system' | 'user'
```

### labels.get

```python
label = service.users().labels().get(userId='me', id='Label_123').execute()
# Returns full label with message/thread counts:
# {id, name, type, messagesTotal, messagesUnread, threadsTotal, threadsUnread,
#  messageListVisibility, labelListVisibility, color: {textColor, backgroundColor}}
```

### labels.create

```python
new_label = service.users().labels().create(
    userId='me',
    body={
        'name': 'Work/Important',  # Slash creates nested label
        'messageListVisibility': 'show',  # 'show' | 'hide'
        'labelListVisibility': 'labelShow',  # 'labelShow' | 'labelShowIfUnread' | 'labelHide'
        'color': {
            'textColor': '#ffffff',
            'backgroundColor': '#16a766'  # Must be a Gmail-supported hex color
        }
    }
).execute()
label_id = new_label['id']
```

### labels.update / patch

```python
# Full update
service.users().labels().update(
    userId='me', id='Label_123',
    body={'name': 'New Name', 'messageListVisibility': 'show', 'labelListVisibility': 'labelShow'}
).execute()

# Partial update
service.users().labels().patch(
    userId='me', id='Label_123',
    body={'name': 'Renamed Label'}
).execute()
```

### labels.delete

```python
service.users().labels().delete(userId='me', id='Label_123').execute()
# Returns empty (204). Messages with deleted label have it removed.
```

---

## Drafts

### drafts.create

```python
draft = service.users().drafts().create(
    userId='me',
    body={
        'message': {'raw': base64url_encoded_message}
    }
).execute()
draft_id = draft['id']
```

### drafts.list

```python
results = service.users().drafts().list(
    userId='me',
    maxResults=20
).execute()
# Returns: {drafts: [{id, message: {id, threadId}}], nextPageToken}
```

### drafts.get

```python
draft = service.users().drafts().get(
    userId='me', id=draft_id, format='full'
).execute()
# Returns: {id, message: <full message object>}
```

### drafts.update

```python
service.users().drafts().update(
    userId='me',
    id=draft_id,
    body={'message': {'raw': base64url_new_content}}
).execute()
```

### drafts.send

```python
result = service.users().drafts().send(
    userId='me',
    body={'id': draft_id}
).execute()
```

### drafts.delete

```python
service.users().drafts().delete(userId='me', id=draft_id).execute()
```

---

## History

The History API provides incremental change detection since a given `historyId`.

```python
results = service.users().history().list(
    userId='me',
    startHistoryId='1234567',
    historyTypes=['messageAdded', 'messageDeleted', 'labelAdded', 'labelRemoved'],
    labelId='INBOX',  # Optional: filter to specific label
    maxResults=100
).execute()

history = results.get('history', [])
for record in history:
    # Each record has historyId and one or more of:
    # messagesAdded, messagesDeleted, labelsAdded, labelsRemoved
    for added in record.get('messagesAdded', []):
        msg = added['message']  # {id, threadId, labelIds}
        print(f"New message: {msg['id']}")
```

**Getting initial historyId**: Call `users.getProfile()` or get from any message's `historyId` field.
**After gap**: If history is unavailable (returns 404 or empty), do a full sync instead.

See [push-notifications.md](push-notifications.md) for using History with Pub/Sub watch.

---

## Profile

```python
profile = service.users().getProfile(userId='me').execute()
# Returns: {emailAddress, messagesTotal, threadsTotal, historyId}
print(profile['emailAddress'])   # user@gmail.com
print(profile['historyId'])      # Current history ID for starting History API sync
```

---

## Watch

See [push-notifications.md](push-notifications.md) for full documentation.

```python
# Register for push notifications
result = service.users().watch(
    userId='me',
    body={
        'topicName': 'projects/my-project/topics/gmail-notifications',
        'labelIds': ['INBOX'],
        'labelFilterAction': 'include'  # 'include' | 'exclude'
    }
).execute()
# Returns: {historyId, expiration (Unix ms timestamp)}
# Watch expires after ~7 days — must be renewed

# Stop watching
service.users().stop(userId='me').execute()
```

---

## Settings

### Filters

```python
# List filters
filters = service.users().settings().filters().list(userId='me').execute()

# Create filter
new_filter = service.users().settings().filters().create(
    userId='me',
    body={
        'criteria': {
            'from': 'newsletter@example.com',
            'subject': 'Weekly digest',
            'hasAttachment': True,
            'excludeChats': True,
            'size': 1000000,          # Min size in bytes
            'sizeComparison': 'larger'  # 'larger' | 'smaller'
        },
        'action': {
            'addLabelIds': ['Label_123'],
            'removeLabelIds': ['INBOX'],
            'forward': 'archive@mycompany.com'
        }
    }
).execute()

# Delete filter
service.users().settings().filters().delete(userId='me', id=filter_id).execute()
```

### Send-As Aliases

```python
# List send-as addresses
aliases = service.users().settings().sendAs().list(userId='me').execute()

# Get specific alias
alias = service.users().settings().sendAs().get(
    userId='me', sendAsEmail='alias@yourdomain.com'
).execute()
# Returns: {sendAsEmail, displayName, replyToAddress, signature, isPrimary, isDefault, treatAsAlias, verificationStatus}

# Update alias
service.users().settings().sendAs().patch(
    userId='me',
    sendAsEmail='alias@yourdomain.com',
    body={'displayName': 'New Name', 'isDefault': True}
).execute()
```

### Vacation Responder

```python
# Get vacation settings
vacation = service.users().settings().getVacation(userId='me').execute()

# Update vacation
service.users().settings().updateVacation(
    userId='me',
    body={
        'enableAutoReply': True,
        'responseSubject': 'Out of office',
        'responseBodyPlainText': 'I am on vacation until Jan 2.',
        'responseBodyHtml': '<p>I am on vacation until Jan 2.</p>',
        'restrictToContacts': False,
        'restrictToDomain': True,
        'startTime': '1703980800000',  # Unix ms
        'endTime': '1704067200000'
    }
).execute()
```

### IMAP/POP Settings

```python
# Get IMAP settings
imap = service.users().settings().getImap(userId='me').execute()
# {enabled, autoExpunge, expungeBehavior, maxFolderSize}

# Update IMAP
service.users().settings().updateImap(
    userId='me',
    body={'enabled': True, 'autoExpunge': False, 'expungeBehavior': 'archive'}
).execute()

# Get POP settings
pop = service.users().settings().getPop(userId='me').execute()
# {accessWindow: 'disabled'|'fromNowOn'|'allMail', disposition: 'leaveInInbox'|'archive'|'trash'|'markRead'}
```
