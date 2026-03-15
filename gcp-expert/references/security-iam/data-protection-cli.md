# Data Protection — CLI Reference

## Cloud DLP (Sensitive Data Protection)

### Inline Inspection

```bash
# Inspect a string for common PII (REST API via curl; DLP has limited direct gcloud CLI)
TOKEN=$(gcloud auth print-access-token)
curl -s -X POST \
  "https://dlp.googleapis.com/v2/projects/PROJECT_ID/content:inspect" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "item": {
      "value": "My name is Alice and my SSN is 123-45-6789. Call me at 555-867-5309."
    },
    "inspectConfig": {
      "infoTypes": [
        {"name": "PERSON_NAME"},
        {"name": "US_SOCIAL_SECURITY_NUMBER"},
        {"name": "PHONE_NUMBER"},
        {"name": "EMAIL_ADDRESS"}
      ],
      "minLikelihood": "LIKELY",
      "limits": {"maxFindingsPerRequest": 100},
      "includeQuote": true
    }
  }'

# De-identify (redact) sensitive data from a string
curl -s -X POST \
  "https://dlp.googleapis.com/v2/projects/PROJECT_ID/content:deidentify" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "item": {
      "value": "My SSN is 123-45-6789 and email is alice@example.com"
    },
    "deidentifyConfig": {
      "infoTypeTransformations": {
        "transformations": [
          {
            "infoTypes": [{"name": "US_SOCIAL_SECURITY_NUMBER"}],
            "primitiveTransformation": {
              "replaceWithInfoTypeConfig": {}
            }
          },
          {
            "infoTypes": [{"name": "EMAIL_ADDRESS"}],
            "primitiveTransformation": {
              "redactConfig": {}
            }
          }
        ]
      }
    },
    "inspectConfig": {
      "infoTypes": [
        {"name": "US_SOCIAL_SECURITY_NUMBER"},
        {"name": "EMAIL_ADDRESS"}
      ]
    }
  }'

# De-identify using format-preserving encryption (tokenization) with a KMS key
curl -s -X POST \
  "https://dlp.googleapis.com/v2/projects/PROJECT_ID/content:deidentify" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "item": {"value": "SSN: 123-45-6789"},
    "deidentifyConfig": {
      "infoTypeTransformations": {
        "transformations": [{
          "infoTypes": [{"name": "US_SOCIAL_SECURITY_NUMBER"}],
          "primitiveTransformation": {
            "cryptoReplaceFfxFpeConfig": {
              "cryptoKey": {
                "kmsWrapped": {
                  "wrappedKey": "WRAPPED_KEY_BASE64",
                  "cryptoKeyName": "projects/PROJECT_ID/locations/REGION/keyRings/KEYRING/cryptoKeys/MY_KEY"
                }
              },
              "commonAlphabet": "NUMERIC"
            }
          }
        }]
      }
    },
    "inspectConfig": {"infoTypes": [{"name": "US_SOCIAL_SECURITY_NUMBER"}]}
  }'
```

### DLP Inspect Templates

```bash
# Create an inspect template
curl -s -X POST \
  "https://dlp.googleapis.com/v2/projects/PROJECT_ID/inspectTemplates" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "inspectTemplate": {
      "displayName": "PCI Data Detection",
      "description": "Detect payment card data",
      "inspectConfig": {
        "infoTypes": [
          {"name": "CREDIT_CARD_NUMBER"},
          {"name": "CREDIT_CARD_TRACK_NUMBER"},
          {"name": "IBAN_CODE"}
        ],
        "minLikelihood": "POSSIBLE",
        "includeQuote": false,
        "limits": {"maxFindingsPerRequest": 1000}
      }
    }
  }'

# List inspect templates
curl -s \
  "https://dlp.googleapis.com/v2/projects/PROJECT_ID/inspectTemplates" \
  -H "Authorization: Bearer $TOKEN"

# Delete an inspect template
curl -s -X DELETE \
  "https://dlp.googleapis.com/v2/projects/PROJECT_ID/inspectTemplates/TEMPLATE_ID" \
  -H "Authorization: Bearer $TOKEN"
```

### DLP Jobs (Scanning Cloud Storage / BigQuery)

```bash
# Create a DLP job to inspect a Cloud Storage bucket
curl -s -X POST \
  "https://dlp.googleapis.com/v2/projects/PROJECT_ID/dlpJobs" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "inspectJob": {
      "storageConfig": {
        "cloudStorageOptions": {
          "fileSet": {
            "url": "gs://my-data-bucket/**"
          },
          "fileTypes": ["CSV", "TEXT_FILE", "EXCEL", "AVRO", "PARQUET"]
        }
      },
      "inspectConfig": {
        "infoTypes": [
          {"name": "US_SOCIAL_SECURITY_NUMBER"},
          {"name": "CREDIT_CARD_NUMBER"},
          {"name": "EMAIL_ADDRESS"}
        ],
        "minLikelihood": "LIKELY"
      },
      "actions": [{
        "saveFindings": {
          "outputConfig": {
            "table": {
              "projectId": "PROJECT_ID",
              "datasetId": "dlp_results",
              "tableId": "findings"
            }
          }
        }
      }]
    }
  }'

# Create a DLP job to inspect a BigQuery table
curl -s -X POST \
  "https://dlp.googleapis.com/v2/projects/PROJECT_ID/dlpJobs" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "inspectJob": {
      "storageConfig": {
        "bigQueryOptions": {
          "tableReference": {
            "projectId": "PROJECT_ID",
            "datasetId": "my_dataset",
            "tableId": "user_records"
          },
          "rowsLimit": 1000000
        }
      },
      "inspectConfig": {
        "infoTypes": [{"name": "PERSON_NAME"}, {"name": "EMAIL_ADDRESS"}],
        "minLikelihood": "LIKELY"
      },
      "actions": [{"saveFindings": {"outputConfig": {"table": {
        "projectId": "PROJECT_ID",
        "datasetId": "dlp_results",
        "tableId": "bq_findings"
      }}}}]
    }
  }'

# List DLP jobs
curl -s \
  "https://dlp.googleapis.com/v2/projects/PROJECT_ID/dlpJobs" \
  -H "Authorization: Bearer $TOKEN" \
  | python3 -m json.tool

# Describe a specific DLP job
curl -s \
  "https://dlp.googleapis.com/v2/projects/PROJECT_ID/dlpJobs/JOB_ID" \
  -H "Authorization: Bearer $TOKEN"

# Cancel a running DLP job
curl -s -X POST \
  "https://dlp.googleapis.com/v2/projects/PROJECT_ID/dlpJobs/JOB_ID:cancel" \
  -H "Authorization: Bearer $TOKEN"

# Delete a completed DLP job
curl -s -X DELETE \
  "https://dlp.googleapis.com/v2/projects/PROJECT_ID/dlpJobs/JOB_ID" \
  -H "Authorization: Bearer $TOKEN"
```

---

## VPC Service Controls

### Setup

```bash
# List access policies (find your org's policy ID)
gcloud access-context-manager policies list \
  --organization=ORG_ID

# If no policy exists, create one
gcloud access-context-manager policies create \
  --organization=ORG_ID \
  --title="Organization Policy"
```

### Access Levels (prerequisites for perimeter ingress/egress)

```bash
# Create an IP-based access level (corporate network)
cat > corp-network.yaml << 'EOF'
- ipSubnetworks:
  - 203.0.113.0/24
  - 198.51.100.0/24
EOF

gcloud access-context-manager levels create CORP_NETWORK \
  --title="Corporate Network" \
  --basic-level-spec=corp-network.yaml \
  --policy=POLICY_ID

# List access levels
gcloud access-context-manager levels list \
  --policy=POLICY_ID
```

### Service Perimeters

```bash
# Create a dry-run service perimeter (test mode; nothing is blocked yet)
gcloud access-context-manager perimeters dry-run create my-data-perimeter \
  --title="Data Perimeter" \
  --resources=projects/PROJECT_NUMBER_1,projects/PROJECT_NUMBER_2 \
  --restricted-services=storage.googleapis.com,bigquery.googleapis.com,secretmanager.googleapis.com \
  --access-levels=accessPolicies/POLICY_ID/accessLevels/CORP_NETWORK \
  --policy=POLICY_ID

# Convert dry-run policy to enforced (after reviewing dry-run audit logs)
gcloud access-context-manager perimeters dry-run enforce my-data-perimeter \
  --policy=POLICY_ID

# Create an enforced service perimeter directly
gcloud access-context-manager perimeters create my-data-perimeter \
  --title="Data Perimeter" \
  --resources=projects/PROJECT_NUMBER_1 \
  --restricted-services=storage.googleapis.com,bigquery.googleapis.com,secretmanager.googleapis.com,cloudkms.googleapis.com \
  --access-levels=accessPolicies/POLICY_ID/accessLevels/CORP_NETWORK \
  --policy=POLICY_ID

# List perimeters
gcloud access-context-manager perimeters list \
  --policy=POLICY_ID

# Describe a perimeter (shows full config)
gcloud access-context-manager perimeters describe my-data-perimeter \
  --policy=POLICY_ID

# Update a perimeter (add a project to the perimeter)
gcloud access-context-manager perimeters update my-data-perimeter \
  --add-resources=projects/PROJECT_NUMBER_3 \
  --policy=POLICY_ID

# Update a perimeter (add a restricted service)
gcloud access-context-manager perimeters update my-data-perimeter \
  --add-restricted-services=artifactregistry.googleapis.com \
  --policy=POLICY_ID

# Delete a perimeter
gcloud access-context-manager perimeters delete my-data-perimeter \
  --policy=POLICY_ID
```

### Ingress and Egress Rules

```bash
# Update perimeter with ingress rule (allow a service account from outside perimeter to access BQ inside)
# ingress-rules.yaml:
# - ingressFrom:
#     identities:
#       - serviceAccount:etl-sa@external-project.iam.gserviceaccount.com
#     sources:
#       - resource: projects/EXTERNAL_PROJECT_NUMBER
#   ingressTo:
#     resources:
#       - projects/DATA_PROJECT_NUMBER
#     operations:
#       - serviceName: bigquery.googleapis.com
#         methodSelectors:
#           - method: "*"

gcloud access-context-manager perimeters update my-data-perimeter \
  --set-ingress-policies=ingress-rules.yaml \
  --policy=POLICY_ID

# Update perimeter with egress rule (allow service inside perimeter to call external KMS)
# egress-rules.yaml:
# - egressFrom:
#     identities:
#       - serviceAccount:data-sa@data-project.iam.gserviceaccount.com
#   egressTo:
#     resources:
#       - projects/KMS_PROJECT_NUMBER
#     operations:
#       - serviceName: cloudkms.googleapis.com
#         methodSelectors:
#           - method: "*"

gcloud access-context-manager perimeters update my-data-perimeter \
  --set-egress-policies=egress-rules.yaml \
  --policy=POLICY_ID

# View VPC SC audit logs (what would have been / was blocked)
gcloud logging read \
  'resource.type="audited_resource" AND logName:"cloudaudit.googleapis.com%2Fpolicy" AND protoPayload.metadata.@type="type.googleapis.com/google.cloud.audit.VpcServiceControlAuditMetadata"' \
  --project=PROJECT_ID \
  --limit=50 \
  --format="table(timestamp,protoPayload.serviceName,protoPayload.methodName,protoPayload.authenticationInfo.principalEmail,protoPayload.metadata.vpcServiceControlsUniqueId)"
```

---

## Binary Authorization

```bash
# Enable the Binary Authorization API
gcloud services enable binaryauthorization.googleapis.com \
  --project=PROJECT_ID

# Get the current Binary Authorization policy for a project
gcloud container binauthz policy export \
  --project=PROJECT_ID

# Import (replace) a Binary Authorization policy from a YAML file
# policy.yaml:
# defaultAdmissionRule:
#   evaluationMode: REQUIRE_ATTESTATION
#   enforcementMode: ENFORCED_BLOCK_AND_AUDIT_LOG
#   requireAttestationsBy:
#     - projects/PROJECT_ID/attestors/prod-attestor
# clusterAdmissionRules:
#   us-central1-a.my-dev-cluster:
#     evaluationMode: ALWAYS_ALLOW
#     enforcementMode: ENFORCED_BLOCK_AND_AUDIT_LOG
# globalPolicyEvaluationMode: ENABLE
gcloud container binauthz policy import policy.yaml \
  --project=PROJECT_ID

# Create an attestor (requires a Cloud KMS asymmetric signing key)
gcloud container binauthz attestors create prod-attestor \
  --attestation-authority-note=projects/PROJECT_ID/notes/prod-attestor-note \
  --description="Production deployment attestor" \
  --project=PROJECT_ID

# Create the Container Analysis note that the attestor references
curl -s -X POST \
  "https://containeranalysis.googleapis.com/v1/projects/PROJECT_ID/notes?noteId=prod-attestor-note" \
  -H "Authorization: Bearer $(gcloud auth print-access-token)" \
  -H "Content-Type: application/json" \
  -d '{
    "attestation": {
      "hint": {
        "humanReadableName": "Production attestor"
      }
    }
  }'

# Add a KMS signing key to an attestor
gcloud container binauthz attestors public-keys add \
  --attestor=prod-attestor \
  --keyversion-project=PROJECT_ID \
  --keyversion-location=us-central1 \
  --keyversion-keyring=binauthz-keyring \
  --keyversion-key=prod-signing-key \
  --keyversion=1 \
  --project=PROJECT_ID

# List attestors
gcloud container binauthz attestors list \
  --project=PROJECT_ID

# Describe an attestor
gcloud container binauthz attestors describe prod-attestor \
  --project=PROJECT_ID

# Create an attestation for an image (sign it) — done in CI/CD pipeline
IMAGE_DIGEST="us-central1-docker.pkg.dev/PROJECT_ID/my-repo/my-app@sha256:HASH"
gcloud container binauthz attestations sign-and-create \
  --attestor=prod-attestor \
  --attestor-project=PROJECT_ID \
  --artifact-url="$IMAGE_DIGEST" \
  --keyversion-project=PROJECT_ID \
  --keyversion-location=us-central1 \
  --keyversion-keyring=binauthz-keyring \
  --keyversion-key=prod-signing-key \
  --keyversion=1 \
  --project=PROJECT_ID

# List attestations for an image
gcloud container binauthz attestations list \
  --attestor=prod-attestor \
  --attestor-project=PROJECT_ID \
  --artifact-url="$IMAGE_DIGEST" \
  --project=PROJECT_ID

# Delete an attestor
gcloud container binauthz attestors delete prod-attestor \
  --project=PROJECT_ID

# Grant a CI/CD service account permission to create attestations
gcloud container binauthz attestors add-iam-policy-binding prod-attestor \
  --member="serviceAccount:cicd-sa@PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/binaryauthorization.attestorsVerifier" \
  --project=PROJECT_ID
```

---

## Certificate Authority Service (CAS)

```bash
# Enable the CAS API
gcloud services enable privateca.googleapis.com \
  --project=PROJECT_ID

# Create a CA pool
gcloud privateca pools create my-ca-pool \
  --location=us-central1 \
  --tier=devops \
  --project=PROJECT_ID

# Create a Root CA in the pool
gcloud privateca roots create my-root-ca \
  --pool=my-ca-pool \
  --location=us-central1 \
  --subject="CN=My Root CA, O=My Organization, C=US" \
  --key-algorithm=ec-p384-sha384 \
  --max-chain-length=1 \
  --validity=P10Y \
  --project=PROJECT_ID

# Create a Subordinate CA signed by the Root CA
gcloud privateca subordinates create my-sub-ca \
  --pool=my-ca-pool \
  --location=us-central1 \
  --issuer-pool=my-ca-pool \
  --issuer-ca=my-root-ca \
  --subject="CN=My Issuing CA, O=My Organization, C=US" \
  --key-algorithm=ec-p256-sha256 \
  --validity=P5Y \
  --project=PROJECT_ID

# List CAs in a pool
gcloud privateca cas list \
  --pool=my-ca-pool \
  --location=us-central1 \
  --project=PROJECT_ID

# Describe a CA
gcloud privateca roots describe my-root-ca \
  --pool=my-ca-pool \
  --location=us-central1 \
  --project=PROJECT_ID

# Enable a CA (activate it for issuance)
gcloud privateca roots enable my-root-ca \
  --pool=my-ca-pool \
  --location=us-central1 \
  --project=PROJECT_ID

# Disable a CA
gcloud privateca roots disable my-root-ca \
  --pool=my-ca-pool \
  --location=us-central1 \
  --project=PROJECT_ID

# Issue a certificate from a pool (CSR-based)
gcloud privateca certificates create my-cert \
  --issuer-pool=my-ca-pool \
  --issuer-location=us-central1 \
  --csr=my-csr.pem \
  --validity=P365D \
  --cert-output-file=my-cert.pem \
  --project=PROJECT_ID

# Issue a certificate with inline subject and SANs (no CSR needed)
gcloud privateca certificates create my-server-cert \
  --issuer-pool=my-ca-pool \
  --issuer-location=us-central1 \
  --subject="CN=my-service.internal" \
  --dns-san=my-service.internal,my-service.svc.cluster.local \
  --validity=P90D \
  --generate-key \
  --key-output-file=server-key.pem \
  --cert-output-file=server-cert.pem \
  --project=PROJECT_ID

# List certificates
gcloud privateca certificates list \
  --issuer-pool=my-ca-pool \
  --issuer-location=us-central1 \
  --project=PROJECT_ID

# Describe a certificate
gcloud privateca certificates describe my-server-cert \
  --issuer-pool=my-ca-pool \
  --issuer-location=us-central1 \
  --project=PROJECT_ID

# Revoke a certificate
gcloud privateca certificates revoke \
  --certificate=my-server-cert \
  --issuer-pool=my-ca-pool \
  --issuer-location=us-central1 \
  --reason=COMPROMISED \
  --project=PROJECT_ID

# Grant a service account permission to request certificates from a pool
gcloud privateca pools add-iam-policy-binding my-ca-pool \
  --location=us-central1 \
  --member="serviceAccount:my-service@PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/privateca.certificateRequester" \
  --project=PROJECT_ID

# Delete a CA pool (must first delete all CAs in the pool)
gcloud privateca pools delete my-ca-pool \
  --location=us-central1 \
  --project=PROJECT_ID
```

---

## Artifact Analysis (Vulnerability Scanning)

```bash
# Enable Artifact Analysis API
gcloud services enable containeranalysis.googleapis.com \
  --project=PROJECT_ID

# List container images with vulnerability occurrences
gcloud artifacts docker images list \
  us-central1-docker.pkg.dev/PROJECT_ID/my-repo \
  --show-occurrences \
  --project=PROJECT_ID

# List vulnerability occurrences for a specific image
gcloud artifacts docker images describe \
  us-central1-docker.pkg.dev/PROJECT_ID/my-repo/my-app:latest \
  --show-package-vulnerability \
  --project=PROJECT_ID

# Scan an image on-demand (any registry)
gcloud artifacts docker images scan \
  us-central1-docker.pkg.dev/PROJECT_ID/my-repo/my-app:latest \
  --format="value(response.scan)" \
  --project=PROJECT_ID

# List all vulnerability occurrences for all images in a project
gcloud beta container images list-tags \
  us-central1-docker.pkg.dev/PROJECT_ID/my-repo \
  --format="value(digest)" | while read digest; do
    gcloud artifacts docker images describe \
      "us-central1-docker.pkg.dev/PROJECT_ID/my-repo@$digest" \
      --show-package-vulnerability 2>/dev/null
  done

# Query vulnerabilities via Container Analysis API
TOKEN=$(gcloud auth print-access-token)
curl -s \
  "https://containeranalysis.googleapis.com/v1/projects/PROJECT_ID/occurrences?filter=kind%3D%22VULNERABILITY%22%20AND%20vulnerability.severity%3D%22CRITICAL%22" \
  -H "Authorization: Bearer $TOKEN"

# Export SBOM for an image
gcloud artifacts sbom export \
  --uri=us-central1-docker.pkg.dev/PROJECT_ID/my-repo/my-app@sha256:DIGEST \
  --destination=gs://my-bucket/sboms/ \
  --project=PROJECT_ID

# Load SBOM into Artifact Analysis
gcloud artifacts sbom load \
  --source=gs://my-bucket/sboms/sbom.json \
  --uri=us-central1-docker.pkg.dev/PROJECT_ID/my-repo/my-app@sha256:DIGEST \
  --project=PROJECT_ID
```

---

## reCAPTCHA Enterprise — CLI

```bash
# Enable reCAPTCHA Enterprise API
gcloud services enable recaptchaenterprise.googleapis.com --project=PROJECT_ID

# Create a score-based site key (web, no challenge)
gcloud recaptcha keys create \
  --display-name="Production Login" \
  --web \
  --domains=example.com,www.example.com \
  --project=PROJECT_ID

# Create a checkbox site key (web, visual challenge)
gcloud recaptcha keys create \
  --display-name="Checkout Challenge" \
  --web \
  --domains=example.com \
  --integration-type=CHECKBOX \
  --project=PROJECT_ID

# Create a mobile (Android) site key
gcloud recaptcha keys create \
  --display-name="Android App" \
  --android \
  --package-names=com.example.myapp \
  --project=PROJECT_ID

# Create an iOS site key
gcloud recaptcha keys create \
  --display-name="iOS App" \
  --ios \
  --bundle-ids=com.example.myapp \
  --project=PROJECT_ID

# List all reCAPTCHA keys
gcloud recaptcha keys list --project=PROJECT_ID

# Describe a key
gcloud recaptcha keys describe KEY_ID --project=PROJECT_ID

# Update a key (add domain)
gcloud recaptcha keys update KEY_ID \
  --web \
  --domains=example.com,api.example.com \
  --project=PROJECT_ID

# Delete a key
gcloud recaptcha keys delete KEY_ID --project=PROJECT_ID

# Create an assessment (server-side token validation) via REST API
# (gcloud doesn't have direct create-assessment; use curl or client library)
curl -X POST \
  "https://recaptchaenterprise.googleapis.com/v1/projects/PROJECT_ID/assessments" \
  -H "Authorization: Bearer $(gcloud auth print-access-token)" \
  -H "Content-Type: application/json" \
  -d '{
    "event": {
      "token": "TOKEN_FROM_FRONTEND",
      "siteKey": "KEY_ID",
      "expectedAction": "login"
    }
  }'

# Annotate an assessment (provide ground truth for model improvement)
curl -X POST \
  "https://recaptchaenterprise.googleapis.com/v1/projects/PROJECT_ID/assessments/ASSESSMENT_ID:annotate" \
  -H "Authorization: Bearer $(gcloud auth print-access-token)" \
  -H "Content-Type: application/json" \
  -d '{
    "annotation": "LEGITIMATE",
    "reasons": ["PASSED_TWO_FACTOR", "CORRECT_PASSWORD"]
  }'

# List metrics for a key (via Monitoring)
gcloud monitoring time-series list \
  --project=PROJECT_ID \
  --filter='metric.type="recaptchaenterprise.googleapis.com/assessment/score_distribution"'
```

## Access Transparency & Access Approval — CLI

```bash
# Enable Access Approval API
gcloud services enable accessapproval.googleapis.com --project=PROJECT_ID

# Get current Access Approval settings for a project
gcloud access-approval settings get --project=PROJECT_ID

# Update Access Approval settings (add approvers)
gcloud access-approval settings update \
  --project=PROJECT_ID \
  --enrolled_services=all \
  --notification_emails=security-team@example.com,ciso@example.com

# Enable Access Approval at folder level
gcloud access-approval settings update \
  --folder=FOLDER_ID \
  --enrolled_services=all \
  --notification_emails=approver@example.com

# List pending access approval requests
gcloud access-approval requests list \
  --project=PROJECT_ID \
  --filter="state=PENDING"

# Describe a specific approval request
gcloud access-approval requests describe \
  projects/PROJECT_ID/approvalRequests/REQUEST_ID

# Approve an access request
gcloud access-approval requests approve \
  projects/PROJECT_ID/approvalRequests/REQUEST_ID

# Dismiss (deny) an access request
gcloud access-approval requests dismiss \
  projects/PROJECT_ID/approvalRequests/REQUEST_ID

# List Access Transparency logs (in Cloud Logging)
gcloud logging read \
  'logName="projects/PROJECT_ID/logs/cloudaudit.googleapis.com%2Faccess_transparency"' \
  --project=PROJECT_ID \
  --limit=50 \
  --format=json

# Set up Pub/Sub export for Access Transparency alerts
gcloud logging sinks create access-transparency-sink \
  pubsub.googleapis.com/projects/PROJECT_ID/topics/access-transparency-alerts \
  --log-filter='logName="projects/PROJECT_ID/logs/cloudaudit.googleapis.com%2Faccess_transparency"' \
  --project=PROJECT_ID
```
