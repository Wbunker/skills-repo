# Azure OpenAI Service — CLI & SDK Reference

## Prerequisites

```bash
# Install/upgrade Azure CLI
az upgrade

# Login
az login

# Set default subscription
az account set --subscription "My Subscription"
```

---

## Resource Management

### Create Azure OpenAI Resource

```bash
# Create a new Azure OpenAI resource
az cognitiveservices account create \
  --name myopenai \
  --resource-group myRG \
  --kind OpenAI \
  --sku S0 \
  --location eastus \
  --yes

# Show resource details (endpoint URL)
az cognitiveservices account show \
  --name myopenai \
  --resource-group myRG \
  --query "properties.endpoint" -o tsv

# List all Azure OpenAI resources in subscription
az cognitiveservices account list \
  --query "[?kind=='OpenAI']" \
  -o table

# Delete resource
az cognitiveservices account delete \
  --name myopenai \
  --resource-group myRG
```

### Network Access Configuration

```bash
# Restrict to selected networks (add VNet rule)
az cognitiveservices account network-rule add \
  --name myopenai \
  --resource-group myRG \
  --subnet /subscriptions/{sub}/resourceGroups/{rg}/providers/Microsoft.Network/virtualNetworks/{vnet}/subnets/{subnet}

# Set default action to Deny (after adding rules)
az cognitiveservices account update \
  --name myopenai \
  --resource-group myRG \
  --default-action Deny

# Create private endpoint
az network private-endpoint create \
  --name myopenai-pe \
  --resource-group myRG \
  --vnet-name myVNet \
  --subnet mySubnet \
  --private-connection-resource-id $(az cognitiveservices account show --name myopenai --resource-group myRG --query id -o tsv) \
  --group-id account \
  --connection-name myopenai-connection
```

---

## Model Deployments

```bash
# Create a deployment (Standard tier, 100K TPM capacity)
az cognitiveservices account deployment create \
  --name myopenai \
  --resource-group myRG \
  --deployment-name gpt-4o-prod \
  --model-name gpt-4o \
  --model-version "2024-11-20" \
  --model-format OpenAI \
  --sku-name Standard \
  --sku-capacity 100

# Create a Global Standard deployment (higher quota)
az cognitiveservices account deployment create \
  --name myopenai \
  --resource-group myRG \
  --deployment-name gpt-4o-global \
  --model-name gpt-4o \
  --model-version "2024-11-20" \
  --model-format OpenAI \
  --sku-name GlobalStandard \
  --sku-capacity 300

# Create embedding deployment
az cognitiveservices account deployment create \
  --name myopenai \
  --resource-group myRG \
  --deployment-name text-embedding-3-small \
  --model-name text-embedding-3-small \
  --model-version "1" \
  --model-format OpenAI \
  --sku-name Standard \
  --sku-capacity 120

# List all deployments in a resource
az cognitiveservices account deployment list \
  --name myopenai \
  --resource-group myRG \
  -o table

# Show specific deployment details (capacity, model version, status)
az cognitiveservices account deployment show \
  --name myopenai \
  --resource-group myRG \
  --deployment-name gpt-4o-prod

# Delete a deployment
az cognitiveservices account deployment delete \
  --name myopenai \
  --resource-group myRG \
  --deployment-name gpt-4o-prod
```

---

## Keys and Authentication

```bash
# List API keys (Key1 and Key2)
az cognitiveservices account keys list \
  --name myopenai \
  --resource-group myRG \
  -o json

# Get just Key1 value
az cognitiveservices account keys list \
  --name myopenai \
  --resource-group myRG \
  --query key1 -o tsv

# Regenerate Key1 (rotate without downtime — update apps to Key2 first)
az cognitiveservices account keys regenerate \
  --name myopenai \
  --resource-group myRG \
  --key-name Key1

# Assign Cognitive Services OpenAI User role (for Managed Identity access)
az role assignment create \
  --assignee <object-id-of-MI-or-user> \
  --role "Cognitive Services OpenAI User" \
  --scope $(az cognitiveservices account show --name myopenai --resource-group myRG --query id -o tsv)

# Assign contributor for deployment management
az role assignment create \
  --assignee <object-id> \
  --role "Cognitive Services OpenAI Contributor" \
  --scope $(az cognitiveservices account show --name myopenai --resource-group myRG --query id -o tsv)
```

---

## Available Models

```bash
# List models available in a region
az cognitiveservices account list-models \
  --name myopenai \
  --resource-group myRG \
  -o table

# List models available in a location (before creating resource)
az cognitiveservices model list \
  --kind OpenAI \
  --location eastus \
  -o table
```

---

## Python SDK Patterns

### Installation

```bash
pip install openai azure-identity
```

### API Key Authentication (dev/test)

```python
from openai import AzureOpenAI

client = AzureOpenAI(
    azure_endpoint="https://myopenai.openai.azure.com/",
    api_key="<your-api-key>",          # from Key Vault in production
    api_version="2024-10-01-preview"   # use latest stable version
)

# Chat completion
response = client.chat.completions.create(
    model="gpt-4o-prod",               # deployment name, not model name
    messages=[
        {"role": "system", "content": "You are a helpful Azure expert."},
        {"role": "user", "content": "What is a PTU?"}
    ],
    max_tokens=500,
    temperature=0.7
)
print(response.choices[0].message.content)
print(f"Tokens used: {response.usage.total_tokens}")
```

### Managed Identity Authentication (production)

```python
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from openai import AzureOpenAI

# DefaultAzureCredential checks: env vars, MI, VS Code, Azure CLI, etc.
token_provider = get_bearer_token_provider(
    DefaultAzureCredential(),
    "https://cognitiveservices.azure.com/.default"
)

client = AzureOpenAI(
    azure_endpoint="https://myopenai.openai.azure.com/",
    azure_ad_token_provider=token_provider,
    api_version="2024-10-01-preview"
)
```

### Streaming Response

```python
stream = client.chat.completions.create(
    model="gpt-4o-prod",
    messages=[{"role": "user", "content": "Write a haiku about Azure."}],
    stream=True
)

for chunk in stream:
    if chunk.choices[0].delta.content is not None:
        print(chunk.choices[0].delta.content, end="", flush=True)
```

### Embeddings

```python
response = client.embeddings.create(
    model="text-embedding-3-small",    # deployment name
    input=["Azure OpenAI is enterprise AI.", "Machine learning at scale."],
    dimensions=512                      # optional: reduce dimensions
)

for i, embedding in enumerate(response.data):
    print(f"Vector {i}: {len(embedding.embedding)} dimensions")
```

### Function Calling / Tool Use

```python
tools = [{
    "type": "function",
    "function": {
        "name": "get_resource_cost",
        "description": "Get Azure resource cost for a given period",
        "parameters": {
            "type": "object",
            "properties": {
                "resource_id": {"type": "string", "description": "Azure resource ID"},
                "period": {"type": "string", "enum": ["last_7_days", "last_30_days"]}
            },
            "required": ["resource_id", "period"]
        }
    }
}]

response = client.chat.completions.create(
    model="gpt-4o-prod",
    messages=[{"role": "user", "content": "What did my storage account cost last month?"}],
    tools=tools,
    tool_choice="auto"
)

# Check if model wants to call a function
if response.choices[0].finish_reason == "tool_calls":
    tool_call = response.choices[0].message.tool_calls[0]
    print(f"Function: {tool_call.function.name}")
    print(f"Arguments: {tool_call.function.arguments}")
```

### Assistants API

```python
# Create an assistant
assistant = client.beta.assistants.create(
    name="Policy Analyst",
    instructions="Answer questions about company policies using the provided documents.",
    model="gpt-4o-prod",
    tools=[{"type": "file_search"}]
)

# Create a vector store and upload files
vector_store = client.beta.vector_stores.create(name="Policy Docs")
with open("hr_policy.pdf", "rb") as f:
    client.beta.vector_stores.file_batches.upload_and_poll(
        vector_store_id=vector_store.id, files=[f]
    )

# Link vector store to assistant
client.beta.assistants.update(
    assistant.id,
    tool_resources={"file_search": {"vector_store_ids": [vector_store.id]}}
)

# Run a conversation
thread = client.beta.threads.create()
client.beta.threads.messages.create(
    thread_id=thread.id, role="user", content="What is our PTO policy?"
)
run = client.beta.threads.runs.create_and_poll(
    thread_id=thread.id, assistant_id=assistant.id
)

messages = client.beta.threads.messages.list(thread_id=thread.id)
print(messages.data[0].content[0].text.value)
```

---

## Content Filter Configuration

```bash
# Content filter policies are configured via Azure portal or REST API
# Use REST API to create a custom content filter policy:
ENDPOINT="https://myopenai.openai.azure.com"
API_VERSION="2024-10-01-preview"
API_KEY=$(az cognitiveservices account keys list --name myopenai --resource-group myRG --query key1 -o tsv)

curl -X PUT "${ENDPOINT}/openai/contentfilters/my-policy?api-version=${API_VERSION}" \
  -H "api-key: ${API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "my-policy",
    "mode": "Default",
    "contentFilters": [
      {"name": "hate", "allowedContentLevel": "Medium", "blocking": true, "enabled": true, "source": "Prompt"},
      {"name": "violence", "allowedContentLevel": "Medium", "blocking": true, "enabled": true, "source": "Prompt"}
    ]
  }'
```

---

## Environment Variable Pattern

```bash
# Set environment variables for SDK configuration
export AZURE_OPENAI_ENDPOINT="https://myopenai.openai.azure.com/"
export AZURE_OPENAI_API_KEY=$(az cognitiveservices account keys list \
  --name myopenai --resource-group myRG --query key1 -o tsv)
export AZURE_OPENAI_API_VERSION="2024-10-01-preview"

# Python SDK auto-reads these env vars:
# client = AzureOpenAI()  # no explicit params needed
```
