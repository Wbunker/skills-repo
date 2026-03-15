# AWS Amazon Q — Capabilities Reference
For CLI commands, see [amazon-q-cli.md](amazon-q-cli.md).

## Amazon Q

### Amazon Q Business

**Purpose**: Fully managed, generative AI-powered enterprise assistant that answers questions, summarizes content, and completes tasks using your organization's data.

| Concept | Description |
|---|---|
| **Application** | Top-level Q Business resource; scopes the assistant to a set of data sources and users |
| **Index** | Search index that stores and retrieves document content; Enterprise or Starter tier |
| **Data source connector** | Managed connector to crawl and sync content: S3, SharePoint, Confluence, Salesforce, Jira, Google Drive, and 40+ others |
| **Retriever** | Component that searches the index; Native Q retriever or Amazon Kendra retriever |
| **Plugin** | Integrations to take actions in third-party apps (Jira, ServiceNow, Salesforce); uses OAuth for auth |
| **Guardrails** | Control what topics Q Business can respond to; block or allow specific topics |
| **User subscription** | Q Business Lite or Q Business Pro per-user pricing |

**Key capabilities**:
- Permissions-aware responses: users only see content they have access to (via IAM Identity Center)
- Citations included in every response
- Hallucination mitigation checks responses in real time
- Anonymous applications supported for public-facing scenarios (no auth required)
- Embed chat UI in your own application or website
- Integrations with Slack, Microsoft Teams, Microsoft 365, and browser extensions

### Amazon Q Developer

**Purpose**: AI-powered coding assistant and developer productivity tool embedded in IDEs and the AWS console.

| Feature | Description |
|---|---|
| **Code suggestions** | Inline real-time code completions in VS Code, JetBrains IDEs, and AWS Cloud9 |
| **/dev agent** | Generates entire features or applications from a natural language description; multi-file edits |
| **/transform agent** | Automated code migration (e.g., Java 8/11 → Java 17, VMware to AWS) |
| **Security scanning** | Detects vulnerabilities in code (OWASP, CWE categories) with remediation suggestions |
| **Amazon Q in the console** | Answer AWS questions, diagnose errors, and explain CloudWatch alarms in the AWS Management Console |
| **CLI companion** | Natural language to shell/CLI command translation |
| **Unit test generation** | Automatically generates unit tests for selected functions |
| **Documentation generation** | Generates inline code documentation |
