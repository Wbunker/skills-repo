# Static Web Apps & App Service — Capabilities Reference
For CLI commands, see [static-apps-cli.md](static-apps-cli.md).

## Azure Static Web Apps (SWA)

**Purpose**: Fully managed hosting for static web applications (HTML, CSS, JavaScript) and Jamstack frameworks. Includes automatic CI/CD, global CDN, managed TLS, API backend via Azure Functions, and built-in authentication — all from a single resource.

### Key Features

| Feature | Details |
|---|---|
| **Automatic CI/CD** | GitHub Actions or Azure DevOps pipeline auto-generated on creation; deploys on every push/PR |
| **Preview environments** | Every pull request gets a unique URL for review (staging slot per PR) |
| **Global CDN distribution** | Static assets distributed globally; Microsoft's edge network |
| **Managed SSL/TLS** | Free certificate for custom domains; auto-renewal |
| **Custom domains** | Multiple custom domains with apex domain support |
| **Built-in auth** | Zero-config authentication with GitHub, Microsoft, Google, Apple, Facebook, Twitter/X |
| **API backend** | Managed Azure Functions backend or bring-your-own linked Functions app |
| **Configuration** | `staticwebapp.config.json` for routing, headers, auth, fallback routes |
| **SWA CLI** | Local development emulator (`swa start`) mimics full SWA behavior locally |

### Supported Frameworks

| Category | Frameworks |
|---|---|
| **React ecosystem** | React (CRA), Next.js (static/hybrid), Gatsby, Remix |
| **Vue ecosystem** | Vue, Nuxt.js (static) |
| **Angular** | Angular |
| **Other SPA** | Svelte, SvelteKit, Lit, Solid, Qwik |
| **Static site generators** | Hugo, Jekyll, Eleventy, Hexo, VuePress |
| **WebAssembly** | Blazor WebAssembly |
| **Plain HTML** | Any static HTML/CSS/JS |

### staticwebapp.config.json

```json
{
  "routes": [
    {
      "route": "/api/*",
      "allowedRoles": ["authenticated"]
    },
    {
      "route": "/admin/*",
      "allowedRoles": ["administrator"]
    },
    {
      "route": "/*",
      "rewrite": "/index.html"
    }
  ],
  "navigationFallback": {
    "rewrite": "/index.html",
    "exclude": ["/images/*.{png,jpg,gif}", "/css/*"]
  },
  "responseOverrides": {
    "401": {
      "statusCode": 302,
      "redirect": "/login"
    },
    "404": {
      "rewrite": "/custom-404.html",
      "statusCode": 404
    }
  },
  "globalHeaders": {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "Content-Security-Policy": "default-src https: 'unsafe-inline';"
  },
  "auth": {
    "identityProviders": {
      "github": {
        "userDetailsClaim": "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/name"
      }
    }
  },
  "mimeTypes": {
    ".json": "text/json"
  }
}
```

### API Integration

| Mode | Description | Use Case |
|---|---|---|
| **Managed Functions** | Functions deployed with SWA; managed together | Simple APIs; single deployment unit |
| **Linked backend** | Bring your own App Service, Functions app, Container App, or API Management | Complex backends; existing infrastructure |

- Managed Functions: limited to Azure Functions (Node.js, Python, C#, Java); no Durable Functions
- Linked backend: full Azure Functions features including Durable Functions, custom triggers

### Tiers

| Tier | Price | Features |
|---|---|---|
| **Free** | $0 | 100 GB bandwidth/month; 2 custom domains; community SLA |
| **Standard** | ~$9/month | 100 GB + $0.20/GB overage; 5 custom domains; 99.95% SLA; private endpoints |

### Preview Environments (Staging)

- Each open PR automatically gets a unique preview URL: `https://<app>.{hash}.westus2.azurestaticapps.net`
- Preview URLs are deactivated when PR is merged or closed
- Preview environments are separate from production; have their own settings override
- Use for QA, stakeholder review, automated testing before merge

---

## Azure App Service for Web/API Hosting

**Purpose**: Fully managed platform for hosting web applications, REST APIs, and mobile backends without managing server infrastructure. Supports multiple languages and runtime stacks.

### Supported Stacks

| Language | Versions | Notes |
|---|---|---|
| **Node.js** | 16, 18, 20 LTS | Native npm support; PM2 clustering |
| **Python** | 3.8–3.12 | Gunicorn (Linux); FastAPI/Flask/Django |
| **Java** | 8, 11, 17, 21 | Tomcat, JBoss, embedded server |
| **.NET** | 6, 7, 8 | ASP.NET Core; Windows or Linux |
| **PHP** | 8.0, 8.2, 8.3 | Apache (Linux) |
| **Ruby** | 3.1, 3.3 | Passenger |
| **Go** | Custom container | Via container deployment |
| **Custom containers** | Any Docker image | Maximum flexibility |

### Key Features

| Feature | Description |
|---|---|
| **Deployment slots** | Staging environments with swap capability (zero-downtime deployments) |
| **Auto-scaling** | Scale out (more instances) or up (larger instances) based on CPU, memory, or schedule |
| **Custom domains** | Multiple domains with SNI TLS; managed TLS certificate |
| **VNet integration** | Route outbound traffic through VNet to access private resources |
| **Private endpoints** | Inbound access via private endpoint (no public internet exposure) |
| **Managed identity** | System or user-assigned identity for accessing Azure services |
| **App Service Environment** | Dedicated infrastructure in your VNet; maximum isolation; v3 (ASEv3) |
| **WebJobs** | Background tasks running within App Service; triggered or continuous |
| **Easy Auth** | Built-in authentication without code changes (see auth-capabilities.md) |

### Deployment Methods

| Method | Tools | Use Case |
|---|---|---|
| **GitHub Actions** | `azure/webapps-deploy` action | CI/CD from GitHub |
| **Azure DevOps** | Azure App Service deployment task | Enterprise CI/CD |
| **Zip deploy** | `az webapp deployment source config-zip` | Quick deploy from CLI |
| **Run from Package** | Set `WEBSITE_RUN_FROM_PACKAGE=1` | Deploy zip; mount as read-only; faster cold start |
| **Container** | Docker registry or ACR | Custom runtime or multi-service apps |
| **VS Code** | Azure App Service extension | Developer workflow |
| **FTP** | Legacy; avoid for new deployments | Only if no other option |

### App Service Plan

| Tier | Scaling | Features | Use Case |
|---|---|---|---|
| **Free/Shared** | No | Shared infrastructure; no custom domains | Dev/testing only |
| **Basic** | Manual | Custom domains; up to 3 instances | Dev with moderate traffic |
| **Standard** | Autoscale | Deployment slots; 5 instances | Production workloads |
| **Premium v3** | Autoscale | 30 instances; larger VMs; zone redundancy | High-scale production |
| **Isolated v2 (ASE)** | Dedicated | VNet isolation; up to 100 instances | Regulated/enterprise |

### Deployment Slots

```bash
# Create staging slot
az webapp deployment slot create --name myapp --resource-group myRG --slot staging

# Deploy to staging slot
az webapp deployment source config-zip --name myapp --resource-group myRG --slot staging --src app.zip

# Swap staging to production (zero-downtime)
az webapp deployment slot swap --name myapp --resource-group myRG --slot staging --target-slot production
```
