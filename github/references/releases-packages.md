# GitHub Releases and Packages Reference

## Table of Contents
1. [Releases REST API](#1-releases-rest-api)
2. [Release Fields](#2-release-fields)
3. [Release Assets](#3-release-assets)
4. [Generating Release Notes](#4-generating-release-notes)
5. [Latest Release Behavior](#5-latest-release-behavior)
6. [gh CLI — Releases](#6-gh-cli--releases)
7. [Package Ecosystems](#7-package-ecosystems)
8. [ghcr.io — GitHub Container Registry](#8-ghcrio--github-container-registry)
9. [Packages REST API](#9-packages-rest-api)
10. [npm Registry](#10-npm-registry)
11. [Packages in GitHub Actions](#11-packages-in-github-actions)
12. [Package Permissions](#12-package-permissions)

---

## 1. Releases REST API

```http
# List
GET  /repos/{owner}/{repo}/releases                    # all releases (paginated)
GET  /repos/{owner}/{repo}/releases/latest             # most recent non-draft, non-prerelease
GET  /repos/{owner}/{repo}/releases/tags/{tag}         # release by exact tag
GET  /repos/{owner}/{repo}/releases/{release_id}       # by numeric ID

# Create / Update / Delete
POST   /repos/{owner}/{repo}/releases
PATCH  /repos/{owner}/{repo}/releases/{release_id}
DELETE /repos/{owner}/{repo}/releases/{release_id}

# Assets
GET    /repos/{owner}/{repo}/releases/{release_id}/assets
GET    /repos/{owner}/{repo}/releases/assets/{asset_id}
PATCH  /repos/{owner}/{repo}/releases/assets/{asset_id}   # rename/label only
DELETE /repos/{owner}/{repo}/releases/assets/{asset_id}

# Upload (uses upload_url from release response — different hostname)
POST   {upload_url}?name={filename}&label={label}
```

All endpoints require `Authorization: Bearer <token>`. Writes require the `contents:write` scope (classic PAT) or `contents: write` permission (fine-grained PAT / Actions token).

---

## 2. Release Fields

| Field | Type | Description |
|---|---|---|
| `tag_name` | string | **Required on create.** The Git tag (created if it doesn't exist). |
| `target_commitish` | string | Branch/SHA the tag is created from. Defaults to the repo's default branch. Ignored if the tag already exists. |
| `name` | string | Release title. Defaults to `tag_name` if omitted. |
| `body` | string | Markdown description. Can be auto-generated (see §4). |
| `draft` | boolean | `true` → unpublished draft; not visible without auth. Default `false`. |
| `prerelease` | boolean | `true` → marked as pre-release; excluded from `/releases/latest`. Default `false`. |
| `generate_release_notes` | boolean | Auto-populate `body` with changelog (see §4). Default `false`. |
| `make_latest` | string | `"true"`, `"false"`, or `"legacy"`. Controls the "latest" badge. Default `"true"` for non-pre-release non-draft. |
| `discussion_category_name` | string | Creates a linked Discussions post on publish. |

**Example — create release:**

```json
POST /repos/acme/myapp/releases
{
  "tag_name": "v1.4.0",
  "target_commitish": "main",
  "name": "v1.4.0 — Faster startup",
  "draft": false,
  "prerelease": false,
  "generate_release_notes": true
}
```

Response includes `id`, `upload_url`, `html_url`, `assets_url`, `tarball_url`, `zipball_url`, and the resolved `body`.

---

## 3. Release Assets

### Uploading

The `upload_url` in the release response is an RFC 6570 URI template:

```
https://uploads.github.com/repos/{owner}/{repo}/releases/{id}/assets{?name,label}
```

Strip the `{?name,label}` suffix and append query params manually:

```bash
curl -X POST \
  -H "Authorization: Bearer $GH_TOKEN" \
  -H "Content-Type: application/octet-stream" \
  --data-binary @myapp-linux-amd64.tar.gz \
  "https://uploads.github.com/repos/acme/myapp/releases/12345678/assets?name=myapp-linux-amd64.tar.gz&label=Linux+x86_64"
```

Key points:
- Use `Content-Type` matching the file type (e.g., `application/zip`, `application/octet-stream`, `image/png`).
- `name` is required; `label` is the human-readable display name (optional).
- Max asset size: **2 GB**.
- The upload URL uses `uploads.github.com`, not `api.github.com`.

### Downloading

Public release assets can be downloaded without auth:

```bash
# Via browser/redirect URL
GET /repos/{owner}/{repo}/releases/assets/{asset_id}
# Add header: Accept: application/octet-stream   (triggers redirect to S3)

# Direct URL (from asset object's browser_download_url field)
curl -L https://github.com/acme/myapp/releases/download/v1.4.0/myapp-linux-amd64.tar.gz
```

Private repos require auth:

```bash
curl -L -H "Authorization: Bearer $GH_TOKEN" \
  -H "Accept: application/octet-stream" \
  https://api.github.com/repos/acme/myapp/releases/assets/{asset_id}
```

---

## 4. Generating Release Notes

**Standalone endpoint** — returns notes without creating a release:

```http
POST /repos/{owner}/{repo}/releases/generate-notes
{
  "tag_name": "v1.4.0",
  "previous_tag_name": "v1.3.0",   # optional; inferred if omitted
  "target_commitish": "main",       # optional
  "configuration_file_path": ".github/release.yml"  # optional
}
```

Response: `{ "name": "v1.4.0", "body": "## What's Changed\n..." }`

**Inline on create/update:** set `"generate_release_notes": true` in the release body. The generated text fills `body` if `body` is not provided, or is **appended** if `body` is provided.

**Customising with `.github/release.yml`:**

```yaml
changelog:
  exclude:
    labels: [skip-changelog]
  categories:
    - title: "Breaking Changes"
      labels: [breaking]
    - title: "New Features"
      labels: [enhancement]
    - title: "Bug Fixes"
      labels: [bug]
```

---

## 5. Latest Release Behavior

| Endpoint | What it returns |
|---|---|
| `GET /releases/latest` | The single most-recent **published** (non-draft), **non-prerelease** release, by `published_at`. Returns 404 if none exist. |
| `GET /releases` | All releases ordered by `created_at` descending, including pre-releases and drafts (drafts only visible with write access). |
| `GET /releases/tags/{tag}` | Exact match on `tag_name`; includes drafts and pre-releases. |

The "latest" badge in the UI is controlled by `make_latest`. Setting it to `"false"` on a new release does not change which release holds the badge.

---

## 6. gh CLI — Releases

```bash
# Create
gh release create v1.4.0 ./dist/*.tar.gz ./dist/*.zip \
  --title "v1.4.0" \
  --notes "Changelog here" \
  --draft \
  --prerelease \
  --target main

# Auto-generate notes
gh release create v1.4.0 --generate-notes

# List
gh release list
gh release list --limit 10 --exclude-drafts --exclude-pre-releases

# View
gh release view v1.4.0
gh release view v1.4.0 --json assets,body,tagName

# Upload additional assets to existing release
gh release upload v1.4.0 ./extra-artifact.zip

# Download assets
gh release download v1.4.0                           # all assets
gh release download v1.4.0 --pattern "*.tar.gz"      # matching pattern
gh release download v1.4.0 --archive tar              # source archive

# Edit
gh release edit v1.4.0 --draft=false --latest

# Delete
gh release delete v1.4.0 --yes
gh release delete v1.4.0 --cleanup-tag --yes          # also delete the tag
```

---

## 7. Package Ecosystems

| Ecosystem | Registry URL | Config file |
|---|---|---|
| Docker/OCI | `ghcr.io` | — |
| npm | `npm.pkg.github.com` | `.npmrc` |
| Maven | `maven.pkg.github.com` | `pom.xml` / `settings.xml` |
| Gradle | `maven.pkg.github.com` | `build.gradle` |
| NuGet | `nuget.pkg.github.com` | `NuGet.Config` |
| RubyGems | `rubygems.pkg.github.com` | `.gemspec` / `~/.gem/credentials` |
| Composer (PHP) | `composer.pkg.github.com` | `composer.json` |

All package types share the same Packages REST API surface and permissions model.

---

## 8. ghcr.io — GitHub Container Registry

### Authentication

```bash
# PAT (classic): requires write:packages scope (includes read:packages)
echo $CR_PAT | docker login ghcr.io -u USERNAME --password-stdin

# Actions: use GITHUB_TOKEN directly
echo ${{ secrets.GITHUB_TOKEN }} | docker login ghcr.io \
  -u ${{ github.actor }} --password-stdin
```

For fine-grained PATs, grant **Read** or **Write** access to the target package (or inherit from the linked repository).

### Push and Pull

```bash
# Build and tag
docker build -t ghcr.io/OWNER/IMAGE_NAME:TAG .

# Push
docker push ghcr.io/OWNER/IMAGE_NAME:TAG
docker push ghcr.io/OWNER/IMAGE_NAME:latest

# Pull
docker pull ghcr.io/OWNER/IMAGE_NAME:TAG
```

`OWNER` is a GitHub username or organisation name (lowercase). Multi-arch manifests and OCI artifact types are supported.

### Image Naming

```
ghcr.io/<owner>/<image-name>:<tag>
ghcr.io/<owner>/<image-name>@sha256:<digest>
```

- Owner and image name are **case-insensitive** but stored lowercase.
- Slashes are allowed for namespacing: `ghcr.io/acme/backend/api:v2`.

### Linking Packages to Repositories

A container package is linked to a repository by setting the `org.opencontainers.image.source` OCI label:

```dockerfile
LABEL org.opencontainers.image.source=https://github.com/OWNER/REPO
```

Or via `docker buildx`:

```bash
docker buildx build \
  --label "org.opencontainers.image.source=https://github.com/acme/myapp" \
  -t ghcr.io/acme/myapp:latest .
```

Linking allows the package to inherit the repository's visibility and access settings.

### Visibility

| Visibility | Behaviour |
|---|---|
| **Private** | Default for new packages in private repos or orgs with private default. Requires auth to pull. |
| **Internal** | (Org only) Visible to all org members. |
| **Public** | Anyone can pull without auth. |

Change visibility via the package settings page or the REST API (`PATCH /user/packages/{type}/{name}` does not expose visibility — use the web UI or organisation settings).

---

## 9. Packages REST API

### List Packages

```http
GET /users/{username}/packages?package_type={type}
GET /orgs/{org}/packages?package_type={type}
GET /repos/{owner}/{repo}/packages           # packages linked to a repo (preview header required)
```

`package_type` values: `npm`, `maven`, `rubygems`, `docker`, `nuget`, `container`.

### Get and Delete a Package

```http
GET    /users/{username}/packages/{package_type}/{package_name}
GET    /orgs/{org}/packages/{package_type}/{package_name}
DELETE /users/{username}/packages/{package_type}/{package_name}
DELETE /orgs/{org}/packages/{package_type}/{package_name}
```

### Package Versions

```http
# List versions
GET    /users/{username}/packages/{package_type}/{package_name}/versions
GET    /orgs/{org}/packages/{package_type}/{package_name}/versions

# Get / Delete a specific version
GET    /users/{username}/packages/{package_type}/{package_name}/versions/{version_id}
DELETE /users/{username}/packages/{package_type}/{package_name}/versions/{version_id}
DELETE /orgs/{org}/packages/{package_type}/{package_name}/versions/{version_id}

# Restore a deleted version (within 30 days)
POST   /users/{username}/packages/{package_type}/{package_name}/versions/{version_id}/restore
POST   /orgs/{org}/packages/{package_type}/{package_name}/versions/{version_id}/restore
```

List versions supports `?state=active|deleted` query param.

---

## 10. npm Registry

### `.npmrc` Configuration

**Per-project** (`.npmrc` in repo root):

```ini
@OWNER:registry=https://npm.pkg.github.com
//npm.pkg.github.com/:_authToken=${NODE_AUTH_TOKEN}
```

**Global** (`~/.npmrc`):

```ini
//npm.pkg.github.com/:_authToken=ghp_xxxxxxxxxxxx
```

### `package.json`

```json
{
  "name": "@acme/my-package",
  "version": "1.0.0",
  "publishConfig": {
    "registry": "https://npm.pkg.github.com"
  }
}
```

The package name **must** be scoped to the owner: `@OWNER/package-name`.

### Publish and Install

```bash
npm publish                          # uses publishConfig registry
npm install @acme/my-package         # resolves via .npmrc scope mapping
```

---

## 11. Packages in GitHub Actions

`GITHUB_TOKEN` is automatically granted `read:packages` and, when the workflow is triggered in the package's linked repository, `write:packages`.

**Docker push example:**

```yaml
jobs:
  build-push:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write
    steps:
      - uses: actions/checkout@v4

      - name: Log in to GHCR
        uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Build and push
        uses: docker/build-push-action@v5
        with:
          push: true
          tags: ghcr.io/${{ github.repository_owner }}/myapp:${{ github.sha }}
```

**npm publish example:**

```yaml
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
          registry-url: 'https://npm.pkg.github.com'
          scope: '@acme'

      - run: npm publish
        env:
          NODE_AUTH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

`actions/setup-node` writes the `.npmrc` automatically when `registry-url` is set.

---

## 12. Package Permissions

### Permission Levels

| Level | Capabilities |
|---|---|
| **Read** | Pull/download packages |
| **Write** | Push/publish new versions |
| **Admin** | Manage settings, visibility, delete package |

### Inheritance and Overrides

- A package linked to a repository **inherits** the repository's collaborator access by default.
- Repository collaborators with `read` → package `read`; `write`/`maintain`/`admin` → package `write`.
- Inheritance can be **disabled** per package; then access is managed explicitly on the package settings page.
- Organisation-level: packages owned by an org respect team permissions granted on the package.
- `GITHUB_TOKEN` in Actions is limited to the permissions declared in the workflow's `permissions:` block. Always declare `packages: write` explicitly when pushing.

### Scopes for Classic PATs

| PAT Scope | Access |
|---|---|
| `read:packages` | Pull/download any package the user can see |
| `write:packages` | Push/publish; includes `read:packages` |
| `delete:packages` | Delete package versions; includes `read:packages` |

For packages in organisations with SSO enforced, the PAT must also be **SSO-authorised**.
