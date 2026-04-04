# Facebook Privacy & Security

## Table of Contents
1. [Privacy Settings](#privacy-settings)
2. [Account Security](#account-security)
3. [Ad Preferences & Data Control](#ad-preferences--data-control)
4. [Off-Facebook Activity](#off-facebook-activity)
5. [Privacy Checkup Tool](#privacy-checkup-tool)
6. [Managing Apps & Permissions](#managing-apps--permissions)

---

## Privacy Settings

**Access:** Settings & Privacy → Privacy Settings

### Who Can See Your Content
| Setting | Path | Options |
|---|---|---|
| Future posts default | Privacy Settings → Your Activity | Public, Friends, Friends except, Only me |
| Profile visibility | Profile → Edit Profile | Per-section: public/friends/only me |
| Friends list | Settings → Privacy → Who can see your friends list | Public, Friends, Only me |
| Pages you follow | Settings → Privacy | Public, Friends, Only me |

### Who Can Find You
| Setting | Options |
|---|---|
| Who can send you friend requests | Everyone / Friends of Friends |
| Who can look you up by email | Everyone / Friends of Friends / Friends |
| Who can look you up by phone | Everyone / Friends of Friends / Friends |
| Search engine linking | Allow / Don't allow |

**Recommended:** Set email/phone lookup to "Friends of Friends" or "Friends" to prevent spam accounts from finding you.

### Limiting Past Posts
- Settings → Privacy → Limit Past Posts → "Limit Past Posts"
- Changes all historical public posts to "Friends" visibility
- **Irreversible in bulk** — to make individual posts public again, edit each post separately

### Tagging Controls
- Settings → Profile and Tagging
- **Review tags**: Approve tags before they appear on your profile
- **Who can post on your profile**: Friends only (or turn off completely)
- **Who can see posts you're tagged in**: Friends, Only me

---

## Account Security

### Two-Factor Authentication (2FA)
**Path:** Settings → Security and Login → Two-Factor Authentication

**Methods (ranked by security):**
1. **Authenticator App** (Google Authenticator, Duo, Authy) — most secure
2. **Security Key** (hardware FIDO2 key) — highest security
3. **SMS/Text Message** — convenient but vulnerable to SIM swap attacks

**Recommendation:** Use an authenticator app, not SMS.

### Login Alerts
- Settings → Security and Login → Get alerts about unrecognized logins
- Enable notifications via Facebook, email, and/or Messenger
- Check "Where You're Logged In" to see all active sessions — remove unrecognized devices

### Passkeys (2026)
Facebook now supports Passkeys for login:
- Settings → Security and Login → Passkeys
- Uses Face ID, Touch ID, or device PIN instead of password
- Phishing-resistant — recommended for all users

### Password Best Practices
- Use a unique, strong password (20+ chars, random)
- Store in a password manager (1Password, Bitwarden, etc.)
- Change immediately if you receive a login alert from an unknown location

### Trusted Contacts
- Settings → Security and Login → Choose 3–5 Trusted Contacts
- Facebook gives them account recovery codes if you're locked out

### Recovering a Hacked Account
1. facebook.com/hacked → "My account is compromised"
2. Follow steps to secure and recover access
3. If email was changed: check original email for a "your email was changed" message — Facebook gives 24 hours to reverse it

---

## Ad Preferences & Data Control

**Access:** Settings → Ads → Ad Preferences

### What You Can Control
| Setting | Description |
|---|---|
| **Interests** | View and remove interest categories Meta uses to target you |
| **Advertisers** | See who has uploaded your data; hide their ads |
| **Ad Topics** | Reduce specific topics (e.g., alcohol, parenting) |
| **Data About Your Activity** | Toggle whether Facebook uses relationship status, employer, job title, education for ads |

### Hiding Specific Advertisers
- Settings → Ads → Advertisers and Businesses → Advertisers Who Have Run Ads Using Your Info
- Click any advertiser → "See fewer of their ads" or "Remove their data"

### Social Ads
- Settings → Ads → Social Actions in Ads
- Controls whether your name/photo appears in ads shown to your friends ("Jane likes X brand")
- Recommended: set to "No one"

---

## Off-Facebook Activity

**Access:** Settings → Your Facebook Information → Off-Facebook Activity

Shows which websites and apps are sending data about you to Facebook (via Pixel, SDK, etc.).

### Managing Off-Facebook Activity
1. View the list of businesses tracking you
2. Click **"Manage Future Activity"** → Toggle off **"Future Off-Facebook Activity"**
3. This disconnects your browsing behavior from ad targeting going forward
4. **Note**: Disabling this reduces ad relevance but does not stop tracking — it only stops Meta from using the data for your ad profile

### Clearing Off-Facebook Activity
- Click **"Clear History"** to disconnect your past browsing from your profile
- This doesn't delete the data — it only unlinks it from your account

---

## Privacy Checkup Tool

**Access:** Settings → Privacy Checkup (or search "Privacy Checkup" in Facebook search)

Walks through key settings in 5 steps:
1. Who can see what you share
2. How to keep your account secure
3. How people can find you on Facebook
4. Your data settings on Facebook
5. Your privacy on Facebook's other products

**Recommended frequency:** Run the Privacy Checkup quarterly — Facebook regularly adds new settings that default to public/permissive.

---

## Managing Apps & Permissions

**Access:** Settings → Apps and Websites

Shows all third-party apps connected to your Facebook account.

### Audit Steps
1. Review list of Active apps — remove any you don't recognize or use
2. Click each app to see what permissions it has (posts, friends list, email, etc.)
3. Click **"Remove"** to revoke access
4. Consider removing ALL non-essential app connections

### Permissions Apps Commonly Request
- `email` — access your email address
- `public_profile` — basic profile info
- `user_friends` — mutual friends list
- `user_posts` — read your posts
- `publish_actions` — post on your behalf (highest risk — revoke unless intentional)

**Best practice:** Remove all apps you haven't used in 90 days. Reconnect only as needed.
