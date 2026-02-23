# Deploying the Datadog Agent

Reference for installing, configuring, and managing the Datadog Agent.

## Table of Contents
- [Installing the Agent](#installing-the-agent)
- [Agent Components](#agent-components)
- [Agent as a Container](#agent-as-a-container)
- [Deployment Use Cases](#deployment-use-cases)
- [Advanced Configuration](#advanced-configuration)
- [Best Practices](#best-practices)

## Installing the Agent

### One-Line Install (Linux)
```bash
DD_API_KEY=<YOUR_API_KEY> DD_SITE="datadoghq.com" bash -c "$(curl -L https://s3.amazonaws.com/dd-agent/scripts/install_script_agent7.sh)"
```

### macOS (Homebrew)
```bash
DD_API_KEY=<YOUR_API_KEY> DD_SITE="datadoghq.com" brew install datadog-agent
```

### Windows (PowerShell)
```powershell
. { iwr -useb https://s3.amazonaws.com/dd-agent/scripts/install_script_agent7.ps1 } | iex; install -apiKey <YOUR_API_KEY> -site "datadoghq.com"
```

### Configuration File
Main config: `/etc/datadog-agent/datadog.yaml`

Key settings:
```yaml
api_key: <YOUR_API_KEY>
site: datadoghq.com
hostname: <custom-hostname>  # optional override
tags:
  - env:production
  - service:web
  - team:backend
logs_enabled: true
apm_config:
  enabled: true
process_config:
  process_collection:
    enabled: true
```

## Agent Components

| Component | Purpose | Port |
|-----------|---------|------|
| **Collector** | Gathers system metrics and integration checks | — |
| **DogStatsD** | Receives custom metrics via UDP | 8125 |
| **APM Agent** | Receives traces from instrumented apps | 8126 |
| **Process Agent** | Collects live process and container data | — |
| **Security Agent** | Runtime security monitoring | — |
| **System Probe** | Network performance monitoring (kernel-level) | — |

### Agent CLI Commands
```bash
# Status and diagnostics
sudo datadog-agent status
sudo datadog-agent health
sudo datadog-agent diagnose

# Service management
sudo systemctl start datadog-agent
sudo systemctl stop datadog-agent
sudo systemctl restart datadog-agent

# Check configuration
sudo datadog-agent configcheck

# Run a specific check
sudo datadog-agent check <integration_name>
```

## Agent as a Container

### Docker
```bash
docker run -d --name datadog-agent \
  -e DD_API_KEY=<YOUR_API_KEY> \
  -e DD_SITE="datadoghq.com" \
  -e DD_LOGS_ENABLED=true \
  -e DD_APM_ENABLED=true \
  -v /var/run/docker.sock:/var/run/docker.sock:ro \
  -v /proc/:/host/proc/:ro \
  -v /sys/fs/cgroup/:/host/sys/fs/cgroup:ro \
  gcr.io/datadoghq/agent:7
```

### Kubernetes (Helm)
```bash
helm repo add datadog https://helm.datadoghq.com
helm install datadog-agent datadog/datadog \
  --set datadog.apiKey=<YOUR_API_KEY> \
  --set datadog.site="datadoghq.com" \
  --set datadog.logs.enabled=true \
  --set datadog.apm.portEnabled=true
```

### Kubernetes (Datadog Operator)
```yaml
apiVersion: datadoghq.com/v2alpha1
kind: DatadogAgent
metadata:
  name: datadog
spec:
  global:
    credentials:
      apiKey: <YOUR_API_KEY>
    site: datadoghq.com
  features:
    apm:
      enabled: true
    logCollection:
      enabled: true
```

## Deployment Use Cases

### Single Host
- Install agent directly on the host
- Configure integrations in `/etc/datadog-agent/conf.d/`

### Multi-Host Fleet
- Use configuration management (Ansible, Chef, Puppet, Terraform)
- Datadog Fleet Automation for centralized config
- Use tags for organizing hosts by env/service/team

### Containerized Environment
- Run agent as a DaemonSet (Kubernetes) or sidecar
- Mount Docker socket for container autodiscovery
- Use Autodiscovery labels/annotations for integration config

## Advanced Configuration

### Proxy
```yaml
proxy:
  http: http://proxy.example.com:3128
  https: http://proxy.example.com:3128
  no_proxy:
    - 169.254.169.254  # AWS metadata
```

### Custom Check Intervals
```yaml
# In conf.d/<integration>.d/conf.yaml
init_config:
instances:
  - min_collection_interval: 30  # seconds
```

### Autodiscovery (Container Environments)
```yaml
# Pod annotation for auto-configuring an integration
ad.datadoghq.com/<container_name>.check_names: '["<integration>"]'
ad.datadoghq.com/<container_name>.init_configs: '[{}]'
ad.datadoghq.com/<container_name>.instances: '[{"host":"%%host%%","port":"%%port%%"}]'
```

## Best Practices

- **Tag everything** — Apply `env`, `service`, `version` tags at the agent level
- **Update regularly** — Keep agent within 1-2 minor versions of latest; update monthly at minimum
- **Limit custom metrics** — Each custom metric has cost implications; use tags instead of separate metric names
- **Use Fleet Automation** — Manage agent configs centrally for large deployments
- **Monitor the agent** — Set up alerts for agent connectivity and health
- **Secure the agent** — Restrict access to config files, use secrets management for API keys
- **Resource limits** — In containers, set CPU/memory limits for the agent (typically 256Mi-512Mi memory, 200m-400m CPU)
