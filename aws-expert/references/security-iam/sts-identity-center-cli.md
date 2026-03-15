# AWS STS & IAM Identity Center — CLI Reference
For service concepts, see [sts-identity-center-capabilities.md](sts-identity-center-capabilities.md).

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
