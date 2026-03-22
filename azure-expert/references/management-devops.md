# Management & DevOps Domain Index

This domain covers Azure's platform management, observability, infrastructure-as-code, CI/CD, and governance portfolio. Load the relevant namespace files based on the user's specific workload.

## Namespace Index

| Namespace | Capabilities | CLI | Load when... |
|-----------|-------------|-----|--------------|
| Azure Monitor | management-devops/monitor-capabilities.md | management-devops/monitor-cli.md | Metrics, Logs (Log Analytics), Application Insights, Alerts (metric/log/activity log), Dashboards, Workbooks, Autoscale, Azure Monitor Agent |
| Bicep & ARM | management-devops/bicep-arm-capabilities.md | management-devops/bicep-arm-cli.md | Bicep language, ARM Templates, Template Specs, Deployment Stacks, Azure Verified Modules, What-If, deployment modes |
| Azure DevOps & GitHub | management-devops/devops-pipelines-capabilities.md | management-devops/devops-pipelines-cli.md | Azure Pipelines (YAML), Azure Repos, Azure Boards, Azure Artifacts, GitHub Actions with Azure, deployment environments |
| Azure Advisor & Policy | management-devops/advisor-governance-capabilities.md | management-devops/advisor-governance-cli.md | Azure Advisor recommendations (reliability, security, performance, cost, operational excellence), Service Health, Resource Health, Activity Log |

## Domain Overview

The Azure management and DevOps portfolio enables:

- **Observability**: Azure Monitor (metrics, logs, traces, alerting) + Application Insights (APM).
- **Infrastructure as Code**: Bicep (Azure-native DSL) and ARM Templates for declarative resource management.
- **CI/CD**: Azure Pipelines (YAML-based) and GitHub Actions with Azure for deployment automation.
- **Governance**: Azure Advisor (recommendations), Policy (guardrails), and Service Health (platform status).

## Key Decision Points

| Scenario | Recommended Service |
|----------|-------------------|
| Monitor application performance and traces | Application Insights |
| Query logs with KQL | Log Analytics (Azure Monitor Logs) |
| Infrastructure metrics and alerting | Azure Monitor Metrics + Alerts |
| Deploy Azure resources via IaC | Bicep (Azure-native, preferred) |
| CI/CD for Azure workloads | Azure Pipelines (YAML) or GitHub Actions |
| Cost optimization recommendations | Azure Advisor (Cost pillar) |
| Security recommendations | Azure Advisor + Defender for Cloud |
| Track Azure platform incidents | Azure Service Health |
| Audit subscription changes | Activity Log |
