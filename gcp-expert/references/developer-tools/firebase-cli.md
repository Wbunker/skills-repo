# Firebase — CLI

## Table of Contents
1. [Installation and Authentication](#installation-and-authentication)
2. [Project Setup and Initialization](#project-setup-and-initialization)
3. [Deployment](#deployment)
4. [Firebase Hosting](#firebase-hosting)
5. [Firebase Functions](#firebase-functions)
6. [Functions: Secrets CLI](#functions-secrets-cli)
7. [Functions: Secrets & Parameters (2nd Gen)](#functions-secrets--parameters-2nd-gen)
8. [Firebase Emulators](#firebase-emulators)
9. [Realtime Database CLI](#realtime-database-cli)
10. [Firestore CLI](#firestore-cli)
11. [Firestore Rules Deployment](#firestore-rules-deployment)
12. [Remote Config CLI](#remote-config-cli)
13. [App Distribution](#app-distribution)
14. [App Management](#app-management)
15. [Extensions](#extensions)
16. [Multi-Site Hosting](#multi-site-hosting)
17. [firebase.json Reference](#firebasejson-reference)
18. [CI/CD Patterns](#cicd-patterns)
19. [Global Flags Reference](#global-flags-reference)
20. [Functions Logs](#functions-logs)
21. [Firebase Admin SDK Examples](#firebase-admin-sdk-examples-nodejs)

---

## Firebase CLI Installation and Authentication

```bash
# Install via npm (recommended)
npm install -g firebase-tools

# Standalone binary (no Node.js required)
curl -sL https://firebase.tools | bash

# Update
npm update -g firebase-tools

# Verify
firebase --version

# Login (opens browser for OAuth)
firebase login

# Login on SSH/remote/headless — prints URL, accepts pasted code
firebase login --no-localhost

# Generate a CI token (deprecated — prefer service account)
firebase login:ci

# Authorize an additional Google account
firebase login:add

# Set default account for current project directory
firebase login:use user@example.com

# List all authorized accounts
firebase login:list

# Logout
firebase logout
```

### Authentication priority order (highest wins)

1. `GOOGLE_APPLICATION_CREDENTIALS` env var (service account JSON key)
2. `firebase login` stored credentials
3. Application Default Credentials (`gcloud auth application-default login`)
4. `--token` flag / `FIREBASE_TOKEN` env var (deprecated)

```bash
# Service account auth (preferred for CI)
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account-key.json
firebase deploy

# Per-command account override
firebase deploy --account user@example.com

# List projects
firebase projects:list
```

---

## Project Setup and Initialization

```bash
# Initialize Firebase in a directory (interactive wizard)
# Prompts to select features: Hosting, Firestore, Functions, Storage, etc.
firebase init

# Initialize specific features only
firebase init hosting
firebase init firestore
firebase init functions
firebase init storage
firebase init emulators
firebase init remoteconfig
firebase init extensions
firebase init dataconnect    # Firebase Data Connect (SQL-based)
firebase init apphosting     # Firebase App Hosting (Next.js / Angular SSR)

# Associate directory with a specific Firebase project
firebase use my-project-id

# Add a project alias
firebase use --add
# Prompts to select project and set an alias (e.g., "staging")

# Switch between project aliases
firebase use staging
firebase use production

# Show all configured project aliases
firebase use --list

# Set alias directly (no interactive prompt)
firebase use --alias staging my-project-staging

# Remove an alias
firebase use --unalias staging

# Clear active project selection
firebase use --clear

# Create a new Firebase project
firebase projects:create my-new-project --display-name "My New Project"

# Add Firebase to an existing GCP project
firebase projects:addfirebase existing-gcp-project-id
```

---

## Deployment

```bash
# Deploy all Firebase features configured in firebase.json
firebase deploy

# Deploy with a message (description for the release)
firebase deploy --message "v2.3.0 release - new checkout flow"

# Deploy only Firebase Hosting
firebase deploy --only hosting

# Deploy only Cloud Functions
firebase deploy --only functions

# Deploy only specific functions
firebase deploy --only functions:onUserCreated,functions:sendNotification

# Deploy all functions in a named codebase
firebase deploy --only functions:codebase:myCodebase

# Delete Cloud Functions removed from code (without confirmation prompt)
firebase deploy --only functions --force

# Deploy only Firestore rules and indexes
firebase deploy --only firestore
firebase deploy --only firestore:rules
firebase deploy --only firestore:indexes

# Deploy only Cloud Storage rules
firebase deploy --only storage

# Deploy only Realtime Database rules
firebase deploy --only database

# Deploy hosting and functions together
firebase deploy --only hosting,functions

# Skip prompts (for CI/CD)
firebase deploy --non-interactive

# Dry run (validate without deploying)
firebase deploy --only hosting --dry-run
```

---

## Firebase Hosting

```bash
# Serve hosting locally
firebase serve
firebase serve --only hosting
firebase serve --port 3000
firebase serve --host 0.0.0.0    # expose on all interfaces (e.g., for Docker)

# Disable hosting (takes site offline)
firebase hosting:disable
firebase hosting:disable --site my-site-id

# Create a preview channel (temporary URL for testing)
firebase hosting:channel:deploy preview-v2 \
  --expires 7d

# Create PR preview channel (commonly used in CI)
firebase hosting:channel:deploy pr-$PR_NUMBER \
  --expires 14d

# List all preview channels
firebase hosting:channel:list

# Describe a channel (get URL)
firebase hosting:channel:open preview-v2

# Delete a preview channel
firebase hosting:channel:delete preview-v2

# Delete all expired channels
firebase hosting:channel:delete --all-expired

# List hosting releases (versions)
firebase hosting:releases:list

# Roll back to a previous release
firebase hosting:rollback

# Clone hosting from one site to another
firebase hosting:clone SOURCE_SITE:CHANNEL DEST_SITE:CHANNEL

# Add a Firebase Hosting site (for multi-site hosting in one project)
firebase hosting:sites:create my-second-site
firebase hosting:sites:list
```

---

## Firebase Functions

```bash
# List deployed functions
firebase functions:list

# Delete a function (use when removing a function from code)
firebase functions:delete onUserCreated
firebase functions:delete onUserCreated --region=us-central1

# Set a function configuration value
firebase functions:config:set myapp.api_key="abc123"
firebase functions:config:set stripe.secret_key="sk_live_..."

# Get all function configuration
firebase functions:config:get

# Get specific config value
firebase functions:config:get myapp.api_key

# Unset a function configuration value
firebase functions:config:unset myapp.api_key

# Export function config to .runtimeconfig.json (for emulator use)
firebase functions:config:export

# Shell for interactive function testing
firebase functions:shell
firebase functions:shell --inspect-functions        # attach Node debugger on port 9229
firebase functions:shell --inspect-functions 9230   # custom debugger port

# In the shell, call a function:
# > myFunction({data: 'value'})
# > httpFunction.get('/path')

# Run a function locally (for HTTP functions)
firebase emulators:start --only functions
```

---

## Firebase Emulators

The Firebase Local Emulator Suite allows running Firebase services locally for development and testing.

```bash
# Start all configured emulators
firebase emulators:start

# Start specific emulators
firebase emulators:start --only hosting,functions,firestore

# Start emulators and import seed data
firebase emulators:start --import=./firebase-seed-data

# Start emulators and export data on exit
firebase emulators:start \
  --import=./firebase-seed-data \
  --export-on-exit=./firebase-seed-data

# Attach Node.js debugger to emulated functions
firebase emulators:start --inspect-functions
firebase emulators:start --inspect-functions 9230  # custom port

# Log verbosity
firebase emulators:start --log-verbosity DEBUG    # DEBUG | INFO | QUIET | SILENT

# Start emulators in the background (for CI)
firebase emulators:start --only firestore,functions &

# Run tests with emulators (starts emulators, runs command, exits)
firebase emulators:exec "npm test" --only firestore,functions
firebase emulators:exec --import ./seed-data "npm test"

# Export emulator data to a directory
firebase emulators:export ./emulator-data

# Available emulators and their default ports:
# Auth:                    localhost:9099
# Firestore:               localhost:8080
# Realtime Database:       localhost:9000
# Cloud Functions:         localhost:5001
# Pub/Sub:                 localhost:8085
# Cloud Storage:           localhost:9199
# Firebase Hosting:        localhost:5000
# Eventarc:                localhost:9299
# Cloud Tasks:             localhost:9499
# Extensions:              localhost:5002
# Logging:                 (no fixed port)
# Data Connect:            localhost:9399
# Emulator UI:             localhost:4000

# Manually download emulator binaries (useful in air-gapped CI)
firebase setup:emulators:firestore
firebase setup:emulators:database
firebase setup:emulators:pubsub
firebase setup:emulators:storage
firebase setup:emulators:ui

# Minimum Java version required: 21
```

---

## Firebase Admin SDK Examples (Node.js)

For operations not available via CLI, use the Firebase Admin SDK. These examples show common patterns.

```javascript
// Initialize Admin SDK (in Cloud Functions or server)
const admin = require('firebase-admin');
admin.initializeApp();  // uses ADC or FIREBASE_CONFIG env var

const db = admin.firestore();
const auth = admin.auth();
const storage = admin.storage().bucket();

// --- Authentication ---

// Create a user
await auth.createUser({
  uid: 'custom-uid-123',
  email: 'user@example.com',
  password: 'secure-password',
  displayName: 'John Doe',
  disabled: false,
});

// Set custom claims (for RBAC in Security Rules)
await auth.setCustomUserClaims('user-uid-123', {
  admin: true,
  orgId: 'my-org',
  subscription: 'premium',
});

// Get user by email
const user = await auth.getUserByEmail('user@example.com');
console.log(user.uid, user.customClaims);

// List all users (paginated)
let nextPageToken;
do {
  const listResult = await auth.listUsers(1000, nextPageToken);
  listResult.users.forEach(u => console.log(u.uid, u.email));
  nextPageToken = listResult.pageToken;
} while (nextPageToken);

// Disable a user
await auth.updateUser('user-uid-123', { disabled: true });

// Delete a user
await auth.deleteUser('user-uid-123');

// Verify an ID token from a client request
const decodedToken = await auth.verifyIdToken(idTokenFromClient);
const uid = decodedToken.uid;
const claims = decodedToken;  // includes custom claims

// Generate a custom token for a server-to-Firebase auth flow
const customToken = await auth.createCustomToken('user-uid-123', {
  orgId: 'my-org',
  role: 'editor',
});

// Revoke a user's refresh tokens (forces re-login on all devices)
await auth.revokeRefreshTokens('user-uid-123');

// --- Firestore (Admin, no security rules) ---

// Write a document
await db.collection('orders').doc('order-123').set({
  userId: 'user-uid-123',
  items: [{sku: 'ABC', qty: 2}],
  status: 'pending',
  createdAt: admin.firestore.FieldValue.serverTimestamp(),
});

// Read a document
const doc = await db.collection('orders').doc('order-123').get();
if (doc.exists) {
  console.log(doc.data());
}

// Query with Admin SDK (no security rules restriction)
const snapshot = await db.collection('orders')
  .where('userId', '==', 'user-uid-123')
  .where('status', '==', 'pending')
  .orderBy('createdAt', 'desc')
  .limit(10)
  .get();
snapshot.forEach(doc => console.log(doc.id, doc.data()));

// Batch write
const batch = db.batch();
batch.set(db.collection('orders').doc('order-456'), { status: 'shipped' });
batch.update(db.collection('users').doc('user-uid-123'), { lastOrderAt: new Date() });
await batch.commit();

// Transaction
await db.runTransaction(async (transaction) => {
  const orderRef = db.collection('orders').doc('order-789');
  const order = await transaction.get(orderRef);
  if (!order.exists) throw new Error('Order not found');
  transaction.update(orderRef, { status: 'cancelled' });
});
```

---

## Firestore Rules Deployment

```bash
# Deploy Firestore Security Rules
firebase deploy --only firestore:rules

# Deploy Firestore indexes
firebase deploy --only firestore:indexes

# View current Firestore rules
cat firestore.rules

# Test Firestore rules with the Rules playground (CLI testing)
# Use the Emulator + Jest/Mocha for rule unit tests:
# npm install --save-dev @firebase/rules-unit-testing
# Then write tests using initializeTestEnvironment() and assertFails/assertSucceeds
```

---

## Remote Config CLI

```bash
# Get current Remote Config template (JSON)
firebase remoteconfig:get

# Get and save to file
firebase remoteconfig:get --output=remote-config.json

# Update Remote Config from a JSON file
firebase remoteconfig:update remote-config.json

# Roll back to a previous version
firebase remoteconfig:rollback --version-number=5

# List Remote Config versions
firebase remoteconfig:versions:list --limit=10
```

---

## App Distribution

```bash
# Distribute an Android APK
firebase appdistribution:distribute app-release.apk \
  --app 1:123456789:android:abc123 \
  --groups testers-group \
  --release-notes "Fixed checkout bug; added dark mode"

# Distribute an iOS IPA
firebase appdistribution:distribute app-release.ipa \
  --app 1:123456789:ios:def456 \
  --testers "tester1@example.com,tester2@example.com" \
  --release-notes-file release-notes.txt

# List groups
firebase appdistribution:groups:list \
  --app 1:123456789:android:abc123

# Create a tester group
firebase appdistribution:groups:create beta-users \
  --app 1:123456789:android:abc123

# Add testers to a group
firebase appdistribution:testers:add \
  --app 1:123456789:android:abc123 \
  --groups beta-users \
  "user1@example.com user2@example.com"

# Remove testers
firebase appdistribution:testers:remove \
  --app 1:123456789:android:abc123 \
  "user1@example.com"
```

---

## Realtime Database CLI

```bash
# Read data at a path
firebase database:get /users/uid-123

# Read and format as JSON
firebase database:get /users --pretty

# Shallow read (keys only, no values — avoids downloading large subtrees)
firebase database:get /users --shallow

# Save output to file
firebase database:get /data -o output.json

# Order and limit
firebase database:get /scores --order-by-value --limit-to-first 10
firebase database:get /items --order-by-key --start-at "a" --end-at "z"

# Write data (replaces existing)
firebase database:set /config '{"theme":"dark","lang":"en"}'
firebase database:set /config data.json
firebase database:set /config data.json --disable-triggers  # skip Cloud Functions triggers
firebase database:set /config data.json --force

# Push data (generates a new key, like .push())
firebase database:push /messages '{"text":"hello","uid":"abc"}'
firebase database:push /messages data.json --disable-triggers

# Update specific fields (PATCH, does not replace)
firebase database:update /users/uid-123 '{"lastSeen":"2025-01-01"}'
firebase database:update /users/uid-123 updates.json

# Remove data at a path
firebase database:remove /users/uid-123 --confirm
firebase database:remove /users/uid-123 --disable-triggers

# Profile database operations (measure read/write performance)
firebase database:profile
firebase database:profile -d 30            # collect for 30 seconds
firebase database:profile -o report.json
firebase database:profile --raw            # newline-delimited JSON
firebase database:profile --no-collapse    # don't collapse similar paths

# Manage database instances
firebase database:instances:list
firebase database:instances:create my-new-instance

# Deploy Realtime Database security rules
firebase deploy --only database

# Target a specific database instance (multi-database projects)
firebase database:get /path --instance my-db-name
```

---

## Firestore CLI

```bash
# Delete a single document
firebase firestore:delete /users/uid-123

# Delete a collection and all subcollections (deep)
firebase firestore:delete /users --recursive

# Delete documents only, leave subcollections intact
firebase firestore:delete /users --shallow

# Wipe the entire database (use with extreme caution)
firebase firestore:delete --all-collections

# Target a named database (not default)
firebase firestore:delete /users --recursive --database my-named-db

# Skip confirmation prompt
firebase firestore:delete /sessions --recursive --force

# Deploy indexes
firebase deploy --only firestore:indexes

# Deploy security rules
firebase deploy --only firestore:rules

# List indexes (shows current state)
firebase firestore:indexes

# Export/import (via gcloud, not firebase CLI)
gcloud firestore export gs://my-bucket/backups/$(date +%F)
gcloud firestore import gs://my-bucket/backups/2024-01-01
```

`firestore.indexes.json` format:
```json
{
  "indexes": [
    {
      "collectionGroup": "orders",
      "queryScope": "COLLECTION",
      "fields": [
        {"fieldPath": "userId", "order": "ASCENDING"},
        {"fieldPath": "createdAt", "order": "DESCENDING"}
      ]
    }
  ],
  "fieldOverrides": [
    {
      "collectionGroup": "posts",
      "fieldPath": "tags",
      "indexes": [
        {"order": "ASCENDING", "queryScope": "COLLECTION"},
        {"arrayConfig": "CONTAINS", "queryScope": "COLLECTION"}
      ]
    }
  ]
}
```

---

## App Management

```bash
# List all apps in the current Firebase project
firebase apps:list

# List Android apps only
firebase apps:list ANDROID

# List iOS apps only
firebase apps:list IOS

# List Web apps only
firebase apps:list WEB

# Create a new Android app
firebase apps:create ANDROID "My Android App" --package-name com.example.myapp

# Create a new iOS app
firebase apps:create IOS "My iOS App" --bundle-id com.example.myapp

# Create a new Web app
firebase apps:create WEB "My Web App"

# Get SDK config for an app (outputs google-services.json / GoogleService-Info.plist / firebaseConfig)
firebase apps:sdkconfig ANDROID 1:123456789:android:abc123
firebase apps:sdkconfig IOS    1:123456789:ios:def456
firebase apps:sdkconfig WEB    1:123456789:web:ghi789

# Download google-services.json directly
firebase apps:sdkconfig ANDROID 1:123456789:android:abc123 \
  --out google-services.json
```

---

## Extensions

```bash
# Browse available extensions
firebase ext:list

# Install an extension from the Extensions Hub
firebase ext:install firebase/firestore-send-email

# Install with project flag
firebase ext:install storage-resize-images --project my-project-id

# List installed extensions in current project
firebase ext:list

# View details of an installed extension instance
firebase ext:info storage-resize-images

# Reconfigure an installed extension
firebase ext:configure storage-resize-images

# Update an extension to the latest version
firebase ext:update storage-resize-images

# Uninstall an extension
firebase ext:uninstall storage-resize-images

# Deploy extension config changes
firebase deploy --only extensions
firebase deploy --only extensions:storage-resize-images
```

---

## Functions: Secrets CLI

Manage Secret Manager secrets used by Cloud Functions directly from the CLI:

```bash
# Create or update a secret (prompts for value)
firebase functions:secrets:set STRIPE_API_KEY

# Set from a file
firebase functions:secrets:set STRIPE_API_KEY --data-file ./secret.txt

# Set from stdin (pipe-friendly)
echo -n "sk_live_..." | firebase functions:secrets:set STRIPE_API_KEY --data-file -

# Get secret metadata (name, versions — NOT the value)
firebase functions:secrets:get STRIPE_API_KEY

# Read the actual secret value
firebase functions:secrets:access STRIPE_API_KEY

# Prune unused/old secret versions (keeps only the latest in-use version)
firebase functions:secrets:prune

# Destroy a secret entirely
firebase functions:secrets:destroy STRIPE_API_KEY
firebase functions:secrets:destroy STRIPE_API_KEY --force
```

---

## Functions: Secrets & Parameters (2nd Gen)

The legacy `functions:config:set/get` approach is deprecated for 2nd gen functions. Use the new params system instead.

```javascript
// In functions/index.js — define typed parameters
const { defineString, defineInt, defineSecret, defineBoolean } = require('firebase-functions/params');

// String parameter (prompted at deploy time or set via .env)
const apiEndpoint = defineString('API_ENDPOINT', {
  default: 'https://api.example.com',
  description: 'Base URL of the external API',
});

// Secret parameter (stored in Secret Manager, never in plaintext)
const stripeSecret = defineSecret('STRIPE_SECRET_KEY');

// Use in a function
exports.processPayment = onRequest(
  { secrets: [stripeSecret] },   // grant access to secret
  (req, res) => {
    const key = stripeSecret.value();
    // ...
  }
);
```

```bash
# Set a parameter value for a specific environment
# Create a .env file for local use:
echo "API_ENDPOINT=https://api.example.com" >> functions/.env

# For production, set via CLI (writes to .env.<project-id>):
firebase functions:params:set API_ENDPOINT=https://api.example.com

# Secrets are managed via Secret Manager — the CLI prompts you at deploy
firebase deploy --only functions
# Prompts: "Enter a value for STRIPE_SECRET_KEY: [hidden]"

# Or set secret value manually via gcloud:
echo -n "sk_live_..." | gcloud secrets create STRIPE_SECRET_KEY --data-file=-
echo -n "sk_live_..." | gcloud secrets versions add STRIPE_SECRET_KEY --data-file=-
```

---

## firebase.json Reference

Complete `firebase.json` schema:

```json
{
  "$schema": "https://raw.githubusercontent.com/firebase/firebase-tools/master/schema/firebase-config.json",

  "hosting": {
    "public": "build",
    "ignore": ["firebase.json", "**/.*", "**/node_modules/**"],
    "cleanUrls": true,
    "trailingSlash": false,
    "predeploy": ["npm run build"],
    "postdeploy": ["echo 'Hosting deployed!'"],
    "rewrites": [
      { "source": "/api/**", "function": "api" },
      { "source": "/ssr/**", "run": { "serviceId": "ssr-app", "region": "us-central1" } },
      { "source": "**", "destination": "/index.html" }
    ],
    "redirects": [
      { "source": "/old-page", "destination": "/new-page", "type": 301 }
    ],
    "headers": [
      {
        "source": "**/*.@(js|css)",
        "headers": [{ "key": "Cache-Control", "value": "max-age=31536000" }]
      },
      {
        "source": "**",
        "headers": [
          { "key": "X-Frame-Options", "value": "SAMEORIGIN" },
          { "key": "X-Content-Type-Options", "value": "nosniff" }
        ]
      }
    ],
    "i18n": {
      "root": "/locales"
    }
  },
  "functions": [
    {
      "source": "functions",
      "codebase": "default",
      "runtime": "nodejs20",
      "predeploy": ["npm --prefix \"$RESOURCE_DIR\" run build"],
      "ignore": ["node_modules", ".git"]
    }
  ],
  "firestore": {
    "rules": "firestore.rules",
    "indexes": "firestore.indexes.json"
  },
  "database": {
    "rules": "database.rules.json"
  },
  "storage": {
    "rules": "storage.rules"
  },
  "remoteconfig": {
    "template": "remoteconfig.template.json"
  },
  "extensions": {},
  "emulators": {
    "auth":      { "port": 9099 },
    "functions": { "port": 5001 },
    "firestore": { "port": 8080 },
    "database":  { "port": 9000 },
    "hosting":   { "port": 5000 },
    "pubsub":    { "port": 8085 },
    "storage":   { "port": 9199 },
    "eventarc":  { "port": 9299 },
    "tasks":     { "port": 9499 },
    "ui":        { "enabled": true, "port": 4000 },
    "singleProjectMode": true
  }
}
```

`.firebaserc` format:
```json
{
  "projects": {
    "default":    "my-project-prod",
    "staging":    "my-project-staging",
    "dev":        "my-project-dev"
  },
  "targets": {
    "my-project-prod": {
      "hosting": {
        "main-site":   ["my-project-prod"],
        "admin-panel": ["my-project-prod-admin"]
      }
    }
  }
}
```

---

## CI/CD Patterns

### GitHub Actions with service account (recommended over FIREBASE_TOKEN)

```yaml
# .github/workflows/deploy.yml
name: Deploy to Firebase

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'

      - run: npm ci
      - run: npm run build

      # Option A: Workload Identity Federation (no long-lived key)
      - id: auth
        uses: google-github-actions/auth@v2
        with:
          workload_identity_provider: projects/123/locations/global/workloadIdentityPools/github/providers/github
          service_account: firebase-deployer@my-project.iam.gserviceaccount.com

      - uses: google-github-actions/setup-gcloud@v2

      - name: Deploy to Firebase
        run: firebase deploy --only hosting --non-interactive

  preview:
    if: github.event_name == 'pull_request'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: npm ci && npm run build

      # Option B: Service account JSON secret
      - uses: google-github-actions/auth@v2
        with:
          credentials_json: ${{ secrets.FIREBASE_SERVICE_ACCOUNT_JSON }}

      - name: Deploy preview channel
        run: |
          firebase hosting:channel:deploy pr-${{ github.event.number }} \
            --expires 7d \
            --non-interactive
```

### Official Firebase GitHub Action (simplest for hosting)

```yaml
# .github/workflows/firebase-hosting-merge.yml
name: Deploy to Firebase Hosting on merge
on:
  push:
    branches: [main]

jobs:
  build_and_deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: npm ci && npm run build

      - uses: FirebaseExtended/action-hosting-deploy@v0
        with:
          repoToken: ${{ secrets.GITHUB_TOKEN }}
          firebaseServiceAccount: ${{ secrets.FIREBASE_SERVICE_ACCOUNT_MY_PROJECT }}
          channelId: live           # deploys to production
          projectId: my-project-id

# .github/workflows/firebase-hosting-pr.yml
name: Deploy PR preview to Firebase Hosting
on:
  pull_request:
    branches: [main]

jobs:
  build_and_preview:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: npm ci && npm run build

      - uses: FirebaseExtended/action-hosting-deploy@v0
        with:
          repoToken: ${{ secrets.GITHUB_TOKEN }}
          firebaseServiceAccount: ${{ secrets.FIREBASE_SERVICE_ACCOUNT_MY_PROJECT }}
          projectId: my-project-id
          # No channelId = creates a PR preview channel automatically
          # Posts the preview URL as a PR comment
```

The `FIREBASE_SERVICE_ACCOUNT_MY_PROJECT` secret is the contents of a downloaded service account JSON key. The action auto-creates and names preview channels from the PR number.

### Legacy FIREBASE_TOKEN approach

```bash
# Generate a CI token (one-time, store as CI secret)
firebase login:ci
# Copy the printed token → store as FIREBASE_TOKEN in CI secrets

# Use in CI scripts
firebase deploy --only hosting --token "$FIREBASE_TOKEN" --non-interactive
```

`FIREBASE_TOKEN` is a long-lived credential and less secure than service account + Workload Identity. Prefer service accounts for new projects.

### Service account required permissions

Minimum IAM roles for the deploying service account:
- `roles/firebase.admin` — or more granular:
- `roles/firebasehosting.admin` — hosting deploys
- `roles/cloudfunctions.admin` — functions deploys
- `roles/datastore.owner` — Firestore rules/indexes
- `roles/iam.serviceAccountUser` — needed for functions deploys

---

## Global Flags Reference

| Flag | Description | Example |
|------|-------------|---------|
| `-P, --project <id>` | Override active project | `firebase deploy --project my-staging-project` |
| `--account <email>` | Use a specific authorized account | `firebase deploy --account user@example.com` |
| `--only <targets>` | Deploy only specified targets (comma-separated) | `--only hosting,functions` |
| `--except <targets>` | Deploy everything except these targets | `--except functions` |
| `--token <token>` | Auth via CI token (deprecated; prefer service account) | `--token "$FIREBASE_TOKEN"` |
| `--non-interactive` | Disable interactive prompts; fail on ambiguity | CI/CD pipelines |
| `--force` | Skip confirmation prompts; auto-delete removed functions | `firebase deploy --only functions --force` |
| `--dry-run` | Validate and build without deploying | `firebase deploy --dry-run` |
| `--debug` | Print verbose debug output | Troubleshooting deploy failures |
| `--json` | Output as JSON (machine-readable) | `firebase projects:list --json` |
| `--config <path>` | Use a custom firebase.json path | `--config firebase.staging.json` |
| `-m, --message <msg>` | Deployment description | `--message "v2.1 release"` |

---

## Functions Logs

```bash
# Stream live function logs (all functions)
firebase functions:log

# Logs for a specific function
firebase functions:log --only onUserCreated

# Last N lines
firebase functions:log --lines 50

# Filter by severity
firebase functions:log --only myFunction 2>&1 | grep ERROR

# View logs in Cloud Logging (web)
firebase open functions     # opens Firebase console → Functions tab
```

---

## Multi-Site Hosting

For projects with multiple web properties (e.g., main site + admin panel):

```bash
# Create additional hosting sites
firebase hosting:sites:create my-project-admin
firebase hosting:sites:list

# Define deploy targets in .firebaserc
firebase target:apply hosting main-site  my-project
firebase target:apply hosting admin-site my-project-admin

# firebase.json: array of hosting configs, each with a target
```

```json
{
  "hosting": [
    {
      "target": "main-site",
      "public": "build/main",
      "rewrites": [{"source": "**", "destination": "/index.html"}]
    },
    {
      "target": "admin-site",
      "public": "build/admin",
      "rewrites": [{"source": "**", "destination": "/index.html"}]
    }
  ]
}
```

```bash
# Deploy only main site
firebase deploy --only hosting:main-site

# Deploy only admin site
firebase deploy --only hosting:admin-site
```
