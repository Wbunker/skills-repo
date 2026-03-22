# Google Slides API Reference

Base URL: `https://slides.googleapis.com/v1/presentations/{presentationId}`

## Table of Contents
1. [Core Concepts](#core-concepts)
2. [Create & Get Presentations](#create--get-presentations)
3. [Reading Presentations](#reading-presentations)
4. [batchUpdate Requests](#batchupdate-requests)
5. [Managing Slides](#managing-slides)
6. [Shapes & Text Boxes](#shapes--text-boxes)
7. [Text Manipulation](#text-manipulation)
8. [Images](#images)
9. [Tables](#tables)
10. [Styling](#styling)
11. [Common Patterns](#common-patterns)

---

## Core Concepts

- **Presentation ID**: Found in URL: `https://docs.google.com/presentation/d/{PRESENTATION_ID}/edit`
- **All edits via `batchUpdate`**: Every modification goes through `presentations.batchUpdate` with typed request objects.
- **Object IDs**: Every page (slide) and page element (shape, image, table, etc.) has a unique `objectId`. You can specify your own IDs when creating objects (e.g., `'SLIDE_1'`), or let the API generate them.
- **Layouts & Masters**: Slides inherit from layouts, which inherit from masters. You can specify a layout when creating a slide.
- **Indices**: Page element positions and sizes use EMU (English Metric Units): 1 inch = 914400 EMU. A standard slide is 9144000 × 5143500 EMU (10 × 5.625 inches).
- **Placeholders**: Template slides have placeholders (title, body, etc.) that you can reference by type or index.

---

## Create & Get Presentations

### Create a presentation

```python
service = build('slides', 'v1', credentials=creds)

presentation = service.presentations().create(
    body={'title': 'My Presentation'}
).execute()

presentation_id = presentation['presentationId']
print(f"Created: https://docs.google.com/presentation/d/{presentation_id}/edit")
```

### Get a presentation

```python
presentation = service.presentations().get(
    presentationId=presentation_id
).execute()

print(f"Title: {presentation['title']}")
slides = presentation.get('slides', [])
print(f"Slides: {len(slides)}")

for i, slide in enumerate(slides):
    print(f"  Slide {i+1}: objectId={slide['objectId']}")
    for element in slide.get('pageElements', []):
        print(f"    Element: {element['objectId']} ({element.get('shape', {}).get('shapeType', '?')})")
```

---

## Reading Presentations

### Extract all text from all slides

```python
def extract_all_text(presentation: dict) -> list[dict]:
    """Return list of {slide_index, element_id, text} for all text in the presentation."""
    results = []
    for i, slide in enumerate(presentation.get('slides', [])):
        for element in slide.get('pageElements', []):
            if 'shape' in element:
                text_content = element['shape'].get('text', {})
                text = ''.join(
                    tr.get('textRun', {}).get('content', '')
                    for tr in text_content.get('textElements', [])
                    if 'textRun' in tr
                )
                if text.strip():
                    results.append({
                        'slide_index': i,
                        'slide_id': slide['objectId'],
                        'element_id': element['objectId'],
                        'text': text.strip()
                    })
    return results
```

### Get slide layout info

```python
# Get available layouts
presentation = service.presentations().get(presentationId=presentation_id).execute()
for layout in presentation.get('layouts', []):
    props = layout.get('layoutProperties', {})
    print(f"Layout: {layout['objectId']} - {props.get('displayName', 'unknown')}")
```

---

## batchUpdate Requests

```python
result = service.presentations().batchUpdate(
    presentationId=presentation_id,
    body={
        'requests': [
            # ... list of request objects
        ]
    }
).execute()

# replies[i] corresponds to requests[i] (some requests return data)
replies = result.get('replies', [])
```

---

## Managing Slides

### Create a slide

```python
result = service.presentations().batchUpdate(
    presentationId=presentation_id,
    body={
        'requests': [{
            'createSlide': {
                'objectId': 'SLIDE_2',         # Optional: specify your own ID
                'insertionIndex': 1,            # 0-based position
                'slideLayoutReference': {
                    'predefinedLayout': 'TITLE_AND_BODY'
                    # Options: BLANK, CAPTION_ONLY, TITLE, TITLE_AND_BODY,
                    #          TITLE_AND_TWO_COLUMNS, TITLE_ONLY, SECTION_HEADER,
                    #          SECTION_TITLE_AND_DESCRIPTION, ONE_COLUMN_TEXT,
                    #          MAIN_POINT, BIG_NUMBER
                }
            }
        }]
    }
).execute()
new_slide_id = result['replies'][0]['createSlide']['objectId']
```

### Delete a slide

```python
service.presentations().batchUpdate(
    presentationId=presentation_id,
    body={
        'requests': [{
            'deleteObject': {'objectId': slide_id}
        }]
    }
).execute()
```

### Duplicate a slide

```python
result = service.presentations().batchUpdate(
    presentationId=presentation_id,
    body={
        'requests': [{
            'duplicateObject': {
                'objectId': source_slide_id,
                'objectIds': {
                    # Map old object IDs to new ones (optional)
                    source_slide_id: 'NEW_SLIDE_ID'
                }
            }
        }]
    }
).execute()
```

### Reorder slides

```python
service.presentations().batchUpdate(
    presentationId=presentation_id,
    body={
        'requests': [{
            'updateSlidesPosition': {
                'slideObjectIds': ['SLIDE_3', 'SLIDE_1', 'SLIDE_2'],  # New order
                'insertionIndex': 0
            }
        }]
    }
).execute()
```

---

## Shapes & Text Boxes

### Create a text box

```python
SLIDE_WIDTH  = 9144000   # 10 inches in EMU
SLIDE_HEIGHT = 5143500   # 5.625 inches in EMU

result = service.presentations().batchUpdate(
    presentationId=presentation_id,
    body={
        'requests': [{
            'createShape': {
                'objectId': 'MY_TEXT_BOX',
                'shapeType': 'TEXT_BOX',
                'elementProperties': {
                    'pageObjectId': slide_id,
                    'size': {
                        'width':  {'magnitude': 4000000, 'unit': 'EMU'},  # ~4.4 inches
                        'height': {'magnitude': 1000000, 'unit': 'EMU'},  # ~1.1 inches
                    },
                    'transform': {
                        'scaleX': 1, 'scaleY': 1,
                        'translateX': 1000000,  # ~1.1 inches from left
                        'translateY': 1000000,  # ~1.1 inches from top
                        'unit': 'EMU'
                    }
                }
            }
        }]
    }
).execute()
```

### Insert text into a shape

```python
service.presentations().batchUpdate(
    presentationId=presentation_id,
    body={
        'requests': [{
            'insertText': {
                'objectId': shape_id,
                'insertionIndex': 0,    # 0 = beginning
                'text': 'Hello, Slides!'
            }
        }]
    }
).execute()
```

### Set placeholder text (for template slides)

```python
# Get placeholder IDs first
slide = service.presentations().pages().get(
    presentationId=presentation_id,
    pageObjectId=slide_id
).execute()

for element in slide.get('pageElements', []):
    if 'shape' in element:
        placeholder = element['shape'].get('placeholder', {})
        if placeholder:
            print(f"Placeholder type: {placeholder.get('type')} id: {element['objectId']}")

# Set title placeholder
service.presentations().batchUpdate(
    presentationId=presentation_id,
    body={
        'requests': [
            {
                'deleteText': {
                    'objectId': title_placeholder_id,
                    'textRange': {'type': 'ALL'}
                }
            },
            {
                'insertText': {
                    'objectId': title_placeholder_id,
                    'insertionIndex': 0,
                    'text': 'My Slide Title'
                }
            }
        ]
    }
).execute()
```

---

## Text Manipulation

### Delete all text in a shape

```python
service.presentations().batchUpdate(
    presentationId=presentation_id,
    body={
        'requests': [{
            'deleteText': {
                'objectId': shape_id,
                'textRange': {'type': 'ALL'}
            }
        }]
    }
).execute()
```

### Replace all text in a presentation

Useful for template fills:

```python
def fill_presentation_template(service, presentation_id: str, replacements: dict):
    """Replace {{KEY}} placeholders throughout the entire presentation."""
    requests = [
        {
            'replaceAllText': {
                'containsText': {'text': f'{{{{{key}}}}}', 'matchCase': True},
                'replaceText': str(value)
            }
        }
        for key, value in replacements.items()
    ]
    service.presentations().batchUpdate(
        presentationId=presentation_id,
        body={'requests': requests}
    ).execute()

fill_presentation_template(service, presentation_id, {
    'COMPANY': 'Acme Corp',
    'QUARTER': 'Q1 2024',
    'REVENUE': '$1.2M',
})
```

---

## Images

### Create an image from a URL

```python
service.presentations().batchUpdate(
    presentationId=presentation_id,
    body={
        'requests': [{
            'createImage': {
                'objectId': 'MY_IMAGE',
                'url': 'https://example.com/logo.png',
                'elementProperties': {
                    'pageObjectId': slide_id,
                    'size': {
                        'width':  {'magnitude': 2000000, 'unit': 'EMU'},
                        'height': {'magnitude': 1000000, 'unit': 'EMU'},
                    },
                    'transform': {
                        'scaleX': 1, 'scaleY': 1,
                        'translateX': 500000,
                        'translateY': 500000,
                        'unit': 'EMU'
                    }
                }
            }
        }]
    }
).execute()
```

**Note**: Images must be publicly accessible URLs at time of insertion. For private images, upload to Drive and use the `driveImage.driveId` alternative.

---

## Tables

### Create a table

```python
result = service.presentations().batchUpdate(
    presentationId=presentation_id,
    body={
        'requests': [{
            'createTable': {
                'objectId': 'MY_TABLE',
                'rows': 4,
                'columns': 3,
                'elementProperties': {
                    'pageObjectId': slide_id,
                    'size': {
                        'width':  {'magnitude': 6000000, 'unit': 'EMU'},
                        'height': {'magnitude': 2000000, 'unit': 'EMU'},
                    },
                    'transform': {
                        'scaleX': 1, 'scaleY': 1,
                        'translateX': 1500000,
                        'translateY': 1500000,
                        'unit': 'EMU'
                    }
                }
            }
        }]
    }
).execute()

# Insert text into table cell (row 0, col 0)
service.presentations().batchUpdate(
    presentationId=presentation_id,
    body={
        'requests': [{
            'insertText': {
                'objectId': 'MY_TABLE',
                'cellLocation': {'rowIndex': 0, 'columnIndex': 0},
                'insertionIndex': 0,
                'text': 'Header 1'
            }
        }]
    }
).execute()
```

---

## Styling

### Update text style

```python
service.presentations().batchUpdate(
    presentationId=presentation_id,
    body={
        'requests': [{
            'updateTextStyle': {
                'objectId': shape_id,
                'textRange': {
                    'type': 'FIXED_RANGE',
                    'startIndex': 0,
                    'endIndex': 10
                },
                'style': {
                    'bold': True,
                    'italic': False,
                    'fontFamily': 'Arial',
                    'fontSize': {'magnitude': 24, 'unit': 'PT'},
                    'foregroundColor': {
                        'opaqueColor': {
                            'rgbColor': {'red': 0.1, 'green': 0.3, 'blue': 0.8}
                        }
                    }
                },
                'fields': 'bold,italic,fontFamily,fontSize,foregroundColor'
            }
        }]
    }
).execute()
```

### Update shape background color

```python
service.presentations().batchUpdate(
    presentationId=presentation_id,
    body={
        'requests': [{
            'updateShapeProperties': {
                'objectId': shape_id,
                'shapeProperties': {
                    'shapeBackgroundFill': {
                        'solidFill': {
                            'color': {
                                'rgbColor': {'red': 0.2, 'green': 0.4, 'blue': 0.8}
                            },
                            'alpha': 1.0
                        }
                    }
                },
                'fields': 'shapeBackgroundFill'
            }
        }]
    }
).execute()
```

### Update slide background

```python
service.presentations().batchUpdate(
    presentationId=presentation_id,
    body={
        'requests': [{
            'updatePageProperties': {
                'objectId': slide_id,
                'pageProperties': {
                    'pageBackgroundFill': {
                        'solidFill': {
                            'color': {
                                'rgbColor': {'red': 0.95, 'green': 0.95, 'blue': 0.98}
                            }
                        }
                    }
                },
                'fields': 'pageBackgroundFill'
            }
        }]
    }
).execute()
```

---

## Common Patterns

### Create a presentation from a Drive template

```python
def create_presentation_from_template(drive_service, slides_service,
                                       template_id: str, title: str,
                                       replacements: dict) -> str:
    """Copy template presentation and fill placeholders."""
    copy = drive_service.files().copy(
        fileId=template_id,
        body={'name': title}
    ).execute()
    new_id = copy['id']

    fill_presentation_template(slides_service, new_id, replacements)
    return new_id
```

### EMU conversion helpers

```python
def inches_to_emu(inches: float) -> int:
    return int(inches * 914400)

def pt_to_emu(points: float) -> int:
    return int(points * 12700)

# Standard slide dimensions
SLIDE_W = inches_to_emu(10)       # 9144000
SLIDE_H = inches_to_emu(5.625)    # 5143500

def center_element(elem_w_emu: int, elem_h_emu: int) -> dict:
    """Return transform dict to center an element on a standard slide."""
    return {
        'scaleX': 1, 'scaleY': 1,
        'translateX': (SLIDE_W - elem_w_emu) // 2,
        'translateY': (SLIDE_H - elem_h_emu) // 2,
        'unit': 'EMU'
    }
```

### Scope Reference

| Scope | Access |
|-------|--------|
| `https://www.googleapis.com/auth/presentations.readonly` | Read only |
| `https://www.googleapis.com/auth/presentations` | Full read/write |
| `https://www.googleapis.com/auth/drive` | All Drive files |
