---
name: datadog-expert
description: >
  Datadog cloud monitoring expert covering agent deployment, dashboards, metrics, monitors/alerts,
  integrations (AWS/GCP/Azure, databases, web servers, queues), DogStatsD, JMX, SNMP, REST API,
  Docker/Kubernetes monitoring, log management, APM/tracing, synthetic tests, security monitoring,
  Terraform/Ansible automation, custom checks, RBAC/SSO, SLOs, and incident management.
  Use when the user asks any Datadog-related question: setup, configuration, alerting, dashboards,
  integrations, container monitoring, log collection, APM, scripting, or monitoring best practices.
---

# Datadog Expert

Comprehensive Datadog monitoring guidance organized by domain. Load only the reference file relevant to the user's question.

## Topic Routing

Determine the user's topic and read the corresponding reference file:

### Section 1: Getting Started
- **Monitoring fundamentals, terminology, types of monitoring, tool landscape** → Read [references/01-introduction-to-monitoring.md](references/01-introduction-to-monitoring.md)
- **Agent installation, configuration, components, containerized agent, fleet management** → Read [references/02-deploying-the-agent.md](references/02-deploying-the-agent.md)
- **Dashboards, widgets, Metrics Explorer, Host Map, screenboards/timeboards, notebooks, SLOs** → Read [references/03-dashboards.md](references/03-dashboards.md)
- **Users, roles, RBAC, organizations, SSO/SAML, API/app keys, usage tracking** → Read [references/04-account-management.md](references/04-account-management.md)

### Section 2: Core Monitoring
- **Metric types (count/gauge/histogram/distribution), metric naming, events, tags, tagging strategy, Unified Service Tagging** → Read [references/05-metrics-events-tags.md](references/05-metrics-events-tags.md)
- **Host metrics (CPU/memory/disk/network), Host Map, infrastructure integrations (Nginx, PostgreSQL, Redis, Kafka), SNMP, cloud integrations (AWS/GCP/Azure), database monitoring** → Read [references/06-monitoring-infrastructure.md](references/06-monitoring-infrastructure.md)
- **Monitor types, alert conditions, thresholds, anomaly/forecast/composite monitors, notification templates, downtimes, monitor management API, Terraform monitors** → Read [references/07-monitors-and-alerts.md](references/07-monitors-and-alerts.md)

### Section 3: Extending Datadog
- **Integration configuration (web servers, databases, caches, queues), cloud platform setup, integration types, Ansible/Terraform for integrations** → Read [references/08-integrating-platform-components.md](references/08-integrating-platform-components.md)
- **REST API authentication, endpoints, querying metrics, managing monitors/dashboards via API, client libraries (Python/Go/Ruby/Java), rate limits, scripting patterns, bulk operations** → Read [references/09-rest-api.md](references/09-rest-api.md)
- **DogStatsD protocol and clients (Python/Go/Ruby/Java/Node.js), JMX monitoring (Cassandra, Kafka), SNMP v2c/v3, Network Device Monitoring, client library overview** → Read [references/10-monitoring-standards.md](references/10-monitoring-standards.md)
- **Custom Agent checks, Integration Development Kit, webhooks, Terraform provider (monitors/dashboards/SLOs/synthetics), Ansible module** → Read [references/11-developing-integrations.md](references/11-developing-integrations.md)

### Section 4: Advanced Monitoring
- **Docker monitoring, Kubernetes (Helm/Operator), Autodiscovery (labels/annotations), container metrics, Cluster Agent, Orchestrator Explorer** → Read [references/12-monitoring-containers.md](references/12-monitoring-containers.md)
- **Log collection (file/Docker/K8s), log processing pipelines, Grok parsing, indexes, archives, log search syntax, log-based metrics, Logging Without Limits** → Read [references/13-managing-logs.md](references/13-managing-logs.md)
- **APM/tracing setup (Python/Java/Node.js), Synthetic Monitoring (API/browser tests), Security Monitoring/Cloud SIEM, RUM, CI Visibility, SLOs/error budgets, Incident Management** → Read [references/14-advanced-monitoring.md](references/14-advanced-monitoring.md)

## Usage

1. Identify which topic the user's question maps to
2. Read only the relevant reference file(s) — typically just one
3. If a question spans multiple topics (e.g., "set up APM with Kubernetes"), read both relevant files
4. Apply the reference material to answer the specific question with concrete examples
