# Security Monitoring
## Chapter 12: Security Event Monitoring, Anomaly Detection, Audit Trails

---

## Security Monitoring Is Operational Monitoring

Security monitoring uses the same tools and techniques as operational monitoring — metrics, logging, alerting, and dashboards — applied to a different question: not "is the system working?" but "is the system being abused or attacked?"

The overlap with operational monitoring is large:
- The same log pipeline that handles application errors also handles security events
- The same alerting infrastructure that pages for high latency also pages for failed login spikes
- The same dashboards framework serves both audiences

Treat security monitoring as a domain within your monitoring practice, not a separate silo.

---

## What to Monitor for Security

### Authentication Events

These are the highest-value security signals available to most applications:

| Event | Log Fields | Alert On |
|-------|-----------|---------|
| Successful login | user_id, IP, user_agent, timestamp | Unusual geography or time |
| Failed login | username/email, IP, timestamp, reason | High rate from one IP or for one account |
| Account lockout | user_id, IP, lockout_count | Any triggered lockout |
| Password reset | user_id, IP, requested_by | Bulk resets; resets for privileged accounts |
| MFA bypass or failure | user_id, method, success | Any MFA failure spike |
| Session creation | session_id, user_id, IP | Concurrent sessions from different countries |
| Privilege escalation | user_id, from_role, to_role | Any elevation of privilege |
| Admin login | user_id, IP | Always log; alert on unusual time/IP |

### Authorization Events

- Permission denied events — high rate may indicate probing or misconfigured access
- Access to sensitive resources — log and retain (compliance)
- Bulk data access — accessing far more records than normal for a user or API key

### API and Network Events

- Requests from unknown or unexpected user agents
- Rate anomalies (requests per second far above user's normal pattern)
- Requests to admin or internal endpoints from external IPs
- Unusual geographic patterns (user normally in US, request from unusual country)
- Scanning patterns (sequential requests to many different paths/endpoints)

### Data Events

- Bulk export or download requests
- Unusual data modifications (bulk deletes, large updates)
- Access to data outside normal access patterns

---

## Audit Logging

Audit logs are the permanent record of who did what to which data and when. They differ from operational logs in that:
- They must be retained longer (often 1–7 years)
- They must be tamper-evident (should not be modifiable by the application itself)
- They must capture business-meaningful events, not just HTTP requests

### What to Audit

| Category | Examples |
|----------|---------|
| **Data access** | Which user viewed which records |
| **Data modification** | Create, update, delete of sensitive records |
| **Configuration changes** | Permission changes, feature flag changes, system configuration |
| **Authentication** | All login/logout events |
| **Administrative actions** | User creation, account deactivation, role changes |
| **Export/download** | Any bulk data extraction |

### Audit Log Format

Every audit log entry should include:

```json
{
  "timestamp": "2024-01-15T14:23:01.234Z",
  "event_type": "user.data.accessed",
  "actor": {
    "user_id": "admin-456",
    "email": "admin@example.com",
    "ip": "203.0.113.45",
    "session_id": "sess-789"
  },
  "resource": {
    "type": "customer_record",
    "id": "cust-12345"
  },
  "outcome": "success",
  "details": {
    "fields_accessed": ["name", "email", "payment_method"]
  }
}
```

### Audit Log Storage

Audit logs should be:
- Written to a separate, append-only store (not the same pipeline as debug logs)
- Immutable — the application should not have write/delete access to its own audit logs
- Encrypted at rest
- Retained per compliance requirements (SOC 2, HIPAA, GDPR, PCI DSS each have different requirements)

---

## Anomaly Detection for Security

Security anomalies are behaviors that deviate from a user's or system's normal pattern. Static thresholds often miss them or produce false positives; behavioral baselines work better.

### Baseline-Based Detection

Establish normal patterns per user, per IP, per API key, and alert on significant deviation:

- **Login geography:** user normally logs in from New York; now logging in from Moscow → alert
- **Request volume:** API key normally sends 1,000 req/hour; now sending 50,000 → alert
- **Data access volume:** user normally views 5–10 records per session; now viewing 10,000 → alert
- **Time-of-day:** service account always active 2–6am UTC; now active at 2pm → investigate

### Velocity Checks

Alert when actions happen faster than humanly possible:
- 100 failed login attempts in 60 seconds from one IP → credential stuffing
- 1,000 API requests per minute from one user → automated attack
- 50 password reset requests in 10 minutes for different accounts → account takeover attempt

### Impossible Travel

If a user logs in from City A and City B within a time window where physical travel is impossible:
- Flag as suspicious
- Require re-authentication or MFA
- Alert security team

---

## SIEM Concepts

A SIEM (Security Information and Event Management) system aggregates security events from multiple sources, correlates them, and provides search and alerting capabilities.

You do not necessarily need a dedicated SIEM product. Your existing log aggregation stack (Elasticsearch, Splunk, etc.) can serve SIEM functions if properly configured.

### SIEM Functions

| Function | Description |
|----------|-------------|
| **Collection** | Aggregate logs from all systems |
| **Normalization** | Convert different log formats to a common schema |
| **Correlation** | Link related events across systems |
| **Alerting** | Notify on patterns indicative of attacks |
| **Retention** | Long-term storage for forensics and compliance |
| **Search** | Rapid investigation during incident response |

### When to Adopt a Dedicated SIEM

Consider a dedicated SIEM product when:
- Compliance requires it (PCI DSS Level 1, SOC 2 Type II, FedRAMP)
- Your team has dedicated security analysts who need its advanced correlation features
- You have more than ~20 distinct log sources with different formats

For smaller organizations, extending the existing observability stack is usually sufficient.

---

## Incident Response for Security Events

Security incidents require the same incident response framework as operational incidents, with additional steps:

1. **Detect** — monitoring alerts fire, or threat intel matches
2. **Contain** — limit the blast radius (block IP, revoke token, isolate system)
3. **Eradicate** — remove the attacker's access or malicious artifact
4. **Recover** — restore systems to normal operation
5. **Post-incident analysis** — blameless review; update detections and runbooks

### Containment Actions to Pre-Authorize

Document and pre-approve containment steps so on-call responders can act quickly:
- Block an IP range at the WAF/load balancer
- Revoke a user's session tokens
- Disable an API key
- Isolate a host from network (if compromised)
- Enable emergency rate limiting

Responders should not need to get approval for these during an active incident; the approval is in the runbook.

---

## Security Monitoring Checklist

- [ ] All authentication events (success and failure) logged and retained
- [ ] Failed login rate alerting configured (per-IP and per-account)
- [ ] Audit logs stored in immutable, separate store
- [ ] Privileged action alerting (admin logins, permission changes)
- [ ] Velocity checks on authentication and API endpoints
- [ ] Geographic anomaly detection for user sessions
- [ ] Bulk data access alerting
- [ ] Audit log retention meets compliance requirements
- [ ] Security runbooks for common scenarios (credential stuffing, data exfiltration attempt)
- [ ] Containment actions pre-approved and documented
