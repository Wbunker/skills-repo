# AWS X-Ray / Fault Injection Service — Capabilities Reference

For CLI commands, see [xray-fis-cli.md](xray-fis-cli.md).

## AWS X-Ray

**Purpose**: Distributed tracing service for analyzing and debugging distributed applications; provides end-to-end request visibility across microservices.

### Core Concepts

| Concept | Description |
|---|---|
| **Trace** | An end-to-end record of a request as it travels through all services; composed of segments |
| **Segment** | Data from one service that processed the request; includes timing, metadata, subsegments, and errors |
| **Subsegment** | Detail within a segment for a downstream call (DB query, HTTP call, AWS SDK call) |
| **Annotation** | Key-value pair indexed for filtering traces (e.g., `userId`, `environment`); queryable in console/API |
| **Metadata** | Key-value pairs not indexed; for storing additional context within a trace (not filterable) |
| **Sampling rule** | Rules defining what percentage of requests are traced; reservoir + fixed rate model |
| **Group** | A named filter expression on traces; enables separate sampling rules and metrics per group |
| **Service Map** | Visual graph of services and their connections; shows request rates, error rates, and latency |
| **X-Ray daemon** | Lightweight process that buffers segment documents from SDK and uploads to X-Ray API in batches; runs on EC2, ECS, Lambda (built-in) |
| **X-Ray SDK** | Instruments application code; available for Java, Python, Go, Node.js, Ruby, .NET |

### Instrumentation

- **AWS SDK calls**: Automatically traced when using X-Ray SDK wrapper
- **Incoming HTTP requests**: Middleware intercepts and starts a segment per request
- **Lambda**: Active tracing enabled via function configuration; daemon pre-installed
- **ECS**: Sidecar container pattern for the X-Ray daemon; or use AWS Distro for OpenTelemetry (ADOT)
- **OpenTelemetry**: X-Ray supports OTLP trace ingestion via AWS Distro for OpenTelemetry

### Sampling

```
Default rule: 1 reservoir (1 req/sec guaranteed) + 5% fixed rate of remaining requests
Custom rules: Define reservoir size and fixed rate per service name, URL, method, annotation
```

---

## AWS Fault Injection Service (FIS)

**Purpose**: Managed fault injection service for running controlled chaos engineering experiments to validate application resilience.

### Core Concepts

| Concept | Description |
|---|---|
| **Experiment template** | Defines actions, targets, stop conditions, and IAM role for a fault injection experiment |
| **Action** | A specific fault to inject (e.g., terminate EC2 instances, add CPU stress, throttle network, inject Lambda errors) |
| **Target** | AWS resources the action applies to; selected by resource type, ID, or tags; supports random selection |
| **Stop condition** | CloudWatch alarm that automatically halts the experiment if a safety threshold is breached |
| **Experiment** | A running instance of a template; generates a report with before/after observations |
| **Target account configuration** | Cross-account experiments using delegated accounts |

### Available Action Categories

- **AWS EC2**: Terminate instances, stop instances, reboot instances, CPU/memory stress, network disruption
- **AWS ECS**: Stop tasks, CPU/memory stress on containers
- **AWS EKS**: Terminate nodes, pod stress
- **AWS RDS**: Failover DB cluster, reboot DB instance
- **AWS Lambda**: Inject invocation errors, add invocation latency
- **AWS Networking**: Disrupt connectivity, route table changes
- **AWS Systems Manager**: Run stress via SSM documents (CPU, memory, disk, kill process)
