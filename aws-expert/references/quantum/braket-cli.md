# Amazon Braket — CLI Reference

For service concepts, see [braket-capabilities.md](braket-capabilities.md).

---

## Devices

```bash
# --- Get details of a specific device ---
# Gate-based QPU: IonQ Aria
aws braket get-device \
  --device-arn "arn:aws:braket:us-east-1::device/qpu/ionq/Aria-1"

# Gate-based QPU: Rigetti Aspen-M-3
aws braket get-device \
  --device-arn "arn:aws:braket:us-west-1::device/qpu/rigetti/Aspen-M-3"

# D-Wave Advantage annealer
aws braket get-device \
  --device-arn "arn:aws:braket:us-west-2::device/qpu/d-wave/Advantage_system6"

# Managed simulator: SV1
aws braket get-device \
  --device-arn "arn:aws:braket:::device/quantum-simulator/amazon/sv1"

# Managed simulator: DM1
aws braket get-device \
  --device-arn "arn:aws:braket:::device/quantum-simulator/amazon/dm1"

# Managed simulator: TN1
aws braket get-device \
  --device-arn "arn:aws:braket:::device/quantum-simulator/amazon/tn1"

# --- Search for available devices ---
aws braket search-devices \
  --filters '[
    {"name": "deviceType", "values": ["QPU"]},
    {"name": "deviceStatus", "values": ["ONLINE"]}
  ]'

# Search for gate-based devices
aws braket search-devices \
  --filters '[{"name": "paradigmName", "values": ["gate-based"]}]'

# Search for annealing devices
aws braket search-devices \
  --filters '[{"name": "paradigmName", "values": ["annealing"]}]'
```

---

## Quantum Tasks

```bash
# --- Create a quantum task (submit circuit to a device) ---
# Note: The openQASM program is typically submitted via SDK.
# CLI submission requires the program source inline in the action JSON.

aws braket create-quantum-task \
  --device-arn "arn:aws:braket:::device/quantum-simulator/amazon/sv1" \
  --output-s3-bucket "my-braket-results" \
  --output-s3-key-prefix "tasks/2024" \
  --shots 1000 \
  --action '{
    "braketSchemaHeader": {
      "name": "braket.ir.openqasm.program",
      "version": "1"
    },
    "source": "OPENQASM 3.0;\nqubit[2] q;\nh q[0];\ncnot q[0], q[1];\n#pragma braket result probability q[0], q[1]",
    "inputs": {}
  }'

# --- Get task status ---
aws braket get-quantum-task \
  --quantum-task-id a1b2c3d4-e5f6-7890-abcd-ef1234567890

# --- Cancel a running task ---
aws braket cancel-quantum-task \
  --quantum-task-id a1b2c3d4-e5f6-7890-abcd-ef1234567890 \
  --client-token "cancel-token-$(date +%s)"

# --- Search quantum tasks ---
aws braket search-quantum-tasks \
  --filters '[{"name": "status", "values": ["COMPLETED"]}]'

aws braket search-quantum-tasks \
  --filters '[
    {"name": "deviceArn", "values": ["arn:aws:braket:::device/quantum-simulator/amazon/sv1"]},
    {"name": "status", "values": ["RUNNING", "QUEUED"]}
  ]'
```

---

## Hybrid Jobs

```bash
# --- Create a hybrid job ---
aws braket create-job \
  --client-token "job-token-$(date +%s)" \
  --job-name "vqe-hydrogen-molecule" \
  --role-arn "arn:aws:iam::123456789012:role/AmazonBraketJobsExecutionRole" \
  --algorithm-specification '{
    "scriptModeConfig": {
      "entryPoint": "vqe_algorithm:main",
      "s3Uri": "s3://my-braket-jobs/scripts/vqe_algorithm.py",
      "compressionType": "NONE"
    }
  }' \
  --input-data-config '[
    {
      "channelName": "training",
      "dataSource": {
        "s3DataSource": {
          "s3Uri": "s3://my-braket-jobs/input-data/"
        }
      }
    }
  ]' \
  --output-data-config '{
    "s3Path": "s3://my-braket-results/jobs/vqe-hydrogen/"
  }' \
  --checkpoint-config '{
    "s3Uri": "s3://my-braket-results/checkpoints/vqe-hydrogen/",
    "localPath": "/opt/braket/checkpoints"
  }' \
  --instance-config '{
    "instanceType": "ml.m5.large",
    "instanceCount": 1,
    "volumeSizeInGb": 30
  }' \
  --stopping-condition '{"maxRuntimeInSeconds": 3600}' \
  --hyper-parameters '{
    "num_qubits": "4",
    "max_iterations": "100",
    "device_arn": "arn:aws:braket:::device/quantum-simulator/amazon/sv1"
  }'

# --- Get job status ---
aws braket get-job --job-arn "arn:aws:braket:us-east-1:123456789012:job/vqe-hydrogen-molecule"

# --- Search jobs ---
aws braket search-jobs \
  --filters '[{"name": "status", "values": ["RUNNING"]}]'

aws braket search-jobs \
  --filters '[{"name": "jobName", "values": ["vqe-*"]}]'

# --- Cancel a job ---
aws braket cancel-job \
  --job-arn "arn:aws:braket:us-east-1:123456789012:job/vqe-hydrogen-molecule"
```

---

## Tag Management

```bash
# --- Tag a resource (quantum task or job) ---
aws braket tag-resource \
  --resource-arn "arn:aws:braket:us-east-1:123456789012:quantum-task/a1b2c3d4-e5f6-7890-abcd-ef1234567890" \
  --tags '{"Project": "VQEExperiment", "Team": "QuantumResearch"}'

aws braket tag-resource \
  --resource-arn "arn:aws:braket:us-east-1:123456789012:job/vqe-hydrogen-molecule" \
  --tags '{"Experiment": "H2-VQE-Run01", "Researcher": "alice@example.com"}'

# --- List tags for a resource ---
aws braket list-tags-for-resource \
  --resource-arn "arn:aws:braket:us-east-1:123456789012:quantum-task/a1b2c3d4-e5f6-7890-abcd-ef1234567890"

# --- Remove tags from a resource ---
aws braket untag-resource \
  --resource-arn "arn:aws:braket:us-east-1:123456789012:quantum-task/a1b2c3d4-e5f6-7890-abcd-ef1234567890" \
  --tag-keys '["Project", "Team"]'
```

---

## Notes

- **Notebooks**: Braket notebooks are SageMaker-backed; manage them via `aws sagemaker` CLI or the Braket/SageMaker console — there is no `aws braket` subcommand for notebooks.
- **Braket Direct**: Dedicated QPU access is arranged through the Braket console or AWS account team; no CLI commands for reservation management.
- Task results are written to the S3 bucket and key prefix specified at task creation time.
