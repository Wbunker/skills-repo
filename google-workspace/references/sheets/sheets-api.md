# Google Sheets API Reference

Base URL: `https://sheets.googleapis.com/v4/spreadsheets/{spreadsheetId}`

## Table of Contents
1. [Core Concepts](#core-concepts)
2. [Create & Get Spreadsheets](#create--get-spreadsheets)
3. [Reading Cell Data](#reading-cell-data)
4. [Writing Cell Data](#writing-cell-data)
5. [Appending Rows](#appending-rows)
6. [Clearing Cells](#clearing-cells)
7. [Structural Changes (batchUpdate)](#structural-changes-batchupdate)
8. [Formatting](#formatting)
9. [Named Ranges](#named-ranges)
10. [Scope Reference](#scope-reference)

---

## Core Concepts

- **Spreadsheet ID**: Found in the URL: `https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/edit`
- **Sheet ID** (`sheetId`): Integer identifier for a tab within the spreadsheet
- **A1 Notation**: Range format like `Sheet1!A1:C10`, `A:A`, `1:3`, `Sheet1!A1`
  - Sheet name optional if targeting the first sheet
  - Quotes required for sheet names with spaces: `'My Sheet'!A1:B10`
- **Two sub-APIs**:
  - `spreadsheets.values.*` — read/write cell data (fast, simple)
  - `spreadsheets.batchUpdate` — structural changes: formatting, sheet management, charts
- **ValueInputOption**: How input is interpreted
  - `'USER_ENTERED'` — like typing in the UI (interprets formulas, dates)
  - `'RAW'` — literal values (strings stay as strings, no formula parsing)
- **ValueRenderOption**: How output is returned
  - `'FORMATTED_VALUE'` — as displayed in the UI (default)
  - `'UNFORMATTED_VALUE'` — raw value before formatting
  - `'FORMULA'` — returns formula strings

---

## Create & Get Spreadsheets

### Create a spreadsheet

```python
service = build('sheets', 'v4', credentials=creds)

spreadsheet = service.spreadsheets().create(
    body={
        'properties': {'title': 'My New Spreadsheet'},
        'sheets': [
            {'properties': {'title': 'Sheet1'}},
            {'properties': {'title': 'Data'}},
        ]
    },
    fields='spreadsheetId,spreadsheetUrl,sheets.properties'
).execute()

spreadsheet_id = spreadsheet['spreadsheetId']
print(f"Created: {spreadsheet['spreadsheetUrl']}")
```

### Get spreadsheet metadata

```python
# Get full spreadsheet metadata (sheets, named ranges, etc.)
spreadsheet = service.spreadsheets().get(
    spreadsheetId=spreadsheet_id,
    includeGridData=False  # True to include cell data (expensive)
).execute()

sheets = spreadsheet.get('sheets', [])
for sheet in sheets:
    props = sheet['properties']
    print(f"{props['title']} (id={props['sheetId']}, rows={props['gridProperties']['rowCount']})")
```

---

## Reading Cell Data

### Get a range

```python
result = service.spreadsheets().values().get(
    spreadsheetId=spreadsheet_id,
    range='Sheet1!A1:D10',
    valueRenderOption='FORMATTED_VALUE',  # 'UNFORMATTED_VALUE' | 'FORMULA'
    dateTimeRenderOption='FORMATTED_STRING',  # 'SERIAL_NUMBER'
).execute()

values = result.get('values', [])  # List of rows; short rows omit trailing empty cells
for row in values:
    print(row)
```

### Batch get multiple ranges

```python
result = service.spreadsheets().values().batchGet(
    spreadsheetId=spreadsheet_id,
    ranges=['Sheet1!A1:B5', 'Data!C1:C100', 'Sheet1!E1:E1'],
    valueRenderOption='UNFORMATTED_VALUE',
).execute()

for value_range in result.get('valueRanges', []):
    print(f"Range: {value_range['range']}")
    print(f"Values: {value_range.get('values', [])}")
```

### Read entire sheet

```python
result = service.spreadsheets().values().get(
    spreadsheetId=spreadsheet_id,
    range='Sheet1',  # No cell range = entire sheet
).execute()
```

### Handling sparse data

```python
values = result.get('values', [])

# Rows with no data are omitted; short rows skip trailing empty cells
# Safe access:
for i, row in enumerate(values):
    col_a = row[0] if len(row) > 0 else ''
    col_b = row[1] if len(row) > 1 else ''
    col_c = row[2] if len(row) > 2 else ''
```

---

## Writing Cell Data

### Update a range

```python
result = service.spreadsheets().values().update(
    spreadsheetId=spreadsheet_id,
    range='Sheet1!A1',
    valueInputOption='USER_ENTERED',  # 'RAW' for literal values
    body={
        'values': [
            ['Name', 'Score', 'Grade'],      # Row 1
            ['Alice', 95, '=IF(B2>=90,"A","B")'],  # Row 2
            ['Bob', 78, '=IF(B3>=90,"A","B")'],    # Row 3
        ]
    }
).execute()

print(f"Updated {result['updatedCells']} cells")
```

### Batch update multiple ranges

```python
result = service.spreadsheets().values().batchUpdate(
    spreadsheetId=spreadsheet_id,
    body={
        'valueInputOption': 'USER_ENTERED',
        'data': [
            {
                'range': 'Sheet1!A1:C1',
                'values': [['Header 1', 'Header 2', 'Header 3']]
            },
            {
                'range': 'Data!A1',
                'values': [['Updated at'], ['=NOW()']]
            },
        ]
    }
).execute()

print(f"Updated {result['totalUpdatedCells']} cells across {result['totalUpdatedSheets']} sheets")
```

### Write a single cell

```python
service.spreadsheets().values().update(
    spreadsheetId=spreadsheet_id,
    range='Sheet1!B2',
    valueInputOption='USER_ENTERED',
    body={'values': [['Hello']]}
).execute()
```

---

## Appending Rows

Append adds data after the last row with data in the specified range:

```python
result = service.spreadsheets().values().append(
    spreadsheetId=spreadsheet_id,
    range='Sheet1!A1',            # Finds the table starting here
    valueInputOption='USER_ENTERED',
    insertDataOption='INSERT_ROWS',  # 'OVERWRITE' to overwrite existing cells
    body={
        'values': [
            ['2024-01-15', 'Alice', 100],
            ['2024-01-15', 'Bob', 95],
        ]
    }
).execute()

updates = result.get('updates', {})
print(f"Appended to range: {updates.get('updatedRange')}")
print(f"Appended {updates.get('updatedRows')} rows")
```

---

## Clearing Cells

```python
# Clear a range (removes values, keeps formatting)
service.spreadsheets().values().clear(
    spreadsheetId=spreadsheet_id,
    range='Sheet1!A2:Z1000',
    body={}
).execute()

# Batch clear multiple ranges
service.spreadsheets().values().batchClear(
    spreadsheetId=spreadsheet_id,
    body={'ranges': ['Sheet1!A2:Z100', 'Data!A1:Z1000']}
).execute()
```

---

## Structural Changes (batchUpdate)

Structural changes (add/delete sheets, formatting, charts, merges, etc.)
all go through `spreadsheets.batchUpdate`. Multiple requests can be sent in one call.

```python
result = service.spreadsheets().batchUpdate(
    spreadsheetId=spreadsheet_id,
    body={
        'requests': [
            # ... list of request objects
        ]
    }
).execute()
```

### Add a sheet

```python
result = service.spreadsheets().batchUpdate(
    spreadsheetId=spreadsheet_id,
    body={
        'requests': [{
            'addSheet': {
                'properties': {
                    'title': 'New Tab',
                    'gridProperties': {'rowCount': 1000, 'columnCount': 26},
                    'tabColor': {'red': 0.0, 'green': 0.8, 'blue': 0.0}
                }
            }
        }]
    }
).execute()

new_sheet_id = result['replies'][0]['addSheet']['properties']['sheetId']
```

### Delete a sheet

```python
service.spreadsheets().batchUpdate(
    spreadsheetId=spreadsheet_id,
    body={'requests': [{'deleteSheet': {'sheetId': sheet_id}}]}
).execute()
```

### Duplicate a sheet

```python
result = service.spreadsheets().batchUpdate(
    spreadsheetId=spreadsheet_id,
    body={
        'requests': [{
            'duplicateSheet': {
                'sourceSheetId': source_sheet_id,
                'insertSheetIndex': 2,        # Position (0-indexed)
                'newSheetName': 'Copy of Sheet1'
            }
        }]
    }
).execute()
new_id = result['replies'][0]['duplicateSheet']['properties']['sheetId']
```

### Rename a sheet

```python
service.spreadsheets().batchUpdate(
    spreadsheetId=spreadsheet_id,
    body={
        'requests': [{
            'updateSheetProperties': {
                'properties': {
                    'sheetId': sheet_id,
                    'title': 'Renamed Sheet'
                },
                'fields': 'title'
            }
        }]
    }
).execute()
```

### Resize columns / rows

```python
service.spreadsheets().batchUpdate(
    spreadsheetId=spreadsheet_id,
    body={
        'requests': [
            # Auto-resize column A (index 0)
            {
                'autoResizeDimensions': {
                    'dimensions': {
                        'sheetId': sheet_id,
                        'dimension': 'COLUMNS',
                        'startIndex': 0,
                        'endIndex': 1
                    }
                }
            },
            # Set row height for rows 1-10
            {
                'updateDimensionProperties': {
                    'range': {
                        'sheetId': sheet_id,
                        'dimension': 'ROWS',
                        'startIndex': 0,
                        'endIndex': 10
                    },
                    'properties': {'pixelSize': 30},
                    'fields': 'pixelSize'
                }
            }
        ]
    }
).execute()
```

### Freeze rows/columns

```python
service.spreadsheets().batchUpdate(
    spreadsheetId=spreadsheet_id,
    body={
        'requests': [{
            'updateSheetProperties': {
                'properties': {
                    'sheetId': sheet_id,
                    'gridProperties': {
                        'frozenRowCount': 1,     # Freeze header row
                        'frozenColumnCount': 0
                    }
                },
                'fields': 'gridProperties.frozenRowCount,gridProperties.frozenColumnCount'
            }
        }]
    }
).execute()
```

### Insert / delete rows or columns

```python
service.spreadsheets().batchUpdate(
    spreadsheetId=spreadsheet_id,
    body={
        'requests': [
            # Insert 3 rows after row 5 (0-indexed: after index 4)
            {
                'insertDimension': {
                    'range': {
                        'sheetId': sheet_id,
                        'dimension': 'ROWS',
                        'startIndex': 5,
                        'endIndex': 8      # inserts 3 rows (8-5)
                    },
                    'inheritFromBefore': True
                }
            },
            # Delete rows 2-4 (0-indexed)
            {
                'deleteDimension': {
                    'range': {
                        'sheetId': sheet_id,
                        'dimension': 'ROWS',
                        'startIndex': 1,
                        'endIndex': 4
                    }
                }
            }
        ]
    }
).execute()
```

---

## Formatting

### repeatCell — apply format to a range

```python
def make_cell_format(
    bold=False, italic=False, font_size=None, font_family=None,
    fg_color=None, bg_color=None, h_align=None, number_format=None
) -> dict:
    """Build a CellFormat dict for use in repeatCell or updateCells."""
    fmt = {}
    text_fmt = {}
    if bold:
        text_fmt['bold'] = True
    if italic:
        text_fmt['italic'] = True
    if font_size:
        text_fmt['fontSize'] = font_size
    if font_family:
        text_fmt['fontFamily'] = font_family
    if fg_color:
        text_fmt['foregroundColor'] = fg_color  # {red, green, blue} 0.0-1.0
    if text_fmt:
        fmt['textFormat'] = text_fmt
    if bg_color:
        fmt['backgroundColor'] = bg_color
    if h_align:
        fmt['horizontalAlignment'] = h_align  # 'LEFT' | 'CENTER' | 'RIGHT'
    if number_format:
        fmt['numberFormat'] = number_format  # {'type': 'NUMBER', 'pattern': '#,##0.00'}
    return fmt


# Bold + centered header row
service.spreadsheets().batchUpdate(
    spreadsheetId=spreadsheet_id,
    body={
        'requests': [{
            'repeatCell': {
                'range': {
                    'sheetId': sheet_id,
                    'startRowIndex': 0, 'endRowIndex': 1,   # Row 1
                    'startColumnIndex': 0, 'endColumnIndex': 5  # Columns A-E
                },
                'cell': {
                    'userEnteredFormat': make_cell_format(
                        bold=True, font_size=12,
                        bg_color={'red': 0.2, 'green': 0.4, 'blue': 0.8},
                        fg_color={'red': 1.0, 'green': 1.0, 'blue': 1.0},
                        h_align='CENTER'
                    )
                },
                'fields': 'userEnteredFormat(textFormat,backgroundColor,horizontalAlignment)'
            }
        }]
    }
).execute()
```

### Merge cells

```python
service.spreadsheets().batchUpdate(
    spreadsheetId=spreadsheet_id,
    body={
        'requests': [{
            'mergeCells': {
                'range': {
                    'sheetId': sheet_id,
                    'startRowIndex': 0, 'endRowIndex': 1,
                    'startColumnIndex': 0, 'endColumnIndex': 4
                },
                'mergeType': 'MERGE_ALL'  # 'MERGE_COLUMNS' | 'MERGE_ROWS'
            }
        }]
    }
).execute()
```

### Number formats

```python
NUMBER_FORMATS = {
    'currency':    {'type': 'CURRENCY',    'pattern': '"$"#,##0.00'},
    'percentage':  {'type': 'PERCENT',     'pattern': '0.00%'},
    'date':        {'type': 'DATE',        'pattern': 'yyyy-mm-dd'},
    'datetime':    {'type': 'DATE_TIME',   'pattern': 'yyyy-mm-dd hh:mm'},
    'integer':     {'type': 'NUMBER',      'pattern': '#,##0'},
    'decimal':     {'type': 'NUMBER',      'pattern': '#,##0.00'},
}
```

---

## Named Ranges

```python
# Add a named range
result = service.spreadsheets().batchUpdate(
    spreadsheetId=spreadsheet_id,
    body={
        'requests': [{
            'addNamedRange': {
                'namedRange': {
                    'name': 'SalesData',
                    'range': {
                        'sheetId': sheet_id,
                        'startRowIndex': 1, 'endRowIndex': 101,
                        'startColumnIndex': 0, 'endColumnIndex': 4
                    }
                }
            }
        }]
    }
).execute()
named_range_id = result['replies'][0]['addNamedRange']['namedRange']['namedRangeId']

# Read using named range
result = service.spreadsheets().values().get(
    spreadsheetId=spreadsheet_id,
    range='SalesData'
).execute()

# List all named ranges
spreadsheet = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
for nr in spreadsheet.get('namedRanges', []):
    print(f"{nr['name']}: {nr['range']}")
```

---

## Scope Reference

| Scope | Access |
|-------|--------|
| `https://www.googleapis.com/auth/spreadsheets.readonly` | Read-only |
| `https://www.googleapis.com/auth/spreadsheets` | Full read/write |
| `https://www.googleapis.com/auth/drive` | All Drive files (broader) |
| `https://www.googleapis.com/auth/drive.readonly` | Read all Drive files |
| `https://www.googleapis.com/auth/drive.file` | Only files app created/opened |
