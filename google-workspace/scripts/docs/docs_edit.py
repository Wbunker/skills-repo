"""
Google Docs Edit Script
Covers: create documents, insert/delete text, replace placeholders, read content.
"""
from googleapiclient.errors import HttpError


# ---------------------------------------------------------------------------
# Create & Read
# ---------------------------------------------------------------------------

def create_doc(service, title: str) -> dict:
    """
    Create a new Google Document.

    Returns:
        Document resource with documentId.
    """
    return service.documents().create(body={'title': title}).execute()


def get_doc(service, document_id: str) -> dict:
    """Fetch the full document resource."""
    return service.documents().get(documentId=document_id).execute()


def get_end_index(doc: dict) -> int:
    """Return the index just before the document's trailing newline (safe append point)."""
    content = doc['body'].get('content', [])
    if not content:
        return 1
    return content[-1]['endIndex'] - 1


def extract_text(doc: dict) -> str:
    """Extract all plain text from the document body."""
    parts = []
    for element in doc['body'].get('content', []):
        if 'paragraph' in element:
            for pe in element['paragraph'].get('elements', []):
                if 'textRun' in pe:
                    parts.append(pe['textRun']['content'])
    return ''.join(parts)


def extract_paragraphs(doc: dict) -> list[dict]:
    """
    Return list of {style, text} for each paragraph.

    style values: 'NORMAL_TEXT', 'HEADING_1'...'HEADING_6', 'TITLE', 'SUBTITLE'
    """
    result = []
    for element in doc['body'].get('content', []):
        if 'paragraph' in element:
            para = element['paragraph']
            style = para.get('paragraphStyle', {}).get('namedStyleType', 'NORMAL_TEXT')
            text = ''.join(
                pe.get('textRun', {}).get('content', '')
                for pe in para.get('elements', [])
            )
            result.append({'style': style, 'text': text.rstrip('\n'), 'raw': text})
    return result


# ---------------------------------------------------------------------------
# Batch update helper
# ---------------------------------------------------------------------------

def batch_update(service, document_id: str, requests: list) -> dict:
    """Send a list of batchUpdate requests to the document."""
    return service.documents().batchUpdate(
        documentId=document_id,
        body={'requests': requests}
    ).execute()


# ---------------------------------------------------------------------------
# Inserting content
# ---------------------------------------------------------------------------

def insert_text(service, document_id: str, text: str, index: int = 1) -> dict:
    """
    Insert text at a specific index.

    Args:
        text: Text to insert. Include '\\n' for paragraph breaks.
        index: Character index (1 = beginning of document).
    """
    return batch_update(service, document_id, [{
        'insertText': {
            'location': {'index': index},
            'text': text
        }
    }])


def append_text(service, document_id: str, text: str) -> dict:
    """Append text at the end of the document."""
    doc = get_doc(service, document_id)
    end = get_end_index(doc)
    return insert_text(service, document_id, text, end)


def insert_page_break(service, document_id: str, index: int = None) -> dict:
    """Insert a page break at the given index (default: end of document)."""
    if index is None:
        doc = get_doc(service, document_id)
        index = get_end_index(doc)
    return batch_update(service, document_id, [{
        'insertPageBreak': {'location': {'index': index}}
    }])


# ---------------------------------------------------------------------------
# Template fills
# ---------------------------------------------------------------------------

def replace_text(service, document_id: str, old_text: str,
                 new_text: str, match_case: bool = True) -> dict:
    """Replace all occurrences of old_text with new_text."""
    return batch_update(service, document_id, [{
        'replaceAllText': {
            'containsText': {'text': old_text, 'matchCase': match_case},
            'replaceText': new_text
        }
    }])


def fill_template(service, document_id: str, replacements: dict,
                  placeholder_format: str = '{{{}}}') -> dict:
    """
    Replace multiple {{KEY}} placeholders with their values.

    Args:
        replacements: {'KEY': 'value', ...}
        placeholder_format: Format string for placeholder wrapping (default: '{{KEY}}')

    Example:
        fill_template(service, doc_id, {
            'CUSTOMER': 'Acme Corp',
            'DATE': '2024-01-15',
            'AMOUNT': '$1,500.00',
        })
    """
    requests = [
        {
            'replaceAllText': {
                'containsText': {
                    'text': placeholder_format.format(key),
                    'matchCase': True
                },
                'replaceText': str(value)
            }
        }
        for key, value in replacements.items()
    ]
    return batch_update(service, document_id, requests)


# ---------------------------------------------------------------------------
# Deletion
# ---------------------------------------------------------------------------

def delete_range(service, document_id: str, start: int, end: int) -> dict:
    """Delete content between start and end indices."""
    return batch_update(service, document_id, [{
        'deleteContentRange': {
            'range': {'startIndex': start, 'endIndex': end}
        }
    }])


# ---------------------------------------------------------------------------
# Styling
# ---------------------------------------------------------------------------

def apply_text_style(service, document_id: str, start: int, end: int,
                     bold: bool = None, italic: bool = None,
                     font_size_pt: float = None, font_family: str = None,
                     link_url: str = None) -> dict:
    """Apply text formatting to a range."""
    style = {}
    fields = []

    if bold is not None:
        style['bold'] = bold
        fields.append('bold')
    if italic is not None:
        style['italic'] = italic
        fields.append('italic')
    if font_size_pt is not None:
        style['fontSize'] = {'magnitude': font_size_pt, 'unit': 'PT'}
        fields.append('fontSize')
    if font_family is not None:
        style['fontFamily'] = font_family
        fields.append('fontFamily')
    if link_url is not None:
        style['link'] = {'url': link_url}
        fields.append('link')

    if not fields:
        return {}

    return batch_update(service, document_id, [{
        'updateTextStyle': {
            'range': {'startIndex': start, 'endIndex': end},
            'textStyle': style,
            'fields': ','.join(fields)
        }
    }])


def set_heading(service, document_id: str, start: int, end: int,
                level: int = 1) -> dict:
    """
    Apply a heading style to a paragraph range.

    Args:
        level: 1-6 for HEADING_1..HEADING_6, 0 for NORMAL_TEXT
    """
    style_type = f'HEADING_{level}' if level > 0 else 'NORMAL_TEXT'
    return batch_update(service, document_id, [{
        'updateParagraphStyle': {
            'range': {'startIndex': start, 'endIndex': end},
            'paragraphStyle': {'namedStyleType': style_type},
            'fields': 'namedStyleType'
        }
    }])


# ---------------------------------------------------------------------------
# Templates (copy + fill)
# ---------------------------------------------------------------------------

def create_from_template(drive_service, docs_service,
                          template_id: str, title: str,
                          replacements: dict,
                          folder_id: str = None) -> str:
    """
    Copy a template document, fill placeholders, return new document ID.

    Args:
        drive_service: Authenticated Drive service.
        docs_service: Authenticated Docs service.
        template_id: Document ID of the template.
        title: Title for the new document.
        replacements: {'PLACEHOLDER': 'value', ...}
        folder_id: Optional Drive folder ID to place the new document.

    Returns:
        New document ID.
    """
    body = {'name': title}
    if folder_id:
        body['parents'] = [folder_id]

    copy = drive_service.files().copy(fileId=template_id, body=body).execute()
    new_doc_id = copy['id']

    fill_template(docs_service, new_doc_id, replacements)

    return new_doc_id


# ---------------------------------------------------------------------------
# Example
# ---------------------------------------------------------------------------

if __name__ == '__main__':
    from auth import get_all_services

    services = get_all_services()
    docs = services['docs']
    drive = services['drive']

    # Create a new doc
    doc = create_doc(docs, 'Test Document')
    doc_id = doc['documentId']
    print(f"Created: https://docs.google.com/document/d/{doc_id}/edit")

    # Append some content
    append_text(docs, doc_id, 'Introduction\n')
    append_text(docs, doc_id, 'This is a test document created via the Docs API.\n')

    # Read it back
    doc = get_doc(docs, doc_id)
    paras = extract_paragraphs(doc)
    for p in paras:
        if p['text']:
            print(f"[{p['style']}] {p['text']}")
