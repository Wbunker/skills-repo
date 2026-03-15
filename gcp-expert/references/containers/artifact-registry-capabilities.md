# Artifact Registry — Capabilities

## Purpose and Overview

Artifact Registry is GCP's unified managed service for storing and managing build artifacts. It replaces the legacy Container Registry (`gcr.io`) and extends it to support a wide variety of artifact formats beyond Docker images. Artifact Registry is deeply integrated with GCP security (CMEK, VPC-SC, IAM), build services (Cloud Build), and deployment targets (GKE, Cloud Run).

**Migration from Container Registry**: Google has deprecated `gcr.io` Container Registry. Artifacts stored at `gcr.io/PROJECT_ID/IMAGE` should be migrated to `REGION-docker.pkg.dev/PROJECT_ID/REPO/IMAGE`. Cloud Build projects using `gcr.io` as the default registry should update references to Artifact Registry. Google provides a `gcr.io` redirection feature that can route `gcr.io` reads to Artifact Registry during migration.

---

## Supported Artifact Formats

### Docker (Container Images)
- Standard OCI/Docker image storage.
- Multi-arch manifests (image index) for multi-platform images.
- Image layers deduplicated across tags in the same repository.
- Digest-based (`@sha256:...`) and tag-based pulls.
- Repository URL: `REGION-docker.pkg.dev/PROJECT_ID/REPO_NAME/IMAGE_NAME:TAG`

### Maven (Java)
- Store JARs, WARs, POM files.
- Standard Maven repository protocol.
- Configure `~/.m2/settings.xml` or `build.gradle` to use Artifact Registry as a Maven repo.
- Supports release and SNAPSHOT artifacts.

### npm (Node.js)
- Store npm packages (`.tgz`).
- Configure `.npmrc` with authentication to pull from and publish to Artifact Registry.
- Supports scoped packages (`@my-org/my-package`).

### Python (PyPI)
- Store Python wheels (`.whl`) and source distributions (`.tar.gz`).
- Configure `pip` or `twine` with Artifact Registry index URL.
- Authentication via `keyring` or `~/.netrc`.

### Go Modules
- Store Go module proxies.
- Configure `GOPROXY=https://REGION-go.pkg.dev/PROJECT_ID/REPO_NAME,direct`.
- Private module hosting without exposing source code.

### Helm Charts
- OCI-compliant Helm chart storage.
- `helm push` and `helm pull` from `oci://REGION-docker.pkg.dev/PROJECT_ID/REPO_NAME`.
- `helm registry login` with `gcloud auth print-access-token` as password.

### Apt (Debian/Ubuntu packages)
- Host internal Debian packages.
- Configure `/etc/apt/sources.list.d/` to point to Artifact Registry.
- Useful for distributing internal tools as deb packages.

### Yum (RPM packages)
- Host internal RPM packages for RHEL/CentOS/Fedora.
- Configure `/etc/yum.repos.d/` with Artifact Registry repo URL.

### Generic Files
- Store arbitrary binary files, zip archives, tarballs.
- No format-specific protocol; use `gcloud artifacts generic upload/download`.
- Use for: release binaries, compiled WASM files, model weights, data files.

---

## Repository Types

### Standard Repository
The default repository type. Stores artifacts you push directly. You have full write access and control over what is stored. Used for your own build outputs (container images, packages).

### Remote Repository
Acts as a proxy and cache for an upstream registry or package index. Supported upstreams:
- **Docker Hub**: `docker.io`
- **Google Container Registry**: `gcr.io`
- **GitHub Container Registry**: `ghcr.io`
- **Quay.io**: `quay.io`
- **Maven Central**: `https://repo1.maven.org/maven2/`
- **PyPI**: `https://pypi.org`
- **npm**: `https://registry.npmjs.org`
- **Helm Hub (Artifact Hub)**
- Any custom upstream with authentication

**Benefits of remote repositories**:
- Cache upstream artifacts in your region — faster pulls, no external network dependency.
- Apply Artifact Registry security policies (VPC-SC, IAM) to upstream pulls.
- Vulnerability scanning on cached images.
- Guaranteed availability even if Docker Hub rate-limits or has an outage.
- Audit log of all upstream pulls.

### Virtual Repository
An aggregation layer over multiple upstream repositories (standard and/or remote). Consumers configure a single repository URL; Artifact Registry searches the configured upstreams in priority order to resolve artifact requests.

**Use cases**:
- Provide developers a single endpoint that checks your internal standard repo first, then a cached Docker Hub remote, then the live registry.
- Gradually migrate from an old repo to a new one (both listed in virtual repo; new repo has higher priority).

---

## Regions and Location Strategy

- **Regional**: a repository in a single GCP region (e.g., `us-central1`). Lowest latency for workloads in that region. Best for single-region GKE clusters and Cloud Run services.
- **Multi-regional**: a repository in a multi-region location (US, europe, asia). Google replicates data across zones within that multi-region. Accessible from any region in the multi-region with improved latency.
- **Repository location should match your primary build and deploy region**: Cloud Build in `us-central1` pushing to `us-central1-docker.pkg.dev` avoids inter-region egress costs. GKE in `us-central1` pulling from `us-central1-docker.pkg.dev` is the fastest path.

---

## Security

### IAM

Artifact Registry uses standard GCP IAM. Key roles:
- `roles/artifactregistry.reader`: pull images, read artifacts.
- `roles/artifactregistry.writer`: push artifacts (in addition to reader permissions).
- `roles/artifactregistry.repoAdmin`: manage repository settings, cleanup policies, tags.
- `roles/artifactregistry.admin`: create and delete repositories; all repo admin permissions.

Grant IAM at the **repository level** (not project level) for least-privilege: give GKE node service accounts `reader` on specific repos; give CI service accounts `writer` on specific repos.

### CMEK (Customer-Managed Encryption Keys)

By default, artifacts are encrypted with Google-managed keys. For regulatory compliance, configure CMEK using Cloud KMS to manage your own encryption keys. Specify the KMS key at repository creation time — cannot be changed after creation.

### VPC Service Controls

Artifact Registry supports VPC Service Controls (VPC-SC). Adding Artifact Registry to a VPC-SC perimeter blocks access from outside the perimeter (e.g., blocks public internet pushes/pulls; only allows access from within the perimeter's VPC). Use for high-security environments where all artifact access must be from within the corporate network.

### Binary Authorization Integration

Container Analysis vulnerability data and attestations from Cloud Build are associated with images in Artifact Registry. Binary Authorization policies reference these attestations to control which images can be deployed to GKE.

---

## Container Analysis and Vulnerability Scanning

Artifact Registry integrates with Container Analysis (part of Artifact Analysis API) for automated vulnerability scanning:

- **On-push scanning**: automatically triggered when a new image is pushed to the repository. Scans the OS packages and language packages (Python, Node.js, Java, Go) within the image layers.
- **On-demand scanning**: `gcloud artifacts docker images scan` for scanning before push (in CI pipeline, to fail the build on critical CVEs).
- **Continuous scanning**: `--scanning-mode=ALWAYS_ON` rescans stored images daily against updated CVE databases.

**Vulnerability data**:
- Source: OS vendor advisories (Debian, Ubuntu, RHEL, Alpine), NVD (National Vulnerability Database), GitHub Security Advisories.
- Severity: CRITICAL, HIGH, MEDIUM, LOW, MINIMAL.
- Fixed/unfixed status: shows whether a patched version is available.
- Integration with Security Command Center: vulnerabilities surface in SCC findings.

---

## Cleanup Policies

Cleanup policies automatically delete old artifact versions based on configured rules, reducing storage costs and keeping repositories tidy.

**Condition types**:
- `TAG_STATE=TAGGED`: only tagged versions; `UNTAGGED`: only untagged.
- `OLDER_THAN`: delete versions older than a duration (e.g., `30d`).
- `TAG_PREFIXES`: match versions whose tags start with specified prefixes (e.g., `dev-`, `branch-`).
- `PACKAGE_NAME_PREFIXES`: match package names.
- `VERSION_NAME_PREFIXES`: match version names.

**Keep policy**: a keep policy can exempt certain versions from deletion (e.g., keep the 5 most recent versions of each tag). Keep policies take precedence over delete policies.

**Example use case**: delete untagged images older than 7 days (post-build digest accumulation); keep the 10 most recent tagged releases; delete versions with `dev-` tag prefix older than 24 hours.

---

## gcr.io Migration

The `gcr.io`, `us.gcr.io`, `eu.gcr.io`, and `asia.gcr.io` hostnames are deprecated. To migrate:

1. Create Artifact Registry repositories in the equivalent regions.
2. Copy existing images using `gcloud artifacts docker images copy` or `gcrane copy`.
3. Update Cloud Build configuration, Kubernetes manifests, Helm charts, and Cloud Run deployments to use the new `REGION-docker.pkg.dev` URLs.
4. Optionally enable `gcr.io` redirects: `gcloud artifacts settings enable-upgrade-redirection` — this makes `gcr.io/PROJECT_ID/IMAGE` reads redirect to Artifact Registry.
