# AWS CloudWatch Synthetics — Capabilities Reference
For CLI commands, see [cloudwatch-synthetics-cli.md](cloudwatch-synthetics-cli.md).

## What Is a Canary?

A canary is a configurable script that runs on a schedule as a Lambda function in your account. It simulates customer actions to continuously monitor endpoints and APIs for availability, latency, and correctness — before real users are affected. Canaries publish metrics to CloudWatch namespace `CloudWatchSynthetics`, upload artifacts (screenshots, HAR files, logs) to S3, and optionally integrate with X-Ray.

---

## Blueprints

| Blueprint | Description | Playwright Support |
|---|---|---|
| **Heartbeat Monitor** | Loads one or more URLs; captures screenshot and HAR; logs load time and status | Yes |
| **API Canary** | Tests REST read/write operations; supports multiple APIs per canary | No |
| **Broken Link Checker** | Crawls page links; detects 404s, invalid hostnames, bad HTTP codes, timeouts | No |
| **Visual Monitoring** | Compares screenshots against a baseline run; fails on configurable variance % | Yes (3.0+) |
| **Canary Recorder** | Chrome browser extension records user interactions → generates Node.js script | No |
| **GUI Workflow Builder** | Configures steps (click, input, verify selector/text) without scripting | Yes |
| **Multi Checks (2025)** | Up to 10 monitoring steps in one JSON config; HTTP, DNS, SSL cert, TCP port checks; no scripting required | — |

---

## Runtime Families

| Family | Browser |
|---|---|
| `syn-nodejs-puppeteer-X.X` | Puppeteer (Chrome; Firefox from v11+) |
| `syn-nodejs-playwright-X.X` | Playwright (Chrome; Firefox from v3+) — does NOT support API canary, broken link, or recorder blueprints |
| `syn-python-selenium-X.X` | Selenium (Chrome only) — does NOT support visual monitoring |

### Current Recommended Versions (as of 2026)

| Runtime | Node/Python | Notes |
|---|---|---|
| `syn-nodejs-puppeteer-15.0` | Node 22.x | Latest; Puppeteer 24.37.5, Chrome 145 |
| `syn-nodejs-playwright-6.0` | Node 22.x | Latest; Playwright 1.58.2, Chrome 145 |
| `syn-python-selenium-10.0` | Python 3.11 | Latest; Selenium 4.32.0, Chrome 145 |

**Breaking change — v13.1 (Puppeteer) / v5.1 (Playwright):** Require `@aws/synthetics-puppeteer` / `@aws/synthetics-playwright` namespaces. Old `require('Synthetics')` breaks.

**AWS SDK:** `syn-nodejs-puppeteer-7.0+` requires SDK V3; V2 is unavailable in those runtimes.

**Visual monitoring:** Not supported in `syn-nodejs-puppeteer-8.0` — use 9.0+.

**Deprecated:** Puppeteer 3.x–5.x, Selenium 2.x–3.x.

---

## Configuration

### Schedule
- Rate: `rate(5 minutes)`, `rate(1 hour)`, `rate(1 day)`
- Cron: `cron(0 12 * * ? *)`
- `DurationInSeconds: 0` = run continuously (default); non-zero = auto-stop after N seconds

### Retention
| Parameter | Default | Range |
|---|---|---|
| `--success-retention-period-in-days` | 31 | 1–455 |
| `--failure-retention-period-in-days` | 31 | 1–455 |

### Run Config (`--run-config`)
```json
{
  "TimeoutInSeconds": 60,
  "MemoryInMB": 960,
  "ActiveTracing": true,
  "EnvironmentVariables": {
    "APP_URL": "https://example.com",
    "SECRET_NAME": "prod/myapp/creds"
  },
  "EphemeralStorage": 1024
}
```
- `TimeoutInSeconds`: 3–840
- `MemoryInMB`: 960–3008; must be multiple of 64
- `EphemeralStorage`: 1024–10240 MB
- `ActiveTracing`: X-Ray integration; requires `syn-nodejs-2.0+` and xray permissions in execution role

### Environment Variables
- Max total: 4 KB; start with letter; 2+ characters; no Lambda reserved names
- Never store secrets directly — use Secrets Manager references via `process.env.SECRET_NAME`

### Artifact Storage
- Specified as `s3://bucket-name/prefix` in `--artifact-s3-location`
- **Bucket name cannot contain periods** (breaks SSL)
- Stores: screenshots (PNG), HAR files, logs (`*-log.txt`)
- Synthetics auto-uploads `/tmp` contents after each run

### Artifact Encryption
```json
{ "S3Encryption": { "EncryptionMode": "SSE_KMS", "KmsKeyArn": "arn:aws:kms:..." } }
```
Options: `SSE_S3` or `SSE_KMS`

### VPC Configuration
To run canaries inside a VPC:
- VPC must have DNS Resolution and DNS Hostnames enabled
- Internet access: NAT Gateway in public subnet, or egress-only internet gateway (IPv6)
- For fully private VPCs: add interface endpoint `com.amazonaws.<region>.monitoring` and S3 gateway endpoint for artifact upload

### Retry Configuration (2025)
```json
{
  "Expression": "rate(5 minutes)",
  "RetryConfig": { "MaxRetries": 2 }
}
```
0–2 retries on failure. Retries cost same as regular runs. `SuccessPercentWithRetries` metric captures final outcome.

---

## Script Structure

### Node.js (Puppeteer)
```javascript
const synthetics = require('@aws/synthetics-puppeteer');  // v13.1+ namespace

const canary = async function () {
    const page = await synthetics.getPage();  // instrumented Puppeteer Page

    await synthetics.executeStep('loadPage', async () => {
        await page.goto('https://example.com', { waitUntil: 'networkidle0' });
    });

    await synthetics.executeStep('verifyContent', async () => {
        const title = await page.title();
        if (!title) throw new Error('No page title');
    });
};

exports.handler = async () => await canary();
```

**Key library functions:**
- `synthetics.getPage()` — instrumented Puppeteer Page (auto-logs requests, generates HAR, adds canary ARN to user-agent)
- `synthetics.executeStep(name, fn, [config])` — step with logging, screenshots, and metrics
- `synthetics.executeHttpStep(name, reqOptions, [callback], [config])` — HTTP request with metrics
- `synthetics.takeScreenshot(name, suffix)` — saves PNG to S3
- `synthetics.addExecutionError(msg, ex)` — records error without stopping

**SyntheticsConfiguration (global defaults):**
```javascript
synthetics.getConfiguration().setConfig({
    continueOnStepFailure: false,
    continueOnHttpStepFailure: true,
    screenshotOnStepStart: true,
    screenshotOnStepSuccess: true,
    screenshotOnStepFailure: true,
    restrictedHeaders: ['Authorization', 'X-Amz-Security-Token'],
    restrictedUrlParameters: ['access_token'],
    harFile: true
});
```

**Visual monitoring config:**
```javascript
synthetics.getConfiguration().withVisualCompareWithBaseRun(true)
    .withVisualVarianceThresholdPercentage(5)
    .withFailCanaryRunOnVisualVariance(true);
```

### Python (Selenium)
```python
from aws_synthetics.selenium import synthetics_webdriver as webdriver

def handler(event, context):
    browser = webdriver.Chrome()
    browser.get('https://example.com')
    browser.save_screenshot('/tmp/loaded.png')
```
- `syn-python-selenium-1.1+` and Node.js `3.4+`: handler can have any name; specify as `filename.functionName` in the handler field
- Python canary scripts must be in a `python/` directory within the ZIP

---

## Metrics

**Namespace:** `CloudWatchSynthetics`
**Dimensions:** `CanaryName` (always); `StepName` (when using executeStep/executeHttpStep); `Browser` (multi-browser canaries)

| Metric | Description | Stat |
|---|---|---|
| `SuccessPercent` | % of runs that succeeded | Average |
| `SuccessPercentWithRetries` | % succeeded after all retries | Average |
| `Duration` | Canary execution time | Average (ms) |
| `Failed` | Count of failed runs | Sum |
| `Failed requests` | Count of failed HTTP requests | Sum |
| `RetryCount` | Number of retry attempts | Sum |
| `2xx` / `4xx` / `5xx` | HTTP response code counts | Sum |
| `VisualMonitoringSuccessPercent` | Screenshot comparison match rate | Average |
| `EphemeralStorageUsagePercent` | Max ephemeral storage used | — |

---

## Visual Monitoring

- Powered by ImageMagick; first successful run becomes the baseline
- Update baseline: via console or `UpdateCanary` API (`nextrun`, `lastrun`, or specific run ID)
- Draw exclusion boundaries on baseline image to ignore dynamic content areas
- **Supported:** `syn-nodejs-puppeteer-3.2+`, `syn-nodejs-playwright-3.0+`
- **Not supported:** Python Selenium, Playwright v1/v2, Puppeteer 8.0

---

## Canary Groups

- **Global resource** (region-agnostic); up to 10 canaries per group; canaries from any region can be added
- Aggregates Duration, SuccessPercent, errors across all canaries in a single dashboard view
- No additional cost to create groups

---

## Safe Canary Updates (Dry Run, 2025)

- Executes canary script once with proposed changes without modifying the live canary or publishing metrics
- **Supported runtimes:** `syn-nodejs-puppeteer-10.0+`, `syn-nodejs-playwright-2.0+`, `syn-python-selenium-5.1+`
- Only one dry run per canary at a time; cannot test Schedule changes
- CloudFormation: `DryRunAndUpdate: true` runs a dry run before every stack update

---

## IAM Roles

Two separate roles:

**Execution role** (what the canary Lambda runs as) — minimum permissions:

| Service | Permission |
|---|---|
| S3 | `s3:PutObject`, `s3:GetObject`, `s3:GetBucketLocation`, `s3:ListBucket` on `cw-syn-results-*` and artifact bucket |
| CloudWatch | `cloudwatch:PutMetricData` scoped to `CloudWatchSynthetics` namespace |
| CloudWatch Logs | `logs:CreateLogGroup`, `logs:CreateLogStream`, `logs:PutLogEvents` on `/aws/lambda/cwsyn-*` |
| X-Ray (if tracing) | `xray:PutTraceSegments`, `xray:PutTelemetryRecords` |
| Secrets Manager (if used) | `secretsmanager:GetSecretValue` on the specific secret ARN |
| VPC (if in VPC) | `ec2:CreateNetworkInterface`, `ec2:DescribeNetworkInterfaces`, `ec2:DeleteNetworkInterface` |

**Management role** (for creating/managing canaries) — AWS managed policies: `CloudWatchSyntheticsFullAccess` or `CloudWatchSyntheticsReadOnlyAccess`

---

## Security Best Practices

- Store secrets in Secrets Manager; reference via `process.env.SECRET_NAME` — never hardcode
- Use `restrictedHeaders` and `restrictedUrlParameters` to prevent credential leakage in HAR/logs
- Store canary scripts in S3 (versioned) rather than ZIP — prevents script content appearing in CloudTrail
- Use `getSanitizedUrl()` and `getSanitizedErrorMessage()` before logging
- Request/response headers and bodies are NOT logged by default (`syn-nodejs-puppeteer-3.2+`)
- The canary ARN appears in outbound HTTP User-Agent headers — do not encode secrets in canary names

---

## Pricing

- **$0.0012 per canary run** (free tier: 100 runs/month)
- Dry runs and retries priced the same as regular runs
- Additional costs at standard rates: Lambda execution, S3 artifact storage, CloudWatch Logs, CloudWatch custom metrics

**Example:** 5 canaries × every 5 minutes = ~44,640 runs/month ≈ **$53.57/month** (after free tier)

---

## Common Gotchas

1. **S3 bucket name with periods** — artifact bucket names cannot contain periods (breaks SSL)
2. **AWS SDK V2 unavailable** in `syn-nodejs-puppeteer-7.0+` — must use SDK V3
3. **Visual monitoring missing** in `syn-nodejs-puppeteer-8.0` — use 9.0+
4. **ZIP size limit** — 225 KB max for API upload; larger scripts must be uploaded to S3 first
5. **Namespace change** — `require('Synthetics')` breaks in Puppeteer v13.1+ and Playwright v5.1+
6. **Playwright limitations** — no API canary blueprint, broken link checker, or Chrome recorder
7. **Python handler naming** — `handler` required in v1.0; any name allowed in v1.1+
8. **Max 4 KB environment variables** — use S3 for larger config files
