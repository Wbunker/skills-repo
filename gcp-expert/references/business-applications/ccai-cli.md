# Contact Center AI (CCAI) — CLI Reference

## Enable CCAI APIs

```bash
# Enable Dialogflow CX API
gcloud services enable dialogflow.googleapis.com --project=my-project

# Enable CCAI Insights
gcloud services enable contactcenterinsights.googleapis.com --project=my-project

# Enable Speech-to-Text (used internally by CCAI)
gcloud services enable speech.googleapis.com --project=my-project

# Verify enabled
gcloud services list --enabled \
  --filter="name:(dialogflow OR contactcenter OR speech)" \
  --project=my-project
```

---

## Dialogflow CX — Agents

```bash
# Create a Dialogflow CX agent
gcloud dialogflow cx agents create \
  --display-name="Customer Support Agent" \
  --default-language-code=en \
  --time-zone="America/New_York" \
  --location=us-central1 \
  --project=my-project

# List all CX agents
gcloud dialogflow cx agents list \
  --location=us-central1 \
  --project=my-project \
  --format="table(name,displayName,defaultLanguageCode,timeZone)"

# Describe an agent
gcloud dialogflow cx agents describe AGENT_ID \
  --location=us-central1 \
  --project=my-project

# Update agent display name
gcloud dialogflow cx agents update AGENT_ID \
  --display-name="Updated Agent Name" \
  --location=us-central1 \
  --project=my-project

# Export agent (download agent config as blob for backup/migration)
gcloud dialogflow cx agents export AGENT_ID \
  --agent-uri=gs://my-bucket/agent-export-$(date +%Y%m%d).blob \
  --location=us-central1 \
  --project=my-project

# Restore agent from export
gcloud dialogflow cx agents restore AGENT_ID \
  --agent-uri=gs://my-bucket/agent-export-20250115.blob \
  --location=us-central1 \
  --project=my-project

# Delete an agent
gcloud dialogflow cx agents delete AGENT_ID \
  --location=us-central1 \
  --project=my-project
```

---

## Dialogflow CX — Flows

```bash
# List flows in an agent
gcloud dialogflow cx agents flows list \
  --agent=AGENT_ID \
  --location=us-central1 \
  --project=my-project \
  --format="table(name,displayName)"

# Describe a flow
gcloud dialogflow cx agents flows describe FLOW_ID \
  --agent=AGENT_ID \
  --location=us-central1 \
  --project=my-project

# Train a flow (trigger NLU training after making changes)
gcloud dialogflow cx agents flows train FLOW_ID \
  --agent=AGENT_ID \
  --location=us-central1 \
  --project=my-project
```

---

## Dialogflow CX — Pages

```bash
# List pages in a flow
gcloud dialogflow cx agents flows pages list \
  --agent=AGENT_ID \
  --flow=FLOW_ID \
  --location=us-central1 \
  --project=my-project \
  --format="table(name,displayName)"

# Describe a page
gcloud dialogflow cx agents flows pages describe PAGE_ID \
  --agent=AGENT_ID \
  --flow=FLOW_ID \
  --location=us-central1 \
  --project=my-project
```

---

## Dialogflow CX — Intents

```bash
# List intents in an agent
gcloud dialogflow cx agents intents list \
  --agent=AGENT_ID \
  --location=us-central1 \
  --project=my-project \
  --format="table(name,displayName,isFallback)"

# Describe an intent (shows training phrases and parameters)
gcloud dialogflow cx agents intents describe INTENT_ID \
  --agent=AGENT_ID \
  --location=us-central1 \
  --project=my-project

# Export intents to a file (for bulk editing)
gcloud dialogflow cx agents intents export \
  --agent=AGENT_ID \
  --location=us-central1 \
  --intents-uri=gs://my-bucket/intents-export.json \
  --project=my-project

# Import intents from file (bulk import after editing)
gcloud dialogflow cx agents intents import \
  --agent=AGENT_ID \
  --location=us-central1 \
  --intents-uri=gs://my-bucket/intents-export.json \
  --merge-option=REPLACE \
  --project=my-project
```

---

## Dialogflow CX — Versions and Environments

```bash
# Create a version of the Default Start Flow (snapshot)
gcloud dialogflow cx agents flows versions create \
  --agent=AGENT_ID \
  --flow=FLOW_ID \
  --display-name="v1.2 - Billing update" \
  --location=us-central1 \
  --project=my-project

# List versions of a flow
gcloud dialogflow cx agents flows versions list \
  --agent=AGENT_ID \
  --flow=FLOW_ID \
  --location=us-central1 \
  --project=my-project \
  --format="table(name,displayName,state,createTime)"

# List environments
gcloud dialogflow cx agents environments list \
  --agent=AGENT_ID \
  --location=us-central1 \
  --project=my-project \
  --format="table(name,displayName)"

# Create an environment
gcloud dialogflow cx agents environments create \
  --agent=AGENT_ID \
  --display-name="Production" \
  --version-configs=flow=FLOW_ID,version=VERSION_ID \
  --location=us-central1 \
  --project=my-project

# Deploy a version to an environment (update environment to new version)
gcloud dialogflow cx agents environments update ENVIRONMENT_ID \
  --agent=AGENT_ID \
  --display-name="Production" \
  --version-configs=flow=FLOW_ID,version=NEW_VERSION_ID \
  --location=us-central1 \
  --project=my-project

# Describe an environment
gcloud dialogflow cx agents environments describe ENVIRONMENT_ID \
  --agent=AGENT_ID \
  --location=us-central1 \
  --project=my-project

# List deployments for an environment (deployment history)
gcloud dialogflow cx agents environments deployments list \
  --agent=AGENT_ID \
  --environment=ENVIRONMENT_ID \
  --location=us-central1 \
  --project=my-project
```

---

## Dialogflow ES — Agents (Legacy)

```bash
# Create a Dialogflow ES agent (project-level; one ES agent per project)
gcloud dialogflow es agents set-by-example \
  --project=my-project
# Note: ES agent creation is primarily done via Console or REST API

# Get ES agent details
gcloud dialogflow es agents describe \
  --project=my-project

# Train the ES agent
gcloud dialogflow es agents train \
  --project=my-project

# Export ES agent (download as zip to GCS)
gcloud dialogflow es agents export \
  --destination=gs://my-bucket/es-agent-export.zip \
  --project=my-project

# Restore ES agent from zip
gcloud dialogflow es agents restore \
  --source=gs://my-bucket/es-agent-export.zip \
  --project=my-project

# List ES intents
gcloud dialogflow es intents list \
  --project=my-project \
  --format="table(name,displayName,isFallback)"

# List ES entity types
gcloud dialogflow es entity-types list \
  --project=my-project \
  --format="table(name,displayName,kind)"
```

---

## CCAI Insights

```bash
# Enable Contact Center Insights API
gcloud services enable contactcenterinsights.googleapis.com --project=my-project

# Create a conversation (upload transcript for analysis)
gcloud contact-center-insights conversations create \
  --location=us-central1 \
  --medium=PHONE_CALL \
  --duration=3600s \
  --start-time=2025-01-15T14:00:00Z \
  --call-metadata-agent-channel=1 \
  --call-metadata-customer-channel=2 \
  --transcript-uri=gs://my-bucket/transcripts/call-001.json \
  --project=my-project

# List conversations
gcloud contact-center-insights conversations list \
  --location=us-central1 \
  --project=my-project \
  --format="table(name,medium,duration,createTime)"

# Analyze a conversation (run NLP analysis)
gcloud contact-center-insights conversations analyze \
  CONVERSATION_ID \
  --location=us-central1 \
  --project=my-project

# Describe a conversation (shows sentiment, topics, entities)
gcloud contact-center-insights conversations describe \
  CONVERSATION_ID \
  --location=us-central1 \
  --project=my-project

# List issue models
gcloud contact-center-insights issue-models list \
  --location=us-central1 \
  --project=my-project \
  --format="table(name,displayName,state,issueCount)"

# Describe an issue model
gcloud contact-center-insights issue-models describe ISSUE_MODEL_ID \
  --location=us-central1 \
  --project=my-project

# Export insights data to BigQuery
gcloud contact-center-insights conversations export \
  --location=us-central1 \
  --bigquery-table=my-project.ccai_insights.conversations \
  --filter="medium=PHONE_CALL" \
  --project=my-project

# Delete a conversation
gcloud contact-center-insights conversations delete CONVERSATION_ID \
  --location=us-central1 \
  --project=my-project
```

---

## Notes on Dialogflow CX vs CLI Usage

Most Dialogflow CX operations in production are performed via:
1. **Dialogflow CX Console** (dialogflow.cloud.google.com) — primary authoring tool
2. **Dialogflow CX REST API** or **gRPC API** — for programmatic agent building and CI/CD
3. **Dialogflow CX client libraries** (Python, Node.js, Java, Go) — for webhook fulfillment

The `gcloud dialogflow cx` commands are useful for:
- CI/CD pipelines (export → modify → import → train → deploy)
- Backup and disaster recovery (export agent regularly)
- Environment promotion (staging → production version promotion)
- Bulk intent/entity management
