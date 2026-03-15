# AWS ECR — Capabilities Reference
For CLI commands, see [ecr-cli.md](ecr-cli.md).

## Amazon ECR

**Purpose**: Managed container image registry; store, manage, and deploy Docker and OCI container images and artifacts.

### Key Concepts

| Concept | Description |
|---|---|
| **Registry** | One private registry per AWS account per region; endpoint: `<account-id>.dkr.ecr.<region>.amazonaws.com` |
| **Repository** | Stores container images or OCI artifacts; supports tag immutability and encryption (AES-256 or KMS CMK) |
| **ECR Public** | Public gallery at `public.ecr.aws`; share images publicly; no authentication required for pulls |
| **Image tag immutability** | Prevent existing tags from being overwritten; forces use of new tags for new image versions |
| **OCI artifact support** | Store Helm charts, WASM modules, and other OCI-compatible artifacts alongside container images |

### Lifecycle Policies

Define rules to automatically expire images and reduce storage costs:

| Rule type | Example use |
|---|---|
| **Expire untagged images** | Remove untagged images older than N days |
| **Keep last N tagged** | Retain only the most recent N images matching a tag prefix |
| **Expire by age** | Remove images with a specific tag prefix older than N days |

Rules are evaluated in priority order; use `start-lifecycle-policy-preview` to dry-run before applying.

### Image Scanning

| Type | Description |
|---|---|
| **Basic scanning** | Uses open-source Clair; scans OS packages; triggered on push or on demand |
| **Enhanced scanning** | Powered by Amazon Inspector; OS + programming language packages; continuous re-scanning when new CVEs published; findings in Inspector console |

### Cross-Region and Cross-Account Replication

Configured at the registry level as replication rules:
- **Cross-region**: Replicate to specified regions in the same account
- **Cross-account**: Replicate to another AWS account (destination must set a registry policy granting the source account)
- Replication is asynchronous; new images and tags are replicated automatically

### Pull-Through Cache

Cache images from upstream public registries (Docker Hub, Quay, GitHub Container Registry, Kubernetes registry, Amazon Linux) in your private ECR:
- Create a pull-through cache rule mapping an ECR repository prefix to an upstream registry URL
- First pull triggers caching; subsequent pulls serve from ECR
- Periodic sync keeps cached images current
- Apply lifecycle policies to manage storage of cached images

### Repository Creation Templates

Apply standard settings (tag immutability, encryption, lifecycle policy, repository policy, resource tags) automatically to newly created repositories — triggered by pull-through cache, create-on-push, or cross-account replication.

### Managed Image Signing

Automatically generates cryptographic signatures for images pushed to a repository (using AWS Signer). Verify signatures before deploying to ECS or EKS.
