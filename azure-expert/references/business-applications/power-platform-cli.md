# Power Platform — CLI Reference
For service concepts, see [power-platform-capabilities.md](power-platform-capabilities.md).

## Power Platform CLI (pac)

```bash
# --- Install Power Platform CLI ---
# Windows (via .NET tool)
dotnet tool install --global Microsoft.PowerApps.CLI.Tool

# macOS/Linux
npm install -g @microsoft/powerplatform-cli

# Or via winget on Windows
winget install Microsoft.PowerAppsCLI

# Verify installation
pac help
pac --version

# --- Authentication ---
pac auth create                                # Authenticate interactively (browser)
pac auth create \
  --url https://myorg.crm.dynamics.com        # Auth to specific environment

pac auth create \
  --applicationId <app-id> \
  --clientSecret <secret> \
  --tenant <tenant-id> \
  --url https://myorg.crm.dynamics.com        # Service principal auth (for CI/CD)

pac auth list                                  # List all saved auth profiles
pac auth select --index 1                      # Switch active auth profile
pac auth delete --index 2                      # Remove an auth profile
pac auth clear                                 # Remove all auth profiles

# --- Environment Management ---
pac env list                                   # List all accessible environments
pac env select --environment myEnvId           # Set active environment
pac env who                                    # Show current environment and user
pac env create \
  --name "Dev-MyProject" \
  --type Sandbox \
  --region unitedstates \
  --currency USD \
  --language 1033                              # Create new sandbox environment (requires admin)
```

## Solution ALM

```bash
# --- Solution Export ---
pac solution export \
  --path ./mysolution.zip \
  --name MySolution \
  --managed false                              # Export unmanaged solution (development)

pac solution export \
  --path ./mysolution-managed.zip \
  --name MySolution \
  --managed true                               # Export managed solution (for deployment)

pac solution export \
  --path ./mysolution.zip \
  --name MySolution \
  --overwrite                                  # Overwrite if file exists

# --- Solution Import ---
pac solution import \
  --path ./mysolution-managed.zip              # Import managed solution to current env

pac solution import \
  --path ./mysolution.zip \
  --force-overwrite \
  --publish-changes                            # Import and immediately publish

pac solution import \
  --path ./mysolution.zip \
  --async                                      # Import asynchronously (large solutions)

# --- Solution Clone (extract to source control) ---
pac solution clone \
  --name MySolution \
  --outputDirectory ./src/solution             # Clone solution to folder (for source control)

# --- Solution Pack/Unpack (source control friendly format) ---
pac solution pack \
  --zipfile ./mysolution.zip \
  --folder ./src/solution \
  --packagetype Both                           # Pack from source to ZIP (Managed + Unmanaged)

pac solution unpack \
  --zipfile ./mysolution.zip \
  --folder ./src/solution \
  --packagetype Both                           # Unpack ZIP to source folder

# --- Solution List & Info ---
pac solution list                              # List all solutions in current environment
pac solution check \
  --path ./mysolution.zip \
  --outputDirectory ./check-results            # Run solution checker (best practice validation)

# --- Publish Customizations ---
pac solution publish                           # Publish all unpublished customizations
```

## Apps and Flows

```bash
# --- Apps ---
pac app list                                   # List all canvas apps in current environment
pac app show --app-id <app-id>                 # Show app details
pac app download \
  --app-id <app-id> \
  --file-name myapp.msapp                      # Download canvas app file (.msapp)

# --- Power Pages (Portals) ---
pac pages download \
  --path ./portal-site \
  --webSiteId <website-id>                    # Download portal content for source control

pac pages upload \
  --path ./portal-site                         # Upload portal content to environment

# --- Flows ---
pac flow list                                  # List cloud flows in current environment
pac flow run list --id <flow-id>              # List recent runs for a flow
pac flow run cancel --flow-id <id> --run-id <run-id>  # Cancel a running flow

# --- PCF (Power Component Framework) Controls ---
pac pcf init \
  --namespace MyControls \
  --name MyCustomControl \
  --template dataset                           # Initialize new PCF control project

pac pcf push \
  --publisher-prefix myprefix                  # Build and push PCF control to environment

pac pcf version \
  --strategy manifest                          # Auto-increment PCF version
```

## Power BI CLI (via PowerShell module)

```powershell
# Install Power BI PowerShell module
Install-Module -Name MicrosoftPowerBIMgmt -Scope CurrentUser

# --- Authentication ---
Connect-PowerBIServiceAccount                  # Interactive login
Connect-PowerBIServiceAccount -ServicePrincipal -Credential $cred -Tenant $tenantId  # SP auth

# --- Workspaces ---
Get-PowerBIWorkspace                           # List all workspaces
Get-PowerBIWorkspace -Name "Finance Analytics" # Get specific workspace
New-PowerBIWorkspace -Name "Sales Analytics"   # Create new workspace

# --- Reports ---
Get-PowerBIReport                              # List all reports
Get-PowerBIReport -WorkspaceId <ws-id>         # List reports in workspace
Export-PowerBIReport -Id <report-id> -OutFile ./report.pbix  # Export report PBIX

# --- Datasets ---
Get-PowerBIDataset                             # List all datasets
Invoke-PowerBIRestMethod -Url "groups/{ws-id}/datasets/{ds-id}/refreshes" -Method POST  # Trigger refresh

# --- Publish report via REST ---
Add-PowerBIReport \
  -Path ./report.pbix \
  -WorkspaceId <ws-id> \
  -ConflictAction CreateOrOverwrite            # Publish/update report

# --- Import Dataset ---
New-PowerBIReport \
  -Path ./report.pbix \
  -Name "Sales Report" \
  -WorkspaceId <ws-id>
```

## CI/CD Pipeline Example (GitHub Actions)

```yaml
# .github/workflows/deploy-solution.yml
name: Deploy Power Platform Solution

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Install Power Platform CLI
        run: |
          npm install -g @microsoft/powerplatform-cli

      - name: Authenticate to Power Platform
        run: |
          pac auth create \
            --applicationId ${{ secrets.PP_CLIENT_ID }} \
            --clientSecret ${{ secrets.PP_CLIENT_SECRET }} \
            --tenant ${{ secrets.PP_TENANT_ID }} \
            --url ${{ secrets.PP_ENVIRONMENT_URL }}

      - name: Pack solution
        run: |
          pac solution pack \
            --zipfile ./release/MySolution_managed.zip \
            --folder ./src/solution \
            --packagetype Managed

      - name: Import solution to production
        run: |
          pac solution import \
            --path ./release/MySolution_managed.zip \
            --environment ${{ secrets.PP_ENVIRONMENT_URL }} \
            --force-overwrite \
            --publish-changes \
            --async
```
