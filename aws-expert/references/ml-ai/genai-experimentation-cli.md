# Generative AI & Experimentation — CLI Reference
For capabilities, see [genai-experimentation-capabilities.md](genai-experimentation-capabilities.md).

## Amazon Nova Act

Nova Act is primarily accessed via the Python SDK. CLI-style interaction uses the Nova Act IDE extension or the AWS Console for monitoring. The Python SDK is the canonical interface.

```bash
# --- Install the Nova Act SDK ---
pip install nova-act

# --- Authenticate with API key (development) ---
export NOVA_ACT_API_KEY="your-api-key-here"

# --- Run a basic Nova Act workflow (Python script) ---
python3 - <<'EOF'
from nova_act import NovaAct

with NovaAct(starting_page="https://example.com") as nova:
    nova.act("search for 'AWS re:Invent 2025 keynote'")
    result = nova.act("extract the first search result title and URL")
    print(result.response)
EOF

# --- Run a workflow script ---
python3 my_workflow.py

# --- Example workflow: form automation ---
python3 - <<'EOF'
from nova_act import NovaAct
import json

with NovaAct(
    starting_page="https://mycrm.example.com",
    headless=True               # run without visible browser window
) as nova:
    nova.act("log in with credentials from environment variables")

    with open("leads.json") as f:
        leads = json.load(f)

    for lead in leads:
        nova.act(f"navigate to New Contact form")
        nova.act(f"fill in Name: '{lead['name']}', Email: '{lead['email']}', Company: '{lead['company']}'")
        nova.act("click Save")
        print(f"Created contact: {lead['name']}")
EOF

# --- IAM-based authentication (production) ---
# Assign the instance role or ECS task role the necessary Nova Act permissions
# Then initialize without API key:
python3 - <<'EOF'
from nova_act import NovaAct
import boto3

# Uses IAM role from instance metadata / ECS task role
with NovaAct(
    starting_page="https://my-app.example.com",
    aws_region="us-east-1"
) as nova:
    nova.act("perform the automation task")
EOF

# --- Monitor workflow runs (AWS CLI) ---
# List Nova Act workflow runs (uses bedrock-agent-runtime or nova-act management API)
aws bedrock-agent-runtime list-sessions \
  --agent-id YOUR_NOVA_ACT_AGENT_ID \
  --agent-alias-id ALIAS_ID

# Describe a specific session/workflow run
aws bedrock-agent-runtime get-session \
  --session-id SESSION_ID
```

---

## Amazon Bedrock AgentCore

AgentCore is managed via the `bedrock-agentcore` and `bedrock-agentcore-control` AWS CLI namespaces, plus the standard Bedrock CLI for associated resources.

```bash
# --- AgentCore Runtime: Create a Runtime ---
aws bedrock-agentcore-control create-agent-runtime \
  --name my-production-agent \
  --description "LangGraph-based research agent" \
  --network-configuration '{
    "networkMode": "PUBLIC"
  }' \
  --agent-runtime-artifact '{
    "containerConfiguration": {
      "containerUri": "123456789012.dkr.ecr.us-east-1.amazonaws.com/my-agent:latest"
    }
  }' \
  --role-arn arn:aws:iam::123456789012:role/AgentCoreExecutionRole

aws bedrock-agentcore-control get-agent-runtime \
  --agent-runtime-id RUNTIME_ID

aws bedrock-agentcore-control list-agent-runtimes
aws bedrock-agentcore-control delete-agent-runtime --agent-runtime-id RUNTIME_ID

# --- Invoke an Agent Runtime ---
aws bedrock-agentcore invoke-agent-runtime \
  --agent-runtime-endpoint-id ENDPOINT_ID \
  --session-id "session-$(date +%s)" \
  --request '{"input": "Research the latest developments in quantum computing and summarize key findings"}'

# --- AgentCore Gateway: Register Tool Sources ---
# Register a Lambda function as an agent tool
aws bedrock-agentcore-control create-gateway \
  --name internal-tools-gateway \
  --description "Gateway exposing internal business APIs to agents" \
  --role-arn arn:aws:iam::123456789012:role/AgentCoreGatewayRole

aws bedrock-agentcore-control create-gateway-target \
  --gateway-identifier GATEWAY_ID \
  --name crm-api-tool \
  --description "CRM API for customer lookup and updates" \
  --endpoint-configuration '{
    "lambda": {
      "lambdaArn": "arn:aws:lambda:us-east-1:123456789012:function:crm-api-handler",
      "toolSchema": {
        "inlinePayload": [
          {
            "name": "get_customer",
            "description": "Look up a customer by email or customer ID",
            "inputSchema": {
              "json": {
                "type": "object",
                "properties": {
                  "identifier": {"type": "string", "description": "Customer email or ID"}
                },
                "required": ["identifier"]
              }
            }
          }
        ]
      }
    }
  }' \
  --credential-configuration '{
    "credentialProviderType": "GATEWAY_IAM_ROLE"
  }'

aws bedrock-agentcore-control list-gateway-targets --gateway-identifier GATEWAY_ID

# List available tools (semantic search)
aws bedrock-agentcore list-gateway-targets \
  --gateway-identifier GATEWAY_ID \
  --search-query "customer information lookup"

# --- AgentCore Memory: Manage Memory Stores ---
aws bedrock-agentcore-control create-memory \
  --name agent-memory-store \
  --description "Long-term memory for customer service agent" \
  --memory-execution-role-arn arn:aws:iam::123456789012:role/AgentCoreMemoryRole \
  --event-expiry-duration 90

aws bedrock-agentcore-control get-memory --memory-id MEMORY_ID
aws bedrock-agentcore-control list-memories

# Retrieve memory events for a specific actor
aws bedrock-agentcore retrieve-memory-records \
  --memory-id MEMORY_ID \
  --actor-id "user-12345" \
  --namespace "customer_preferences"

# --- AgentCore Evaluations ---
aws bedrock-agentcore-control create-agent-runtime-evaluation \
  --name quality-evaluation-jan-2025 \
  --agent-runtime-id RUNTIME_ID \
  --evaluation-criteria '{
    "criteria": [
      {
        "name": "task_completion",
        "description": "Did the agent complete the requested task?",
        "scale": {"min": 1, "max": 5}
      },
      {
        "name": "accuracy",
        "description": "Was the agent output factually accurate?",
        "scale": {"min": 1, "max": 5}
      }
    ]
  }' \
  --sampling-rate 0.1

aws bedrock-agentcore-control list-agent-runtime-evaluations \
  --agent-runtime-id RUNTIME_ID

# --- CDK Deployment Pattern ---
# AgentCore can also be deployed via CDK (TypeScript/Python):
cat <<'CDKEOF'
// CDK snippet (TypeScript) — deploy a containerized agent to AgentCore
import * as bedrock from '@aws-cdk/aws-bedrock-alpha';

const agentRuntime = new bedrock.AgentRuntime(this, 'MyAgent', {
  agentRuntimeName: 'my-production-agent',
  networkMode: bedrock.NetworkMode.PUBLIC,
  agentRuntimeArtifact: bedrock.AgentRuntimeArtifact.fromEcr(myEcrRepo, 'latest'),
  executionRole: agentRole,
});
CDKEOF

# Note: CLI namespaces for AgentCore (bedrock-agentcore, bedrock-agentcore-control)
# are available in recent AWS CLI versions. Check availability:
aws bedrock-agentcore-control help
aws bedrock-agentcore help
```

---

## Amazon PartyRock

PartyRock is a browser-only service at partyrock.aws — there is no AWS CLI or API access. The following notes cover management via the web console and related Bedrock CLI operations for teams transitioning from PartyRock to production Bedrock apps.

```bash
# PartyRock has no CLI interface.
# All operations are performed at: https://partyrock.aws

# -----------------------------------------------------------------
# Transitioning a PartyRock prototype to a Bedrock production app:
# -----------------------------------------------------------------

# 1. Identify the models used in your PartyRock app, then invoke them directly:
aws bedrock-runtime converse \
  --model-id anthropic.claude-3-5-sonnet-20241022-v2:0 \
  --messages '[{
    "role": "user",
    "content": [{"text": "Write a blog post about renewable energy"}]
  }]'

# 2. Replicate a chatbot widget as a Bedrock Converse API call:
aws bedrock-runtime converse \
  --model-id amazon.nova-pro-v1:0 \
  --system '[{"text": "You are a helpful writing assistant. Context: the user is writing about @{topic}"}]' \
  --messages '[
    {"role": "user", "content": [{"text": "Help me write an introduction"}]},
    {"role": "assistant", "content": [{"text": "Here is a draft introduction..."}]},
    {"role": "user", "content": [{"text": "Make it more engaging"}]}
  ]'

# 3. Replicate an image generation widget:
aws bedrock-runtime invoke-model \
  --model-id amazon.nova-canvas-v1:0 \
  --body '{"taskType":"TEXT_IMAGE","textToImageParams":{"text":"A futuristic city powered by solar energy, photorealistic"},"imageGenerationConfig":{"numberOfImages":1,"height":1024,"width":1024,"quality":"premium"}}' \
  --cli-binary-format raw-in-base64-out \
  output-image.json

# 4. List available Bedrock models (to match what PartyRock offers):
aws bedrock list-foundation-models \
  --query 'modelSummaries[?outputModalities[?contains(@,`TEXT`)] && inferenceTypesSupported[?contains(@,`ON_DEMAND`)]].{ModelId:modelId,Provider:providerName}' \
  --output table

# 5. For multi-step prompt chains (replicating connected widgets):
# Use Bedrock Prompt Management to store and version your prompts:
aws bedrock create-prompt \
  --name blog-intro-prompt \
  --description "Generates blog introduction from topic" \
  --variants '[{
    "name": "default",
    "templateType": "TEXT",
    "templateConfiguration": {
      "text": {
        "text": "Write an engaging introduction for a blog post about {{topic}}. Keep it under 150 words.",
        "inputVariables": [{"name": "topic"}]
      }
    },
    "modelId": "amazon.nova-pro-v1:0",
    "inferenceConfiguration": {
      "text": {"maxTokens": 256, "temperature": 0.7}
    }
  }]'

# Invoke a saved prompt:
aws bedrock-runtime converse-with-prompt \
  --prompt-identifier arn:aws:bedrock:us-east-1:123456789012:prompt/PROMPT_ID:1 \
  --prompt-variables '{"topic":{"text":"renewable energy"}}'
```
