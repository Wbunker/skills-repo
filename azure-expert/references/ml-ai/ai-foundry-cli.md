# Azure AI Foundry — CLI & SDK Reference

## Prerequisites

```bash
# AI Foundry hub/projects use the Azure ML CLI extension (v2)
az extension add -n ml
az extension update -n ml

# Prompt Flow CLI
pip install promptflow promptflow-tools

# Azure AI Projects SDK (for AI Agent Service)
pip install azure-ai-projects azure-ai-inference

az login
az account set --subscription "My Subscription"
```

---

## Hub Management

```bash
# Create an AI Foundry hub
az ml workspace create \
  --kind hub \
  --name my-ai-hub \
  --resource-group myRG \
  --location eastus \
  --display-name "My AI Hub"

# Create hub with managed VNet (recommended for production)
az ml workspace create \
  --kind hub \
  --name my-ai-hub \
  --resource-group myRG \
  --location eastus \
  --managed-network allow_internet_outbound

# Show hub details
az ml workspace show \
  --name my-ai-hub \
  --resource-group myRG

# List all hubs in resource group
az ml workspace list \
  --resource-group myRG \
  --query "[?kind=='hub']" \
  -o table

# Delete hub (will fail if projects exist — delete projects first)
az ml workspace delete \
  --name my-ai-hub \
  --resource-group myRG \
  --yes
```

---

## Project Management

```bash
# Get hub resource ID
HUB_ID=$(az ml workspace show \
  --name my-ai-hub \
  --resource-group myRG \
  --query id -o tsv)

# Create an AI Foundry project within a hub
az ml workspace create \
  --kind project \
  --name my-ai-project \
  --resource-group myRG \
  --hub-id $HUB_ID \
  --display-name "Customer Support Bot"

# List projects within a hub
az ml workspace list \
  --resource-group myRG \
  --query "[?kind=='project']" \
  -o table

# Show project details (includes connection string)
az ml workspace show \
  --name my-ai-project \
  --resource-group myRG

# Get project connection string (for SDK)
az ml workspace show \
  --name my-ai-project \
  --resource-group myRG \
  --query "properties.discoveryUrl" -o tsv
```

---

## Connections

```bash
# Create an Azure OpenAI connection at hub level
az ml connection create \
  --file openai-connection.yaml \
  --resource-group myRG \
  --workspace-name my-ai-hub

# openai-connection.yaml example:
cat <<EOF > openai-connection.yaml
name: azure-openai-eastus
type: azure_open_ai
endpoint: https://myopenai.openai.azure.com/
api_key: <key>  # or use managed identity
api_version: "2024-10-01-preview"
EOF

# Create Azure AI Search connection
az ml connection create \
  --file search-connection.yaml \
  --resource-group myRG \
  --workspace-name my-ai-hub

# search-connection.yaml:
cat <<EOF > search-connection.yaml
name: azure-ai-search
type: cognitive_search
endpoint: https://mysearch.search.windows.net
api_key: <admin-key>
EOF

# List connections (hub-level)
az ml connection list \
  --resource-group myRG \
  --workspace-name my-ai-hub \
  -o table

# List connections (project-level — includes inherited hub connections)
az ml connection list \
  --resource-group myRG \
  --workspace-name my-ai-project \
  -o table

# Show connection details
az ml connection show \
  --name azure-openai-eastus \
  --resource-group myRG \
  --workspace-name my-ai-hub

# Delete connection
az ml connection delete \
  --name old-connection \
  --resource-group myRG \
  --workspace-name my-ai-hub \
  --yes
```

---

## Model Deployments (Serverless API / MaaS)

Serverless API deployments are managed via the AI Foundry portal or REST/SDK. The `az ml` CLI does not have a dedicated `serverless-deployment` command; use the SDK or portal.

```python
# Deploy a model via serverless API using azure-ai-ml SDK
from azure.ai.ml import MLClient
from azure.ai.ml.entities import ServerlessEndpoint
from azure.identity import DefaultAzureCredential

ml_client = MLClient(
    DefaultAzureCredential(),
    subscription_id="<sub-id>",
    resource_group_name="myRG",
    workspace_name="my-ai-project"
)

# Create a serverless endpoint for LLaMA 3
endpoint = ServerlessEndpoint(
    name="llama-3-70b-endpoint",
    model_id="azureml://registries/azureml-meta/models/Meta-Llama-3.1-70B-Instruct/versions/3"
)
created_endpoint = ml_client.serverless_endpoints.begin_create_or_update(endpoint).result()
print(f"Endpoint URI: {created_endpoint.scoring_uri}")
print(f"Key: {ml_client.serverless_endpoints.get_keys(name=endpoint.name).primary_key}")
```

```bash
# List serverless endpoints (online endpoints with serverless billing)
az ml online-endpoint list \
  --resource-group myRG \
  --workspace-name my-ai-project \
  -o table
```

---

## Prompt Flow CLI

The `pf` (prompt flow) CLI is the primary tool for local development, testing, and deployment of flows.

```bash
# Initialize a new flow from template
pf flow init --flow ./my-chat-flow --type chat

# Initialize a standard (non-chat) flow
pf flow init --flow ./my-rag-flow --type standard

# Test a flow locally with a single input
pf flow test \
  --flow ./my-chat-flow \
  --inputs question="What is Azure AI Foundry?"

# Test with interactive chat mode
pf flow test \
  --flow ./my-chat-flow \
  --interactive

# Run a flow against a dataset (batch testing)
pf run create \
  --flow ./my-chat-flow \
  --data ./test_data.jsonl \
  --column-mapping question='${data.question}' \
  --stream

# List all runs
pf run list

# Show run details and metrics
pf run show --name <run-name>

# Show run outputs
pf run show-details --name <run-name>

# Show run metrics (for evaluation flows)
pf run show-metrics --name <run-name>

# Build flow for deployment (packages into deployable artifact)
pf flow build \
  --flow ./my-chat-flow \
  --output ./build-output \
  --format docker

# Validate flow YAML
pf flow validate --flow ./my-chat-flow

# Create a connection for local development
pf connection create --file azure-openai-connection.yaml

# List local connections
pf connection list

# Show connection
pf connection show --name azure-openai-connection
```

---

## Prompt Flow on Azure (Remote Runs)

```bash
# Submit a flow run to Azure AI Foundry (project)
pf run create \
  --flow ./my-chat-flow \
  --data ./test_data.jsonl \
  --column-mapping question='${data.question}' \
  --runtime <runtime-name> \
  --subscription <sub-id> \
  --resource-group myRG \
  --workspace-name my-ai-project \
  --stream

# Run an evaluation flow against a previous run's outputs
pf run create \
  --flow ./eval_flow \
  --run <previous-run-name> \
  --column-mapping answer='${run.outputs.answer}' question='${run.inputs.question}' ground_truth='${data.ground_truth}' \
  --subscription <sub-id> \
  --resource-group myRG \
  --workspace-name my-ai-project

# Deploy a flow as an online endpoint in Azure
pf flow deploy \
  --flow ./my-chat-flow \
  --endpoint-name my-flow-endpoint \
  --subscription <sub-id> \
  --resource-group myRG \
  --workspace-name my-ai-project
```

---

## Azure AI Projects SDK (Agent Service)

```python
import os
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import (
    AgentThread, ThreadMessage, RunStatus,
    FileSearchTool, BingGroundingTool, CodeInterpreterTool
)
from azure.identity import DefaultAzureCredential

# Initialize client using connection string from portal
project_client = AIProjectClient.from_connection_string(
    conn_str=os.environ["AIPROJECT_CONNECTION_STRING"],
    credential=DefaultAzureCredential()
)

# --- Create and use an agent ---
agent = project_client.agents.create_agent(
    model="gpt-4o-prod",
    name="Research Assistant",
    instructions="You are a research assistant. Use file search and Bing to answer questions.",
    tools=FileSearchTool().definitions + BingGroundingTool(
        connection_id="<bing-connection-id>"
    ).definitions
)

# Create a thread
thread = project_client.agents.create_thread()

# Send a message
project_client.agents.create_message(
    thread_id=thread.id,
    role="user",
    content="What are the latest developments in Azure AI Foundry?"
)

# Run the agent and wait for completion
run = project_client.agents.create_and_process_run(
    thread_id=thread.id,
    assistant_id=agent.id
)

# Get the response
messages = project_client.agents.list_messages(thread_id=thread.id)
print(messages.data[0].content[0].text.value)

# Cleanup
project_client.agents.delete_agent(agent.id)
```

---

## Azure AI Inference SDK (Model Endpoints)

```python
from azure.ai.inference import ChatCompletionsClient
from azure.ai.inference.models import SystemMessage, UserMessage
from azure.core.credentials import AzureKeyCredential

# For serverless API (MaaS) endpoints
client = ChatCompletionsClient(
    endpoint="https://myproject.eastus.models.ai.azure.com",
    credential=AzureKeyCredential("<key>")
)

response = client.complete(
    messages=[
        SystemMessage(content="You are a helpful assistant."),
        UserMessage(content="Summarize the key benefits of Azure AI Foundry.")
    ],
    model="llama-3-1-70b-instruct",
    max_tokens=500,
    temperature=0.7
)
print(response.choices[0].message.content)

# Streaming
stream = client.complete(
    messages=[UserMessage(content="Explain RAG in detail.")],
    model="llama-3-1-70b-instruct",
    stream=True
)
for event in stream:
    if event.choices:
        print(event.choices[0].delta.content or "", end="")
```
