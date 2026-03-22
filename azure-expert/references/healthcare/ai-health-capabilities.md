# Azure AI Health Services — Capabilities Reference
For CLI commands, see [ai-health-cli.md](ai-health-cli.md).

## Azure Health Bot

**Purpose**: Managed intelligent health bot service for building HIPAA-eligible healthcare chatbots. Pre-built healthcare knowledge, medical database integrations, and customizable clinical scenarios — deployed for patient triage, symptom checking, scheduling, and general health information.

### Key Capabilities

| Capability | Details |
|---|---|
| **Pre-built scenarios** | COVID-19 assessment, symptom triage, medication info, appointment scheduling |
| **Medical databases** | CDC, WHO, Infermedica (symptom checker AI), UMLS medical terminologies |
| **Custom scenarios** | Visual scenario editor; branching conversation flows; code steps (JavaScript) |
| **Clinical decision support** | Infermedica API integration for probabilistic differential diagnoses |
| **Channels** | Web chat widget, Microsoft Teams, Facebook Messenger, LINE, WhatsApp (via Azure Communication Services) |
| **Authentication** | Azure AD (staff), Azure AD B2C / Entra External ID (patients), anonymous |
| **EHR integration** | FHIR API calls from within scenarios; real-time patient data retrieval |
| **Localization** | Multiple languages; auto-translate capabilities |
| **Analytics** | Built-in conversation analytics; session counts, completion rates, symptom patterns |
| **HIPAA eligibility** | Covered by Microsoft BAA; PHI handling enabled |

### Bot Scenario Types

| Type | Description |
|---|---|
| **Triage** | Symptom assessment → triage recommendation (emergency/urgent/routine) |
| **Information** | Answer health FAQs from integrated medical knowledge bases |
| **Appointment** | Schedule/cancel/reschedule appointments via backend API call |
| **Medication** | Drug information, interactions, adherence reminders |
| **Post-discharge** | Follow-up care instructions, symptom monitoring after discharge |
| **Custom** | Any conversational flow with API integrations |

### Integration Points

- **FHIR Service**: Fetch patient records (observations, medications, conditions) within scenarios
- **Azure Functions**: Custom logic steps within bot scenarios
- **Azure Logic Apps**: Trigger workflows (e.g., escalate to human agent, notify care team)
- **Teams**: Deploy as Teams app for staff-facing tools (nurse triage, clinical decision support)
- **Web widget**: Embed in patient portal websites

---

## Text Analytics for Health

**Purpose**: Pre-trained NLP service for extracting and structuring medical entities from unstructured clinical text (clinical notes, discharge summaries, radiology reports, patient messages).

### Extracted Entity Categories

| Category | Examples |
|---|---|
| **Diagnoses / Conditions** | "Acute myocardial infarction", "Type 2 diabetes mellitus" |
| **Symptoms** | "chest pain", "shortness of breath", "dyspnea on exertion" |
| **Medications** | "metformin 500mg", "lisinopril 10mg daily" |
| **Dosage** | "500mg", "twice daily", "IV bolus" |
| **Routes of administration** | "oral", "intravenous", "subcutaneous" |
| **Body site** | "left lung", "right knee", "posterior fossa" |
| **Medical procedures** | "coronary artery bypass graft", "MRI of the brain" |
| **Examination / Test results** | "ejection fraction 35%", "troponin elevated" |
| **Family history** | "father had MI at age 55" |
| **Time references** | "3 days ago", "for the past 2 weeks", "chronic" |

### Relation Extraction

Identifies semantic relationships between entities:

| Relation Type | Example |
|---|---|
| **Direction** | "pain in the **left** knee" (Direction: left, Entity: knee) |
| **Body site of condition** | "fracture of the **right tibia**" |
| **Dosage of medication** | "**metformin** at **500mg**" |
| **Route of medication** | "**IV** metoprolol" |
| **Time of event** | "MI **3 years ago**" |
| **Qualifier** | "**moderate** chest pain" |
| **Assertion** | negation ("**no** chest pain"), conditional ("**if** fever persists") |

### Negation and Assertion Detection

```
Input: "Patient denies chest pain. No shortness of breath. History of hypertension."

Output:
- "chest pain": negated (denied)
- "shortness of breath": negated (no)
- "hypertension": historical (history of)
```

### FHIR Output

- Text Analytics for Health can return results as FHIR R4 resources
- Conditions, Medications, Observations as structured FHIR resources
- Enables direct ingestion into FHIR Service after NLP processing
- Use for: clinical note processing pipelines, CDI (Clinical Documentation Improvement)

### SDK Example

```python
from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.credentials import AzureKeyCredential

client = TextAnalyticsClient(endpoint=endpoint, credential=AzureKeyCredential(key))

documents = [
    "Patient is a 65-year-old male with Type 2 diabetes mellitus, managed on metformin 500mg twice daily. "
    "He presents with chest pain radiating to the left arm for 3 hours. No prior MI. "
    "Troponin elevated at 2.3. EKG shows ST elevation in leads II, III, aVF."
]

poller = client.begin_analyze_healthcare_entities(documents, language="en")
result = poller.result()

for doc in result:
    for entity in doc.entities:
        print(f"Entity: {entity.text}, Category: {entity.category}, "
              f"Subcategory: {entity.subcategory}, Confidence: {entity.confidence_score:.2f}")
    for relation in doc.entity_relations:
        print(f"Relation: {relation.relation_type}")
        for role in relation.roles:
            print(f"  {role.name}: {role.entity.text}")
```

### Use Cases

- **Clinical Documentation Improvement (CDI)**: Extract and validate ICD-10 coding from notes
- **Adverse event detection**: Identify medication side effects in clinical notes
- **Population health**: Aggregate conditions and medications across patient populations
- **Real-world evidence**: Extract structured data from clinical narratives for research
- **Risk stratification**: Identify high-risk patients from note content

---

## Azure AI Health Insights

**Purpose**: Preview suite of AI models for specialized healthcare clinical analytics. Goes beyond entity extraction to provide clinical decision support insights.

> Note: Azure AI Health Insights services are in public preview as of 2025. APIs may change.

### Radiology Insights

| Insight Type | Description |
|---|---|
| **Critical findings** | Detect radiological findings requiring urgent follow-up (pneumothorax, pulmonary embolism) |
| **Age/sex mismatch** | Flag when patient demographics don't match radiological findings |
| **Follow-up recommendations** | Extract follow-up recommendations from radiology report text |
| **Complete order mismatch** | Identify if findings relate to a different anatomy than ordered |
| **Laterality discrepancy** | Detect when "left" vs "right" differs between order and report |

### Clinical Trial Matching

- Match patients to eligible clinical trials based on inclusion/exclusion criteria
- Input: patient clinical data (FHIR resources or structured data)
- Output: list of matching trials with eligibility confidence scores
- Use cases: oncology trial enrollment, rare disease research
- Integrates with ClinicalTrials.gov registry

### Patient Timeline

- Reconstruct longitudinal patient care timeline from unstructured clinical documents
- Extract: diagnoses, procedures, medications, vital signs with temporal context
- Output: structured chronological view of patient history
- Use cases: care coordination, discharge summary generation, clinical review

### Oncology Insights (Preview)

| Insight | Description |
|---|---|
| **TNM staging extraction** | Extract tumor-node-metastasis staging from pathology/oncology notes |
| **Histology classification** | Identify cancer type and histology from notes |
| **Treatment line extraction** | Identify treatment lines (first-line, second-line) from clinical notes |
| **Biomarker extraction** | Extract mutation status (EGFR, BRCA, HER2, PD-L1) from reports |
