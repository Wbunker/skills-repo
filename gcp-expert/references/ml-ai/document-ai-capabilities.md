# Document AI — Capabilities

## Purpose

Document AI is a managed service for extracting structured data from documents using a combination of computer vision, OCR, and NLP. It eliminates the need to build custom document parsing pipelines. Document AI provides pre-trained parsers for common document types and supports training custom extractors for proprietary document formats.

---

## Core Concepts

### Processor
A processor is a Document AI resource that encapsulates a trained model for a specific document type. Each processor belongs to a project and region. You call the processor's API endpoint to process documents.

Processor resource name: `projects/PROJECT_ID/locations/REGION/processors/PROCESSOR_ID`

### Processor Version
Each processor can have multiple versions. You can deploy, undeploy, set a default, and compare versions. Custom Document Extractor supports training new versions on your labeled data.

### Process Request
A single synchronous API call to process one document. Supports inline document bytes (base64) or a Cloud Storage URI. Maximum document size: 20 MB inline or GCS; 10 MB PDF for synchronous.

### Batch Process Request
An asynchronous operation to process multiple documents from Cloud Storage. Results written to a Cloud Storage output prefix. Use for large volumes (hundreds to thousands of documents).

### Document (Response Object)
The structured output from processing a document. Contains:
- `text`: the full OCR text of the document
- `pages`: list of pages, each with layout info, blocks, paragraphs, lines, tokens, visual elements
- `entities`: extracted named entities (key-value pairs, normalized values)
- `shards`: for multi-page documents split across API calls
- `error`: any processing errors

---

## Pre-trained Processors

### Enterprise Document OCR
**Purpose**: High-accuracy text extraction from any document type.
**Output**: `text` field with full document text; `pages` with character-level layout and confidence scores.
**Supports**: PDF, TIFF, GIF, JPEG, PNG, BMP, WebP.
**Use when**: you need accurate OCR output and will post-process the text yourself.
**Features**: handwriting recognition, table extraction, form field detection.

### Form Parser
**Purpose**: Extract key-value pairs from structured forms (tax forms, questionnaires, applications).
**Output**: `entities` with detected form field names and values; `pages[].formFields` with key-value pairs and bounding boxes.
**Use when**: documents have consistent form layouts with labeled fields (e.g., "Name:", "Date:", "Signature:").

### Invoice Parser
**Purpose**: Extract structured data from vendor invoices.
**Output entities**: `invoice_id`, `invoice_date`, `due_date`, `vendor_name`, `vendor_address`, `ship_to_name`, `ship_to_address`, `line_item` (description, quantity, unit_price, amount), `subtotal`, `total_tax`, `total_amount`, `currency`, `purchase_order`.
**Normalized values**: amounts normalized to numeric type; dates normalized to ISO 8601.

### Expense Parser (Receipt/Expense)
**Purpose**: Extract data from retail receipts and expense reports.
**Output entities**: `merchant_name`, `merchant_address`, `transaction_date`, `transaction_time`, `total_amount`, `currency`, `line_item` (description, quantity, unit_price, amount), `tip`, `tax`.

### Identity Document Parser
**Purpose**: Extract data from government-issued identity documents.
**Document types**: US/international passports, US driver's licenses, national identity cards.
**Output entities**: `given_names`, `family_name`, `document_id`, `expiry_date`, `date_of_birth`, `address`, `portrait` (image of face), MRZ line data.
**Compliance note**: check regional data processing regulations before sending identity documents to cloud APIs.

### US Tax Form Parsers
- **W2 Parser**: extract employer/employee information, wages, withholding amounts from W-2 forms.
- **1099 Parser**: supports 1099-INT, 1099-DIV, 1099-MISC, 1099-NEC forms.
- **Pay Stub Parser**: extract earnings, deductions, and YTD amounts from pay stubs.

### Lending Document Parsers
Specialized parsers for US mortgage and lending industry documents:
- Bank statements
- Pay stubs (lending-specific)
- 1003 Uniform Residential Loan Application
- 1040 US Individual Income Tax Return
- Property appraisal reports

### Contract Document Understanding
**Purpose**: Extract clauses, parties, dates, and obligations from legal contracts.
**Output**: contract type, parties, effective date, term, governing law, payment terms, key obligation entities.

### Custom Document Extractor (CDE)
**Purpose**: Train a custom extraction model for your proprietary document types not covered by pre-built parsers.
**Workflow**:
1. Create a Custom Document Extractor processor.
2. Upload sample documents to Cloud Storage.
3. Label entities using the Document AI Workbench labeling tool in the Console.
4. Train a new processor version (fine-tunes a base model on your labeled data).
5. Evaluate: review precision/recall per entity type.
6. Deploy the version.

**Minimum data requirements**: 10 labeled documents per entity type (50+ recommended for high accuracy).
**Entity types**: define your own entity names (e.g., `contract_number`, `delivery_date`, `product_sku`).

### Document Classifier
**Purpose**: Route incoming documents to the correct specialized parser automatically.
**Use case**: multi-document workflows where the document type is unknown (e.g., a mixed batch of invoices, receipts, and contracts).
**Output**: document type label with confidence score.
**Can be combined**: use the classifier's output to dynamically route to the correct parser.

---

## HITL (Human-in-the-Loop) Review

For high-stakes document processing where low-confidence extractions must be reviewed by a human:
- Configure a **review threshold**: entities below this confidence score are flagged for review.
- Document AI sends flagged documents to a **Human Review queue** (stored in Cloud Storage).
- Reviewers access the queue via the Document AI Workbench in the Console to verify/correct extractions.
- Reviewed documents can feed back into training data to improve the model.
- Integrated with Cloud Storage for document storage and Cloud Tasks for queue management.

---

## Document AI Warehouse (Enterprise)

Document AI Warehouse is a full **document management system** built on top of Document AI extraction:
- **Ingest**: upload documents via API or connectors; automatically extract entities with Document AI processors
- **Schema**: define custom document schemas (metadata fields) per document type
- **Search**: full-text search and structured search across document metadata and extracted content
- **Access control**: IAM-based document-level access control
- **Versions**: document versioning and audit history
- **Linking**: link related documents (e.g., contract → invoice → payment)
- **Use case**: contract lifecycle management, loan origination systems, regulatory document repositories

---

## Supported Document Formats

| Format | Synchronous | Batch | Notes |
|---|---|---|---|
| PDF | Yes | Yes | Up to 15 pages synchronous; up to 2,000 pages batch |
| GIF | Yes | Yes | Multi-frame treated as multi-page |
| TIFF | Yes | Yes | Multi-page supported |
| JPEG | Yes | Yes | Single image |
| PNG | Yes | Yes | Single image |
| BMP | Yes | Yes | Single image |
| WebP | Yes | Yes | Single image |

---

## Pricing Factors

- Billed per page processed.
- OCR-based parsers (Form Parser, custom) cost less than specialized parsers (Invoice, Identity).
- Human review adds additional per-page cost.
- Batch processing same price as synchronous.
- First X pages per month free (varies by processor).

---

## Best Practices

1. **Use synchronous processing for real-time user-facing workflows** and batch processing for back-office bulk workflows.
2. **Validate entity confidence scores** before writing to downstream systems; set an application-level threshold (e.g., 0.85) below which you escalate to human review or flag for correction.
3. **Use the Document Classifier first** for mixed-document-type workflows; don't send invoices to the Form Parser or vice versa.
4. **Label at least 50 examples per entity type** for Custom Document Extractor before evaluating; fewer labels produce unreliable precision/recall estimates.
5. **Normalize extracted values**: Document AI returns raw text; use normalized fields (`money_value`, `date_value`) where available instead of parsing raw text strings.
6. **Store raw processor output** alongside the processed result; the raw output allows reprocessing without re-sending documents to the API.
7. **Use batch processing with Cloud Storage for document pipelines**: poll the long-running operation or use Eventarc to trigger downstream processing when batch results are ready.
8. **Enable HITL for critical financial or identity documents**: human review on low-confidence extractions prevents costly downstream errors.
9. **Test with diverse document samples**: processor accuracy varies with document quality, layout variation, fonts, and scan resolution; test with representative samples before production deployment.
10. **Tune the base processor with domain data**: even pre-built parsers can be fine-tuned (in processors that support versioning) on your specific document samples to improve accuracy for your document population.
