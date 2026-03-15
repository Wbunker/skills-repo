# AWS Runtime & Testing — Capabilities Reference

For CLI commands, see [runtime-testing-cli.md](runtime-testing-cli.md).

**Note**: Deep reference for X-Ray and FIS is in [management-devops/xray-fis-capabilities.md](../management-devops/xray-fis-capabilities.md). This file covers Amazon Corretto in full and provides concise summaries with cross-references for X-Ray and FIS.

---

## Amazon Corretto

**Purpose**: No-cost, multiplatform, production-ready distribution of the Open Java Development Kit (OpenJDK). Maintained by Amazon with long-term support (LTS), quarterly security patches, and performance enhancements used internally by Amazon services.

### Key Characteristics

| Attribute | Description |
|---|---|
| **No-cost** | Freely available under the GNU General Public License with the Classpath Exception (GPL v2 + CPE) |
| **OpenJDK-compatible** | 100% compatible with Java SE standards; passes the OpenJDK Technology Compatibility Kit (TCK) |
| **Amazon-internal** | The same JDK used to run Amazon services in production; patches are tested at massive scale |
| **LTS commitment** | Amazon provides long-term patches beyond the upstream OpenJDK LTS window |
| **Quarterly updates** | Security and performance patches released on the OpenJDK quarterly schedule |
| **Performance patches** | Includes backported performance and reliability fixes from upstream or developed internally |

### Supported Versions (LTS)

| Corretto Version | Java SE Version | Amazon LTS Until |
|---|---|---|
| **Corretto 8** | Java SE 8 | At least May 2026 |
| **Corretto 11** | Java SE 11 | At least September 2027 |
| **Corretto 17** | Java SE 17 | At least October 2029 |
| **Corretto 21** | Java SE 21 | At least September 2031 |

Non-LTS versions (e.g., Corretto 20) are available but receive only 6 months of support.

### Supported Platforms

| Platform | Distribution Method |
|---|---|
| **Amazon Linux 2** | `amazon-linux-extras` and `yum`; included in AL2 by default |
| **Amazon Linux 2023** | `dnf`; default Java on AL2023 |
| **Linux (RPM)** | RPM packages for RHEL/CentOS/Fedora-compatible systems |
| **Linux (DEB)** | DEB packages for Debian/Ubuntu systems |
| **Windows** | MSI installer |
| **macOS** | PKG installer or Homebrew (`brew install corretto`) |
| **Docker** | Official images on Amazon ECR Public (`public.ecr.aws/amazoncorretto/amazoncorretto:<version>`) and Docker Hub |
| **AWS services** | Pre-installed on CodeBuild managed images; available in Lambda (Java runtimes); used in Elastic Beanstalk Java platforms |

### Installation Examples

```bash
# Amazon Linux 2
sudo yum install java-17-amazon-corretto-devel

# Amazon Linux 2023
sudo dnf install java-17-amazon-corretto-devel

# Ubuntu / Debian (add Corretto apt repository first)
wget -O - https://apt.corretto.aws/corretto.key | sudo apt-key add -
sudo add-apt-repository 'deb https://apt.corretto.aws stable main'
sudo apt-get update && sudo apt-get install -y java-17-amazon-corretto-jdk

# macOS (Homebrew)
brew install corretto17

# Docker
FROM public.ecr.aws/amazoncorretto/amazoncorretto:21
```

### Multiple Version Management

Use `alternatives` (Linux) or `update-alternatives` to switch between installed Corretto versions:

```bash
sudo alternatives --config java
sudo alternatives --config javac
```

### Migrating from Oracle JDK

- Drop-in replacement for Oracle JDK; no code changes required
- Same Java SE API surface; existing applications run without modification
- Replace JVM flags: `-XX:+UseG1GC` is the default garbage collector; Corretto supports ZGC and Shenandoah as alternatives
- Oracle JDK commercial features (Flight Recorder, Mission Control) are available as open-source in Corretto 11+
- JDK Flight Recorder (JFR): available in Corretto 8u262+, 11+, and all later LTS releases

### Corretto in AWS Lambda

Java Lambda runtimes use Corretto:
- `java8.al2` — Corretto 8 on Amazon Linux 2
- `java11` — Corretto 11 on Amazon Linux 2
- `java17` — Corretto 17 on Amazon Linux 2023
- `java21` — Corretto 21 on Amazon Linux 2023

Lambda SnapStart (Java 17 and 21): Creates a snapshot of the initialized Lambda execution environment, dramatically reducing cold start latency.

---

## AWS X-Ray

**Purpose**: Distributed tracing service for analyzing and debugging production distributed applications; provides end-to-end request visibility and a service map.

For full reference, see [management-devops/xray-fis-capabilities.md](../management-devops/xray-fis-capabilities.md).

### Concise Concept Summary

| Concept | Description |
|---|---|
| **Trace** | End-to-end record of a request spanning all services it touches |
| **Segment** | Data contributed by one service (timing, errors, metadata) |
| **Subsegment** | Detail within a segment for a downstream call (DB, HTTP, SDK) |
| **Annotation** | Indexed key-value pair; queryable in filter expressions |
| **Metadata** | Non-indexed key-value pair; additional context not used for filtering |
| **Sampling** | Default: 1 req/sec reservoir + 5% of remaining; custom rules by service/path/method |
| **Service Map** | Visual graph of services, connections, error rates, and latency distributions |
| **Groups** | Named filter expressions enabling separate sampling rules and CloudWatch metrics per group |
| **X-Ray daemon** | Lightweight UDP listener that buffers and batches segments to the X-Ray API |
| **X-Ray SDK** | Instruments code; available for Java, Python, Node.js, Go, Ruby, .NET |
| **ADOT** | AWS Distro for OpenTelemetry — alternative instrumentation path; sends OTLP traces to X-Ray |

### Key Integration Points

- **Lambda**: Enable active tracing on function; daemon is built-in; no separate process needed
- **ECS**: Run X-Ray daemon as a sidecar container; or use ADOT Collector sidecar
- **EC2/ECS/EKS**: Run the X-Ray daemon as a process/container; configure SDK to send to `localhost:2000`
- **API Gateway**: Enable X-Ray tracing on a stage; traces automatically propagate to downstream Lambda/ECS
- **CloudWatch**: X-Ray groups generate CloudWatch metrics (error rate, throttle rate, fault rate, response time)

---

## AWS Fault Injection Service (FIS)

**Purpose**: Managed chaos engineering service; run controlled fault injection experiments to validate application and infrastructure resilience.

For full reference, see [management-devops/xray-fis-capabilities.md](../management-devops/xray-fis-capabilities.md).

### Concise Concept Summary

| Concept | Description |
|---|---|
| **Experiment template** | Blueprint defining targets, actions, stop conditions, and IAM role |
| **Target** | AWS resources selected by resource type + tags or resource IDs; supports random % selection |
| **Action** | A specific fault to inject (terminate EC2 instances, inject Lambda errors, add network latency, etc.) |
| **Stop condition** | CloudWatch alarm that auto-halts the experiment if a safety threshold is breached |
| **Experiment** | A running instance of a template; generates before/after observations and a result report |
| **Target account configuration** | Enables cross-account experiments by delegating to another account |

### Available Fault Categories

- **EC2**: Terminate, stop, reboot instances; CPU/memory stress; network disruption; AZ availability disruption
- **ECS**: Stop tasks; CPU/memory stress
- **EKS**: Terminate nodes; pod-level stress
- **RDS**: Failover cluster; reboot DB instance
- **Lambda**: Inject invocation errors; add latency
- **Networking**: Disrupt connectivity; modify route tables
- **Systems Manager**: Run SSM stress documents (CPU, memory, disk I/O, kill process)

### Best Practices

1. Always define a CloudWatch alarm stop condition before running an experiment
2. Start with small blast radius (low percent targets) and increase incrementally
3. Run in non-production first; validate resilience hypothesis before production
4. Observe metrics (CloudWatch, X-Ray service map) during the experiment window
5. Use tags to target specific environments (`Env=staging`) and avoid unintended scope
