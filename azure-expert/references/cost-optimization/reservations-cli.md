# Azure Reservations & Savings Plans — CLI Reference
For service concepts, see [reservations-capabilities.md](reservations-capabilities.md).

> **Note**: Reservation purchase via Azure CLI has limited support; most purchases are made through the Azure portal or REST API. The CLI provides comprehensive listing, utilization reporting, and management commands.

## Reservations Management

```bash
# --- Install the reservations extension ---
az extension add --name reservation

# --- List reservations ---
# List all reservations in a billing enrollment/account
az reservations reservation-order list \
  --query "[].{OrderId:name, DisplayName:displayName, Term:term, ExpiryDate:expiryDate, Quantity:reservedResourceProperties.quantity}" \
  --output table

# List reservations within a specific order
az reservations reservation list \
  --reservation-order-id {reservation-order-id} \
  --query "[].{ReservationId:name, SKU:sku.name, Region:location, State:provisioningState, ExpiryDate:expiryDate}" \
  --output table

# Show details of a specific reservation
az reservations reservation show \
  --reservation-order-id {reservation-order-id} \
  --reservation-id {reservation-id}

# List all reservation orders
az reservations reservation-order list \
  --output table

# Show details of a reservation order
az reservations reservation-order show \
  --reservation-order-id {reservation-order-id}

# --- Calculate reservation purchase price ---
# Calculate price before purchasing (returns estimated cost)
az reservations reservation-order calculate \
  --sku Standard_D4s_v5 \
  --location eastus \
  --reserved-resource-type VirtualMachines \
  --billing-scope /subscriptions/{subId} \
  --term P1Y \
  --billing-plan Upfront \
  --quantity 3 \
  --applied-scope-type Shared

# Calculate for 3-year term with monthly billing
az reservations reservation-order calculate \
  --sku Standard_D4s_v5 \
  --location eastus \
  --reserved-resource-type VirtualMachines \
  --billing-scope /subscriptions/{subId} \
  --term P3Y \
  --billing-plan Monthly \
  --quantity 1 \
  --applied-scope-type Single \
  --applied-scopes /subscriptions/{subId}

# Calculate SQL Database reservation price
az reservations reservation-order calculate \
  --sku GP_Gen5 \
  --location eastus \
  --reserved-resource-type SqlDatabases \
  --billing-scope /subscriptions/{subId} \
  --term P1Y \
  --billing-plan Upfront \
  --quantity 1

# --- Purchase a reservation ---
# Purchase a VM reserved instance (1-year, shared scope, upfront payment)
az reservations reservation-order purchase \
  --reservation-order-id $(uuidgen) \
  --sku Standard_D4s_v5 \
  --location eastus \
  --reserved-resource-type VirtualMachines \
  --billing-scope /subscriptions/{subId} \
  --term P1Y \
  --billing-plan Upfront \
  --quantity 2 \
  --applied-scope-type Shared \
  --display-name "D4s_v5_EastUS_Prod_2x"

# --- Update reservation scope ---
# Change from single subscription scope to shared scope
az reservations reservation update \
  --reservation-order-id {reservation-order-id} \
  --reservation-id {reservation-id} \
  --applied-scope-type Shared

# Change to specific subscription scope
az reservations reservation update \
  --reservation-order-id {reservation-order-id} \
  --reservation-id {reservation-id} \
  --applied-scope-type Single \
  --applied-scopes /subscriptions/{subId}
```

## Reservation Utilization Reporting

```bash
# --- Consumption: Reservation utilization ---
# List reservation details (daily utilization) for a month
az consumption reservation detail list \
  --start-date 2024-12-01 \
  --end-date 2024-12-31 \
  --reservation-order-id {reservation-order-id} \
  --query "[].{Date:usageDate, ReservedHours:reservedHours, UsedHours:usedHours, UtilizationPct:utilizationPercentage}" \
  --output table

# List reservation summaries (monthly rollup)
az consumption reservation summary list \
  --start-date 2024-12-01 \
  --end-date 2024-12-31 \
  --reservation-order-id {reservation-order-id} \
  --grain monthly \
  --query "[].{Month:usageDate, ReservedHours:reservedHours, UsedHours:usedHours, UtilizationPct:utilizationPercentage}" \
  --output table

# List daily reservation summaries for a specific order
az consumption reservation summary list \
  --start-date 2024-12-01 \
  --end-date 2024-12-31 \
  --reservation-order-id {reservation-order-id} \
  --grain daily \
  --output table

# --- Usage reporting for cost analysis ---
# Get subscription usage/spend for last month
az consumption usage list \
  --start-date 2024-12-01 \
  --end-date 2024-12-31 \
  --query "[?contains(instanceId, 'microsoft.compute')].{ResourceId:instanceId, Cost:pretaxCost, Currency:currency}" \
  --output table

# List marketplace usage (3rd-party services)
az consumption marketplace list \
  --start-date 2024-12-01 \
  --end-date 2024-12-31 \
  --output table
```

## Azure Savings Plans

```bash
# --- Install billing extension ---
az extension add --name billing

# List savings plan orders
az billing savings-plan-order list \
  --query "[].{Name:name, DisplayName:displayName, Term:term, Status:status}" \
  --output table

# Show a specific savings plan order
az billing savings-plan-order show \
  --savings-plan-order-id {savings-plan-order-id}

# List savings plans within an order
az billing savings-plan list \
  --savings-plan-order-id {savings-plan-order-id} \
  --query "[].{Name:name, DisplayName:displayName, Commitment:commitment.amount, Currency:commitment.currencyCode, Term:term}" \
  --output table

# Show savings plan details
az billing savings-plan-order savings-plan show \
  --savings-plan-order-id {savings-plan-order-id} \
  --savings-plan-id {savings-plan-id}

# List all savings plans in the account
az billing savings-plan list \
  --output table
```

## Reservation Recommendations

```bash
# --- Azure Advisor recommendations for reservations ---
# List all Cost category recommendations (includes RI suggestions)
az advisor recommendation list \
  --category Cost \
  --query "[?shortDescription.solution != null].{Resource:resourceId, Impact:impact, Solution:shortDescription.solution}" \
  --output table

# List specifically RI-related recommendations
az advisor recommendation list \
  --category Cost \
  --query "[?contains(shortDescription.solution, 'Reserved Instance') || contains(shortDescription.solution, 'reservation')].{Resource:resourceId, Impact:impact, Solution:shortDescription.solution}" \
  --output table

# Show a specific recommendation in detail
az advisor recommendation describe \
  --recommendation-id {recommendation-id} \
  --resource-group myRG \
  --resource-name myVM \
  --resource-type Microsoft.Compute/virtualMachines \
  --output json
```

## Reservation Governance Scripts

```bash
# --- Find underutilized reservations (utilization < 80%) ---
# Script: check all reservation orders and flag low utilization
for order_id in $(az reservations reservation-order list --query "[].name" -o tsv); do
  echo "=== Reservation Order: ${order_id} ==="
  az consumption reservation summary list \
    --start-date $(date -d "30 days ago" +%Y-%m-01) \
    --end-date $(date +%Y-%m-%d) \
    --reservation-order-id ${order_id} \
    --grain monthly \
    --query "[?utilizationPercentage < '80'].{UsageDate:usageDate, UsedHours:usedHours, ReservedHours:reservedHours, Utilization:utilizationPercentage}" \
    --output table 2>/dev/null
done

# --- Find VMs that are good candidates for reservation ---
# List VMs running consistently (stopped VMs waste reservations)
az vm list \
  --show-details \
  --query "[?powerState=='VM running'].{Name:name, RG:resourceGroup, Size:hardwareProfile.vmSize, Location:location}" \
  --output table

# --- Check expiring reservations (next 90 days) ---
# Find reservations expiring soon
az reservations reservation-order list \
  --query "[].{OrderId:name, DisplayName:displayName, ExpiryDate:expiryDate}" \
  --output tsv | awk -v today="$(date +%Y-%m-%d)" -v limit="$(date -d "+90 days" +%Y-%m-%d)" \
  '$3 <= limit && $3 >= today {print "EXPIRING SOON:", $0}'
```
