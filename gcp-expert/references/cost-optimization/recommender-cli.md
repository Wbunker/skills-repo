# GCP Recommender & Active Assist — CLI Reference

## Listing Insights

```bash
# List VM rightsizing insights for a project and region
gcloud recommender insights list \
  --recommender=google.compute.instance.MachineTypeRecommender \
  --location=us-central1 \
  --project=my-project \
  --format="table(name,insightSubtype,stateInfo.state,lastRefreshTime)"

# List idle resource insights (disk)
gcloud recommender insights list \
  --recommender=google.compute.disk.IdleResourceRecommender \
  --location=us-central1 \
  --project=my-project

# List IAM excess permissions insights (global)
gcloud recommender insights list \
  --recommender=google.iam.policy.Recommender \
  --location=global \
  --project=my-project \
  --format="table(name,description,stateInfo.state)"

# Describe a specific insight
gcloud recommender insights describe INSIGHT_ID \
  --recommender=google.compute.instance.MachineTypeRecommender \
  --location=us-central1 \
  --project=my-project
```

---

## Listing Recommendations

```bash
# List VM rightsizing recommendations for us-central1
gcloud recommender recommendations list \
  --recommender=google.compute.instance.MachineTypeRecommender \
  --location=us-central1 \
  --project=my-project \
  --format="table(name,recommenderSubtype,stateInfo.state,primaryImpact.costProjection.cost.currencyCode,primaryImpact.costProjection.cost.units)"

# List idle VM recommendations
gcloud recommender recommendations list \
  --recommender=google.compute.instance.IdleResourceRecommender \
  --location=us-central1 \
  --project=my-project

# List idle disk recommendations
gcloud recommender recommendations list \
  --recommender=google.compute.disk.IdleResourceRecommender \
  --location=us-central1 \
  --project=my-project \
  --format="table(name,description,stateInfo.state,primaryImpact.costProjection.cost.units)"

# List idle IP address recommendations
gcloud recommender recommendations list \
  --recommender=google.compute.address.IdleResourceRecommender \
  --location=us-central1 \
  --project=my-project

# List CUD purchase recommendations
gcloud recommender recommendations list \
  --recommender=google.compute.commitment.UsageCommitmentRecommender \
  --location=us-central1 \
  --project=my-project \
  --format="table(name,description,primaryImpact.costProjection.cost.units,stateInfo.state)"

# List unattended project recommendations (global, org-level)
gcloud recommender recommendations list \
  --recommender=google.resourcemanager.projectUtilization.Recommender \
  --location=global \
  --project=my-project

# List IAM policy recommendations
gcloud recommender recommendations list \
  --recommender=google.iam.policy.Recommender \
  --location=global \
  --project=my-project \
  --format="table(name,description,stateInfo.state,primaryImpact.securityProjection.details)"

# Describe a specific recommendation
gcloud recommender recommendations describe RECOMMENDATION_ID \
  --recommender=google.compute.instance.MachineTypeRecommender \
  --location=us-central1 \
  --project=my-project
```

---

## Managing Recommendation State

Recommendations follow a lifecycle: ACTIVE → CLAIMED → SUCCEEDED/FAILED

```bash
# Mark a recommendation as CLAIMED (you intend to apply it)
gcloud recommender recommendations mark-claimed RECOMMENDATION_ID \
  --recommender=google.compute.instance.MachineTypeRecommender \
  --location=us-central1 \
  --project=my-project \
  --etag=ETAG_FROM_DESCRIBE \
  --state-metadata=reviewedBy=alice,reviewDate=2025-01-15

# Mark a recommendation as SUCCEEDED (you applied it)
gcloud recommender recommendations mark-succeeded RECOMMENDATION_ID \
  --recommender=google.compute.instance.MachineTypeRecommender \
  --location=us-central1 \
  --project=my-project \
  --etag=ETAG_FROM_DESCRIBE

# Mark a recommendation as FAILED (you tried but it didn't work)
gcloud recommender recommendations mark-failed RECOMMENDATION_ID \
  --recommender=google.compute.instance.MachineTypeRecommender \
  --location=us-central1 \
  --project=my-project \
  --etag=ETAG_FROM_DESCRIBE \
  --state-metadata=failureReason="VM is part of critical HA group"

# Mark a recommendation as DISMISSED (you don't want to apply it)
gcloud recommender recommendations mark-dismissed RECOMMENDATION_ID \
  --recommender=google.compute.instance.MachineTypeRecommender \
  --location=us-central1 \
  --project=my-project \
  --etag=ETAG_FROM_DESCRIBE
```

> **Note**: The `--etag` value must match the current etag from `describe`; this prevents concurrent conflicting updates.

---

## Common Recommender IDs Reference

| Recommender ID | Type | Scope |
|---|---|---|
| `google.compute.instance.MachineTypeRecommender` | VM rightsizing | regional |
| `google.compute.instance.IdleResourceRecommender` | Idle VMs | regional |
| `google.compute.disk.IdleResourceRecommender` | Idle persistent disks | regional |
| `google.compute.address.IdleResourceRecommender` | Idle IP addresses | regional |
| `google.compute.image.IdleResourceRecommender` | Idle custom images | global |
| `google.compute.commitment.UsageCommitmentRecommender` | CUD purchase suggestions | regional |
| `google.iam.policy.Recommender` | IAM excess permissions | global |
| `google.resourcemanager.projectUtilization.Recommender` | Unattended projects | global |
| `google.cloudsql.instance.IdleRecommender` | Idle Cloud SQL | regional |
| `google.cloudsql.instance.OverprovisionedRecommender` | Overprovisioned Cloud SQL | regional |
| `google.container.DiagnosisRecommender` | GKE issues | regional |

---

## Automation Script: Release All Idle IP Addresses

```bash
#!/bin/bash
# Auto-release idle static IP addresses based on Recommender API
# Safe to automate; idle IPs have no traffic impact

PROJECT="my-project"
REGION="us-central1"
RECOMMENDER="google.compute.address.IdleResourceRecommender"

# Get all active idle IP recommendations
RECOMMENDATIONS=$(gcloud recommender recommendations list \
  --recommender=${RECOMMENDER} \
  --location=${REGION} \
  --project=${PROJECT} \
  --filter="stateInfo.state=ACTIVE" \
  --format="value(name,primaryImpact.costProjection.cost.units)" 2>/dev/null)

if [ -z "$RECOMMENDATIONS" ]; then
  echo "No idle IP recommendations found."
  exit 0
fi

echo "Found idle IP recommendations:"
echo "$RECOMMENDATIONS"

while IFS=$'\t' read -r rec_name savings; do
  REC_ID=$(basename "$rec_name")
  echo "Processing recommendation: $REC_ID (savings: \$${savings}/month)"

  # Get current etag
  ETAG=$(gcloud recommender recommendations describe "$REC_ID" \
    --recommender=${RECOMMENDER} \
    --location=${REGION} \
    --project=${PROJECT} \
    --format="value(etag)" 2>/dev/null)

  # Mark as claimed
  gcloud recommender recommendations mark-claimed "$REC_ID" \
    --recommender=${RECOMMENDER} \
    --location=${REGION} \
    --project=${PROJECT} \
    --etag="$ETAG" \
    --state-metadata="automatedBy=cost-cleanup-script" 2>/dev/null

  # Get the IP address name from the recommendation description
  IP_NAME=$(gcloud recommender recommendations describe "$REC_ID" \
    --recommender=${RECOMMENDER} \
    --location=${REGION} \
    --project=${PROJECT} \
    --format="value(content.operationGroups[0].operations[0].resource)" 2>/dev/null | \
    sed 's|.*/addresses/||')

  echo "Releasing IP: $IP_NAME"

  # Release the IP address
  if gcloud compute addresses delete "$IP_NAME" \
    --region=${REGION} \
    --project=${PROJECT} \
    --quiet 2>/dev/null; then

    # Mark recommendation as succeeded
    NEW_ETAG=$(gcloud recommender recommendations describe "$REC_ID" \
      --recommender=${RECOMMENDER} \
      --location=${REGION} \
      --project=${PROJECT} \
      --format="value(etag)" 2>/dev/null)

    gcloud recommender recommendations mark-succeeded "$REC_ID" \
      --recommender=${RECOMMENDER} \
      --location=${REGION} \
      --project=${PROJECT} \
      --etag="$NEW_ETAG" 2>/dev/null

    echo "Successfully released $IP_NAME"
  else
    echo "Failed to release $IP_NAME"
  fi

done <<< "$RECOMMENDATIONS"
```

---

## Automation Script: List All Active Cost Recommendations (All Types)

```bash
#!/bin/bash
# List all active cost recommendations across common recommenders for a project

PROJECT="my-project"

RECOMMENDERS=(
  "google.compute.instance.MachineTypeRecommender:us-central1"
  "google.compute.instance.MachineTypeRecommender:us-east1"
  "google.compute.instance.IdleResourceRecommender:us-central1"
  "google.compute.disk.IdleResourceRecommender:us-central1"
  "google.compute.address.IdleResourceRecommender:us-central1"
  "google.compute.commitment.UsageCommitmentRecommender:us-central1"
  "google.iam.policy.Recommender:global"
  "google.resourcemanager.projectUtilization.Recommender:global"
)

TOTAL_SAVINGS=0

for ENTRY in "${RECOMMENDERS[@]}"; do
  RECOMMENDER="${ENTRY%%:*}"
  LOCATION="${ENTRY##*:}"

  echo ""
  echo "=== ${RECOMMENDER} (${LOCATION}) ==="

  gcloud recommender recommendations list \
    --recommender="${RECOMMENDER}" \
    --location="${LOCATION}" \
    --project="${PROJECT}" \
    --filter="stateInfo.state=ACTIVE" \
    --format="table(name.basename(),description,primaryImpact.costProjection.cost.units)" \
    2>/dev/null || echo "  (no recommendations or insufficient permissions)"
done
```
