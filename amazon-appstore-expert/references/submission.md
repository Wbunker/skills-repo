# Amazon Appstore: App Submission

## Prerequisites

Before submitting, you need:
- An Amazon developer account (free at https://developer.amazon.com)
- App binary: APK, AAB (Fire OS), or VPKG (Vega OS)
- Image assets (screenshots, icons)
- App metadata (descriptions, category, content rating)
- IP documentation if using third-party intellectual property (as PDF with formal license letters — screenshots are not accepted)
- Physical device for testing

---

## Four-Step Submission Workflow

The Developer Console auto-saves as you progress. A green check mark appears on each step when complete. You cannot submit until steps 1, 2, and 3 all show completion markers.

### Step 1: Upload Your App File

**Supported formats:**
- **Fire OS**: APK or Android App Bundle (AAB)
- **Vega OS**: VPKG (must include `main` category in manifest for TV launcher)

**File size:**
- Maximum: 2.5 GB
- Recommended: keep under 50 MB (warning shown at >50 MB; also warned when binary increases 10% from previous version)
- Maximum installed size: 4 GB

**APK/AAB requirements:**
- Must be zip-aligned (Android Studio does this automatically)
- Version code must be an integer and must increase with each update
- `android:versionName` must be under 50 characters
- 64-bit support (`arm64-v8a`) required alongside 32-bit (`armeabi-v7a`) for broad device compatibility
- Package name must be unique across the Appstore; cannot contain "amazon"
- Up to 15 binary files can be uploaded simultaneously (for multiple device categories)

**Important — Amazon re-signs your app:**
> "Amazon removes the signature you used to sign your app and re-signs it with an Amazon signature that is unique to you"

This means apps distributed through Amazon Appstore will have a different signature from the same app on Google Play. Plan accordingly if your app does signature verification.

**DRM configuration:**
During upload, you choose whether to enable Amazon's automatic DRM. DRM is recommended for paid apps; unnecessary for free apps with IAP (IAP API already protects purchased content).

**Multiple binaries:**
- Different binaries can target Fire TVs vs. Fire tablets within a single listing
- Fire OS and Vega OS apps can coexist under one listing with the same package name
- Version codes remain independent per binary

### Step 2: Target Your App

Specify device compatibility and filtering:
- Select target device categories (Fire tablets, Fire TV, Echo Show)
- Declare hardware/software feature requirements in the Android manifest (these drive device filtering)
- Amazon uses manifest declarations to determine which devices see your app

**Device targeting considerations:**
- Apps requiring features not available on a device will be filtered out
- Apps must handle missing hardware gracefully (e.g., no camera, no GPS)
- For Fire TV apps, you must include the appropriate intent filter for the TV launcher

### Step 3: Add Appstore Details

Complete all metadata and store listing information.

#### App Metadata Requirements

| Field | Requirement |
|-------|-------------|
| **Display Title** | Brief name for Appstore listing |
| **Short Description** | Max 2,000 bytes (~1,200 English chars, ~400 Japanese/Chinese chars); Fire TV shows only first 200 characters |
| **Long Description** | Max 4,000 characters; plain text only (no HTML); appears on Appstore website and Fire OS 5+ tablets |
| **Product Feature Bullets** | 3–5 required; one feature per line |
| **Keywords** | Comma-separated; optional |
| **Category** | Required; select from 29 main categories (see Categories section below) |
| **Content Rating** | Required |

#### Image Asset Requirements — Fire Tablets

| Asset | Dimensions | Format | Notes |
|-------|-----------|--------|-------|
| **Small Icon** (required) | 114 × 114 px | PNG (transparent) | |
| **Large Icon** (required) | 512 × 512 px | PNG (transparent) | |
| **Screenshots** (3–10 required) | 800×480, 1024×600, 1280×720, 1280×800, 1920×1080, 1920×1200, or 2560×1600 px | PNG or JPEG | Landscape or portrait |
| **Promotional Image** (optional) | 1024 × 500 px | PNG or JPEG | Landscape; text must remain legible when scaled to 300×146 px |
| **Video** (optional, up to 5) | 720 px high × 1080 px wide | MPEG-2, WMV, QuickTime, FLV, AVI, H.264 MPEG-4 | Min bitrate: 1200 kbps; max duration: 60 min; max size: 262.14 MB |

#### Image Asset Requirements — Fire TV

| Asset | Dimensions | Format | Notes |
|-------|-----------|--------|-------|
| **App Icon** (required) | 1280 × 720 px | PNG (no transparency) | Safe area: 882 × 448 px |
| **Screenshots** (3–10 required) | 1920 × 1080 px | JPG or 24-bit PNG (no transparency) | Landscape only |
| **Background Image** (required) | 1920 × 1080 px | JPG or 24-bit PNG (no transparency) | Safe area: 1214 × 830 px |

#### Pricing

- **Free or Paid**: Set during Appstore Details step
- **Minimum price**: $0.99 USD (€0.69, £0.59, AUD/CAD $0.99)
- **Maximum price**: $999.99 USD
- Price is set per marketplace; Amazon handles currency conversion display

#### Content Ratings

Content ratings are required. Amazon uses a questionnaire-based system to assign ratings. Apps without completed ratings may be rejected or have distribution restricted.

#### IP Documentation

If your app uses third-party intellectual property (licensed characters, brands, etc.), you must provide a PDF containing formal confirmation letters or license agreements. Screenshots of licenses are not accepted.

### Step 4: Review and Submit

Final verification before publishing. Review all sections, confirm completeness, and submit. After submission, the app transitions to "Submitted" status and you can no longer edit it (though you may cancel the review request).

---

## Categories

Amazon Appstore has 29 main categories:

Books & Comics, Business, Communication, Customization, Education, Finance, Food & Drink, Games, Health & Fitness, Kids, Lifestyle, Local, Magazines, Medical, Movies & TV, Music & Audio, News, Novelty, Photos & Video, Productivity, Reference, Shopping, Social, Sports, Transportation, Travel, Utilities, Weather, and Games (with extensive subcategories by type).

---

## Updating a Published App

- Increment the version code in each new binary
- Upload via Developer Console → your app → Add upcoming version
- The update goes through the same review process
- You can cancel an in-review update before it is approved

---

## Additional Configurations (Pre-Submission)

| Feature | Requirement |
|---------|-------------|
| **In-App Purchases (IAP)** | All IAP items must be submitted and approved before app launch; Amazon will not test apps until both app and IAP catalog items are submitted |
| **Login with Amazon** | Associate your Login with Amazon security profile during submission |
| **Amazon Device Messaging** | Configure security credentials before submission |

---

## Documentation References

- Submission overview: https://developer.amazon.com/docs/app-submission/submitting-apps-to-amazon-appstore.html
- Upload app file: https://developer.amazon.com/docs/app-submission/upload-app-file.html
- Appstore details (assets, metadata): https://developer.amazon.com/docs/app-submission/appstore-details.html
- Target your app: https://developer.amazon.com/docs/app-submission/target-your-app.html
- Review and submit: https://developer.amazon.com/docs/app-submission/review-submit.html
- Update a published app: https://developer.amazon.com/docs/app-submission/update-published-app.html
