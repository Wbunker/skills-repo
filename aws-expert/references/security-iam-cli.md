# AWS Security, Identity & Compliance — CLI Reference

AWS CLI commands for all security and identity services. For service concepts and capabilities, see [security-iam-capabilities.md](security-iam-capabilities.md).

## Table of Contents
1. [IAM](#iam)
2. [STS](#sts)
3. [IAM Identity Center](#iam-identity-center)
4. [AWS Organizations](#aws-organizations)
5. [Amazon Cognito](#amazon-cognito)
6. [Amazon Verified Permissions](#amazon-verified-permissions)
7. [AWS KMS](#aws-kms)
8. [AWS Secrets Manager](#aws-secrets-manager)
9. [AWS Certificate Manager (ACM)](#aws-certificate-manager)
10. [AWS CloudHSM](#aws-cloudhsm)
11. [Amazon GuardDuty](#amazon-guardduty)
12. [AWS Security Hub](#aws-security-hub)
13. [Amazon Inspector](#amazon-inspector)
14. [Amazon Macie](#amazon-macie)
15. [Amazon Detective](#amazon-detective)
16. [AWS WAF](#aws-waf)
17. [AWS Shield](#aws-shield)
18. [AWS Network Firewall](#aws-network-firewall)
19. [AWS Firewall Manager](#aws-firewall-manager)

---

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

# --- Access Analyzer ---
aws accessanalyzer list-analyzers
aws accessanalyzer create-analyzer --analyzer-name MyAnalyzer --type ACCOUNT
aws accessanalyzer list-findings --analyzer-arn arn:aws:access-analyzer:us-east-1:123456789012:analyzer/MyAnalyzer
aws accessanalyzer get-finding \
  --analyzer-arn arn:aws:access-analyzer:us-east-1:123456789012:analyzer/MyAnalyzer \
  --id finding-id
aws accessanalyzer archive-finding \
  --analyzer-arn arn:aws:access-analyzer:us-east-1:123456789012:analyzer/MyAnalyzer \
  --ids finding-id
aws accessanalyzer validate-policy \
  --policy-document file://policy.json \
  --policy-type IDENTITY_POLICY
aws accessanalyzer check-access-not-granted \
  --policy-document file://policy.json \
  --access Actions=s3:DeleteBucket
aws accessanalyzer generate-policy \
  --trail-arn arn:aws:cloudtrail:us-east-1:123456789012:trail/MyTrail
```

---

## STS

```bash
# Get current caller identity
aws sts get-caller-identity

# Assume a role
aws sts assume-role \
  --role-arn arn:aws:iam::123456789012:role/AdminRole \
  --role-session-name MySession \
  --duration-seconds 3600

# Assume role with MFA
aws sts assume-role \
  --role-arn arn:aws:iam::123456789012:role/SensitiveRole \
  --role-session-name MFASession \
  --serial-number arn:aws:iam::123456789012:mfa/alice \
  --token-code 123456

# Assume role with OIDC (web identity)
aws sts assume-role-with-web-identity \
  --role-arn arn:aws:iam::123456789012:role/GitHubActionsRole \
  --role-session-name github-deploy \
  --web-identity-token "$GITHUB_TOKEN"

# Get session token (for MFA-protected API access)
aws sts get-session-token \
  --serial-number arn:aws:iam::123456789012:mfa/alice \
  --token-code 123456 \
  --duration-seconds 43200

# Decode authorization error message
aws sts decode-authorization-message --encoded-message <encoded-error-string>
```

---

## IAM Identity Center

```bash
# --- SSO CLI login (end-user workflow) ---
aws configure sso
# Follow prompts: SSO start URL, SSO region, account, role
aws sso login --profile my-sso-profile
aws sso logout

# Use profile in commands
aws s3 ls --profile my-sso-profile

# --- Admin: Permission sets ---
aws sso-admin list-instances  # get InstanceArn
aws sso-admin create-permission-set \
  --instance-arn arn:aws:sso:::instance/ssoins-xxx \
  --name ReadOnlyAccess \
  --description "Read-only access to all services" \
  --session-duration PT8H
aws sso-admin list-permission-sets --instance-arn arn:aws:sso:::instance/ssoins-xxx
aws sso-admin describe-permission-set \
  --instance-arn arn:aws:sso:::instance/ssoins-xxx \
  --permission-set-arn arn:aws:sso:::permissionSet/ssoins-xxx/ps-xxx

# Attach AWS managed policy to permission set
aws sso-admin attach-managed-policy-to-permission-set \
  --instance-arn arn:aws:sso:::instance/ssoins-xxx \
  --permission-set-arn arn:aws:sso:::permissionSet/ssoins-xxx/ps-xxx \
  --managed-policy-arn arn:aws:iam::aws:policy/ReadOnlyAccess

# Attach customer managed policy
aws sso-admin attach-customer-managed-policy-reference-to-permission-set \
  --instance-arn arn:aws:sso:::instance/ssoins-xxx \
  --permission-set-arn arn:aws:sso:::permissionSet/ssoins-xxx/ps-xxx \
  --customer-managed-policy-reference Name=MyCustomPolicy

# Inline policy on permission set
aws sso-admin put-inline-policy-to-permission-set \
  --instance-arn arn:aws:sso:::instance/ssoins-xxx \
  --permission-set-arn arn:aws:sso:::permissionSet/ssoins-xxx/ps-xxx \
  --inline-policy file://inline.json

# Permission boundary on permission set
aws sso-admin put-permissions-boundary-to-permission-set \
  --instance-arn arn:aws:sso:::instance/ssoins-xxx \
  --permission-set-arn arn:aws:sso:::permissionSet/ssoins-xxx/ps-xxx \
  --permissions-boundary ManagedPolicyArn=arn:aws:iam::aws:policy/PowerUserAccess

# --- Account assignments ---
aws sso-admin create-account-assignment \
  --instance-arn arn:aws:sso:::instance/ssoins-xxx \
  --target-id 123456789012 \
  --target-type AWS_ACCOUNT \
  --permission-set-arn arn:aws:sso:::permissionSet/ssoins-xxx/ps-xxx \
  --principal-type GROUP \
  --principal-id group-id

aws sso-admin list-account-assignments \
  --instance-arn arn:aws:sso:::instance/ssoins-xxx \
  --account-id 123456789012 \
  --permission-set-arn arn:aws:sso:::permissionSet/ssoins-xxx/ps-xxx

aws sso-admin delete-account-assignment \
  --instance-arn arn:aws:sso:::instance/ssoins-xxx \
  --target-id 123456789012 \
  --target-type AWS_ACCOUNT \
  --permission-set-arn arn:aws:sso:::permissionSet/ssoins-xxx/ps-xxx \
  --principal-type GROUP \
  --principal-id group-id

# Provision permission sets (push to accounts after changes)
aws sso-admin provision-permission-set \
  --instance-arn arn:aws:sso:::instance/ssoins-xxx \
  --permission-set-arn arn:aws:sso:::permissionSet/ssoins-xxx/ps-xxx \
  --target-type ALL_PROVISIONED_ACCOUNTS

# --- Users and groups (built-in directory) ---
aws identitystore list-users --identity-store-id d-xxxxxxxxxx
aws identitystore list-groups --identity-store-id d-xxxxxxxxxx
aws identitystore describe-user --identity-store-id d-xxxxxxxxxx --user-id user-id
aws identitystore describe-group --identity-store-id d-xxxxxxxxxx --group-id group-id
aws identitystore get-group-membership-id \
  --identity-store-id d-xxxxxxxxxx \
  --group-id group-id \
  --member-id UserId=user-id
aws identitystore create-user \
  --identity-store-id d-xxxxxxxxxx \
  --user-name alice \
  --display-name "Alice Smith" \
  --emails Value=alice@example.com,Type=work,Primary=true \
  --name Formatted="Alice Smith",GivenName=Alice,FamilyName=Smith
aws identitystore create-group \
  --identity-store-id d-xxxxxxxxxx \
  --display-name "Platform Engineers"
aws identitystore create-group-membership \
  --identity-store-id d-xxxxxxxxxx \
  --group-id group-id \
  --member-id UserId=user-id
aws identitystore delete-group-membership \
  --identity-store-id d-xxxxxxxxxx \
  --membership-id membership-id
```

---

## AWS Organizations

```bash
# --- Org setup ---
aws organizations create-organization --feature-set ALL
aws organizations describe-organization
aws organizations list-roots

# --- Accounts ---
aws organizations list-accounts
aws organizations describe-account --account-id 123456789012
aws organizations create-account --email newaccount@example.com --account-name "Production"
aws organizations describe-create-account-status --create-account-request-id req-xxx
aws organizations close-account --account-id 123456789012  # irreversible; 90-day quarantine
aws organizations remove-account-from-organization --account-id 123456789012

# Move account to OU
aws organizations move-account \
  --account-id 123456789012 \
  --source-parent-id r-xxxx \  # root or OU id
  --destination-parent-id ou-xxxx-xxxxxxxx

# --- OUs ---
aws organizations list-organizational-units-for-parent --parent-id r-xxxx  # list OUs under root
aws organizations create-organizational-unit --parent-id r-xxxx --name Production
aws organizations describe-organizational-unit --organizational-unit-id ou-xxxx-xxxxxxxx
aws organizations update-organizational-unit \
  --organizational-unit-id ou-xxxx-xxxxxxxx \
  --name "Production Workloads"
aws organizations delete-organizational-unit --organizational-unit-id ou-xxxx-xxxxxxxx
aws organizations list-children --parent-id ou-xxxx-xxxxxxxx --child-type ACCOUNT
aws organizations list-parents --child-id 123456789012

# --- SCPs ---
aws organizations list-policies --filter SERVICE_CONTROL_POLICY
aws organizations create-policy \
  --name "DenyLeavingOrg" \
  --description "Prevent accounts from leaving the organization" \
  --type SERVICE_CONTROL_POLICY \
  --content file://deny-leave-org.json
aws organizations describe-policy --policy-id p-xxxxxxxx
aws organizations update-policy \
  --policy-id p-xxxxxxxx \
  --content file://updated-policy.json
aws organizations delete-policy --policy-id p-xxxxxxxx

# Attach/detach SCP
aws organizations attach-policy --policy-id p-xxxxxxxx --target-id ou-xxxx-xxxxxxxx
aws organizations attach-policy --policy-id p-xxxxxxxx --target-id 123456789012
aws organizations detach-policy --policy-id p-xxxxxxxx --target-id ou-xxxx-xxxxxxxx
aws organizations list-policies-for-target \
  --target-id 123456789012 \
  --filter SERVICE_CONTROL_POLICY
aws organizations list-targets-for-policy --policy-id p-xxxxxxxx

# Enable policy types (SCPs must be enabled on root first)
aws organizations enable-policy-type --root-id r-xxxx --policy-type SERVICE_CONTROL_POLICY
aws organizations disable-policy-type --root-id r-xxxx --policy-type TAG_POLICY
aws organizations list-roots  # check EnabledPolicyTypes

# --- Delegated administrators ---
aws organizations register-delegated-administrator \
  --account-id 123456789012 \
  --service-principal securityhub.amazonaws.com
aws organizations list-delegated-administrators
aws organizations list-delegated-services-for-account --account-id 123456789012
aws organizations deregister-delegated-administrator \
  --account-id 123456789012 \
  --service-principal securityhub.amazonaws.com

# --- Invitations (manual invite workflow for non-CreateAccount) ---
aws organizations invite-account-to-organization \
  --target Id=john@example.com,Type=EMAIL
aws organizations list-handshakes-for-organization
aws organizations accept-handshake --handshake-id h-xxxxxxxx
aws organizations decline-handshake --handshake-id h-xxxxxxxx
aws organizations cancel-handshake --handshake-id h-xxxxxxxx
```

---

## Amazon Cognito

```bash
# --- User Pools ---
aws cognito-idp create-user-pool \
  --pool-name MyUserPool \
  --policies PasswordPolicy="{MinimumLength=12,RequireUppercase=true,RequireLowercase=true,RequireNumbers=true,RequireSymbols=true}" \
  --auto-verified-attributes email \
  --username-attributes email \
  --mfa-configuration OPTIONAL \
  --account-recovery-setting RecoveryMechanisms="[{Priority=1,Name=verified_email}]"

aws cognito-idp list-user-pools --max-results 20
aws cognito-idp describe-user-pool --user-pool-id us-east-1_xxxxxxxxx
aws cognito-idp delete-user-pool --user-pool-id us-east-1_xxxxxxxxx

# App clients
aws cognito-idp create-user-pool-client \
  --user-pool-id us-east-1_xxxxxxxxx \
  --client-name MyWebApp \
  --generate-secret \
  --explicit-auth-flows ALLOW_USER_SRP_AUTH ALLOW_REFRESH_TOKEN_AUTH \
  --supported-identity-providers COGNITO Google \
  --callback-urls https://myapp.example.com/callback \
  --logout-urls https://myapp.example.com/logout \
  --allowed-o-auth-flows code \
  --allowed-o-auth-scopes openid email profile \
  --allowed-o-auth-flows-user-pool-client
aws cognito-idp list-user-pool-clients --user-pool-id us-east-1_xxxxxxxxx
aws cognito-idp describe-user-pool-client \
  --user-pool-id us-east-1_xxxxxxxxx \
  --client-id xxxxxxxxxxxxxxxxxxxxxxxxxx
aws cognito-idp delete-user-pool-client \
  --user-pool-id us-east-1_xxxxxxxxx \
  --client-id xxxxxxxxxxxxxxxxxxxxxxxxxx

# Domain (hosted UI)
aws cognito-idp create-user-pool-domain \
  --domain myapp-auth \
  --user-pool-id us-east-1_xxxxxxxxx
aws cognito-idp describe-user-pool-domain --domain myapp-auth
aws cognito-idp delete-user-pool-domain \
  --domain myapp-auth \
  --user-pool-id us-east-1_xxxxxxxxx

# Users (admin operations)
aws cognito-idp admin-create-user \
  --user-pool-id us-east-1_xxxxxxxxx \
  --username alice@example.com \
  --temporary-password 'TempP@ss1!' \
  --user-attributes Name=email,Value=alice@example.com Name=email_verified,Value=true \
  --message-action SUPPRESS
aws cognito-idp admin-get-user --user-pool-id us-east-1_xxxxxxxxx --username alice@example.com
aws cognito-idp list-users --user-pool-id us-east-1_xxxxxxxxx --filter "email = \"alice@example.com\""
aws cognito-idp admin-update-user-attributes \
  --user-pool-id us-east-1_xxxxxxxxx \
  --username alice@example.com \
  --user-attributes Name=custom:role,Value=admin
aws cognito-idp admin-disable-user --user-pool-id us-east-1_xxxxxxxxx --username alice@example.com
aws cognito-idp admin-enable-user --user-pool-id us-east-1_xxxxxxxxx --username alice@example.com
aws cognito-idp admin-delete-user --user-pool-id us-east-1_xxxxxxxxx --username alice@example.com
aws cognito-idp admin-reset-user-password \
  --user-pool-id us-east-1_xxxxxxxxx \
  --username alice@example.com
aws cognito-idp admin-set-user-password \
  --user-pool-id us-east-1_xxxxxxxxx \
  --username alice@example.com \
  --password 'NewP@ssword1!' \
  --permanent

# Groups
aws cognito-idp create-group \
  --group-name admins \
  --user-pool-id us-east-1_xxxxxxxxx \
  --role-arn arn:aws:iam::123456789012:role/CognitoAdminRole
aws cognito-idp list-groups --user-pool-id us-east-1_xxxxxxxxx
aws cognito-idp admin-add-user-to-group \
  --user-pool-id us-east-1_xxxxxxxxx \
  --username alice@example.com \
  --group-name admins
aws cognito-idp admin-remove-user-from-group \
  --user-pool-id us-east-1_xxxxxxxxx \
  --username alice@example.com \
  --group-name admins
aws cognito-idp admin-list-groups-for-user \
  --user-pool-id us-east-1_xxxxxxxxx \
  --username alice@example.com

# Identity providers
aws cognito-idp create-identity-provider \
  --user-pool-id us-east-1_xxxxxxxxx \
  --provider-name Google \
  --provider-type Google \
  --provider-details client_id=xxx,client_secret=xxx,authorize_scopes="email profile openid"
aws cognito-idp list-identity-providers --user-pool-id us-east-1_xxxxxxxxx
aws cognito-idp describe-identity-provider \
  --user-pool-id us-east-1_xxxxxxxxx \
  --provider-name Google
aws cognito-idp delete-identity-provider --user-pool-id us-east-1_xxxxxxxxx --provider-name Google

# --- Identity Pools ---
aws cognito-identity create-identity-pool \
  --identity-pool-name MyIdentityPool \
  --allow-unauthenticated-identities \
  --cognito-identity-providers ProviderName=cognito-idp.us-east-1.amazonaws.com/us-east-1_xxxxxxxxx,ClientId=xxxxxxxxxxxxxxxxxxxxxxxxxx,ServerSideTokenCheck=true
aws cognito-identity list-identity-pools --max-results 20
aws cognito-identity describe-identity-pool --identity-pool-id us-east-1:xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
aws cognito-identity delete-identity-pool \
  --identity-pool-id us-east-1:xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx

# Set IAM roles for identity pool
aws cognito-identity set-identity-pool-roles \
  --identity-pool-id us-east-1:xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx \
  --roles authenticated=arn:aws:iam::123456789012:role/CognitoAuthRole,unauthenticated=arn:aws:iam::123456789012:role/CognitoUnauthRole
aws cognito-identity get-identity-pool-roles \
  --identity-pool-id us-east-1:xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
```

---

## Amazon Verified Permissions

```bash
# --- Policy stores ---
aws verifiedpermissions create-policy-store \
  --validation-settings Mode=STRICT
aws verifiedpermissions list-policy-stores
aws verifiedpermissions get-policy-store --policy-store-id psEXAMPLEid
aws verifiedpermissions update-policy-store \
  --policy-store-id psEXAMPLEid \
  --validation-settings Mode=OFF
aws verifiedpermissions delete-policy-store --policy-store-id psEXAMPLEid

# --- Schema ---
aws verifiedpermissions put-schema \
  --policy-store-id psEXAMPLEid \
  --definition file://schema.json  # Cedar schema JSON
aws verifiedpermissions get-schema --policy-store-id psEXAMPLEid

# --- Policies ---
aws verifiedpermissions create-policy \
  --policy-store-id psEXAMPLEid \
  --definition Static="{Description=\"Allow premium users\",Statement=\"permit(principal in Group::premium-users, action == Action::ViewPhoto, resource);\"}"
aws verifiedpermissions list-policies --policy-store-id psEXAMPLEid
aws verifiedpermissions get-policy --policy-store-id psEXAMPLEid --policy-id policyId
aws verifiedpermissions update-policy \
  --policy-store-id psEXAMPLEid \
  --policy-id policyId \
  --definition Static="{Statement=\"permit(principal in Group::premium-users, action, resource);\"}"
aws verifiedpermissions delete-policy --policy-store-id psEXAMPLEid --policy-id policyId

# --- Policy templates ---
aws verifiedpermissions create-policy-template \
  --policy-store-id psEXAMPLEid \
  --description "Share with specific user" \
  --statement "permit(principal == ?principal, action == Action::ViewPhoto, resource == ?resource);"
aws verifiedpermissions list-policy-templates --policy-store-id psEXAMPLEid
aws verifiedpermissions get-policy-template --policy-store-id psEXAMPLEid --policy-template-id templateId
aws verifiedpermissions create-policy \
  --policy-store-id psEXAMPLEid \
  --definition TemplateLinked="{PolicyTemplateId=templateId,Principal={EntityType=User,EntityId=alice},Resource={EntityType=Photo,EntityId=photo123}}"
aws verifiedpermissions delete-policy-template --policy-store-id psEXAMPLEid --policy-template-id templateId

# --- Authorization ---
aws verifiedpermissions is-authorized \
  --policy-store-id psEXAMPLEid \
  --principal EntityType=User,EntityId=alice \
  --action ActionType=Action,ActionId=ViewPhoto \
  --resource EntityType=Photo,EntityId=photo123
# Response: {"Decision": "ALLOW", "Errors": []}

aws verifiedpermissions is-authorized-with-token \
  --policy-store-id psEXAMPLEid \
  --access-token "$ACCESS_TOKEN" \
  --action ActionType=Action,ActionId=ViewPhoto \
  --resource EntityType=Photo,EntityId=photo123
```

---

## AWS KMS

```bash
# --- Key management ---
aws kms create-key \
  --description "My application encryption key" \
  --key-usage ENCRYPT_DECRYPT \
  --origin AWS_KMS \
  --policy file://key-policy.json \
  --tags TagKey=Environment,TagValue=Production
aws kms list-keys
aws kms describe-key --key-id alias/my-key  # can use alias, key ID, or ARN
aws kms get-key-policy --key-id alias/my-key --policy-name default
aws kms put-key-policy --key-id alias/my-key --policy-name default --policy file://updated-policy.json

# Key rotation
aws kms enable-key-rotation --key-id alias/my-key
aws kms disable-key-rotation --key-id alias/my-key
aws kms get-key-rotation-status --key-id alias/my-key
aws kms rotate-key-on-demand --key-id alias/my-key  # immediate manual rotation

# Enable/disable/schedule deletion
aws kms enable-key --key-id key-id
aws kms disable-key --key-id key-id
aws kms schedule-key-deletion --key-id key-id --pending-window-in-days 30  # 7-30 days
aws kms cancel-key-deletion --key-id key-id

# --- Aliases ---
aws kms create-alias --alias-name alias/my-key --target-key-id key-id
aws kms list-aliases
aws kms list-aliases --key-id key-id
aws kms update-alias --alias-name alias/my-key --target-key-id new-key-id
aws kms delete-alias --alias-name alias/my-key

# --- Encrypt / Decrypt ---
aws kms encrypt \
  --key-id alias/my-key \
  --plaintext fileb://secret.txt \
  --output text --query CiphertextBlob | base64 -d > secret.enc

aws kms decrypt \
  --ciphertext-blob fileb://secret.enc \
  --output text --query Plaintext | base64 -d

aws kms re-encrypt \
  --ciphertext-blob fileb://old.enc \
  --destination-key-id alias/new-key \
  --output text --query CiphertextBlob | base64 -d > new.enc

# --- Data keys (envelope encryption) ---
aws kms generate-data-key \
  --key-id alias/my-key \
  --key-spec AES_256
  # Returns: {CiphertextBlob, Plaintext, KeyId}
  # Use Plaintext to encrypt data, store CiphertextBlob alongside encrypted data
  # Discard Plaintext from memory after encrypting

aws kms generate-data-key-without-plaintext \
  --key-id alias/my-key \
  --key-spec AES_256
  # For pre-generating encrypted data keys without decrypting them yet

# --- Grants ---
aws kms create-grant \
  --key-id alias/my-key \
  --grantee-principal arn:aws:iam::123456789012:role/MyServiceRole \
  --operations Decrypt GenerateDataKey
aws kms list-grants --key-id alias/my-key
aws kms retire-grant --key-id alias/my-key --grant-id grant-id
aws kms revoke-grant --key-id alias/my-key --grant-id grant-id

# --- Multi-region keys ---
aws kms replicate-key \
  --key-id arn:aws:kms:us-east-1:123456789012:key/mrk-xxx \
  --replica-region us-west-2
aws kms update-primary-region \
  --key-id arn:aws:kms:us-east-1:123456789012:key/mrk-xxx \
  --primary-region us-west-2

# --- Asymmetric keys ---
aws kms create-key --key-usage SIGN_VERIFY --key-spec RSA_2048
aws kms sign \
  --key-id key-id \
  --message fileb://message.txt \
  --message-type RAW \
  --signing-algorithm RSASSA_PKCS1_V1_5_SHA_256 \
  --output text --query Signature | base64 -d > signature.bin
aws kms verify \
  --key-id key-id \
  --message fileb://message.txt \
  --message-type RAW \
  --signing-algorithm RSASSA_PKCS1_V1_5_SHA_256 \
  --signature fileb://signature.bin
aws kms get-public-key --key-id key-id  # export public key for verification outside AWS
```

---

## AWS Secrets Manager

```bash
# --- Create and manage secrets ---
aws secretsmanager create-secret \
  --name prod/myapp/database \
  --description "Production DB credentials" \
  --secret-string '{"username":"admin","password":"s3cr3t"}' \
  --kms-key-id alias/my-key \
  --tags Key=Environment,Value=Production

# From file
aws secretsmanager create-secret \
  --name prod/myapp/apikey \
  --secret-string file://secret.json

aws secretsmanager list-secrets
aws secretsmanager describe-secret --secret-id prod/myapp/database
aws secretsmanager update-secret \
  --secret-id prod/myapp/database \
  --secret-string '{"username":"admin","password":"newpassword"}'
aws secretsmanager delete-secret \
  --secret-id prod/myapp/database \
  --recovery-window-in-days 30  # or --force-delete-without-recovery

# --- Retrieve secrets ---
aws secretsmanager get-secret-value --secret-id prod/myapp/database
aws secretsmanager get-secret-value \
  --secret-id prod/myapp/database \
  --version-stage AWSPREVIOUS  # get previous version

# --- Rotation ---
aws secretsmanager rotate-secret \
  --secret-id prod/myapp/database \
  --rotation-lambda-arn arn:aws:lambda:us-east-1:123456789012:function:SecretsManagerRotation
aws secretsmanager rotate-secret \
  --secret-id prod/myapp/database \
  --rotate-immediately  # rotate now and enable ongoing rotation

# Built-in rotation for RDS (managed rotation)
aws secretsmanager rotate-secret \
  --secret-id prod/myapp/database
  # If using native rotation (RDS), Secrets Manager handles Lambda automatically

aws secretsmanager describe-secret --secret-id prod/myapp/database  # check RotationEnabled

# Cancel rotation
aws secretsmanager cancel-rotate-secret --secret-id prod/myapp/database

# --- Versions ---
aws secretsmanager list-secret-version-ids --secret-id prod/myapp/database
aws secretsmanager update-secret-version-stage \
  --secret-id prod/myapp/database \
  --version-stage AWSCURRENT \
  --move-to-version-id version-id \
  --remove-from-version-id old-version-id

# --- Resource policy ---
aws secretsmanager put-resource-policy \
  --secret-id prod/myapp/database \
  --resource-policy file://secret-policy.json \
  --block-public-policy
aws secretsmanager get-resource-policy --secret-id prod/myapp/database
aws secretsmanager delete-resource-policy --secret-id prod/myapp/database

# --- Replication ---
aws secretsmanager replicate-secret-to-regions \
  --secret-id prod/myapp/database \
  --add-replica-regions Region=us-west-2 Region=eu-west-1
aws secretsmanager remove-regions-from-replication \
  --secret-id prod/myapp/database \
  --remove-replica-regions us-west-2
aws secretsmanager stop-replication-to-replica --secret-id replica-arn
```

---

## AWS Certificate Manager

```bash
# --- Request certificates ---
# Public cert - DNS validation
aws acm request-certificate \
  --domain-name myapp.example.com \
  --subject-alternative-names "*.myapp.example.com" "api.example.com" \
  --validation-method DNS \
  --idempotency-token myapp-cert-2024

# Public cert - Email validation
aws acm request-certificate \
  --domain-name myapp.example.com \
  --validation-method EMAIL

aws acm list-certificates
aws acm describe-certificate --certificate-arn arn:aws:acm:us-east-1:123456789012:certificate/xxx
aws acm get-certificate --certificate-arn arn:aws:acm:us-east-1:123456789012:certificate/xxx
aws acm delete-certificate --certificate-arn arn:aws:acm:us-east-1:123456789012:certificate/xxx
aws acm renew-certificate --certificate-arn arn:aws:acm:us-east-1:123456789012:certificate/xxx

# Get DNS validation records (to add to Route 53 or other DNS)
aws acm describe-certificate \
  --certificate-arn arn:aws:acm:us-east-1:123456789012:certificate/xxx \
  --query 'Certificate.DomainValidationOptions[*].ResourceRecord'

# Add validation CNAME to Route 53 automatically
aws acm add-tags-to-certificate \
  --certificate-arn arn:aws:acm:us-east-1:123456789012:certificate/xxx \
  --tags Key=Environment,Value=Production
aws acm list-tags-for-certificate \
  --certificate-arn arn:aws:acm:us-east-1:123456789012:certificate/xxx
aws acm remove-tags-from-certificate \
  --certificate-arn arn:aws:acm:us-east-1:123456789012:certificate/xxx \
  --tags Key=Environment

# --- Import certificate ---
aws acm import-certificate \
  --certificate fileb://certificate.pem \
  --private-key fileb://private.key \
  --certificate-chain fileb://chain.pem

# Update imported cert (re-import with same ARN)
aws acm import-certificate \
  --certificate-arn arn:aws:acm:us-east-1:123456789012:certificate/xxx \
  --certificate fileb://new-certificate.pem \
  --private-key fileb://new-private.key \
  --certificate-chain fileb://new-chain.pem

# --- Private CA certs ---
aws acm request-certificate \
  --domain-name internal.example.com \
  --certificate-authority-arn arn:aws:acm-pca:us-east-1:123456789012:certificate-authority/xxx \
  --validation-method NONE  # private CA; no domain validation needed
```

---

## AWS CloudHSM

```bash
# --- Cluster management ---
aws cloudhsmv2 create-cluster \
  --hsm-type hsm2m.medium \
  --subnet-ids subnet-xxxxxxxx subnet-yyyyyyyy
aws cloudhsmv2 describe-clusters
aws cloudhsmv2 describe-clusters \
  --filters clusterIds=cluster-xxxxxxxxxxxxxxxxx
aws cloudhsmv2 delete-cluster --cluster-id cluster-xxxxxxxxxxxxxxxxx

# --- HSM instances ---
aws cloudhsmv2 create-hsm \
  --cluster-id cluster-xxxxxxxxxxxxxxxxx \
  --availability-zone us-east-1a
aws cloudhsmv2 describe-clusters  # see HSMs under each cluster
aws cloudhsmv2 delete-hsm \
  --cluster-id cluster-xxxxxxxxxxxxxxxxx \
  --hsm-id hsm-xxxxxxxxxxxxxxxxx

# --- Initialization (first-time setup) ---
# 1. Get cluster CSR
aws cloudhsmv2 describe-clusters \
  --filters clusterIds=cluster-xxx \
  --query 'Clusters[0].Certificates.ClusterCsr' \
  --output text > cluster.csr
# 2. Sign CSR with your CA → cluster-cert.pem
# 3. Initialize
aws cloudhsmv2 initialize-cluster \
  --cluster-id cluster-xxx \
  --signed-cert file://cluster-cert.pem \
  --trust-anchor file://ca-cert.pem

# --- Backups ---
aws cloudhsmv2 list-tags --resource-id cluster-xxxxxxxxxxxxxxxxx
aws cloudhsmv2 describe-backups
aws cloudhsmv2 copy-backup-to-region \
  --destination-region us-west-2 \
  --backup-id backup-xxxxxxxxxxxxxxxxx
aws cloudhsmv2 delete-backup --backup-id backup-xxxxxxxxxxxxxxxxx
aws cloudhsmv2 restore-backup --backup-id backup-xxxxxxxxxxxxxxxxx

# --- Tags ---
aws cloudhsmv2 tag-resource \
  --resource-id cluster-xxxxxxxxxxxxxxxxx \
  --tag-list Key=Environment,Value=Production
aws cloudhsmv2 untag-resource \
  --resource-id cluster-xxxxxxxxxxxxxxxxx \
  --tag-key-list Environment
```

---

## Amazon GuardDuty

```bash
# --- Enable / manage ---
aws guardduty create-detector \
  --enable \
  --finding-publishing-frequency FIFTEEN_MINUTES \
  --features Name=S3_DATA_EVENTS,Status=ENABLED \
            Name=EKS_AUDIT_LOGS,Status=ENABLED \
            Name=MALWARE_PROTECTION,Status=ENABLED \
            Name=RDS_LOGIN_EVENTS,Status=ENABLED \
            Name=LAMBDA_NETWORK_LOGS,Status=ENABLED \
            Name=RUNTIME_MONITORING,Status=ENABLED
aws guardduty list-detectors
aws guardduty get-detector --detector-id abc123
aws guardduty update-detector \
  --detector-id abc123 \
  --finding-publishing-frequency ONE_HOUR
aws guardduty delete-detector --detector-id abc123

# --- Findings ---
aws guardduty list-findings --detector-id abc123
aws guardduty list-findings --detector-id abc123 \
  --finding-criteria '{"Criterion":{"severity":{"Gte":7},"service.archived":{"Eq":["false"]}}}'
aws guardduty get-findings --detector-id abc123 --finding-ids finding-id-1 finding-id-2
aws guardduty archive-findings --detector-id abc123 --finding-ids finding-id-1
aws guardduty unarchive-findings --detector-id abc123 --finding-ids finding-id-1
aws guardduty update-findings-feedback \
  --detector-id abc123 \
  --finding-ids finding-id-1 \
  --feedback USEFUL \
  --comments "True positive - confirmed malicious activity"

# Describe finding types
aws guardduty list-finding-statistics \
  --detector-id abc123 \
  --finding-statistic-types COUNT_BY_SEVERITY

# Create sample findings (for testing)
aws guardduty create-sample-findings \
  --detector-id abc123 \
  --finding-types UnauthorizedAccess:EC2/TorIPCaller Backdoor:EC2/C&CActivity.B

# --- Trusted IPs and threat intel ---
aws guardduty create-ip-set \
  --detector-id abc123 \
  --name TrustedCorporateIPs \
  --format TXT \
  --location s3://my-guardduty-lists/trusted-ips.txt \
  --activate
aws guardduty list-ip-sets --detector-id abc123
aws guardduty get-ip-set --detector-id abc123 --ip-set-id ip-set-id
aws guardduty update-ip-set \
  --detector-id abc123 \
  --ip-set-id ip-set-id \
  --activate

aws guardduty create-threat-intel-set \
  --detector-id abc123 \
  --name MaliciousIPs \
  --format TXT \
  --location s3://my-guardduty-lists/malicious-ips.txt \
  --activate
aws guardduty list-threat-intel-sets --detector-id abc123

# --- Suppression rules ---
aws guardduty create-filter \
  --detector-id abc123 \
  --name SuppressDevEC2 \
  --action ARCHIVE \
  --finding-criteria '{"Criterion":{"resource.instanceDetails.tags.value":{"Eq":["dev"]},"type":{"Eq":["UnauthorizedAccess:EC2/TorIPCaller"]}}}'
aws guardduty list-filters --detector-id abc123
aws guardduty get-filter --detector-id abc123 --filter-name SuppressDevEC2
aws guardduty delete-filter --detector-id abc123 --filter-name SuppressDevEC2

# --- Multi-account / Organizations ---
aws guardduty enable-organization-admin-account --admin-account-id 123456789012
aws guardduty list-organization-admin-accounts
aws guardduty describe-organization-configuration --detector-id abc123
aws guardduty update-organization-configuration \
  --detector-id abc123 \
  --auto-enable-organization-members NEW_ACCOUNTS \
  --features Name=S3_DATA_EVENTS,AutoEnable=NEW Status=ENABLED

# Member accounts
aws guardduty list-members --detector-id abc123
aws guardduty get-member --detector-id abc123 --account-ids 111111111111
aws guardduty create-members \
  --detector-id abc123 \
  --account-details AccountId=111111111111,Email=account@example.com
aws guardduty invite-members \
  --detector-id abc123 \
  --account-ids 111111111111
aws guardduty disassociate-members --detector-id abc123 --account-ids 111111111111
aws guardduty delete-members --detector-id abc123 --account-ids 111111111111

# --- Finding export ---
aws guardduty create-publishing-destination \
  --detector-id abc123 \
  --destination-type S3 \
  --destination-properties DestinationArn=arn:aws:s3:::my-guardduty-findings,KmsKeyArn=arn:aws:kms:...
aws guardduty list-publishing-destinations --detector-id abc123
aws guardduty delete-publishing-destination --detector-id abc123 --destination-id dest-id

# --- Malware Protection ---
aws guardduty create-malware-protection-plan \
  --role arn:aws:iam::123456789012:role/GuardDutyMalwareProtectionRole \
  --protected-resource S3Bucket="{BucketName=my-bucket,ObjectPrefixes=[uploads/]}"
aws guardduty list-malware-protection-plans
aws guardduty get-malware-protection-plan --malware-protection-plan-id plan-id
aws guardduty delete-malware-protection-plan --malware-protection-plan-id plan-id
```

---

## AWS Security Hub

```bash
# --- Enable ---
aws securityhub enable-security-hub \
  --enable-default-standards \
  --tags Environment=Production
aws securityhub describe-hub
aws securityhub disable-security-hub

# --- Standards ---
aws securityhub describe-standards
aws securityhub batch-enable-standards \
  --standards-subscription-requests \
    StandardsArn=arn:aws:securityhub:us-east-1::standards/aws-foundational-security-best-practices/v/1.0.0 \
    StandardsArn=arn:aws:securityhub:::ruleset/cis-aws-foundations-benchmark/v/1.2.0
aws securityhub get-enabled-standards
aws securityhub batch-disable-standards \
  --standards-subscription-arns arn:aws:securityhub:us-east-1:123456789012:subscription/pci-dss/v/3.2.1

# Controls
aws securityhub describe-standards-controls \
  --standards-subscription-arn arn:aws:securityhub:us-east-1:123456789012:subscription/aws-foundational-security-best-practices/v/1.0.0
aws securityhub update-standards-control \
  --standards-control-arn arn:aws:securityhub:us-east-1:123456789012:control/cis-aws-foundations-benchmark/v/1.2.0/2.9 \
  --control-status DISABLED \
  --disabled-reason "S3 access logging not required for this bucket"

# --- Findings ---
aws securityhub get-findings
aws securityhub get-findings \
  --filters '{"SeverityLabel":[{"Value":"CRITICAL","Comparison":"EQUALS"}],"RecordState":[{"Value":"ACTIVE","Comparison":"EQUALS"}]}'
aws securityhub batch-update-findings \
  --finding-identifiers Id=finding-id,ProductArn=arn:aws:securityhub:us-east-1::product/aws/guardduty \
  --workflow Status=RESOLVED \
  --note Text="Investigated and resolved - false positive",UpdatedBy=soc-analyst

# Custom findings (from your own tools)
aws securityhub batch-import-findings --findings file://findings.json  # must follow ASFF format

# --- Insights ---
aws securityhub get-insights
aws securityhub create-insight \
  --name "Critical unresolved findings by account" \
  --filters '{"SeverityLabel":[{"Value":"CRITICAL","Comparison":"EQUALS"}],"WorkflowStatus":[{"Value":"NEW","Comparison":"EQUALS"}]}' \
  --group-by-attribute AwsAccountId
aws securityhub get-insight-results --insight-arn arn:aws:securityhub:us-east-1:123456789012:insight/123456789012/custom/xxx
aws securityhub delete-insight --insight-arn arn:aws:securityhub:...:insight/xxx

# --- Custom actions (for EventBridge) ---
aws securityhub create-action-target \
  --name "Notify Slack" \
  --description "Send finding to Slack channel via EventBridge" \
  --id NOTIFY-SLACK
aws securityhub describe-action-targets
aws securityhub update-action-target \
  --action-target-arn arn:aws:securityhub:us-east-1:123456789012:action/custom/NOTIFY-SLACK \
  --description "Updated description"
aws securityhub delete-action-target \
  --action-target-arn arn:aws:securityhub:us-east-1:123456789012:action/custom/NOTIFY-SLACK

# --- Multi-account ---
aws securityhub enable-organization-admin-account --admin-account-id 123456789012
aws securityhub list-organization-admin-accounts
aws securityhub describe-organization-configuration
aws securityhub update-organization-configuration \
  --auto-enable \
  --auto-enable-standards DEFAULT

# Aggregation
aws securityhub create-finding-aggregator --region-linking-mode ALL_REGIONS
aws securityhub get-finding-aggregator \
  --finding-aggregator-arn arn:aws:securityhub:us-east-1:123456789012:finding-aggregator/xxx
aws securityhub update-finding-aggregator \
  --finding-aggregator-arn arn:aws:securityhub:us-east-1:123456789012:finding-aggregator/xxx \
  --region-linking-mode SPECIFIED_REGIONS \
  --regions us-east-1 us-west-2 eu-west-1
aws securityhub delete-finding-aggregator \
  --finding-aggregator-arn arn:aws:securityhub:us-east-1:123456789012:finding-aggregator/xxx
```

---

## Amazon Inspector

```bash
# --- Enable ---
aws inspector2 enable \
  --account-ids 123456789012 \
  --resource-types EC2 ECR LAMBDA LAMBDA_CODE
aws inspector2 describe-organization-configuration
aws inspector2 update-organization-configuration \
  --auto-enable Ec2=true,Ecr=true,Lambda=true,LambdaCode=true
aws inspector2 disable --account-ids 123456789012 --resource-types ECR

# --- Findings ---
aws inspector2 list-findings
aws inspector2 list-findings \
  --filter-criteria '{"severities":[{"comparison":"EQUALS","value":"CRITICAL"}],"findingStatus":[{"comparison":"EQUALS","value":"ACTIVE"}]}'
aws inspector2 batch-get-finding-details --finding-arns arn:aws:inspector2:us-east-1:123456789012:finding/xxx
aws inspector2 list-finding-aggregations \
  --aggregation-type AWS_EC2_INSTANCE
aws inspector2 get-findings-report-status

# Suppress findings
aws inspector2 create-filter \
  --name SuppressAcceptedRisk \
  --action SUPPRESS \
  --filter-criteria '{"vulnerabilityId":[{"comparison":"EQUALS","value":"CVE-2021-44228"}]}'
aws inspector2 list-filters
aws inspector2 update-filter \
  --filter-arn arn:aws:inspector2:us-east-1:123456789012:filter/xxx \
  --name UpdatedFilterName
aws inspector2 delete-filter --filter-arn arn:aws:inspector2:...:filter/xxx

# --- Coverage ---
aws inspector2 list-coverage  # see all resources being scanned
aws inspector2 list-coverage-statistics  # summary counts
aws inspector2 get-configuration  # EC2/ECR/Lambda scan settings

# --- CIS Scans ---
aws inspector2 create-cis-scan-configuration \
  --scan-name "CIS Level 1 Weekly" \
  --security-level LEVEL_1 \
  --schedule Weekly='{Day=MONDAY,StartTime={TimeOfDay="08:00",Timezone="UTC"}}' \
  --targets AccountIds=123456789012,All=false
aws inspector2 list-cis-scan-configurations
aws inspector2 list-cis-scans
aws inspector2 get-cis-scan-report \
  --scan-arn arn:aws:inspector2:us-east-1:123456789012:owner/123456789012/cis-scan/xxx \
  --target-accounts 123456789012 \
  --report-format PDF \
  --s3-destination BucketName=my-bucket,KeyPrefix=cis-reports/

# --- SBOM export ---
aws inspector2 create-sbom-export \
  --report-format CYCLONEDX_1_4 \
  --s3-destination BucketName=my-bucket,KeyPrefix=sboms/ \
  --resource-filter-criteria '{"ec2InstanceTags":[{"comparison":"EQUALS","key":"Environment","value":"Production"}]}'
aws inspector2 get-sbom-export --report-id report-id
aws inspector2 cancel-sbom-export --report-id report-id

# --- Multi-account ---
aws inspector2 enable-delegated-admin-account --delegated-admin-account-id 123456789012
aws inspector2 get-delegated-admin-account
aws inspector2 disable-delegated-admin-account --delegated-admin-account-id 123456789012
aws inspector2 list-member-accounts
aws inspector2 associate-member --account-id 111111111111
aws inspector2 disassociate-member --account-id 111111111111
```

---

## Amazon Macie

```bash
# --- Enable ---
aws macie2 enable-macie --finding-publishing-frequency FIFTEEN_MINUTES --status ENABLED
aws macie2 get-macie-session
aws macie2 update-macie-session \
  --finding-publishing-frequency ONE_HOUR \
  --status PAUSED  # or ENABLED
aws macie2 disable-macie

# --- S3 bucket inventory ---
aws macie2 describe-buckets  # all S3 buckets Macie monitors
aws macie2 describe-buckets \
  --criteria '{"sharedAccess":{"eq":["EXTERNAL"]}}'  # externally shared buckets
aws macie2 get-bucket-statistics
aws macie2 get-s3-resources  # S3 resources Macie is configured to monitor

# --- Sensitive data discovery jobs ---
aws macie2 create-classification-job \
  --name WeeklyS3Scan \
  --job-type SCHEDULED \
  --s3-job-definition '{
    "bucketDefinitions": [{"accountId":"123456789012","buckets":["my-data-bucket"]}]
  }' \
  --schedule-frequency DailySchedule={} \
  --sampling-percentage 100 \
  --managed-data-identifier-selector ALL

aws macie2 list-classification-jobs
aws macie2 describe-classification-job --job-id job-id
aws macie2 update-classification-job \
  --job-id job-id \
  --job-status CANCELLED  # RUNNING, PAUSED, CANCELLED (permanent)

# --- Findings ---
aws macie2 list-findings
aws macie2 list-findings \
  --finding-criteria '{"criterion":{"severity.description":{"eq":["High","Critical"]}}}'
aws macie2 get-findings --finding-ids finding-id-1 finding-id-2
aws macie2 get-finding-statistics \
  --group-by resourcesAffected.s3Object.path

# Suppress findings
aws macie2 create-findings-filter \
  --name SuppressTestData \
  --action ARCHIVE \
  --finding-criteria '{"criterion":{"resourcesAffected.s3Bucket.name":{"eq":["test-data-bucket"]}}}'
aws macie2 list-findings-filters
aws macie2 get-findings-filter --id filter-id
aws macie2 update-findings-filter \
  --id filter-id \
  --name UpdatedFilterName
aws macie2 delete-findings-filter --id filter-id

# --- Custom data identifiers ---
aws macie2 create-custom-data-identifier \
  --name InternalEmployeeID \
  --regex "EMP-[0-9]{6}" \
  --keywords "employee" "staff" \
  --ignore-words "test" "sample" \
  --maximum-match-distance 50
aws macie2 list-custom-data-identifiers
aws macie2 get-custom-data-identifier --id identifier-id
aws macie2 test-custom-data-identifier \
  --regex "EMP-[0-9]{6}" \
  --sample-text "Employee EMP-123456 has been flagged"  # returns matchCount
aws macie2 delete-custom-data-identifier --id identifier-id

# --- Allow lists ---
aws macie2 create-allow-list \
  --name KnownTestSSNs \
  --criteria Regex="{Regex=\"123-45-6789|000-00-0000\"}"
aws macie2 list-allow-lists
aws macie2 get-allow-list --id list-id
aws macie2 update-allow-list \
  --id list-id \
  --name UpdatedListName \
  --criteria Regex="{Regex=\"123-45-6789\"}"
aws macie2 delete-allow-list --id list-id

# --- Multi-account ---
aws macie2 enable-organization-admin-account --admin-account-id 123456789012
aws macie2 describe-organization-configuration
aws macie2 update-organization-configuration --auto-enable
aws macie2 list-members
aws macie2 create-member --account AccountId=111111111111,Email=account@example.com
aws macie2 get-member --id 111111111111
aws macie2 delete-member --id 111111111111

# --- Finding export ---
aws macie2 put-findings-publication-configuration \
  --security-hub-configuration PublishClassificationFindings=true,PublishPolicyFindings=true
aws macie2 get-findings-publication-configuration
```

---

## Amazon Detective

```bash
# --- Enable (create behavior graph) ---
aws detective create-graph --tags Environment=Production
aws detective list-graphs
aws detective get-members --graph-arn arn:aws:detective:us-east-1:123456789012:graph:xxx

# --- Multi-account ---
aws detective create-members \
  --graph-arn arn:aws:detective:us-east-1:123456789012:graph:xxx \
  --accounts AccountId=111111111111,EmailAddress=account@example.com \
  --message "You are invited to join Detective for security investigation"
aws detective list-members --graph-arn arn:aws:detective:us-east-1:123456789012:graph:xxx
aws detective delete-members \
  --graph-arn arn:aws:detective:us-east-1:123456789012:graph:xxx \
  --account-ids 111111111111
aws detective disassociate-membership \
  --graph-arn arn:aws:detective:us-east-1:123456789012:graph:xxx

# Member invitations
aws detective accept-invitation \
  --graph-arn arn:aws:detective:us-east-1:123456789012:graph:xxx
aws detective reject-invitation \
  --graph-arn arn:aws:detective:us-east-1:123456789012:graph:xxx
aws detective list-invitations

# --- Organization integration ---
aws detective enable-organization-admin-account --account-id 123456789012
aws detective list-organization-admin-accounts
aws detective describe-organization-configuration \
  --graph-arn arn:aws:detective:us-east-1:123456789012:graph:xxx
aws detective update-organization-configuration \
  --graph-arn arn:aws:detective:us-east-1:123456789012:graph:xxx \
  --auto-enable

# --- Investigations ---
aws detective start-investigation \
  --graph-arn arn:aws:detective:us-east-1:123456789012:graph:xxx \
  --entity-arn arn:aws:iam::123456789012:user/alice \
  --scope-start-time 2024-01-01T00:00:00Z \
  --scope-end-time 2024-01-07T23:59:59Z
aws detective list-investigations \
  --graph-arn arn:aws:detective:us-east-1:123456789012:graph:xxx
aws detective get-investigation \
  --graph-arn arn:aws:detective:us-east-1:123456789012:graph:xxx \
  --investigation-id investigation-id
aws detective update-investigation-state \
  --graph-arn arn:aws:detective:us-east-1:123456789012:graph:xxx \
  --investigation-id investigation-id \
  --state CLOSED
aws detective list-indicators \
  --graph-arn arn:aws:detective:us-east-1:123456789012:graph:xxx \
  --investigation-id investigation-id

# Delete graph (disables Detective)
aws detective delete-graph --graph-arn arn:aws:detective:us-east-1:123456789012:graph:xxx
```

---

## AWS WAF

```bash
# --- Web ACLs ---
aws wafv2 create-web-acl \
  --name MyWebACL \
  --scope REGIONAL \
  --default-action Allow={} \
  --rules file://rules.json \
  --visibility-config SampledRequestsEnabled=true,CloudWatchMetricsEnabled=true,MetricName=MyWebACL

aws wafv2 list-web-acls --scope REGIONAL
aws wafv2 get-web-acl --name MyWebACL --scope REGIONAL --id web-acl-id
aws wafv2 update-web-acl \
  --name MyWebACL --scope REGIONAL --id web-acl-id \
  --lock-token $(aws wafv2 get-web-acl --name MyWebACL --scope REGIONAL --id web-acl-id --query LockToken --output text) \
  --default-action Block={} \
  --rules file://updated-rules.json \
  --visibility-config SampledRequestsEnabled=true,CloudWatchMetricsEnabled=true,MetricName=MyWebACL
aws wafv2 delete-web-acl --name MyWebACL --scope REGIONAL --id web-acl-id --lock-token <token>

# Associate with resource
aws wafv2 associate-web-acl \
  --web-acl-arn arn:aws:wafv2:us-east-1:123456789012:regional/webacl/MyWebACL/xxx \
  --resource-arn arn:aws:elasticloadbalancing:us-east-1:123456789012:loadbalancer/app/my-alb/xxx
aws wafv2 get-web-acl-for-resource \
  --resource-arn arn:aws:elasticloadbalancing:us-east-1:123456789012:loadbalancer/app/my-alb/xxx
aws wafv2 disassociate-web-acl \
  --resource-arn arn:aws:elasticloadbalancing:us-east-1:123456789012:loadbalancer/app/my-alb/xxx

# --- Managed rule groups ---
aws wafv2 list-available-managed-rule-groups --scope REGIONAL
aws wafv2 describe-managed-rule-group \
  --vendor-name AWS \
  --name AWSManagedRulesCommonRuleSet \
  --scope REGIONAL

# Example rules.json with managed rule group
cat > rules.json << 'EOF'
[{
  "Name": "AWSManagedCommon",
  "Priority": 1,
  "Statement": {
    "ManagedRuleGroupStatement": {
      "VendorName": "AWS",
      "Name": "AWSManagedRulesCommonRuleSet",
      "ExcludedRules": []
    }
  },
  "OverrideAction": {"None": {}},
  "VisibilityConfig": {
    "SampledRequestsEnabled": true,
    "CloudWatchMetricsEnabled": true,
    "MetricName": "AWSManagedCommon"
  }
}]
EOF

# --- IP sets ---
aws wafv2 create-ip-set \
  --name BlockedIPs \
  --scope REGIONAL \
  --ip-address-version IPV4 \
  --addresses 192.0.2.0/24 198.51.100.0/24
aws wafv2 list-ip-sets --scope REGIONAL
aws wafv2 get-ip-set --name BlockedIPs --scope REGIONAL --id ip-set-id
aws wafv2 update-ip-set \
  --name BlockedIPs --scope REGIONAL --id ip-set-id \
  --lock-token <token> \
  --addresses 192.0.2.0/24 198.51.100.0/24 203.0.113.0/24
aws wafv2 delete-ip-set --name BlockedIPs --scope REGIONAL --id ip-set-id --lock-token <token>

# --- Logging ---
aws wafv2 put-logging-configuration \
  --logging-configuration \
    ResourceArn=arn:aws:wafv2:us-east-1:123456789012:regional/webacl/MyWebACL/xxx,\
    LogDestinationConfigs=arn:aws:firehose:us-east-1:123456789012:deliverystream/aws-waf-logs-stream
aws wafv2 get-logging-configuration \
  --resource-arn arn:aws:wafv2:us-east-1:123456789012:regional/webacl/MyWebACL/xxx
aws wafv2 delete-logging-configuration \
  --resource-arn arn:aws:wafv2:us-east-1:123456789012:regional/webacl/MyWebACL/xxx

# --- Sampled requests (inspect recent traffic) ---
aws wafv2 get-sampled-requests \
  --web-acl-arn arn:aws:wafv2:us-east-1:123456789012:regional/webacl/MyWebACL/xxx \
  --rule-metric-name MyWebACL \
  --scope REGIONAL \
  --time-window StartTime=$(date -u -d '1 hour ago' +%s),EndTime=$(date -u +%s) \
  --max-items 100
```

---

## AWS Shield

```bash
# --- Subscribe ---
aws shield create-subscription
aws shield get-subscription-state
aws shield describe-subscription

# --- Protections ---
aws shield create-protection \
  --name MyALBProtection \
  --resource-arn arn:aws:elasticloadbalancing:us-east-1:123456789012:loadbalancer/app/my-alb/xxx
aws shield list-protections
aws shield describe-protection --protection-id protection-id
aws shield delete-protection --protection-id protection-id

# Protection groups
aws shield create-protection-group \
  --protection-group-id WebTier \
  --aggregation SUM \
  --pattern BY_RESOURCE_TYPE \
  --resource-type APPLICATION_LOAD_BALANCER
aws shield list-protection-groups
aws shield describe-protection-group --protection-group-id WebTier
aws shield delete-protection-group --protection-group-id WebTier

# --- Attack monitoring ---
aws shield list-attacks \
  --start-time StartTime=$(date -u -d '7 days ago' --iso-8601=seconds) \
  --end-time EndTime=$(date -u --iso-8601=seconds)
aws shield describe-attack --attack-id attack-id
aws shield describe-attack-statistics

# --- DRT access ---
aws shield associate-drt-role \
  --role-arn arn:aws:iam::123456789012:role/AWSShieldDRTAccessRole
aws shield associate-drt-log-bucket --log-bucket my-vpc-flowlogs-bucket
aws shield describe-drt-access
aws shield disassociate-drt-role

# --- Proactive engagement ---
aws shield associate-proactive-engagement-details \
  --emergency-contact-list \
    EmailAddress=secops@example.com,PhoneNumber=+15555555555,ContactNotes="24/7 on-call"
aws shield enable-proactive-engagement
aws shield disable-proactive-engagement

# --- Auto L7 mitigation (requires WAF) ---
aws shield enable-application-layer-automatic-response \
  --resource-arn arn:aws:cloudfront::123456789012:distribution/EDFDVBD6EXAMPLE \
  --action Block={}
aws shield disable-application-layer-automatic-response \
  --resource-arn arn:aws:cloudfront::123456789012:distribution/EDFDVBD6EXAMPLE

# Update subscription
aws shield update-subscription --auto-renew ENABLED
```

---

## AWS Network Firewall

```bash
# --- Firewalls ---
aws network-firewall create-firewall \
  --firewall-name ProdVPCFirewall \
  --firewall-policy-arn arn:aws:network-firewall:us-east-1:123456789012:firewall-policy/MyPolicy \
  --vpc-id vpc-xxxxxxxx \
  --subnet-mappings SubnetId=subnet-xxxxxxxx
aws network-firewall describe-firewall --firewall-name ProdVPCFirewall
aws network-firewall list-firewalls
aws network-firewall delete-firewall --firewall-name ProdVPCFirewall

# Add/remove subnets (multi-AZ)
aws network-firewall associate-subnets \
  --firewall-name ProdVPCFirewall \
  --subnet-mappings SubnetId=subnet-yyyyyyyy
aws network-firewall disassociate-subnets \
  --firewall-name ProdVPCFirewall \
  --subnet-ids subnet-yyyyyyyy

# --- Firewall policies ---
aws network-firewall create-firewall-policy \
  --firewall-policy-name MyPolicy \
  --firewall-policy '{
    "StatelessDefaultActions": ["aws:forward_to_sfe"],
    "StatelessFragmentDefaultActions": ["aws:forward_to_sfe"],
    "StatefulRuleGroupReferences": [{
      "ResourceArn": "arn:aws:network-firewall:us-east-1:123456789012:stateful-rulegroup/MyRules"
    }],
    "StatefulDefaultActions": ["aws:drop_established"],
    "StatefulEngineOptions": {"RuleOrder": "STRICT_ORDER"}
  }'
aws network-firewall list-firewall-policies
aws network-firewall describe-firewall-policy --firewall-policy-name MyPolicy
POLICY_TOKEN=$(aws network-firewall describe-firewall-policy --firewall-policy-name MyPolicy --query 'UpdateToken' --output text)
aws network-firewall update-firewall-policy \
  --firewall-policy-name MyPolicy \
  --update-token "$POLICY_TOKEN" \
  --firewall-policy file://updated-policy.json
aws network-firewall delete-firewall-policy --firewall-policy-name MyPolicy

# --- Rule groups (domain list - most common) ---
aws network-firewall create-rule-group \
  --rule-group-name AllowedDomains \
  --type STATEFUL \
  --capacity 100 \
  --rule-group '{
    "RulesSource": {
      "RulesSourceList": {
        "Targets": [".amazonaws.com", ".github.com", ".docker.io"],
        "TargetTypes": ["HTTP_HOST", "TLS_SNI"],
        "GeneratedRulesType": "ALLOWLIST"
      }
    }
  }'

# Rule group (Suricata rules)
aws network-firewall create-rule-group \
  --rule-group-name SuricataRules \
  --type STATEFUL \
  --capacity 200 \
  --rule-group '{
    "RulesSource": {
      "RulesString": "drop http any any -> any any (http.uri; content:\"/malicious\"; nocase; sid:1001; rev:1;)\nalert tls any any -> any any (tls.sni; content:\".malware.com\"; nocase; sid:1002; rev:1;)"
    }
  }'

aws network-firewall list-rule-groups
aws network-firewall describe-rule-group --rule-group-name AllowedDomains --type STATEFUL
RG_TOKEN=$(aws network-firewall describe-rule-group --rule-group-name AllowedDomains --type STATEFUL --query 'UpdateToken' --output text)
aws network-firewall update-rule-group \
  --rule-group-name AllowedDomains \
  --type STATEFUL \
  --update-token "$RG_TOKEN" \
  --rule-group file://updated-rule-group.json
aws network-firewall delete-rule-group --rule-group-name AllowedDomains --type STATEFUL

# --- Logging ---
aws network-firewall update-logging-configuration \
  --firewall-name ProdVPCFirewall \
  --logging-configuration '{
    "LogDestinationConfigs": [
      {
        "LogType": "ALERT",
        "LogDestinationType": "CloudWatchLogs",
        "LogDestination": {"logGroup": "/aws/network-firewall/alerts"}
      },
      {
        "LogType": "FLOW",
        "LogDestinationType": "S3",
        "LogDestination": {"bucketName": "my-nfw-logs", "prefix": "flow/"}
      }
    ]
  }'
aws network-firewall describe-logging-configuration --firewall-name ProdVPCFirewall
```

---

## AWS Firewall Manager

```bash
# --- Setup ---
aws fms associate-admin-account --admin-account 123456789012  # run from Org management account
aws fms get-admin-account
aws fms disassociate-admin-account

# --- Policies ---
# WAF policy example
aws fms put-policy --policy '{
  "PolicyName": "EnforceWAFOnALBs",
  "SecurityServicePolicyData": {
    "Type": "WAFV2",
    "ManagedServiceData": "{\"type\":\"WAFV2\",\"preProcessRuleGroups\":[{\"managedRuleGroupIdentifier\":{\"vendorName\":\"AWS\",\"managedRuleGroupName\":\"AWSManagedRulesCommonRuleSet\"},\"overrideAction\":{\"type\":\"NONE\"},\"ruleGroupArn\":null,\"excludeRules\":[],\"ruleGroupType\":\"ManagedRuleGroup\"}],\"postProcessRuleGroups\":[],\"defaultAction\":{\"type\":\"ALLOW\"},\"overrideCustomerWebACLAssociation\":false,\"loggingConfiguration\":null}"
  },
  "ResourceType": "AWS::ElasticLoadBalancingV2::LoadBalancer",
  "ResourceTypeList": [],
  "ResourceTags": [],
  "ExcludeResourceTags": false,
  "RemediationEnabled": true,
  "IncludeMap": {"ORGUNIT": ["ou-xxxx-xxxxxxxx"]},
  "ExcludeMap": {}
}'

aws fms list-policies
aws fms get-policy --policy-id policy-id
aws fms delete-policy --policy-id policy-id --delete-all-policy-resources

# --- Compliance ---
aws fms list-compliance-status --policy-id policy-id
aws fms get-compliance-detail \
  --policy-id policy-id \
  --member-account 111111111111
aws fms get-violation-details \
  --policy-id policy-id \
  --member-account 111111111111 \
  --resource-id arn:aws:elasticloadbalancing:... \
  --resource-type AWS::ElasticLoadBalancingV2::LoadBalancer

# --- Notification ---
aws fms put-notification-channel \
  --sns-topic-arn arn:aws:sns:us-east-1:123456789012:FMSAlerts \
  --sns-role-name arn:aws:iam::123456789012:role/FMSSNSRole
aws fms get-notification-channel
aws fms delete-notification-channel

# --- Member accounts ---
aws fms list-member-accounts
```
