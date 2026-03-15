# AWS Network Firewall & Firewall Manager — Capabilities Reference
For CLI commands, see [network-firewall-fms-cli.md](network-firewall-fms-cli.md).

## AWS Network Firewall

**Purpose**: Managed, stateful network firewall and intrusion prevention system (IPS) for VPCs.

### Key Concepts

| Concept | Description |
|---|---|
| **Firewall** | Deployed into a VPC; requires dedicated subnet per AZ |
| **Firewall policy** | Associates stateless and stateful rule groups; sets default actions |
| **Stateless rule group** | Processes packets individually; actions: pass, drop, forward to stateful engine |
| **Stateful rule group** | Inspects traffic flows; supports Suricata-compatible rules, domain lists, standard rules |
| **Rule group** | Can be shared across firewalls via resource policy |

### Stateful Rule Types

| Type | Use case |
|---|---|
| **Suricata-compatible rules** | Full IDS/IPS signatures; supports `alert`, `drop`, `pass` |
| **Domain list rules** | Allow/deny list of FQDNs; inspect HTTP Host and TLS SNI headers |
| **Standard 5-tuple rules** | Source/dest IP, port, protocol with optional keyword matching |

### Traffic Flow Pattern

```
Internet → IGW → Firewall endpoint (in firewall subnet) → Application subnet
(Route tables must route traffic through the firewall endpoint)
```

### Key Features

- **TLS inspection**: Decrypt and inspect TLS traffic (requires Certificate Manager private CA)
- **Centralized deployment**: Single firewall for multiple VPCs via Transit Gateway
- **Logging**: Alert and flow logs to S3, CloudWatch Logs, or Kinesis Firehose
- **Traffic analysis reports**: Identify top traffic patterns for rule creation

---

## AWS Firewall Manager

**Purpose**: Centrally configure and enforce AWS WAF, Shield Advanced, Network Firewall, and security group policies across accounts in AWS Organizations.

### Policy Types

| Policy Type | What it manages |
|---|---|
| **AWS WAF** | Deploy Web ACLs to ALBs, CloudFront, API Gateway across accounts |
| **Shield Advanced** | Auto-protect resource types across accounts |
| **Security group** | Enforce security group usage or audit non-compliant groups |
| **Network Firewall** | Deploy Network Firewalls to VPCs across accounts |
| **Route 53 DNS Firewall** | Deploy DNS Firewall rule groups across VPCs/accounts |
| **Palo Alto / third-party** | Deploy third-party NGFW via Marketplace |

### Key Requirements

- Must have **AWS Organizations** enabled
- **AWS Config** must be enabled in all member accounts (Firewall Manager uses Config to discover resources)
- Designate a **Firewall Manager administrator** account (separate from Org management account recommended)

### Key Features

- **Automatic remediation**: Automatically bring non-compliant resources into compliance
- **Compliance dashboard**: View policy compliance status per account
- **Resource sets**: Define a specific set of resources for a policy to target
- **Discovered resources**: Identify unprotected resources matching policy scope
- **Notification channel**: SNS alerts for compliance violations
