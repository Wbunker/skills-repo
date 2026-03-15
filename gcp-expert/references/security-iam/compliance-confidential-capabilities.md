# Assured Workloads & Confidential Computing — Capabilities Reference

For CLI commands, see [compliance-confidential-cli.md](compliance-confidential-cli.md).

## Assured Workloads

**Purpose**: Compliance controls framework for regulated workloads on Google Cloud; enforces data residency, access controls, and compliance posture for government and regulated industries.

### Core Concepts

| Concept | Description |
|---|---|
| **Workload** | A folder in the GCP resource hierarchy with compliance controls applied |
| **Compliance Regime** | The regulatory framework being enforced (FedRAMP, ITAR, HIPAA, etc.) |
| **Data Residency** | Restricts data storage and processing to specific regions (e.g., US only) |
| **Personnel Data Access** | Controls and limits access to data by Google personnel |
| **Support Personnel** | For IL4/IL5: access restricted to US Citizens |
| **Org Policy Constraints** | Automatically applied constraints to enforce regime requirements |
| **Violation Monitoring** | Alerts when workload drifts out of compliance with its regime |
| **Control Package** | Pre-defined set of org policies and access controls for a given regime |

### Supported Compliance Regimes

| Regime | Description | Key Controls |
|---|---|---|
| **FedRAMP Moderate** | US Federal Risk and Authorization Management Program - Moderate | US data residency, limited Google access |
| **FedRAMP High** | FedRAMP for high-impact systems | US data residency, US-person access only, enhanced controls |
| **DoD IL2** | Department of Defense Impact Level 2 | US regions, FedRAMP Moderate baseline |
| **DoD IL4** | DoD Impact Level 4 (CUI) | US regions, US-person access only for support |
| **DoD IL5** | DoD Impact Level 5 (National Security) | Dedicated infrastructure, US-person access |
| **ITAR** | International Traffic in Arms Regulations | US data residency, US-person access controls |
| **CJIS** | Criminal Justice Information Services | FBI-compliant controls for law enforcement |
| **HIPAA** | Health Insurance Portability and Accountability Act | BAA with Google, PHI controls |
| **HITRUST** | Health Information Trust Alliance | Healthcare data security controls |
| **EU Sovereign Controls** | European Union data boundary | EU data residency, EU-person access controls |
| **Australia Regions** | Australian data residency | AU-region restriction |
| **Canada Regions** | Canadian data residency | Canada-region restriction |

### What Assured Workloads Enforces

1. **Data Residency**: Org policies restrict resource creation to compliant regions; prevents accidental data placement outside boundary
2. **Access Controls**: Restricts Google personnel with data access to US Citizens (for ITAR/IL4/IL5); Access Approval enabled
3. **Key Management**: Requires CMEK with Cloud KMS or EKM; key residency in compliant region
4. **Monitoring**: Violation detection; alerts when org policies are violated or resources drift
5. **Compliance Dashboard**: Overview of compliance status in Security Command Center

### Supported Services in Assured Workloads
Not all GCP services are FedRAMP/ITAR authorized. Assured Workloads restricts which services can be used within the workload folder. Authorized services include: Compute Engine, GKE, Cloud Storage, BigQuery, Cloud SQL, Cloud Run, Pub/Sub, and ~100+ services. See Google's FedRAMP Authorization Package for current list.

### Assured Workloads Folder Structure
```
Organization
└── Assured Workloads Folder (compliance regime applied)
    ├── Project A (inherits controls)
    └── Project B (inherits controls)
```
All projects created inside an Assured Workloads folder automatically inherit compliance controls.

### Key Limitations
- Cannot move existing projects into Assured Workloads folders (must create new)
- Some services are not available in all regimes (check authorization status)
- Data residency controls prevent use of global services that cache data outside the boundary
- Assured Workloads is separate from FedRAMP authorization — using Assured Workloads enables compliance but doesn't automatically make your workload compliant

---

## Confidential Computing

**Purpose**: Encrypts data in use (in memory) using hardware-based Trusted Execution Environments (TEEs); protects sensitive data even from the cloud provider.

### Core Concepts

| Concept | Description |
|---|---|
| **Confidential VM** | GCE VM with AMD SEV (Secure Encrypted Virtualization); memory encrypted with VM-specific key managed by AMD hardware |
| **Confidential GKE Node** | GKE node pool using Confidential VMs; all pods on the node have encrypted memory |
| **Confidential Dataflow** | Dataflow workers run on Confidential VMs; pipeline data encrypted in memory |
| **Confidential Dataproc** | Dataproc cluster nodes use Confidential VMs |
| **Confidential Space** | Multi-party computation; run workloads in TEE; attestation proves code hasn't been tampered with; input data encrypted from all parties |
| **AMD SEV** | Secure Encrypted Virtualization; hardware memory encryption with per-VM keys |
| **AMD SEV-SNP** | SEV with Secure Nested Paging; adds memory integrity protection and stronger attestation |
| **Intel TDX** | Trust Domain Extensions; Intel's equivalent to AMD SEV; available on select machine types |
| **Attestation** | Cryptographic proof that the TEE is genuine hardware and the workload code matches expected hash |
| **vTPM** | Virtual Trusted Platform Module; provides Shielded VM features + attestation for Confidential VMs |

### Confidential VM Details

**Supported Machine Types**: N2D (AMD EPYC Rome/Milan with SEV), C2D, M3, C3 (with SEV-SNP), select Intel with TDX

**Confidential VM vs Regular VM**:
- Memory encrypted at hardware level by AMD PSP (Platform Security Processor)
- ~5-10% performance overhead for most workloads
- Cannot live-migrate (migration policy must be TERMINATE)
- Requires Confidential-compatible OS images (CentOS, RHEL, Debian, Ubuntu, Container-Optimized OS, Windows)
- Logs attestation reports to Cloud Monitoring

### Confidential Space

Use case: two or more parties want to jointly analyze data without revealing raw data to each other or the cloud provider.

**Pattern**:
1. Party A encrypts their data to the Confidential Space TEE key
2. Party B encrypts their data to the Confidential Space TEE key
3. Workload runs in Confidential Space (TEE); only decrypts data if attestation passes
4. Neither party can see the other's raw data; Google cannot see either party's data
5. Results returned to authorized parties

**Example use cases**: healthcare data collaboration (hospital A + hospital B run joint ML without exposing patient records), financial fraud detection across institutions, genomics research

### Shielded VMs (Related)
Shielded VMs provide: Secure Boot, vTPM, Integrity Monitoring. Not full TEE encryption, but protection against boot-time malware.
- Secure Boot: only signed boot components load
- vTPM: measured boot; baseline stored; deviation alerts via Cloud Monitoring
- Integrity Monitoring: compare boot measurement to known-good baseline

### When to Use Confidential Computing

- **Regulatory compliance**: ITAR, HIPAA, FedRAMP High — encrypt data even from cloud provider
- **Multi-party computation**: joint ML or analytics across organizations with Confidential Space
- **IP protection**: run proprietary ML models without exposing weights to cloud infrastructure
- **Financial services**: meet data-in-use encryption requirements
- **Healthcare**: PHI processing in untrusted environments

### Important Patterns & Constraints

- Confidential VMs cannot live-migrate; set `--maintenance-policy=TERMINATE` (VM stops, doesn't migrate on host maintenance)
- Performance overhead: ~5-10% for memory-intensive workloads; less for compute-bound
- Confidential GKE nodes require N2D or C2D machine types
- Confidential Space uses Workload Identity Federation for attestation-based token exchange
- AMD SEV does NOT protect against a malicious OS kernel (only hypervisor isolation); SEV-SNP adds stronger isolation
- Attestation reports are sent to Cloud Monitoring automatically for Confidential VMs
