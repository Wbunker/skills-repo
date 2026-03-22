---
name: aws-cognito
description: AWS Cognito authentication setup via CLI and Flutter/Amplify integration. Use when setting up user authentication for web/mobile apps including email/phone/password login, social sign-in (Google, Apple, Facebook, Amazon), MFA, and OAuth flows. Covers CLI commands for user pools, identity pools, identity providers, and domains. Includes Flutter Amplify SDK code for signUp, signIn, signOut, password reset, and social authentication.
---

# AWS Cognito Authentication

## Quick Start Workflow

### 1. Create User Pool (CLI)

```bash
aws cognito-idp create-user-pool \
  --pool-name "MyApp" \
  --username-attributes email \
  --auto-verified-attributes email \
  --mfa-configuration OPTIONAL \
  --policies 'PasswordPolicy={MinimumLength=8,RequireUppercase=true,RequireLowercase=true,RequireNumbers=true,RequireSymbols=false}'
```

### 2. Create Domain

```bash
aws cognito-idp create-user-pool-domain \
  --user-pool-id us-east-1_EXAMPLE \
  --domain myapp-auth
```

### 3. Create App Client (Mobile - No Secret)

```bash
aws cognito-idp create-user-pool-client \
  --user-pool-id us-east-1_EXAMPLE \
  --client-name "MobileClient" \
  --no-generate-secret \
  --explicit-auth-flows ALLOW_USER_SRP_AUTH ALLOW_REFRESH_TOKEN_AUTH \
  --callback-urls "myapp://callback" \
  --logout-urls "myapp://logout" \
  --allowed-o-auth-flows code \
  --allowed-o-auth-scopes openid email profile \
  --allowed-o-auth-flows-user-pool-client
```

### 4. Flutter Setup

```yaml
# pubspec.yaml
dependencies:
  amplify_flutter: ^2.0.0
  amplify_auth_cognito: ^2.0.0
```

```dart
// Initialize
await Amplify.addPlugin(AmplifyAuthCognito());
await Amplify.configure(amplifyConfig);

// Sign Up
await Amplify.Auth.signUp(
  username: email,
  password: password,
  options: SignUpOptions(userAttributes: {AuthUserAttributeKey.email: email}),
);

// Confirm
await Amplify.Auth.confirmSignUp(username: email, confirmationCode: code);

// Sign In
await Amplify.Auth.signIn(username: email, password: password);

// Sign Out
await Amplify.Auth.signOut();
```

---

## Reference Files

### CLI Commands
See [references/cli-commands.md](references/cli-commands.md) for:
- User pool creation with all parameters
- Identity pool setup
- App client configuration
- Identity provider CLI commands (Google, Apple, Facebook, OIDC, SAML)
- Domain setup (prefix and custom)
- User management commands

### Flutter/Amplify Integration
See [references/flutter-amplify.md](references/flutter-amplify.md) for:
- Full signUp/confirmSignUp flow
- Multi-step signIn handling (MFA, new password, challenges)
- Social signInWithWebUI
- Password reset/update
- MFA setup (TOTP, SMS)
- Session and token management
- Platform configuration (Android, iOS, Web)
- Manual Cognito configuration without Amplify CLI

### Social Provider Setup
See [references/social-providers.md](references/social-providers.md) for:
- Google OAuth setup (Cloud Console)
- Apple Sign In setup (Developer Portal, Services ID, Private Key)
- Facebook Login setup
- Amazon Login setup
- CLI commands for each provider
- Attribute mapping reference
- Testing and troubleshooting

---

## Common Patterns

### Email + Password + Social Login

```bash
# 1. Create user pool with email
aws cognito-idp create-user-pool --pool-name MyApp --username-attributes email

# 2. Add domain
aws cognito-idp create-user-pool-domain --user-pool-id $POOL_ID --domain myapp-auth

# 3. Add Google provider
aws cognito-idp create-identity-provider --user-pool-id $POOL_ID \
  --provider-name Google --provider-type Google \
  --provider-details authorize_scopes="email profile openid",client_id="...",client_secret="..."

# 4. Create client with all providers
aws cognito-idp create-user-pool-client --user-pool-id $POOL_ID \
  --client-name Mobile --no-generate-secret \
  --supported-identity-providers COGNITO Google \
  --callback-urls "myapp://callback" \
  --allowed-o-auth-flows code --allowed-o-auth-scopes openid email profile \
  --allowed-o-auth-flows-user-pool-client
```

### Phone + Email Login

```bash
aws cognito-idp create-user-pool \
  --pool-name MyApp \
  --alias-attributes email phone_number \
  --auto-verified-attributes email phone_number \
  --sms-configuration 'SnsCallerArn=arn:aws:iam::123456789012:role/CognitoSNSRole'
```

### Flutter Social Sign-In

```dart
// Google
await Amplify.Auth.signInWithWebUI(provider: AuthProvider.google);

// Apple
await Amplify.Auth.signInWithWebUI(provider: AuthProvider.apple);

// Facebook
await Amplify.Auth.signInWithWebUI(provider: AuthProvider.facebook);
```

---

## Key Configuration Values

| Setting | CLI Parameter | Flutter Config |
|---------|--------------|----------------|
| User Pool ID | Output of create-user-pool | `PoolId` in config |
| Client ID | Output of create-user-pool-client | `AppClientId` in config |
| Region | `--region` or AWS_REGION | `Region` in config |
| Domain | create-user-pool-domain | `WebDomain` in OAuth config |
| Callback URL | `--callback-urls` | `SignInRedirectURI` |

## Auth Flow Types

| Flow | When to Use |
|------|-------------|
| `USER_SRP_AUTH` | Default for password auth (secure) |
| `USER_PASSWORD_AUTH` | Simple but less secure |
| `CUSTOM_AUTH` | Lambda-based custom flows |
| `USER_AUTH` | Selection-based (passwordless + password) |
