# AWS Amazon Q — CLI Reference
For service concepts, see [amazon-q-capabilities.md](amazon-q-capabilities.md).

Amazon Q Business and Amazon Q Developer are primarily configured and managed through the AWS Console and SDKs. Amazon Q Developer's CLI companion feature (`q` CLI) is installed separately as part of the AWS Toolkit. Core management operations are performed via the `qbusiness` CLI namespace.

```bash
# --- Amazon Q Business: Applications ---
aws qbusiness list-applications
aws qbusiness get-application --application-id APPLICATION_ID
aws qbusiness delete-application --application-id APPLICATION_ID

# --- Amazon Q Business: Indices ---
aws qbusiness list-indices --application-id APPLICATION_ID
aws qbusiness get-index --application-id APPLICATION_ID --index-id INDEX_ID
aws qbusiness delete-index --application-id APPLICATION_ID --index-id INDEX_ID

# --- Amazon Q Business: Data Sources ---
aws qbusiness list-data-sources --application-id APPLICATION_ID --index-id INDEX_ID
aws qbusiness get-data-source --application-id APPLICATION_ID --index-id INDEX_ID --data-source-id DATA_SOURCE_ID

# Start a data source sync
aws qbusiness start-data-source-sync-job \
  --application-id APPLICATION_ID \
  --index-id INDEX_ID \
  --data-source-id DATA_SOURCE_ID

aws qbusiness stop-data-source-sync-job \
  --application-id APPLICATION_ID \
  --index-id INDEX_ID \
  --data-source-id DATA_SOURCE_ID

aws qbusiness list-data-source-sync-jobs \
  --application-id APPLICATION_ID \
  --index-id INDEX_ID \
  --data-source-id DATA_SOURCE_ID

# --- Amazon Q Business: Plugins ---
aws qbusiness list-plugins --application-id APPLICATION_ID
aws qbusiness get-plugin --application-id APPLICATION_ID --plugin-id PLUGIN_ID

# --- Amazon Q Business: Conversations ---
aws qbusiness list-conversations --application-id APPLICATION_ID --user-id USER_ID
aws qbusiness delete-conversation \
  --application-id APPLICATION_ID \
  --conversation-id CONVERSATION_ID \
  --user-id USER_ID

# --- Amazon Q Business: Users and Groups ---
aws qbusiness list-groups --application-id APPLICATION_ID --index-id INDEX_ID
aws qbusiness get-group --application-id APPLICATION_ID --index-id INDEX_ID --group-name GROUP_NAME --data-source-id DATA_SOURCE_ID

# --- Amazon Q Business: Documents ---
aws qbusiness list-documents --application-id APPLICATION_ID --index-id INDEX_ID
aws qbusiness batch-delete-document \
  --application-id APPLICATION_ID \
  --index-id INDEX_ID \
  --documents '[{"id":"doc-001"},{"id":"doc-002"}]'

# --- Amazon Q Business: Web Experience ---
aws qbusiness list-web-experiences --application-id APPLICATION_ID
aws qbusiness get-web-experience --application-id APPLICATION_ID --web-experience-id WEB_EXPERIENCE_ID
```
