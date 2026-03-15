# Identity Platform — CLI Reference

## Enable Identity Platform

```bash
# Enable Identity Toolkit API (Identity Platform)
gcloud services enable identitytoolkit.googleapis.com --project=my-project

# Enable Identity Platform (upgrade from Firebase Auth)
# Upgrading is done via the Cloud Console or REST API:
# Console: Firebase Console → Authentication → "Upgrade to Identity Platform"
# Or via REST:
TOKEN=$(gcloud auth print-access-token)
curl -s -X POST \
  -H "Authorization: Bearer ${TOKEN}" \
  "https://identitytoolkit.googleapis.com/v2/projects/my-project/identityPlatform:initializeAuth"

# Verify the API is enabled
gcloud services list --enabled --filter="name:identitytoolkit" --project=my-project
```

---

## Multi-Tenancy — Tenant Management

```bash
# Create a tenant
gcloud identity platform tenants create \
  --display-name="Acme Corp" \
  --project=my-project

# Note: --enable-email-link-signin, --allow-password-signup flags available
gcloud identity platform tenants create \
  --display-name="WidgetCo" \
  --allow-password-signup \
  --project=my-project

# List all tenants
gcloud identity platform tenants list \
  --project=my-project \
  --format="table(name,displayName)"

# Describe a tenant
gcloud identity platform tenants describe TENANT_ID \
  --project=my-project

# Update tenant settings
gcloud identity platform tenants update TENANT_ID \
  --display-name="Acme Corporation Updated" \
  --project=my-project

# Delete a tenant (also deletes all users in the tenant — irreversible)
gcloud identity platform tenants delete TENANT_ID \
  --project=my-project
```

---

## SAML IdP Configurations

```bash
# Create an inbound SAML IdP config (for a specific tenant)
gcloud identity platform tenants inbound-saml-configs create \
  --tenant=TENANT_ID \
  --display-name="Acme Azure AD SSO" \
  --enabled \
  --idp-metadata-xml-path=idp-metadata.xml \
  --sp-entity-id="my-project.firebaseapp.com" \
  --sp-certificate-path=sp-cert.pem \
  --project=my-project

# Create SAML config at project level (not tenant-specific)
gcloud identity platform inbound-saml-configs create \
  --display-name="Corporate SSO" \
  --enabled \
  --idp-metadata-xml-path=idp-metadata.xml \
  --sp-entity-id="my-project.firebaseapp.com" \
  --project=my-project

# List SAML configs for a tenant
gcloud identity platform tenants inbound-saml-configs list \
  --tenant=TENANT_ID \
  --project=my-project

# List project-level SAML configs
gcloud identity platform inbound-saml-configs list \
  --project=my-project

# Describe a SAML config
gcloud identity platform tenants inbound-saml-configs describe SAML_CONFIG_ID \
  --tenant=TENANT_ID \
  --project=my-project

# Update SAML config (re-upload IdP metadata after rotation)
gcloud identity platform tenants inbound-saml-configs update SAML_CONFIG_ID \
  --tenant=TENANT_ID \
  --idp-metadata-xml-path=updated-idp-metadata.xml \
  --project=my-project

# Delete a SAML config
gcloud identity platform tenants inbound-saml-configs delete SAML_CONFIG_ID \
  --tenant=TENANT_ID \
  --project=my-project
```

---

## OIDC IdP Configurations

```bash
# Create an OIDC IdP config for a tenant
gcloud identity platform tenants oidc-idp-configs create \
  --tenant=TENANT_ID \
  --display-name="Okta SSO" \
  --enabled \
  --client-id="0oa1b2c3d4e5f6g7h8i9" \
  --issuer="https://my-org.okta.com" \
  --project=my-project

# Note: client-secret must be set via REST API (not exposed in gcloud)
# Set client secret via REST:
TOKEN=$(gcloud auth print-access-token)
curl -s -X PATCH \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"clientSecret": "your-oidc-client-secret"}' \
  "https://identitytoolkit.googleapis.com/v2/projects/my-project/tenants/TENANT_ID/oauthIdpConfigs/OIDC_CONFIG_ID?updateMask=clientSecret"

# List OIDC configs for a tenant
gcloud identity platform tenants oidc-idp-configs list \
  --tenant=TENANT_ID \
  --project=my-project \
  --format="table(name,displayName,enabled,issuer,clientId)"

# Project-level OIDC configs
gcloud identity platform oidc-idp-configs list \
  --project=my-project

# Describe an OIDC config
gcloud identity platform tenants oidc-idp-configs describe OIDC_CONFIG_ID \
  --tenant=TENANT_ID \
  --project=my-project

# Update OIDC config
gcloud identity platform tenants oidc-idp-configs update OIDC_CONFIG_ID \
  --tenant=TENANT_ID \
  --display-name="Updated Okta SSO" \
  --enabled=false \
  --project=my-project

# Delete an OIDC config
gcloud identity platform tenants oidc-idp-configs delete OIDC_CONFIG_ID \
  --tenant=TENANT_ID \
  --project=my-project
```

---

## User Management via Admin SDK (not gcloud)

Identity Platform user management is primarily done via the Firebase Admin SDK or REST API. Here are examples:

```bash
# Install Firebase Admin SDK
pip install firebase-admin

# Python: create a user with custom claims (for tenant)
python3 - << 'EOF'
import firebase_admin
from firebase_admin import auth, credentials

cred = credentials.ApplicationDefault()
firebase_admin.initialize_app(cred)

# Create a user in the project (no tenant)
user = auth.create_user(
    email='newuser@example.com',
    password='SecurePassword123!',
    display_name='New User',
    email_verified=True
)
print(f"Created user: {user.uid}")

# Set custom claims (for RBAC in the app)
auth.set_custom_user_claims(user.uid, {'admin': True, 'org_id': 'acme'})

# Revoke all refresh tokens (force re-login)
auth.revoke_refresh_tokens(user.uid)

# Get user by email
user = auth.get_user_by_email('newuser@example.com')
print(f"User: {user.uid}, email_verified: {user.email_verified}")

# Delete a user
auth.delete_user(user.uid)

# Tenant-specific user management
tenant_client = auth.TenantManager(None).auth_for_tenant('acme-corp-tenant-id')
tenant_user = tenant_client.create_user(
    email='employee@acme.com',
    password='AcmePassword456!'
)
print(f"Created tenant user: {tenant_user.uid}")
EOF
```

---

## Blocking Functions Deployment

```bash
# Deploy a blocking function for Identity Platform (beforeCreate trigger)
cat > index.js << 'EOF'
const functions = require('firebase-functions');

// Block sign-up from non-corporate email domains
exports.beforeCreate = functions.auth.user().beforeCreate((user, context) => {
  const allowedDomains = ['example.com', 'subsidiary.com'];
  const emailDomain = user.email ? user.email.split('@')[1] : '';

  if (!allowedDomains.includes(emailDomain)) {
    throw new functions.auth.HttpsError(
      'invalid-argument',
      `Email domain ${emailDomain} is not allowed to register.`
    );
  }

  // Enrich user with custom claims from internal DB (illustrative)
  return {
    customClaims: {
      domain: emailDomain,
      registered_at: new Date().toISOString()
    }
  };
});

// Block sign-in from suspended accounts (check custom claim set by admin)
exports.beforeSignIn = functions.auth.user().beforeSignIn((user, context) => {
  if (user.customClaims && user.customClaims.suspended) {
    throw new functions.auth.HttpsError(
      'permission-denied',
      'Your account has been suspended. Contact support@example.com.'
    );
  }
});
EOF

cat > package.json << 'EOF'
{
  "name": "identity-platform-blocking",
  "version": "1.0.0",
  "dependencies": {
    "firebase-functions": "^4.0.0",
    "firebase-admin": "^11.0.0"
  }
}
EOF

# Deploy using Firebase CLI
npm install
firebase deploy --only functions:beforeCreate,functions:beforeSignIn \
  --project=my-project
```

---

## REST API: Identity Platform Configuration

```bash
TOKEN=$(gcloud auth print-access-token)

# Get project-level Identity Platform config
curl -s -H "Authorization: Bearer ${TOKEN}" \
  "https://identitytoolkit.googleapis.com/v2/projects/my-project/config" \
  | python3 -m json.tool

# Update project config: set authorized domains
curl -s -X PATCH \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "authorizedDomains": [
      "app.example.com",
      "localhost",
      "my-project.firebaseapp.com"
    ]
  }' \
  "https://identitytoolkit.googleapis.com/v2/projects/my-project/config?updateMask=authorizedDomains"

# Enable App Check enforcement
curl -s -X PATCH \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "appCheckConfig": {
      "tokenTtl": "3600s",
      "debugTokens": []
    }
  }' \
  "https://identitytoolkit.googleapis.com/v2/projects/my-project/config?updateMask=appCheckConfig"
```
