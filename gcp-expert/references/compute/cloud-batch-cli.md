# Cloud Batch — CLI Reference

Capabilities reference: [cloud-batch-capabilities.md](cloud-batch-capabilities.md)

Cloud Batch uses `gcloud batch`. Job definitions are specified as JSON or YAML files.

```bash
gcloud config set project my-project-id
```

---

## Jobs

### Submit a Job

```bash
# Submit a job from a JSON definition file
gcloud batch jobs submit my-batch-job \
  --location=us-central1 \
  --config=job.json

# Submit from a YAML file
gcloud batch jobs submit my-batch-job \
  --location=us-central1 \
  --config=job.yaml

# Submit inline with a JSON config (for simple jobs)
gcloud batch jobs submit my-simple-job \
  --location=us-central1 \
  --config='
{
  "taskGroups": [
    {
      "taskCount": 1,
      "parallelism": 1,
      "taskSpec": {
        "runnables": [
          {
            "script": {
              "text": "echo Hello from task $BATCH_TASK_INDEX"
            }
          }
        ]
      }
    }
  ],
  "allocationPolicy": {
    "instances": [
      {
        "policy": {
          "machineType": "e2-standard-4"
        }
      }
    ]
  },
  "logsPolicy": {
    "destination": "CLOUD_LOGGING"
  }
}'
```

### Job Definition Examples

**Container job with 100 parallel tasks (job.json):**
```json
{
  "taskGroups": [
    {
      "taskCount": 100,
      "parallelism": 10,
      "taskSpec": {
        "runnables": [
          {
            "container": {
              "imageUri": "us-central1-docker.pkg.dev/my-project/my-repo/my-processor:latest",
              "commands": ["/app/process"],
              "args": [
                "--input",
                "gs://my-input-bucket/items/$(BATCH_TASK_INDEX).json",
                "--output",
                "gs://my-output-bucket/results/$(BATCH_TASK_INDEX).json"
              ],
              "entrypoint": ""
            }
          }
        ],
        "computeResource": {
          "cpuMilli": 2000,
          "memoryMib": 4096
        },
        "maxRetryCount": 3,
        "maxRunDuration": "3600s",
        "environment": {
          "variables": {
            "LOG_LEVEL": "info",
            "ENV": "production"
          }
        }
      }
    }
  ],
  "allocationPolicy": {
    "instances": [
      {
        "policy": {
          "machineType": "n2-standard-4",
          "provisioningModel": "SPOT",
          "disks": [
            {
              "newDisk": {
                "type": "pd-ssd",
                "sizeGb": 50
              },
              "deviceName": "scratch"
            }
          ]
        }
      }
    ],
    "location": {
      "allowedLocations": ["regions/us-central1"]
    },
    "serviceAccount": {
      "email": "my-batch-sa@my-project.iam.gserviceaccount.com",
      "scopes": ["https://www.googleapis.com/auth/cloud-platform"]
    },
    "network": {
      "networkInterfaces": [
        {
          "network": "projects/my-project/global/networks/my-vpc",
          "subnetwork": "projects/my-project/regions/us-central1/subnetworks/my-subnet",
          "noExternalIpAddress": true
        }
      ]
    }
  },
  "logsPolicy": {
    "destination": "CLOUD_LOGGING"
  }
}
```

**Script job with GPU (job-gpu.json):**
```json
{
  "taskGroups": [
    {
      "taskCount": 4,
      "parallelism": 4,
      "taskSpec": {
        "runnables": [
          {
            "container": {
              "imageUri": "us-central1-docker.pkg.dev/my-project/my-repo/ml-trainer:latest",
              "commands": ["python3", "train.py"],
              "args": ["--shard", "$(BATCH_TASK_INDEX)", "--total-shards", "4"]
            }
          }
        ],
        "computeResource": {
          "cpuMilli": 12000,
          "memoryMib": 85000
        },
        "maxRetryCount": 1,
        "maxRunDuration": "86400s"
      }
    }
  ],
  "allocationPolicy": {
    "instances": [
      {
        "installGpuDrivers": true,
        "policy": {
          "machineType": "a2-highgpu-1g",
          "accelerators": [
            {
              "type": "nvidia-tesla-a100",
              "count": 1
            }
          ]
        }
      }
    ],
    "location": {
      "allowedLocations": ["zones/us-central1-a", "zones/us-central1-b"]
    },
    "serviceAccount": {
      "email": "my-ml-sa@my-project.iam.gserviceaccount.com"
    }
  },
  "logsPolicy": {
    "destination": "CLOUD_LOGGING"
  }
}
```

**Multi-runnable job (setup + main + cleanup):**
```json
{
  "taskGroups": [
    {
      "taskCount": 10,
      "parallelism": 5,
      "taskSpec": {
        "runnables": [
          {
            "script": {
              "text": "#!/bin/bash\necho 'Downloading inputs...'\ngsutil cp gs://my-bucket/inputs/$BATCH_TASK_INDEX.gz /tmp/input.gz\ngunzip /tmp/input.gz"
            }
          },
          {
            "container": {
              "imageUri": "us-central1-docker.pkg.dev/my-project/my-repo/processor:latest",
              "commands": ["/app/process"],
              "args": ["--input", "/tmp/input", "--output", "/tmp/output"]
            }
          },
          {
            "script": {
              "text": "#!/bin/bash\necho 'Uploading results...'\ngsutil cp /tmp/output gs://my-bucket/outputs/$BATCH_TASK_INDEX\necho 'Task $BATCH_TASK_INDEX complete'"
            }
          }
        ],
        "computeResource": {
          "cpuMilli": 4000,
          "memoryMib": 8192
        },
        "maxRetryCount": 2
      }
    }
  ],
  "allocationPolicy": {
    "instances": [
      {
        "policy": {
          "machineType": "n2-standard-4"
        }
      }
    ]
  },
  "logsPolicy": {
    "destination": "CLOUD_LOGGING"
  }
}
```

---

### Describe a Job

```bash
# Get full job details
gcloud batch jobs describe my-batch-job --location=us-central1

# Get job status only
gcloud batch jobs describe my-batch-job \
  --location=us-central1 \
  --format="get(status.state)"

# Get task group status (counts of running/succeeded/failed tasks)
gcloud batch jobs describe my-batch-job \
  --location=us-central1 \
  --format="get(status.taskGroups)"
```

### List Jobs

```bash
# List all jobs in a location
gcloud batch jobs list --location=us-central1

# List jobs with status filter
gcloud batch jobs list \
  --location=us-central1 \
  --filter="status.state=RUNNING"

# List failed jobs
gcloud batch jobs list \
  --location=us-central1 \
  --filter="status.state=FAILED"

# List with custom format
gcloud batch jobs list \
  --location=us-central1 \
  --format="table(name.basename(),status.state,createTime,status.runDuration)"
```

### Cancel and Delete Jobs

```bash
# Cancel a running job (stops all tasks and VMs)
gcloud batch jobs cancel my-batch-job --location=us-central1

# Delete a job (must be in terminal state: SUCCEEDED, FAILED, CANCELLED)
gcloud batch jobs delete my-batch-job --location=us-central1 --quiet

# Delete all succeeded jobs (cleanup)
gcloud batch jobs list \
  --location=us-central1 \
  --filter="status.state=SUCCEEDED" \
  --format="get(name.basename())" | \
xargs -I{} gcloud batch jobs delete {} --location=us-central1 --quiet
```

---

## Viewing Task Logs

```bash
# View logs for a batch job in Cloud Logging
gcloud logging read \
  'resource.type="batch.googleapis.com/Job" AND labels."batch.googleapis.com/job_name"="my-batch-job"' \
  --location=us-central1 \
  --limit=200 \
  --format="table(timestamp,textPayload,labels.'batch.googleapis.com/task_id')"

# Filter for a specific task index
gcloud logging read \
  'resource.type="batch.googleapis.com/Job"
   AND labels."batch.googleapis.com/job_name"="my-batch-job"
   AND labels."batch.googleapis.com/task_id"="group0-task5"' \
  --location=us-central1 \
  --limit=100

# Filter for errors only
gcloud logging read \
  'resource.type="batch.googleapis.com/Job"
   AND labels."batch.googleapis.com/job_name"="my-batch-job"
   AND severity>=ERROR' \
  --location=us-central1 \
  --limit=50
```

---

## Resource Allowances

```bash
# Create a resource allowance (limits total CPU hours for jobs using this allowance)
gcloud batch resource-allowances create my-team-allowance \
  --location=us-central1 \
  --usage-resource-allowance-spec-from-file=allowance.json

# allowance.json example:
# {
#   "limit": {
#     "calendarPeriod": "MONTH",
#     "limit": 10000
#   },
#   "resourceType": "cpu"
# }

# List resource allowances
gcloud batch resource-allowances list --location=us-central1
```

---

## IAM for Cloud Batch

```bash
# Grant a service account the Batch Agent Reporter role (for VMs running tasks)
gcloud projects add-iam-policy-binding my-project \
  --member=serviceAccount:my-batch-sa@my-project.iam.gserviceaccount.com \
  --role=roles/batch.agentReporter

# Grant Cloud Storage access (for reading inputs and writing outputs)
gcloud projects add-iam-policy-binding my-project \
  --member=serviceAccount:my-batch-sa@my-project.iam.gserviceaccount.com \
  --role=roles/storage.objectAdmin

# Grant Artifact Registry reader access (for pulling private container images)
gcloud artifacts repositories add-iam-policy-binding my-repo \
  --location=us-central1 \
  --member=serviceAccount:my-batch-sa@my-project.iam.gserviceaccount.com \
  --role=roles/artifactregistry.reader

# Grant Logs Writer role (for writing task logs to Cloud Logging)
gcloud projects add-iam-policy-binding my-project \
  --member=serviceAccount:my-batch-sa@my-project.iam.gserviceaccount.com \
  --role=roles/logging.logWriter

# Allow a user or CI/CD SA to submit batch jobs
gcloud projects add-iam-policy-binding my-project \
  --member=serviceAccount:ci-cd-sa@my-project.iam.gserviceaccount.com \
  --role=roles/batch.jobsEditor
```
