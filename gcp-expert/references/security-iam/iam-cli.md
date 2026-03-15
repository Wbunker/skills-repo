# Cloud IAM — CLI Reference

## Projects IAM

```bash
# View the IAM policy for a project
gcloud projects get-iam-policy PROJECT_ID

# View as JSON
gcloud projects get-iam-policy PROJECT_ID --format=json

# Add a single binding (non-destructive, merges with existing policy)
gcloud projects add-iam-policy-binding PROJECT_ID \
  --member="user:alice@example.com" \
  --role="roles/storage.objectViewer"

# Add a binding with a time-limited condition (IAM policy version 3)
gcloud projects add-iam-policy-binding PROJECT_ID \
  --member="user:contractor@example.com" \
  --role="roles/compute.viewer" \
  --condition='expression=request.time < timestamp("2025-06-01T00:00:00Z"),title=Expires June 2025'

# Remove a binding
gcloud projects remove-iam-policy-binding PROJECT_ID \
  --member="user:alice@example.com" \
  --role="roles/storage.objectViewer"

# Replace the entire policy with a file (use with caution — replaces all bindings)
gcloud projects set-iam-policy PROJECT_ID policy.json
```

---

## Folders IAM

```bash
# Get IAM policy for a folder
gcloud resource-manager folders get-iam-policy FOLDER_ID

# Add a binding to a folder
gcloud resource-manager folders add-iam-policy-binding FOLDER_ID \
  --member="group:platform-admins@example.com" \
  --role="roles/resourcemanager.folderAdmin"

# Remove a binding from a folder
gcloud resource-manager folders remove-iam-policy-binding FOLDER_ID \
  --member="group:platform-admins@example.com" \
  --role="roles/resourcemanager.folderAdmin"
```

---

## Organization IAM

```bash
# Get IAM policy for an organization
gcloud organizations get-iam-policy ORG_ID

# Add a binding at org level
gcloud organizations add-iam-policy-binding ORG_ID \
  --member="group:security-team@example.com" \
  --role="roles/securitycenter.admin"

# Remove a binding at org level
gcloud organizations remove-iam-policy-binding ORG_ID \
  --member="user:bob@example.com" \
  --role="roles/resourcemanager.organizationViewer"
```

---

## Service Accounts

```bash
# Create a service account
gcloud iam service-accounts create SA_NAME \
  --display-name="My Service Account" \
  --description="Used by the data pipeline" \
  --project=PROJECT_ID

# List service accounts in a project
gcloud iam service-accounts list --project=PROJECT_ID

# Describe a service account
gcloud iam service-accounts describe SA_EMAIL

# Update display name and description
gcloud iam service-accounts update SA_EMAIL \
  --display-name="Updated Name" \
  --description="New description"

# Disable a service account (blocks all authentication)
gcloud iam service-accounts disable SA_EMAIL

# Enable a disabled service account
gcloud iam service-accounts enable SA_EMAIL

# Delete a service account
gcloud iam service-accounts delete SA_EMAIL

# Undelete a recently deleted service account (within 30 days)
gcloud iam service-accounts undelete SA_UNIQUE_ID

# Grant a role to the service account on a project
gcloud projects add-iam-policy-binding PROJECT_ID \
  --member="serviceAccount:SA_EMAIL" \
  --role="roles/bigquery.dataViewer"

# Grant a user the ability to impersonate a service account
gcloud iam service-accounts add-iam-policy-binding SA_EMAIL \
  --member="user:developer@example.com" \
  --role="roles/iam.serviceAccountTokenCreator"

# Grant a user the ability to attach a SA to a resource (run as)
gcloud iam service-accounts add-iam-policy-binding SA_EMAIL \
  --member="user:developer@example.com" \
  --role="roles/iam.serviceAccountUser"

# View the IAM policy on a service account (who can act as it)
gcloud iam service-accounts get-iam-policy SA_EMAIL
```

### Service Account Keys

```bash
# Create a JSON key (avoid when possible — use Workload Identity instead)
gcloud iam service-accounts keys create key.json \
  --iam-account=SA_EMAIL

# List keys for a service account
gcloud iam service-accounts keys list \
  --iam-account=SA_EMAIL

# Describe a specific key
gcloud iam service-accounts keys get SA_EMAIL \
  --key=KEY_ID

# Delete a key
gcloud iam service-accounts keys delete KEY_ID \
  --iam-account=SA_EMAIL

# Upload an existing public key (to allow authenticating with an existing private key)
gcloud iam service-accounts keys upload public_key.pem \
  --iam-account=SA_EMAIL
```

---

## Custom Roles

```bash
# Create a custom role at project level from a YAML file
# role.yaml:
#   title: "Custom Storage Lister"
#   description: "Can only list buckets and objects"
#   stage: "GA"
#   includedPermissions:
#     - storage.buckets.list
#     - storage.objects.list
gcloud iam roles create customStorageLister \
  --project=PROJECT_ID \
  --file=role.yaml

# Create a custom role at org level
gcloud iam roles create customStorageLister \
  --organization=ORG_ID \
  --file=role.yaml

# Create a custom role inline
gcloud iam roles create customRole \
  --project=PROJECT_ID \
  --title="Custom Role" \
  --description="Minimal permissions for data pipeline" \
  --permissions=storage.objects.get,storage.objects.list,bigquery.jobs.create \
  --stage=GA

# List custom roles in a project
gcloud iam roles list --project=PROJECT_ID

# List all predefined roles
gcloud iam roles list

# Describe a predefined role (see its permissions)
gcloud iam roles describe roles/storage.objectViewer

# Describe a custom role
gcloud iam roles describe customStorageLister --project=PROJECT_ID

# Update a custom role (add/remove permissions)
gcloud iam roles update customStorageLister \
  --project=PROJECT_ID \
  --add-permissions=storage.objects.get \
  --remove-permissions=storage.objects.list

# Update by replacing with a new YAML
gcloud iam roles update customStorageLister \
  --project=PROJECT_ID \
  --file=updated-role.yaml

# Disable a custom role (prevents it from being granted, existing grants remain but are inert)
gcloud iam roles update customStorageLister \
  --project=PROJECT_ID \
  --stage=DISABLED

# Delete a custom role
gcloud iam roles delete customStorageLister --project=PROJECT_ID

# Copy a predefined role to create a custom role starting from its permissions
gcloud iam roles copy \
  --source=roles/storage.objectAdmin \
  --destination=customStorageAdmin \
  --dest-project=PROJECT_ID
```

---

## Workload Identity Pools and Providers

```bash
# Create a Workload Identity Pool
gcloud iam workload-identity-pools create my-wi-pool \
  --location=global \
  --display-name="My WI Pool" \
  --description="Pool for GitHub Actions" \
  --project=PROJECT_ID

# Describe a pool
gcloud iam workload-identity-pools describe my-wi-pool \
  --location=global \
  --project=PROJECT_ID

# List pools
gcloud iam workload-identity-pools list \
  --location=global \
  --project=PROJECT_ID

# Create an OIDC provider (GitHub Actions example)
gcloud iam workload-identity-pools providers create-oidc github-provider \
  --location=global \
  --workload-identity-pool=my-wi-pool \
  --display-name="GitHub OIDC Provider" \
  --issuer-uri="https://token.actions.githubusercontent.com" \
  --attribute-mapping="google.subject=assertion.sub,attribute.repository=assertion.repository,attribute.actor=assertion.actor" \
  --attribute-condition="assertion.repository_owner=='my-github-org'" \
  --project=PROJECT_ID

# Create an OIDC provider (generic)
gcloud iam workload-identity-pools providers create-oidc my-oidc-provider \
  --location=global \
  --workload-identity-pool=my-wi-pool \
  --issuer-uri="https://accounts.example.com" \
  --allowed-audiences="https://my-app.example.com" \
  --attribute-mapping="google.subject=assertion.sub" \
  --project=PROJECT_ID

# Create an AWS provider
gcloud iam workload-identity-pools providers create-aws my-aws-provider \
  --location=global \
  --workload-identity-pool=my-wi-pool \
  --account-id="123456789012" \
  --attribute-mapping="google.subject=assertion.arn,attribute.account=assertion.account" \
  --project=PROJECT_ID

# Create an X.509 / certificate-based provider
gcloud iam workload-identity-pools providers create-x509 my-x509-provider \
  --location=global \
  --workload-identity-pool=my-wi-pool \
  --trust-store-config-path=trust-store.yaml \
  --project=PROJECT_ID

# Bind a service account to a WI pool principal (for GitHub Actions: specific repo)
gcloud iam service-accounts add-iam-policy-binding SA_EMAIL \
  --role=roles/iam.workloadIdentityUser \
  --member="principalSet://iam.googleapis.com/projects/PROJECT_NUMBER/locations/global/workloadIdentityPools/my-wi-pool/attribute.repository/my-github-org/my-repo" \
  --project=PROJECT_ID

# Bind for any identity in a WI pool
gcloud iam service-accounts add-iam-policy-binding SA_EMAIL \
  --role=roles/iam.workloadIdentityUser \
  --member="principalSet://iam.googleapis.com/projects/PROJECT_NUMBER/locations/global/workloadIdentityPools/my-wi-pool/*" \
  --project=PROJECT_ID

# Get the OIDC credential configuration file (for use in application default credentials)
gcloud iam workload-identity-pools create-cred-config \
  "projects/PROJECT_NUMBER/locations/global/workloadIdentityPools/my-wi-pool/providers/github-provider" \
  --service-account=SA_EMAIL \
  --output-file=credentials.json \
  --credential-source-file=/path/to/token \
  --credential-source-type=text

# Delete a provider
gcloud iam workload-identity-pools providers delete github-provider \
  --location=global \
  --workload-identity-pool=my-wi-pool \
  --project=PROJECT_ID

# Delete a pool
gcloud iam workload-identity-pools delete my-wi-pool \
  --location=global \
  --project=PROJECT_ID
```

---

## Workforce Identity Federation (External Human Users)

```bash
# Create a Workforce Identity Pool (org-level, not project-level)
gcloud iam workforce-pools create my-workforce-pool \
  --organization=ORG_ID \
  --location=global \
  --display-name="Corporate IdP" \
  --description="Okta workforce federation"

# Create an OIDC provider for the workforce pool
gcloud iam workforce-pools providers create-oidc okta-provider \
  --workforce-pool=my-workforce-pool \
  --location=global \
  --display-name="Okta OIDC" \
  --issuer-uri="https://my-org.okta.com/oauth2/default" \
  --client-id="my-client-id" \
  --client-secret-value="my-client-secret" \
  --attribute-mapping="google.subject=assertion.sub,google.email=assertion.email,google.groups=assertion.groups" \
  --web-sso-response-type=id-token \
  --web-sso-assertion-claims-behavior=merge-user-info-over-id-token-claims

# Create a SAML provider for the workforce pool
gcloud iam workforce-pools providers create-saml adfs-provider \
  --workforce-pool=my-workforce-pool \
  --location=global \
  --display-name="AD FS SAML" \
  --idp-metadata-path=metadata.xml \
  --attribute-mapping="google.subject=assertion.subject,google.email=assertion.attributes['http://schemas.xmlsoap.org/ws/2005/05/identity/claims/emailaddress'][0]"

# List workforce pools
gcloud iam workforce-pools list --organization=ORG_ID --location=global

# Grant a workforce pool principal a role on a project
gcloud projects add-iam-policy-binding PROJECT_ID \
  --member="principal://iam.googleapis.com/locations/global/workforcePools/my-workforce-pool/subject/alice@corp.example" \
  --role="roles/viewer"

# Grant all users in a workforce pool a role
gcloud projects add-iam-policy-binding PROJECT_ID \
  --member="principalSet://iam.googleapis.com/locations/global/workforcePools/my-workforce-pool/*" \
  --role="roles/viewer"
```

---

## Policy Intelligence — Activity Analyzer

```bash
# Query which principals have accessed a resource in the last 90 days
gcloud policy-intelligence query-activity \
  --activity-type=serviceAccountLastAuthentication \
  --project=PROJECT_ID

# Query permission usage for a service account
gcloud policy-intelligence query-activity \
  --activity-type=serviceAccountKeyLastAuthentication \
  --project=PROJECT_ID

# Analyze IAM policy to find who has access to a resource
gcloud policy-intelligence analyze-iam-policy \
  --organization=ORG_ID \
  --full-resource-name="//cloudresourcemanager.googleapis.com/projects/PROJECT_ID" \
  --identity="user:alice@example.com"

# Check if a principal has a specific permission on a resource
gcloud policy-intelligence analyze-iam-policy \
  --organization=ORG_ID \
  --full-resource-name="//storage.googleapis.com/projects/_/buckets/my-bucket" \
  --permissions="storage.objects.get"
```

---

## IAM Recommender

```bash
# List IAM policy insights for a project
gcloud recommender insights list \
  --project=PROJECT_ID \
  --location=global \
  --insight-type=google.iam.policy.Insight \
  --format="table(name,description,stateInfo.state,insightSubtype)"

# List recommendations for IAM (role downsizing, removal)
gcloud recommender recommendations list \
  --project=PROJECT_ID \
  --location=global \
  --recommender=google.iam.policy.Recommender \
  --format="table(name,description,stateInfo.state,recommenderSubtype)"

# Describe a specific recommendation
gcloud recommender recommendations describe RECOMMENDATION_ID \
  --project=PROJECT_ID \
  --location=global \
  --recommender=google.iam.policy.Recommender

# Mark a recommendation as claimed (in progress)
gcloud recommender recommendations mark-claimed RECOMMENDATION_ID \
  --project=PROJECT_ID \
  --location=global \
  --recommender=google.iam.policy.Recommender \
  --etag=ETAG

# Mark a recommendation as succeeded (applied)
gcloud recommender recommendations mark-succeeded RECOMMENDATION_ID \
  --project=PROJECT_ID \
  --location=global \
  --recommender=google.iam.policy.Recommender \
  --etag=ETAG

# Mark a recommendation as dismissed
gcloud recommender recommendations mark-dismissed RECOMMENDATION_ID \
  --project=PROJECT_ID \
  --location=global \
  --recommender=google.iam.policy.Recommender \
  --etag=ETAG

# List SA insights (unused service accounts)
gcloud recommender insights list \
  --project=PROJECT_ID \
  --location=global \
  --insight-type=google.iam.serviceAccount.Insight
```

---

## Organization Policies

```bash
# List all available org policy constraints
gcloud resource-manager org-policies list-available-constraints \
  --organization=ORG_ID

# List org policies in effect for a project
gcloud resource-manager org-policies list \
  --project=PROJECT_ID

# Describe a specific org policy
gcloud resource-manager org-policies describe \
  constraints/iam.disableServiceAccountKeyCreation \
  --project=PROJECT_ID

# Enforce a boolean constraint (e.g., disable SA key creation)
gcloud resource-manager org-policies enable-enforce \
  constraints/iam.disableServiceAccountKeyCreation \
  --project=PROJECT_ID

# Enforce at org level
gcloud resource-manager org-policies enable-enforce \
  constraints/iam.disableServiceAccountKeyCreation \
  --organization=ORG_ID

# Disable a previously enforced constraint
gcloud resource-manager org-policies disable-enforce \
  constraints/iam.disableServiceAccountKeyCreation \
  --project=PROJECT_ID

# Set a list constraint from a YAML file
# policy.yaml:
#   constraint: constraints/gcp.resourceLocations
#   listPolicy:
#     allowedValues:
#       - in:us-locations
#       - in:eu-locations
gcloud resource-manager org-policies set-policy policy.yaml \
  --organization=ORG_ID

# Restore default behavior (remove custom policy, inherit from parent)
gcloud resource-manager org-policies delete \
  constraints/gcp.resourceLocations \
  --project=PROJECT_ID

# Set an org policy to allow only specific IAM member domains
# domain-policy.yaml:
#   constraint: constraints/iam.allowedPolicyMemberDomains
#   listPolicy:
#     allowedValues:
#       - C0xxxxxxx  # Cloud Identity customer ID for example.com
gcloud resource-manager org-policies set-policy domain-policy.yaml \
  --organization=ORG_ID
```

---

## IAM Deny Policies

```bash
# Create a deny policy from a JSON file
# deny-policy.json: (see iam-capabilities.md for schema)
gcloud iam policies create deny-sa-creation \
  --attachment-point="cloudresourcemanager.googleapis.com/organizations/ORG_ID" \
  --kind=DenyPolicy \
  --policy-file=deny-policy.json

# List deny policies on an organization
gcloud iam policies list \
  --attachment-point="cloudresourcemanager.googleapis.com/organizations/ORG_ID" \
  --kind=DenyPolicy

# List deny policies on a project
gcloud iam policies list \
  --attachment-point="cloudresourcemanager.googleapis.com/projects/PROJECT_NUMBER" \
  --kind=DenyPolicy

# Describe a deny policy
gcloud iam policies get deny-sa-creation \
  --attachment-point="cloudresourcemanager.googleapis.com/organizations/ORG_ID" \
  --kind=DenyPolicy

# Update a deny policy (replaces content; use etag from get output)
gcloud iam policies update deny-sa-creation \
  --attachment-point="cloudresourcemanager.googleapis.com/organizations/ORG_ID" \
  --kind=DenyPolicy \
  --policy-file=updated-deny-policy.json

# Delete a deny policy
gcloud iam policies delete deny-sa-creation \
  --attachment-point="cloudresourcemanager.googleapis.com/organizations/ORG_ID" \
  --kind=DenyPolicy
```

---

## Useful Queries and Auditing

```bash
# Find all IAM bindings for a specific principal across a project
gcloud asset search-all-iam-policies \
  --scope=projects/PROJECT_ID \
  --query="policy:user:alice@example.com"

# Find all resources a principal has access to (org-wide)
gcloud asset search-all-iam-policies \
  --scope=organizations/ORG_ID \
  --query="policy:serviceAccount:sa@project.iam.gserviceaccount.com"

# Find all bindings for a specific role
gcloud asset search-all-iam-policies \
  --scope=organizations/ORG_ID \
  --query="policy.role.permissions:storage.objects.delete"

# List all service accounts across a project
gcloud asset list \
  --project=PROJECT_ID \
  --asset-types=iam.googleapis.com/ServiceAccount \
  --format="table(name,resource.data.email,resource.data.disabled)"

# Verify current authentication
gcloud auth list

# Print access token for the active account
gcloud auth print-access-token

# Impersonate a service account for a gcloud command
gcloud storage ls \
  --impersonate-service-account=SA_EMAIL
```
