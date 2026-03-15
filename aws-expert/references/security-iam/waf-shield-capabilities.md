# AWS WAF & Shield — Capabilities Reference
For CLI commands, see [waf-shield-cli.md](waf-shield-cli.md).

## AWS WAF

**Purpose**: Web Application Firewall protecting web apps and APIs against Layer 7 attacks.

### Key Concepts

| Concept | Description |
|---|---|
| **Web ACL** | The top-level WAF resource; attached to ALB, CloudFront, API Gateway, Cognito, AppSync, App Runner |
| **Rule** | Inspects requests using conditions; has an action (Allow, Block, Count, CAPTCHA, Challenge) |
| **Rule group** | Reusable collection of rules; can be AWS Managed, third-party, or custom |
| **IP set** | List of IP/CIDR ranges for use in rules |
| **Regex pattern set** | Regular expressions for matching request content |
| **Scope** | REGIONAL (ALB, API Gateway, etc.) or CLOUDFRONT (must be in us-east-1) |

### AWS Managed Rule Groups

| Group | Protects Against |
|---|---|
| `AWSManagedRulesCommonRuleSet` | OWASP Top 10, common exploits |
| `AWSManagedRulesKnownBadInputsRuleSet` | Log4j, Spring4Shell, known exploit payloads |
| `AWSManagedRulesSQLiRuleSet` | SQL injection |
| `AWSManagedRulesLinuxRuleSet` | Linux-specific attacks |
| `AWSManagedRulesAmazonIpReputationList` | Amazon-tracked malicious IPs |
| `AWSManagedRulesBotControlRuleSet` | Bot detection (common bots; intelligent threat mitigation) |
| `AWSManagedRulesATPRuleSet` | Account takeover protection (credential stuffing) |
| `AWSManagedRulesACFPRuleSet` | Account creation fraud prevention |

### Rule Actions

| Action | Description |
|---|---|
| **Allow** | Permit the request; skip remaining rules |
| **Block** | Return 403 to the client |
| **Count** | Log the match but do not block; useful for testing rules |
| **CAPTCHA** | Serve a CAPTCHA puzzle; block if failed |
| **Challenge** | Serve a silent browser challenge (JavaScript check); block if failed |

### Key Features

- **Rate-based rules**: Block IPs exceeding a request rate threshold
- **Geo-match**: Allow or block by country
- **Label matching**: Rules can add labels; subsequent rules can match labels (chained logic)
- **Managed rule group versions**: Pin to a specific version or opt into auto-update
- **Request sampling**: Inspect 100 recent matched requests per rule in console/API
- **Logging**: Full request/response logging to Kinesis Firehose, S3, or CloudWatch Logs

---

## AWS Shield

**Purpose**: DDoS protection for AWS resources.

### Tiers

| Tier | Cost | What it includes |
|---|---|---|
| **Standard** | Free, automatic | Always-on L3/L4 protection for all AWS customers |
| **Advanced** | $3,000/month + data transfer | Enhanced detection, attack diagnostics, DRT access, cost protection, L7 auto-mitigation |

### Shield Advanced Key Features

| Feature | Description |
|---|---|
| **DDoS Response Team (DRT)** | 24/7 AWS security experts; grant them access via IAM role + Flow Logs |
| **Attack diagnostics** | Real-time attack visibility and post-attack reports |
| **Proactive engagement** | DRT contacts you proactively when health checks fail during an attack |
| **Cost protection** | AWS credits for scaling costs incurred during DDoS events |
| **Health-check based detection** | Tie Route 53 health checks to protections for faster detection |
| **Automatic L7 mitigation** | Automatically creates WAF rules during CloudFront/ALB attacks (requires WAF) |
| **Protection groups** | Logically group resources (e.g., all ALBs) for aggregate protection view |

### Protected Resource Types (Advanced)

EC2 Elastic IPs, ELB (ALB/NLB/CLB), CloudFront, Route 53, AWS Global Accelerator
