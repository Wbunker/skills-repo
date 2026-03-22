# Developer Environments — CLI Reference
For service concepts, see [dev-environments-capabilities.md](dev-environments-capabilities.md).

## Azure DevTest Labs

```bash
# --- Lab Management ---
az lab create \
  --resource-group myRG \
  --name myLab \
  --location eastus                               # Create a DevTest Lab

az lab show --resource-group myRG --name myLab   # Get lab details
az lab list --resource-group myRG                # List labs in resource group

az lab delete --resource-group myRG --name myLab --yes  # Delete lab

# --- VM Management ---
az lab vm create \
  --resource-group myRG \
  --lab-name myLab \
  --name myLabVM \
  --image "Visual Studio 2022 Enterprise on Windows 11 Enterprise (x64)" \
  --image-type GalleryImage \
  --size Standard_D4s_v5 \
  --user-name devuser \
  --generate-ssh-keys                            # Create lab VM

az lab vm list \
  --resource-group myRG \
  --lab-name myLab                               # List all VMs in lab

az lab vm show \
  --resource-group myRG \
  --lab-name myLab \
  --name myLabVM                                 # Get VM details

az lab vm start \
  --resource-group myRG \
  --lab-name myLab \
  --name myLabVM                                 # Start a lab VM

az lab vm stop \
  --resource-group myRG \
  --lab-name myLab \
  --name myLabVM                                 # Stop a lab VM

az lab vm delete \
  --resource-group myRG \
  --lab-name myLab \
  --name myLabVM --yes                           # Delete a lab VM

az lab vm claim \
  --resource-group myRG \
  --lab-name myLab                               # Claim a claimable VM

# --- Environments ---
az lab environment create \
  --resource-group myRG \
  --lab-name myLab \
  --name myEnv \
  --arm-template "/subscriptions/{subId}/..." \
  --artifact-source-name "Public Repo"           # Create an environment from ARM template

az lab environment list \
  --resource-group myRG \
  --lab-name myLab                               # List environments in lab

az lab environment delete \
  --resource-group myRG \
  --lab-name myLab \
  --name myEnv --yes                             # Delete environment

# --- Custom Images ---
az lab custom-image list \
  --resource-group myRG \
  --lab-name myLab                               # List custom images

az lab gallery-image list \
  --resource-group myRG \
  --lab-name myLab                               # List available gallery images

# --- Artifact Sources ---
az lab artifact-source list \
  --resource-group myRG \
  --lab-name myLab                               # List artifact repositories

az lab arm-template list \
  --resource-group myRG \
  --lab-name myLab \
  --artifact-source-name "Public Repo"           # List available ARM templates
```

## Microsoft Dev Box

```bash
# Install Dev Center extension
az extension add --name devcenter

# --- Dev Center Management ---
az devcenter admin devcenter create \
  --resource-group myRG \
  --name myDevCenter \
  --location eastus                              # Create a Dev Center

az devcenter admin devcenter list \
  --resource-group myRG                          # List Dev Centers

# --- Dev Box Definitions ---
az devcenter admin devbox-definition create \
  --resource-group myRG \
  --dev-center-name myDevCenter \
  --name "VS2022-8core" \
  --image-reference id="/subscriptions/.../galleries/.../images/..." \
  --os-storage-type "ssd_512gb" \
  --sku name="general_8c32gb512ssd_v2"           # Create a Dev Box definition

az devcenter admin devbox-definition list \
  --resource-group myRG \
  --dev-center-name myDevCenter                  # List definitions

# --- Projects ---
az devcenter admin project create \
  --resource-group myRG \
  --dev-center-id /subscriptions/.../devcenters/myDevCenter \
  --name myProject \
  --location eastus                              # Create a project

az devcenter admin project list \
  --resource-group myRG                          # List projects

# --- Dev Box Pools ---
az devcenter admin pool create \
  --resource-group myRG \
  --project-name myProject \
  --name myPool \
  --devbox-definition-name "VS2022-8core" \
  --local-administrator Enabled \
  --network-connection-name myNetworkConnection  # Create a pool

az devcenter admin pool list \
  --resource-group myRG \
  --project-name myProject                       # List pools

# --- Developer Operations (self-service) ---
az devcenter dev dev-box create \
  --dev-center-name myDevCenter \
  --project-name myProject \
  --pool-name myPool \
  --name myDevBox \
  --user-id "me"                                 # Create a Dev Box (as developer)

az devcenter dev dev-box list \
  --dev-center-name myDevCenter \
  --project-name myProject                       # List my Dev Boxes

az devcenter dev dev-box show \
  --dev-center-name myDevCenter \
  --project-name myProject \
  --name myDevBox                                # Get Dev Box details

az devcenter dev dev-box start \
  --dev-center-name myDevCenter \
  --project-name myProject \
  --name myDevBox                                # Start Dev Box

az devcenter dev dev-box stop \
  --dev-center-name myDevCenter \
  --project-name myProject \
  --name myDevBox                                # Stop (deallocate) Dev Box

az devcenter dev dev-box restart \
  --dev-center-name myDevCenter \
  --project-name myProject \
  --name myDevBox                                # Restart Dev Box

az devcenter dev dev-box delete \
  --dev-center-name myDevCenter \
  --project-name myProject \
  --name myDevBox --yes                          # Delete Dev Box

az devcenter dev dev-box get-remote-connection \
  --dev-center-name myDevCenter \
  --project-name myProject \
  --name myDevBox                                # Get RDP connection URL
```

## Azure Deployment Environments

```bash
# --- Environment Management (developer self-service) ---
az devcenter dev environment create \
  --dev-center-name myDevCenter \
  --project-name myProject \
  --name myEnv \
  --environment-type Dev \
  --catalog-name "myCompanyCatalog" \
  --environment-definition-name "webapp-with-sql"  # Deploy an environment from catalog

az devcenter dev environment list \
  --dev-center-name myDevCenter \
  --project-name myProject                         # List my environments

az devcenter dev environment show \
  --dev-center-name myDevCenter \
  --project-name myProject \
  --name myEnv                                     # Get environment details

az devcenter dev environment deploy \
  --dev-center-name myDevCenter \
  --project-name myProject \
  --name myEnv \
  --parameters '{"sqlSku": "S1"}'                  # Re-deploy with updated parameters

az devcenter dev environment delete \
  --dev-center-name myDevCenter \
  --project-name myProject \
  --name myEnv --yes                               # Delete environment and resources

# --- Catalog Management (platform engineering) ---
az devcenter admin catalog create \
  --resource-group myRG \
  --dev-center-name myDevCenter \
  --name myCompanyCatalog \
  --git-hub uri="https://github.com/myorg/environments.git" branch="main" path="/definitions"

az devcenter admin catalog list \
  --resource-group myRG \
  --dev-center-name myDevCenter                    # List catalogs

az devcenter admin catalog sync \
  --resource-group myRG \
  --dev-center-name myDevCenter \
  --name myCompanyCatalog                          # Sync catalog from Git
```

## Dev Tunnels

```bash
# --- Dev Tunnels CLI ---
devtunnel login                                    # Authenticate with Microsoft account
devtunnel logout

devtunnel host --port 3000                         # Quick tunnel: expose localhost:3000
devtunnel host --port 3000 --allow-anonymous       # Public tunnel (no auth required)

devtunnel create my-tunnel                         # Create a named persistent tunnel
devtunnel port add my-tunnel --port-number 3000 --protocol http  # Add port to tunnel
devtunnel port add my-tunnel --port-number 5000 --protocol http  # Add second port
devtunnel host my-tunnel                           # Start hosting the named tunnel

devtunnel show my-tunnel                           # Show tunnel details and URLs
devtunnel list                                     # List all tunnels for current user
devtunnel delete my-tunnel                         # Delete tunnel

devtunnel access create my-tunnel --anonymous      # Allow anonymous access
devtunnel access list my-tunnel                    # List access policies

# Access a hosted tunnel (from another machine)
devtunnel connect my-tunnel                        # Connect to a tunnel
```
