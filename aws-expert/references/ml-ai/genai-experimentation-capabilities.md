# Generative AI & Experimentation — Capabilities Reference
For CLI commands, see [genai-experimentation-cli.md](genai-experimentation-cli.md).

## Amazon Nova Act

**Purpose**: AI agent service for building and deploying fleets of agents that automate production browser-based UI workflows; combines natural language task instructions with Python code for complex, multi-step automation at scale.

### Core Concepts

| Concept | Description |
|---|---|
| **Act** | A natural language task instruction passed to the model via the `nova.act()` call; the model executes the task in the browser |
| **Step** | One observe-and-act cycle: the model takes a screenshot, reasons about the current page state, and performs one action |
| **Session** | A browser/API client instance containing a sequence of `act()` calls; maintains browser state across steps |
| **Workflow** | End-to-end task definition combining `act()` statements, Python logic, and conditionals |
| **Workflow run** | A single invocation of a workflow; tracks begin/end times, step traces, and result output |
| **Escalation** | When the agent cannot complete a task with sufficient confidence, it surfaces the task to a human reviewer |

### Nova Act SDK

The Python SDK (`nova-act`) is the primary development interface:

```python
from nova_act import NovaAct

# Basic session with API key (development)
with NovaAct(starting_page="https://example.com") as nova:
    nova.act("search for 'rubber duck debugging'")
    nova.act("click the first result")
    result = nova.act("extract the page title and first paragraph")
    print(result.response)

# Workflow with conditional logic
with NovaAct(starting_page="https://my-app.example.com/login") as nova:
    nova.act("log in with username 'admin' and password from environment")
    for item in items_to_process:
        nova.act(f"navigate to the orders page and find order {item['id']}")
        nova.act(f"update the status to 'Shipped' and save")
```

### Authentication Modes

| Mode | Use Case |
|---|---|
| **API key** | Local development and prototyping; quick setup |
| **AWS IAM** | Production deployments; integrates with IAM roles and policies |

### Deployment Path

```
Playground (web) → Local IDE (VS Code / Cursor / Kiro extension)
→ CDK deployment → AWS Console monitoring + workflow traces
```

### Key Features

- **Custom foundation model**: Nova Act uses a purpose-built model trained specifically for browser interaction, not a general-purpose LLM
- **Vertical integration**: Model, browser runtime, and infrastructure are co-designed for reliability
- **Natural language + Python**: Combine `act()` calls with standard Python control flow for complex workflows
- **Human escalation**: Configurable confidence thresholds trigger human-in-the-loop review
- **Built-in observability**: Workflow runs, step-by-step traces, and performance metrics in AWS Console
- **MCP tool integration**: Connect agents to external APIs and data sources via remote MCP servers
- **Strand Agents compatibility**: Compose Nova Act agents within multi-agent orchestration frameworks

### Common Use Cases

| Use Case | Example Pattern |
|---|---|
| **Data entry** | CRM updates, ERP task entry, form population from structured data |
| **Data extraction** | Web scraping, competitive intelligence, dashboard monitoring and export |
| **E-commerce automation** | Checkout flows, order tracking, inventory checks |
| **Web QA testing** | Automated user-journey validation, regression test execution |
| **Back-office automation** | Invoice processing, account reconciliation, report generation |

### Availability

- Generally Available (GA) since 2025
- Region: US East (N. Virginia) at launch
- Access: AWS Management Console, Nova Act SDK (Python), IDE extensions

---

## Amazon Bedrock AgentCore

**Purpose**: Fully managed platform for deploying, operating, and scaling production AI agents built with any framework (LangGraph, Strand, AutoGen, custom) — providing runtime isolation, tool connectivity, memory, identity, policy enforcement, and quality monitoring without infrastructure management.

### Core Components

| Component | Description |
|---|---|
| **AgentCore Runtime** | Managed execution environment for agents; complete session isolation; supports long-running workloads up to 8 hours; pay-per-use billing |
| **AgentCore Gateway** | Transforms existing REST APIs, GraphQL endpoints, and Lambda functions into agent-compatible tools; semantic tool discovery via natural language search |
| **AgentCore Memory** | Persistent context store across conversations; short-term (session) and long-term (cross-session) memory; agents learn from past interactions |
| **AgentCore Identity** | Secure agent access to AWS services and third-party APIs; native integration with corporate identity providers (Okta, Azure AD) |
| **AgentCore Policy Engine** | Real-time guardrails on agent actions; define boundaries in natural language, automatically converted to Cedar policy rules |
| **AgentCore Evaluations** | Continuous quality monitoring; sample and score live agent interactions against custom criteria; detect regressions |

### Architecture

```
Agent code (any framework) → AgentCore Runtime (session-isolated container)
├── AgentCore Gateway → (REST APIs / Lambda tools / MCP servers)
├── AgentCore Memory → (session context + long-term knowledge)
├── AgentCore Identity → (IAM / IdP / OAuth tokens)
├── AgentCore Policy Engine → (Cedar rules / guardrails)
└── AgentCore Evaluations → (live quality scoring + CloudWatch)
```

### Key Differentiators vs Bedrock Agents

| Dimension | Bedrock Agents | Bedrock AgentCore |
|---|---|---|
| **Framework** | AWS-proprietary orchestration | Any framework (LangGraph, Strand, AutoGen, etc.) |
| **Model** | Bedrock-hosted FMs only | Any model (Bedrock, SageMaker, external) |
| **Session duration** | Shorter, conversational | Up to 8 hours for complex agentic workflows |
| **Tool definition** | OpenAPI schema or Lambda | Gateway auto-transforms existing APIs |
| **Policy enforcement** | Guardrails (content/topic) | Cedar-based action policies + Guardrails |
| **Target user** | Builders using AWS orchestration | Teams with existing agent code needing production hosting |

### Framework Integration Examples

```python
# LangGraph agent deployed to AgentCore Runtime
from langgraph.graph import StateGraph
from bedrock_agentcore import AgentCoreRuntime

# Build your agent graph using LangGraph
graph = StateGraph(MyAgentState)
graph.add_node("planner", planner_node)
graph.add_node("executor", executor_node)
# ...

# Wrap and deploy to AgentCore
runtime = AgentCoreRuntime()
runtime.deploy(graph.compile(), name="my-production-agent")
```

### Key Features

- **Framework agnostic**: Deploy LangGraph, Strand Agents, AutoGen, or fully custom agent code
- **Session isolation**: Each agent invocation runs in an isolated container; no state leakage between sessions
- **Long-running sessions**: Support for complex workflows requiring hours of execution (e.g., research agents, workflow automation)
- **Semantic tool discovery**: AgentCore Gateway enables agents to find relevant tools by semantic search rather than hard-coded tool lists
- **VPC + PrivateLink**: Enterprise security with private connectivity to internal APIs and AWS services
- **Live evaluation**: Continuously sample and score agent outputs against custom rubrics without manual review overhead

### Use Case Patterns

| Pattern | Components Used |
|---|---|
| Research and synthesis agent | Runtime + Gateway (web APIs) + Memory (prior research) |
| Customer service agent | Runtime + Identity (CRM auth) + Policy Engine (scope limits) |
| Code review agent | Runtime + Gateway (GitHub API) + Evaluations (quality scoring) |
| Long-running data pipeline agent | Runtime (8h session) + Gateway (Lambda tools) + Memory |

---

## Amazon PartyRock

**Purpose**: Code-free, browser-based generative AI app builder (playground) powered by Amazon Bedrock; enables anyone — including non-developers — to build, share, and remix AI-powered applications using foundation models without writing code.

### Core Concepts

| Concept | Description |
|---|---|
| **App** | A named collection of widgets arranged on a canvas that defines a generative AI application |
| **Widget** | A building block in an app; each widget has a type and is connected to inputs/outputs of other widgets |
| **Prompt widget** | Calls a foundation model with a prompt template that can reference other widgets as dynamic variables |
| **Text input widget** | User-facing text field; provides input values to prompt widgets |
| **File upload widget** | Allows users to upload images or documents as input to multimodal prompt widgets |
| **Image generation widget** | Generates an image from a text prompt using a Bedrock image generation model |
| **Chatbot widget** | Interactive multi-turn conversational interface backed by a Bedrock FM |
| **Remix** | Copy a public app and modify it — the primary collaboration mechanism |

### Widget Connectivity

Widgets communicate by referencing each other in prompt templates:

```
[Text Input: "Topic"] → [Prompt Widget: "Write a blog post about @{Topic}"] → [Output display]
[Chatbot Widget]: uses @{Topic} as context in its system prompt
```

### How to Build an App

1. Go to partyrock.aws and sign in (no AWS account required for basic use)
2. Describe the app you want to build in plain English — PartyRock auto-generates an initial widget layout
3. Add, remove, and reconfigure widgets from the palette
4. Connect widgets by referencing them in prompt templates with `@{WidgetName}`
5. Choose a foundation model for each prompt/chatbot widget
6. Test with your own inputs
7. Share publicly (generates a shareable URL) or keep private

### Foundation Models Available

PartyRock provides access to a curated subset of Amazon Bedrock's foundation models, including models from Anthropic (Claude), Amazon (Nova, Titan), and others — without needing to configure IAM or manage API access.

### Key Features

- **No AWS account required**: Sign in with Amazon, Google, or Apple ID for personal use
- **Auto-layout from description**: Describe your app idea in natural language; PartyRock creates a starting layout
- **Multimodal support**: File upload and image generation widgets for visual workflows
- **Public app gallery**: Browse and remix community-created apps
- **Snapshot sharing**: Share a read-only snapshot of an app and its current outputs
- **Bedrock relationship**: PartyRock is a front-end consumer of Amazon Bedrock; production apps should be built directly on Bedrock APIs

### Limitations

| Limitation | Details |
|---|---|
| **No custom data sources** | Cannot connect to private knowledge bases or S3 data (use Bedrock Knowledge Bases for RAG) |
| **No API access** | PartyRock apps cannot be invoked programmatically; console-only |
| **Rate limits** | Free tier has usage limits per session; heavy users should move to Bedrock directly |
| **No persistence** | Apps do not maintain state between sessions beyond the widget configuration |

### Use Cases

| Use Case | Example |
|---|---|
| Rapid prototyping | Validate a generative AI concept before building a production Bedrock app |
| Demos and presentations | Build interactive AI demos without deploying infrastructure |
| Education | Learn prompt engineering and FM behavior interactively |
| Content workflows | Draft-and-refine loops for marketing copy, emails, and social posts |
| Internal tools (non-production) | Quick productivity tools for team use with shared app URLs |
