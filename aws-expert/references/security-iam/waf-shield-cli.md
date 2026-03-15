# AWS WAF & Shield — CLI Reference
For service concepts, see [waf-shield-capabilities.md](waf-shield-capabilities.md).

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
