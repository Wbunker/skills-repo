# Azure CLI & Cloud Shell — Capabilities Reference
For CLI commands, see [cli-shell-cli.md](cli-shell-cli.md).

## Azure CLI (az)

**Purpose**: Cross-platform, Python-based command-line interface for managing Azure resources. Supports Windows, macOS, Linux, and runs natively in Azure Cloud Shell.

### Core Architecture

| Concept | Description |
|---|---|
| **Command groups** | Hierarchical structure mirroring Azure services: `az vm`, `az storage`, `az network`, etc. |
| **Global parameters** | Apply to any command: `--output`, `--query`, `--verbose`, `--debug`, `--subscription`, `--only-show-errors` |
| **JMESPath queries** | `--query` flag accepts JMESPath expressions for server-side filtering of JSON output |
| **Extensions** | Optional add-ons for preview/specialized services: `az extension add --name <name>` |
| **Interactive mode** | `az interactive` provides auto-complete with embedded documentation |
| **Configuration** | `az configure` sets persistent defaults; stored in `~/.azure/config` |

### Output Formats

| Format | Flag | Use Case |
|---|---|---|
| `json` | `--output json` | Default; machine-readable; full fidelity |
| `jsonc` | `--output jsonc` | Colorized JSON for terminal readability |
| `table` | `--output table` | Human-readable ASCII table |
| `tsv` | `--output tsv` | Tab-separated; ideal for shell scripting and `awk`/`cut` |
| `yaml` | `--output yaml` | YAML format; useful for Kubernetes-style configs |
| `yamlc` | `--output yamlc` | Colorized YAML |
| `none` | `--output none` | Suppress output; useful in automation when only exit code matters |

### Common Global Flags

| Flag | Description |
|---|---|
| `--subscription` | Override the active subscription by name or ID |
| `--resource-group` / `-g` | Target resource group |
| `--location` / `-l` | Azure region (e.g., `eastus`, `westeurope`) |
| `--name` / `-n` | Resource name |
| `--output` / `-o` | Output format (json, table, tsv, yaml, etc.) |
| `--query` | JMESPath expression to filter/project output |
| `--verbose` | Show detailed request/response info |
| `--debug` | Show full HTTP request/response for troubleshooting |
| `--no-wait` | Submit async operation without waiting for completion |
| `--only-show-errors` | Suppress warnings; show only errors |

### JMESPath Query Examples

```bash
# Project specific fields from a list
az vm list --query "[].{name:name, location:location, size:hardwareProfile.vmSize}" -o table

# Filter by property value
az vm list --query "[?location=='eastus'].name" -o tsv

# Nested filtering
az storage account list --query "value[?name=='mystorageacct']"

# Get a single property
az group show --name myRG --query location -o tsv

# Count resources
az resource list --query "length(@)"

# Sort (requires client-side sort after tsv output)
az vm list --query "sort_by(@, &name)[].name" -o tsv
```

---

## Azure Cloud Shell

**Purpose**: Browser-based shell environment with persistent storage and pre-installed Azure management tools. Accessible from the Azure Portal or directly at shell.azure.com.

### Key Characteristics

| Feature | Details |
|---|---|
| **Shell types** | Bash (default) or PowerShell; switch anytime |
| **Persistent storage** | `$HOME` backed by an Azure Files share (5 GiB default) mounted at `/home/<user>` |
| **Authentication** | Automatically authenticated as the signed-in Azure AD user; no `az login` needed |
| **Ephemeral compute** | Container spun up per session; non-home files are ephemeral |
| **Timeout** | Session times out after ~20 minutes of inactivity |
| **Connectivity** | Runs inside Microsoft's network; can access private endpoints via Cloud Shell VNet injection |

### Pre-installed Tools

| Tool | Purpose |
|---|---|
| `az` | Azure CLI |
| `pwsh` | PowerShell 7 with Az module |
| `kubectl` | Kubernetes management |
| `helm` | Kubernetes package manager |
| `terraform` | Infrastructure as code |
| `git` | Version control |
| `docker` | Container CLI (daemon not available; build via ACR Tasks) |
| `ansible` | Configuration management |
| `python3` | Scripting; azure SDK available |
| `node` / `npm` | JavaScript runtime |
| `dotnet` | .NET SDK |
| `jq` | JSON processing |
| `code` | Monaco editor (browser-integrated) |

---

## Azure PowerShell (Az Module)

**Purpose**: PowerShell module providing cmdlets for Azure resource management. Preferred for Windows shops, complex conditional logic, and integration with existing PowerShell automation.

### Core Cmdlets

| Cmdlet | Description |
|---|---|
| `Connect-AzAccount` | Authenticate to Azure (browser, device code, service principal, managed identity) |
| `Get-AzSubscription` | List available subscriptions |
| `Set-AzContext` | Switch active subscription/tenant |
| `Get-AzResourceGroup` | List or get a specific resource group |
| `New-AzResourceGroup` | Create a resource group |
| `Remove-AzResourceGroup` | Delete a resource group (with `-Force` to skip confirmation) |
| `Get-AzResource` | List/search resources across resource groups |
| `New-AzResourceGroupDeployment` | Deploy ARM/Bicep templates |
| `Get-AzRoleAssignment` | List RBAC role assignments |
| `New-AzRoleAssignment` | Assign an RBAC role |

### Authentication Options

```powershell
# Interactive browser login
Connect-AzAccount

# Device code flow (for headless environments)
Connect-AzAccount -UseDeviceAuthentication

# Service principal with client secret
$cred = New-Object -TypeName PSCredential -ArgumentList $clientId, (ConvertTo-SecureString $clientSecret -AsPlainText -Force)
Connect-AzAccount -ServicePrincipal -Credential $cred -Tenant $tenantId

# Managed identity (from Azure resource)
Connect-AzAccount -Identity

# Switch subscription after login
Set-AzContext -Subscription "00000000-0000-0000-0000-000000000000"
```

---

## Service Principal Authentication

**Purpose**: Non-interactive authentication for CI/CD pipelines, automation, and application identities.

### Azure CLI Service Principal Login

```bash
# Login with client secret
az login --service-principal \
  --username $AZURE_CLIENT_ID \
  --password $AZURE_CLIENT_SECRET \
  --tenant $AZURE_TENANT_ID

# Login with certificate
az login --service-principal \
  --username $AZURE_CLIENT_ID \
  --tenant $AZURE_TENANT_ID \
  --password /path/to/cert.pem
```

### Environment Variables for SDK Authentication

| Variable | Description |
|---|---|
| `AZURE_SUBSCRIPTION_ID` | Target subscription ID |
| `AZURE_TENANT_ID` | Entra ID tenant ID |
| `AZURE_CLIENT_ID` | Application (client) ID of the service principal |
| `AZURE_CLIENT_SECRET` | Client secret (password-based auth) |
| `AZURE_CLIENT_CERTIFICATE_PATH` | Path to PEM/PFX certificate (certificate-based auth) |
| `AZURE_FEDERATED_TOKEN_FILE` | Path to OIDC token file (workload identity / federated credential) |

---

## Managed Identity Authentication

**Purpose**: Eliminate credential management for workloads running on Azure resources. The Azure platform handles token issuance automatically.

| Type | Description |
|---|---|
| **System-assigned** | Identity tied to a single resource lifecycle; deleted when resource is deleted |
| **User-assigned** | Standalone identity; can be shared across multiple resources |

```bash
# Azure CLI from a VM/container with managed identity
az login --identity                     # system-assigned
az login --identity --username <client-id>  # specific user-assigned identity

# SDK: DefaultAzureCredential (recommended for all production code)
# Tries: Environment vars → Workload Identity → Managed Identity → Azure CLI → VS Code → ...
```

### DefaultAzureCredential Chain (Python example)

```python
from azure.identity import DefaultAzureCredential
from azure.mgmt.compute import ComputeManagementClient

credential = DefaultAzureCredential()
client = ComputeManagementClient(credential, subscription_id)
# No hardcoded secrets; works locally (CLI auth) and in production (Managed Identity)
```
