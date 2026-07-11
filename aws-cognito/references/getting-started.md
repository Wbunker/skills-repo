# Getting Started (Console) & Example Apps

The fastest first path: let the Amazon Cognito console create a user pool + app client from an application template, then move the finalized design to IaC ([iac.md](iac.md)) for production. This file covers the console flow, the decisions that are **permanent**, and the official runnable example apps.

## Table of Contents
1. [Console quick path](#console-quick-path)
2. [Application types](#application-types)
3. [Decisions you can't undo](#decisions-you-cant-undo)
4. [Official example apps](#official-example-apps)
5. [Minimal SDK sign-up/in](#minimal-sdk-sign-upin)

---

## Console quick path

IAM permission needed: the `AmazonCognitoPowerUser` managed policy is enough to create/manage pools.

1. Cognito console → **Create user pool** (or "Get started for free").
2. **Define your application** → choose an **Application type** (below).
3. **Name your application.**
4. **Configure options** (some are permanent — see [below](#decisions-you-cant-undo)):
   - **Sign-in identifiers**: username, email, phone, or a combination.
   - **Required attributes for sign-up**: what to collect at registration. Sign-in identifier drives the minimum (email sign-in ⇒ email required, so reset codes can be delivered).
5. **Add a return URL** (callback), e.g. `https://localhost:3000/callback` — a route in your app that runs OIDC libraries to process the result.
6. **Create** → Cognito provisions a pool + app client + a domain with template defaults.
7. **Set up your application** page gives copy-paste code for your platform; **Go to overview** to explore.
8. Add more apps later via **App clients**; add federation/MFA anytime after creation.

The console auto-creates a **domain**; if you're doing SDK-only auth you can delete it from the **Domain** tab.

## Application types

The template picks sensible defaults (client type, auth flows, whether a secret is generated):

| Type | Client | Secret | Typical flow |
|---|---|---|---|
| **Single-page application (SPA)** | Public | No | Managed login / OAuth code + PKCE |
| **Traditional web application** | Confidential | **Yes** | OAuth code + client secret |
| **Mobile app** | Public | No | SDK or managed login |
| **Machine-to-machine** | Confidential | **Yes** | `client_credentials` grant |

**Confidential** = runs on a server, can hold a secret (⇒ `SECRET_HASH` required). **Public** = SPA/mobile, no secret. Choosing M2M or Traditional web is the console way to get a client secret; SPA/Mobile give a secret-less public client.

## Decisions you can't undo

Set these correctly at creation — changing them later means creating a **new** pool (and migrating users). The console can't reverse them; some are only settable via SDK/IaC at creation:

| Setting | Locked behavior | Only changeable by |
|---|---|---|
| **Sign-in identifiers** (`UsernameAttributes`) | email/phone/username sign-in | new pool |
| **Client secret** | secret hash required on auth calls | new app client (pick Traditional-web/M2M) |
| **Username case sensitivity** | console defaults to **case-insensitive** (`JohnD` == `johnd`) | create pool via **SDK/IaC** (`UsernameConfiguration`) |
| **`preferred_username` as alias** | console pools **don't** accept it as an alias | create pool via **SDK/IaC** |
| **Required attributes** | required-at-signup set | new pool |
| **Custom attributes** | can add, never delete/rename; mutability fixed | — |
| **SMS messaging** | once **activated it can't be deactivated** (individual SMS uses — MFA/verification/invitation — stay toggleable) | new pool |

The pool **name** is *not* on this list anymore — it used to be immutable but is now editable. If you need case-sensitive usernames or `preferred_username` aliasing, you **must** create the pool programmatically — the console can't. See [cli-commands.md](cli-commands.md) / [iac.md](iac.md).

**Editing an existing pool/client via SDK/CLI/IaC is itself a trap:** `UpdateUserPool`/`UpdateUserPoolClient` reset every omitted parameter to its default (wiping triggers, schema, message config). Always read-modify-write the full config — see [app-clients.md](app-clients.md#updating-clients--pools-safely).

## Official example apps

AWS maintains runnable references (good starting points to copy):

- **React SPA** (AWS SDK v3, no Amplify) — [aws-doc-sdk-examples / cognito-developer-guide-react-example](https://github.com/awsdocs/aws-doc-sdk-examples/tree/main/javascriptv3/example_code/cognito-identity-provider/scenarios/cognito-developer-guide-react-example). Vite + `react-ts`; edit `src/config.json` with region/userPoolId/clientId; requires a public client with `ALLOW_USER_PASSWORD_AUTH`, email sign-in, optional MFA, self-registration on. `npm install && npm run dev` → `http://localhost:5173`.
- **Flutter / Android** — [aws-doc-sdk-examples / cognito_flutter_mobile_app](https://github.com/awsdocs/aws-doc-sdk-examples/tree/main/kotlin/usecases/cognito_flutter_mobile_app). Uses `amazon_cognito_identity_dart_2` + `flutter_secure_storage`; put IDs in `assets/config.json`. See [flutter-amplify.md](flutter-amplify.md) for the Amplify path.
- **Node OIDC (managed login)** — the console's NodeJS template uses the [`openid-client`](https://www.npmjs.com/package/openid-client) npm library to redeem the auth code at `/callback` and fetch user info.

Example-app pool requirements (common to the React & Flutter samples): **email** sign-in, case-insensitive usernames, **optional** MFA, verify email, **email** the only required attribute, self-registration **enabled**, public client with `ALLOW_USER_PASSWORD_AUTH`.

## Minimal SDK sign-up/in

The smallest local-user flow with the AWS SDK (no Amplify) — full flows in [auth-flows.md](auth-flows.md), frontend patterns in [web-frontend.md](web-frontend.md):

```js
import {
  CognitoIdentityProviderClient, SignUpCommand,
  ConfirmSignUpCommand, InitiateAuthCommand,
} from "@aws-sdk/client-cognito-identity-provider";

const c = new CognitoIdentityProviderClient({ region: "us-east-1" });
const ClientId = "1example23456789";           // public client, no secret

await c.send(new SignUpCommand({ ClientId, Username: email, Password: pw,
  UserAttributes: [{ Name: "email", Value: email }] }));
// user gets an emailed code:
await c.send(new ConfirmSignUpCommand({ ClientId, Username: email, ConfirmationCode: code }));
const { AuthenticationResult } = await c.send(new InitiateAuthCommand({
  ClientId, AuthFlow: "USER_PASSWORD_AUTH",
  AuthParameters: { USERNAME: email, PASSWORD: pw },
}));
// AuthenticationResult.{IdToken, AccessToken, RefreshToken}
```
