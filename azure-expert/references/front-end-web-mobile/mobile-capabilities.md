# Mobile & Notification — Capabilities Reference
For CLI commands, see [mobile-cli.md](mobile-cli.md).

## Azure Notification Hubs

**Purpose**: Cross-platform push notification infrastructure. Send push notifications to hundreds of millions of devices on iOS (APNs), Android (FCM), Windows (WNS), Kindle (ADM), and Baidu — from a single API, without managing per-platform complexity.

### Architecture

```
Mobile App (iOS/Android/Windows)
  ↓ registers device handle + tags
Azure Notification Hubs
  ↓ sends via platform-specific channel
[Apple Push Notification service (APNs)] → iOS devices
[Firebase Cloud Messaging (FCM v1)]     → Android devices
[Windows Notification Service (WNS)]   → Windows/UWP apps
[Amazon Device Messaging (ADM)]         → Kindle Fire
[Baidu Cloud Push]                      → China Android
```

### Key Concepts

| Concept | Description |
|---|---|
| **Namespace** | Container for notification hubs; regional billing unit; shared quota |
| **Hub** | Notification hub instance; bound to one app; stores registrations |
| **Registration** | Device's platform handle (APNs device token, FCM registration token) + optional tags; created by client SDK |
| **Installation** | Preferred alternative to registration; server-managed; supports templates and tags; identified by `installationId` |
| **Tag** | String label on a registration (e.g., `userId:123`, `topic:sports`, `env:prod`) |
| **Tag expression** | Boolean combination: `userId:123 && (topic:news || topic:sports)` |
| **Template** | Per-device notification payload format; allows sending platform-agnostic body |
| **Direct send** | Send to a specific platform handle without registration lookup |
| **Scheduled push** | Send notification at a future date/time |

### Tags for Targeting

```
# Broadcast (all registered devices)
Send with no tag filter

# User-targeted
Tags on installation: ["userId:abc123"]
Send to: "userId:abc123"

# Topic subscription
Tags on installation: ["topic:breaking-news", "region:us-west", "lang:en"]
Send to: "topic:breaking-news && region:us-west"

# Segment
Send to: "premium && !churned"
```

### Templates (Platform-agnostic Sends)

Device registers a template for its platform:

iOS template:
```json
{"aps": {"alert": "$(message)", "badge": "$(badge)"}}
```

Android template:
```json
{"data": {"msg": "$(message)", "type": "$(type)"}}
```

Server sends platform-agnostic body:
```json
{"message": "New sale alert!", "badge": "5", "type": "sale"}
```

Each device receives the message formatted for its platform.

### Tiers

| Tier | Registrations | Pushes/month | SLA |
|---|---|---|---|
| **Free** | 500 | 1,000,000 | None |
| **Basic** | 200,000 | 10,000,000 | 99.9% |
| **Standard** | Unlimited | Unlimited (extra cost) | 99.9% |

### SDK Integration

```swift
// iOS Swift - Register for push notifications
func application(_ application: UIApplication,
                 didRegisterForRemoteNotificationsWithDeviceToken deviceToken: Data) {
    let hub = MSNotificationHub(connectionString: "<Listen connection string>",
                                notificationHubPath: "<Hub name>")
    hub.registerNative(with: deviceToken, tags: ["userId:\(userId)", "topic:news"])
}
```

```kotlin
// Android Kotlin - Register FCM token with hub
FirebaseMessaging.getInstance().token.addOnCompleteListener { task ->
    val fcmToken = task.result
    val hub = NotificationHub("<Hub name>", "<Listen connection string>", context)
    hub.register(fcmToken, "userId:$userId", "topic:sports")
}
```

---

## Azure Spatial Anchors

**Purpose**: Create and share mixed reality anchors that persist across devices and sessions. Enable multi-user AR experiences where virtual objects remain anchored to physical locations.

### Key Capabilities

| Capability | Details |
|---|---|
| **Cloud persistence** | Anchors stored in Azure; survive app restarts and device switches |
| **Multi-user sharing** | Multiple users locate the same anchor; shared AR space |
| **Cross-platform** | HoloLens (Windows), iOS (ARKit), Android (ARCore) |
| **Spatial understanding** | Anchors attached to physical world features; relocalized using visual data |
| **Anchor relationships** | Graph of related anchors; navigate between anchor points |
| **Coarse relocalization** | Find nearby anchors using WiFi, Bluetooth, GPS sensors |

### Use Cases

- **Industrial**: Mark equipment locations in a factory floor; overlay maintenance procedures
- **Retail**: Place virtual product info at physical shelf locations; shared store maps
- **Healthcare**: Virtual surgical planning overlaid on physical space
- **Gaming**: Shared AR game world anchored to real locations
- **Navigation**: Indoor wayfinding anchors at decision points

### SDK Platforms

| Platform | SDK |
|---|---|
| HoloLens (Unity) | `Azure.MixedReality.SpatialAnchors` NuGet |
| iOS (Swift/ObjC) | `AzureSpatialAnchors` CocoaPod |
| Android (Kotlin/Java) | `com.microsoft.azure.spatialanchors:spatialanchors_jni` |
| Unity (all platforms) | Azure Spatial Anchors Unity SDK |
| Xamarin | Azure Spatial Anchors Xamarin SDK |

### Anchor Lifecycle

```
1. Start ASA session
2. Scan environment (collect visual data)
3. Create anchor at specific position in AR space
4. Upload anchor to Azure (get anchor ID)
5. Share anchor ID with other users/sessions
6. Other users: query Azure with anchor ID
7. Azure returns anchor; app localizes against environment
8. All users see shared virtual object at same physical location
```

---

## App Center — RETIRED

> **App Center has been retired as of March 31, 2025.** All App Center services are discontinued. Migrate to the following alternatives:

### Migration Guide

| App Center Feature | Recommended Replacement |
|---|---|
| **Crash reporting** | Firebase Crashlytics (iOS/Android); Sentry; Microsoft Azure Application Insights |
| **Analytics** | Firebase Analytics; Azure Application Insights (custom events) |
| **Distribution** | Firebase App Distribution (test builds); TestFlight (iOS); Google Play Internal Testing |
| **Push notifications** | Azure Notification Hubs; Firebase Cloud Messaging (FCM) directly |
| **Build** | GitHub Actions; Azure DevOps Pipelines; Xcode Cloud (iOS) |
| **Test** | Firebase Test Lab; BrowserStack; Azure DevTest Labs |
| **Authentication (App Center Auth)** | Microsoft Entra External ID; Firebase Authentication |

### Firebase Crashlytics (Primary Crash Replacement)

```kotlin
// Android - Initialize Crashlytics
FirebaseCrashlytics.getInstance().apply {
    setUserId(userId)
    setCustomKey("screen", "MainDashboard")
    log("User clicked checkout button")
}
// Crashes auto-reported; custom non-fatal:
FirebaseCrashlytics.getInstance().recordException(exception)
```

```swift
// iOS Swift - Crashlytics
Crashlytics.crashlytics().setUserID(userId)
Crashlytics.crashlytics().setCustomValue("MainDashboard", forKey: "screen")
Crashlytics.crashlytics().log("User clicked checkout")
// Non-fatal:
Crashlytics.crashlytics().record(error: error)
```

### Azure Application Insights for Mobile

- Use Application Insights SDK or REST API from mobile apps
- Track custom events, page views, dependencies, exceptions
- Funnel analysis, user flow, retention reports in Application Insights portal
- Works alongside Firebase (use both: Firebase for crash/distribution, App Insights for custom business telemetry)
