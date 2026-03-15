# AWS Conversation & Recommendation Services — Capabilities Reference
For CLI commands, see [conversation-recommendation-cli.md](conversation-recommendation-cli.md).

## Amazon Lex

**Purpose**: Conversational AI service for building voice and text chatbots powered by the same deep learning technologies as Alexa. V2 is the current version (V1 end-of-support September 2025).

### Core Concepts (V2)

| Concept | Description |
|---|---|
| **Bot** | Top-level resource containing all conversational logic |
| **Bot locale** | Language/region configuration within a bot (e.g., en_US, es_ES); each locale is trained independently |
| **Intent** | Represents a user's goal (e.g., `BookHotel`, `OrderPizza`, `CancelSubscription`) |
| **Utterance** | Example phrases users might say to trigger an intent; used for training |
| **Slot** | A named piece of information to collect (e.g., `CheckInDate`, `RoomType`); has a type (built-in or custom) |
| **Slot type** | Defines valid values for a slot; built-in types include dates, times, numbers, cities; custom types supported |
| **Fulfillment** | What happens when all required slots are filled; Lambda function invocation or response card |
| **Fallback intent** | Triggered when no other intent matches the user input |
| **Bot alias** | Pointer to a bot version for deployment; configure Lambda hook, logging, and sentiment analysis per alias |
| **Bot version** | Immutable snapshot of a bot for production stability |
| **Session** | Conversation context maintained across turns; session attributes available to Lambda |

### Conversation Flow

```
User utterance → Intent classification → Slot elicitation (as needed)
→ Confirmation prompt (optional) → Fulfillment (Lambda or closing response)
```

### Key Features

- **Assisted NLU**: LLM-powered intent classification; requires less training data
- **Conditional branching**: Build complex conversation flows without Lambda code
- **Streaming conversations**: `StartConversation` API for real-time bidirectional audio/text streaming
- **Multi-language**: 75+ locales; custom vocabulary for each
- **Multi-region replication (MRR)**: Deploy bots across regions for high availability
- **Integrations**: Amazon Connect (contact centers), Slack, Twilio, Facebook Messenger, Kik

---

## Amazon Personalize

**Purpose**: Managed ML service for building real-time personalization and recommendation systems using the same technology as Amazon.com; no ML expertise required.

### Key Concepts

| Concept | Description |
|---|---|
| **Dataset group** | Container for all related datasets and models for a single use case |
| **Dataset** | Structured data imported into Personalize: Interactions (required), Users, Items, Action Interactions, Actions |
| **Schema** | Avro-formatted definition of dataset fields and types |
| **Recipe** | Pre-built algorithm for a specific use case (see below) |
| **Solution** | A trained model based on a dataset group and recipe |
| **Solution version** | A specific training run of a solution |
| **Campaign** | Deployed solution version serving real-time recommendations; auto-scaling capacity |
| **Event tracker** | Real-time ingestion endpoint for streaming user interaction events |
| **Recommender** | Simplified deployment for domain-specific use cases (VIDEO_ON_DEMAND, E-COMMERCE) |
| **Filter** | Business rules applied to recommendations (e.g., exclude items already purchased) |

### Recipes

| Category | Recipe | Use Case |
|---|---|---|
| **User personalization** | `aws-user-personalization` | Personalized item recommendations per user |
| **Similar items** | `aws-similar-items` | Items similar to a given item |
| **Related items** | `aws-related-items` | Items frequently interacted with together |
| **Trending** | `aws-trending-now` | Trending items across all users |
| **Reranking** | `aws-personalized-ranking` | Rerank a candidate list of items for a user |
| **User segmentation** | `aws-item-affinity` | Segment users by affinity for an item |

### Real-time vs. Batch Recommendations

- **Real-time**: Call `personalize-runtime:GetRecommendations` or `GetPersonalizedRanking`
- **Batch**: Create a batch inference job; input from S3; output to S3

---

## Amazon Forecast

**Purpose**: Managed time-series forecasting service using ML; produces accurate predictions for demand, inventory, staffing, energy, and financial planning.

### Key Concepts

| Concept | Description |
|---|---|
| **Dataset group** | Container for related datasets for a forecasting domain |
| **Dataset** | Time-series data: Target Time Series (required), Related Time Series, Item Metadata |
| **Domain** | Pre-configured schema template: RETAIL, INVENTORY_PLANNING, EC2_CAPACITY, WORK_FORCE, WEB_TRAFFIC, METRICS, CUSTOM |
| **Predictor** | Trained forecasting model; `CreateAutoPredictor` explores multiple algorithms automatically |
| **Forecast** | Generated predictions from a predictor; query by item ID and time range |
| **What-if analysis** | Simulate forecast changes under different scenarios (e.g., price changes, promotions) |
| **Explainability** | Impact scores showing which features drive forecast values (impact analysis) |
| **Forecast export** | Export forecast data to S3 for downstream analysis |

### AutoPredictor

The recommended approach: `CreateAutoPredictor` automatically selects the best algorithm from:
- ARIMA, ETS, NPTS, Prophet, DeepAR+, CNN-QR

Output is a probabilistic forecast (P10, P50, P90 quantiles by default).

### Query Methods

- **Console / SDK**: `forecastquery:QueryForecast` for item-level point-in-time queries
- **Batch**: Export entire forecast to S3 via `CreateForecastExportJob`

---

## Amazon Kendra

**Purpose**: Intelligent enterprise search service powered by ML; understands natural language queries and returns precise answers (not just keyword matches) from connected document repositories.

### Key Concepts

| Concept | Description |
|---|---|
| **Index** | The search index; Enterprise or Developer edition |
| **Data source** | Connector to a document repository: S3, SharePoint, Salesforce, ServiceNow, RDS, OneDrive, Confluence, Google Drive, and 40+ others |
| **FAQ** | Curated question-answer pairs uploaded directly to the index |
| **Document** | Any indexed item; has title, text content, metadata attributes, and ACL |
| **Access control list (ACL)** | Per-document permissions; Kendra filters results to what the querying user can access |
| **Relevance tuning** | Boost or demote results based on document metadata attributes |
| **Synonyms** | Custom synonym lists to improve recall |

### Query Types

| Type | Description |
|---|---|
| **Factoid** | Questions with a single answer ("Who founded Amazon?") |
| **Descriptive** | Open-ended questions needing a passage ("How do I reset my password?") |
| **Keyword** | Traditional keyword-based search |

### Key Features

- **Featured results**: Pin specific documents to the top for designated queries
- **Incremental sync**: Data source connectors detect changed/deleted documents automatically
- **Kendra GenAI index**: Enhanced retrieval index compatible with Amazon Q Business and Bedrock Knowledge Bases
- **Experience builder**: No-code UI for building search interfaces
- **Query suggestions**: Auto-complete based on past queries
- **Document enrichment**: Ingest-time Lambda function to transform or enrich document content
