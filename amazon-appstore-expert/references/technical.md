# Amazon Appstore: Technical Requirements

## Fire OS Overview

Fire OS is Amazon's operating system for Fire tablets, Fire TV, and Echo Show devices. It is a **fork of Android Open Source Project (AOSP)** — not standard Android with Google services.

### Key Facts
- Android apps are compatible at the binary level (APK/AAB format)
- **Google Play Services are not available** — all Google service dependencies must be replaced with Amazon equivalents
- Fire OS versions map to specific Android API levels
- Minimum recommended API level: **API 10** for broadest Fire tablet compatibility

### Fire OS to Android API Level Mapping

| Fire OS Version | Android Equivalent | Notes |
|-----------------|--------------------|-------|
| Fire OS 5 | Android 5.1 (API 22) | Older Fire tablets |
| Fire OS 6 | Android 7.1 (API 25) | |
| Fire OS 7 | Android 9 (API 28) | Current Fire tablets |
| Fire OS 8+ | Android 11+ | Newer Fire TV devices |

**Generation-specific API guidance:**
- API 11–15: Avoid on 1st Gen Kindle Fire
- API 16–17: Avoid on 1st–2nd Gen devices
- API 18+: Avoid on 3rd Gen devices

---

## Google Services Replacement Table

When porting from Android/Google Play to Fire OS, replace these Google services:

| Google Service | Amazon/Fire OS Alternative |
|----------------|---------------------------|
| Google Play Billing | Appstore Billing Compatibility SDK (or Appstore SDK) |
| Firebase Cloud Messaging (FCM) | A3L Messaging SDK |
| Google Sign-In / Firebase Auth | A3L Authentication SDK |
| Google Location Services / Maps | A3L Location SDK |
| Google Play Games | No direct equivalent; use own implementation |

**Firebase note**: Not all Firebase libraries require Google Play Services. Check each Firebase library individually — some are compatible with Fire OS. Only replace those that depend on Google Play Services.

---

## Porting an Android App to Fire OS: 5-Step Process

1. **Identify unsupported APIs and services** — audit your app for Google service dependencies
2. **Update minimum API levels** — set minimum API level appropriate for your target Fire devices
3. **Remove incompatible features** — features that cannot be ported (see Unsupported Features below)
4. **Recompile and test thoroughly** — on actual Amazon hardware
5. **Submit to Amazon Appstore** — follow the standard submission workflow

### Unsupported Features (Cannot Be Ported)
- Themes and wallpapers
- Screensavers
- Custom keyboards
- Home screen widgets with UI manipulation
- `disable_keyguard` permissions
- Lock screen customizations

---

## Binary Requirements

| Requirement | Specification |
|-------------|---------------|
| **Formats** | APK, AAB (Fire OS); VPKG (Vega OS) |
| **Maximum file size** | 2.5 GB upload limit |
| **Maximum installed size** | 4 GB |
| **Recommended size** | Under 50 MB (user adoption decreases significantly above this) |
| **Zip-alignment** | Required (Android Studio does this automatically) |
| **64-bit support** | `arm64-v8a` required alongside `armeabi-v7a` |
| **Version code** | Integer; must increment with each update |
| **Package name** | Must be unique; cannot contain "amazon" |
| **Re-signing** | Amazon removes your signature and re-signs with a unique Amazon signature |

---

## Fire TV Specific Requirements

### Device Specifications (Current Gen)
- Quad-core CPU with dedicated GPU
- 4 GB RAM and 32 GB internal storage
- 4K Ultra HD video output
- HDR and Dolby Atmos audio support

### Supported Fire OS Versions
Fire TV runs Fire OS 5 through Fire OS 14. Always target a broad range when possible.

### Development Frameworks
Three frameworks are supported on Fire TV:

| Framework | Notes |
|-----------|-------|
| **Android (native)** | Standard Android tools and IDEs; must use Amazon services |
| **HTML5 Web Apps** | Browser-based; optimized for TV |
| **React Native** | JavaScript framework with Fire OS-compatible libraries |

### Required Fire TV SDKs
- **In-App Purchasing API**: Leverages pre-registered Amazon payment profiles
- **Fire TV Integration SDK**: For content personalization and linear TV integration
- **Appstore Billing Compatibility SDK**: For apps migrating from Google Play Billing

### Fire TV App Icon Requirements
- **Size**: 1280 × 720 px (larger than mobile — displays prominently on TV UI)
- **Format**: PNG, no transparency
- **Safe area**: 882 × 448 px (keep critical content within this zone)

### Fire TV Screenshot Requirements
- **Size**: 1920 × 1080 px, landscape only
- **Format**: JPG or 24-bit PNG, no transparency

### Fire TV Background Image (required, no mobile equivalent)
- **Size**: 1920 × 1080 px, landscape
- **Format**: JPG or 24-bit PNG, no transparency
- **Safe area**: 1214 × 830 px

### Fire TV UX Requirements (10-Foot UI)

**Navigation — D-Pad only:**
- All actionable elements must be reachable via directional buttons (Up, Down, Left, Right)
- Every screen must have a clear up-down/left-right orientation
- The Select button (center D-pad) or A button triggers actions
- Every focusable element must have a visible focus state
- Users must never need to press two buttons simultaneously for core functionality

**Text sizing:**
- Body text minimum: **14sp** (~19 px on 720p, ~28 px on 1080p)
- Use short, declarative sentences with greater line spacing than desktop design

**Safe zones:**
- Keep all UI elements within the inner 90% of the screen (avoid outer 5% edges)
- TV manufacturers reserve unpredictable overscan space

**Color guidance:**
- Use desaturated colors
- Cool tones (blue, purple, gray) work better than warm tones (red, orange)
- Test contrast levels — TV screens show higher saturation than monitors

**Information density:**
- Minimize menus, buttons, and images per screen
- Prioritize content consumption over feature access

**Touch UI elements:**
- Remove all touch-specific UI elements (Fire TV has no touchscreen)
- No swipe gestures, pinch-to-zoom, or tap targets

### Fire TV Test Criteria (Common Failure Points)
- Frame rate below 25 fps sustained
- App takes more than 2 seconds to exit when Home button pressed
- Load screen without progress indicator lasting more than 15 seconds
- UI occupying less than 80% of screen area
- Inability to navigate using D-pad only
- HDMI disconnection not pausing media playback
- Text illegible from 10 feet away

---

## Fire Tablet Specifics

### Soft Key Behavior
Fire tablets have soft keys (Back, Home, Menu). Your app must handle:
- Back key: navigate back through activity stack or exit app
- Home key: send app to background
- Menu key (if present): open contextual menu

### Screen Sizes
Fire tablets span multiple resolutions — test across common sizes:
- 800 × 480 px (older 7" models)
- 1024 × 600 px
- 1280 × 800 px
- 1920 × 1080 px / 1920 × 1200 px
- 2560 × 1600 px (HD models)

---

## Echo Show Specifics

Echo Show devices have touchscreens and Alexa voice integration. Apps targeting Echo Show:
- Can use both touch and voice input
- Should follow Alexa Smart Home guidelines for voice interactions
- Screen sizes vary by model (8", 10", 15")

---

## Development and Testing Tools

### ADB (Android Debug Bridge)
- Connect to Fire TV via ADB over the network (no USB required on most Fire TV devices)
- Enable ADB in Fire TV Settings → My Fire TV → Developer Options

### App Tester
- Tool for testing IAP flows locally without real transactions
- Documentation: https://developer.amazon.com/docs/in-app-purchasing/iap-app-tester-user-guide.html

### Live App Testing
- Invite users to test in the production Appstore environment
- Supports testing IAP, real device testing, and beta feedback
- Access: Developer Console → your app → Live App Testing

### Amazon Device Farm
Amazon offers device farm testing capabilities. Check current availability at:
https://developer.amazon.com/apps-and-games/test

### Device Specifications Reference
Full specs for all Amazon devices: https://developer.amazon.com/docs/device-specs/device-specifications.html

---

## Amazon Appstore vs. Google Play: Key Differences

| Aspect | Amazon Appstore | Google Play |
|--------|----------------|-------------|
| **Platform** | Fire OS (AOSP fork) | Android with Google services |
| **Google Play Services** | Not available | Required for many features |
| **Billing** | Appstore SDK / Billing Compat SDK | Google Play Billing |
| **Push notifications** | A3L Messaging SDK | Firebase Cloud Messaging |
| **Auth** | A3L Auth SDK / Login with Amazon | Google Sign-In / Firebase Auth |
| **Maps/Location** | A3L Location SDK | Google Maps / Location Services |
| **App signing** | Amazon re-signs your app with its own signature | Developer signature retained |
| **Review time** | Days (no published SLA) | Hours to days |
| **Revenue share** | 80/20 (under $1M); 70/30 otherwise | 85/15 first $1M, then 70/30 |
| **DRM** | Optional Amazon DRM or Appstore SDK | Play Asset Delivery / licensing |
| **IAP testing** | App Tester utility (local) | Google Play Console test tracks |
| **Sideloading** | Enabled by default on Fire devices | Disabled by default on Android |
| **Store format** | APK or AAB | Primarily AAB |
| **Fire TV** | Native platform | Not applicable |
| **Device reach** | 250M+ Amazon devices; no third-party Android | All Android devices |

### What Works Differently

1. **APK signature**: Your app will have a different package signature on Amazon vs. Google Play. If your app checks its own signature (e.g., for anti-tamper), this will fail on Amazon unless you update the expected signature value.

2. **In-app purchasing**: You cannot use Google Play Billing on Fire OS at all. You must implement Amazon's IAP SDK or the Billing Compatibility SDK.

3. **Push notifications**: FCM is unavailable. Use Amazon Device Messaging (ADM) or the A3L Messaging SDK.

4. **Google Maps**: Unavailable. Use A3L Location SDK for location features, or implement your own map solution.

5. **Google Analytics / Firebase Analytics**: May or may not work depending on which Firebase libraries you use. Audit each dependency.

6. **Android TV vs. Fire TV**: Apps built for Android TV will not run on Fire TV without modification. The input handling, launcher integration, and required intents differ.

7. **Sideloading is easier on Fire**: Amazon intentionally allows sideloading (installing APKs outside the Appstore) on Fire devices. This affects piracy risk for paid apps — use DRM if this matters to you.
