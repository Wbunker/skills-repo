# AWS IAM — CLI Reference
For service concepts, see [iam-capabilities.md](iam-capabilities.md).

## IAM

```bash
# --- Users ---
aws iam create-user --user-name alice
aws iam list-users
aws iam get-user --user-name alice
aws iam update-user --user-name alice --new-user-name alice-admin
aws iam delete-user --user-name alice

# Console password
aws iam create-login-profile --user-name alice --password 'P@ssw0rd!' --password-reset-required
aws iam update-login-profile --user-name alice --password 'NewP@ss!' --no-password-reset-required
aws iam delete-login-profile --user-name alice
aws iam get-login-profile --user-name alice

# Access keys
aws iam create-access-key --user-name alice
aws iam list-access-keys --user-name alice
aws iam update-access-key --user-name alice --access-key-id AKIAIOSFODNN7EXAMPLE --status Inactive
aws iam delete-access-key --user-name alice --access-key-id AKIAIOSFODNN7EXAMPLE
aws iam get-access-key-last-used --access-key-id AKIAIOSFODNN7EXAMPLE

# MFA devices
aws iam enable-mfa-device --user-name alice --serial-number arn:aws:iam::123456789012:mfa/alice \
  --authentication-code1 123456 --authentication-code2 789012
aws iam list-mfa-devices --user-name alice
aws iam deactivate-mfa-device --user-name alice --serial-number arn:aws:iam::123456789012:mfa/alice
aws iam delete-virtual-mfa-device --serial-number arn:aws:iam::123456789012:mfa/alice
aws iam create-virtual-mfa-device --virtual-mfa-device-name alice-mfa --outfile /tmp/qrcode.png --bootstrap-method QRCodePNG
aws iam list-virtual-mfa-devices

# --- Groups ---
aws iam create-group --group-name developers
aws iam list-groups
aws iam get-group --group-name developers
aws iam delete-group --group-name developers
aws iam add-user-to-group --group-name developers --user-name alice
aws iam remove-user-from-group --group-name developers --user-name alice
aws iam list-groups-for-user --user-name alice

# --- Roles ---
aws iam create-role --role-name MyLambdaRole \
  --assume-role-policy-document file://trust-policy.json \
  --description "Role for Lambda execution" \
  --max-session-duration 3600
aws iam list-roles
aws iam get-role --role-name MyLambdaRole
aws iam update-role --role-name MyLambdaRole --description "Updated description" --max-session-duration 7200
aws iam update-role-description --role-name MyLambdaRole --description "Role for Lambda"
aws iam delete-role --role-name MyLambdaRole

# Assume role trust policy
aws iam update-assume-role-policy --role-name MyLambdaRole \
  --policy-document file://updated-trust-policy.json

# Role last activity
aws iam get-role --role-name MyLambdaRole  # check RoleLastUsed field

# --- Policies ---
# Create managed policy
aws iam create-policy --policy-name MyS3ReadPolicy \
  --policy-document file://policy.json \
  --description "Allows read access to specific S3 bucket"

aws iam list-policies --scope Local          # customer-managed only
aws iam list-policies --scope AWS            # AWS managed only
aws iam get-policy --policy-arn arn:aws:iam::123456789012:policy/MyS3ReadPolicy
aws iam delete-policy --policy-arn arn:aws:iam::123456789012:policy/MyS3ReadPolicy

# Policy versions
aws iam create-policy-version \
  --policy-arn arn:aws:iam::123456789012:policy/MyS3ReadPolicy \
  --policy-document file://updated-policy.json \
  --set-as-default
aws iam list-policy-versions --policy-arn arn:aws:iam::123456789012:policy/MyS3ReadPolicy
aws iam get-policy-version \
  --policy-arn arn:aws:iam::123456789012:policy/MyS3ReadPolicy \
  --version-id v2
aws iam set-default-policy-version \
  --policy-arn arn:aws:iam::123456789012:policy/MyS3ReadPolicy \
  --version-id v1
aws iam delete-policy-version \
  --policy-arn arn:aws:iam::123456789012:policy/MyS3ReadPolicy \
  --version-id v1

# Attach/detach policies
aws iam attach-user-policy --user-name alice \
  --policy-arn arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess
aws iam attach-group-policy --group-name developers \
  --policy-arn arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess
aws iam attach-role-policy --role-name MyLambdaRole \
  --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
aws iam detach-user-policy --user-name alice \
  --policy-arn arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess
aws iam detach-group-policy --group-name developers \
  --policy-arn arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess
aws iam detach-role-policy --role-name MyLambdaRole \
  --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole

# List attached policies
aws iam list-attached-user-policies --user-name alice
aws iam list-attached-group-policies --group-name developers
aws iam list-attached-role-policies --role-name MyLambdaRole
aws iam list-entities-for-policy --policy-arn arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess

# Inline policies
aws iam put-user-policy --user-name alice \
  --policy-name InlinePolicy --policy-document file://inline.json
aws iam put-group-policy --group-name developers \
  --policy-name InlinePolicy --policy-document file://inline.json
aws iam put-role-policy --role-name MyLambdaRole \
  --policy-name InlinePolicy --policy-document file://inline.json
aws iam list-user-policies --user-name alice
aws iam list-group-policies --group-name developers
aws iam list-role-policies --role-name MyLambdaRole
aws iam get-user-policy --user-name alice --policy-name InlinePolicy
aws iam get-group-policy --group-name developers --policy-name InlinePolicy
aws iam get-role-policy --role-name MyLambdaRole --policy-name InlinePolicy
aws iam delete-user-policy --user-name alice --policy-name InlinePolicy
aws iam delete-group-policy --group-name developers --policy-name InlinePolicy
aws iam delete-role-policy --role-name MyLambdaRole --policy-name InlinePolicy

# Permission boundaries
aws iam put-user-permissions-boundary --user-name alice \
  --permissions-boundary arn:aws:iam::123456789012:policy/DeveloperBoundary
aws iam put-role-permissions-boundary --role-name MyLambdaRole \
  --permissions-boundary arn:aws:iam::123456789012:policy/ServiceBoundary
aws iam delete-user-permissions-boundary --user-name alice
aws iam delete-role-permissions-boundary --role-name MyLambdaRole

# --- Service-linked roles ---
aws iam create-service-linked-role --aws-service-name elasticloadbalancing.amazonaws.com
aws iam get-service-linked-role-deletion-status --deletion-task-id task-id
aws iam delete-service-linked-role --role-name AWSServiceRoleForElasticLoadBalancing

# --- Instance profiles ---
aws iam create-instance-profile --instance-profile-name MyEC2Profile
aws iam add-role-to-instance-profile --instance-profile-name MyEC2Profile --role-name MyEC2Role
aws iam list-instance-profiles
aws iam get-instance-profile --instance-profile-name MyEC2Profile
aws iam list-instance-profiles-for-role --role-name MyEC2Role
aws iam remove-role-from-instance-profile --instance-profile-name MyEC2Profile --role-name MyEC2Role
aws iam delete-instance-profile --instance-profile-name MyEC2Profile

# --- OIDC Identity Providers ---
aws iam create-open-id-connect-provider \
  --url https://token.actions.githubusercontent.com \
  --client-id-list sts.amazonaws.com \
  --thumbprint-list 6938fd4d98bab03faadb97b34396831e3780aea1
aws iam list-open-id-connect-providers
aws iam get-open-id-connect-provider \
  --open-id-connect-provider-arn arn:aws:iam::123456789012:oidc-provider/token.actions.githubusercontent.com
aws iam delete-open-id-connect-provider \
  --open-id-connect-provider-arn arn:aws:iam::123456789012:oidc-provider/token.actions.githubusercontent.com

# --- SAML Identity Providers ---
aws iam create-saml-provider --name MyOkta --saml-metadata-document file://okta-metadata.xml
aws iam list-saml-providers
aws iam get-saml-provider --saml-provider-arn arn:aws:iam::123456789012:saml-provider/MyOkta
aws iam update-saml-provider \
  --saml-provider-arn arn:aws:iam::123456789012:saml-provider/MyOkta \
  --saml-metadata-document file://updated-metadata.xml
aws iam delete-saml-provider --saml-provider-arn arn:aws:iam::123456789012:saml-provider/MyOkta

# --- Account settings ---
aws iam get-account-password-policy
aws iam update-account-password-policy \
  --minimum-password-length 14 \
  --require-symbols \
  --require-numbers \
  --require-uppercase-characters \
  --require-lowercase-characters \
  --allow-users-to-change-password \
  --max-password-age 90 \
  --password-reuse-prevention 5
aws iam delete-account-password-policy
aws iam get-account-summary
aws iam get-account-authorization-details  # full dump of all IAM entities and policies

# --- Credential report ---
aws iam generate-credential-report
aws iam get-credential-report  # base64-encoded CSV; pipe through: | jq -r '.Content' | base64 -d

```

## IAM Access Analyzer

```bash
# --- Analyzers ---
aws accessanalyzer create-analyzer --analyzer-name MyAnalyzer --type ACCOUNT
aws accessanalyzer create-analyzer --analyzer-name OrgAnalyzer --type ORGANIZATION
# Unused access analyzer (requires type ACCOUNT_UNUSED_ACCESS or ORGANIZATION_UNUSED_ACCESS)
aws accessanalyzer create-analyzer --analyzer-name UnusedAnalyzer --type ACCOUNT_UNUSED_ACCESS \
  --configuration '{"unusedAccess":{"unusedAccessAge":90}}'
aws accessanalyzer get-analyzer --analyzer-name MyAnalyzer
aws accessanalyzer list-analyzers

# --- Findings ---
# list-findings-v2 is the current API (supports unused access findings)
aws accessanalyzer list-findings-v2 \
  --analyzer-arn arn:aws:access-analyzer:us-east-1:123456789012:analyzer/MyAnalyzer
aws accessanalyzer list-findings-v2 \
  --analyzer-arn arn:aws:access-analyzer:us-east-1:123456789012:analyzer/MyAnalyzer \
  --filter '{"status":{"eq":["ACTIVE"]}}'
aws accessanalyzer get-finding-v2 \
  --analyzer-arn arn:aws:access-analyzer:us-east-1:123456789012:analyzer/MyAnalyzer \
  --id finding-id

# Archive / update findings
aws accessanalyzer archive-finding \
  --analyzer-arn arn:aws:access-analyzer:us-east-1:123456789012:analyzer/MyAnalyzer \
  --ids finding-id-1 finding-id-2

# --- Archive Rules ---
aws accessanalyzer create-archive-rule \
  --analyzer-name MyAnalyzer \
  --rule-name TrustedAccountRule \
  --filter '{"principal.AWS":{"contains":["arn:aws:iam::111122223333:root"]}}'
aws accessanalyzer list-archive-rules --analyzer-name MyAnalyzer

# --- Resource Scan ---
aws accessanalyzer start-resource-scan \
  --analyzer-arn arn:aws:access-analyzer:us-east-1:123456789012:analyzer/MyAnalyzer \
  --resource-arn arn:aws:s3:::my-bucket

# --- Policy Validation ---
aws accessanalyzer validate-policy \
  --policy-document file://policy.json \
  --policy-type IDENTITY_POLICY        # IDENTITY_POLICY | RESOURCE_POLICY | SERVICE_CONTROL_POLICY | TRUST_POLICY

# --- Custom Policy Checks ---
# Verify new policy grants no more access than reference policy
aws accessanalyzer check-no-new-access \
  --new-policy-document file://new-policy.json \
  --existing-policy-document file://reference-policy.json \
  --policy-type IDENTITY_POLICY

# Verify policy does not grant specific actions
aws accessanalyzer check-access-not-granted \
  --policy-document file://policy.json \
  --access '[{"actions":["s3:DeleteBucket","s3:DeleteObject"]}]' \
  --policy-type IDENTITY_POLICY

# --- Access Preview ---
aws accessanalyzer create-access-preview \
  --analyzer-arn arn:aws:access-analyzer:us-east-1:123456789012:analyzer/MyAnalyzer \
  --configurations file://preview-config.json
aws accessanalyzer get-access-preview \
  --analyzer-arn arn:aws:access-analyzer:us-east-1:123456789012:analyzer/MyAnalyzer \
  --access-preview-id preview-id
```

## IAM Roles Anywhere

```bash
# --- Trust Anchors ---
# Create trust anchor using ACM Private CA
aws rolesanywhere create-trust-anchor \
  --name MyTrustAnchor \
  --source '{"sourceType":"AWS_ACM_PCA","sourceData":{"acmPcaArn":"arn:aws:acm-pca:us-east-1:123456789012:certificate-authority/ca-id"}}' \
  --enabled

# Create trust anchor using a self-signed/external CA certificate
aws rolesanywhere create-trust-anchor \
  --name ExternalCATrustAnchor \
  --source '{"sourceType":"CERTIFICATE_BUNDLE","sourceData":{"x509CertificateData":"-----BEGIN CERTIFICATE-----\n...\n-----END CERTIFICATE-----"}}' \
  --enabled

aws rolesanywhere get-trust-anchor --trust-anchor-id ta-id
aws rolesanywhere list-trust-anchors
aws rolesanywhere enable-trust-anchor --trust-anchor-id ta-id
aws rolesanywhere disable-trust-anchor --trust-anchor-id ta-id

# --- Profiles ---
# Profile selects which IAM role(s) to assume and session constraints
aws rolesanywhere create-profile \
  --name MyProfile \
  --role-arns arn:aws:iam::123456789012:role/RolesAnywhereRole \
  --session-policy file://session-policy.json \
  --duration-seconds 3600 \
  --enabled

aws rolesanywhere get-profile --profile-id profile-id
aws rolesanywhere list-profiles

# --- CRL (Certificate Revocation List) ---
aws rolesanywhere create-crl \
  --name MyCRL \
  --crl-data fileb://crl.der \
  --trust-anchor-arn arn:aws:rolesanywhere:us-east-1:123456789012:trust-anchor/ta-id \
  --enabled
aws rolesanywhere get-crl --crl-id crl-id
aws rolesanywhere list-crls

# --- Subjects ---
# Subjects are auto-created when a workload first authenticates
aws rolesanywhere list-subjects
aws rolesanywhere get-subject --subject-id subject-id

# --- Sessions ---
# Revoke a subject's session (invalidate temporary credentials issued to a subject)
aws rolesanywhere delete-session --subject-id subject-id

# --- Credential Helper (aws_signing_helper) ---
# Obtain temporary credentials using X.509 cert + private key
aws_signing_helper credential-process \
  --certificate /path/to/cert.pem \
  --private-key /path/to/key.pem \
  --trust-anchor-arn arn:aws:rolesanywhere:us-east-1:123456789012:trust-anchor/ta-id \
  --profile-arn arn:aws:rolesanywhere:us-east-1:123456789012:profile/profile-id \
  --role-arn arn:aws:iam::123456789012:role/RolesAnywhereRole
```
