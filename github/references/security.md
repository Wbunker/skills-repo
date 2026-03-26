# GitHub Security Features Reference

## Branch Protection

### Branch Protection Rules

Configure via **Settings > Branches > Add rule** or the REST API. Rules match branches by name pattern (supports wildcards).

| Setting | Description |
|---|---|
| `required_status_checks` | CI checks that must pass before merging |
| `strict` (status checks) | Branch must be up to date before merging |
| `required_pull_request_reviews` | Require PR reviews before merging |
| `required_approving_review_count` | Number of approvals required (0–6) |
| `dismiss_stale_reviews` | Re-require review after new commits are pushed |
| `require_code_owner_reviews` | Require review from CODEOWNERS file owners |
| `require_last_push_approval` | Last pusher cannot approve their own PR |
| `restrictions` | Limit who can push to the branch (users/teams/apps) |
| `required_linear_history` | Disallow merge commits; require squash or rebase |
| `required_signatures` | Require signed commits (GPG/SSH) |
| `allow_force_pushes` | Allow force pushes to the branch |
| `allow_deletions` | Allow deletion of the branch |
| `lock_branch` | Make branch read-only |
| `enforce_admins` | Apply rules to admins as well |

### Branch Protection REST API

Base path: `/repos/{owner}/{repo}/branches/{branch}/protection`

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `.../protection` | Get all protection settings |
| `PUT` | `.../protection` | Update (replace) all protection settings |
| `DELETE` | `.../protection` | Remove all protection |
| `GET` | `.../protection/required_status_checks` | Get required status checks |
| `PATCH` | `.../protection/required_status_checks` | Update required status checks |
| `DELETE` | `.../protection/required_status_checks` | Remove required status checks |
| `GET` | `.../protection/required_pull_request_reviews` | Get PR review requirements |
| `PATCH` | `.../protection/required_pull_request_reviews` | Update PR review requirements |
| `DELETE` | `.../protection/required_pull_request_reviews` | Remove PR review requirements |
| `GET` | `.../protection/restrictions` | Get push restrictions |
| `DELETE` | `.../protection/restrictions` | Remove push restrictions |

```bash
# Get branch protection
gh api repos/{owner}/{repo}/branches/main/protection

# Update: require 2 approvals + passing CI
gh api repos/{owner}/{repo}/branches/main/protection \
  --method PUT \
  --field required_status_checks='{"strict":true,"contexts":["ci/tests"]}' \
  --field required_pull_request_reviews='{"required_approving_review_count":2,"dismiss_stale_reviews":true}' \
  --field enforce_admins=true \
  --field restrictions=null
```

### Rulesets (Newer System)

Rulesets replace and extend branch protection rules. They can target branches and tags, apply at repo or org level, and support bypass actors.

**Key differences from branch protection rules:**
- Multiple rulesets can apply to the same branch (rules are merged)
- Org-level rulesets cascade to all repos
- Bypass actors: specific users, teams, or apps can bypass rules
- Enforcement modes: `active`, `evaluate` (log only), `disabled`

**Ruleset REST API:**

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/repos/{owner}/{repo}/rulesets` | List repo rulesets |
| `POST` | `/repos/{owner}/{repo}/rulesets` | Create repo ruleset |
| `GET` | `/repos/{owner}/{repo}/rulesets/{ruleset_id}` | Get repo ruleset |
| `PUT` | `/repos/{owner}/{repo}/rulesets/{ruleset_id}` | Update repo ruleset |
| `DELETE` | `/repos/{owner}/{repo}/rulesets/{ruleset_id}` | Delete repo ruleset |
| `GET` | `/orgs/{org}/rulesets` | List org rulesets |
| `POST` | `/orgs/{org}/rulesets` | Create org ruleset |

```json
{
  "name": "main-protection",
  "target": "branch",
  "enforcement": "active",
  "bypass_actors": [
    { "actor_id": 1, "actor_type": "OrganizationAdmin", "bypass_mode": "always" }
  ],
  "conditions": { "ref_name": { "include": ["refs/heads/main"], "exclude": [] } },
  "rules": [
    { "type": "required_linear_history" },
    { "type": "required_signatures" },
    { "type": "pull_request", "parameters": { "required_approving_review_count": 1 } }
  ]
}
```

---

## Code Scanning

### Alerts REST API

Base: `/repos/{owner}/{repo}/code-scanning/alerts`

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `.../alerts` | List all alerts |
| `GET` | `.../alerts/{alert_number}` | Get a specific alert |
| `PATCH` | `.../alerts/{alert_number}` | Dismiss or reopen an alert |
| `DELETE` | `.../alerts/{alert_number}` | Delete an alert (admins only) |
| `GET` | `.../analyses` | List analyses |
| `GET` | `.../analyses/{analysis_id}` | Get an analysis |
| `DELETE` | `.../analyses/{analysis_id}` | Delete an analysis |

**Query parameters for listing:**
- `state`: `open`, `dismissed`, `fixed`
- `severity`: `critical`, `high`, `medium`, `low`, `warning`, `note`, `error`
- `tool_name`: filter by scanner (e.g., `CodeQL`)
- `ref`: branch/tag ref

### Alert Object Fields

| Field | Description |
|---|---|
| `number` | Alert number (unique per repo) |
| `state` | `open`, `dismissed`, `fixed` |
| `dismissed_reason` | `false positive`, `won't fix`, `used in tests` |
| `dismissed_comment` | Free-text explanation |
| `rule.id` | Rule identifier (e.g., `js/sql-injection`) |
| `rule.severity` | `error`, `warning`, `note` |
| `rule.security_severity_level` | `critical`, `high`, `medium`, `low` |
| `rule.description` | Human-readable rule name |
| `tool.name` | Scanner name (e.g., `CodeQL`) |
| `tool.version` | Scanner version |
| `most_recent_instance.ref` | Branch where alert was last seen |
| `most_recent_instance.location` | File path and line numbers |
| `most_recent_instance.message.text` | Alert message |

```bash
# Dismiss an alert
gh api repos/{owner}/{repo}/code-scanning/alerts/42 \
  --method PATCH \
  --field state=dismissed \
  --field dismissed_reason="false positive" \
  --field dismissed_comment="Sanitized upstream"
```

### SARIF Upload

Upload results from custom or third-party tools:

```bash
# POST /repos/{owner}/{repo}/code-scanning/sarifs
gh api repos/{owner}/{repo}/code-scanning/sarifs \
  --method POST \
  --field commit_sha=$(git rev-parse HEAD) \
  --field ref=refs/heads/main \
  --field sarif=$(cat results.sarif | gzip | base64 -w0) \
  --field tool_name="my-scanner"
```

SARIF must be gzip-compressed and base64-encoded. Response includes a `id` to poll upload status at `.../sarifs/{sarif_id}`.

### CodeQL and GitHub Actions

CodeQL is GitHub's semantic analysis engine. Integration via Actions:

```yaml
# .github/workflows/codeql.yml
jobs:
  analyze:
    uses: github/codeql-action/init@v3  # Initialize CodeQL
    with:
      languages: javascript, python     # Languages to analyze

    # ... build steps (auto-detected for interpreted languages) ...

    uses: github/codeql-action/analyze@v3  # Run analysis + upload SARIF
```

- Results appear under **Security > Code scanning alerts**
- Supports: C/C++, C#, Go, Java/Kotlin, JavaScript/TypeScript, Python, Ruby, Swift
- Custom queries: add `.ql` files or query packs to the workflow
- `autobuild` step compiles compiled languages automatically

---

## Secret Scanning

### Alerts REST API

Base: `/repos/{owner}/{repo}/secret-scanning/alerts`

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `.../alerts` | List secret scanning alerts |
| `GET` | `.../alerts/{alert_number}` | Get a specific alert |
| `PATCH` | `.../alerts/{alert_number}` | Resolve or reopen an alert |
| `GET` | `.../alerts/{alert_number}/locations` | Get commit locations for a secret |

**Query parameters:** `state` (`open`/`resolved`), `secret_type`, `resolution`

### Alert Object Fields

| Field | Description |
|---|---|
| `number` | Alert number |
| `state` | `open` or `resolved` |
| `secret_type` | Pattern identifier (e.g., `github_personal_access_token`) |
| `secret_type_display_name` | Human-readable type name |
| `secret` | The actual detected secret value |
| `resolution` | `false_positive`, `wont_fix`, `revoked`, `used_in_tests`, `pattern_deleted`, `pattern_edited` |
| `resolved_by` | User who resolved the alert |
| `resolved_at` | ISO 8601 timestamp |
| `push_protection_bypassed` | Whether push protection was bypassed |
| `push_protection_bypassed_by` | User who bypassed push protection |

```bash
# Resolve a secret scanning alert
gh api repos/{owner}/{repo}/secret-scanning/alerts/7 \
  --method PATCH \
  --field state=resolved \
  --field resolution=revoked
```

### Push Protection

Blocks pushes containing known secret patterns before they reach the remote. Users may bypass with a reason:
- `false_positive`
- `used_in_tests`
- `will_fix_later`

Bypass events are logged and visible in the alert. Enable at org or repo level under **Settings > Security > Secret scanning > Push protection**.

### Custom Patterns

Org-level custom patterns let you define proprietary secret formats using regular expressions.

```bash
# Create org-level custom pattern
gh api orgs/{org}/secret-scanning/patterns \
  --method POST \
  --field name="internal-api-key" \
  --field pattern='MYCO-[A-Z0-9]{32}' \
  --field secret_type="internal_api_key"
```

Custom patterns support `pattern` (regex), optional `before_secret` / `after_secret` context anchors, and test strings for validation before publishing.

---

## Dependabot

### Alerts REST API

Base: `/repos/{owner}/{repo}/dependabot/alerts`

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `.../alerts` | List Dependabot alerts |
| `GET` | `.../alerts/{alert_number}` | Get a specific alert |
| `PATCH` | `.../alerts/{alert_number}` | Dismiss or reopen an alert |

**Query parameters:** `state` (`open`/`dismissed`/`fixed`/`auto_dismissed`), `severity`, `ecosystem`, `package`, `scope` (`runtime`/`development`)

### Alert Object Fields

| Field | Description |
|---|---|
| `number` | Alert number |
| `state` | `open`, `dismissed`, `fixed`, `auto_dismissed` |
| `dependency.package.name` | Package name |
| `dependency.package.ecosystem` | `npm`, `pip`, `maven`, `rubygems`, `nuget`, `cargo`, etc. |
| `dependency.manifest_path` | Path to the manifest file (e.g., `package-lock.json`) |
| `dependency.scope` | `runtime` or `development` |
| `security_advisory.ghsa_id` | GitHub Security Advisory ID |
| `security_advisory.severity` | `critical`, `high`, `medium`, `low` |
| `security_advisory.cvss_score` | CVSS numeric score |
| `security_advisory.cve_ids` | List of CVE identifiers |
| `security_advisory.summary` | Short description |
| `security_vulnerability.vulnerable_version_range` | Affected versions |
| `security_vulnerability.first_patched_version` | Earliest safe version |
| `dismissed_reason` | `tolerable_risk`, `no_bandwidth`, `inaccurate`, `not_used` |
| `auto_dismissed_at` | When auto-dismiss fired (if applicable) |

```bash
# Dismiss a Dependabot alert
gh api repos/{owner}/{repo}/dependabot/alerts/12 \
  --method PATCH \
  --field state=dismissed \
  --field dismissed_reason=tolerable_risk \
  --field dismissed_comment="Dependency not reachable in production"
```

### Security Updates vs. Version Updates

| Feature | Security Updates | Version Updates |
|---|---|---|
| Purpose | Fix vulnerable dependencies | Keep dependencies current |
| Trigger | New vulnerability advisory | Schedule-based or on manifest change |
| PR target | Minimum safe version | Latest version (per strategy) |
| Config required | None (auto-enabled with alerts) | `dependabot.yml` required |

### dependabot.yml Configuration

Located at `.github/dependabot.yml`:

```yaml
version: 2
updates:
  - package-ecosystem: "npm"
    directory: "/"           # Location of package manifest
    schedule:
      interval: "weekly"     # daily | weekly | monthly
      day: "monday"
      time: "09:00"
      timezone: "America/New_York"
    open-pull-requests-limit: 10
    target-branch: "develop"
    labels: ["dependencies"]
    reviewers: ["my-team"]
    ignore:
      - dependency-name: "lodash"
        versions: ["4.x"]
    groups:
      dev-dependencies:
        patterns: ["eslint*", "prettier"]
        dependency-type: "development"

  - package-ecosystem: "github-actions"
    directory: "/"
    schedule:
      interval: "monthly"
```

---

## Security Advisories

### Repository Security Advisories

Used to privately report and coordinate vulnerability disclosures (CVD).

Base: `/repos/{owner}/{repo}/security-advisories`

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `.../security-advisories` | List repo security advisories |
| `POST` | `.../security-advisories` | Create a draft advisory |
| `GET` | `.../security-advisories/{ghsa_id}` | Get a specific advisory |
| `PATCH` | `.../security-advisories/{ghsa_id}` | Update an advisory |
| `POST` | `.../security-advisories/{ghsa_id}/publish` | Publish (make public) |
| `POST` | `/repos/{owner}/{repo}/security-advisories/reports` | Submit private vulnerability report |

### Advisory Object Fields

| Field | Description |
|---|---|
| `ghsa_id` | GitHub Security Advisory ID (e.g., `GHSA-xxxx-xxxx-xxxx`) |
| `cve_id` | Associated CVE (if requested/assigned) |
| `summary` | Short title (max 200 chars) |
| `description` | Full markdown description |
| `severity` | `critical`, `high`, `medium`, `low` (derived from CVSS or set manually) |
| `cvss` | Object with `vector_string` and `score` |
| `cwes` | Array of `{ cwe_id, name }` objects |
| `state` | `draft`, `published`, `withdrawn`, `triage` |
| `credits` | Array of `{ login, type }` — types: `reporter`, `finder`, `analyst`, `coordinator`, `remediation_developer`, etc. |
| `vulnerabilities` | Array of affected packages with `ecosystem`, `package_name`, `vulnerable_version_range`, `patched_versions` |
| `published_at` | ISO 8601 publish timestamp |

```bash
# Create a draft advisory
gh api repos/{owner}/{repo}/security-advisories \
  --method POST \
  --field summary="SQL injection in search endpoint" \
  --field description="An attacker can..." \
  --field severity=high \
  --field vulnerabilities='[{"package":{"ecosystem":"npm","name":"mylib"},"vulnerable_version_range":"< 2.1.0","patched_versions":"2.1.0"}]' \
  --field credits='[{"login":"reporter-user","type":"reporter"}]'

# Publish a draft advisory
gh api repos/{owner}/{repo}/security-advisories/GHSA-xxxx-xxxx-xxxx/publish \
  --method POST
```

### Global (Public) Advisories

Read-only public database of all published security advisories.

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/advisories` | List global advisories |
| `GET` | `/advisories/{ghsa_id}` | Get a specific global advisory |

**Query parameters for listing:** `type` (`reviewed`/`unreviewed`/`malware`), `cve_id`, `ecosystem`, `severity`, `affects` (package name), `published`, `updated`, `modified`

Global advisory objects include the same CVSS, CWEs, and credits fields as repository advisories, plus `references` (array of URLs) and `source_code_location`.
