# AWS Elastic Beanstalk — Capabilities Reference

For CLI commands, see [elastic-beanstalk-cli.md](elastic-beanstalk-cli.md).

## AWS Elastic Beanstalk

**Purpose**: PaaS service that deploys and manages web applications and worker services on EC2 infrastructure; handles provisioning, load balancing, auto scaling, and monitoring automatically.

### Core Concepts

| Concept | Description |
|---|---|
| **Application** | Logical container for environments and application versions |
| **Application version** | A specific deployable artifact (zip, WAR, Docker image) stored in S3 |
| **Environment** | Running deployment of an application version; owns its own AWS resources (EC2, ELB, ASG) |
| **Environment tier** | Web Server (HTTP traffic) or Worker (SQS queue processing) |
| **Platform** | The runtime stack; e.g., "Python 3.11 on Amazon Linux 2023"; managed by AWS with regular updates |
| **Configuration template** | Saved environment configuration that can be applied to new or existing environments |
| `.ebextensions/` | Directory in your app bundle with `.config` YAML/JSON files to customize AWS resources and OS |
| `Buildfile` / `Procfile` | Control build commands and process types within the environment |

### Supported Platforms

Go, Java SE, Java with Tomcat, .NET on Windows Server, .NET Core on Linux, Node.js, PHP, Python, Ruby, Docker (single-container and multi-container), Preconfigured Docker

### Environment Tiers

| Tier | Description |
|---|---|
| **Web Server** | Runs behind an Elastic Load Balancer; handles HTTP/HTTPS traffic |
| **Worker** | Runs without a load balancer; SQS daemon forwards messages to a local HTTP endpoint; for background jobs |

### Deployment Policies

| Policy | Description | Downtime | Extra Capacity |
|---|---|---|---|
| **All at once** | Deploy to all instances simultaneously | Yes (briefly) | No |
| **Rolling** | Deploy in batches; batch out of service during update | No (degraded) | No |
| **Rolling with additional batch** | Launch extra instances for the batch; maintain full capacity | No | Temporary |
| **Immutable** | Launch entirely new ASG; swap on success | No | Full duplication |
| **Traffic splitting** | Canary deployment; send percentage of traffic to new version | No | Yes |

### Key Features

- **Managed platform updates**: Elastic Beanstalk applies platform patch updates automatically during maintenance windows
- **Environment cloning**: Duplicate an environment for testing or blue/green deployments
- **Blue/green via CNAME swap**: `swap-environment-cnames` to do zero-downtime blue/green deployment
- **EB CLI**: Specialized CLI (`eb`) for creating, deploying, and managing applications locally
- **Monitoring**: Health dashboard, CloudWatch integration, enhanced health reporting with per-instance metrics
- **No additional charge**: Pay only for underlying resources (EC2, ELB, RDS, etc.)
