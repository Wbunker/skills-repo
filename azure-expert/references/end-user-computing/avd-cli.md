# Azure Virtual Desktop — CLI Reference
For service concepts, see [avd-capabilities.md](avd-capabilities.md).

## AVD Core Resources

```bash
# Install desktopvirtualization extension
az extension add --name desktopvirtualization

# --- Workspaces ---
az desktopvirtualization workspace create \
  --resource-group myRG \
  --name myWorkspace \
  --location eastus \
  --friendly-name "Engineering Workspace" \
  --description "Workspace for engineering team virtual desktops"

az desktopvirtualization workspace list \
  --resource-group myRG                          # List workspaces

az desktopvirtualization workspace show \
  --resource-group myRG \
  --name myWorkspace                             # Show workspace details

az desktopvirtualization workspace update \
  --resource-group myRG \
  --name myWorkspace \
  --friendly-name "Engineering Desktop"          # Update workspace

az desktopvirtualization workspace delete \
  --resource-group myRG \
  --name myWorkspace --yes                       # Delete workspace

# --- Host Pools ---
az desktopvirtualization hostpool create \
  --resource-group myRG \
  --name myPooledHostPool \
  --location eastus \
  --host-pool-type Pooled \
  --load-balancer-type BreadthFirst \
  --preferred-app-group-type Desktop \
  --max-session-limit 10 \
  --personal-desktop-assignment-type Automatic  # Create pooled host pool (breadth-first)

az desktopvirtualization hostpool create \
  --resource-group myRG \
  --name myPersonalHostPool \
  --location eastus \
  --host-pool-type Personal \
  --load-balancer-type Persistent \
  --preferred-app-group-type Desktop \
  --personal-desktop-assignment-type Automatic  # Create personal (dedicated) host pool

az desktopvirtualization hostpool list \
  --resource-group myRG                          # List all host pools

az desktopvirtualization hostpool show \
  --resource-group myRG \
  --name myPooledHostPool                        # Show host pool details

az desktopvirtualization hostpool update \
  --resource-group myRG \
  --name myPooledHostPool \
  --max-session-limit 15 \
  --load-balancer-type DepthFirst                # Update host pool settings

az desktopvirtualization hostpool delete \
  --resource-group myRG \
  --name myPooledHostPool --yes                  # Delete host pool

# Generate registration token for adding session hosts
az desktopvirtualization hostpool retrieve-registration-token \
  --resource-group myRG \
  --name myPooledHostPool                        # Get registration token (used when joining VMs to pool)

az desktopvirtualization hostpool registration-info \
  --resource-group myRG \
  --name myPooledHostPool                        # Show current registration info and expiry
```

## Application Groups

```bash
# --- Application Groups ---
az desktopvirtualization applicationgroup create \
  --resource-group myRG \
  --name myDesktopAppGroup \
  --location eastus \
  --application-group-type Desktop \
  --host-pool-arm-path /subscriptions/{subId}/resourceGroups/myRG/providers/Microsoft.DesktopVirtualization/hostPools/myPooledHostPool \
  --workspace-arm-path /subscriptions/{subId}/resourceGroups/myRG/providers/Microsoft.DesktopVirtualization/workspaces/myWorkspace  # Create Desktop app group

az desktopvirtualization applicationgroup create \
  --resource-group myRG \
  --name myRemoteApps \
  --location eastus \
  --application-group-type RemoteApp \
  --host-pool-arm-path /subscriptions/{subId}/resourceGroups/myRG/providers/Microsoft.DesktopVirtualization/hostPools/myPooledHostPool \
  --workspace-arm-path /subscriptions/{subId}/resourceGroups/myRG/providers/Microsoft.DesktopVirtualization/workspaces/myWorkspace  # Create RemoteApp group

az desktopvirtualization applicationgroup list \
  --resource-group myRG                          # List all application groups

az desktopvirtualization applicationgroup show \
  --resource-group myRG \
  --name myDesktopAppGroup                       # Show app group details

az desktopvirtualization applicationgroup delete \
  --resource-group myRG \
  --name myDesktopAppGroup --yes                 # Delete app group

# --- Assign users/groups to application group ---
az role assignment create \
  --assignee "user@company.com" \
  --role "Desktop Virtualization User" \
  --scope /subscriptions/{subId}/resourceGroups/myRG/providers/Microsoft.DesktopVirtualization/applicationGroups/myDesktopAppGroup

az role assignment create \
  --assignee <group-object-id> \
  --role "Desktop Virtualization User" \
  --scope /subscriptions/{subId}/resourceGroups/myRG/providers/Microsoft.DesktopVirtualization/applicationGroups/myDesktopAppGroup

# --- RemoteApp Applications ---
az desktopvirtualization application create \
  --resource-group myRG \
  --application-group-name myRemoteApps \
  --name notepad \
  --friendly-name "Notepad" \
  --file-path "C:\\Windows\\System32\\notepad.exe" \
  --icon-path "C:\\Windows\\System32\\notepad.exe" \
  --icon-index 0 \
  --command-line-setting Allow                   # Publish Notepad as RemoteApp

az desktopvirtualization application create \
  --resource-group myRG \
  --application-group-name myRemoteApps \
  --name excel \
  --friendly-name "Microsoft Excel" \
  --application-type InBuilt \
  --msix-package-family-name "Microsoft.Office.EXCEL..."  # Publish MSIX-packaged app

az desktopvirtualization application list \
  --resource-group myRG \
  --application-group-name myRemoteApps          # List published RemoteApp applications

az desktopvirtualization application delete \
  --resource-group myRG \
  --application-group-name myRemoteApps \
  --name notepad                                 # Remove published application
```

## Session Hosts

```bash
# --- Session Hosts ---
az desktopvirtualization sessionhost list \
  --resource-group myRG \
  --host-pool-name myPooledHostPool              # List all session hosts in pool

az desktopvirtualization sessionhost show \
  --resource-group myRG \
  --host-pool-name myPooledHostPool \
  --name "myHostPool/myVM01.company.com"         # Show session host details

az desktopvirtualization sessionhost update \
  --resource-group myRG \
  --host-pool-name myPooledHostPool \
  --name "myHostPool/myVM01.company.com" \
  --allow-new-session false                      # Drain sessions (prevent new sessions)

az desktopvirtualization sessionhost delete \
  --resource-group myRG \
  --host-pool-name myPooledHostPool \
  --name "myHostPool/myVM01.company.com"         # Remove session host registration

# --- User Sessions ---
az desktopvirtualization usersession list \
  --resource-group myRG \
  --host-pool-name myPooledHostPool \
  --host-session-host-name "myHostPool/myVM01.company.com"  # List active sessions on a host

az desktopvirtualization usersession disconnect \
  --resource-group myRG \
  --host-pool-name myPooledHostPool \
  --host-session-host-name "myHostPool/myVM01.company.com" \
  --user-session-id 2                            # Disconnect a user session

az desktopvirtualization usersession delete \
  --resource-group myRG \
  --host-pool-name myPooledHostPool \
  --host-session-host-name "myHostPool/myVM01.company.com" \
  --user-session-id 2 \
  --force                                        # Force logoff a user session
```

## Scaling Plans

```bash
# --- Scaling Plans ---
az desktopvirtualization scalingplan create \
  --resource-group myRG \
  --name myScalingPlan \
  --location eastus \
  --host-pool-type Pooled \
  --time-zone "Eastern Standard Time" \
  --schedules '[{
    "name": "weekdays",
    "daysOfWeek": ["Monday","Tuesday","Wednesday","Thursday","Friday"],
    "rampUpStartTime": {"hour": 7, "minute": 0},
    "rampUpLoadBalancingAlgorithm": "BreadthFirst",
    "rampUpMinimumHostsPct": 20,
    "rampUpCapacityThresholdPct": 60,
    "peakStartTime": {"hour": 9, "minute": 0},
    "peakLoadBalancingAlgorithm": "BreadthFirst",
    "rampDownStartTime": {"hour": 18, "minute": 0},
    "rampDownLoadBalancingAlgorithm": "DepthFirst",
    "rampDownMinimumHostsPct": 10,
    "rampDownCapacityThresholdPct": 90,
    "rampDownForceLogoffUsers": false,
    "rampDownWaitTimeMinutes": 30,
    "rampDownNotificationMessage": "Session ending in 30 minutes",
    "offPeakStartTime": {"hour": 20, "minute": 0},
    "offPeakLoadBalancingAlgorithm": "DepthFirst"
  }]'

az desktopvirtualization scalingplan list \
  --resource-group myRG                          # List scaling plans

az desktopvirtualization scalingplan show \
  --resource-group myRG \
  --name myScalingPlan                           # Show scaling plan details

# Assign scaling plan to host pool
az desktopvirtualization scalingplan update \
  --resource-group myRG \
  --name myScalingPlan \
  --host-pool-references host-pool-arm-path=/subscriptions/{subId}/resourceGroups/myRG/providers/Microsoft.DesktopVirtualization/hostPools/myPooledHostPool,scaling-plan-enabled=true

az desktopvirtualization scalingplan delete \
  --resource-group myRG \
  --name myScalingPlan --yes                     # Delete scaling plan

# --- MSIX App Attach ---
az desktopvirtualization msixpackage create \
  --resource-group myRG \
  --host-pool-name myPooledHostPool \
  --name myMSIXPackage \
  --image-path "\\\\myfileserver\\msix\\myapp.vhd" \
  --is-active true \
  --package-name "MyApp"                         # Register MSIX package for app attach
```
