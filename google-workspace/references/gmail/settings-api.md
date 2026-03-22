# Gmail Settings API

## Table of Contents
1. [Filters](#filters)
2. [Forwarding Addresses](#forwarding-addresses)
3. [Auto-Forwarding](#auto-forwarding)
4. [Send-As Aliases](#send-as-aliases)
5. [Vacation Responder](#vacation-responder)
6. [IMAP Settings](#imap-settings)
7. [POP Settings](#pop-settings)
8. [Delegates (Workspace only)](#delegates)
9. [Scopes Required](#scopes-required)

---

## Scopes Required

| Feature | Required Scope |
|---------|---------------|
| Filters, send-as, vacation, IMAP, POP | `gmail.settings.basic` |
| Forwarding, delegates | `gmail.settings.sharing` |
| Read-only access to settings | `gmail.readonly` |

---

## Filters

Filters automatically process incoming messages.

### List filters

```python
result = service.users().settings().filters().list(userId='me').execute()
filters = result.get('filter', [])

for f in filters:
    print(f"Filter ID: {f['id']}")
    print(f"  Criteria: {f.get('criteria', {})}")
    print(f"  Action: {f.get('action', {})}")
```

### Filter structure

```python
filter_body = {
    'criteria': {
        # Match criteria (all are optional, ANDed together)
        'from': 'newsletter@example.com',           # From address
        'to': 'me@gmail.com',                       # To address
        'subject': 'Weekly Update',                 # Subject contains
        'query': 'has:attachment larger:1M',        # Raw Gmail search
        'negatedQuery': 'is:important',             # Exclude if matches
        'hasAttachment': True,                      # Has any attachment
        'excludeChats': True,                       # Exclude chat messages
        'size': 1048576,                            # Size threshold in bytes
        'sizeComparison': 'larger'                  # 'larger' | 'smaller' | 'unspecified'
    },
    'action': {
        # Actions to take (multiple can be combined)
        'addLabelIds': ['STARRED', 'Label_123'],    # Add labels
        'removeLabelIds': ['INBOX'],                # Remove labels (archive)
        'forward': 'archive@other.com'              # Forward to address
    }
}
```

### Create filter

```python
new_filter = service.users().settings().filters().create(
    userId='me',
    body=filter_body
).execute()

filter_id = new_filter['id']
print(f"Created filter: {filter_id}")
```

### Delete filter

```python
service.users().settings().filters().delete(
    userId='me',
    id=filter_id
).execute()
```

**Note:** Filters cannot be updated — delete and recreate to change.

### Common filter recipes

```python
# Archive newsletters
newsletter_filter = {
    'criteria': {'query': 'unsubscribe'},
    'action': {'removeLabelIds': ['INBOX'], 'addLabelIds': []}
}

# Star emails from VIPs
vip_filter = {
    'criteria': {'from': 'ceo@company.com'},
    'action': {'addLabelIds': ['STARRED', 'IMPORTANT']}
}

# Label and archive receipts
receipt_filter = {
    'criteria': {'subject': 'receipt OR order confirmation OR invoice'},
    'action': {
        'addLabelIds': ['Label_receipts'],
        'removeLabelIds': ['INBOX']
    }
}
```

---

## Forwarding Addresses

Before enabling auto-forwarding, the destination address must be verified.

### List forwarding addresses

```python
result = service.users().settings().forwardingAddresses().list(userId='me').execute()
addresses = result.get('forwardingAddresses', [])
# Each: {forwardingEmail, verificationStatus: 'accepted'|'pending'}
```

### Create (request verification for) forwarding address

```python
result = service.users().settings().forwardingAddresses().create(
    userId='me',
    body={'forwardingEmail': 'archive@example.com'}
).execute()
# Sends verification email to archive@example.com
# verificationStatus will be 'pending' until confirmed
print(result['verificationStatus'])  # 'pending'
```

### Delete forwarding address

```python
service.users().settings().forwardingAddresses().delete(
    userId='me',
    forwardingEmail='archive@example.com'
).execute()
```

---

## Auto-Forwarding

Requires `gmail.settings.sharing` scope.

### Get auto-forward settings

```python
result = service.users().settings().getAutoForwarding(userId='me').execute()
# {enabled, emailAddress, disposition}
# disposition: 'leaveInInbox' | 'archive' | 'trash' | 'markRead'
```

### Update auto-forwarding

```python
# Must verify the email first (see Forwarding Addresses above)
service.users().settings().updateAutoForwarding(
    userId='me',
    body={
        'enabled': True,
        'emailAddress': 'archive@example.com',  # Must be verified
        'disposition': 'archive'
    }
).execute()

# Disable
service.users().settings().updateAutoForwarding(
    userId='me',
    body={'enabled': False, 'emailAddress': 'archive@example.com'}
).execute()
```

---

## Send-As Aliases

Manage "send mail as" addresses shown in Gmail's From dropdown.

### List aliases

```python
result = service.users().settings().sendAs().list(userId='me').execute()
for alias in result.get('sendAs', []):
    print(f"{alias['sendAsEmail']}: {alias.get('displayName', '')}")
    print(f"  Primary: {alias.get('isPrimary', False)}")
    print(f"  Default: {alias.get('isDefault', False)}")
    print(f"  Verified: {alias.get('verificationStatus', '')}")
```

### Get specific alias

```python
alias = service.users().settings().sendAs().get(
    userId='me',
    sendAsEmail='alias@yourdomain.com'
).execute()
# Full response:
# {
#   sendAsEmail, displayName, replyToAddress, signature,
#   isPrimary, isDefault, treatAsAlias,
#   verificationStatus: 'accepted' | 'pending',
#   smtpMsa: {...}  # Custom SMTP settings if applicable
# }
```

### Update alias

```python
service.users().settings().sendAs().patch(
    userId='me',
    sendAsEmail='alias@yourdomain.com',
    body={
        'displayName': 'Alice Smith (Work)',
        'replyToAddress': 'replies@yourdomain.com',
        'signature': '<p>Best regards,<br>Alice</p>',
        'isDefault': True,
        'treatAsAlias': True  # Whether replies come to primary inbox
    }
).execute()
```

### Send-As verification

```python
# Resend verification email for a pending send-as alias
service.users().settings().sendAs().verify(
    userId='me',
    sendAsEmail='alias@yourdomain.com'
).execute()
```

### S/MIME info (sub-resource)

```python
# List S/MIME configs for a send-as address
service.users().settings().sendAs().smimeInfo().list(
    userId='me',
    sendAsEmail='alias@example.com'
).execute()

# Set default S/MIME config
service.users().settings().sendAs().smimeInfo().setDefault(
    userId='me',
    sendAsEmail='alias@example.com',
    id=smime_id
).execute()

# Update signature via sendAs.patch
service.users().settings().sendAs().patch(
    userId='me',
    sendAsEmail='alias@example.com',
    body={'signature': '<p>My HTML signature</p>'}
).execute()
```

---

## Vacation Responder

### Get vacation settings

```python
vacation = service.users().settings().getVacation(userId='me').execute()
# {
#   enableAutoReply: bool,
#   responseSubject: str,
#   responseBodyPlainText: str,
#   responseBodyHtml: str,
#   restrictToContacts: bool,
#   restrictToDomain: bool,
#   startTime: str (Unix ms),
#   endTime: str (Unix ms)
# }
print(f"Auto-reply enabled: {vacation.get('enableAutoReply', False)}")
```

### Enable vacation responder

```python
from datetime import datetime

def enable_vacation(service, subject: str, body_html: str,
                     start_date: datetime, end_date: datetime,
                     contacts_only: bool = False, domain_only: bool = False):
    service.users().settings().updateVacation(
        userId='me',
        body={
            'enableAutoReply': True,
            'responseSubject': subject,
            'responseBodyHtml': body_html,
            'responseBodyPlainText': body_html,  # Fallback plain text
            'restrictToContacts': contacts_only,
            'restrictToDomain': domain_only,
            'startTime': str(int(start_date.timestamp() * 1000)),
            'endTime': str(int(end_date.timestamp() * 1000))
        }
    ).execute()

# Example
from datetime import datetime
enable_vacation(
    service,
    subject='Out of office: Jan 1-5',
    body_html='<p>I am on vacation. I will respond when I return on Jan 6.</p>',
    start_date=datetime(2025, 1, 1),
    end_date=datetime(2025, 1, 5, 23, 59, 59),
    domain_only=True  # Only auto-reply to @yourcompany.com
)
```

### Disable vacation responder

```python
service.users().settings().updateVacation(
    userId='me',
    body={'enableAutoReply': False}
).execute()
```

---

## IMAP Settings

### Get IMAP

```python
imap = service.users().settings().getImap(userId='me').execute()
# {
#   enabled: bool,
#   autoExpunge: bool,
#   expungeBehavior: 'archive' | 'trash' | 'deleteForever' | 'expungeBehaviorUnspecified',
#   maxFolderSize: int (0 = unlimited)
# }
```

### Update IMAP

```python
service.users().settings().updateImap(
    userId='me',
    body={
        'enabled': True,
        'autoExpunge': False,
        'expungeBehavior': 'archive',
        'maxFolderSize': 0  # Unlimited
    }
).execute()
```

---

## POP Settings

### Get POP

```python
pop = service.users().settings().getPop(userId='me').execute()
# {
#   accessWindow: 'disabled' | 'fromNowOn' | 'allMail',
#   disposition: 'leaveInInbox' | 'archive' | 'trash' | 'markRead'
# }
```

### Update POP

```python
service.users().settings().updatePop(
    userId='me',
    body={
        'accessWindow': 'fromNowOn',   # Enable POP for new mail only
        'disposition': 'archive'        # Archive after POP retrieval
    }
).execute()

# Disable POP
service.users().settings().updatePop(
    userId='me',
    body={'accessWindow': 'disabled'}
).execute()
```

---

## Delegates

Requires `gmail.settings.sharing` scope. Google Workspace accounts only.

Delegates can read, send, and delete messages on behalf of the delegating account.

### List delegates

```python
result = service.users().settings().delegates().list(userId='me').execute()
for delegate in result.get('delegates', []):
    print(f"{delegate['delegateEmail']}: {delegate['verificationStatus']}")
```

### Add delegate

```python
service.users().settings().delegates().create(
    userId='me',
    body={'delegateEmail': 'assistant@yourdomain.com'}
).execute()
# Sends verification email to delegate
# verificationStatus: 'accepted' | 'pending' | 'rejected' | 'expired'
```

### Remove delegate

```python
service.users().settings().delegates().delete(
    userId='me',
    delegateEmail='assistant@yourdomain.com'
).execute()
```
