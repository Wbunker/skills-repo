# Azure Key Vault — CLI Reference

---

## Vault Management

```bash
# Create a Key Vault with RBAC authorization and Premium SKU
az keyvault create \
  --name myKeyVault \
  --resource-group myRG \
  --location eastus \
  --sku Premium \
  --enable-rbac-authorization true \
  --enable-soft-delete true \
  --soft-delete-retention-days 90 \
  --enable-purge-protection true \
  --public-network-access Disabled \
  --tags Environment=Prod Team=Security

# Create a Key Vault (Standard, allow public network with no firewall — dev only)
az keyvault create \
  --name myDevKeyVault \
  --resource-group myRG \
  --location eastus \
  --sku Standard \
  --enable-rbac-authorization true

# List Key Vaults in a resource group
az keyvault list \
  --resource-group myRG \
  --output table

# List all Key Vaults in subscription (across resource groups)
az keyvault list \
  --output table

# Show Key Vault details
az keyvault show \
  --name myKeyVault \
  --resource-group myRG

# Update vault settings (enable purge protection after creation)
az keyvault update \
  --name myKeyVault \
  --resource-group myRG \
  --enable-purge-protection true

# Disable public network access (force Private Endpoint only)
az keyvault update \
  --name myKeyVault \
  --resource-group myRG \
  --public-network-access Disabled

# Enable RBAC authorization on existing vault (migrates from access policies)
az keyvault update \
  --name myKeyVault \
  --resource-group myRG \
  --enable-rbac-authorization true

# Delete a Key Vault (goes to soft-deleted state)
az keyvault delete \
  --name myKeyVault \
  --resource-group myRG

# List soft-deleted Key Vaults
az keyvault list-deleted \
  --output table

# Recover a soft-deleted Key Vault
az keyvault recover \
  --name myKeyVault \
  --location eastus

# Permanently delete a soft-deleted vault (purge protection must be disabled or retention period must have expired)
az keyvault purge \
  --name myKeyVault \
  --location eastus
```

---

## Access Control

### RBAC (Recommended)

```bash
# Grant Key Vault Secrets User role to a managed identity
MI_PRINCIPAL_ID=$(az identity show --name myMI --resource-group myRG --query principalId --output tsv)
az role assignment create \
  --assignee $MI_PRINCIPAL_ID \
  --role "Key Vault Secrets User" \
  --scope /subscriptions/<sub>/resourceGroups/<rg>/providers/Microsoft.KeyVault/vaults/myKeyVault

# Grant Key Vault Administrator to a user
az role assignment create \
  --assignee admin@contoso.com \
  --role "Key Vault Administrator" \
  --scope /subscriptions/<sub>/resourceGroups/<rg>/providers/Microsoft.KeyVault/vaults/myKeyVault

# Grant Key Vault Secrets Officer to a group
az role assignment create \
  --assignee <group-object-id> \
  --role "Key Vault Secrets Officer" \
  --scope /subscriptions/<sub>/resourceGroups/<rg>/providers/Microsoft.KeyVault/vaults/myKeyVault

# Grant Key Vault Crypto Service Encryption User (for CMK by Azure services)
az role assignment create \
  --assignee <service-principal-id> \
  --role "Key Vault Crypto Service Encryption User" \
  --scope /subscriptions/<sub>/resourceGroups/<rg>/providers/Microsoft.KeyVault/vaults/myKeyVault

# List role assignments on the vault
az role assignment list \
  --scope /subscriptions/<sub>/resourceGroups/<rg>/providers/Microsoft.KeyVault/vaults/myKeyVault \
  --output table
```

### Access Policies (Legacy)

```bash
# Set access policy for a service principal (secrets only)
az keyvault set-policy \
  --name myKeyVault \
  --resource-group myRG \
  --spn <app-id> \
  --secret-permissions get list

# Set access policy for a managed identity
az keyvault set-policy \
  --name myKeyVault \
  --resource-group myRG \
  --object-id <managed-identity-object-id> \
  --secret-permissions get list set delete \
  --key-permissions get list \
  --certificate-permissions get list

# Set access policy for a user
az keyvault set-policy \
  --name myKeyVault \
  --resource-group myRG \
  --upn admin@contoso.com \
  --key-permissions backup create decrypt delete encrypt get import list recover restore sign unwrapKey update verify wrapKey \
  --secret-permissions backup delete get list recover restore set \
  --certificate-permissions backup create delete deleteissuers get getissuers import list listissuers managecontacts manageissuers recover restore setissuers update

# Remove an access policy
az keyvault delete-policy \
  --name myKeyVault \
  --resource-group myRG \
  --object-id <object-id>
```

---

## Secrets

```bash
# Create a secret
az keyvault secret set \
  --vault-name myKeyVault \
  --name myDatabasePassword \
  --value "SuperSecret123!" \
  --content-type "text/plain" \
  --tags Environment=Prod

# Create a secret with expiry
az keyvault secret set \
  --vault-name myKeyVault \
  --name myTempSecret \
  --value "TemporaryValue" \
  --expires "2024-12-31T23:59:59Z"

# Show a secret value
az keyvault secret show \
  --vault-name myKeyVault \
  --name myDatabasePassword

# Show only the secret value (for scripting)
az keyvault secret show \
  --vault-name myKeyVault \
  --name myDatabasePassword \
  --query value \
  --output tsv

# Show a specific version of a secret
az keyvault secret show \
  --vault-name myKeyVault \
  --name myDatabasePassword \
  --version <version-id>

# List all secrets in a vault (names only, not values)
az keyvault secret list \
  --vault-name myKeyVault \
  --output table

# List all versions of a secret
az keyvault secret list-versions \
  --vault-name myKeyVault \
  --name myDatabasePassword \
  --output table

# Update secret attributes (without changing value)
az keyvault secret set-attributes \
  --vault-name myKeyVault \
  --name myDatabasePassword \
  --enabled true \
  --expires "2025-12-31T23:59:59Z" \
  --tags LastRotated="2024-01-15"

# Disable a secret version
az keyvault secret set-attributes \
  --vault-name myKeyVault \
  --name myDatabasePassword \
  --enabled false

# Delete a secret (soft delete)
az keyvault secret delete \
  --vault-name myKeyVault \
  --name myDatabasePassword

# List deleted secrets
az keyvault secret list-deleted \
  --vault-name myKeyVault \
  --output table

# Recover a deleted secret
az keyvault secret recover \
  --vault-name myKeyVault \
  --name myDatabasePassword

# Permanently purge a deleted secret
az keyvault secret purge \
  --vault-name myKeyVault \
  --name myDatabasePassword

# Backup a secret to a file
az keyvault secret backup \
  --vault-name myKeyVault \
  --name myDatabasePassword \
  --file mySecret.bak

# Restore a secret from backup
az keyvault secret restore \
  --vault-name myKeyVault \
  --file mySecret.bak
```

---

## Keys

```bash
# Create an RSA 4096-bit key (software-protected)
az keyvault key create \
  --vault-name myKeyVault \
  --name myRSAKey \
  --kty RSA \
  --size 4096 \
  --ops encrypt decrypt sign verify wrapKey unwrapKey

# Create an RSA 4096-bit key (HSM-backed, Premium SKU required)
az keyvault key create \
  --vault-name myKeyVault \
  --name myHSMKey \
  --kty RSA-HSM \
  --size 4096

# Create an EC P-256 key
az keyvault key create \
  --vault-name myKeyVault \
  --name myECKey \
  --kty EC \
  --curve P-256

# Create a key with expiry and not-before date
az keyvault key create \
  --vault-name myKeyVault \
  --name myTimedKey \
  --kty RSA \
  --size 2048 \
  --not-before "2024-01-01T00:00:00Z" \
  --expires "2025-01-01T00:00:00Z"

# Show key details (does not return private key material)
az keyvault key show \
  --vault-name myKeyVault \
  --name myRSAKey

# Show a specific key version
az keyvault key show \
  --vault-name myKeyVault \
  --name myRSAKey \
  --version <version-id>

# List keys in a vault
az keyvault key list \
  --vault-name myKeyVault \
  --output table

# List all versions of a key
az keyvault key list-versions \
  --vault-name myKeyVault \
  --name myRSAKey \
  --output table

# Configure automatic key rotation policy
az keyvault key rotation-policy update \
  --vault-name myKeyVault \
  --name myRSAKey \
  --value '{
    "lifetimeActions": [
      {
        "trigger": { "timeBeforeExpiry": "P30D" },
        "action": { "type": "Rotate" }
      },
      {
        "trigger": { "timeBeforeExpiry": "P7D" },
        "action": { "type": "Notify" }
      }
    ],
    "attributes": {
      "expiryTime": "P1Y"
    }
  }'

# Show key rotation policy
az keyvault key rotation-policy show \
  --vault-name myKeyVault \
  --name myRSAKey

# Manually rotate a key (creates new version)
az keyvault key rotate \
  --vault-name myKeyVault \
  --name myRSAKey

# Delete a key
az keyvault key delete \
  --vault-name myKeyVault \
  --name myRSAKey

# Recover a deleted key
az keyvault key recover \
  --vault-name myKeyVault \
  --name myRSAKey

# Import a key from PEM file (bring your own key)
az keyvault key import \
  --vault-name myKeyVault \
  --name myImportedKey \
  --pem-file mykey.pem \
  --pem-password "keypassword"
```

---

## Certificates

```bash
# Create a self-signed certificate
az keyvault certificate create \
  --vault-name myKeyVault \
  --name mySelfSignedCert \
  --policy '{
    "x509CertificateProperties": {
      "subject": "CN=example.com",
      "subjectAlternativeNames": {
        "dnsNames": ["example.com", "www.example.com"]
      },
      "validityInMonths": 12,
      "keyUsage": ["digitalSignature", "keyEncipherment"]
    },
    "issuerParameters": { "name": "Self" },
    "keyProperties": {
      "exportable": true,
      "keyType": "RSA",
      "keySize": 2048,
      "reuseKey": false
    },
    "secretProperties": { "contentType": "application/x-pkcs12" },
    "lifetimeActions": [
      {
        "trigger": { "daysBeforeExpiry": 30 },
        "action": { "actionType": "AutoRenew" }
      }
    ]
  }'

# Import an existing certificate (PFX)
az keyvault certificate import \
  --vault-name myKeyVault \
  --name myImportedCert \
  --file mycert.pfx \
  --password "certpassword"

# Import a PEM certificate
az keyvault certificate import \
  --vault-name myKeyVault \
  --name myPEMCert \
  --file mycert.pem

# Show certificate details
az keyvault certificate show \
  --vault-name myKeyVault \
  --name mySelfSignedCert

# List certificates in a vault
az keyvault certificate list \
  --vault-name myKeyVault \
  --output table

# Download certificate (public portion only)
az keyvault certificate download \
  --vault-name myKeyVault \
  --name mySelfSignedCert \
  --file mycert.pem \
  --encoding PEM

# Delete a certificate
az keyvault certificate delete \
  --vault-name myKeyVault \
  --name mySelfSignedCert

# Get certificate as secret (PFX/PEM with private key)
az keyvault secret show \
  --vault-name myKeyVault \
  --name mySelfSignedCert \
  --query value \
  --output tsv | base64 --decode > mycert.pfx
```

---

## Network Rules (Firewall)

```bash
# Allow a specific IP range (Key Vault firewall)
az keyvault network-rule add \
  --name myKeyVault \
  --resource-group myRG \
  --ip-address "203.0.113.0/24"

# Add a specific IP
az keyvault network-rule add \
  --name myKeyVault \
  --resource-group myRG \
  --ip-address "203.0.113.10/32"

# Allow a VNet subnet (Service Endpoint must be enabled on subnet)
az keyvault network-rule add \
  --name myKeyVault \
  --resource-group myRG \
  --vnet-name myVNet \
  --subnet mySubnet

# Set default action to Deny (enable firewall)
az keyvault update \
  --name myKeyVault \
  --resource-group myRG \
  --default-action Deny

# Allow trusted Azure services to bypass firewall
az keyvault update \
  --name myKeyVault \
  --resource-group myRG \
  --bypass AzureServices

# Remove a network rule
az keyvault network-rule remove \
  --name myKeyVault \
  --resource-group myRG \
  --ip-address "203.0.113.0/24"

# List all network rules
az keyvault network-rule list \
  --name myKeyVault \
  --resource-group myRG

# Disable public network access completely (Private Endpoint only)
az keyvault update \
  --name myKeyVault \
  --resource-group myRG \
  --public-network-access Disabled
```

---

## Managed HSM

```bash
# Create a Managed HSM (single-tenant, FIPS 140-2 Level 3)
az keyvault create \
  --hsm-name myManagedHSM \
  --resource-group myRG \
  --location eastus \
  --administrators <admin-object-id-1> <admin-object-id-2> \
  --retention-days 90

# Note: Use az keyvaulthsm commands for Managed HSM operations
# List Managed HSMs
az keyvault list \
  --resource-type managedHSMs \
  --output table

# Create HSM-backed key in Managed HSM
az keyvault key create \
  --hsm-name myManagedHSM \
  --name myHSMKey \
  --kty EC-HSM \
  --curve P-384

# Show Managed HSM key
az keyvault key show \
  --hsm-name myManagedHSM \
  --name myHSMKey
```
