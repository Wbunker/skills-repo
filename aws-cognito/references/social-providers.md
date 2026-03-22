# Social Identity Provider Setup

## Table of Contents
1. [Overview](#overview)
2. [Google Setup](#google-setup)
3. [Apple Setup](#apple-setup)
4. [Facebook Setup](#facebook-setup)
5. [Amazon Setup](#amazon-setup)
6. [Cognito Configuration](#cognito-configuration)
7. [Testing](#testing)

---

## Overview

All social providers require:
1. Developer account with the provider
2. App/project created in provider's console
3. OAuth credentials (Client ID/Secret)
4. Callback URL configured: `https://<your-domain>/oauth2/idpresponse`

**Cognito Callback URL Format:**
- Prefix domain: `https://<prefix>.auth.<region>.amazoncognito.com/oauth2/idpresponse`
- Custom domain: `https://auth.example.com/oauth2/idpresponse`

---

## Google Setup

### 1. Google Cloud Console

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create new project or select existing
3. Navigate to **APIs & Services** → **OAuth consent screen**
4. Configure consent screen:
   - App name
   - User support email
   - **Authorized domains**: Add `amazoncognito.com` (required)
   - Developer contact email
5. Add scopes: `email`, `profile`, `openid`
6. Add test users (for testing before verification)

### 2. Create OAuth Credentials

1. Go to **APIs & Services** → **Credentials**
2. Click **Create Credentials** → **OAuth client ID**
3. Application type: **Web application**
4. Name: Your app name
5. **Authorized JavaScript origins**:
   ```
   https://<your-cognito-domain>
   ```
6. **Authorized redirect URIs**:
   ```
   https://<your-cognito-domain>/oauth2/idpresponse
   ```
7. Click **Create**
8. **Save Client ID and Client Secret**

### 3. CLI Configuration

```bash
aws cognito-idp create-identity-provider \
  --user-pool-id us-east-1_EXAMPLE \
  --provider-name Google \
  --provider-type Google \
  --provider-details \
    authorize_scopes="email profile openid",\
    client_id="YOUR_CLIENT_ID.apps.googleusercontent.com",\
    client_secret="YOUR_CLIENT_SECRET" \
  --attribute-mapping email=email,name=name,picture=picture
```

---

## Apple Setup

### 1. Apple Developer Console

1. Go to [Apple Developer](https://developer.apple.com/account)
2. Navigate to **Certificates, Identifiers & Profiles**

### 2. Create App ID

1. **Identifiers** → **+** → **App IDs** → **App**
2. Enter Description and Bundle ID
3. Enable **Sign In with Apple** capability
4. Register

### 3. Create Services ID

1. **Identifiers** → **+** → **Services IDs**
2. Enter Description and Identifier (this becomes your `client_id`)
3. Enable **Sign In with Apple**
4. Click **Configure**:
   - Primary App ID: Select your App ID
   - **Domains**: `<your-cognito-domain>` (without https://)
   - **Return URLs**: `https://<your-cognito-domain>/oauth2/idpresponse`
5. Save and Register

### 4. Create Private Key

1. **Keys** → **+**
2. Enter Key Name
3. Enable **Sign In with Apple** → **Configure**
4. Select Primary App ID
5. Register and **Download** the `.p8` file
6. **Note the Key ID** (shown on download page)

### 5. Get Team ID

Found in top-right of Apple Developer portal or in **Membership** section.

### 6. CLI Configuration

```bash
# Read private key from file
PRIVATE_KEY=$(cat AuthKey_XXXXXX.p8)

aws cognito-idp create-identity-provider \
  --user-pool-id us-east-1_EXAMPLE \
  --provider-name SignInWithApple \
  --provider-type SignInWithApple \
  --provider-details \
    authorize_scopes="email name",\
    client_id="com.example.app.service",\
    team_id="XXXXXXXXXX",\
    key_id="XXXXXXXXXX",\
    private_key="$PRIVATE_KEY" \
  --attribute-mapping email=email,name=name
```

**Important:** Apple only returns name on first sign-in. Store it immediately.

---

## Facebook Setup

### 1. Facebook Developer Console

1. Go to [Facebook Developers](https://developers.facebook.com)
2. Click **My Apps** → **Create App**
3. Select use case → Enter app name
4. Create app

### 2. Configure Facebook Login

1. In app dashboard, go to **App Settings** → **Basic**
2. **Note App ID and App Secret**
3. Add **App Domains**: `<your-cognito-domain>`
4. Add platform (if needed)
5. Go to **Products** → **Facebook Login** → **Settings**
6. **Valid OAuth Redirect URIs**:
   ```
   https://<your-cognito-domain>/oauth2/idpresponse
   ```
7. Save changes

### 3. CLI Configuration

```bash
aws cognito-idp create-identity-provider \
  --user-pool-id us-east-1_EXAMPLE \
  --provider-name Facebook \
  --provider-type Facebook \
  --provider-details \
    api_version="v17.0",\
    authorize_scopes="public_profile,email",\
    client_id="YOUR_APP_ID",\
    client_secret="YOUR_APP_SECRET" \
  --attribute-mapping email=email,name=name,picture=picture
```

**Note:** Use the latest stable API version. Check Facebook docs for current version.

---

## Amazon Setup

### 1. Login with Amazon Console

1. Go to [Login with Amazon](https://developer.amazon.com/loginwithamazon/console/site/lwa/overview.html)
2. Click **Create a Security Profile** (if none exists)
3. Fill in:
   - Security Profile Name
   - Security Profile Description
   - Consent Privacy Notice URL
4. Save

### 2. Configure Web Settings

1. Hover over gear icon → **Web Settings** → **Edit**
2. **Allowed Origins**:
   ```
   https://<your-cognito-domain>
   ```
3. **Allowed Return URLs**:
   ```
   https://<your-cognito-domain>/oauth2/idpresponse
   ```
4. Save
5. **Note Client ID and Client Secret** (click "Show Secret")

### 3. CLI Configuration

```bash
aws cognito-idp create-identity-provider \
  --user-pool-id us-east-1_EXAMPLE \
  --provider-name LoginWithAmazon \
  --provider-type LoginWithAmazon \
  --provider-details \
    authorize_scopes="profile postal_code",\
    client_id="amzn1.application-oa2-client.EXAMPLE",\
    client_secret="YOUR_CLIENT_SECRET" \
  --attribute-mapping email=email,name=name
```

---

## Cognito Configuration

### Update App Client to Include Social Providers

After creating identity providers, update your app client:

```bash
aws cognito-idp update-user-pool-client \
  --user-pool-id us-east-1_EXAMPLE \
  --client-id YOUR_CLIENT_ID \
  --supported-identity-providers COGNITO Google Facebook SignInWithApple LoginWithAmazon \
  --callback-urls "https://example.com/callback" "myapp://callback" \
  --logout-urls "https://example.com/logout" "myapp://logout" \
  --allowed-o-auth-flows code \
  --allowed-o-auth-scopes openid email profile \
  --allowed-o-auth-flows-user-pool-client
```

### Attribute Mapping Reference

| Provider | Available Attributes |
|----------|---------------------|
| Google | email, name, picture, given_name, family_name, locale |
| Apple | email, name (first sign-in only) |
| Facebook | email, name, picture, first_name, last_name |
| Amazon | email, name, postal_code |

### Common Cognito Attribute Mappings

```bash
--attribute-mapping \
  email=email,\
  name=name,\
  given_name=given_name,\
  family_name=family_name,\
  picture=picture
```

---

## Testing

### Test URL Format

```
https://<your-domain>/login?response_type=code&client_id=<client-id>&redirect_uri=<callback-url>
```

### Example Test URL

```
https://myapp.auth.us-east-1.amazoncognito.com/login?response_type=code&client_id=1abc2defghij3klmno4pqrst5&redirect_uri=https://example.com/callback
```

### Direct Provider Test

```
https://<your-domain>/oauth2/authorize?identity_provider=Google&response_type=code&client_id=<client-id>&redirect_uri=<callback-url>&scope=openid+email+profile
```

### Troubleshooting

**"redirect_mismatch" error:**
- Verify callback URL in provider console matches exactly (including trailing slashes)

**"invalid_client" error:**
- Check client ID and secret are correct
- Verify provider is enabled in Cognito

**User not created in Cognito:**
- Check attribute mapping
- Verify required attributes can be satisfied by provider scopes

**Apple name not available:**
- Apple only sends name on first authorization
- User may have denied name sharing
- Store name immediately on first sign-in

---

## Complete Setup Script

```bash
#!/bin/bash
POOL_ID="us-east-1_EXAMPLE"
CLIENT_ID="your-client-id"
DOMAIN="myapp.auth.us-east-1.amazoncognito.com"

# Google
aws cognito-idp create-identity-provider \
  --user-pool-id $POOL_ID \
  --provider-name Google \
  --provider-type Google \
  --provider-details \
    authorize_scopes="email profile openid",\
    client_id="$GOOGLE_CLIENT_ID",\
    client_secret="$GOOGLE_CLIENT_SECRET" \
  --attribute-mapping email=email,name=name

# Facebook
aws cognito-idp create-identity-provider \
  --user-pool-id $POOL_ID \
  --provider-name Facebook \
  --provider-type Facebook \
  --provider-details \
    api_version="v17.0",\
    authorize_scopes="public_profile,email",\
    client_id="$FACEBOOK_APP_ID",\
    client_secret="$FACEBOOK_APP_SECRET" \
  --attribute-mapping email=email,name=name

# Apple
aws cognito-idp create-identity-provider \
  --user-pool-id $POOL_ID \
  --provider-name SignInWithApple \
  --provider-type SignInWithApple \
  --provider-details \
    authorize_scopes="email name",\
    client_id="$APPLE_SERVICE_ID",\
    team_id="$APPLE_TEAM_ID",\
    key_id="$APPLE_KEY_ID",\
    private_key="$APPLE_PRIVATE_KEY" \
  --attribute-mapping email=email,name=name

# Update client with all providers
aws cognito-idp update-user-pool-client \
  --user-pool-id $POOL_ID \
  --client-id $CLIENT_ID \
  --supported-identity-providers COGNITO Google Facebook SignInWithApple \
  --callback-urls "https://example.com/callback" "myapp://callback" \
  --logout-urls "https://example.com/logout" "myapp://logout" \
  --allowed-o-auth-flows code \
  --allowed-o-auth-scopes openid email profile \
  --allowed-o-auth-flows-user-pool-client

echo "Social providers configured. Test at:"
echo "https://$DOMAIN/login?response_type=code&client_id=$CLIENT_ID&redirect_uri=https://example.com/callback"
```
