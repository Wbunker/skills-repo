# AWS Collaboration — Capabilities Reference

For CLI commands, see [collaboration-cli.md](collaboration-cli.md).

## Amazon WorkMail

**Purpose**: Managed business email and calendar service, compatible with Microsoft Outlook and standard IMAP/SMTP clients, backed by AWS infrastructure.

### Core Concepts

| Concept | Description |
|---|---|
| **Organization** | A WorkMail deployment; maps to a domain; billed per user/month |
| **User** | A mailbox-enabled account with email address, calendar, and contacts |
| **Group** | Distribution list or shared mailbox; members receive email sent to the group alias |
| **Resource** | A bookable entity like a conference room or equipment; has its own mailbox |
| **Alias** | Additional email address for a user, group, or resource (all deliver to same mailbox) |
| **Impersonation role** | IAM-style role allowing programmatic access to mailboxes without user credentials |

### Email & Calendar Features

| Feature | Description |
|---|---|
| **IMAP access** | Standard IMAP4 and SMTP over TLS; compatible with any IMAP email client |
| **Microsoft Outlook** | Full support via Autodiscover; works with Outlook for Windows, Mac, and mobile |
| **Exchange Web Services (EWS)** | WorkMail exposes a subset of EWS for migration and integration tools |
| **Calendar** | Per-user calendar; meeting invitations, resource booking, free/busy sharing |
| **Contacts** | Global address list (GAL) from the organization directory; personal contacts |
| **Storage** | 50 GB mailbox storage per user; backed by S3 |

### Active Directory Integration

| Mode | Description |
|---|---|
| **AWS Managed Microsoft AD** | WorkMail syncs users/groups from a Managed AD directory; SSO via AWS SSO |
| **AD Connector** | Proxy authentication to an on-premises AD without syncing passwords |
| **Simple AD** | Lightweight standalone directory for smaller organizations |
| **SAML federation** | Use any SAML 2.0 IdP for single sign-on to the WorkMail web app |

### Email Rules & Flow

| Feature | Description |
|---|---|
| **Inbound email rules** | Lambda-based rules that can modify, block, or copy incoming email |
| **Outbound email rules** | Lambda-based rules on outgoing email; use case: DLP, disclaimers |
| **Email flow rules** | Organization-wide rules: allow/block, bounce, or run a Lambda action on matched email |
| **Availability configurations** | Share free/busy information with external EWS or EWS-compatible systems |
| **Mobile device policies** | Enforce passcode, encryption, remote wipe via ActiveSync MDM |

### S3 Email Storage

Configure WorkMail to store a copy of every email to an S3 bucket for compliance/archival:
- Delivered to `s3://bucket/domain/mailbox/year/month/day/messageId.eml`
- Works alongside normal mailbox storage (not a replacement)

---

## Amazon WorkDocs

**Purpose**: Managed enterprise document storage, collaboration, and review service with version control and fine-grained sharing.

### Core Concepts

| Concept | Description |
|---|---|
| **Site** | A WorkDocs deployment associated with a directory; one site per directory |
| **User** | An active or managed user with a personal drive (default 1 TB) |
| **Folder** | A hierarchical container for documents and sub-folders |
| **Document** | A file stored in WorkDocs; can have multiple versions |
| **Version** | Each upload creates a new version; all versions are retained |
| **Comment** | Inline annotations on document versions for review workflows |
| **Activity** | An audit event (upload, download, share, move, delete) recorded per resource |

### Sharing & Permissions

| Permission Level | Description |
|---|---|
| **Viewer** | Read-only access; can download |
| **Contributor** | Can upload new versions; cannot delete |
| **Co-owner** | Full control except deleting the root resource |
| **Owner** | Full control including deletion and permission management |

Sharing can be scoped to: specific users, the organization (all users in the site), or a public share link.

### Key Features

| Feature | Description |
|---|---|
| **Version history** | Every upload is a new version; restore any previous version; no version limit |
| **Lock/checkout** | Lock a document to prevent concurrent edits; unlock/check in when done |
| **Feedback & approval** | Request review from specific users; track approval status |
| **Activity feed** | Per-document and organization-wide activity log with filter and export |
| **WorkDocs Drive** | Desktop sync client for Windows and macOS; mounts WorkDocs as a network drive |
| **Search** | Full-text search across document content (supported formats: Office, PDF, text) |
| **Notifications** | Email or mobile push notification on document activity you're subscribed to |

### WorkDocs SDK

The `WorkDocs API` allows programmatic management of documents and metadata:

| API Capability | Description |
|---|---|
| **Upload documents** | Initiate upload → get presigned S3 URL → PUT file → update document version status |
| **Download documents** | Get download URL for a specific version |
| **Manage permissions** | Add/remove collaborators; set permission levels |
| **Custom metadata** | Attach up to 8 custom key-value pairs per document for categorization |
| **Labels** | Tag documents with colored labels for organization/filtering |
| **Notifications via SNS** | Subscribe to an SNS endpoint for real-time activity events |

---

## AWS Wickr

**Purpose**: End-to-end encrypted messaging and collaboration platform for enterprises and government agencies requiring strong data security and compliance.

### Core Concepts

| Concept | Description |
|---|---|
| **Network** | An isolated Wickr deployment for an organization |
| **User** | A Wickr account within a network; identified by Wickr ID |
| **Room** | A multi-participant encrypted conversation (like a group chat) |
| **Direct message** | Encrypted one-to-one conversation |
| **End-to-end encryption (E2EE)** | Messages are encrypted on sender's device; only recipients can decrypt; Wickr servers see only ciphertext |

### Encryption Model

| Feature | Description |
|---|---|
| **Military-grade encryption** | AES-256 for content; ECDH for key exchange; per-message encryption keys |
| **Perfect forward secrecy** | Each message uses a unique session key; compromise of one key does not expose others |
| **No plaintext on servers** | AWS/Wickr infrastructure never has access to message content |
| **Configurable message expiration** | Messages auto-delete after a configurable time (minutes to years) on all devices |
| **Ephemeral messaging** | Sender-controlled deletion timer; messages vanish from all recipients' devices |

### Data Retention & Compliance (AKEM)

AWS Wickr includes **Admin Key Escrow Module (AKEM)** for regulated industries:

| Feature | Description |
|---|---|
| **AKEM** | Escrows a copy of encryption keys with the organization; enables lawful intercept and eDiscovery |
| **Retention bot** | A bot user that passively receives copies of all messages for archival to S3 or other destinations |
| **Audit logging** | Immutable log of administrative actions and user activities |
| **Data retention policies** | Set minimum retention periods; prevent users from deleting below threshold |
| **Integration with SIEM** | Export audit logs to Splunk, QRadar, or other security tools |

### Bot Framework

| Feature | Description |
|---|---|
| **Wickr bot** | A programmatic Wickr user that can send/receive messages and files |
| **Bot SDK** | Available in Python and Java; handles E2EE transparently |
| **Use cases** | Alerting bots, ticketing integrations, ChatOps automation, compliance bots |
| **File attachments** | Bots can send and receive encrypted files |

### Wickr Enterprise vs. Wickr Gov

| Aspect | Wickr Enterprise | Wickr Gov |
|---|---|---|
| **Deployment** | AWS commercial regions | AWS GovCloud (US) |
| **Certifications** | SOC 2, ISO 27001 | FedRAMP High authorized, DoD IL4/IL5 capable |
| **Target** | Commercial enterprises | US government, defense contractors |
| **FIPS 140-2** | Not required | FIPS 140-2 validated cryptographic modules |
