# Introduction to Monitoring

Reference for Datadog monitoring fundamentals, terminology, and use cases.

## Table of Contents
- [Why Monitoring](#why-monitoring)
- [Proactive Monitoring](#proactive-monitoring)
- [Monitoring Use Cases](#monitoring-use-cases)
- [Monitoring Terminology](#monitoring-terminology)
- [Types of Monitoring](#types-of-monitoring)
- [Monitoring Tools Landscape](#monitoring-tools-landscape)

## Why Monitoring

Monitoring ensures systems are healthy, performant, and available. Without monitoring, teams operate blind — reacting to outages instead of preventing them.

**Key motivations:**
- Detect failures before users do
- Understand system behavior under load
- Meet SLA/SLO commitments
- Capacity planning and cost optimization
- Root cause analysis during incidents

## Proactive Monitoring

Three pillars of proactive monitoring:

### 1. Comprehensive Monitoring Solution
- Cover all layers: infrastructure, platform, application, business
- Correlate metrics across layers to find root causes
- Use a single pane of glass (Datadog) to unify visibility

### 2. Alerting for Impending Issues
- Set thresholds that warn before failure, not after
- Use anomaly detection for metrics without obvious static thresholds
- Alert on trends (e.g., disk filling up) not just current state

### 3. Feedback Loop
- Post-incident reviews feed back into monitoring improvements
- Continuously refine alerts to reduce noise and catch real issues
- Runbooks linked to alerts for fast remediation

## Monitoring Use Cases

### All in a Data Center
- Traditional on-premises infrastructure
- Monitor physical hosts, VMs, network devices
- Datadog Agent installed on each host

### Hybrid (App in DC + Cloud Monitoring)
- Applications remain on-prem, monitoring is SaaS
- Agent sends data to Datadog cloud
- Reduces monitoring infrastructure overhead

### All in the Cloud
- Full cloud-native stack (AWS, GCP, Azure)
- Cloud integrations pull metrics directly from provider APIs
- Combine agent-based and agentless monitoring

## Monitoring Terminology

| Term | Definition |
|------|-----------|
| **Host** | A physical or virtual machine being monitored |
| **Agent** | Software installed on a host to collect and send metrics |
| **Metric** | A numerical measurement sampled over time (e.g., CPU usage) |
| **Check** | A periodic evaluation of a metric or service state |
| **Threshold** | A boundary value that triggers a state change |
| **Monitor** | A Datadog construct that evaluates metrics against conditions |
| **Alert** | A notification triggered when a monitor enters a warning/critical state |
| **Severity Level** | Priority classification (P1-P5) for incidents |
| **Downtime** | Scheduled suppression of alerts during maintenance |
| **Event** | A discrete occurrence in the system (deploy, error, config change) |
| **Incident** | An active issue requiring investigation and response |
| **On Call** | The person or team responsible for responding to alerts |
| **Runbook** | Step-by-step remediation instructions linked to a monitor |

## Types of Monitoring

### Infrastructure Monitoring
- CPU, memory, disk, network on hosts
- VM and bare-metal health
- Datadog: Host Map, Infrastructure List

### Platform Monitoring
- Databases (RDS, PostgreSQL, MySQL, Redis)
- Message queues (Kafka, RabbitMQ)
- Web servers (Nginx, Apache)
- Datadog: 750+ integrations

### Application Monitoring
- Request latency, error rates, throughput
- Traces across microservices
- Datadog: APM, distributed tracing

### Business Monitoring
- Conversion rates, revenue, user signups
- Custom metrics from application code
- Datadog: custom metrics via DogStatsD or API

### Last-Mile Monitoring (Synthetics)
- Simulate user interactions from global locations
- API tests, browser tests, multi-step tests
- Datadog: Synthetic Monitoring

### Log Aggregation
- Centralized log collection, indexing, search
- Correlate logs with metrics and traces
- Datadog: Log Management

### Meta-Monitoring
- Monitor the monitoring system itself
- Ensure agents are running, data is flowing
- Datadog: Agent health checks, fleet automation

## Monitoring Tools Landscape

### On-Premises Tools
- Nagios, Zabbix, Prometheus + Grafana, Icinga
- Full control but high operational overhead

### SaaS Solutions
- Datadog, New Relic, Splunk, Dynatrace
- Lower operational overhead, faster time to value
- Datadog differentiator: unified platform (metrics + traces + logs + synthetics + security)

### Cloud-Native Tools
- AWS CloudWatch, GCP Cloud Monitoring, Azure Monitor
- Deep integration with their own cloud but limited cross-cloud visibility
- Often used alongside Datadog for vendor-specific metrics
