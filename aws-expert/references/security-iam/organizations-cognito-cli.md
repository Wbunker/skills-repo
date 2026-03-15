# AWS Organizations & Amazon Cognito — CLI Reference
For service concepts, see [organizations-cognito-capabilities.md](organizations-cognito-capabilities.md).

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
