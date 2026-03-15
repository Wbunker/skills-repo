# Identity & Access — CLI Reference

## Cloud Identity — Groups

```bash
# Create a Google Group
gcloud identity groups create \
  --email=my-group@example.com \
  --display-name="My Engineering Group" \
  --description="Platform engineering team" \
  --organization=ORG_ID

# List all groups in an organization
gcloud identity groups list \
  --organization=ORG_ID

# Describe a group
gcloud identity groups describe \
  --email=my-group@example.com

# Search groups by display name
gcloud identity groups search \
  --labels="cloudidentity.googleapis.com/groups.discussion_forum" \
  --organization=ORG_ID

# Delete a group
gcloud identity groups delete \
  --email=my-group@example.com

# Update group description
gcloud identity groups update \
  --email=my-group@example.com \
  --display-name="Updated Engineering Group"
```

### Group Memberships

```bash
# Add a member to a group
gcloud identity groups memberships add \
  --group-email=my-group@example.com \
  --member-email=alice@example.com

# Add a member with a specific role (OWNER, MANAGER, MEMBER)
gcloud identity groups memberships add \
  --group-email=my-group@example.com \
  --member-email=alice@example.com \
  --roles=MANAGER

# List members of a group
gcloud identity groups memberships list \
  --group-email=my-group@example.com

# Describe a specific membership
gcloud identity groups memberships describe \
  --group-email=my-group@example.com \
  --member-email=alice@example.com

# Modify a member's role
gcloud identity groups memberships modify-membership-roles \
  --group-email=my-group@example.com \
  --member-email=alice@example.com \
  --add-roles=OWNER \
  --remove-roles=MEMBER

# Remove a member from a group
gcloud identity groups memberships delete \
  --group-email=my-group@example.com \
  --member-email=alice@example.com

# List groups that a user belongs to
gcloud identity groups memberships list \
  --member-email=alice@example.com
```

---

## Cloud Identity-Aware Proxy (IAP)

### Enable and Configure IAP

```bash
# Enable IAP on an App Engine application
gcloud iap web enable \
  --resource-type=app-engine \
  --project=PROJECT_ID

# Enable IAP on a Cloud Run service (requires backend service in LB)
gcloud iap web enable \
  --resource-type=backend-services \
  --service=my-cloud-run-backend-service \
  --project=PROJECT_ID

# Enable IAP on a Compute Engine backend service (in a load balancer)
gcloud iap web enable \
  --resource-type=backend-services \
  --service=my-backend-service \
  --project=PROJECT_ID

# Disable IAP on an App Engine application
gcloud iap web disable \
  --resource-type=app-engine \
  --project=PROJECT_ID

# Get IAP web settings
gcloud iap settings get \
  --project=PROJECT_ID \
  --resource-type=app-engine

# Update IAP settings (e.g., set access denied page URL)
gcloud iap settings set settings.yaml \
  --project=PROJECT_ID \
  --resource-type=app-engine
```

### IAP IAM — Grant Access to Applications

```bash
# Grant a user access to an IAP-protected App Engine application
gcloud iap web add-iam-policy-binding \
  --resource-type=app-engine \
  --member="user:alice@example.com" \
  --role="roles/iap.httpsResourceAccessor" \
  --project=PROJECT_ID

# Grant a group access to an IAP-protected App Engine service
gcloud iap web add-iam-policy-binding \
  --resource-type=app-engine \
  --service=my-service \
  --member="group:devs@example.com" \
  --role="roles/iap.httpsResourceAccessor" \
  --project=PROJECT_ID

# Grant access to an IAP-protected backend service (Compute Engine / Cloud Run LB)
gcloud iap web add-iam-policy-binding \
  --resource-type=backend-services \
  --service=my-backend-service \
  --member="group:engineers@example.com" \
  --role="roles/iap.httpsResourceAccessor" \
  --project=PROJECT_ID

# Remove IAP access for a user
gcloud iap web remove-iam-policy-binding \
  --resource-type=app-engine \
  --member="user:alice@example.com" \
  --role="roles/iap.httpsResourceAccessor" \
  --project=PROJECT_ID

# Get IAM policy for an IAP-protected resource
gcloud iap web get-iam-policy \
  --resource-type=app-engine \
  --project=PROJECT_ID
```

### IAP TCP Tunneling (SSH to Private VMs)

```bash
# Allow IAP traffic to reach VMs (firewall rule — one-time setup per VPC)
gcloud compute firewall-rules create allow-iap-ssh \
  --direction=INGRESS \
  --action=ALLOW \
  --rules=tcp:22 \
  --source-ranges=35.235.240.0/20 \
  --target-tags=iap-ssh \
  --network=default

# Open an SSH tunnel to a private VM via IAP (port 22 → local port 2222)
gcloud compute start-iap-tunnel my-private-vm 22 \
  --local-host-port=localhost:2222 \
  --zone=us-central1-a \
  --project=PROJECT_ID

# SSH directly to a private VM via IAP (gcloud handles tunnel automatically)
gcloud compute ssh my-private-vm \
  --zone=us-central1-a \
  --tunnel-through-iap \
  --project=PROJECT_ID

# Open an RDP tunnel to a private Windows VM
gcloud compute start-iap-tunnel my-windows-vm 3389 \
  --local-host-port=localhost:3389 \
  --zone=us-central1-a \
  --project=PROJECT_ID

# Open a tunnel to a private database port
gcloud compute start-iap-tunnel my-db-proxy-vm 5432 \
  --local-host-port=localhost:5432 \
  --zone=us-central1-a \
  --project=PROJECT_ID

# Grant a user IAP tunnel access to a specific instance
gcloud compute instances add-iam-policy-binding my-private-vm \
  --zone=us-central1-a \
  --member="user:developer@example.com" \
  --role="roles/iap.tunnelResourceAccessor"

# Grant a group IAP tunnel access at the project level (all instances)
gcloud projects add-iam-policy-binding PROJECT_ID \
  --member="group:devs@example.com" \
  --role="roles/iap.tunnelResourceAccessor"
```

---

## Workforce Identity Federation

```bash
# Create a Workforce Identity Pool (org-level resource)
gcloud iam workforce-pools create corporate-idp-pool \
  --organization=ORG_ID \
  --location=global \
  --display-name="Corporate IdP Pool" \
  --description="Workforce federation for Okta users" \
  --session-duration=28800s

# List workforce pools
gcloud iam workforce-pools list \
  --organization=ORG_ID \
  --location=global

# Describe a workforce pool
gcloud iam workforce-pools describe corporate-idp-pool \
  --organization=ORG_ID \
  --location=global

# Create an OIDC provider in the workforce pool
gcloud iam workforce-pools providers create-oidc okta-oidc \
  --workforce-pool=corporate-idp-pool \
  --location=global \
  --display-name="Okta OIDC" \
  --description="Okta as OIDC IdP" \
  --issuer-uri="https://my-org.okta.com/oauth2/default" \
  --client-id="0oa1abc2defGHIJK3456" \
  --client-secret-value="YOUR_CLIENT_SECRET" \
  --attribute-mapping="google.subject=assertion.sub,google.email=assertion.email,google.groups=assertion.groups,attribute.department=assertion.department" \
  --attribute-condition="assertion.email.endsWith('@example.com')" \
  --web-sso-response-type=id-token \
  --web-sso-assertion-claims-behavior=merge-user-info-over-id-token-claims

# Create a SAML provider in the workforce pool
gcloud iam workforce-pools providers create-saml adfs-saml \
  --workforce-pool=corporate-idp-pool \
  --location=global \
  --display-name="AD FS SAML" \
  --idp-metadata-path=adfs-metadata.xml \
  --attribute-mapping="google.subject=assertion.subject,google.email=assertion.attributes['http://schemas.xmlsoap.org/ws/2005/05/identity/claims/emailaddress'][0],google.groups=assertion.attributes['http://schemas.microsoft.com/ws/2008/06/identity/claims/groups']"

# List providers in a workforce pool
gcloud iam workforce-pools providers list \
  --workforce-pool=corporate-idp-pool \
  --location=global

# Grant a workforce pool user a role on a project
gcloud projects add-iam-policy-binding PROJECT_ID \
  --member="principal://iam.googleapis.com/locations/global/workforcePools/corporate-idp-pool/subject/alice@example.com" \
  --role="roles/viewer"

# Grant all users in the workforce pool a role
gcloud projects add-iam-policy-binding PROJECT_ID \
  --member="principalSet://iam.googleapis.com/locations/global/workforcePools/corporate-idp-pool/*" \
  --role="roles/viewer"

# Grant users in a specific group (based on mapped attribute)
gcloud projects add-iam-policy-binding PROJECT_ID \
  --member="principalSet://iam.googleapis.com/locations/global/workforcePools/corporate-idp-pool/attribute.department/engineering" \
  --role="roles/bigquery.dataViewer"

# Disable a workforce pool provider
gcloud iam workforce-pools providers update-oidc okta-oidc \
  --workforce-pool=corporate-idp-pool \
  --location=global \
  --disabled

# Delete a workforce pool provider
gcloud iam workforce-pools providers delete okta-oidc \
  --workforce-pool=corporate-idp-pool \
  --location=global

# Delete a workforce pool
gcloud iam workforce-pools delete corporate-idp-pool \
  --organization=ORG_ID \
  --location=global
```

---

## Identity Platform (Firebase Authentication)

```bash
# Identity Platform is primarily managed via the Firebase CLI or GCP Console.
# Some operations are available via gcloud beta.

# Enable Identity Platform API
gcloud services enable identitytoolkit.googleapis.com \
  --project=PROJECT_ID

# List Identity Platform tenants (multi-tenancy)
gcloud alpha identity platform tenants list \
  --project=PROJECT_ID

# Create a tenant
gcloud alpha identity platform tenants create \
  --display-name="My Tenant" \
  --project=PROJECT_ID

# Describe a tenant
gcloud alpha identity platform tenants describe TENANT_ID \
  --project=PROJECT_ID

# Delete a tenant
gcloud alpha identity platform tenants delete TENANT_ID \
  --project=PROJECT_ID

# Firebase CLI: deploy auth configuration (sign-in methods, etc.)
# (Requires Firebase CLI: npm install -g firebase-tools)
firebase use PROJECT_ID
firebase deploy --only auth

# List users in Identity Platform via the Admin SDK (Python example)
python3 - <<'EOF'
import firebase_admin
from firebase_admin import credentials, auth

app = firebase_admin.initialize_app()
for user in auth.list_users().iterate_all():
    print(f'{user.uid}: {user.email}')
EOF
```

---

## Access Context Manager (for BeyondCorp / Context-Aware Access)

```bash
# Create an Access Policy (one per organization; usually already exists)
gcloud access-context-manager policies create \
  --organization=ORG_ID \
  --title="Organization Access Policy"

# List access policies
gcloud access-context-manager policies list \
  --organization=ORG_ID

# Describe an access policy
gcloud access-context-manager policies describe POLICY_ID

# Create a basic access level (IP-based)
gcloud access-context-manager levels create CORP_NETWORK_LEVEL \
  --title="Corporate Network" \
  --basic-level-spec=conditions.yaml \
  --policy=POLICY_ID
# conditions.yaml:
# - ipSubnetworks:
#   - 203.0.113.0/24
#   - 198.51.100.0/24

# Create an access level requiring an Endpoint Verified device
# (device policy requirements; configured via YAML)
gcloud access-context-manager levels create MANAGED_DEVICE_LEVEL \
  --title="Managed Device" \
  --basic-level-spec=device-policy.yaml \
  --policy=POLICY_ID
# device-policy.yaml:
# - devicePolicy:
#     requireScreenlock: true
#     allowedEncryptionStatuses:
#       - ENCRYPTED
#     osConstraints:
#       - osType: DESKTOP_CHROME_OS
#       - osType: DESKTOP_MAC

# List access levels
gcloud access-context-manager levels list \
  --policy=POLICY_ID

# Describe an access level
gcloud access-context-manager levels describe CORP_NETWORK_LEVEL \
  --policy=POLICY_ID

# Delete an access level
gcloud access-context-manager levels delete CORP_NETWORK_LEVEL \
  --policy=POLICY_ID

# Bind an access level to an IAP resource (via Console or Terraform; gcloud IAP settings)
# For IAM conditions, reference the access level as:
# 'accessPolicies/POLICY_ID/accessLevels/LEVEL_NAME' in the condition expression:
# request.auth.access_levels.exists(x, x == 'accessPolicies/POLICY_ID/accessLevels/CORP_NETWORK_LEVEL')
gcloud projects add-iam-policy-binding PROJECT_ID \
  --member="group:all-employees@example.com" \
  --role="roles/bigquery.dataViewer" \
  --condition="title=CorpNetworkOnly,expression=request.auth.access_levels.exists(x, x == 'accessPolicies/POLICY_ID/accessLevels/CORP_NETWORK_LEVEL')"
```
