# Operational Security: Threat Modeling for APIs

Threat modeling is the disciplined practice of identifying, cataloging, and mitigating security threats before they are exploited. For APIs, which serve as the programmatic front door to an organization's data and business logic, threat modeling is not optional. It is a core engineering activity that must be woven into the design and development lifecycle. This reference covers the OWASP API Security Top 10, a structured approach to threat modeling using STRIDE and DREAD, and practical guidance for securing APIs against real-world attack vectors.

## The Cost of Unsecured APIs

APIs that are exposed without adequate security controls represent one of the highest-risk attack surfaces in modern software. Unlike traditional web applications where a human interacts with a browser, APIs are consumed by automated clients at machine speed, meaning exploitation can be scaled trivially once a vulnerability is discovered.

Real-world breaches underscore the severity. The 2019 Capital One breach exploited a misconfigured API endpoint behind a web application firewall, leading to the exfiltration of over 100 million customer records. The Facebook Graph API vulnerability in 2018 exposed access tokens for 50 million accounts through a chain of API-level authorization flaws. In 2021, the Peloton API exposed private user data because object-level authorization checks were absent, allowing any authenticated user to retrieve any other user's account details by modifying an identifier in the request.

The business impact of these failures extends beyond immediate data loss. Regulatory penalties under GDPR, CCPA, and PCI DSS can reach into the hundreds of millions. Customer trust, once broken, erodes revenue for years. Engineering teams are pulled into costly incident response cycles instead of building product value. The common thread across these incidents is that a structured threat modeling process would have identified the exploitable weakness before deployment.

## OWASP API Security Top 10 (2023)

The OWASP API Security Top 10 provides a prioritized catalog of the most critical API vulnerabilities. Each entry represents a category of weakness that appears repeatedly in production API deployments.

### API1: Broken Object Level Authorization (BOLA/IDOR)

The most prevalent API vulnerability. It occurs when an API endpoint accepts an object identifier from the client (such as a user ID, order number, or document reference) and retrieves the corresponding resource without verifying that the authenticated user is authorized to access that specific object. An attacker simply iterates through identifiers to access other users' data. Mitigation requires server-side authorization checks on every request that references an object, using the authenticated identity from the session rather than any client-supplied ownership claim.

### API2: Broken Authentication

APIs that implement authentication incorrectly or incompletely. This includes endpoints that accept weak credentials, fail to enforce brute-force protections, expose tokens in URLs, do not validate token signatures, or allow credential stuffing. Authentication is the foundation of all subsequent authorization decisions. If it is broken, every downstream security control is undermined. Mitigations include using established protocols such as OAuth 2.0 and OpenID Connect, enforcing multi-factor authentication for sensitive operations, and implementing token rotation and revocation.

### API3: Broken Object Property Level Authorization

A refinement of BOLA that focuses on individual properties within an object. An API might correctly restrict access to an object as a whole but fail to enforce authorization on specific fields. For example, a user might be allowed to read their own profile but should not be able to modify the `role` or `account_balance` fields. This vulnerability manifests in two patterns: excessive data exposure (returning more fields than the consumer needs) and mass assignment (accepting writes to fields the consumer should not control). Mitigation requires explicit allowlists of readable and writable properties per role.

### API4: Unrestricted Resource Consumption

APIs that do not impose limits on the volume or cost of requests a client can make. This includes missing rate limits, unbounded pagination, unrestricted file upload sizes, and operations that trigger expensive backend processing without throttling. Attackers exploit this for denial of service or to inflate cloud infrastructure costs. Mitigation involves rate limiting at multiple layers (per user, per IP, per endpoint), setting maximum page sizes, imposing request body size limits, and using cost-aware throttling for computationally expensive operations.

### API5: Broken Function Level Authorization

Occurs when API endpoints do not enforce authorization checks at the function level. Administrative endpoints are accessible to regular users, or destructive operations (DELETE, PUT) are available to consumers who should only have read access. This often arises when authorization is implemented only at the UI layer, and the API trusts that the client will not call endpoints it was not shown. Mitigation requires server-side authorization enforcement on every endpoint, using role-based or attribute-based access control that is independent of the client.

### API6: Unrestricted Access to Sensitive Business Flows

Some API-accessible business flows can be abused at scale even when each individual request is technically legitimate. Examples include automated ticket scalping, mass account creation for spam, and programmatic coupon redemption. The threat is not a single malicious request but the automated repetition of a legitimate flow. Mitigation involves device fingerprinting, CAPTCHA challenges for sensitive flows, behavioral analysis to detect bot patterns, and business-logic rate limits that go beyond simple request-per-second throttling.

### API7: Server-Side Request Forgery (SSRF)

Occurs when an API accepts a URL or network address from the client and makes a server-side request to that destination without proper validation. Attackers use this to probe internal networks, access cloud metadata services (such as the AWS instance metadata endpoint at `169.254.169.254`), or exfiltrate data through the server as a proxy. Mitigation requires validating and sanitizing all client-supplied URLs, maintaining allowlists of permitted destinations, blocking requests to private IP ranges and cloud metadata endpoints, and disabling unnecessary URL-fetching functionality.

### API8: Security Misconfiguration

A broad category covering insecure default configurations, incomplete hardening, overly permissive CORS policies, verbose error messages that leak stack traces or internal architecture details, missing security headers, and unnecessary HTTP methods left enabled. This is often the result of deploying APIs with development-time configurations in production. Mitigation requires a hardened baseline configuration, automated configuration scanning in CI/CD, and regular audit of deployed configurations against the baseline.

### API9: Improper Inventory Management

Organizations frequently lose track of which API versions, endpoints, and environments are deployed and accessible. Deprecated API versions remain online, development or staging environments are exposed to the internet without authentication, and shadow APIs built by individual teams operate outside centralized governance. Attackers target these forgotten or ungoverned endpoints because they are less likely to have current security controls. Mitigation requires a centralized API inventory, automated discovery of deployed endpoints, and lifecycle management that includes decommissioning.

### API10: Unsafe Consumption of APIs

APIs do not only serve data; they also consume data from upstream third-party APIs. When an API trusts data received from a third-party service without validation, it inherits the security posture of that third party. If the upstream service is compromised or returns malicious data, the consuming API becomes a vector for injection, data corruption, or further exploitation. Mitigation requires treating all external API responses as untrusted input, applying the same validation and sanitization rules used for client-supplied data.

## Threat Modeling Fundamentals

Threat modeling is the structured process of identifying what can go wrong in a system, how likely it is, and what to do about it. It answers four questions: What are we building? What can go wrong? What are we going to do about it? Did we do a good enough job?

The value of threat modeling is that it shifts security analysis left in the development lifecycle. Discovering a broken authorization model in a design review costs a fraction of what it costs to discover the same flaw through a production breach. Threat modeling should be performed at the start of any new API project, when significant changes are made to an existing API's architecture or data flows, before major releases, and periodically as part of ongoing security review.

### Thinking Like an Attacker

Effective threat modeling requires adopting the adversary's perspective. Attacker motivations vary: financial gain through data theft or ransomware, competitive intelligence through corporate espionage, disruption through hacktivism or state-sponsored attacks, and opportunistic exploitation by automated scanners that probe every publicly accessible endpoint.

The attack surface of an API includes every endpoint, every input parameter, every authentication mechanism, every trust boundary between services, and every data store that the API reads from or writes to. External APIs have the broadest attack surface because they are directly reachable from the internet. Internal APIs between microservices have a narrower but still significant attack surface, particularly when a compromised service can pivot laterally. Partner APIs occupy a middle ground where trust assumptions about the calling party may be overly generous.

## The Six-Step Threat Modeling Process

### Step 1: Identify Objectives

Define what you are protecting and why. This includes the data assets (customer PII, financial records, authentication credentials, intellectual property), the business processes (payment processing, account management, order fulfillment), and the compliance requirements (PCI DSS, HIPAA, GDPR) that constrain how those assets must be handled. Clear objectives focus the threat modeling effort on the highest-value targets rather than attempting to enumerate every conceivable threat.

### Step 2: Gather Information

Collect the architectural artifacts needed to reason about the system. This includes API specifications (OpenAPI/Swagger documents), architecture diagrams showing service boundaries and network topology, data flow diagrams tracing how information moves through the system, authentication and authorization configurations, deployment topology including cloud provider, region, and network segmentation, and dependency inventories for third-party services and libraries. If these artifacts do not exist, creating them is the first deliverable of the threat modeling exercise.

### Step 3: Decompose the System

Break the system into components and identify the elements relevant to security analysis:

- **Entry points**: Every API endpoint, webhook receiver, message queue consumer, and administrative interface that accepts input.
- **Assets**: Data stores, credentials, encryption keys, configuration secrets, and any resource that has value to an attacker.
- **Trust levels**: The different privilege levels that exist in the system (anonymous, authenticated user, service account, administrator) and the boundaries where trust level changes (the API gateway, the authentication middleware, the database access layer).
- **Trust boundaries**: The lines in the architecture where data crosses from one trust level to another. Every trust boundary is a potential point of failure if the transition is not properly validated.

### Step 4: Identify Threats Using STRIDE

STRIDE is a mnemonic for six categories of threat that map systematically to the components identified in Step 3.

**Spoofing Identity** targets authentication mechanisms. Can an attacker impersonate a legitimate user or service? Examples include forging JWT tokens with weak signing keys, replaying stolen session tokens, and exploiting misconfigured service-to-service authentication. For APIs, spoofing is particularly dangerous because automated clients do not have the visual cues (such as browser certificate warnings) that help human users detect impersonation.

**Tampering with Data** targets data integrity. Can an attacker modify data in transit or at rest? Examples include intercepting and modifying API requests over unencrypted connections, exploiting mass assignment to modify fields the client should not control, and injecting malicious payloads into request bodies that are stored and later processed. APIs that accept structured data (JSON, XML) are vulnerable to injection attacks if input is not validated against a strict schema.

**Repudiation** targets accountability. Can a user or service deny having performed an action? If an API does not maintain adequate audit logs, or if logs can be tampered with, then malicious actions cannot be attributed. For financial APIs and APIs that process regulated data, non-repudiation is a compliance requirement, not merely a nice-to-have.

**Information Disclosure** targets confidentiality. Can an attacker extract data they should not have access to? This includes verbose error messages that reveal internal architecture, API responses that return more data than the consumer needs, timing side-channels that reveal whether a resource exists, and log files that capture sensitive request or response data.

**Denial of Service** targets availability. Can an attacker render the API unavailable to legitimate users? Beyond volumetric DDoS attacks, API-specific denial of service includes sending requests that trigger expensive database queries, uploading extremely large payloads, and exploiting algorithmic complexity vulnerabilities (such as regex denial of service or hash collision attacks).

**Elevation of Privilege** targets authorization. Can an attacker gain access to functionality or data beyond their authorized level? This includes exploiting broken function-level authorization to access admin endpoints, manipulating tokens or session state to assume a higher privilege level, and chaining multiple lower-severity vulnerabilities to achieve unauthorized access.

### Step 5: Evaluate Threat Risks

Not all threats are equal. Risk evaluation prioritizes threats so that mitigation effort is directed where it has the greatest impact. Two common approaches are used.

**DREAD scoring** rates each threat on five dimensions, each scored from 1 to 10: Damage potential (how severe is the impact?), Reproducibility (how reliably can the attack be executed?), Exploitability (how much skill or tooling is required?), Affected users (how many users are impacted?), and Discoverability (how easy is it to find the vulnerability?). The average of these scores provides a composite risk rating.

**Risk matrix** maps threats on two axes: likelihood (how probable is exploitation?) and impact (how severe are the consequences?). Threats that are both highly likely and highly impactful are addressed first. This approach is simpler than DREAD and works well for teams that are new to threat modeling.

Regardless of the evaluation method, the output is a prioritized list of threats with associated risk levels, which drives the mitigation plan.

### Step 6: Validation

Threat modeling is not a one-time activity. Validation ensures that identified threats have been mitigated and that the model itself remains current. This includes verifying that mitigations have been implemented and are effective (through code review, automated testing, and penetration testing), updating the threat model when the architecture changes, when new endpoints are added, or when new vulnerabilities are disclosed in dependencies, and conducting periodic reviews even when no changes have occurred, because the threat landscape evolves independently of the system.

## API-Specific Attack Vectors

Beyond the OWASP Top 10 categories, several attack vectors are particularly relevant to API implementations.

**Injection attacks** exploit APIs that incorporate client-supplied data into queries or commands without sanitization. SQL injection, NoSQL injection, and command injection are all possible when API parameters are concatenated into backend queries. GraphQL APIs are additionally vulnerable to query injection where deeply nested or circular queries consume excessive server resources.

**Mass assignment** occurs when an API binds client-supplied JSON or form data directly to internal data models without filtering. An attacker adds fields to the request body that map to sensitive model properties (such as `isAdmin`, `price`, or `accountBalance`), and the server processes them. Prevention requires explicit allowlists of bindable fields for each endpoint.

**Excessive data exposure** occurs when API responses include more data than the consumer needs, relying on the client to filter what is displayed. An attacker bypasses the client and reads the full response. Prevention requires shaping API responses on the server to include only the fields necessary for the specific consumer and operation.

**Rate limiting bypass** exploits weaknesses in how rate limits are enforced. Attackers rotate IP addresses, distribute requests across multiple API keys, or exploit inconsistencies between rate limiting at the gateway and at the application layer. Effective rate limiting must be applied at multiple levels (IP, user, API key, endpoint) and must account for distributed attack patterns.

## Data Flow Diagrams for API Threat Modeling

Data flow diagrams (DFDs) are the primary visual artifact in API threat modeling. A DFD for an API system includes four element types:

- **External entities**: Clients, third-party services, and any actor outside the system boundary. Represented as rectangles.
- **Processes**: API endpoints, middleware, background workers, and any component that transforms data. Represented as circles.
- **Data stores**: Databases, caches, file systems, and message queues. Represented as parallel lines.
- **Data flows**: The movement of data between entities, processes, and stores, annotated with the protocol, authentication mechanism, and encryption status. Represented as arrows.

Trust boundaries are drawn as dashed lines across the diagram wherever data crosses from one trust level to another. Every trust boundary crossing is a candidate for threat identification using STRIDE. A well-constructed DFD for an API system will show the flow from the external client through the API gateway, through authentication and authorization middleware, into the business logic layer, and down to the data stores, with trust boundaries marked at each transition.

## Common Mitigations

**Input validation**: Validate all incoming data against a strict schema. Use allowlists rather than denylists. Reject requests that do not conform to the expected structure, type, length, and range constraints. For APIs with an OpenAPI specification, enforce the specification at the gateway layer.

**Output encoding**: Encode all output data appropriately for its context. This prevents injection attacks when API responses are rendered in browsers or consumed by downstream systems that interpret special characters.

**Authentication**: Use established, well-tested protocols. OAuth 2.0 with PKCE for user-facing APIs, mutual TLS for service-to-service communication, and API keys (with rotation policies) for partner integrations. Never implement custom authentication schemes without expert review.

**Authorization**: Enforce authorization on the server for every request. Use a centralized policy engine where possible. Implement both role-based access control (for function-level authorization) and attribute-based access control (for object-level authorization). Test authorization logic with negative test cases that verify denied access as rigorously as permitted access.

**Encryption**: Use TLS 1.2 or later for all data in transit. Encrypt sensitive data at rest. Manage encryption keys through a dedicated key management service rather than embedding them in application code or configuration files.

**Rate limiting**: Apply rate limits at the API gateway and enforce them per user, per IP, and per endpoint. Set distinct limits for read and write operations. Implement exponential backoff responses (HTTP 429) that include `Retry-After` headers. Monitor rate limit metrics to detect distributed attacks that stay below per-source thresholds but exceed aggregate capacity.

**Logging and monitoring**: Log all authentication events, authorization failures, and input validation rejections. Do not log sensitive data such as passwords, tokens, or PII. Forward logs to a centralized security information and event management (SIEM) system. Set up alerts for anomalous patterns such as spikes in 401/403 responses, unusual request volumes from a single consumer, or access patterns that suggest enumeration attacks.

## Integrating Threat Modeling into the API Development Lifecycle

Threat modeling delivers the most value when it is a continuous practice rather than a periodic audit. Integration points in the development lifecycle include:

- **Design phase**: Conduct the initial threat model when the API's endpoints, data flows, and authorization model are being designed. This is where architectural mitigations (such as adding an authorization middleware layer or segmenting sensitive data into a separate service) are least expensive to implement.
- **Implementation phase**: Use the threat model as a checklist during code review. Verify that each identified threat has a corresponding mitigation implemented in code. Automated static analysis tools can catch some categories of vulnerability (such as SQL injection or hardcoded credentials) but cannot replace the judgment applied during threat modeling.
- **Testing phase**: Derive security test cases directly from the threat model. Each identified threat should have at least one test that verifies the mitigation is effective. Include these tests in the CI/CD pipeline so that regressions are caught automatically.
- **Deployment phase**: Validate that production configurations match the security baseline defined in the threat model. Automated configuration scanning and infrastructure-as-code review help ensure that deployment does not introduce misconfigurations.
- **Operations phase**: Monitor production telemetry for indicators of the threats identified in the model. Update the threat model based on incidents, near-misses, and changes in the threat landscape. Schedule periodic reviews (quarterly for high-risk APIs, annually for lower-risk ones) to keep the model current.

The threat model is a living document. It should be version-controlled alongside the API specification and architecture diagrams, updated as the system evolves, and accessible to every engineer who works on the API. When threat modeling becomes a routine part of how APIs are designed, built, and operated, the organization's security posture improves not through reactive patching but through proactive design.
