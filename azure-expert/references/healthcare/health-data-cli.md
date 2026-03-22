# Azure Health Data Services — CLI Reference
For service concepts, see [health-data-capabilities.md](health-data-capabilities.md).

## AHDS Workspace Management

```bash
# Install Healthcare APIs extension
az extension add --name healthcareapis

# --- Workspace ---
az healthcareapis workspace create \
  --resource-group myRG \
  --workspace-name myHealthWorkspace \
  --location eastus                            # Create AHDS workspace

az healthcareapis workspace list \
  --resource-group myRG                        # List workspaces

az healthcareapis workspace show \
  --resource-group myRG \
  --workspace-name myHealthWorkspace           # Show workspace details

az healthcareapis workspace update \
  --resource-group myRG \
  --workspace-name myHealthWorkspace \
  --tags environment=production                # Update workspace tags

az healthcareapis workspace delete \
  --resource-group myRG \
  --workspace-name myHealthWorkspace --yes     # Delete workspace (also deletes child services)
```

## FHIR Service

```bash
# --- Create FHIR Service ---
az healthcareapis workspace fhir-service create \
  --resource-group myRG \
  --workspace-name myHealthWorkspace \
  --fhir-service-name myFhirService \
  --location eastus \
  --kind fhir-R4                               # Create FHIR R4 service (recommended)

az healthcareapis workspace fhir-service create \
  --resource-group myRG \
  --workspace-name myHealthWorkspace \
  --fhir-service-name myFhirStu3Service \
  --location eastus \
  --kind fhir-Stu3                             # Create FHIR STU3 service (legacy)

# Create with managed identity and auth audience
az healthcareapis workspace fhir-service create \
  --resource-group myRG \
  --workspace-name myHealthWorkspace \
  --fhir-service-name myFhirService \
  --location eastus \
  --kind fhir-R4 \
  --identity-type SystemAssigned \
  --authentication-authority https://login.microsoftonline.com/<tenant-id> \
  --authentication-audience "https://myFhirService.fhir.azurehealthcareapis.com"

az healthcareapis workspace fhir-service list \
  --resource-group myRG \
  --workspace-name myHealthWorkspace           # List FHIR services in workspace

az healthcareapis workspace fhir-service show \
  --resource-group myRG \
  --workspace-name myHealthWorkspace \
  --fhir-service-name myFhirService            # Show FHIR service details and endpoint URL

az healthcareapis workspace fhir-service update \
  --resource-group myRG \
  --workspace-name myHealthWorkspace \
  --fhir-service-name myFhirService \
  --export-storage-account-name myStorageAcct  # Configure export storage account

az healthcareapis workspace fhir-service delete \
  --resource-group myRG \
  --workspace-name myHealthWorkspace \
  --fhir-service-name myFhirService --yes      # Delete FHIR service

# --- Grant FHIR RBAC Roles ---
# Get FHIR service resource ID
FHIR_ID=$(az healthcareapis workspace fhir-service show \
  --resource-group myRG \
  --workspace-name myHealthWorkspace \
  --fhir-service-name myFhirService \
  --query id -o tsv)

# Grant FHIR Data Contributor to a service principal
az role assignment create \
  --assignee <sp-object-id-or-email> \
  --role "FHIR Data Contributor" \
  --scope $FHIR_ID

# Grant FHIR Data Reader to a user
az role assignment create \
  --assignee user@hospital.org \
  --role "FHIR Data Reader" \
  --scope $FHIR_ID

# Grant FHIR Data Contributor to a managed identity (e.g., Function App)
az role assignment create \
  --assignee <managed-identity-object-id> \
  --role "FHIR Data Contributor" \
  --scope $FHIR_ID

# List FHIR role assignments
az role assignment list --scope $FHIR_ID --output table
```

## DICOM Service

```bash
# --- Create DICOM Service ---
az healthcareapis workspace dicom-service create \
  --resource-group myRG \
  --workspace-name myHealthWorkspace \
  --dicom-service-name myDicomService \
  --location eastus                            # Create DICOM service

az healthcareapis workspace dicom-service list \
  --resource-group myRG \
  --workspace-name myHealthWorkspace           # List DICOM services

az healthcareapis workspace dicom-service show \
  --resource-group myRG \
  --workspace-name myHealthWorkspace \
  --dicom-service-name myDicomService          # Show DICOM service details and service URL

az healthcareapis workspace dicom-service delete \
  --resource-group myRG \
  --workspace-name myHealthWorkspace \
  --dicom-service-name myDicomService --yes    # Delete DICOM service

# --- Grant DICOM RBAC Roles ---
DICOM_ID=$(az healthcareapis workspace dicom-service show \
  --resource-group myRG \
  --workspace-name myHealthWorkspace \
  --dicom-service-name myDicomService \
  --query id -o tsv)

az role assignment create \
  --assignee <sp-object-id> \
  --role "DICOM Data Owner" \
  --scope $DICOM_ID                            # Full DICOM read/write/delete

az role assignment create \
  --assignee <user-email> \
  --role "DICOM Data Reader" \
  --scope $DICOM_ID                            # Read-only DICOM access
```

## MedTech Service (IoT Connector)

```bash
# --- Create MedTech Service ---
az healthcareapis workspace iot-connector create \
  --resource-group myRG \
  --workspace-name myHealthWorkspace \
  --iot-connector-name myMedTechService \
  --location eastus \
  --identity-type SystemAssigned \
  --ingestion-endpoint-configuration \
    consumer-group=medtech \
    event-hub-name=myEventHub \
    fully-qualified-event-hub-namespace=myEventHubNS.servicebus.windows.net \
  --device-mapping '{"templateType": "CollectionContent", "template": []}' \
  --fhir-mapping '{"templateType": "CollectionFhir", "template": []}'

az healthcareapis workspace iot-connector list \
  --resource-group myRG \
  --workspace-name myHealthWorkspace           # List MedTech services

az healthcareapis workspace iot-connector show \
  --resource-group myRG \
  --workspace-name myHealthWorkspace \
  --iot-connector-name myMedTechService        # Show MedTech service details

az healthcareapis workspace iot-connector delete \
  --resource-group myRG \
  --workspace-name myHealthWorkspace \
  --iot-connector-name myMedTechService --yes  # Delete MedTech service

# --- Create FHIR Destination for MedTech ---
az healthcareapis workspace iot-connector fhir-destination create \
  --resource-group myRG \
  --workspace-name myHealthWorkspace \
  --iot-connector-name myMedTechService \
  --fhir-destination-name myFhirDest \
  --location eastus \
  --resource-identity-resolution-type Create \
  --fhir-service-resource-id $FHIR_ID \
  --fhir-mapping '{"templateType": "CollectionFhir", "template": [...]}'

# --- Grant Event Hub access to MedTech managed identity ---
MEDTECH_IDENTITY=$(az healthcareapis workspace iot-connector show \
  --resource-group myRG \
  --workspace-name myHealthWorkspace \
  --iot-connector-name myMedTechService \
  --query identity.principalId -o tsv)

# Get Event Hub resource ID
EH_ID=$(az eventhubs eventhub show \
  --resource-group myRG \
  --namespace-name myEventHubNS \
  --name myEventHub \
  --query id -o tsv)

az role assignment create \
  --assignee $MEDTECH_IDENTITY \
  --role "Azure Event Hubs Data Receiver" \
  --scope $EH_ID                               # Allow MedTech to read from Event Hub

# Grant MedTech write access to FHIR
az role assignment create \
  --assignee $MEDTECH_IDENTITY \
  --role "FHIR Data Writer" \
  --scope $FHIR_ID
```

## FHIR REST API Operations (via az rest)

```bash
# Get bearer token for FHIR service
TOKEN=$(az account get-access-token \
  --resource "https://myFhirService.fhir.azurehealthcareapis.com" \
  --query accessToken -o tsv)

FHIR_URL="https://myFhirService.fhir.azurehealthcareapis.com"

# --- FHIR API Calls ---
# Get FHIR capability statement
curl -H "Authorization: Bearer $TOKEN" "$FHIR_URL/metadata"

# Create a Patient resource
curl -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/fhir+json" \
  -d '{"resourceType":"Patient","name":[{"family":"Smith","given":["John"]}],"gender":"male","birthDate":"1990-01-15"}' \
  "$FHIR_URL/Patient"

# Search Patients
curl -H "Authorization: Bearer $TOKEN" "$FHIR_URL/Patient?name=Smith&_count=10"

# Get a specific Patient
curl -H "Authorization: Bearer $TOKEN" "$FHIR_URL/Patient/patient-id"

# Update a Patient (PUT)
curl -X PUT \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/fhir+json" \
  -d '{"resourceType":"Patient","id":"patient-id","name":[{"family":"Smith","given":["John","Michael"]}],"gender":"male","birthDate":"1990-01-15"}' \
  "$FHIR_URL/Patient/patient-id"

# Delete a Patient
curl -X DELETE -H "Authorization: Bearer $TOKEN" "$FHIR_URL/Patient/patient-id"

# Initiate bulk export
curl -X GET \
  -H "Authorization: Bearer $TOKEN" \
  -H "Accept: application/fhir+json" \
  -H "Prefer: respond-async" \
  "$FHIR_URL/\$export?_type=Patient,Observation,Condition"

# Check export status
curl -H "Authorization: Bearer $TOKEN" "$FHIR_URL/_operations/export/{job-id}"

# FHIR transaction bundle
curl -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/fhir+json" \
  -d @bundle.json \
  "$FHIR_URL"
```

## Legacy API (Single FHIR Service)

```bash
# Legacy API Management command (pre-workspace FHIR service)
az healthcareapis service create \
  --resource-group myRG \
  --resource-name myLegacyFhir \
  --kind fhir-R4 \
  --location eastus \
  --cosmos-db-configuration offer-throughput=1000 \
  --authentication-authority https://login.microsoftonline.com/<tenant-id> \
  --authentication-audience "https://myLegacyFhir.azurehealthcareapis.com" \
  --authentication-smart-proxy-enabled false  # Create legacy FHIR API (use workspace API for new deployments)

az healthcareapis service list --resource-group myRG  # List legacy FHIR API services
```
