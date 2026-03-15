# Governance, Testing & Business ML — Capabilities Reference
For CLI commands, see [governance-testing-ml-cli.md](governance-testing-ml-cli.md).

## Amazon CodeGuru Reviewer

**Purpose**: ML and program-analysis service that automatically reviews Java and Python code for quality issues, security vulnerabilities, and secrets exposure during pull requests or on-demand — integrates with common source control providers.

> **Note**: As of November 7, 2025, new repository associations can no longer be created. AWS recommends Amazon Q Developer as the successor for AI-powered code review and suggestions.

### Core Concepts

| Concept | Description |
|---|---|
| **Repository association** | Connection between CodeGuru Reviewer and a source repository (CodeCommit, GitHub, Bitbucket, GitHub Enterprise) |
| **Code review** | Analysis run against a pull request or a specific repository branch/commit |
| **Recommendation** | A specific issue found in the code; includes file path, line number, severity, and remediation guidance |
| **Recommendation feedback** | Thumbs up/down feedback on recommendations; used to improve future suggestions |

### Supported Languages and Source Providers

| Dimension | Options |
|---|---|
| **Languages** | Java, Python |
| **Source providers** | AWS CodeCommit, GitHub, GitHub Enterprise Cloud, GitHub Enterprise Server, Bitbucket |

### Types of Recommendations

| Category | Examples |
|---|---|
| **Security** | Input validation, SQL injection, XSS, path traversal, insecure deserialization |
| **Secrets detection** | Hardcoded passwords, API keys, access tokens in source code |
| **Resource leaks** | Unclosed file handles, database connections, network sockets |
| **Code quality** | Incorrect use of concurrency primitives, overly complex code, common bugs |
| **AWS best practices** | Correct use of AWS SDK clients, pagination patterns, IAM anti-patterns |

### Review Modes

| Mode | Trigger | Use Case |
|---|---|---|
| **Pull request review** | Automatic on PR creation/update | Inline PR comments in developer workflow |
| **Repository analysis** | On-demand; scans entire default branch | Baseline review of existing codebase |

---

## Amazon CodeGuru Profiler

**Purpose**: Continuous runtime profiling service that instruments live applications, identifies the most expensive code paths consuming CPU and memory, and provides ML-powered recommendations to reduce latency and infrastructure costs.

### Core Concepts

| Concept | Description |
|---|---|
| **Profiling group** | Named resource representing a single application or microservice being profiled |
| **Profiling agent** | Library embedded in the application that periodically samples the call stack and reports to the service |
| **Flame graph (profile)** | Aggregated visualization of call stack samples; wider bars indicate more CPU time |
| **Recommendation report** | ML-generated findings identifying costly code patterns with suggested improvements |
| **Anomaly** | Detected deviation from the application's normal performance baseline |
| **Frame metric** | Named metric tracking the latency or cost of a specific method over time |

### Supported Languages

| Language | Heap Summary | Notes |
|---|---|---|
| **Java / JVM** | Yes | Broadest feature support; all JVM languages (Kotlin, Scala, Groovy) |
| **Python 3.6+** | No | CPU and anomaly detection supported |

### Agent Integration

```python
# Python agent (pip install codeguru_profiler_agent)
from codeguru_profiler_agent import Profiler
profiler = Profiler(profiling_group_name='my-service-profiler')
profiler.start()
# ... application code runs ...
profiler.stop()
```

```java
// Java agent — JVM flag approach (no code changes)
-javaagent:/path/to/codeguru-profiler-java-agent.jar
-Dcom.amazonaws.codeguruprofiler.profilingGroupName=my-service-profiler
```

### Key Features

- **Always-on profiling**: Low-overhead agent (~5% CPU overhead) runs continuously in production
- **Automated anomaly detection**: Alerts when a function's cost exceeds a learned baseline
- **Flame graph visualization**: Interactive call graph in the console; drill down to problematic methods
- **Notifications**: SNS or email alerts when new recommendations or anomalies are detected
- **Differential profiling**: Compare two time periods to identify regressions after deployments
- **Lambda support**: Profile Lambda function execution (Java and Python)

---

## Amazon DevOps Guru

**Purpose**: ML-powered cloud operations service that continuously analyzes application metrics, logs, events, and traces to detect operational anomalies, surface actionable insights, and recommend remediations — reducing mean time to detect (MTTD) and resolve (MTTR) production issues.

### Core Concepts

| Concept | Description |
|---|---|
| **Resource coverage** | The set of AWS resources DevOps Guru monitors; defined by CloudFormation stack, AWS account, or tag |
| **Reactive insight** | Triggered when an anomaly is detected in current operational data; describes an ongoing issue |
| **Proactive insight** | Identified risk or degrading trend that could cause future problems before they impact availability |
| **Anomaly** | Metric, log, or event that deviates significantly from the learned normal baseline |
| **Recommendation** | Specific remediation guidance associated with an insight (e.g., "scale up capacity", "fix Lambda timeout") |
| **OpsItem** | Automatically created AWS Systems Manager OpsCenter item linked to each insight |
| **Feedback** | Operator rating (useful / not useful) on an insight; improves future detection accuracy |

### Data Sources Analyzed

| Source | What DevOps Guru Looks At |
|---|---|
| **CloudWatch metrics** | Latency, error rates, throttles, queue depth, CPU, memory |
| **CloudWatch Logs** | Anomalous log patterns and error spikes via CloudWatch Log Anomaly Detection |
| **AWS Config** | Configuration change events |
| **CloudTrail** | API call patterns and unusual activity |
| **X-Ray traces** | Service map anomalies, fault rates, latency distributions |
| **AWS Systems Manager** | OpsCenter integration for ticketing |

### Supported AWS Services

DevOps Guru has native integration with: Lambda, API Gateway, DynamoDB, RDS, ECS, EKS, SNS, SQS, S3, Kinesis, ElastiCache, CloudFormation stacks, and more.

### Insight Types

| Type | Severity | Description |
|---|---|---|
| **Reactive — High** | Active impact on availability or performance | P1/P2 equivalent; immediate action needed |
| **Reactive — Medium** | Degradation detected | Investigate and remediate proactively |
| **Proactive — High** | Imminent risk | Action recommended before impact occurs |

### Notification Integration

```
DevOps Guru → SNS Topic → Email / PagerDuty / Slack (via Lambda)
DevOps Guru → EventBridge → Automated remediation Lambda
DevOps Guru → OpsCenter OpsItem → Systems Manager runbooks
```

### Key Features

- **One-click activation**: No agents to deploy; enable per account/region in the console
- **CloudFormation-scoped coverage**: Monitor resources belonging to specific stacks
- **Cost estimation**: Estimate the monthly DevOps Guru cost before enabling for large accounts
- **Organization-level insights**: View cross-account/cross-region insights from AWS Organizations management account

---

## Amazon Augmented AI (A2I)

**Purpose**: Human review workflow service that routes low-confidence ML predictions to human reviewers for validation; removes the complexity of building and managing human-in-the-loop pipelines for quality-critical AI applications.

### Core Concepts

| Concept | Description |
|---|---|
| **Flow definition** | Configuration of a human review workflow: who reviews (workforce), what they see (task template), and when to trigger (conditions) |
| **Human task UI (worker task template)** | Liquid-templated HTML interface displayed to human reviewers for a specific review task type |
| **Human loop** | A single instance of human review triggered for a specific prediction; contains the input data and reviewer output |
| **Workforce** | The group of reviewers: Amazon Mechanical Turk (public), private (your employees), or AWS Marketplace vendor workforce |
| **Work team** | A subset of a private workforce assigned to a specific flow definition |
| **Condition** | Rule determining when a human loop is triggered (e.g., model confidence < 0.7, random sample %) |

### Built-In Task Types

A2I provides pre-built task templates and flow definitions for native AWS services:

| AWS Service | Review Task | What Reviewers Validate |
|---|---|---|
| **Amazon Textract** | Form key-value extraction | Verify extracted form fields from documents |
| **Amazon Rekognition** | Image content moderation | Confirm or override unsafe content classifications |

### Custom Task Types

For any ML service or custom model:
- Build an HTML worker task UI with Liquid templating
- Trigger human loops programmatically via `StartHumanLoop` API
- Route reviewer outputs back to your application or S3

### Human Review Workflow

```
ML prediction (low confidence or sampled) → StartHumanLoop API
→ Human review task routed to Work Team via labeling portal
→ Reviewer submits judgment → Output JSON written to S3
→ Your application reads reviewer decisions → Retrain or correct prediction
```

### Key Features

- **Condition-based triggering**: Invoke human review only when the model score falls below a threshold; avoid unnecessary review costs
- **Random sampling**: Route a percentage of all predictions to human review for ongoing quality auditing
- **Output to S3**: Reviewer decisions written as JSON to S3; consume via Lambda, EventBridge, or batch processing
- **Audit trail**: All human loop outputs logged with reviewer ID, timestamps, and decisions
- **Worker portal**: Pre-built web interface for private workforce reviewers; no custom front-end required

---

## Amazon Fraud Detector

**Purpose**: Managed ML fraud detection service that combines 20+ years of Amazon fraud expertise with models trained on your transaction data to score events (account registrations, payments, logins) for fraud risk in real time.

> **Note**: Amazon Fraud Detector is no longer accepting new customers as of November 7, 2025. AWS recommends Amazon SageMaker with AutoGluon, or AWS WAF for web fraud prevention, as alternatives.

### Core Concepts

| Concept | Description |
|---|---|
| **Event type** | Definition of a fraud scenario: what data fields are collected (e.g., `account_registration`, `online_payment`) |
| **Entity type** | The actor involved in an event (e.g., `customer`, `merchant`, `ip_address`) |
| **Label** | Classification of a historical event: `fraud` or `legit`; used to train models |
| **Variable** | A named data attribute in an event: IP address, email, device ID, order amount, etc. |
| **Model** | Trained ML model for a specific event type; two types: Online Fraud Insights (OFI) and Transaction Fraud Insights (TFI) |
| **Model version** | Specific training run; must be activated before use |
| **Detector** | Named resource that defines the fraud evaluation logic for an event type |
| **Detector version** | Versioned configuration of rules and models within a detector |
| **Rule** | Conditional logic applied to model scores and event variables to produce an outcome |
| **Outcome** | Result action assigned when a rule fires (e.g., `approve`, `review`, `block`) |

### Model Types

| Model Type | Description | Best For |
|---|---|---|
| **Online Fraud Insights (OFI)** | Scores individual events; uses entity-level behavior history | Account registration fraud, login anomalies |
| **Transaction Fraud Insights (TFI)** | Optimized for payment transactions; uses graph-based entity relationships | Payment fraud, card-not-present fraud |

### Fraud Detection Workflow

```
Send event data → GetEventPrediction API
→ Run model scoring + rule evaluation
→ Return model scores + matched rule outcomes (approve/review/block)
→ Application applies outcome action
```

### Key Features

- **Amazon-trained prior**: Models pre-trained on Amazon's fraud patterns; your data fine-tunes on top
- **Real-time scoring**: `GetEventPrediction` returns a fraud score and outcome in <100ms
- **Explainability**: Top fraud indicators returned with each prediction
- **Batch predictions**: `CreateBatchPredictionJob` for scoring historical datasets
- **External model integration**: Use your own SageMaker endpoint alongside Fraud Detector rules
- **List variables**: Maintain allow/block lists (trusted emails, blocked IPs) for rule evaluation
