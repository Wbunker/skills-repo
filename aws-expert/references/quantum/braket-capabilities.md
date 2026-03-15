# Amazon Braket — Capabilities Reference

For CLI commands, see [braket-cli.md](braket-cli.md).

---

## Overview

Amazon Braket is a fully managed quantum computing service for experimenting with quantum algorithms. It provides access to quantum processing units (QPUs) from multiple hardware vendors, managed simulators, and a development environment for building and running quantum algorithms.

---

## Core Concepts

| Concept | Description |
|---|---|
| **Quantum Task** | A single execution of a quantum circuit or annealing problem on a QPU or simulator. Unit of work and billing. |
| **Device** | A QPU (quantum hardware) or managed simulator available through Braket. Identified by a device ARN. |
| **Circuit** | A quantum program expressed as a sequence of quantum gates applied to qubits. Used with gate-based QPUs and simulators. |
| **Annealing Problem** | An optimization problem expressed as an Ising or QUBO (Quadratic Unconstrained Binary Optimization) formulation. Used with D-Wave. |
| **Shot** | A single execution of a quantum circuit measurement; results are probabilistic. Tasks run a specified number of shots and return aggregated measurement results. |
| **Hybrid Job** | A job combining classical computation (on EC2/managed container) with quantum task calls in a loop (e.g., variational algorithms like VQE, QAOA). |

---

## Supported Hardware (QPUs)

| Provider | Device | Type | Technology | Notes |
|---|---|---|---|---|
| **IonQ** | Harmony, Aria | Gate-based | Trapped ion | High fidelity; all-to-all connectivity; slower gate times |
| **Rigetti** | Aspen-M series | Gate-based | Superconducting | Fixed topology; faster gate times; QUIL language |
| **OQC (Oxford Quantum Circuits)** | Lucy | Gate-based | Superconducting | 8-qubit processor |
| **IQM** | Garnet | Gate-based | Superconducting | 20-qubit processor |
| **D-Wave** | Advantage | Quantum annealing | Superconducting flux qubits | Optimization problems; 5000+ qubits; not universal gate-based |

### QPU Access Notes

- QPU time is billed **per-task + per-shot**
- Devices have maintenance windows (offline periods); check device availability before submitting
- Queue depth varies by device; tasks are queued and executed when device is available
- Native gate sets differ by QPU; Braket SDK handles transpilation
- Regional availability varies by device; not all QPUs are available in all regions

---

## Managed Simulators

| Simulator | Name | Max Qubits | Billing | Description |
|---|---|---|---|---|
| **SV1** | State vector | 34 qubits | Per task | Full state vector simulation; exact results; parallelized across managed compute |
| **DM1** | Density matrix | 17 qubits | Per task | Simulates noise models; models decoherence and gate errors |
| **TN1** | Tensor network | 50 qubits (circuit-dependent) | Per task | Efficient for low-entanglement circuits; can simulate more qubits if circuit structure allows |

- Simulators are always available (no queue, no maintenance windows)
- Billed per-task (flat rate), not per-shot
- SV1 and DM1 support parallelism; TN1 uses distributed tensor contraction
- **Local simulators** (via SDK): run on your local machine; free

---

## Amazon Braket SDK

The open-source Python SDK (`amazon-braket-sdk-python`) is the primary development interface. Key classes:

| Class / Module | Purpose |
|---|---|
| `braket.circuits.Circuit` | Build quantum circuits using gates |
| `braket.aws.AwsDevice` | Reference a QPU or managed simulator by ARN |
| `braket.aws.AwsQuantumTask` | Submit and poll quantum tasks |
| `braket.devices.LocalSimulator` | Run circuits locally without AWS calls |
| `amazon-braket-pennylane-plugin` | PennyLane plugin to use Braket devices as PennyLane backends for QML |

```python
from braket.aws import AwsDevice, AwsQuantumTask
from braket.circuits import Circuit

# Build a Bell state circuit
circuit = Circuit().h(0).cnot(0, 1)

# Run on SV1 simulator
device = AwsDevice("arn:aws:braket:::device/quantum-simulator/amazon/sv1")
task = device.run(circuit, shots=1000, s3_destination_folder=("my-braket-bucket", "results/"))
result = task.result()
print(result.measurement_counts)
```

---

## Hybrid Jobs (Amazon Braket Hybrid Jobs)

**Purpose**: Execute variational quantum algorithms that alternate between classical optimization steps and quantum circuit execution (e.g., VQE, QAOA, QML).

| Concept | Description |
|---|---|
| **Job** | A containerized execution environment (managed EC2) that calls QPUs/simulators in a loop |
| **Algorithm script** | Python script using the Braket SDK and PennyLane; submitted as the job entry point |
| **PennyLane integration** | Open-source QML library; Braket provides a PennyLane plugin for using Braket devices as PennyLane backends |
| **Managed containers** | Pre-built containers with PennyLane, TensorFlow, or PyTorch pre-installed |
| **Instance type** | Classical compute instance for the job container (e.g., `ml.m5.large`, `ml.p3.2xlarge` for GPU-accelerated classical steps) |
| **Priority access** | Jobs get priority QPU access during execution (skips the public task queue) |
| **Checkpointing** | Jobs can checkpoint state to S3, allowing restart without losing progress |
| **Job metrics** | Classical and quantum metrics emitted to CloudWatch during job execution |

### Job Lifecycle

`QUEUED` → `RUNNING` → `COMPLETED` / `FAILED` / `CANCELLED`

---

## Amazon Braket Direct

**Purpose**: On-demand, dedicated QPU access for research teams with high-throughput requirements.

- Reserve dedicated QPU time blocks (reserved capacity)
- Bypass the shared task queue
- Available for IonQ, Rigetti, and OQC hardware
- Managed through the Braket console or account team

---

## Amazon Braket Notebooks

- Managed Jupyter notebooks (Amazon SageMaker-backed) pre-installed with the Braket SDK, PennyLane, and example algorithms
- Created and managed via the Braket Console (not directly via Braket CLI; managed via SageMaker CLI/console)
- Pre-built notebook examples: Bell state, Grover's algorithm, QAOA, VQE, QML tutorials

---

## Pricing Model

| Resource | Pricing basis |
|---|---|
| **QPU task** | Per-task fee (flat, varies by device) + per-shot fee × number of shots |
| **Managed simulators (SV1, DM1, TN1)** | Per-task flat fee (no per-shot charge) |
| **Local simulators** | Free (runs on your local machine via SDK) |
| **Hybrid Jobs (classical compute)** | Per-minute billing for the EC2 instance used |
| **Notebooks** | Standard SageMaker notebook instance pricing |

### Example QPU Pricing (approximate, varies by region/device)

| Device | Per-task | Per-shot |
|---|---|---|
| IonQ | ~$0.30 | ~$0.01 |
| Rigetti | ~$0.30 | ~$0.0009 |
| D-Wave | ~$0.30 | ~$0.00019 |
| SV1 simulator | ~$0.075 | No per-shot fee |

---

## Important Limits & Quotas

| Resource | Limit |
|---|---|
| Concurrent quantum tasks per account per QPU | 5 (soft limit) |
| Concurrent Hybrid Jobs | 5 (soft limit) |
| Maximum shots per task (gate-based QPU) | 10,000 (device-dependent) |
| Quantum task result retention | Results stored in your S3 bucket; no automatic expiration |

---

## Integration Patterns

| Pattern | Description |
|---|---|
| **Braket + S3** | All task results stored in S3; use S3 event notifications to trigger downstream processing via Lambda |
| **Braket + SageMaker** | Run quantum-classical hybrid ML workflows combining SageMaker training jobs with Braket quantum tasks |
| **Braket + Step Functions** | Orchestrate multi-stage quantum workflows; poll task status in a Step Functions wait-for-callback pattern |
