# Lambda Triggers

User pool Lambda triggers let you customize auth behavior: validate sign-ups, migrate users, add token claims, build custom challenges, and localize/redirect messages. Cognito invokes them **synchronously** (5s timeout, no retry on 5xx) and expects the event object back with your changes in `event.response`.

## Table of Contents
1. [Trigger catalog](#trigger-catalog)
2. [Event shape](#event-shape)
3. [Recipes](#recipes)
4. [Gotchas](#gotchas)

---

## Trigger catalog

| Trigger | When | Typical use |
|---|---|---|
| **Pre sign-up** | Before a user is created | Auto-confirm, block domains, custom validation |
| **Post confirmation** | After confirm sign-up / reset | Create a DB row, send welcome, subscribe to SNS |
| **Pre authentication** | Before sign-in is validated | Block sign-in by custom rule |
| **Post authentication** | After successful sign-in | Analytics, audit logging |
| **Pre token generation** | Before ID/access tokens issued | Add/modify/suppress claims, add groups/scopes |
| **Migrate user** | Sign-in/forgot-password for an unknown user | Import users from a legacy directory on first login |
| **Custom message** | Before Cognito sends email/SMS | Customize/localize message copy |
| **Custom email/SMS sender** | Instead of Cognito sending | Send via your own provider (SES/Twilio); receives KMS-encrypted code |
| **Define auth challenge** | Custom (`CUSTOM_AUTH`) flow control | Decide the next challenge / when done |
| **Create auth challenge** | Custom flow | Produce the challenge (e.g. email a code) |
| **Verify auth challenge** | Custom flow | Grade the user's answer |
| **Pre sign-up (ExternalProvider)** / **Inbound federation** | First federated login | Transform IdP claims before creating the user |

`triggerSource` on the event tells you the exact cause (e.g. `PreSignUp_SignUp` vs `PreSignUp_AdminCreateUser` vs `PreSignUp_ExternalProvider`) — branch on it.

## Event shape

Common envelope (trigger-specific fields go under `request`/`response`):
```json
{
  "version": "1",
  "triggerSource": "PreSignUp_SignUp",
  "region": "us-east-1",
  "userPoolId": "us-east-1_EXAMPLE",
  "userName": "uuid-or-username",
  "callerContext": { "awsSdkVersion": "…", "clientId": "…" },
  "request": { "userAttributes": { "email": "a@b.com" } },
  "response": {}
}
```
Always **return the whole event**. Returning it unmodified = "proceed with default." Throwing an error aborts the operation (and, in managed login, shows your error text to the user — keep it user-safe; log secrets via `console.log`, not the thrown message).

## Recipes

### Pre sign-up — auto-confirm + auto-verify (skip email confirmation)
```js
export const handler = async (event) => {
  event.response.autoConfirmUser = true;
  if (event.request.userAttributes.email) event.response.autoVerifyEmail = true;
  // event.response.autoVerifyPhone = true;  // needs a valid non-null phone_number
  return event;
};
```
- Response flags `autoConfirmUser`/`autoVerifyEmail`/`autoVerifyPhone` are **ignored for the `PreSignUp_AdminCreateUser` source** — they only apply to self-signup/federated.
- `autoVerifyEmail`/`autoVerifyPhone` require a valid non-null `email`/`phone_number`, or sign-up errors out.
- **Alias-move risk:** if the verified attribute is a sign-in **alias** and another user already holds it, the alias **moves** to the new user and the old user's attribute is marked unverified. Check with `ListUsers` before auto-verifying to avoid account hijacking.
- Request also carries `validationData` and `clientMetadata` (see [Gotchas](#gotchas)).

### Pre sign-up — restrict to a domain
```js
export const handler = async (event) => {
  const email = event.request.userAttributes.email || "";
  if (!email.endsWith("@example.com")) throw new Error("Sign-up restricted to example.com");
  return event;
};
```

### Post confirmation — provision a user row
```js
import { DynamoDBClient, PutItemCommand } from "@aws-sdk/client-dynamodb";
const ddb = new DynamoDBClient({});
export const handler = async (event) => {
  if (event.triggerSource === "PostConfirmation_ConfirmSignUp") {
    await ddb.send(new PutItemCommand({
      TableName: "Users",
      Item: { sub: { S: event.request.userAttributes.sub },
              email: { S: event.request.userAttributes.email } },
    }));
  }
  return event;
};
```
- **Doesn't fire for admin-created users** — post confirmation runs on `ConfirmSignUp`/`AdminConfirmSignUp`/`ConfirmForgotPassword` (self-signup + managed login), **not** `AdminCreateUser`. Provision those users another way.
- Runs **after** the account is confirmed — an error here can't un-confirm the user, so make the work **idempotent** and non-blocking (a later retry re-runs it). No response fields are expected.

### Pre token generation — add a custom claim / group / scope
```js
export const handler = async (event) => {
  event.response = {
    claimsOverrideDetails: {
      claimsToAddOrOverride: { tenant_id: "acme", role: "editor" },
      claimsToSuppress: ["family_name"],
      groupOverrideDetails: { groupsToOverride: ["editors"] },
    },
  };
  return event;
};
```
Pre-token-generation **event versions** gate what you can customize (higher versions need Essentials/Plus):
- **V1_0** — ID-token claims/roles/groups only (all plans).
- **V2_0** — adds **access-token** claims, scopes, groups for **user** identities (Essentials/Plus); use `event.response.claimsAndScopeOverrideDetails`.
- **V3_0** — as V2 plus access-token customization for **machine (M2M) client-credentials** identities.

Downgrading below Essentials requires reverting an access-token trigger back to a `V1_0` (ID-token-only) trigger. V1 response = `claimsOverrideDetails`; V2/V3 response = `claimsAndScopeOverrideDetails` with `idTokenGeneration` + `accessTokenGeneration` sub-objects, each taking `claimsToAddOrOverride`/`claimsToSuppress` (access token also `scopesToAdd`/`scopesToSuppress`).

**Reserved claims you CAN'T add/modify/suppress:** `sub`, `iss`, `aud`*, `token_use`, `client_id`, `cognito:username`, `identities`, `device_key`, `event_id`, `acr`, `amr`, `auth_time`, `exp`, `iat`, `nbf`, `jti`, `origin_jti`, `nonce`, `azp`, `at_hash`, `version`, and any other `cognito:`-prefixed claim (only `cognito:groups`/`cognito:roles`/`cognito:preferred_role` are editable). `dev:` attributes can be suppressed but not added/modified. *You may add `aud` to an **access** token but the value must equal `event.callerContext.clientId`.
- **Suppress beats override** — if you both add and suppress a claim, it's suppressed.
- **`scopesToAdd` values can't contain spaces.**
- **`groupOverrideDetails`: an empty/null object suppresses `cognito:groups`.** To keep groups, copy `request.groupConfiguration` into the response. Groups are the only access-token change a V1 event can make.
- Complex claim values (array/JSON) need V2/V3; in the **ID token** they're not allowed for `phone_number_verified`, `email_verified`, `updated_at`, `address`.
- **Watch token size** — every added claim/scope enlarges the JWT (and counts toward the [5,000 combined claims+scopes limit](quotas.md#resource-limits)). Keep names short and namespace them to avoid collisions with reserved/OIDC claims, e.g. `company.app.role` rather than `role`.

### Migrate user — import from a legacy directory on first sign-in
```js
export const handler = async (event) => {
  if (event.triggerSource === "UserMigration_Authentication") {
    const ok = await legacyLogin(event.userName, event.request.password); // your check
    if (!ok) throw new Error("Bad credentials");
    event.response.userAttributes = { email: ok.email, email_verified: "true" };
    event.response.finalUserStatus = "CONFIRMED";
    event.response.messageAction = "SUPPRESS";
  }
  return event;
};
```
Requires the app client to allow `USER_PASSWORD_AUTH` (Cognito needs the plaintext password to verify against the legacy store). Not invoked for passwordless sign-in.
- **`finalUserStatus`:** `CONFIRMED` lets the user sign in with their existing password immediately; the default `RESET_REQUIRED` forces a reset (your client must handle `PasswordResetRequiredException`).
- **Cognito doesn't enforce your password policy during migration** — validate strength yourself and set `RESET_REQUIRED` if it fails.
- **Forgot-password flow** (`UserMigration_ForgotPassword`) sends **no `password`** — just look the user up and return `userAttributes` with a **verified** `email`/`phone_number` so the reset code can be delivered.
- Other response fields: `messageAction: SUPPRESS` (skip welcome message), `desiredDeliveryMediums` (`EMAIL`/`SMS`, default SMS), `forceAliasCreation` (steal an existing alias), `enableSMSMFA`.

### Pre authentication — deny a sign-in
```js
export const handler = async (event) => {
  if (event.callerContext.clientId === BLOCKED_CLIENT_ID) {
    throw new Error("Sign-in not allowed from this app client");
  }
  return event;               // response body is ignored; throw to deny
};
```
- **Does NOT fire for a nonexistent user** unless the app client has `PreventUserExistenceErrors: ENABLED` (then `event.request.userNotFound` is set). It also **doesn't fire on session renewal** (token refresh) — so it blocks only *new* sessions.
- `event.request.validationData` carries `ClientMetadata` from `InitiateAuth`/`AdminInitiateAuth`.

### Post authentication — log a successful sign-in
```js
export const handler = async (event) => {
  console.log("signin", { user: event.userName, client: event.callerContext.clientId,
                          newDevice: event.request.newDeviceUsed });
  return event;               // must return the event or auth fails to complete
};
```
- Runs after auth succeeds, before tokens are issued. `newDeviceUsed` is set only when remembered-devices is `Always` or `User Opt-In`.
- Here `clientMetadata` comes from `RespondToAuthChallenge` (**not** `InitiateAuth`).

### Inbound federation — transform IdP claims programmatically
The `InboundFederation_ExternalProvider` trigger fires before a federated user profile is created/updated (new **and** returning users) — a programmatic alternative to static [attribute mapping](federation.md#attribute-mapping). Map IdP groups into a Cognito custom attribute:
```js
export const handler = async (event) => {
  const { providerType, attributes } = event.request;
  const idp = providerType === "SAML"
    ? (attributes.samlResponse || {})
    : { ...(attributes.userInfo || {}), ...(attributes.idToken || {}) };  // OIDC/social

  const groups = (idp.groups || "").split(",").map(g => g.trim());
  event.response.userAttributesToMap = {
    ...idp,                                            // MUST re-include everything to keep
    "custom:user_groups": groups.filter(Boolean).join(","),
  };
  return event;
};
```
- `request.attributes` shape depends on `providerType` (`OIDC`/`SAML`/`Facebook`/`Google`/`SignInWithApple`/`LoginWithAmazon`): OIDC/social get `tokenResponse` + `idToken` + `userInfo`; SAML gets `samlResponse`.
- **`userAttributesToMap` is all-or-nothing:** any attribute you omit is **dropped**. Returning `{}` is a **no-op** (all original IdP attributes retained) — different from omitting them.
- Common uses: IdP-group → Cognito-group mapping, truncating attributes over the 2048-char limit, federation logging.
- **Account linking on every sign-in:** this trigger runs on **every** federated login, not just the first — so it's the right place to link a federated identity to an existing local account by matching a fresh IdP attribute (e.g. `email`). The **pre sign-up** trigger can only link at initial account creation.

### Custom auth (CUSTOM_AUTH) — define / create / verify

Three triggers cooperate to run a challenge sequence you design (CAPTCHA, magic link, security question, hardware token). SDK-only — **not available in managed login**. The client loops `InitiateAuth`(`CUSTOM_AUTH`) → `RespondToAuthChallenge` until tokens issue; each response carries a **new** `Session` id.

- **Define auth challenge** — the orchestrator. Reads `request.session` (chronological array of `ChallengeResult` = `{challengeName, challengeResult, challengeMetadata}`) and sets the response: `challengeName` (next step), `issueTokens`, or `failAuthentication`.
- **Create auth challenge** — produces the challenge: `response.publicChallengeParameters` (shown to the user) and `privateChallengeParameters` (the answer, passed only to verify).
- **Verify auth challenge response** — grades it: compare `request.challengeAnswer` to `privateChallengeParameters`, set `response.answerCorrect`.

```js
// define-auth-challenge: SRP password check, then two CUSTOM_CHALLENGEs, then tokens
export const handler = async (event) => {
  const s = event.request.session, r = event.response;
  const done = (i, name) => s.length === i && s[i-1].challengeName === name && s[i-1].challengeResult;
  if (s.length === 1 && s[0].challengeName === "SRP_A") { r.challengeName = "PASSWORD_VERIFIER"; }
  else if (done(2, "PASSWORD_VERIFIER")) { r.challengeName = "CUSTOM_CHALLENGE"; }
  else if (done(3, "CUSTOM_CHALLENGE")) { r.challengeName = "CUSTOM_CHALLENGE"; }
  else if (done(4, "CUSTOM_CHALLENGE")) { r.issueTokens = true; }
  else { r.failAuthentication = true; }
  return event;
};
```
```js
// create-auth-challenge: CAPTCHA (3rd challenge) then a security question (4th)
export const handler = async (event) => {
  if (event.request.challengeName !== "CUSTOM_CHALLENGE") return event;
  const r = event.response;
  if (event.request.session.length === 2) {           // right after PASSWORD_VERIFIER
    r.publicChallengeParameters = { captchaUrl: "url/123.jpg" };
    r.privateChallengeParameters = { answer: "5" };
  } else if (event.request.session.length === 3) {
    r.publicChallengeParameters = { securityQuestion: "Favorite mascot?" };
    r.privateChallengeParameters = { answer: "Peccy" };
  }
  return event;
};
```

Key rules:
- **`challengeName` values** you'll see in `session`: `SRP_A`, `PASSWORD_VERIFIER`, `CUSTOM_CHALLENGE`, `SMS_MFA`, `EMAIL_OTP`, `SOFTWARE_TOKEN_MFA`, `DEVICE_SRP_AUTH`, `DEVICE_PASSWORD_VERIFIER`, `NEW_PASSWORD_REQUIRED`, `ADMIN_NO_SRP_AUTH`.
- **Password-first is optional.** Start `InitiateAuth` with `AuthParameters.CHALLENGE_NAME: SRP_A` (+`SRP_A`,`USERNAME`) to verify the password before custom challenges, or with `CHALLENGE_NAME: CUSTOM_CHALLENGE` to go straight to your challenges (passwordless).
- **MFA auto-follows PASSWORD_VERIFIER.** If the user has MFA and you issue `PASSWORD_VERIFIER`, Cognito inserts an `SMS_MFA`/`EMAIL_OTP`/`SOFTWARE_TOKEN_MFA` challenge — handle those results in `session`, but you don't issue MFA yourself.
- **Always check `challengeName` before setting `issueTokens: true`** — issuing tokens on the wrong/failed challenge is a real vulnerability.
- **Password reset in-flow:** for `FORCE_CHANGE_PASSWORD`/`RESET_REQUIRED` users, Cognito adds a `NEW_PASSWORD_REQUIRED` challenge after `PASSWORD_VERIFIER`; the `session` grows accordingly.
- **`userNotFound`** appears (when `PreventUserExistenceErrors: ENABLED`) in define/create — keep behavior identical for missing users to avoid account enumeration.
- **Third-party / step-up MFA via redirect (Duo, Okta Verify, etc.):** custom auth is the way to bolt on an external MFA provider. In **create**, return the provider's **auth URL + a `state`** as `publicChallengeParameters`; the client stores its Cognito `Session` + `state` (e.g. localStorage), redirects the user to the provider, and on callback submits the provider's returned code as `challengeAnswer`. **Verify** exchanges that code with the provider's API (keys in **Secrets Manager**) and sets `answerCorrect`. This runs *after* `PASSWORD_VERIFIER`, giving you a fully custom second factor beyond Cognito's built-in SMS/email/TOTP.

### Custom message — reword the built-in emails/SMS
Rewrites the copy of Cognito's own messages (verification codes, MFA, temp passwords). Branch on `triggerSource` (`CustomMessage_SignUp`/`_ForgotPassword`/`_ResendCode`/`_UpdateUserAttribute`/`_VerifyUserAttribute`/`_Authentication`/`_AdminCreateUser`).
```js
export const handler = async (event) => {
  if (event.triggerSource === "CustomMessage_SignUp") {
    const code = event.request.codeParameter;            // placeholder, MUST appear in the message
    event.response.emailSubject = "Confirm your account";
    event.response.emailMessage = `Your code is <b>${code}</b>.`;   // HTML ok in email
    event.response.smsMessage   = `Your code is ${code}.`;
  }
  return event;
};
```
- **Must embed `codeParameter`** (rendered as `{####}`) or the user gets no code. For `CustomMessage_AdminCreateUser`, also embed `usernameParameter` (the message carries username **and** temp password).
- **`emailMessage`/`emailSubject` only work when the pool's `EmailSendingAccount` is `DEVELOPER` (Amazon SES).** With the default (`COGNITO_DEFAULT`), returning them throws `InvalidLambdaResponseException` (400) — you can still set `smsMessage`.
- Limits: email **20,000** UTF-8 chars, SMS **140** UTF-8 chars (code included).
- This trigger only rewords Cognito-sent messages — to send via your own provider, use custom sender (below).

### Custom email / SMS sender — deliver via your own provider
Replaces Cognito's SES/SNS delivery so you send through Twilio, a third-party SMTP relay, an SNS topic, etc. The code arrives **KMS-encrypted**; decrypt it with the **AWS Encryption SDK**. This also unlocks **alternative channels** — e.g. deliver the OTP over **WhatsApp** (AWS End User Messaging Social / WhatsApp Business API, with the WhatsApp token in Secrets Manager) instead of SMS, which sidesteps SMS-pumping cost ([security.md](security.md#network-protection-waf--sms-abuse)).
```js
import { KmsKeyringNode, buildClient, CommitmentPolicy } from "@aws-crypto/client-node";
const { decrypt } = buildClient(CommitmentPolicy.REQUIRE_ENCRYPT_ALLOW_DECRYPT);
const keyring = new KmsKeyringNode({ generatorKeyId: process.env.KEY_ID, keyIds: [process.env.KEY_ARN] });

export const handler = async (event) => {
  let code;
  if (event.request.code) {                              // event.request.type = customEmailSenderRequestV1 / customSMSSenderRequestV1
    const { plaintext } = await decrypt(keyring, Buffer.from(event.request.code, "base64"));
    code = Buffer.from(plaintext).toString("utf-8");
  }
  if (event.triggerSource === "CustomSMSSender_SignUp") {
    await myProvider.sendSms(event.request.userAttributes.phone_number, `Code: ${code}`);
  }
  // …branch other CustomEmailSender_* / CustomSMSSender_* sources
};
```
Setup (**API/CLI only — not the console**):
1. Create a **symmetric KMS key**; grant the pool admin `kms:CreateGrant` (condition `kms:EncryptionContext:userpool-id = <poolId>`) and the Lambda role `kms:Decrypt`.
2. `aws lambda add-permission … --principal cognito-idp.amazonaws.com --action lambda:InvokeFunction`.
3. `UpdateUserPool` with `LambdaConfig` containing `KMSKeyID` + `CustomEmailSender`/`CustomSMSSender` (`{LambdaArn, LambdaVersion: "V1_0"}`) **plus all your existing pool config** (UpdateUserPool resets omitted params).
- **Custom email sender only:** temp passwords arrive HTML-escaped (`<`→`&lt;`) — un-escape after decrypt before sending (codes aren't escaped). Email-only source `CustomEmailSender_AccountTakeOverNotification` sends no `clientMetadata`.

## Gotchas

- **5-second synchronous timeout**, unchangeable. Keep triggers fast; do slow work async elsewhere.
- **Adding a trigger outside the console** requires a Lambda resource-based policy allowing `cognito-idp.amazonaws.com` to invoke it (the console adds this automatically). Scope it with `aws:SourceArn` = your pool and `aws:SourceAccount`.
- **Custom sender triggers** get the OTP/code **KMS-encrypted** and are **API-only to configure** — see the [custom sender recipe](#custom-email--sms-sender--deliver-via-your-own-provider).
- **Federated sign-in** invokes only pre sign-up, post confirmation, pre auth, post auth, and pre token generation — not custom challenge, migrate, custom message, or custom sender.
- **Deleting a function** without clearing the trigger reference breaks the flow — unset the trigger too.
- Event schemas can gain fields; don't do strict input validation that breaks on unknown keys.
- **Error surfacing:** a thrown error blocks the operation. Managed login shows the error text above the sign-in prompt; the API returns `[trigger] failed with error [text]`. Only throw messages safe for users; log sensitive detail with `console.log`/`print` to CloudWatch.
- **No retry on 5xx.** An invoke error with HTTP 500-599 (config problem) is not retried; other retryable failures may be retried within the 5s window.
- **Pinning a version:** you can't set a function version in the trigger config (Cognito calls `$LATEST`). To pin, point the trigger `LambdaArn` at a **version alias ARN** — API/CloudFormation only, not the console.
- **Cross-account triggers** are allowed but must be added via API/CLI/CloudFormation (not the console), and you must add the invoke permission to the function's resource policy yourself.
- **`validationData` vs `clientMetadata`:** both pass extra data to triggers. `validationData` (from `SignUp`/`AdminCreateUser`) is **temporary** — not stored as user attributes — and reaches the **pre sign-up** trigger; `clientMetadata` (from many APIs' `ClientMetadata`) reaches most triggers. For pre-auth/migrate, a request's `ClientMetadata` arrives as `validationData`. For M2M, pass `aws_client_metadata=<url-encoded-json>` in the token-endpoint POST body to reach the pre-token-generation trigger.
