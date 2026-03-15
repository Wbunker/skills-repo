# AWS Amazon Bedrock — CLI Reference
For service concepts, see [bedrock-capabilities.md](bedrock-capabilities.md).

## Amazon Bedrock

```bash
# --- Foundation Models ---
aws bedrock list-foundation-models
aws bedrock list-foundation-models --by-provider anthropic
aws bedrock list-foundation-models --by-output-modality TEXT
aws bedrock get-foundation-model --model-identifier anthropic.claude-3-5-sonnet-20241022-v2:0
aws bedrock get-foundation-model-availability --model-id amazon.nova-pro-v1:0

# --- Guardrails ---
aws bedrock create-guardrail \
  --name my-guardrail \
  --content-policy-config '{"filtersConfig":[{"type":"HATE","inputStrength":"HIGH","outputStrength":"HIGH"},{"type":"VIOLENCE","inputStrength":"MEDIUM","outputStrength":"MEDIUM"}]}' \
  --sensitive-information-policy-config '{"piiEntitiesConfig":[{"type":"EMAIL","action":"BLOCK"},{"type":"SSN","action":"ANONYMIZE"}]}' \
  --topic-policy-config '{"topicsConfig":[{"name":"competitor-products","definition":"Questions about competitor offerings","type":"DENY"}]}' \
  --blocked-input-messaging "I cannot respond to that request." \
  --blocked-outputs-messaging "The response was blocked."

aws bedrock create-guardrail-version --guardrail-identifier GUARDRAIL_ID
aws bedrock get-guardrail --guardrail-identifier GUARDRAIL_ID --guardrail-version DRAFT
aws bedrock list-guardrails
aws bedrock update-guardrail --guardrail-identifier GUARDRAIL_ID --name updated-name
aws bedrock delete-guardrail --guardrail-identifier GUARDRAIL_ID

# --- Model Customization (Fine-tuning / Continued Pre-training) ---
aws bedrock create-model-customization-job \
  --job-name my-finetune-job \
  --custom-model-name my-fine-tuned-model \
  --role-arn arn:aws:iam::123456789012:role/BedrockCustomizationRole \
  --base-model-identifier amazon.titan-text-express-v1 \
  --customization-type FINE_TUNING \
  --training-data-config '{"s3Uri":"s3://my-bucket/train/"}' \
  --output-data-config '{"s3Uri":"s3://my-bucket/output/"}' \
  --hyper-parameters '{"epochCount":"3","batchSize":"32","learningRate":"0.00005"}'

aws bedrock get-model-customization-job --job-identifier JOB_ID
aws bedrock list-model-customization-jobs
aws bedrock stop-model-customization-job --job-identifier JOB_ID
aws bedrock list-custom-models
aws bedrock get-custom-model --model-identifier my-fine-tuned-model

# --- Model Evaluation ---
aws bedrock create-evaluation-job \
  --job-name my-eval-job \
  --role-arn arn:aws:iam::123456789012:role/BedrockEvalRole \
  --evaluation-config '{"automated":{"datasetMetricConfigs":[{"taskType":"Summarization","dataset":{"name":"cnn_dailymail"},"metricNames":["Accuracy"]}]}}' \
  --inference-config '{"models":[{"bedrockModel":{"modelIdentifier":"anthropic.claude-3-haiku-20240307-v1:0","inferenceParams":"{\"max_tokens\":512}"}}]}' \
  --output-data-config '{"s3Uri":"s3://my-bucket/eval-output/"}'

aws bedrock get-evaluation-job --job-identifier JOB_ID
aws bedrock list-evaluation-jobs
aws bedrock stop-evaluation-job --job-identifier JOB_ID

# --- Provisioned Throughput ---
aws bedrock create-provisioned-model-throughput \
  --model-units 1 \
  --provisioned-model-name my-provisioned \
  --model-id anthropic.claude-3-haiku-20240307-v1:0
aws bedrock get-provisioned-model-throughput --provisioned-model-id PROVISIONED_ID
aws bedrock list-provisioned-model-throughputs
aws bedrock delete-provisioned-model-throughput --provisioned-model-id PROVISIONED_ID

# --- Batch Inference ---
aws bedrock create-model-invocation-job \
  --job-name batch-job \
  --role-arn arn:aws:iam::123456789012:role/BedrockBatchRole \
  --model-id anthropic.claude-3-haiku-20240307-v1:0 \
  --input-data-config '{"s3InputDataConfig":{"s3Uri":"s3://my-bucket/inputs/","s3InputFormat":"JSONL"}}' \
  --output-data-config '{"s3OutputDataConfig":{"s3Uri":"s3://my-bucket/outputs/"}}'
aws bedrock get-model-invocation-job --job-identifier JOB_ID
aws bedrock list-model-invocation-jobs

# --- Invocation Logging ---
aws bedrock put-model-invocation-logging-configuration \
  --logging-config '{"cloudWatchConfig":{"logGroupName":"/aws/bedrock/invocations","roleArn":"arn:aws:iam::123456789012:role/BedrockLoggingRole"},"s3Config":{"bucketName":"my-bedrock-logs","keyPrefix":"bedrock-logs/"}}'
aws bedrock get-model-invocation-logging-configuration

# --- Inference Profiles (cross-region) ---
aws bedrock create-inference-profile \
  --inference-profile-name my-cross-region-profile \
  --model-source '{"copyFrom":"arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-3-5-sonnet-20241022-v2:0"}'
aws bedrock list-inference-profiles
aws bedrock get-inference-profile --inference-profile-identifier PROFILE_ID

# --- Tagging ---
aws bedrock list-tags-for-resource --resource-arn RESOURCE_ARN
aws bedrock tag-resource --resource-arn RESOURCE_ARN --tags key=env,value=prod
aws bedrock untag-resource --resource-arn RESOURCE_ARN --tag-keys env
```

---

## Amazon Bedrock Runtime

```bash
# --- InvokeModel (model-specific request bodies) ---

# Anthropic Claude
aws bedrock-runtime invoke-model \
  --model-id anthropic.claude-3-5-sonnet-20241022-v2:0 \
  --body '{"anthropic_version":"bedrock-2023-05-31","max_tokens":1024,"messages":[{"role":"user","content":"Explain quantum computing in simple terms."}]}' \
  --cli-binary-format raw-in-base64-out \
  output.json
cat output.json

# Amazon Nova
aws bedrock-runtime invoke-model \
  --model-id amazon.nova-pro-v1:0 \
  --body '{"messages":[{"role":"user","content":[{"text":"What are the key features of Amazon Nova?"}]}],"inferenceConfig":{"maxTokens":512,"temperature":0.7}}' \
  --cli-binary-format raw-in-base64-out \
  output.json

# Meta Llama
aws bedrock-runtime invoke-model \
  --model-id meta.llama3-70b-instruct-v1:0 \
  --body '{"prompt":"<|begin_of_text|><|start_header_id|>user<|end_header_id|>\nExplain the difference between AI and ML.<|eot_id|><|start_header_id|>assistant<|end_header_id|>","max_gen_len":512,"temperature":0.5}' \
  --cli-binary-format raw-in-base64-out \
  output.json

# Mistral
aws bedrock-runtime invoke-model \
  --model-id mistral.mistral-large-2402-v1:0 \
  --body '{"prompt":"<s>[INST] Write a haiku about cloud computing. [/INST]","max_tokens":100,"temperature":0.7}' \
  --cli-binary-format raw-in-base64-out \
  output.json

# Amazon Titan Text
aws bedrock-runtime invoke-model \
  --model-id amazon.titan-text-express-v1 \
  --body '{"inputText":"Summarize the benefits of serverless computing.","textGenerationConfig":{"maxTokenCount":512,"temperature":0.7,"topP":0.9}}' \
  --cli-binary-format raw-in-base64-out \
  output.json

# --- Converse API (unified, model-agnostic) ---
aws bedrock-runtime converse \
  --model-id anthropic.claude-3-5-sonnet-20241022-v2:0 \
  --messages '[{"role":"user","content":[{"text":"What is the capital of France?"}]}]'

# Converse with system prompt and inference config
aws bedrock-runtime converse \
  --model-id amazon.nova-pro-v1:0 \
  --system '[{"text":"You are a helpful AWS solutions architect."}]' \
  --messages '[{"role":"user","content":[{"text":"What is the best way to architect a highly available web application?"}]}]' \
  --inference-config '{"maxTokens":1024,"temperature":0.7,"topP":0.9}'

# Converse with multi-turn history
aws bedrock-runtime converse \
  --model-id anthropic.claude-3-5-sonnet-20241022-v2:0 \
  --messages '[{"role":"user","content":[{"text":"My name is Alice."}]},{"role":"assistant","content":[{"text":"Nice to meet you, Alice!"}]},{"role":"user","content":[{"text":"What is my name?"}]}]'

# Converse with guardrail
aws bedrock-runtime converse \
  --model-id anthropic.claude-3-5-sonnet-20241022-v2:0 \
  --messages '[{"role":"user","content":[{"text":"Tell me about investing."}]}]' \
  --guardrail-config '{"guardrailIdentifier":"GUARDRAIL_ID","guardrailVersion":"1","trace":"enabled"}'

# Converse with tool use (function calling)
aws bedrock-runtime converse \
  --model-id anthropic.claude-3-5-sonnet-20241022-v2:0 \
  --messages '[{"role":"user","content":[{"text":"What is the weather in Seattle?"}]}]' \
  --tool-config '{"tools":[{"toolSpec":{"name":"get_weather","description":"Get current weather for a city","inputSchema":{"json":{"type":"object","properties":{"city":{"type":"string","description":"City name"}},"required":["city"]}}}}]}'

# Converse Stream (streaming responses)
aws bedrock-runtime converse-stream \
  --model-id anthropic.claude-3-5-sonnet-20241022-v2:0 \
  --messages '[{"role":"user","content":[{"text":"Write a short poem about AWS."}]}]'

# --- Apply Guardrail (standalone, without model invocation) ---
aws bedrock-runtime apply-guardrail \
  --guardrail-identifier GUARDRAIL_ID \
  --guardrail-version 1 \
  --source INPUT \
  --content '[{"text":{"text":"This is the text to evaluate."}}]'

# --- Async Invocation ---
aws bedrock-runtime start-async-invoke \
  --model-id amazon.nova-reel-v1:0 \
  --model-input '{"taskType":"TEXT_VIDEO","textToVideoParams":{"text":"A serene mountain lake at sunset"},"videoGenerationConfig":{"durationSeconds":6,"fps":24,"dimension":"1280x720"}}' \
  --output-data-config '{"s3OutputDataConfig":{"s3Uri":"s3://my-bucket/video-output/"}}'

aws bedrock-runtime get-async-invoke --invocation-arn INVOCATION_ARN
aws bedrock-runtime list-async-invokes

# --- Token Counting ---
aws bedrock-runtime count-tokens \
  --model-id anthropic.claude-3-5-sonnet-20241022-v2:0 \
  --system '[{"text":"You are a helpful assistant."}]' \
  --messages '[{"role":"user","content":[{"text":"Hello, how are you?"}]}]'
```

---

## Amazon Bedrock Agent

```bash
# --- Agents ---
aws bedrock-agent create-agent \
  --agent-name my-agent \
  --agent-resource-role-arn arn:aws:iam::123456789012:role/AmazonBedrockExecutionRoleForAgents \
  --foundation-model anthropic.claude-3-5-sonnet-20241022-v2:0 \
  --instruction "You are a helpful customer service agent for Acme Corp. Help users with orders and returns."

aws bedrock-agent get-agent --agent-id AGENT_ID
aws bedrock-agent list-agents
aws bedrock-agent update-agent \
  --agent-id AGENT_ID \
  --agent-name my-agent \
  --agent-resource-role-arn arn:aws:iam::123456789012:role/AmazonBedrockExecutionRoleForAgents \
  --foundation-model anthropic.claude-3-5-sonnet-20241022-v2:0 \
  --instruction "Updated instructions for the agent."
aws bedrock-agent delete-agent --agent-id AGENT_ID

# Prepare agent (must call before creating alias or testing updates)
aws bedrock-agent prepare-agent --agent-id AGENT_ID

# Create agent alias (for production use)
aws bedrock-agent create-agent-alias \
  --agent-id AGENT_ID \
  --agent-alias-name production \
  --routing-configuration '[{"agentVersion":"1"}]'

# --- Action Groups ---
# Action group with Lambda function
aws bedrock-agent create-agent-action-group \
  --agent-id AGENT_ID \
  --agent-version DRAFT \
  --action-group-name order-management \
  --action-group-executor '{"lambda":"arn:aws:lambda:us-east-1:123456789012:function:OrderManagementFn"}' \
  --api-schema '{"s3":{"s3BucketName":"my-bucket","s3ObjectKey":"openapi/order-api.json"}}'

# Action group with return of control (agent returns to caller instead of invoking Lambda)
aws bedrock-agent create-agent-action-group \
  --agent-id AGENT_ID \
  --agent-version DRAFT \
  --action-group-name user-input-action \
  --action-group-executor '{"customControl":"RETURN_CONTROL"}' \
  --function-schema '{"functions":[{"name":"get_customer_info","description":"Retrieve customer information","parameters":{"customer_id":{"description":"Customer ID","type":"string","required":true}}}]}'

aws bedrock-agent list-agent-action-groups --agent-id AGENT_ID --agent-version DRAFT
aws bedrock-agent get-agent-action-group --agent-id AGENT_ID --agent-version DRAFT --action-group-id AG_ID
aws bedrock-agent delete-agent-action-group --agent-id AGENT_ID --agent-version DRAFT --action-group-id AG_ID

# --- Knowledge Bases ---
# Create a knowledge base with OpenSearch Serverless vector store
aws bedrock-agent create-knowledge-base \
  --name my-knowledge-base \
  --role-arn arn:aws:iam::123456789012:role/AmazonBedrockExecutionRoleForKnowledgeBase \
  --knowledge-base-configuration '{"type":"VECTOR","vectorKnowledgeBaseConfiguration":{"embeddingModelArn":"arn:aws:bedrock:us-east-1::foundation-model/amazon.titan-embed-text-v2:0"}}' \
  --storage-configuration '{"type":"OPENSEARCH_SERVERLESS","opensearchServerlessConfiguration":{"collectionArn":"arn:aws:aoss:us-east-1:123456789012:collection/my-collection","vectorIndexName":"bedrock-knowledge-base-index","fieldMapping":{"vectorField":"embedding","textField":"text","metadataField":"metadata"}}}'

aws bedrock-agent get-knowledge-base --knowledge-base-id KB_ID
aws bedrock-agent list-knowledge-bases
aws bedrock-agent delete-knowledge-base --knowledge-base-id KB_ID

# Associate knowledge base with agent
aws bedrock-agent associate-agent-knowledge-base \
  --agent-id AGENT_ID \
  --agent-version DRAFT \
  --knowledge-base-id KB_ID \
  --description "Product documentation knowledge base" \
  --knowledge-base-state ENABLED

aws bedrock-agent list-agent-knowledge-bases --agent-id AGENT_ID --agent-version DRAFT
aws bedrock-agent disassociate-agent-knowledge-base --agent-id AGENT_ID --agent-version DRAFT --knowledge-base-id KB_ID

# --- Data Sources ---
# Create S3 data source with fixed-size chunking
aws bedrock-agent create-data-source \
  --knowledge-base-id KB_ID \
  --name s3-product-docs \
  --data-source-configuration '{"type":"S3","s3Configuration":{"bucketArn":"arn:aws:s3:::my-docs-bucket","inclusionPrefixes":["products/"]}}' \
  --vector-ingestion-configuration '{"chunkingConfiguration":{"chunkingStrategy":"FIXED_SIZE","fixedSizeChunkingConfiguration":{"maxTokens":512,"overlapPercentage":20}}}'

# Create data source with semantic chunking
aws bedrock-agent create-data-source \
  --knowledge-base-id KB_ID \
  --name s3-docs-semantic \
  --data-source-configuration '{"type":"S3","s3Configuration":{"bucketArn":"arn:aws:s3:::my-docs-bucket"}}' \
  --vector-ingestion-configuration '{"chunkingConfiguration":{"chunkingStrategy":"SEMANTIC","semanticChunkingConfiguration":{"maxTokens":300,"bufferSize":0,"breakpointPercentileThreshold":95}}}'

aws bedrock-agent get-data-source --knowledge-base-id KB_ID --data-source-id DS_ID
aws bedrock-agent list-data-sources --knowledge-base-id KB_ID
aws bedrock-agent delete-data-source --knowledge-base-id KB_ID --data-source-id DS_ID

# --- Ingestion Jobs ---
aws bedrock-agent start-ingestion-job \
  --knowledge-base-id KB_ID \
  --data-source-id DS_ID

aws bedrock-agent get-ingestion-job --knowledge-base-id KB_ID --data-source-id DS_ID --ingestion-job-id JOB_ID
aws bedrock-agent list-ingestion-jobs --knowledge-base-id KB_ID --data-source-id DS_ID

# Ingest documents directly (without crawling S3)
aws bedrock-agent ingest-knowledge-base-documents \
  --knowledge-base-id KB_ID \
  --data-source-id DS_ID \
  --documents '[{"content":{"dataSourceType":"CUSTOM","custom":{"customDocumentIdentifier":{"id":"doc-001"},"sourceType":"IN_LINE","inlineContent":{"type":"TEXT","textContent":{"data":"Product XYZ costs $99 and is available in blue and red."}}}},"metadata":{"type":"IN_LINE_ATTRIBUTE","inlineAttributes":[{"key":"category","value":{"type":"STRING","stringValue":"products"}}]}}]'

# --- Prompts ---
aws bedrock-agent create-prompt \
  --name customer-service-prompt \
  --description "Prompt for customer service agent" \
  --variants '[{"name":"default","templateType":"TEXT","modelId":"anthropic.claude-3-5-sonnet-20241022-v2:0","templateConfiguration":{"text":{"text":"You are a helpful assistant. {{user_input}}","inputVariables":[{"name":"user_input"}]}}}]'

aws bedrock-agent list-prompts
aws bedrock-agent get-prompt --prompt-identifier PROMPT_ID
```

---

## Amazon Bedrock Agent Runtime

```bash
# --- Invoke Agent ---
aws bedrock-agent-runtime invoke-agent \
  --agent-id AGENT_ID \
  --agent-alias-id ALIAS_ID \
  --session-id my-session-$(date +%s) \
  --input-text "I need to return order #12345"

# Invoke agent with session attributes
aws bedrock-agent-runtime invoke-agent \
  --agent-id AGENT_ID \
  --agent-alias-id ALIAS_ID \
  --session-id existing-session-id \
  --input-text "What is the status of my order?" \
  --session-state '{"sessionAttributes":{"customerId":"CUST-001"},"promptSessionAttributes":{"customerTier":"gold"}}'

# --- Knowledge Base Retrieval ---
# Retrieve relevant documents from a knowledge base
aws bedrock-agent-runtime retrieve \
  --knowledge-base-id KB_ID \
  --retrieval-query '{"text":"What are the product warranty terms?"}' \
  --retrieval-configuration '{"vectorSearchConfiguration":{"numberOfResults":5,"overrideSearchType":"SEMANTIC"}}'

# Retrieve with metadata filter
aws bedrock-agent-runtime retrieve \
  --knowledge-base-id KB_ID \
  --retrieval-query '{"text":"laptop specifications"}' \
  --retrieval-configuration '{"vectorSearchConfiguration":{"numberOfResults":3,"filter":{"equals":{"key":"category","value":{"stringValue":"laptops"}}}}}'

# --- Retrieve and Generate (RAG) ---
aws bedrock-agent-runtime retrieve-and-generate \
  --input '{"text":"What is the return policy for electronics?"}' \
  --retrieve-and-generate-configuration '{"type":"KNOWLEDGE_BASE","knowledgeBaseConfiguration":{"knowledgeBaseId":"KB_ID","modelArn":"arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-3-5-sonnet-20241022-v2:0"}}'

# Retrieve and generate with citations and guardrail
aws bedrock-agent-runtime retrieve-and-generate \
  --input '{"text":"Summarize the safety procedures"}' \
  --retrieve-and-generate-configuration '{"type":"KNOWLEDGE_BASE","knowledgeBaseConfiguration":{"knowledgeBaseId":"KB_ID","modelArn":"arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-3-5-sonnet-20241022-v2:0","retrievalConfiguration":{"vectorSearchConfiguration":{"numberOfResults":5}},"generationConfiguration":{"guardrailConfiguration":{"guardrailId":"GUARDRAIL_ID","guardrailVersion":"1"}}}}'

# --- Sessions ---
aws bedrock-agent-runtime create-session \
  --agent-id AGENT_ID \
  --agent-alias-id ALIAS_ID
aws bedrock-agent-runtime get-session --session-id SESSION_ID
aws bedrock-agent-runtime list-sessions
aws bedrock-agent-runtime end-session --session-id SESSION_ID
aws bedrock-agent-runtime delete-session --session-id SESSION_ID

# --- Agent Memory ---
aws bedrock-agent-runtime get-agent-memory \
  --agent-id AGENT_ID \
  --agent-alias-id ALIAS_ID \
  --memory-type SESSION_SUMMARY \
  --memory-id MEMORY_ID
aws bedrock-agent-runtime delete-agent-memory \
  --agent-id AGENT_ID \
  --agent-alias-id ALIAS_ID \
  --memory-id MEMORY_ID

# --- Reranking ---
aws bedrock-agent-runtime rerank \
  --sources '[{"type":"INLINE","inlineDocumentSource":{"type":"TEXT","textDocument":{"text":"Product A has a 2-year warranty."}}},{"type":"INLINE","inlineDocumentSource":{"type":"TEXT","textDocument":{"text":"Product B has a 1-year warranty."}}}]' \
  --queries '[{"type":"TEXT","textQuery":{"text":"warranty information"}}]' \
  --reranking-configuration '{"type":"BEDROCK_RERANKING_MODEL","bedrockRerankingConfiguration":{"modelConfiguration":{"modelArn":"arn:aws:bedrock:us-east-1::foundation-model/amazon.rerank-v1:0"},"numberOfRerankedResults":2}}'
```
