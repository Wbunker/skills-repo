# Azure App Service — Capabilities Reference

For CLI commands, see [app-service-cli.md](app-service-cli.md).

## Azure App Service

**Purpose**: Fully managed PaaS platform for hosting web applications, REST APIs, and mobile backends. Supports .NET, Node.js, Python, Java, PHP, Ruby, and containerized apps. Abstracts OS patching, load balancing, and auto-scaling.

---

## App Service Plans

An App Service Plan defines the region, OS, pricing tier, and compute resources shared by all apps in the plan.

| Tier | Category | vCPUs | RAM | Scale Out | Key Features |
|---|---|---|---|---|---|
| **Free (F1)** | Shared | Shared | 1 GB | 1 instance | Dev/test; no custom domain; no SLA |
| **Shared (D1)** | Shared | Shared | 1 GB | 1 instance | Custom domain; no SLA |
| **Basic (B1/B2/B3)** | Dedicated | 1/2/4 | 1.75/3.5/7 GB | Up to 3 | Custom domain, SSL, manual scale |
| **Standard (S1/S2/S3)** | Dedicated | 1/2/4 | 1.75/3.5/7 GB | Up to 10 | Auto-scale, deployment slots (5), VNet integration, daily backup |
| **Premium v3 (P0v3–P3mv3)** | Dedicated | 1/2/4/8 | 4/8/16/32 GB | Up to 30 | All Standard features + higher RAM, faster CPU, zone redundancy |
| **Isolated v2 (I1v2–I6v2)** | App Service Environment | 2–32 | 8–128 GB | Up to 200 | Dedicated VNet injection, private endpoints, highest scale and isolation |

### OS Options

- **Windows**: Full .NET Framework support, WebJobs, TLS mutual auth
- **Linux**: Containers, Python, Ruby, Node.js; slightly different extension support

### Zone Redundancy

- Premium v3 and Isolated v2 support zone-redundant App Service Plans
- Requires minimum 3 instances; Azure automatically spreads across zones
- Guarantees 99.99% SLA

---

## Web Apps and API Apps

Web Apps and API Apps are functionally identical; the App type label is cosmetic.

### Runtime Stacks (Linux)

| Stack | Supported Versions |
|---|---|
| .NET | 6, 7, 8 (LTS) |
| Node.js | 18, 20 LTS |
| Python | 3.8, 3.9, 3.10, 3.11, 3.12 |
| Java | 8, 11, 17, 21 (Tomcat, JBoss EAP, Java SE) |
| PHP | 8.0, 8.1, 8.2, 8.3 |
| Ruby | 2.7 (Linux only) |
| Custom container | Any image from ACR or Docker Hub |

### Key Configuration

| Setting | Description |
|---|---|
| **Always On** | Prevents app from idling after 20 minutes of inactivity; required for WebJobs with continuous triggers; available Basic tier and above |
| **Application Settings** | Injected as environment variables; stored encrypted; can reference Key Vault secrets with `@Microsoft.KeyVault(...)` syntax |
| **Connection Strings** | Injected as connection strings; Key Vault reference supported |
| **CORS** | Configure allowed origins at the app level; also configurable in API Management |
| **Managed Identity** | System or user-assigned; allows passwordless access to Key Vault, Storage, SQL, and other Azure services |
| **HTTP/2** | Enabled by default; reduces connection overhead for modern clients |
| **WebSockets** | Supported on Basic and above; required for SignalR and real-time apps |
| **IP Restrictions** | Inbound access rules by IP/CIDR or Service Tag; also supports Private Endpoints for fully private deployments |

---

## Deployment Slots

Deployment slots are separate live environments within the same App Service Plan that allow safe testing and zero-downtime releases.

| Feature | Details |
|---|---|
| **Slot count** | Standard: 5 slots; Premium: 20 slots; Isolated: 20 slots |
| **Slot swap** | Atomically swaps routing between two slots (e.g., staging → production); warms up the slot before swapping |
| **Swap preview** | Validates slot swap in production before committing; supports cancel |
| **Traffic splitting** | Route a percentage of traffic to a non-production slot (A/B testing, canary deployments) |
| **Sticky settings** | App settings and connection strings marked "slot sticky" do not swap; use for slot-specific config (database endpoints, feature flags) |
| **Auto-swap** | Automatically swap to production after a successful deployment to staging; common in CI/CD pipelines |
| **Slot-specific URL** | `https://<app-name>-<slot-name>.azurewebsites.net`; each slot has its own hostname |

---

## Scaling

### Manual Scaling
- Change the instance count directly in the portal or via CLI
- Available on Basic and above

### Auto-scaling (Standard and above)
- **Metric-based**: Scale on CPU %, memory %, request count, HTTP queue length
- **Schedule-based**: Pre-scale for known traffic patterns (business hours, batch windows)
- **Scale out**: Add instances up to plan maximum
- **Scale in**: Remove instances based on cool-down periods (default 5 minutes)
- **Predictive autoscale**: Uses historical data to scale proactively before load arrives (Premium v2+)

### Premium v3 Auto-scale Limits

| SKU | Max Instances |
|---|---|
| P0v3 | 10 |
| P1v3 | 30 |
| P2v3 | 30 |
| P3v3 | 30 |
| P1mv3–P3mv3 | 30 |

---

## Deployment Methods

| Method | Description | Use Case |
|---|---|---|
| **ZIP Deploy** | Upload a ZIP archive via API (`POST /api/zipdeploy`) | CI/CD pipelines, scripted deployments |
| **Git Deploy (Kudu)** | Push to a Git remote managed by App Service | Simple projects, small teams |
| **GitHub Actions** | Native integration with workflow actions for build + deploy | Preferred for GitHub-based projects |
| **Azure DevOps Pipelines** | Azure Pipelines task `AzureWebApp@1` for CI/CD | Enterprise CI/CD |
| **Container (Docker/ACR)** | Point app to a container image; auto-pull on restart | Containerized apps, custom runtimes |
| **FTP/FTPS** | Legacy file upload; not recommended for production | Legacy only |
| **VS Code / Visual Studio** | Publish directly from IDE | Developer convenience; not for production automation |
| **az webapp deploy** | CLI-based artifact deployment | Scripted deployment from CI/CD |

---

## Networking

### Inbound Connectivity

| Feature | Description |
|---|---|
| **Public Endpoint** | Default HTTPS endpoint `<app>.azurewebsites.net`; can restrict with IP restrictions |
| **Private Endpoint** | Expose app on a private IP in your VNet; fully private; disables public endpoint if configured |
| **App Service Environment (ASE)** | Inject the entire App Service into your own VNet (Isolated tier) |
| **Access restrictions** | IP/CIDR or Service Tag rules; priority-based; also supports Azure Front Door service tag |

### Outbound Connectivity

| Feature | Description |
|---|---|
| **Regional VNet Integration** | App can make outbound calls to resources in a VNet (Standard+ tiers); required for private PaaS access |
| **Gateway-required VNet Integration** | Connect to VNets in other regions or classic VNets via VPN Gateway (legacy) |
| **NAT Gateway** | Assign a static outbound IP for VNet-integrated apps |
| **Hybrid Connections** | Connect to on-premises or other network endpoints without VNet peering (Basic+) |

---

## App Service Environment (ASE)

ASE v3 is a fully private deployment of App Service within a customer-managed VNet:

- **Internal (ILB)**: App accessible only via private IP in your VNet; no internet exposure
- **External**: App accessible via public IP but compute is in your VNet
- **Zone Redundant**: ASE v3 supports zone redundancy (3 front-end instances across zones)
- **No inbound NSG required**: ASE manages its own network; only outbound NSG rules needed
- **Dedicated pricing**: Isolated v2 SKU; no charge per-app beyond plan cost (all apps in plan are free once plan is paid)

---

## WebJobs

WebJobs run background tasks in the context of a Web App:

| Type | Description |
|---|---|
| **Continuous** | Starts immediately; runs in a continuous loop; requires Always On |
| **Triggered** | Runs on-demand or on a CRON schedule |
| **Supported runtimes** | .exe, .bat, .cmd, .ps1, .sh, .php, .py, .js, .jar |

---

## Health Checks

- Configure a health check path (e.g., `/health`) on Standard and above
- App Service monitors the path every 1–2 minutes
- Unhealthy instances (after threshold failures) are removed from the load balancer and eventually restarted
- Unhealthy instances are not removed until a replacement is healthy
- Pairs with Azure Monitor to alert on health check failures

---

## Authentication (EasyAuth)

App Service authentication (formerly called EasyAuth) provides built-in OAuth/OIDC integration:

| Identity Provider | Protocol |
|---|---|
| Microsoft Entra ID | OpenID Connect (OIDC) |
| Microsoft Account (personal) | OAuth 2.0 |
| Google | OAuth 2.0 |
| Facebook | OAuth 2.0 |
| GitHub | OAuth 2.0 |
| Any OpenID Connect provider | OIDC |

- Authentication happens at the platform layer before request reaches app code
- Unauthenticated requests: return 401/403 or redirect to login (configurable)
- Token store: Access and refresh tokens stored in `.auth/me` endpoint
- Requires no SDK changes to protect an entire app; use `ClaimsPrincipal` in code for claims

---

## Custom Domains and TLS

- Map custom domains via CNAME or A record
- Free App Service Managed Certificate for custom domains (Standard and above, single domain; no SAN/wildcard)
- Import PFX certificates for wildcard or extended validation certs
- Minimum TLS version configurable (1.2 recommended); TLS 1.3 supported
- HTTPS-only mode enforces HTTPS redirect at platform level
