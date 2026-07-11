# Message Delivery (Email, SMS, Templates)

How Cognito sends verification codes, MFA codes, invitations, and password-reset messages — and how to customize them. To send through your **own** provider instead, use custom sender triggers ([lambda-triggers.md](lambda-triggers.md#custom-email--sms-sender--deliver-via-your-own-provider)). To reword Cognito's messages, use the custom message trigger ([lambda-triggers.md](lambda-triggers.md)).

## Table of Contents
1. [Email: default vs. SES](#email-default-vs-ses)
2. [SMS: SNS setup](#sms-sns-setup)
3. [Message templates & placeholders](#message-templates--placeholders)
4. [Testing without hard bounces](#testing-without-hard-bounces)

---

## Email: default vs. SES

Two modes, set by the pool's `EmailSendingAccount`:

| | `COGNITO_DEFAULT` | `DEVELOPER` (Amazon SES) |
|---|---|---|
| From address | `no-reply@verificationemail.com` | Your SES-verified identity |
| Cost | Free | SES pricing |
| Daily volume | Low (default cap) | Your SES limits |
| Custom FROM / REPLY-TO, HTML | No | Yes |
| `emailMessage`/`emailSubject` from the custom-message trigger | **Rejected** (`InvalidLambdaResponseException`) | Works |

Production apps generally want **SES** (`DEVELOPER`). Configure a **SES Region**, a verified **FROM address** (format `John Stiles <john@example.com>`), an optional configuration set, and REPLY-TO.

- Selecting SES in the console creates the service-linked role **`AWSServiceRoleForAmazonCognitoIdpEmailService`** (no sending-authorization policy needed for the SLR path); this needs `iam:CreateServiceLinkedRole` on the calling session.
- Via CLI/API you must attach a **SES sending-authorization policy** to the identity allowing principal `email.cognito-idp.amazonaws.com` to `SES:SendEmail`/`SendRawEmail`, scoped by `aws:SourceArn` (the pool) + `aws:SourceAccount`. (In an "alternate Region" where SES isn't co-located with Cognito, use the **regional** principal `cognito-idp.<pool-region>.amazonaws.com` and put the identity in the paired SES Region — commonly us-east-1 / us-west-2 / eu-west-1.)
- SES identities can be an email address or a verified domain (domain FROM requires CLI/API).

**Bounce-suppression trap (default config):** with `COGNITO_DEFAULT`, hard-bounced addresses land on an **AWS-managed suppression list you can't edit** — an address can stay suppressed **indefinitely** even after it becomes deliverable. Only the **SES (`DEVELOPER`)** path gives you an account-level suppression list you control. One more reason production uses SES.

## SMS: SNS setup

Cognito sends SMS through **Amazon SNS**, which needs an IAM role you grant (console: **Authentication methods → SMS → Edit → role**). Since Nov 2024 SNS hands off to **AWS End User Messaging SMS** under the hood — but you still grant **`sns:Publish`** (not `sms-voice:SendTextMessage`), and the console still says "Amazon SNS."

- **IAM role `ExternalId` (gotcha):** for **MFA** SMS, the role's trust policy must include an `sts:ExternalId` condition whose value equals the pool's `SmsConfiguration.ExternalId`. The console wires this up when it *creates* a role during pool creation — **but not when you reuse an existing role**; then you must set matching `ExternalId` values on both the role trust policy and the pool yourself. The trust policy also scopes by `aws:SourceArn` (pool) + `aws:SourceAccount`.
- **SMS sandbox:** a new account is in the SMS sandbox per Region — you can only text **verified** numbers (up to 10 with an origination identity) or use simulator numbers. Request production access before going live.
- **US destinations** require an **origination identity** (short code → 10DLC → toll-free priority order, not changeable).
- **Spend quota defaults to $1.00 USD/month** for new accounts — raise it (and re-raise per Region if you change SMS Regions) before production volume.
- SNS/End User Messaging charges per SMS (email is free); phone-number verification texts bill separately.
- **Region nuance:** Cognito uses SNS in the pool's Region or a **legacy alternate** Region (e.g. Seoul pools use Tokyo; Mumbai can use Singapore) — see AWS's alternate-Region table before requesting a separate limit increase.

## Message templates & placeholders

Edit under **Message templates**. Required placeholders **must** appear or the user can't complete the action:

| Placeholder | Meaning | Where |
|---|---|---|
| `{####}` | Verification/MFA **code**, or temp **password** | verification, MFA, forgot-password, invitation |
| `{username}` | User name | invitation, advanced-security messages |
| `{##Verify Your Email##}` | Renders as a **link** (text between `##…##` is editable, e.g. `{##Click here##}`) | email verification, **Link** type |

- **Email verification type is Code or Link.** Link is used for sign-up / resend-code; attribute-update and password-reset always use the **code** template even if Link is selected. Link URL looks like `https://<domain>/confirmUser/?client_id=…&user_name=…&confirmation_code=…` (needs a domain).
- **Length limits:** SMS **140** UTF-8 chars, email **20,000** UTF-8 chars (code/password included). HTML allowed in email.
- **Message types:** *Invitation* (admin-created users), *Verification* (sign-up), *MFA* (SMS MFA). Templates only appear when the corresponding feature (verification/MFA) is enabled.
- **Threat-protection (adaptive auth) placeholders** for notification emails: `{ip-address}`, `{city}`, `{country}`, `{login-time}`, `{device-name}`, `{event-id}`, `{feedback-token}`, and `{one-click-link-valid}`/`{one-click-link-invalid}` (the one-click link needs a domain). Set via the threat-protection Full-function config / `SetRiskConfiguration`.
- For fully dynamic/runtime message content, use the [custom message trigger](lambda-triggers.md).

## Testing without hard bounces

Cognito **throttles email for accounts that repeatedly incur hard bounces** (sending to a mailbox that doesn't exist). When testing:
- Use a **real** address you control, or
- The SES mailbox simulator **`success@simulator.amazonses.com`** (delivers successfully, nothing to read) — add labels for multiple test users: `success+user1@simulator.amazonses.com`.
- **Never** use a fake/nonexistent address.

To **diagnose delivery failures**, turn on `userNotification` **ERROR** log export (any feature plan) → a CloudWatch log group. See [monitoring.md](monitoring.md#log-export).
