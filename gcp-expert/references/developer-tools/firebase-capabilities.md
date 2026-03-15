# Firebase — Capabilities

## Overview

Firebase is Google's mobile and web application development platform. Firebase services are built on top of GCP infrastructure and are accessible via Firebase-specific SDKs (which provide real-time, offline-first, and security-rules-based access patterns) as well as standard GCP SDKs. Firebase is particularly strong for mobile (iOS, Android) and web frontend applications.

---

## Firebase Authentication

Firebase Authentication provides a complete identity solution with support for multiple sign-in methods.

### Sign-In Providers

- **Email/password**: standard registration and login; email verification; password reset.
- **Phone/SMS**: OTP via SMS; reCAPTCHA verification to prevent abuse.
- **Anonymous**: sign in without credentials; convert to permanent account later. Used for guest/pre-auth app experiences.
- **Social / OAuth providers**: Google, Facebook, Apple, GitHub, Twitter/X, Microsoft, Yahoo. Configured with provider OAuth 2.0 credentials.
- **Email link (passwordless)**: magic link sent to email; user clicks to sign in without entering a password.
- **SAML 2.0**: enterprise SSO via SAML identity providers (Okta, Azure AD, OneLogin, PingFederate). Requires Firebase Authentication enterprise tier.
- **OpenID Connect (OIDC)**: connect any OIDC-compliant identity provider.

### Multi-Tenancy

Firebase Authentication supports multi-tenancy for SaaS applications serving multiple organizations. Each tenant has isolated user pools; users in one tenant cannot access another. Configured via the Firebase Identity Platform (extended Auth).

### Custom Tokens

The Firebase Admin SDK (server-side) can create custom tokens from any user identity system. The mobile/web client exchanges the custom token for a Firebase session. Use for integrating Firebase Auth with an existing user database or identity system.

### Blocking Functions (Auth Hooks)

Cloud Functions for Firebase can intercept the sign-in and user creation flows:
- `beforeSignIn`: runs before the sign-in token is issued; can reject or modify the sign-in (add custom claims, block specific users).
- `beforeCreate`: runs before a new user account is created; can reject account creation.

### User Management

Firebase Admin SDK provides server-side user management: create users, list users, get user by email/UID/phone, update profile, disable/enable, delete, revoke refresh tokens, set custom claims (for RBAC in Firestore Security Rules).

### Custom Claims

Add JWT claims to user tokens server-side using the Admin SDK. Claims appear in the Firebase ID token and can be used in Firestore Security Rules (`request.auth.token.CLAIM_NAME`). Use for role-based access control: `admin: true`, `premium: true`, `orgId: "my-org"`.

---

## Firebase Realtime Database

A cloud-hosted NoSQL JSON database that synchronizes data in real time across connected clients. When data changes, all connected clients receive the update immediately.

### Data Model
- Single JSON tree; no collections or documents — everything is one large JSON object.
- Keys should be short (data size is a concern for mobile clients).
- Avoid deep nesting; prefer flat structure with index-based cross-reference.

### Querying
- Limited query capabilities compared to Firestore: orderBy, limitToFirst/Last, startAt/endAt, equalTo.
- No compound queries. Design data structure around your query needs.
- Indexing: add `.indexOn` in Security Rules to enable efficient orderBy queries.

### Security Rules
Firebase Realtime Database Security Rules control read/write access based on the authenticated user identity (`auth.uid`, `auth.token.*`) and the requested data path.

```json
{
  "rules": {
    "users": {
      "$uid": {
        ".read": "$uid === auth.uid",
        ".write": "$uid === auth.uid"
      }
    },
    "posts": {
      ".read": "auth != null",
      "$postId": {
        ".write": "newData.child('author').val() === auth.uid || data.child('author').val() === auth.uid"
      }
    }
  }
}
```

### Offline Support
Firebase Realtime Database SDK caches data locally (IndexedDB in web, SQLite in mobile). Changes made while offline are queued and synchronized when connectivity resumes.

### When to Use Realtime Database vs Firestore
- **Realtime Database**: very simple data structures (chat messages, presence indicators, game state); very high update frequency (thousands of updates per second to a single location); legacy apps already using Realtime Database.
- **Firestore**: most new applications; complex queries, rich data models, offline support, stronger consistency, better scalability.

---

## Cloud Firestore (Firebase)

Firestore is GCP's primary NoSQL document database. When accessed via Firebase SDKs (as opposed to the GCP Cloud Firestore SDK), it uses Firestore Native mode with Firebase Security Rules. All Firestore capabilities (documents, collections, subcollections, queries, transactions, real-time listeners) are available via Firebase SDKs.

See the `database.md` reference index for full Firestore capabilities. Firebase-specific aspects:

### Firebase Security Rules for Firestore

Firebase Security Rules govern read/write access to Firestore when using Firebase SDKs from mobile/web clients. Rules are based on the authenticated Firebase user's identity and the requested document path.

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    match /users/{userId} {
      allow read, write: if request.auth != null && request.auth.uid == userId;
    }
    match /posts/{postId} {
      allow read: if true;  // public readable
      allow create: if request.auth != null && request.resource.data.authorId == request.auth.uid;
      allow update, delete: if request.auth != null && resource.data.authorId == request.auth.uid;
    }
    match /admin/{document=**} {
      allow read, write: if request.auth.token.admin == true;  // custom claim check
    }
  }
}
```

---

## Cloud Storage for Firebase

Cloud Storage for Firebase provides access to GCP Cloud Storage buckets via Firebase SDKs. Firebase SDKs handle authentication automatically (Firebase Auth user's identity) and support Security Rules for client-side access control.

### Firebase Security Rules for Storage

```javascript
rules_version = '2';
service firebase.storage {
  match /b/{bucket}/o {
    match /user-uploads/{userId}/{allPaths=**} {
      allow read: if request.auth != null;
      allow write: if request.auth != null && request.auth.uid == userId
                   && request.resource.size < 5 * 1024 * 1024  // 5 MB max
                   && request.resource.contentType.matches('image/.*');
    }
    match /public/{allPaths=**} {
      allow read: if true;
      allow write: if false;  // write only from server-side
    }
  }
}
```

---

## Firebase Hosting

Firebase Hosting provides fast, secure static web hosting with a global CDN. It is optimized for web apps (SPAs, PWAs) and supports dynamic content via Cloud Functions or Cloud Run.

### Key Features

- **Global CDN**: assets served from Google's edge network worldwide.
- **Automatic HTTPS**: free SSL/TLS certificates via Let's Encrypt; HTTPS enforced automatically.
- **Custom domains**: connect your custom domain; Firebase provisions the certificate.
- **SPA routing**: configure `rewrites` to serve `index.html` for all routes (for React Router, Vue Router, etc.).
- **Preview channels**: deploy to a temporary URL (e.g., `https://my-app--preview-abc123.web.app`) for staging, PR previews, or UAT. Channels expire after a configurable time.
- **Versioned releases**: each deployment creates a numbered release; roll back to any previous release instantly.

### Dynamic Content Integration

Configure `rewrites` in `firebase.json` to route specific URL patterns to Cloud Functions or Cloud Run:
```json
{
  "hosting": {
    "public": "build",
    "rewrites": [
      {"source": "/api/**", "run": {"serviceId": "my-api", "region": "us-central1"}},
      {"source": "**", "destination": "/index.html"}
    ]
  }
}
```

---

## Cloud Functions for Firebase

Cloud Functions for Firebase is the same product as GCP Cloud Functions (2nd gen), with additional Firebase-specific trigger types and the Firebase Admin SDK pre-configured.

### Firebase-Specific Trigger Types

- **Firestore triggers**: `onDocumentCreated`, `onDocumentUpdated`, `onDocumentDeleted`, `onDocumentWritten` — triggered when a Firestore document changes.
- **Firebase Authentication triggers**: `beforeUserCreated`, `beforeUserSignedIn` (blocking functions); `onUserCreated`, `onUserDeleted` (background functions).
- **Cloud Storage triggers**: `onObjectFinalized`, `onObjectDeleted`, `onObjectArchived`, `onObjectMetadataUpdated`.
- **Realtime Database triggers**: `onValueCreated`, `onValueUpdated`, `onValueDeleted`, `onValueWritten`.
- **Remote Config triggers**: `onConfigUpdated`.
- **Pub/Sub triggers**: same as GCP Cloud Functions.
- **Scheduled triggers**: same as GCP Cloud Scheduler.

### Firebase Admin SDK

Server-side SDK for full administrative access to Firebase services:
- Manage users (create, update, delete, custom claims).
- Read/write Firestore without security rule restrictions.
- Send push notifications (FCM).
- Generate custom auth tokens.
- Read/write Realtime Database without security rules.
- Verify Firebase ID tokens.

Available for: Node.js, Python, Java, Go, C#, Ruby.

---

## Remote Config

Firebase Remote Config lets you change app behavior and appearance without requiring users to download an app update.

### Key Features

- **Server-side parameters**: define key-value parameters in the Firebase Console; the app fetches and activates them.
- **Default values**: each parameter has a default value in the app code; the remote value overrides it when fetched.
- **Conditions**: serve different values to different user segments based on app version, platform (iOS/Android/Web), country, language, user property, Firebase A/B test group, or custom signals.
- **A/B testing integration**: Firebase A/B Testing (powered by Google Optimize) uses Remote Config parameters to run experiments; analyze results in Firebase Analytics.
- **Feature flags**: use boolean parameters as feature flags; roll out new features to a percentage of users or specific audiences.
- **Real-time Remote Config**: propagate config updates to clients in seconds (instead of the default ~12-hour fetch interval) using Firebase's real-time connection.

---

## Firebase Analytics (Google Analytics for Firebase)

Firebase Analytics is a free, unlimited analytics solution built on Google Analytics for Firebase events.

### Key Features

- **Automatic events**: page_view, session_start, first_open, app_remove, in_app_purchase, etc. collected automatically.
- **Custom events**: `logEvent("purchase", {item_id: "SKU123", value: 29.99, currency: "USD"})`.
- **User properties**: set user attributes (subscription_type, language, cohort) that persist across events.
- **Audiences**: define user segments based on events and properties; use in Firebase A/B Testing, Remote Config targeting, Cloud Messaging targeting.
- **Funnels**: visualize conversion funnels (registration → onboarding → first purchase).
- **BigQuery export**: daily export of raw events to BigQuery; enables SQL-based analysis, attribution modeling, ML training.

### BigQuery Integration

Enable BigQuery export in Firebase console. Events are exported to a BigQuery dataset with tables per day or as a streaming table. Use BigQuery to run complex queries, join with CRM data, build custom dashboards in Looker Studio, or feed ML models.

---

## Firebase App Distribution

Pre-release distribution of iOS and Android apps to testers without using TestFlight or the Google Play Console.

- Upload a build (IPA or APK) via Firebase CLI or CI/CD.
- Invite testers by email; they receive a link to install the build.
- Manage tester groups for different app variants or environments.
- Integrate with Fastlane (for iOS) or Gradle plugin (for Android) in CI/CD pipelines.

---

## Firebase Test Lab

Cloud-based automated testing on real and virtual Android and iOS devices.

### Test Types

- **Robo test**: AI-driven exploration of the app's UI; no test code required; detects crashes, UI errors; generates a video of the test session.
- **Instrumented tests**: run Espresso (Android) or XCTest/XCUITest (iOS) test suites on real or virtual devices.
- **Game loop tests**: test game apps using a custom loop trigger.

### Device Matrix

Test against multiple combinations of: device model, OS version, screen orientation, locale. Firebase Test Lab reports pass/fail per combination with video recordings, logcat output, and performance data.

---

## Firebase Studio (formerly Project IDX)

Firebase Studio is a browser-based IDE with built-in Firebase and GCP integration.

- Built on Code OSS (VS Code open-source) running in a Google Cloud VM.
- Templates for Firebase + Angular, React, Vue, Flutter, Next.js projects.
- Live preview of web apps during development.
- AI-assisted development (Gemini).
- Firebase emulators pre-configured.
- One-click deploy to Firebase Hosting.
