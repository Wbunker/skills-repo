# Firebase — CLI

## Firebase CLI Installation and Authentication

```bash
# Install Firebase CLI via npm
npm install -g firebase-tools

# Or install via a standalone script (no npm required)
curl -sL https://firebase.tools | bash

# Verify installation
firebase --version

# Login to Firebase (opens browser for OAuth)
firebase login

# Login in non-interactive (CI) environments using service account or token
firebase login:ci   # generates a CI token
# Then use: firebase --token $FIREBASE_TOKEN COMMAND

# Check current login
firebase login --list

# Logout
firebase logout

# Show current project
firebase use

# List all Firebase projects
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
# Serve hosting locally (preview before deploy)
firebase serve --only hosting
# or
firebase hosting:channel:serve

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

# Start emulators in the background (for CI)
firebase emulators:start --only firestore,functions &

# Run tests with emulators (starts emulators, runs command, exits)
firebase emulators:exec "npm test" --only firestore,functions

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
# Emulator UI:             localhost:4000
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
