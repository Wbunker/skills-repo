# Infrastructure as Code (CloudFormation / CDK / Terraform)

Provision Cognito declaratively. For one-off CLI setup see [cli-commands.md](cli-commands.md). Resource-name mapping across tools is at the bottom.

## Table of Contents
1. [CloudFormation](#cloudformation)
2. [AWS CDK (TypeScript)](#aws-cdk-typescript)
3. [Terraform](#terraform)
4. [Resource name map](#resource-name-map)
5. [IaC gotchas](#iac-gotchas)

---

## CloudFormation

```yaml
Resources:
  UserPool:
    Type: AWS::Cognito::UserPool
    Properties:
      UserPoolName: MyApp
      UsernameAttributes: [email]
      AutoVerifiedAttributes: [email]
      MfaConfiguration: OPTIONAL
      UserPoolTier: ESSENTIALS
      Policies:
        PasswordPolicy:
          MinimumLength: 8
          RequireUppercase: true
          RequireLowercase: true
          RequireNumbers: true
          RequireSymbols: false
      AccountRecoverySetting:
        RecoveryMechanisms:
          - { Name: verified_email, Priority: 1 }
      Schema:
        - { Name: email, AttributeDataType: String, Required: true, Mutable: true }

  UserPoolClient:
    Type: AWS::Cognito::UserPoolClient
    Properties:
      UserPoolId: !Ref UserPool
      ClientName: web
      GenerateSecret: false
      ExplicitAuthFlows: [ALLOW_USER_SRP_AUTH, ALLOW_USER_AUTH, ALLOW_REFRESH_TOKEN_AUTH]
      PreventUserExistenceErrors: ENABLED
      SupportedIdentityProviders: [COGNITO]
      AllowedOAuthFlows: [code]
      AllowedOAuthScopes: [openid, email, profile]
      AllowedOAuthFlowsUserPoolClient: true
      CallbackURLs: [https://app.example.com/callback]
      LogoutURLs: [https://app.example.com/]

  UserPoolDomain:
    Type: AWS::Cognito::UserPoolDomain
    Properties:
      UserPoolId: !Ref UserPool
      Domain: myapp-auth       # prefix domain

Outputs:
  UserPoolId:   { Value: !Ref UserPool }
  ClientId:     { Value: !Ref UserPoolClient }
  Issuer:       { Value: !Sub "https://cognito-idp.${AWS::Region}.amazonaws.com/${UserPool}" }
```

Other resource types: `AWS::Cognito::UserPoolIdentityProvider`, `AWS::Cognito::UserPoolGroup`, `AWS::Cognito::UserPoolResourceServer`, `AWS::Cognito::IdentityPool`, `AWS::Cognito::IdentityPoolRoleAttachment`.

## AWS CDK (TypeScript)

```ts
import { Duration } from "aws-cdk-lib";
import {
  UserPool, AccountRecovery, VerificationEmailStyle, OAuthScope,
} from "aws-cdk-lib/aws-cognito";

const pool = new UserPool(this, "UserPool", {
  userPoolName: "MyApp",
  signInAliases: { email: true },
  autoVerify: { email: true },
  selfSignUpEnabled: true,
  mfa: cognito.Mfa.OPTIONAL,
  mfaSecondFactor: { sms: true, otp: true },
  passwordPolicy: { minLength: 8, requireDigits: true, requireLowercase: true, requireUppercase: true },
  accountRecovery: AccountRecovery.EMAIL_ONLY,
  standardAttributes: { email: { required: true, mutable: true } },
  customAttributes: { tenant_id: new cognito.StringAttribute({ mutable: true }) },
});

const client = pool.addClient("web", {
  authFlows: { userSrp: true, user: true },
  preventUserExistenceErrors: true,
  oAuth: {
    flows: { authorizationCodeGrant: true },
    scopes: [OAuthScope.OPENID, OAuthScope.EMAIL, OAuthScope.PROFILE],
    callbackUrls: ["https://app.example.com/callback"],
    logoutUrls: ["https://app.example.com/"],
  },
  accessTokenValidity: Duration.minutes(60),
  refreshTokenValidity: Duration.days(30),
});

pool.addDomain("Domain", { cognitoDomain: { domainPrefix: "myapp-auth" } });

// Lambda trigger:
pool.addTrigger(cognito.UserPoolOperation.PRE_SIGN_UP, myPreSignUpFn);
```

CDK wires Lambda invoke permissions and trigger references automatically — prefer it for trigger-heavy stacks.

## Terraform

```hcl
resource "aws_cognito_user_pool" "main" {
  name                     = "MyApp"
  username_attributes      = ["email"]
  auto_verified_attributes = ["email"]
  mfa_configuration        = "OPTIONAL"
  user_pool_tier           = "ESSENTIALS"

  password_policy {
    minimum_length    = 8
    require_uppercase = true
    require_lowercase = true
    require_numbers   = true
    require_symbols   = false
  }

  account_recovery_setting {
    recovery_mechanism { name = "verified_email"  priority = 1 }
  }

  schema {
    name                = "email"
    attribute_data_type = "String"
    required            = true
    mutable             = true
  }
}

resource "aws_cognito_user_pool_client" "web" {
  name                                 = "web"
  user_pool_id                         = aws_cognito_user_pool.main.id
  generate_secret                      = false
  explicit_auth_flows                  = ["ALLOW_USER_SRP_AUTH", "ALLOW_USER_AUTH", "ALLOW_REFRESH_TOKEN_AUTH"]
  prevent_user_existence_errors        = "ENABLED"
  supported_identity_providers         = ["COGNITO"]
  allowed_oauth_flows                  = ["code"]
  allowed_oauth_scopes                 = ["openid", "email", "profile"]
  allowed_oauth_flows_user_pool_client = true
  callback_urls                        = ["https://app.example.com/callback"]
  logout_urls                          = ["https://app.example.com/"]
}

resource "aws_cognito_user_pool_domain" "main" {
  domain       = "myapp-auth"
  user_pool_id = aws_cognito_user_pool.main.id
}

output "issuer" {
  value = "https://cognito-idp.${data.aws_region.current.name}.amazonaws.com/${aws_cognito_user_pool.main.id}"
}
```

Other resources: `aws_cognito_identity_provider`, `aws_cognito_user_group`, `aws_cognito_resource_server`, `aws_cognito_identity_pool`, `aws_cognito_identity_pool_roles_attachment`.

## Resource name map

| Concept | CloudFormation | CDK | Terraform |
|---|---|---|---|
| User pool | `AWS::Cognito::UserPool` | `UserPool` | `aws_cognito_user_pool` |
| App client | `AWS::Cognito::UserPoolClient` | `UserPoolClient` / `addClient` | `aws_cognito_user_pool_client` |
| Domain | `AWS::Cognito::UserPoolDomain` | `addDomain` | `aws_cognito_user_pool_domain` |
| IdP | `AWS::Cognito::UserPoolIdentityProvider` | `UserPoolIdentityProvider*` | `aws_cognito_identity_provider` |
| Group | `AWS::Cognito::UserPoolGroup` | `CfnUserPoolGroup` | `aws_cognito_user_group` |
| Resource server | `AWS::Cognito::UserPoolResourceServer` | `UserPoolResourceServer` | `aws_cognito_resource_server` |
| Identity pool | `AWS::Cognito::IdentityPool` | `IdentityPool` (`aws-cognito-identitypool` module) | `aws_cognito_identity_pool` |
| Identity pool roles | `AWS::Cognito::IdentityPoolRoleAttachment` | (part of `IdentityPool`) | `aws_cognito_identity_pool_roles_attachment` |

## IaC gotchas

- **Immutable = replacement.** Changing `UsernameAttributes`, `Schema`, or adding a required attribute forces a **new user pool** — all users are lost. Get sign-in identifiers and required attributes right on day one.
- **Custom domain certs must be in us-east-1** regardless of the pool's region (CloudFront requirement).
- **Client secret in state.** If you set `GenerateSecret: true`, the secret lands in CloudFormation/Terraform state — treat state as sensitive. Prefer no secret for public clients.
- **Ordering:** identity providers must exist before an app client can list them in `SupportedIdentityProviders`; declare a `DependsOn` (CFN) or let Terraform/CDK infer via references.
- **Lambda permissions:** outside CDK, add the `AWS::Lambda::Permission` (or `aws_lambda_permission`) granting `cognito-idp.amazonaws.com` invoke rights, scoped by `SourceArn` = pool ARN.
- CloudFormation doesn't cover every newest feature immediately (e.g. some managed-login branding); fall back to the CLI or a custom resource when a property is missing.
- **SDK/CLI updates are full-replacement.** If you script changes with `UpdateUserPool`/`UpdateUserPoolClient` outside your IaC tool, omitted parameters reset to defaults (wiping triggers/schema/message config) — always read-modify-write the whole config. IaC tools handle this for you, so don't mix hand-scripted updates with a managed stack. See [app-clients.md](app-clients.md#updating-clients--pools-safely).
