# ML & AI Domain Index

This domain covers Azure's machine learning, generative AI, and cognitive services portfolio. Load the relevant namespace files based on the user's specific workload.

## Namespace Index

| Namespace | Capabilities | CLI | Load when... |
|-----------|-------------|-----|--------------|
| Azure OpenAI Service | ml-ai/azure-openai-capabilities.md | ml-ai/azure-openai-cli.md | GPT-4o, o1, o3, DALL-E, Whisper, text-embedding models; deployments, quotas, fine-tuning, content filtering, Assistants API, Azure OpenAI Studio |
| Azure Machine Learning | ml-ai/azure-ml-capabilities.md | ml-ai/azure-ml-cli.md | ML workspaces, compute clusters/instances, pipelines, AutoML, MLflow, model registry, managed online/batch endpoints, responsible AI |
| Azure AI Foundry | ml-ai/ai-foundry-capabilities.md | ml-ai/ai-foundry-cli.md | AI Foundry portal (hub+project model), prompt flow, model catalog, AI safety/evaluation, agent frameworks, Grounding with Bing |
| Azure AI Services | ml-ai/ai-services-capabilities.md | ml-ai/ai-services-cli.md | Vision, Speech, Language (CLU, NER, sentiment, summarization), Document Intelligence (Form Recognizer), Translator, Face API, Anomaly Detector, Content Safety, Health Insights |

## Domain Overview

The Azure ML & AI portfolio spans:

- **Generative AI (Azure OpenAI Service / AI Foundry)**: Enterprise-grade access to OpenAI models with Azure security, compliance, and private networking. Azure AI Foundry is the converged platform replacing Azure OpenAI Studio.
- **Classical ML (Azure Machine Learning)**: Full MLOps lifecycle — training, experiment tracking, model registry, deployment, responsible AI tooling.
- **Pre-built AI (Azure AI Services)**: Pay-per-transaction cognitive APIs for vision, speech, language, and document understanding — no ML expertise required.

## Key Decision Points

| Scenario | Recommended Service |
|----------|-------------------|
| Use GPT-4o / o1 / DALL-E in production | Azure OpenAI Service |
| Build custom ML models with MLOps | Azure Machine Learning |
| Build GenAI apps with prompt flow, model catalog | Azure AI Foundry |
| Add OCR, NER, speech-to-text to an app | Azure AI Services |
| RAG application with enterprise data | Azure OpenAI + Azure AI Search |
| Fine-tune a foundation model | Azure OpenAI (GPT-4o mini) or Azure ML |
