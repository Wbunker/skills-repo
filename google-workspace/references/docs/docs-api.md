# Google Docs API Reference

Base URL: `https://docs.googleapis.com/v1/documents/{documentId}`

## Table of Contents
1. [Core Concepts](#core-concepts)
2. [Create & Get Documents](#create--get-documents)
3. [Reading Document Content](#reading-document-content)
4. [batchUpdate Requests](#batchupdate-requests)
5. [Inserting Text & Content](#inserting-text--content)
6. [Deleting Content](#deleting-content)
7. [Text Styling](#text-styling)
8. [Paragraph Styles](#paragraph-styles)
9. [Tables](#tables)
10. [Common Patterns](#common-patterns)

---

## Core Concepts

- **Document ID**: Found in the URL: `https://docs.google.com/document/d/{DOCUMENT_ID}/edit`
- **All edits via `batchUpdate`**: Every modification uses `documents.batchUpdate` with a list of typed request objects. There is no "write text to position X" shortcut — you must know the index.
- **Indices**: Document content uses 0-based character indices. Index 0 is the start of the document body. Indices must be valid (within the current document length).
- **Structural Elements**: Documents contain `content` (list of structural elements: paragraphs, tables, table of contents, section breaks).
- **Paragraph elements**: Paragraphs contain `elements`, each with a `textRun` or inline object.
- **End of body index**: The document always has a trailing newline. Insert before `body.content[-1].endIndex - 1` to append at the end.

---

## Create & Get Documents

### Create a document

```python
service = build('docs', 'v1', credentials=creds)

doc = service.documents().create(
    body={'title': 'My New Document'}
).execute()

document_id = doc['documentId']
print(f"Created: https://docs.google.com/document/d/{document_id}/edit")
```

### Get a document

```python
doc = service.documents().get(documentId=document_id).execute()

print(f"Title: {doc['title']}")
print(f"Revision: {doc['revisionId']}")

# Document body content
body = doc['body']
content = body.get('content', [])
print(f"Body elements: {len(content)}")
print(f"End index: {body['content'][-1]['endIndex']}")  # Total document length
```

---

## Reading Document Content

### Extract all text

```python
def extract_text(doc: dict) -> str:
    """Extract plain text from all body paragraphs."""
    text_parts = []
    for element in doc['body'].get('content', []):
        if 'paragraph' in element:
            for pe in element['paragraph'].get('elements', []):
                if 'textRun' in pe:
                    text_parts.append(pe['textRun']['content'])
    return ''.join(text_parts)

doc = service.documents().get(documentId=document_id).execute()
text = extract_text(doc)
```

### Extract text with structure

```python
def extract_structured(doc: dict) -> list[dict]:
    """Return list of {type, text, style} for each paragraph."""
    result = []
    for element in doc['body'].get('content', []):
        if 'paragraph' in element:
            para = element['paragraph']
            style = para.get('paragraphStyle', {}).get('namedStyleType', 'NORMAL_TEXT')
            text = ''.join(
                pe.get('textRun', {}).get('content', '')
                for pe in para.get('elements', [])
            )
            result.append({'type': style, 'text': text.rstrip('\n')})
        elif 'table' in element:
            result.append({'type': 'TABLE', 'text': '[table]'})
        elif 'sectionBreak' in element:
            result.append({'type': 'SECTION_BREAK', 'text': ''})
    return result
```

### Find text and its index

```python
def find_text(doc: dict, search: str) -> list[dict]:
    """Find all occurrences of search text, return list of {start, end, text}."""
    results = []
    for element in doc['body'].get('content', []):
        if 'paragraph' in element:
            for pe in element['paragraph'].get('elements', []):
                tr = pe.get('textRun', {})
                content = tr.get('content', '')
                if search in content:
                    start = pe['startIndex'] + content.index(search)
                    results.append({
                        'start': start,
                        'end': start + len(search),
                        'text': search
                    })
    return results
```

---

## batchUpdate Requests

All modifications use `documents.batchUpdate`:

```python
result = service.documents().batchUpdate(
    documentId=document_id,
    body={
        'requests': [
            # ... list of request objects
        ]
    }
).execute()
```

Requests are applied in order. Indices shift as content is inserted/deleted — structure later requests accordingly (insert from end to start, or recalculate after each request).

---

## Inserting Text & Content

### Insert text at a position

```python
# Insert text at the beginning of the document (index 1)
service.documents().batchUpdate(
    documentId=document_id,
    body={
        'requests': [{
            'insertText': {
                'location': {'index': 1},
                'text': 'Hello, world!\n'
            }
        }]
    }
).execute()
```

### Append text to the end

```python
doc = service.documents().get(documentId=document_id).execute()
end_index = doc['body']['content'][-1]['endIndex'] - 1  # Before final newline

service.documents().batchUpdate(
    documentId=document_id,
    body={
        'requests': [{
            'insertText': {
                'location': {'index': end_index},
                'text': '\nNew paragraph at end.\n'
            }
        }]
    }
).execute()
```

### Insert a page break

```python
service.documents().batchUpdate(
    documentId=document_id,
    body={
        'requests': [{
            'insertPageBreak': {
                'location': {'index': end_index}
            }
        }]
    }
).execute()
```

---

## Deleting Content

### Delete a range of content

```python
service.documents().batchUpdate(
    documentId=document_id,
    body={
        'requests': [{
            'deleteContentRange': {
                'range': {
                    'startIndex': 5,
                    'endIndex': 20
                }
            }
        }]
    }
).execute()
```

### Replace all occurrences of a string

```python
service.documents().batchUpdate(
    documentId=document_id,
    body={
        'requests': [{
            'replaceAllText': {
                'containsText': {
                    'text': '{{CUSTOMER_NAME}}',
                    'matchCase': True
                },
                'replaceText': 'Acme Corporation'
            }
        }]
    }
).execute()
```

**Template fill pattern** — replace multiple placeholders at once:

```python
def fill_template(service, document_id: str, replacements: dict):
    """Replace {{KEY}} placeholders in a document."""
    requests = [
        {
            'replaceAllText': {
                'containsText': {'text': f'{{{{{key}}}}}', 'matchCase': True},
                'replaceText': str(value)
            }
        }
        for key, value in replacements.items()
    ]
    service.documents().batchUpdate(
        documentId=document_id,
        body={'requests': requests}
    ).execute()

fill_template(service, document_id, {
    'CUSTOMER_NAME': 'Acme Corp',
    'DATE': '2024-01-15',
    'AMOUNT': '$1,500.00',
})
```

---

## Text Styling

Apply formatting to a range of text:

```python
service.documents().batchUpdate(
    documentId=document_id,
    body={
        'requests': [{
            'updateTextStyle': {
                'range': {
                    'startIndex': 5,
                    'endIndex': 25
                },
                'textStyle': {
                    'bold': True,
                    'italic': False,
                    'underline': False,
                    'strikethrough': False,
                    'fontSize': {'magnitude': 14, 'unit': 'PT'},
                    'foregroundColor': {
                        'color': {'rgbColor': {'red': 0.1, 'green': 0.2, 'blue': 0.8}}
                    },
                    'fontFamily': 'Arial',
                    'link': {'url': 'https://example.com'},  # Hyperlink
                },
                'fields': 'bold,italic,fontSize,foregroundColor,fontFamily'
            }
        }]
    }
).execute()
```

**`fields` mask**: Only update specified properties. Use `'*'` for all fields, or comma-separate specific ones. Required to avoid unintentionally clearing unspecified properties.

---

## Paragraph Styles

```python
service.documents().batchUpdate(
    documentId=document_id,
    body={
        'requests': [{
            'updateParagraphStyle': {
                'range': {
                    'startIndex': 0,
                    'endIndex': 50
                },
                'paragraphStyle': {
                    'namedStyleType': 'HEADING_1',  # NORMAL_TEXT | HEADING_1..6 | TITLE | SUBTITLE
                    'alignment': 'CENTER',           # START | CENTER | END | JUSTIFIED
                    'spaceAbove': {'magnitude': 12, 'unit': 'PT'},
                    'spaceBelow': {'magnitude': 6,  'unit': 'PT'},
                    'indentFirstLine': {'magnitude': 36, 'unit': 'PT'},
                },
                'fields': 'namedStyleType,alignment,spaceAbove,spaceBelow'
            }
        }]
    }
).execute()
```

---

## Tables

### Insert a table

```python
doc = service.documents().get(documentId=document_id).execute()
end_index = doc['body']['content'][-1]['endIndex'] - 1

service.documents().batchUpdate(
    documentId=document_id,
    body={
        'requests': [{
            'insertTable': {
                'rows': 4,
                'columns': 3,
                'location': {'index': end_index}
            }
        }]
    }
).execute()
```

### Insert text into a table cell

After inserting a table, get the document again to find table cell indices:

```python
doc = service.documents().get(documentId=document_id).execute()

# Walk content to find table cells
def get_table_cell_indices(doc: dict) -> list[tuple[int, int]]:
    """Return [(startIndex, endIndex)] for each table cell's content."""
    cells = []
    for element in doc['body'].get('content', []):
        if 'table' in element:
            for row in element['table'].get('tableRows', []):
                for cell in row.get('tableCells', []):
                    for content in cell.get('content', []):
                        if 'paragraph' in content:
                            cells.append((content['startIndex'], content['endIndex']))
    return cells
```

---

## Common Patterns

### Copy a template document and fill it

```python
from googleapiclient.discovery import build

def create_from_template(drive_service, docs_service,
                          template_id: str, title: str,
                          replacements: dict, folder_id: str = None) -> str:
    """
    Copy a template document, fill placeholders, return new document ID.
    """
    body = {'name': title}
    if folder_id:
        body['parents'] = [folder_id]

    # Copy via Drive API
    copy = drive_service.files().copy(
        fileId=template_id,
        body=body
    ).execute()
    new_doc_id = copy['id']

    # Fill placeholders
    fill_template(docs_service, new_doc_id, replacements)

    return new_doc_id

new_id = create_from_template(
    drive_service=drive,
    docs_service=docs,
    template_id='1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgVE2upms',
    title='Invoice - Acme Corp - Jan 2024',
    replacements={
        'CUSTOMER': 'Acme Corp',
        'INVOICE_DATE': '2024-01-15',
        'DUE_DATE': '2024-02-15',
        'AMOUNT': '$2,500.00',
    },
    folder_id='1a2b3c4d5e6f'
)
print(f"Created: https://docs.google.com/document/d/{new_id}/edit")
```

### Read document and export as PDF

```python
# Via Drive API (export Google Doc as PDF)
pdf_content = drive_service.files().export(
    fileId=document_id,
    mimeType='application/pdf'
).execute()

with open('document.pdf', 'wb') as f:
    f.write(pdf_content)
```

### Scope Reference

| Scope | Access |
|-------|--------|
| `https://www.googleapis.com/auth/documents.readonly` | Read only |
| `https://www.googleapis.com/auth/documents` | Full read/write |
| `https://www.googleapis.com/auth/drive` | All Drive files (broader) |
