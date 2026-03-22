# Azure AI Health Services — CLI Reference
For service concepts, see [ai-health-capabilities.md](ai-health-capabilities.md).

## Azure Health Bot

```bash
# --- Create Health Bot ---
az bot create \
  --resource-group myRG \
  --name myHealthBot \
  --kind azurebot \
  --location global \
  --sku F0 \
  --endpoint "https://myhealthbot.azurewebsites.net/api/messages" \
  --app-id <microsoft-app-id>                 # Create Azure Bot resource (F0 = free tier)

az bot create \
  --resource-group myRG \
  --name myHealthBot \
  --kind azurebot \
  --location global \
  --sku S1 \
  --endpoint "https://myhealthbot.azurewebsites.net/api/messages" \
  --app-id <microsoft-app-id>                 # Create with S1 premium tier

az bot list --resource-group myRG             # List bot resources
az bot show --resource-group myRG --name myHealthBot  # Show bot details

az bot delete --resource-group myRG --name myHealthBot  # Delete bot

# --- Bot Channels ---
# Enable Microsoft Teams channel
az bot msteams create \
  --resource-group myRG \
  --name myHealthBot \
  --enable-calling false                      # Enable Teams channel (no calling)

# Enable Web Chat channel
az bot webchat show \
  --resource-group myRG \
  --name myHealthBot                          # Show Web Chat channel secret

# List bot channels
az bot channel list \
  --resource-group myRG \
  --name myHealthBot                          # List all enabled channels

# Get Web Chat embed secret
az bot webchat show \
  --resource-group myRG \
  --name myHealthBot \
  --query properties.sites[0].key -o tsv     # Web Chat secret key for embedding

# --- Health Bot Service (separate from generic bot) ---
# Azure Health Bot is a separate service at portal.azure.com
# Create via ARM template or Bicep (no dedicated az CLI command)
az deployment group create \
  --resource-group myRG \
  --template-uri "https://raw.githubusercontent.com/Azure/azure-quickstart-templates/master/quickstarts/microsoft.healthbot/azure-health-bot/azuredeploy.json" \
  --parameters botName=myHealthBot sku=F0    # Deploy Health Bot via ARM template

# Get Health Bot management portal URL
HEALTHBOT_ID=$(az resource list \
  --resource-group myRG \
  --resource-type "Microsoft.HealthBot/healthBots" \
  --query "[0].id" -o tsv)
az resource show --ids $HEALTHBOT_ID --query properties.botManagementPortalLink -o tsv
```

## Text Analytics for Health

```bash
# --- Create Language Service (Text Analytics for Health is part of Language service) ---
az cognitiveservices account create \
  --resource-group myRG \
  --name myLanguageService \
  --kind TextAnalytics \
  --sku S \
  --location eastus \
  --yes                                       # Create Language service (S = Standard, enables TAforH)

# Free tier (limited transactions)
az cognitiveservices account create \
  --resource-group myRG \
  --name myLanguageServiceFree \
  --kind TextAnalytics \
  --sku F0 \
  --location eastus \
  --yes                                       # Create free tier (5K transactions/month)

az cognitiveservices account list \
  --resource-group myRG --output table        # List all cognitive services accounts

az cognitiveservices account show \
  --resource-group myRG \
  --name myLanguageService                    # Show account details and endpoint

# Get API keys
az cognitiveservices account keys list \
  --resource-group myRG \
  --name myLanguageService                    # Get Key1 and Key2

# Regenerate keys
az cognitiveservices account keys regenerate \
  --resource-group myRG \
  --name myLanguageService \
  --key-name key1                             # Regenerate primary key

az cognitiveservices account delete \
  --resource-group myRG \
  --name myLanguageService                    # Delete Language service

# --- Private Endpoint for Language Service (HIPAA compliance) ---
az network private-endpoint create \
  --resource-group myRG \
  --name myLanguageServicePE \
  --vnet-name myVNet \
  --subnet PrivateSubnet \
  --private-connection-resource-id $(az cognitiveservices account show --resource-group myRG --name myLanguageService --query id -o tsv) \
  --group-id account \
  --connection-name myLanguageServiceConnection  # Create private endpoint

# Disable public access after enabling private endpoint
az cognitiveservices account update \
  --resource-group myRG \
  --name myLanguageService \
  --public-network-access Disabled            # Disable public internet access
```

## Text Analytics for Health — REST API

```bash
# Set variables
ENDPOINT="https://myLanguageService.cognitiveservices.azure.com"
KEY=$(az cognitiveservices account keys list --resource-group myRG --name myLanguageService --query key1 -o tsv)

# --- Submit healthcare analysis job ---
curl -X POST \
  "$ENDPOINT/language/analyze-text/jobs?api-version=2023-04-01" \
  -H "Ocp-Apim-Subscription-Key: $KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "displayName": "clinical-note-analysis",
    "analysisInput": {
      "documents": [
        {
          "id": "1",
          "language": "en",
          "text": "Patient is a 65-year-old male with Type 2 diabetes mellitus, managed on metformin 500mg twice daily. He presents with chest pain radiating to the left arm for 3 hours. Troponin elevated at 2.3."
        }
      ]
    },
    "tasks": [
      {
        "kind": "Healthcare",
        "taskName": "healthcare-entities",
        "parameters": {
          "modelVersion": "latest",
          "fhirVersion": "4.0.1"
        }
      }
    ]
  }'
# Returns: {"jobId": "...", "status": "running", ...}

# --- Poll job status ---
JOB_ID="<job-id-from-above>"
curl -H "Ocp-Apim-Subscription-Key: $KEY" \
  "$ENDPOINT/language/analyze-text/jobs/$JOB_ID?api-version=2023-04-01"

# --- Synchronous analysis (short documents) ---
curl -X POST \
  "$ENDPOINT/language/:analyze-text?api-version=2023-04-01" \
  -H "Ocp-Apim-Subscription-Key: $KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "kind": "Healthcare",
    "analysisInput": {
      "documents": [{"id": "1", "language": "en", "text": "Patient has pneumonia with fever 39.2C"}]
    },
    "parameters": {"modelVersion": "latest"}
  }'
```

## AI Health Insights (Preview)

```bash
# --- Create Health Insights Resource ---
az cognitiveservices account create \
  --resource-group myRG \
  --name myHealthInsights \
  --kind HealthInsights \
  --sku S0 \
  --location eastus \
  --yes                                       # Create Health Insights resource (preview)

az cognitiveservices account list \
  --resource-group myRG \
  --query "[?kind=='HealthInsights']" --output table  # List Health Insights resources

# Get endpoint and key
az cognitiveservices account show \
  --resource-group myRG \
  --name myHealthInsights \
  --query properties.endpoint -o tsv          # Show endpoint URL

az cognitiveservices account keys list \
  --resource-group myRG \
  --name myHealthInsights                     # Get API keys
```

## Health Insights REST API

```bash
INSIGHTS_ENDPOINT="https://myHealthInsights.cognitiveservices.azure.com"
INSIGHTS_KEY=$(az cognitiveservices account keys list --resource-group myRG --name myHealthInsights --query key1 -o tsv)

# --- Radiology Insights job ---
curl -X POST \
  "$INSIGHTS_ENDPOINT/health-insights/radiology-insights/jobs?api-version=2024-04-01" \
  -H "Ocp-Apim-Subscription-Key: $INSIGHTS_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "jobData": {
      "configuration": {
        "inferenceOptions": {
          "followupRecommendationOptions": {"includeRecommendationsWithNoSpecifiedModality": true},
          "findingOptions": {"provideFocusedSentenceEvidence": true}
        },
        "inferenceTypes": ["Finding", "CriticalResult", "FollowupRecommendation", "AgeMismatch"],
        "locale": "en-US",
        "verbose": false
      },
      "patients": [{
        "id": "patient-001",
        "info": {"sex": "male", "birthDate": "1959-11-11"},
        "encounters": [{
          "id": "encounter-001",
          "period": {"start": "2024-01-15", "end": "2024-01-15"},
          "class": "inpatient"
        }],
        "patientDocuments": [{
          "type": "note",
          "clinicalType": "radiologyReport",
          "id": "report-001",
          "language": "en",
          "authors": [{"id": "rad-001", "fullName": "Dr. Jane Smith"}],
          "specialtyType": "radiology",
          "createdAt": "2024-01-15T10:00:00Z",
          "administrativeMetadata": {"encounterId": "encounter-001"},
          "content": {
            "sourceType": "inline",
            "value": "CT chest without contrast. The lungs are clear. No pleural effusion. No pneumothorax. The heart size is normal. Impression: No acute cardiopulmonary process."
          }
        }]
      }]
    }
  }'

# Poll job status
RADIOLOGY_JOB_ID="<job-id>"
curl -H "Ocp-Apim-Subscription-Key: $INSIGHTS_KEY" \
  "$INSIGHTS_ENDPOINT/health-insights/radiology-insights/jobs/$RADIOLOGY_JOB_ID?api-version=2024-04-01"

# --- Clinical Trial Matching job ---
curl -X POST \
  "$INSIGHTS_ENDPOINT/health-insights/clinical-matching/jobs?api-version=2024-04-01" \
  -H "Ocp-Apim-Subscription-Key: $INSIGHTS_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "jobData": {
      "configuration": {
        "clinicalTrials": {
          "registryFilters": [{
            "conditions": ["non-small cell lung cancer"],
            "phases": ["phase2", "phase3"],
            "sources": ["clinicaltrials.gov"],
            "facilityLocations": [{"countryOrRegion": "United States", "state": "Washington", "city": "Seattle"}]
          }]
        }
      },
      "patients": [{
        "id": "patient-001",
        "info": {"sex": "female", "birthDate": "1965-03-20"},
        "patientDocuments": [{
          "type": "note",
          "clinicalType": "consultation",
          "id": "note-001",
          "language": "en",
          "content": {
            "sourceType": "inline",
            "value": "Patient has stage IIIA non-small cell lung cancer, EGFR mutation positive. No prior targeted therapy. ECOG performance status 1."
          }
        }]
      }]
    }
  }'
```
