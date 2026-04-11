# Custom Channels

## Table of Contents
- [What custom channels are](#what-custom-channels-are)
- [CI/CD pipeline integration](#cicd-pipeline-integration)
- [Monitoring alert integration](#monitoring-alert-integration)
- [Custom event sources](#custom-event-sources)
- [Designing event payloads](#designing-event-payloads)

---

## What custom channels are

Beyond the first-party Telegram and Discord plugins, Channels supports wiring arbitrary external event sources into Claude Code. This means CI systems, monitoring platforms, deployment pipelines, or any system that can make an HTTP call can trigger Claude Code and receive a response.

Custom channel setup uses the same plugin architecture:
```
/plugin install <channel-name>@claude-plugins-official
```

Or via a custom plugin for self-managed event sources. Consult the official Channels documentation for the current plugin registry — the research preview may add new first-party integrations after this skill was written.

---

## CI/CD pipeline integration

**Pattern**: build fails → CI pushes event → Claude investigates logs → reports findings to your messaging channel.

### GitHub Actions example

Add a step at the end of your workflow that fires when the build fails:

```yaml
- name: Notify Claude on failure
  if: failure()
  run: |
    curl -X POST ${{ secrets.CLAUDE_CHANNELS_WEBHOOK_URL }} \
      -H "Content-Type: application/json" \
      -d '{
        "event": "ci_failure",
        "repo": "${{ github.repository }}",
        "branch": "${{ github.ref_name }}",
        "commit": "${{ github.sha }}",
        "run_url": "${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }}",
        "logs_url": "${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }}/logs"
      }'
```

Claude receives the payload, fetches the logs via `gh run view --log`, analyzes the failure, and reports findings to your Telegram or Discord.

### Useful context to include in CI payloads

- Repository and branch name
- Commit SHA and message
- Direct link to the failing run
- Which jobs/steps failed (if the CI system exposes this)
- Test output snippets if available (keeps Claude from having to fetch them)

### What Claude should do with a CI event

In your channel configuration or in a CLAUDE.md that governs Channels sessions, specify the expected behavior:

```
When you receive a ci_failure event:
1. Fetch the full logs with: gh run view <run_id> --log --repo <repo>
2. Identify the failing test or compilation error
3. Check if the same failure appeared in recent runs (flaky test signal)
4. Report: what failed, likely cause, whether it looks flaky, suggested fix
Keep the report to 3-5 bullet points. Send it to Telegram.
```

---

## Monitoring alert integration

**Pattern**: alert fires → monitoring platform pushes event → Claude triages → summary delivered.

### Datadog example

Use a Datadog Webhook Integration to call Claude Code's channel endpoint when a monitor triggers:

1. In Datadog, go to Integrations → Webhooks
2. Add a webhook with your Claude Channels endpoint URL
3. Payload template:
```json
{
  "event": "monitoring_alert",
  "monitor_name": "$EVENT_TITLE",
  "severity": "$ALERT_TRANSITION",
  "message": "$TEXT_ONLY_MSG",
  "tags": "$TAGS",
  "alert_url": "$LINK"
}
```

4. Attach the webhook to your monitors via the `@webhook-claude` notification handle

### PagerDuty / OpsGenie

Both support outbound webhooks on alert creation. The payload structure differs but the pattern is identical: configure the webhook URL, map alert fields to a JSON payload, Claude receives it.

### What Claude should do with a monitoring alert

```
When you receive a monitoring_alert event:
1. Read the alert context from the payload
2. Check recent logs in the affected service: tail -n 200 /var/log/<service>/app.log
3. Check error rate trend: look at the last 3 deployments in git log
4. Summarize: what the alert means, what you found in logs, whether it looks like a deployment regression
Send a Telegram message with severity, service, and your triage summary.
```

---

## Custom event sources

Any system that can POST JSON to an HTTP endpoint can become a Channels event source. Common examples:

**Deployment completion**:
```json
{ "event": "deploy_complete", "env": "staging", "version": "v2.3.1", "duration_seconds": 142 }
```
Claude responds by running smoke tests and reporting pass/fail.

**Long-running job completion** (data pipelines, ML training runs):
```json
{ "event": "job_complete", "job_id": "train-2026-04-06", "status": "success", "output_path": "s3://..." }
```
Claude fetches the output summary and posts key metrics to Discord.

**Scheduled health check**:
A cron job posts a heartbeat every 15 minutes. If Claude Code doesn't respond within the polling window, your monitoring knows the agent is down. Claude can also run its own checks on receipt:
```json
{ "event": "health_check", "timestamp": "2026-04-06T14:00:00Z" }
```

---

## Designing event payloads

Good event payloads give Claude enough context to act without requiring follow-up fetches for routine cases.

**Include in the payload:**
- `event` field — a clear event type string Claude can match on
- Identifiers (repo, job ID, environment) needed to fetch more context
- Direct URLs to logs, dashboards, or artifacts
- Short human-readable summary of what happened

**Keep out of the payload:**
- Full log output — too large; reference a URL instead
- Secrets or credentials — payloads may appear in Claude's context
- Redundant fields the event type already implies

**Payload size**: Keep payloads under a few KB. Large payloads slow down the receive-parse-act cycle and consume context window. Use URLs to reference large artifacts.

**Event type naming**: Use clear, action-oriented strings: `ci_failure`, `deploy_complete`, `alert_triggered`, `job_finished`. Avoid vague names like `update` or `notification`.
