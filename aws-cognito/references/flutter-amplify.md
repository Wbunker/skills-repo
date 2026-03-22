# Flutter Amplify Auth Integration

## Table of Contents
1. [Setup](#setup)
2. [Sign Up](#sign-up)
3. [Sign In](#sign-in)
4. [Sign Out](#sign-out)
5. [Social Sign-In](#social-sign-in)
6. [Password Management](#password-management)
7. [MFA](#mfa)
8. [Session & User Info](#session--user-info)
9. [Platform Configuration](#platform-configuration)
10. [Using Existing Cognito Resources](#using-existing-cognito-resources)

---

## Setup

### Dependencies (pubspec.yaml)

```yaml
dependencies:
  amplify_flutter: ^2.0.0
  amplify_auth_cognito: ^2.0.0
  amplify_authenticator: ^2.0.0  # Optional: pre-built UI
```

### Initialize Amplify

```dart
import 'package:amplify_flutter/amplify_flutter.dart';
import 'package:amplify_auth_cognito/amplify_auth_cognito.dart';
import 'amplify_outputs.dart';  // Generated config file

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await _configureAmplify();
  runApp(const MyApp());
}

Future<void> _configureAmplify() async {
  try {
    await Amplify.addPlugin(AmplifyAuthCognito());
    await Amplify.configure(amplifyConfig);
    safePrint('Amplify configured successfully');
  } on Exception catch (e) {
    safePrint('Error configuring Amplify: $e');
  }
}
```

### With Authenticator UI

```dart
class MyApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Authenticator(
      child: MaterialApp(
        builder: Authenticator.builder(),
        home: const HomeScreen(),
      ),
    );
  }
}
```

---

## Sign Up

### Basic Sign Up

```dart
Future<void> signUpUser({
  required String username,
  required String password,
  required String email,
  String? phoneNumber,
}) async {
  try {
    final userAttributes = {
      AuthUserAttributeKey.email: email,
      if (phoneNumber != null) AuthUserAttributeKey.phoneNumber: phoneNumber,
    };
    final result = await Amplify.Auth.signUp(
      username: username,
      password: password,
      options: SignUpOptions(userAttributes: userAttributes),
    );
    await _handleSignUpResult(result);
  } on AuthException catch (e) {
    safePrint('Error signing up: ${e.message}');
  }
}

Future<void> _handleSignUpResult(SignUpResult result) async {
  switch (result.nextStep.signUpStep) {
    case AuthSignUpStep.confirmSignUp:
      final codeDeliveryDetails = result.nextStep.codeDeliveryDetails!;
      safePrint('Confirmation code sent to ${codeDeliveryDetails.destination}');
      break;
    case AuthSignUpStep.done:
      safePrint('Sign up complete');
      break;
  }
}
```

### Confirm Sign Up

```dart
Future<void> confirmUser({
  required String username,
  required String confirmationCode,
}) async {
  try {
    final result = await Amplify.Auth.confirmSignUp(
      username: username,
      confirmationCode: confirmationCode,
    );
    await _handleSignUpResult(result);
  } on AuthException catch (e) {
    safePrint('Error confirming user: ${e.message}');
  }
}
```

### Resend Confirmation Code

```dart
Future<void> resendSignUpCode(String username) async {
  try {
    final result = await Amplify.Auth.resendSignUpCode(username: username);
    safePrint('Code resent to ${result.codeDeliveryDetails.destination}');
  } on AuthException catch (e) {
    safePrint('Error resending code: ${e.message}');
  }
}
```

---

## Sign In

### Basic Sign In

```dart
Future<void> signInUser(String username, String password) async {
  try {
    final result = await Amplify.Auth.signIn(
      username: username,
      password: password,
    );
    await _handleSignInResult(result);
  } on AuthException catch (e) {
    safePrint('Error signing in: ${e.message}');
  }
}
```

### Handle Sign In Result (Multi-Step)

```dart
Future<void> _handleSignInResult(SignInResult result) async {
  switch (result.nextStep.signInStep) {
    case AuthSignInStep.confirmSignInWithSmsMfaCode:
      final codeDeliveryDetails = result.nextStep.codeDeliveryDetails!;
      safePrint('SMS code sent to ${codeDeliveryDetails.destination}');
      break;

    case AuthSignInStep.confirmSignInWithTotpMfaCode:
      safePrint('Enter TOTP code from authenticator app');
      break;

    case AuthSignInStep.continueSignInWithMfaSelection:
      final allowedMfaTypes = result.nextStep.allowedMfaTypes!;
      safePrint('Select MFA method: $allowedMfaTypes');
      break;

    case AuthSignInStep.continueSignInWithTotpSetup:
      final totpSetupDetails = result.nextStep.totpSetupDetails!;
      final setupUri = totpSetupDetails.getSetupUri(appName: 'MyApp');
      safePrint('Setup TOTP with URI: $setupUri');
      break;

    case AuthSignInStep.confirmSignInWithNewPassword:
      safePrint('Please set a new password');
      break;

    case AuthSignInStep.confirmSignInWithCustomChallenge:
      final parameters = result.nextStep.additionalInfo;
      safePrint('Custom challenge: $parameters');
      break;

    case AuthSignInStep.resetPassword:
      safePrint('Password reset required');
      break;

    case AuthSignInStep.confirmSignUp:
      safePrint('User needs to confirm sign up first');
      break;

    case AuthSignInStep.done:
      safePrint('Sign in complete');
      break;
  }
}
```

### Confirm Sign In (MFA/Challenge)

```dart
Future<void> confirmSignIn(String confirmationValue) async {
  try {
    final result = await Amplify.Auth.confirmSignIn(
      confirmationValue: confirmationValue,
    );
    await _handleSignInResult(result);
  } on AuthException catch (e) {
    safePrint('Error confirming sign in: ${e.message}');
  }
}
```

### Select MFA Method

```dart
Future<void> selectMfaMethod(MfaType selection) async {
  try {
    final result = await Amplify.Auth.confirmSignIn(
      confirmationValue: selection.confirmationValue,
    );
    await _handleSignInResult(result);
  } on AuthException catch (e) {
    safePrint('Error selecting MFA: ${e.message}');
  }
}
```

---

## Sign Out

### Local Sign Out

```dart
Future<void> signOutCurrentUser() async {
  final result = await Amplify.Auth.signOut();
  if (result is CognitoCompleteSignOut) {
    safePrint('Sign out completed successfully');
  } else if (result is CognitoFailedSignOut) {
    safePrint('Error signing out: ${result.exception.message}');
  }
}
```

### Global Sign Out (All Devices)

```dart
Future<void> signOutGlobally() async {
  final result = await Amplify.Auth.signOut(
    options: const SignOutOptions(globalSignOut: true),
  );
  if (result is CognitoCompleteSignOut) {
    safePrint('Global sign out completed');
  } else if (result is CognitoPartialSignOut) {
    safePrint('Partial sign out: ${result.globalSignOutException?.message}');
  } else if (result is CognitoFailedSignOut) {
    safePrint('Error: ${result.exception.message}');
  }
}
```

---

## Social Sign-In

### Sign In With Web UI

```dart
// Generic (shows all configured providers)
Future<void> signInWithWebUI() async {
  try {
    final result = await Amplify.Auth.signInWithWebUI();
    safePrint('Sign in result: $result');
  } on AuthException catch (e) {
    safePrint('Error: ${e.message}');
  }
}

// Specific provider
Future<void> signInWithGoogle() async {
  try {
    final result = await Amplify.Auth.signInWithWebUI(
      provider: AuthProvider.google,
    );
    safePrint('Signed in with Google');
  } on AuthException catch (e) {
    safePrint('Error: ${e.message}');
  }
}

Future<void> signInWithApple() async {
  try {
    final result = await Amplify.Auth.signInWithWebUI(
      provider: AuthProvider.apple,
    );
    safePrint('Signed in with Apple');
  } on AuthException catch (e) {
    safePrint('Error: ${e.message}');
  }
}

Future<void> signInWithFacebook() async {
  try {
    final result = await Amplify.Auth.signInWithWebUI(
      provider: AuthProvider.facebook,
    );
    safePrint('Signed in with Facebook');
  } on AuthException catch (e) {
    safePrint('Error: ${e.message}');
  }
}

Future<void> signInWithAmazon() async {
  try {
    final result = await Amplify.Auth.signInWithWebUI(
      provider: AuthProvider.amazon,
    );
    safePrint('Signed in with Amazon');
  } on AuthException catch (e) {
    safePrint('Error: ${e.message}');
  }
}
```

### iOS Private Session (Skip Browser Permission Dialog)

```dart
Future<void> signInWithWebUIPrivate() async {
  await Amplify.Auth.signInWithWebUI(
    options: const SignInWithWebUIOptions(
      pluginOptions: CognitoSignInWithWebUIPluginOptions(
        isPreferPrivateSession: true,
      ),
    ),
  );
}
```

---

## Password Management

### Reset Password (Forgot Password)

```dart
Future<void> resetPassword(String username) async {
  try {
    final result = await Amplify.Auth.resetPassword(username: username);
    await _handleResetPasswordResult(result);
  } on AuthException catch (e) {
    safePrint('Error: ${e.message}');
  }
}

Future<void> _handleResetPasswordResult(ResetPasswordResult result) async {
  switch (result.nextStep.updateStep) {
    case AuthResetPasswordStep.confirmResetPasswordWithCode:
      final codeDeliveryDetails = result.nextStep.codeDeliveryDetails!;
      safePrint('Code sent to ${codeDeliveryDetails.destination}');
      break;
    case AuthResetPasswordStep.done:
      safePrint('Password reset complete');
      break;
  }
}
```

### Confirm Reset Password

```dart
Future<void> confirmResetPassword({
  required String username,
  required String newPassword,
  required String confirmationCode,
}) async {
  try {
    final result = await Amplify.Auth.confirmResetPassword(
      username: username,
      newPassword: newPassword,
      confirmationCode: confirmationCode,
    );
    safePrint('Password reset: ${result.isPasswordReset}');
  } on AuthException catch (e) {
    safePrint('Error: ${e.message}');
  }
}
```

### Update Password (Signed-In User)

```dart
Future<void> updatePassword({
  required String oldPassword,
  required String newPassword,
}) async {
  try {
    await Amplify.Auth.updatePassword(
      oldPassword: oldPassword,
      newPassword: newPassword,
    );
    safePrint('Password updated successfully');
  } on AuthException catch (e) {
    safePrint('Error: ${e.message}');
  }
}
```

---

## MFA

### Setup TOTP

```dart
Future<void> setUpTotp() async {
  try {
    final totpSetupDetails = await Amplify.Auth.setUpTotp();
    final setupUri = totpSetupDetails.getSetupUri(appName: 'MyApp');
    safePrint('TOTP Setup URI: $setupUri');
    // Display QR code from setupUri for user to scan
  } on AuthException catch (e) {
    safePrint('Error: $e');
  }
}

Future<void> verifyTotpSetup(String totpCode) async {
  try {
    await Amplify.Auth.verifyTotpSetup(totpCode);
    safePrint('TOTP verified successfully');
  } on AuthException catch (e) {
    safePrint('Error: $e');
  }
}
```

### Get/Update MFA Preferences

```dart
Future<void> getMfaPreference() async {
  final cognitoPlugin = Amplify.Auth.getPlugin(AmplifyAuthCognito.pluginKey);
  final currentPreference = await cognitoPlugin.fetchMfaPreference();
  safePrint('Enabled: ${currentPreference.enabled}');
  safePrint('Preferred: ${currentPreference.preferred}');
}

Future<void> updateMfaPreferences() async {
  final cognitoPlugin = Amplify.Auth.getPlugin(AmplifyAuthCognito.pluginKey);
  await cognitoPlugin.updateMfaPreference(
    sms: MfaPreference.enabled,
    totp: MfaPreference.preferred,
  );
}
```

---

## Session & User Info

### Check Auth Status

```dart
Future<bool> isUserSignedIn() async {
  final result = await Amplify.Auth.fetchAuthSession();
  return result.isSignedIn;
}
```

### Get Current User

```dart
Future<AuthUser> getCurrentUser() async {
  final user = await Amplify.Auth.getCurrentUser();
  safePrint('User ID: ${user.userId}');
  safePrint('Username: ${user.username}');
  return user;
}
```

### Fetch Auth Session with Credentials

```dart
Future<void> fetchSession() async {
  try {
    final session = await Amplify.Auth.fetchAuthSession() as CognitoAuthSession;
    safePrint('Is signed in: ${session.isSignedIn}');
    safePrint('Access Token: ${session.userPoolTokensResult.value.accessToken.raw}');
    safePrint('ID Token: ${session.userPoolTokensResult.value.idToken.raw}');
    safePrint('Refresh Token: ${session.userPoolTokensResult.value.refreshToken}');

    // AWS credentials (if identity pool configured)
    final credentials = session.credentialsResult.value;
    safePrint('AWS Access Key: ${credentials.accessKeyId}');
  } on AuthException catch (e) {
    safePrint('Error: ${e.message}');
  }
}
```

### Fetch User Attributes

```dart
Future<void> fetchUserAttributes() async {
  try {
    final attributes = await Amplify.Auth.fetchUserAttributes();
    for (final attribute in attributes) {
      safePrint('${attribute.userAttributeKey.key}: ${attribute.value}');
    }
  } on AuthException catch (e) {
    safePrint('Error: ${e.message}');
  }
}
```

### Update User Attribute

```dart
Future<void> updateUserEmail(String newEmail) async {
  try {
    final result = await Amplify.Auth.updateUserAttribute(
      userAttributeKey: AuthUserAttributeKey.email,
      value: newEmail,
    );
    if (result.nextStep.updateAttributeStep == AuthUpdateAttributeStep.confirmAttributeWithCode) {
      safePrint('Confirmation code sent');
    }
  } on AuthException catch (e) {
    safePrint('Error: ${e.message}');
  }
}
```

---

## Platform Configuration

### Android (AndroidManifest.xml)

```xml
<manifest>
  <!-- Required for web UI sign-in -->
  <queries>
    <intent>
      <action android:name="android.support.customtabs.action.CustomTabsService" />
    </intent>
  </queries>

  <application>
    <activity android:name=".MainActivity" android:exported="true">
      <!-- Deep link handling for OAuth callback -->
      <intent-filter>
        <action android:name="android.intent.action.VIEW" />
        <category android:name="android.intent.category.DEFAULT" />
        <category android:name="android.intent.category.BROWSABLE" />
        <data android:scheme="myapp" />
      </intent-filter>
    </activity>
  </application>
</manifest>
```

### iOS (Info.plist)

```xml
<!-- Add URL scheme for OAuth callback -->
<key>CFBundleURLTypes</key>
<array>
  <dict>
    <key>CFBundleURLSchemes</key>
    <array>
      <string>myapp</string>
    </array>
  </dict>
</array>
```

### macOS

Enable in Xcode: **Signing & Capabilities** → **App Sandbox** → **Network** → **Incoming Connections (Server)**

### Web

Run with specific port:
```bash
flutter run -d chrome --web-port=3000
```

---

## Using Existing Cognito Resources

### Manual Configuration (amplifyconfiguration.dart)

```dart
const amplifyconfig = '''{
  "auth": {
    "plugins": {
      "awsCognitoAuthPlugin": {
        "IdentityManager": {
          "Default": {}
        },
        "CredentialsProvider": {
          "CognitoIdentity": {
            "Default": {
              "PoolId": "us-east-1:xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
              "Region": "us-east-1"
            }
          }
        },
        "CognitoUserPool": {
          "Default": {
            "PoolId": "us-east-1_XXXXXXXXX",
            "AppClientId": "xxxxxxxxxxxxxxxxxxxxxxxxxx",
            "Region": "us-east-1"
          }
        },
        "Auth": {
          "Default": {
            "authenticationFlowType": "USER_SRP_AUTH",
            "OAuth": {
              "WebDomain": "myapp-auth.auth.us-east-1.amazoncognito.com",
              "AppClientId": "xxxxxxxxxxxxxxxxxxxxxxxxxx",
              "SignInRedirectURI": "myapp://callback/",
              "SignOutRedirectURI": "myapp://signout/",
              "Scopes": ["email", "openid", "profile"]
            }
          }
        }
      }
    }
  }
}''';
```

**Authentication Flow Types:**
- `USER_SRP_AUTH` - Secure Remote Password (recommended)
- `USER_PASSWORD_AUTH` - Plain password
- `CUSTOM_AUTH` - Lambda-based custom auth
