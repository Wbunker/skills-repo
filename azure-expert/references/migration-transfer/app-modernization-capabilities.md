# App Modernization — Capabilities Reference
For CLI commands, see [app-modernization-cli.md](app-modernization-cli.md).

## App Service Migration Assistant

**Purpose**: Automated tool for assessing and migrating IIS-hosted web applications from Windows servers to Azure App Service. Reduces migration effort from weeks to hours for compatible apps.

### Assessment Process

1. Run **App Service Migration Assessment** from Azure Migrate portal OR standalone executable on Windows server
2. Tool scans all IIS sites on the server
3. Produces compatibility report per site: **Ready**, **Ready with conditions**, **Not ready**

### Compatibility Checks

| Check | Impact |
|---|---|
| .NET Framework version | Must be supported by App Service (2.x, 3.5, 4.x) |
| IIS authentication | Supported: Anonymous, Windows (with caveats), Basic, Digest |
| HTTP modules / ISAPI filters | Custom modules may not be supported |
| Application pool identity | Must use `ApplicationPoolIdentity` or `NetworkService` |
| WCF services | Supported for some configurations |
| SSL/TLS certificates | Migrate to App Service Managed Certificates or Key Vault-backed certs |
| Custom error pages | Migrated as static files |
| Web.config transforms | Handled via App Service Application Settings |

### Migration Steps (via Migration Assistant GUI)

1. Select site from discovery results
2. Review pre-migration checklist (firewall, connection strings, secrets)
3. Choose App Service plan tier and region
4. Authenticate to Azure
5. Tool creates App Service plan, web app, and deploys app via zip deploy
6. Test migrated app; update DNS to point to App Service URL
7. Configure custom domain and TLS certificate

---

## Azure Migrate Containerization Tool

**Purpose**: Assess and containerize Java and ASP.NET web applications for deployment to AKS or Azure App Service for Containers. No Dockerfile experience required.

### Supported Sources

| Application Type | Containerization Target |
|---|---|
| ASP.NET apps on IIS (Windows) | Azure App Service for Windows Containers |
| Java apps on Tomcat (Linux) | AKS or Azure App Service for Linux |

### Process

1. **Discover**: Run discovery on source Windows/Linux server to find running web applications
2. **Build container image**: Tool analyzes app, generates Dockerfile, builds image
3. **Push to ACR**: Image pushed to Azure Container Registry
4. **Deploy**: Deploy to AKS (with Helm chart) or App Service (container deployment)

### Key Capabilities

- Auto-generates Dockerfile based on application dependencies
- Maps application configuration (web.config/application.properties) to environment variables
- Parameterizes connection strings and secrets for Kubernetes Secrets or Key Vault integration
- Creates Kubernetes deployment manifest and service YAML
- Supports both new and existing AKS clusters and ACR registries

---

## Spring Apps Migration (Azure Spring Apps)

**Purpose**: Migrate Spring Boot and Spring Cloud microservices from on-premises or VMs to Azure Spring Apps (fully managed Spring runtime).

### Migration Paths

| Source | Target |
|---|---|
| Self-hosted Spring Boot on VM | Azure Spring Apps (Standard or Enterprise tier) |
| Spring Cloud on Kubernetes | Azure Spring Apps Enterprise (with Tanzu components) |
| Spring Boot on App Service | Azure Spring Apps (simpler management) |

### Azure Spring Apps Tiers

| Tier | Features | Use Case |
|---|---|---|
| **Basic** | 25 app instances max; dev/test pricing | Development and testing |
| **Standard** | Up to 500 apps; VNet injection; zone redundancy | Production workloads |
| **Enterprise** | VMware Tanzu components (Spring Cloud Gateway, API Portal, Spring Cloud Config Server replacement) | Enterprise Spring apps |

### Migration Steps

1. **Assess**: Verify Spring Boot version compatibility (2.x, 3.x supported)
2. **Externalize config**: Replace `application.properties` with Spring Cloud Config Server or Azure App Configuration
3. **Service discovery**: Replace Eureka with Azure Spring Apps built-in service registry
4. **Create Azure Spring Apps instance**: Select tier, region, VNet
5. **Deploy applications**: `az spring app deploy` with JAR artifact
6. **Bind services**: Azure Cache for Redis, Azure Database, Azure Service Bus bindings
7. **Configure scaling**: Set CPU/memory per app; configure autoscale rules

---

## Logic Apps Migration

### ISE (Integration Service Environment) → Logic Apps Standard

ISE was retired December 2024. Migration path:

1. **Export**: Export Logic App workflows from ISE
2. **Target**: Logic Apps Standard (single-tenant; runs in App Service Environment or dedicated hosting)
3. **Changes required**:
   - Managed connectors: Some ISE-specific connectors → Standard equivalents
   - Private endpoints: Logic Apps Standard supports private endpoints natively
   - VNet integration: Standard supports regional VNet integration
4. **Deploy**: Use Bicep/ARM or VS Code Logic Apps extension to deploy Standard workflows

### Consumption → Standard Migration

| Aspect | Consumption | Standard |
|---|---|---|
| Hosting | Multi-tenant (Microsoft-managed) | Single-tenant (dedicated hosting plan) |
| Pricing | Per-execution | Per-hour (hosting plan) + per-execution |
| VNet integration | No (limited via connectors) | Yes (full VNet integration) |
| Custom code | Limited | Full Node.js/C# custom code in workflows |
| Stateful vs stateless | Stateful only | Both stateful and stateless workflows |

---

## Azure Static Web Apps Migration

**Purpose**: Migrate existing static sites (GitHub Pages, Netlify, Vercel, S3 static hosting) to Azure Static Web Apps.

### Migration from GitHub Pages

1. Same Git repository; add SWA GitHub Actions workflow
2. Configure `staticwebapp.config.json` for routing rules (replaces Jekyll `_config.yml` routing)
3. Remove GitHub Pages settings; SWA handles custom domain + TLS

### Migration from Netlify/Vercel

- API routes: Migrate Netlify Functions / Vercel Functions → Azure Functions (managed or bring-your-own)
- Environment variables: Migrate to SWA application settings
- `_redirects` / `vercel.json` routing: Migrate to `staticwebapp.config.json` routes array
- Build configuration: Replace netlify.toml/vercel.json build config with GitHub Actions workflow using `azure/static-web-apps-deploy` action

### Key SWA Features After Migration

- Automatic preview environments per pull request (staging environments)
- Built-in authentication (no Netlify Identity/Auth0 needed for simple cases)
- Global CDN distribution (standard with SWA)
- Managed TLS for custom domains (free)
- SLA: 99.95% for standard tier
