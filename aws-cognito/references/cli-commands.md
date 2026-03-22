# AWS Cognito CLI Commands Reference

## Table of Contents
1. [User Pool Management](#user-pool-management)
2. [User Pool Client](#user-pool-client)
3. [Identity Pool](#identity-pool)
4. [Identity Providers](#identity-providers)
5. [Domain Setup](#domain-setup)
6. [User Management](#user-management)

---

## User Pool Management

### Create User Pool

```bash
aws cognito-idp create-user-pool \
  --pool-name "MyAppPool" \
  --username-attributes email \
  --auto-verified-attributes email \
  --mfa-configuration OPTIONAL \
  --policies 'PasswordPolicy={MinimumLength=8,RequireUppercase=true,RequireLowercase=true,RequireNumbers=true,RequireSymbols=false}' \
  --account-recovery-setting 'RecoveryMechanisms=[{Priority=1,Name=verified_email},{Priority=2,Name=verified_phone_number}]' \
  --verification-message-template 'DefaultEmailOption=CONFIRM_WITH_CODE' \
  --user-pool-tags Environment=production
```

**Key Parameters:**

| Parameter | Values | Description |
|-----------|--------|-------------|
| `--username-attributes` | `email`, `phone_number` | What users sign in with |
| `--alias-attributes` | `email`, `phone_number`, `preferred_username` | Alternative sign-in options |
| `--auto-verified-attributes` | `email`, `phone_number` | Auto-verify these attributes |
| `--mfa-configuration` | `OFF`, `ON`, `OPTIONAL` | MFA requirement |
| `--user-pool-tier` | `LITE`, `ESSENTIALS`, `PLUS` | Feature tier |

**Email Configuration (SES):**
```bash
--email-configuration 'SourceArn=arn:aws:ses:us-east-1:111111111111:identity/noreply@example.com,EmailSendingAccount=DEVELOPER,ReplyToEmailAddress=support@example.com'
```

**SMS Configuration:**
```bash
--sms-configuration 'SnsCallerArn=arn:aws:iam::123456789012:role/CognitoSNSRole,SnsRegion=us-east-1'
```

**Password Policy:**
```bash
--policies 'PasswordPolicy={MinimumLength=12,RequireUppercase=true,RequireLowercase=true,RequireNumbers=true,RequireSymbols=true,PasswordHistorySize=5,TemporaryPasswordValidityDays=7}'
```

**Sign-In Policy (Passwordless):**
```bash
--policies 'SignInPolicy={AllowedFirstAuthFactors=[PASSWORD,EMAIL_OTP,SMS_OTP,WEB_AUTHN]}'
```

### Describe/Update/Delete User Pool

```bash
# Describe
aws cognito-idp describe-user-pool --user-pool-id us-east-1_EXAMPLE

# Update
aws cognito-idp update-user-pool --user-pool-id us-east-1_EXAMPLE --mfa-configuration ON

# Delete
aws cognito-idp delete-user-pool --user-pool-id us-east-1_EXAMPLE

# List all
aws cognito-idp list-user-pools --max-results 20
```

---

## User Pool Client

### Create User Pool Client

```bash
aws cognito-idp create-user-pool-client \
  --user-pool-id us-east-1_EXAMPLE \
  --client-name "MyAppClient" \
  --generate-secret \
  --explicit-auth-flows ALLOW_USER_PASSWORD_AUTH ALLOW_USER_SRP_AUTH ALLOW_REFRESH_TOKEN_AUTH \
  --supported-identity-providers COGNITO Google Facebook SignInWithApple \
  --callback-urls "https://example.com/callback" "myapp://callback" \
  --logout-urls "https://example.com/logout" "myapp://logout" \
  --allowed-o-auth-flows code \
  --allowed-o-auth-scopes openid email profile \
  --allowed-o-auth-flows-user-pool-client \
  --access-token-validity 60 \
  --id-token-validity 60 \
  --refresh-token-validity 30 \
  --token-validity-units AccessToken=minutes,IdToken=minutes,RefreshToken=days \
  --prevent-user-existence-errors ENABLED \
  --enable-token-revocation
```

**Authentication Flows:**

| Flow | Description |
|------|-------------|
| `ALLOW_USER_AUTH` | Selection-based sign-in (recommended) |
| `ALLOW_USER_PASSWORD_AUTH` | Username/password (sends password in request) |
| `ALLOW_USER_SRP_AUTH` | Secure Remote Password (recommended for password) |
| `ALLOW_CUSTOM_AUTH` | Lambda trigger-based |
| `ALLOW_REFRESH_TOKEN_AUTH` | Token refresh |
| `ALLOW_ADMIN_USER_PASSWORD_AUTH` | Admin-initiated auth |

**For Mobile Apps (no secret):**
```bash
aws cognito-idp create-user-pool-client \
  --user-pool-id us-east-1_EXAMPLE \
  --client-name "MobileClient" \
  --no-generate-secret \
  --explicit-auth-flows ALLOW_USER_SRP_AUTH ALLOW_REFRESH_TOKEN_AUTH
```

---

## Identity Pool

### Create Identity Pool

```bash
aws cognito-identity create-identity-pool \
  --identity-pool-name "MyAppIdentityPool" \
  --no-allow-unauthenticated-identities \
  --cognito-identity-providers \
    ProviderName="cognito-idp.us-east-1.amazonaws.com/us-east-1_EXAMPLE",ClientId="your-client-id",ServerSideTokenCheck=true
```

**With Social Providers:**
```bash
aws cognito-identity create-identity-pool \
  --identity-pool-name "MyAppIdentityPool" \
  --allow-unauthenticated-identities \
  --supported-login-providers graph.facebook.com="facebook-app-id",accounts.google.com="google-client-id",appleid.apple.com="apple-service-id"
```

---

## Identity Providers

### Google

```bash
aws cognito-idp create-identity-provider \
  --user-pool-id us-east-1_EXAMPLE \
  --provider-name Google \
  --provider-type Google \
  --provider-details \
    authorize_scopes="email profile openid",\
    client_id="YOUR_GOOGLE_CLIENT_ID.apps.googleusercontent.com",\
    client_secret="YOUR_GOOGLE_CLIENT_SECRET" \
  --attribute-mapping email=email,name=name,picture=picture
```

### Sign In With Apple

```bash
aws cognito-idp create-identity-provider \
  --user-pool-id us-east-1_EXAMPLE \
  --provider-name SignInWithApple \
  --provider-type SignInWithApple \
  --provider-details \
    authorize_scopes="email name",\
    client_id="com.example.app",\
    team_id="YOUR_TEAM_ID",\
    key_id="YOUR_KEY_ID",\
    private_key="YOUR_PRIVATE_KEY_CONTENTS" \
  --attribute-mapping email=email,name=name
```

### Facebook

```bash
aws cognito-idp create-identity-provider \
  --user-pool-id us-east-1_EXAMPLE \
  --provider-name Facebook \
  --provider-type Facebook \
  --provider-details \
    api_version="v17.0",\
    authorize_scopes="public_profile,email",\
    client_id="YOUR_FACEBOOK_APP_ID",\
    client_secret="YOUR_FACEBOOK_APP_SECRET" \
  --attribute-mapping email=email,name=name,picture=picture
```

### Login With Amazon

```bash
aws cognito-idp create-identity-provider \
  --user-pool-id us-east-1_EXAMPLE \
  --provider-name LoginWithAmazon \
  --provider-type LoginWithAmazon \
  --provider-details \
    authorize_scopes="profile postal_code",\
    client_id="amzn1.application-oa2-client.EXAMPLE",\
    client_secret="YOUR_AMAZON_CLIENT_SECRET" \
  --attribute-mapping email=email,name=name
```

### OIDC Provider

```bash
aws cognito-idp create-identity-provider \
  --user-pool-id us-east-1_EXAMPLE \
  --provider-name MyOIDC \
  --provider-type OIDC \
  --provider-details \
    authorize_scopes="openid profile email",\
    client_id="YOUR_CLIENT_ID",\
    client_secret="YOUR_CLIENT_SECRET",\
    oidc_issuer="https://auth.example.com",\
    attributes_request_method="GET" \
  --attribute-mapping email=email,name=name
```

### SAML Provider

```bash
aws cognito-idp create-identity-provider \
  --user-pool-id us-east-1_EXAMPLE \
  --provider-name MySAML \
  --provider-type SAML \
  --provider-details \
    MetadataURL="https://idp.example.com/metadata.xml",\
    IDPSignout="true" \
  --attribute-mapping email=emailaddress
```

---

## Domain Setup

### Prefix Domain (Cognito Hosted)

```bash
aws cognito-idp create-user-pool-domain \
  --user-pool-id us-east-1_EXAMPLE \
  --domain myapp-auth
```

Result URL: `https://myapp-auth.auth.us-east-1.amazoncognito.com`

### Custom Domain

```bash
aws cognito-idp create-user-pool-domain \
  --user-pool-id us-east-1_EXAMPLE \
  --domain auth.example.com \
  --custom-domain-config CertificateArn=arn:aws:acm:us-east-1:123456789012:certificate/EXAMPLE
```

**Note:** Certificate must be in us-east-1.

### Managed Login Version

```bash
# Version 2 = Modern managed login
aws cognito-idp create-user-pool-domain \
  --user-pool-id us-east-1_EXAMPLE \
  --domain myapp-auth \
  --managed-login-version 2
```

---

## User Management

### Admin Create User

```bash
aws cognito-idp admin-create-user \
  --user-pool-id us-east-1_EXAMPLE \
  --username user@example.com \
  --user-attributes Name=email,Value=user@example.com Name=email_verified,Value=true \
  --temporary-password "TempPass123!" \
  --message-action SUPPRESS
```

### Admin Set Password

```bash
aws cognito-idp admin-set-user-password \
  --user-pool-id us-east-1_EXAMPLE \
  --username user@example.com \
  --password "NewPassword123!" \
  --permanent
```

### List Users

```bash
aws cognito-idp list-users \
  --user-pool-id us-east-1_EXAMPLE \
  --filter "email ^= \"test\""
```

### Admin Disable/Enable User

```bash
aws cognito-idp admin-disable-user --user-pool-id us-east-1_EXAMPLE --username user@example.com
aws cognito-idp admin-enable-user --user-pool-id us-east-1_EXAMPLE --username user@example.com
```

### Admin Delete User

```bash
aws cognito-idp admin-delete-user --user-pool-id us-east-1_EXAMPLE --username user@example.com
```

---

## Complete Setup Script Example

```bash
#!/bin/bash
REGION="us-east-1"
POOL_NAME="MyApp"

# 1. Create User Pool
POOL_ID=$(aws cognito-idp create-user-pool \
  --pool-name "$POOL_NAME" \
  --username-attributes email \
  --auto-verified-attributes email \
  --mfa-configuration OPTIONAL \
  --query 'UserPool.Id' --output text)

echo "Created User Pool: $POOL_ID"

# 2. Create Domain
aws cognito-idp create-user-pool-domain \
  --user-pool-id $POOL_ID \
  --domain "${POOL_NAME,,}-auth"

# 3. Create App Client (for mobile - no secret)
CLIENT_ID=$(aws cognito-idp create-user-pool-client \
  --user-pool-id $POOL_ID \
  --client-name "${POOL_NAME}Mobile" \
  --no-generate-secret \
  --explicit-auth-flows ALLOW_USER_SRP_AUTH ALLOW_REFRESH_TOKEN_AUTH \
  --callback-urls "myapp://callback" \
  --logout-urls "myapp://logout" \
  --allowed-o-auth-flows code \
  --allowed-o-auth-scopes openid email profile \
  --allowed-o-auth-flows-user-pool-client \
  --query 'UserPoolClient.ClientId' --output text)

echo "Created Client: $CLIENT_ID"

# 4. Create Identity Pool
IDENTITY_POOL_ID=$(aws cognito-identity create-identity-pool \
  --identity-pool-name "${POOL_NAME}Identity" \
  --no-allow-unauthenticated-identities \
  --cognito-identity-providers ProviderName="cognito-idp.${REGION}.amazonaws.com/${POOL_ID}",ClientId="$CLIENT_ID",ServerSideTokenCheck=true \
  --query 'IdentityPoolId' --output text)

echo "Created Identity Pool: $IDENTITY_POOL_ID"

echo "Configuration:"
echo "  User Pool ID: $POOL_ID"
echo "  Client ID: $CLIENT_ID"
echo "  Identity Pool ID: $IDENTITY_POOL_ID"
echo "  Domain: https://${POOL_NAME,,}-auth.auth.${REGION}.amazoncognito.com"
```
