# AWS Network Firewall & Firewall Manager — CLI Reference
For service concepts, see [network-firewall-fms-capabilities.md](network-firewall-fms-capabilities.md).

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
