# Authentication — Save Login Once, Reuse Across Tests

Logging in inside every test is slow and flaky. Authenticate **once**, save the browser state, and
start every test already signed in.

## Contents
- [storageState concept](#storagestate-concept)
- [Recommended: setup project with dependencies](#recommended-setup-project-with-dependencies)
- [Multiple roles / accounts](#multiple-roles--accounts)
- [Per-worker authentication](#per-worker-authentication)
- [API-based authentication](#api-based-authentication)
- [Session storage](#session-storage)
- [Passkeys (WebAuthn)](#passkeys-webauthn)
- [Skipping auth for specific tests](#skipping-auth-for-specific-tests)
- [Pitfalls](#pitfalls)
- [Security](#security)

## storageState concept

`storageState` captures **cookies, localStorage, and IndexedDB** — everything needed to stay signed
in. Save it once, then bootstrap tests with it instead of re-logging in.

```bash
mkdir -p playwright/.auth
echo $'\nplaywright/.auth' >> .gitignore   # never commit session secrets
```

## Recommended: setup project with dependencies

A dedicated **setup project** signs in before the test projects run, and the test projects declare a
`dependencies: ['setup']` plus `storageState` pointing at the saved file.

**`tests/auth.setup.ts`:**
```typescript
import { test as setup, expect } from '@playwright/test';
import path from 'path';

const authFile = path.join(__dirname, '../playwright/.auth/user.json');

setup('authenticate', async ({ page }) => {
  // Perform authentication steps. Replace with your app's login.
  await page.goto('https://github.com/login');
  await page.getByLabel('Username or email address').fill('username');
  await page.getByLabel('Password').fill('password');
  await page.getByRole('button', { name: 'Sign in' }).click();

  // Wait until login is fully complete (cookies set / authed UI visible).
  await page.waitForURL('https://github.com/');
  await expect(page.getByRole('button', { name: 'View profile and more' })).toBeVisible();

  // Persist signed-in state to disk.
  await page.context().storageState({ path: authFile });
});
```

**`playwright.config.ts`:**
```typescript
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  projects: [
    { name: 'setup', testMatch: /.*\.setup\.ts/ },
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'], storageState: 'playwright/.auth/user.json' },
      dependencies: ['setup'],
    },
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'], storageState: 'playwright/.auth/user.json' },
      dependencies: ['setup'],
    },
  ],
});
```

**Tests then start authenticated, with zero login code:**
```typescript
import { test } from '@playwright/test';

test('test', async ({ page }) => {
  // page is already signed in
});
```

## Multiple roles / accounts

Authenticate each role in the setup project, saving to separate files:

```typescript
// tests/auth.setup.ts
import { test as setup, expect } from '@playwright/test';

const adminFile = 'playwright/.auth/admin.json';
setup('authenticate as admin', async ({ page }) => {
  await page.goto('https://github.com/login');
  await page.getByLabel('Username or email address').fill('admin');
  await page.getByLabel('Password').fill('password');
  await page.getByRole('button', { name: 'Sign in' }).click();
  await page.waitForURL('https://github.com/');
  await page.context().storageState({ path: adminFile });
});

const userFile = 'playwright/.auth/user.json';
setup('authenticate as user', async ({ page }) => {
  await page.goto('https://github.com/login');
  await page.getByLabel('Username or email address').fill('user');
  await page.getByLabel('Password').fill('password');
  await page.getByRole('button', { name: 'Sign in' }).click();
  await page.waitForURL('https://github.com/');
  await page.context().storageState({ path: userFile });
});
```

Select a role per test/describe with `test.use()`:
```typescript
import { test } from '@playwright/test';

test.use({ storageState: 'playwright/.auth/admin.json' });
test('admin test', async ({ page }) => { /* signed in as admin */ });

test.describe(() => {
  test.use({ storageState: 'playwright/.auth/user.json' });
  test('user test', async ({ page }) => { /* signed in as user */ });
});
```

Two roles in **one** test — open two contexts:
```typescript
test('admin and user', async ({ browser }) => {
  const adminContext = await browser.newContext({ storageState: 'playwright/.auth/admin.json' });
  const adminPage = await adminContext.newPage();
  const userContext = await browser.newContext({ storageState: 'playwright/.auth/user.json' });
  const userPage = await userContext.newPage();
  // ... interact with both ...
  await adminContext.close();
  await userContext.close();
});
```

For ergonomics, wrap each role in a **fixture** — see
[fixtures.md](fixtures.md#page-objects-as-fixtures).

## Per-worker authentication

When tests **mutate shared server state**, give each parallel worker its own account via a
worker-scoped fixture that authenticates once per worker and reuses the file:

```typescript
// playwright/fixtures.ts
import { test as baseTest, expect } from '@playwright/test';
import fs from 'fs';
import path from 'path';
export * from '@playwright/test';

export const test = baseTest.extend<{}, { workerStorageState: string }>({
  storageState: ({ workerStorageState }, use) => use(workerStorageState),

  workerStorageState: [async ({ browser }, use) => {
    const id = test.info().parallelIndex;   // unique per worker
    const fileName = path.resolve(test.info().project.outputDir, `.auth/${id}.json`);

    if (fs.existsSync(fileName)) {           // reuse if already authed
      await use(fileName);
      return;
    }

    // Authenticate in a clean context (no inherited state).
    const page = await browser.newPage({ storageState: undefined });
    const account = await acquireAccount(id);
    await page.goto('https://github.com/login');
    await page.getByLabel('Username or email address').fill(account.username);
    await page.getByLabel('Password').fill(account.password);
    await page.getByRole('button', { name: 'Sign in' }).click();
    await page.waitForURL('https://github.com/');
    await page.context().storageState({ path: fileName });
    await page.close();
    await use(fileName);
  }, { scope: 'worker' }],
});
```

## API-based authentication

If the app supports it, log in via an HTTP request — faster than driving the UI:

```typescript
import { test as setup } from '@playwright/test';

const authFile = 'playwright/.auth/user.json';
setup('authenticate', async ({ request }) => {
  await request.post('https://github.com/login', {
    form: { user: 'user', password: 'password' },
  });
  await request.storageState({ path: authFile });
});
```

## Session storage

`sessionStorage` is **not** captured by `storageState`. Save/restore it manually only if your app
needs it:

```typescript
// save
const sessionStorage = await page.evaluate(() => JSON.stringify(sessionStorage));
fs.writeFileSync('playwright/.auth/session.json', sessionStorage, 'utf-8');

// restore into a new context
const stored = JSON.parse(fs.readFileSync('playwright/.auth/session.json', 'utf-8'));
await context.addInitScript(storage => {
  if (window.location.hostname === 'example.com')
    for (const [k, v] of Object.entries(storage)) window.sessionStorage.setItem(k, v as string);
}, stored);
```

**Web Storage API (v1.61+):** for *runtime* read/write of a live page's storage (not disk
persistence), use the typed `page.localStorage` / `page.sessionStorage` interface instead of
`page.evaluate`:

```typescript
await page.goto('https://example.com');
await page.localStorage.setItem('token', 'abc');
const token = await page.localStorage.getItem('token');   // Promise<string | null>
const all = await page.localStorage.items();              // [{ name, value }, ...]
await page.sessionStorage.removeItem('flag');
await page.sessionStorage.clear();
```

To persist session storage across contexts you still need the save/load snippet above —
`page.sessionStorage` only reaches the current live page's origin.

## Passkeys (WebAuthn)

`browserContext.credentials` is a **virtual WebAuthn authenticator** (v1.61+), letting tests register
and use passkeys without real hardware keys, across all browsers. It overrides
`navigator.credentials.create()` / `navigator.credentials.get()`.

```typescript
// Seed a credential (auto-generates an ECDSA P-256 keypair if not provided), then install.
await context.credentials.create('example.com', {
  id: process.env.PASSKEY_ID,
  userHandle: process.env.PASSKEY_USER_HANDLE,
  privateKey: process.env.PASSKEY_PRIVATE_KEY,
  publicKey: process.env.PASSKEY_PUBLIC_KEY,
});
await context.credentials.install();   // must run before the page touches navigator.credentials

// Drive the passkey login UI as normal, then capture any newly registered credential:
const creds = await context.credentials.get({ rpId: 'example.com' });
// ...persist creds to disk / env to reuse on later runs; delete with context.credentials.delete(id)
```

Because credentials are **not** part of `storageState`, the canonical way to apply them to every test
is a **context fixture override** that seeds + installs before the page loads.

```typescript
// Option 1 — backend-provisioned passkey (key material from env/secret)
export const test = baseTest.extend({
  context: async ({ context }, use) => {
    await context.credentials.create('example.com', {
      id: process.env.PASSKEY_ID,
      userHandle: process.env.PASSKEY_USER_HANDLE,
      privateKey: process.env.PASSKEY_PRIVATE_KEY,
      publicKey: process.env.PASSKEY_PUBLIC_KEY,
    });
    await context.credentials.install();
    await use(context);
  },
});
```

```typescript
// Option 2 — register once in a setup project, persist, then seed via the fixture
// tests/passkey.setup.ts
setup('enroll passkey', async ({ context, page }) => {
  await context.credentials.install();
  await page.goto('https://example.com/register');
  await page.getByRole('button', { name: 'Create a passkey' }).click();
  const [credential] = await context.credentials.get({ rpId: 'example.com' });
  fs.writeFileSync('playwright/.auth/passkey.json', JSON.stringify(credential));
});
```
```typescript
// fixture seeds the saved credential into every context
export const test = baseTest.extend({
  context: async ({ context }, use) => {
    const credential = JSON.parse(fs.readFileSync('playwright/.auth/passkey.json', 'utf8'));
    await context.credentials.create(credential.rpId, credential);
    await context.credentials.install();
    await use(context);
  },
});
```

`passkey.json` holds a private key — keep it in `playwright/.auth` and out of source control.

## Skipping auth for specific tests

Reset state to test the logged-out experience:
```typescript
import { test } from '@playwright/test';

test.use({ storageState: { cookies: [], origins: [] } });
test('not signed in', async ({ page }) => { /* ... */ });
```

## Pitfalls

- **Expiry** — saved sessions eventually expire. Delete the state file to force re-auth, or write it
  into `testProject.outputDir` (cleared before every run) so each run re-authenticates. The
  [per-worker fixture](#per-worker-authentication) already uses `outputDir`.
- **UI Mode** — setup projects don't run by default in UI mode (for speed). Trigger `auth.setup.ts`
  manually when the stored session expires.
- **Shared account** — the single-account setup only works if tests **don't** mutate shared
  server-side state; otherwise use [per-worker authentication](#per-worker-authentication).

## Security

The state file holds **live session cookies/tokens** that can impersonate the account. Always keep
it under `playwright/.auth/` and add that directory to `.gitignore`. Use throwaway test accounts.
