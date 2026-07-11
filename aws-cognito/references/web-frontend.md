# Web Frontend Integration

Two supported paths for browser apps: **Amplify JS v6** (higher-level, handles tokens/refresh) and **amazon-cognito-identity-js** (lower-level, SRP without Amplify). Plus the raw OAuth redirect for hosted UI. For the OAuth endpoint details see [managed-login.md](managed-login.md); for token verification (done server-side) see [backend.md](backend.md).

## Table of Contents
1. [Which approach](#which-approach)
2. [Amplify JS v6](#amplify-js-v6)
3. [amazon-cognito-identity-js](#amazon-cognito-identity-js)
4. [Raw OAuth redirect (no library)](#raw-oauth-redirect)
5. [Token storage & security](#token-storage--security)

---

## Which approach

| Need | Use |
|---|---|
| Full auth UX (sign-up, MFA, social, refresh) with least code | **Amplify JS v6** |
| Password/SRP + custom UI, no Amplify dependency | **amazon-cognito-identity-js** |
| Only redirect to hosted UI / managed login | Raw OAuth + PKCE, or Amplify's `signInWithRedirect` |
| Client must call AWS services (S3, etc.) | Amplify + an identity pool ([identity-pools.md](identity-pools.md)) |

Public browser clients: **no app-client secret**, and use **PKCE** for the OAuth code flow.

## Amplify JS v6

```bash
npm install aws-amplify
```

Configure once at app start:
```js
import { Amplify } from "aws-amplify";

Amplify.configure({
  Auth: {
    Cognito: {
      userPoolId: "us-east-1_EXAMPLE",
      userPoolClientId: "1example23456789",
      loginWith: {
        oauth: {
          domain: "myapp-auth.auth.us-east-1.amazoncognito.com",
          scopes: ["openid", "email", "profile"],
          redirectSignIn: ["https://app.example.com/"],
          redirectSignOut: ["https://app.example.com/"],
          responseType: "code",          // authorization code + PKCE
        },
      },
    },
  },
});
```

Auth calls (v6 uses standalone functions, not `Auth.*`):
```js
import {
  signUp, confirmSignUp, signIn, confirmSignIn, signOut,
  getCurrentUser, fetchAuthSession, resetPassword, confirmResetPassword,
  signInWithRedirect,
} from "aws-amplify/auth";

// Sign up (email/password)
await signUp({
  username: email,
  password,
  options: { userAttributes: { email } },
});
await confirmSignUp({ username: email, confirmationCode: code });

// Sign in — may return a next step (MFA, new password, etc.)
const { isSignedIn, nextStep } = await signIn({ username: email, password });
if (nextStep.signInStep === "CONFIRM_SIGN_IN_WITH_TOTP_CODE") {
  await confirmSignIn({ challengeResponse: totpCode });
}

// Social / hosted UI
await signInWithRedirect({ provider: "Google" });

// Get tokens (auto-refreshes)
const session = await fetchAuthSession();
const accessToken = session.tokens?.accessToken?.toString();  // send as Bearer
const idToken = session.tokens?.idToken?.toString();

// Password reset
await resetPassword({ username: email });
await confirmResetPassword({ username: email, confirmationCode: code, newPassword });

await signOut();  // add { global: true } to revoke all sessions
```

Amplify stores and refreshes tokens for you and exposes them via `fetchAuthSession()`. Always send the **access token** to your API; verify it server-side.

### Amplify Authenticator (drop-in UI)

If you don't want to build sign-in screens *or* redirect to managed login, the **Authenticator** connected component renders a full themeable sign-up/sign-in/MFA/reset UI in your own app. Available for React, Angular, Vue, React Native, Swift, Android, Flutter.

```jsx
import { Authenticator } from "@aws-amplify/ui-react";
import "@aws-amplify/ui-react/styles.css";

export default function App() {
  return (
    <Authenticator socialProviders={["google"]}>
      {({ signOut, user }) => (
        <>
          <p>Hello {user?.username}</p>
          <button onClick={signOut}>Sign out</button>
        </>
      )}
    </Authenticator>
  );
}
```
Use it when you want Amplify's UX with your branding but none of the wiring; drop to the function API above when you need full control of the screens.

## amazon-cognito-identity-js

Lower-level; implements SRP so the password never leaves the browser. No Amplify.

```bash
npm install amazon-cognito-identity-js
```

```js
import {
  CognitoUserPool, CognitoUser, AuthenticationDetails, CognitoUserAttribute,
} from "amazon-cognito-identity-js";

const pool = new CognitoUserPool({
  UserPoolId: "us-east-1_EXAMPLE",
  ClientId: "1example23456789",
});

// Sign up
pool.signUp(email, password, [new CognitoUserAttribute({ Name: "email", Value: email })], null,
  (err, res) => { /* res.userSub */ });

// Confirm
new CognitoUser({ Username: email, Pool: pool })
  .confirmRegistration(code, true, (err, res) => {});

// Sign in (SRP)
const user = new CognitoUser({ Username: email, Pool: pool });
user.authenticateUser(
  new AuthenticationDetails({ Username: email, Password: password }),
  {
    onSuccess: (session) => {
      const accessToken = session.getAccessToken().getJwtToken();
      const idToken = session.getIdToken().getJwtToken();
    },
    onFailure: (err) => {},
    newPasswordRequired: (attrs) => user.completeNewPasswordChallenge(newPw, {}, this),
    totpRequired: () => user.sendMFACode(totp, this, "SOFTWARE_TOKEN_MFA"),
  }
);

// Current session (refreshes if needed)
pool.getCurrentUser()?.getSession((err, session) => {
  if (session?.isValid()) { /* session.getAccessToken().getJwtToken() */ }
});
```

## Raw OAuth redirect

No library — just the browser navigating to the hosted UI with PKCE. See [managed-login.md](managed-login.md) for the full endpoint spec. Skeleton:

```js
// 1. PKCE verifier + challenge
const verifier = base64url(crypto.getRandomValues(new Uint8Array(32)));
const challenge = base64url(await crypto.subtle.digest("SHA-256", new TextEncoder().encode(verifier)));
sessionStorage.setItem("pkce", verifier);
const state = crypto.randomUUID();
sessionStorage.setItem("state", state);

// 2. Redirect to /authorize
location.href = `https://<domain>/oauth2/authorize?response_type=code`
  + `&client_id=${CLIENT_ID}&redirect_uri=${encodeURIComponent(CALLBACK)}`
  + `&scope=openid+email+profile&state=${state}`
  + `&code_challenge=${challenge}&code_challenge_method=S256`;

// 3. On /callback: check state, POST code + verifier to /oauth2/token, store tokens.
```

## Token storage & security

- Prefer **in-memory** access tokens; keep the refresh token in an **httpOnly, Secure, SameSite** cookie set by your backend (BFF pattern) when you can.
- `localStorage` is XSS-exposed. Amplify defaults to it for convenience; accept the tradeoff knowingly, and keep a strong CSP.
- **Never verify tokens in the browser for authorization** — the browser can't be trusted. Verification is a server-side gate ([backend.md](backend.md)).
- Send the **access token** (`Authorization: Bearer …`) to APIs; the ID token is for reading identity in the UI only.
- Short access-token lifetimes (15–60 min) + refresh reduce the blast radius of a leaked token.
