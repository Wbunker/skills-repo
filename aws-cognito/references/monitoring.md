# Monitoring, Logging & Auditing

Three complementary observability layers: **CloudTrail** (API/endpoint audit trail), **CloudWatch metrics** (aggregated activity + quota usage), and **log export** (fine-grained delivery-error and sign-in-activity logs). Threat-protection user-activity logs are also covered in [threat-protection.md](threat-protection.md#event-history-feedback--log-export).

## Table of Contents
1. [CloudTrail](#cloudtrail)
2. [CloudWatch metrics](#cloudwatch-metrics)
3. [Log export](#log-export)

---

## CloudTrail

- **User pool ops = management events** (logged by default). **Identity pool `GetId`/`GetCredentialsForIdentity`/`GetOpenIdToken*`/`UnlinkIdentity` = data events** — **not logged by default**, extra cost, require an event selector (`resources.type = AWS::Cognito::IdentityPool`).
- **`eventType` distinguishes source**: `AwsApiCall` = your app called the Cognito API; **`AwsServiceEvent` = a managed-login / OAuth endpoint** was hit. Endpoint events have names like `Token_POST`, `login_POST`, `signup_POST`, `mfa_totp_POST`, `passkeys_add_POST`, `Logout`, `UserInfo_GET`, `SAML2Response_POST` — the way to audit hosted-UI activity (which never hits the API).
- **Sensitive fields are redacted** as `HIDDEN_DUE_TO_SECURITY_REASONS` (passwords, tokens). But Cognito does **not** auto-mask PII you put in free-form fields — don't log secrets/PII into attributes.
- **CloudTrail records `UserSub`, not `UserName`**, for user-specific requests — resolve a sub to a user with `ListUsers --filter 'sub = "..."'`.
- Analyze with **CloudWatch Logs Insights** (source `cognito-idp.amazonaws.com`). Useful queries:
  ```
  # Top IPs causing auth failures (credential-stuffing signal)
  filter eventSource="cognito-idp.amazonaws.com" and errorCode="NotAuthorizedException"
  | stats count(*) as n by sourceIPAddress, eventName | sort n desc | limit 25

  # Active vs dormant M2M app clients (audit client_credentials use)
  filter eventName="Token_POST" and additionalEventData.requestParameters.grant_type.0="client_credentials"
    and additionalEventData.responseParameters.status="200"
  | stats count(*) as n, latest(eventTime) as lastUsed by additionalEventData.clientId
  ```

## CloudWatch metrics

Two namespaces: **`AWS/Cognito`** (activity) and **`AWS/Usage`** (quota usage).

**Activity** — each has a `…Successes` and `…Throttles` pair; dimensions `UserPool` + `UserPoolClient` (federation adds `IdentityProvider`):
`SignUp`, `SignIn`, `TokenRefresh`, `Federation`.

- **Token *refresh* is separate from `SignIn`** — `SignInSuccesses` excludes refreshes.
- **A throttled request scores 0** (counts as unsuccessful). Success **rate** = `Average`; **failures** = `SampleCount − Sum` (Math expression); throttles = `Sum` of the throttle metric.
- Odd `UserPoolClient` values: **`Admin`** (request made by an admin API), **`Invalid`** (bad client id in the request). `SignUp` metrics are **not** emitted for CSV import or migrate-user.

**Usage** (`AWS/Usage`, dimension `Resource` = category): **`CallCount`** and **`ThrottleCount`** per API category — the basis for quota alarms (pair with Service Quotas to alarm at a % of your limit).

**Threat protection** (`AWS/Cognito`, dims `Operation` ∈ {SignIn, SignUp, PasswordChange}, `UserPoolId`, `RiskLevel`): `CompromisedCredentialRisk`, `AccountTakeoverRisk`, `OverrideBlock`, `Risk`, `NoRisk`. Console groups them **By Risk Classification** / **By Request Classification**.

> **Gotcha:** a metric with **no data points in 2 weeks disappears** from the console and `list-metrics` — retrieve it with `get-metric-data` / `get-metric-statistics`.

## Log export

Finer-grained than CloudTrail; `SetLogDeliveryConfiguration` / `GetLogDeliveryConfiguration`. Two independent `EventSource` streams (combine both in one call):

| EventSource | Level | Contents | Plan | Destinations |
|---|---|---|---|---|
| **`userNotification`** | `ERROR` | **email/SMS delivery failures** (SES/SNS) | **any plan** | **CloudWatch Logs only** |
| **`userAuthEvents`** | `INFO` | threat-protection sign-in activity + risk | **Plus + threat protection on** | CloudWatch Logs, S3, or Firehose (one only) |

- **`userNotification` is the way to see why messages bounce/fail** and isn't plan-gated — a common blind spot ([messaging.md](messaging.md)). It only goes to CloudWatch Logs.
- `userAuthEvents` mirrors what `AdminListUserAuthEvents` returns ([threat-protection.md](threat-protection.md#event-history-feedback--log-export)); can't fan out to multiple destinations.
- Delivery is **best-effort**; the setup principal must be a pool admin with `cognito-idp:SetLogDeliveryConfiguration` + `logs:CreateLogDelivery` (and target-service perms). For a log group with a **resource policy > 5,120 chars**, use a `/aws/vendedlogs/...` log-group path.
- These don't replace CloudTrail or CloudWatch metrics — Lambda-trigger logs and CSV-import results live in their own separate log groups.
</content>
