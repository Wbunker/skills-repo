# AWS Amplify — Capabilities Reference

For CLI commands, see [amplify-cli.md](amplify-cli.md).

## AWS Amplify Hosting

**Purpose**: Fully managed CI/CD and hosting platform for full-stack web applications. Deploy directly from Git with automatic builds, previews, and global CDN distribution.

### Supported Frameworks

| Category | Frameworks |
|---|---|
| **SSG / CSR** | React, Vue, Angular, Svelte, plain HTML/JS, Gatsby, Hugo, Eleventy, Jekyll |
| **SSR (server-side rendering)** | Next.js (App Router + Pages Router), Nuxt, SvelteKit, Astro (SSR mode) |
| **Monorepos** | Turborepo, Nx — configure `appRoot` in `amplify.yml` to point at the sub-app |

### Git-Based Deployments

| Feature | Description |
|---|---|
| **Branch deployments** | Each Git branch gets its own deployed URL; push to trigger build |
| **PR previews** | Pull request opens → Amplify builds a temporary preview URL automatically |
| **Branch auto-delete** | Delete the Git branch → Amplify deletes the deployed branch environment |
| **Manual deploys** | Upload a ZIP via console or CLI for non-Git workflows |

### Build Configuration (`amplify.yml`)

`amplify.yml` placed at the repository root controls the build pipeline:

```yaml
version: 1
frontend:
  phases:
    preBuild:
      commands:
        - npm ci
    build:
      commands:
        - npm run build
  artifacts:
    baseDirectory: .next  # or dist / build / out depending on framework
    files:
      - '**/*'
  cache:
    paths:
      - node_modules/**/*
```

Key `amplify.yml` options:
- `appRoot` — sub-directory for monorepo app
- `env` — environment variable overrides per branch
- Multiple frontend/backend phases (`preBuild`, `build`, `postBuild`)
- `testPhase` — run tests during build; fail build on test failure

### Custom Domains & HTTPS

- Connect an Amazon Route 53 domain or external registrar domain
- Amplify provisions and auto-renews ACM TLS certificates
- Subdomains can be mapped to specific branches (e.g., `staging.example.com` → staging branch)
- Wildcard subdomains supported for feature branch deployments

### Redirects & Rewrites

Configured in the Amplify console or `amplify.yml`. Common use cases:

| Rule type | Example |
|---|---|
| **SPA fallback** | `/<*>` → `/index.html` (200) — required for React Router, Vue Router |
| **Redirect** | `/old-path` → `/new-path` (301 or 302) |
| **Rewrite (proxy)** | `/api/<*>` → `https://api.example.com/<*>` (200) |
| **Custom 404** | `/<*>` → `/404.html` (404) |

### Server-Side Rendering (SSR)

- Amplify detects Next.js / Nuxt SSR apps automatically
- SSR functions run on AWS-managed compute (not Lambda directly; Amplify manages the infrastructure)
- **Edge SSR**: Next.js Middleware and Edge runtime are supported; runs at CloudFront edge locations
- No additional configuration needed — Amplify interprets `next.config.js` to determine rendering mode

### Access Controls & Security

| Feature | Description |
|---|---|
| **Password protection** | HTTP Basic Auth per branch; useful for staging environments |
| **IP allow-listing** | Restrict access to specific CIDR ranges per branch |
| **Access logs** | S3 access log delivery; CloudWatch metrics for request counts, latency, data transfer |

### Environment Variables

- Set per app or per branch; branch-level overrides app-level
- Mark variables as secret (stored in Secrets Manager; not visible in console after save)
- Variables injected into build environment and runtime (for SSR apps)

---

## AWS Amplify Gen 2 (Code-First DX)

**Purpose**: TypeScript-first, code-driven approach to building full-stack cloud applications on AWS. Backend resources (auth, data, storage, functions) are defined in TypeScript alongside the frontend code.

### Core Philosophy

| Gen 1 (CLI-based) | Gen 2 (Code-first) |
|---|---|
| `amplify push` to deploy | Git-based or `npx ampx sandbox` for personal cloud sandbox |
| JSON/YAML config in `amplify/` folder | TypeScript definitions in `amplify/` folder |
| Shared team environment | Each developer gets isolated personal sandbox |
| Amplify CLI (`amplify` command) | Amplify CLI Gen 2 (`npx ampx` command) |

### Project Structure

```
amplify/
  auth/
    resource.ts        # Cognito User Pool / Identity Pool config
  data/
    resource.ts        # AppSync API + DynamoDB schema
  storage/
    resource.ts        # S3 bucket config
  functions/
    myFunction/
      handler.ts       # Lambda handler
      resource.ts      # Lambda config
  backend.ts           # Root: combines all backend resources
  tsconfig.json
```

### Amplify Data (AppSync + DynamoDB)

Define your schema in TypeScript using the `a.schema()` builder:

```typescript
// amplify/data/resource.ts
import { a, defineData, ClientSchema } from '@aws-amplify/backend';

const schema = a.schema({
  Todo: a.model({
    content: a.string(),
    done: a.boolean(),
  }).authorization(allow => [allow.owner()]),
});

export type Schema = ClientSchema<typeof schema>;
export const data = defineData({ schema });
```

- Generates AppSync GraphQL API + DynamoDB tables automatically
- Type-safe client: `client.models.Todo.list()` — no manual query writing
- Supports custom queries/mutations/subscriptions, custom resolvers, relationships

### Amplify Auth (Cognito)

```typescript
// amplify/auth/resource.ts
import { defineAuth } from '@aws-amplify/backend';

export const auth = defineAuth({
  loginWith: {
    email: true,
    phone: true,
    externalProviders: {
      google: { clientId: secret('GOOGLE_CLIENT_ID'), clientSecret: secret('GOOGLE_CLIENT_SECRET') },
      callbackUrls: ['https://myapp.com/callback'],
    },
  },
  multifactor: { mode: 'OPTIONAL', totp: true },
  userAttributes: { birthdate: { required: false } },
});
```

Capabilities:
- User Pool: sign-up, sign-in, MFA (TOTP, SMS), email/phone verification, password policies
- Identity Pool: vend AWS credentials to authenticated/unauthenticated users
- Social providers: Google, Facebook, Apple, OIDC, SAML
- Custom auth flows via Lambda triggers (pre-sign-up, post-confirmation, custom challenge, etc.)

### Amplify Storage (S3)

```typescript
// amplify/storage/resource.ts
import { defineStorage } from '@aws-amplify/backend';

export const storage = defineStorage({
  name: 'myProjectFiles',
  access: (allow) => ({
    'public/*': [allow.guest.to(['read']), allow.authenticated.to(['read','write','delete'])],
    'protected/{entity_id}/*': [allow.authenticated.to(['read']), allow.entity('identity').to(['read','write','delete'])],
    'private/{entity_id}/*': [allow.entity('identity').to(['read','write','delete'])],
  }),
});
```

- Fine-grained path-based access rules
- Integrates with Amplify Auth for per-user prefixes
- Client library: `uploadData`, `downloadData`, `list`, `remove`, `getUrl`, `copy`

### Amplify Functions (Lambda)

```typescript
// amplify/functions/myFunction/resource.ts
import { defineFunction } from '@aws-amplify/backend';

export const myFunction = defineFunction({
  name: 'my-function',
  entry: './handler.ts',
  environment: { TABLE_NAME: 'my-table' },
  timeoutSeconds: 30,
});
```

- Write Lambda handlers in TypeScript; Amplify compiles and packages automatically
- Functions can be used as custom resolvers in Amplify Data, as Auth triggers, or standalone
- Access other Amplify resources (data, auth, storage) with generated environment variables

### Sandbox Environments

- `npx ampx sandbox` — deploys a personal cloud sandbox to your AWS account
- Each developer has an isolated backend; no shared dev environment conflicts
- `npx ampx sandbox --once` — deploy once without file watching
- `npx ampx generate outputs` — regenerate `amplify_outputs.json` after manual changes

### Git-Based Full-Stack Deployments

- Connect repository to Amplify Hosting; Gen 2 backend + frontend deployed together on each push
- Branch environments: `main` → production, `develop` → staging, feature branches → preview environments
- `amplify_outputs.json` is generated by Amplify during build and injected into the frontend bundle automatically

---

## Amplify Studio

**Purpose**: Visual development environment integrated with Amplify Gen 2. Build UI components, manage content, and design forms without writing backend code.

| Feature | Description |
|---|---|
| **Component builder** | Drag-and-drop UI component editor; generates React code |
| **Figma import** | Import Figma designs; Amplify maps them to React components with binding |
| **Form builder** | Auto-generate forms from your data model; validation, custom fields |
| **Content management** | CMS-style data management UI for non-developers to edit DynamoDB records |

---

## Amplify Libraries

Client-side libraries for connecting frontend/mobile apps to Amplify backend resources.

| Platform | Package |
|---|---|
| **JavaScript / TypeScript** | `aws-amplify` (works with React, Vue, Angular, Next.js, plain JS) |
| **React (UI components)** | `@aws-amplify/ui-react` — Authenticator, FileUploader, StorageImage, etc. |
| **iOS (Swift)** | `Amplify` Swift package |
| **Android (Kotlin/Java)** | `aws-amplify-android` |
| **Flutter** | `amplify_flutter` |

### Library Category Overview

| Category | Description |
|---|---|
| **Auth** | `signIn`, `signUp`, `signOut`, `confirmSignUp`, `fetchAuthSession`, `getCurrentUser`, social sign-in, MFA |
| **API (GraphQL)** | `generateClient()` for type-safe Gen 2 queries; `client.models.X.create/list/get/update/delete`, subscriptions |
| **API (REST)** | `get`, `post`, `put`, `patch`, `del` against API Gateway / App Runner / custom endpoints |
| **Storage** | `uploadData`, `downloadData`, `list`, `remove`, `getUrl`, `copy` with access level control |
| **Analytics** | Record events to Amazon Pinpoint; auto-session tracking, attribute enrichment |
| **Predictions** | Text recognition, entity detection, text translation, speech-to-text via Amazon AI services |
| **Geo** | Map rendering (MapLibre GL), location search, geofencing via Amazon Location Service |
| **Notifications** | In-app messaging and push notifications via Pinpoint |
