# Excel Online API (Microsoft Graph)

Read and modify Excel workbooks stored in OneDrive for Business or SharePoint
document libraries via the Microsoft Graph Excel REST API.

## Permissions

| Scenario | Delegated | Application |
|----------|-----------|-------------|
| Read workbooks | `Files.Read` | `Files.Read.All` |
| Read + write workbooks | `Files.ReadWrite` | `Files.ReadWrite.All` |

Excel API piggybacks on Files permissions — there are no separate "Excel" scopes.

## Limitations

- Only `.xlsx` files (Office Open XML format) — `.xls` is NOT supported
- Files must be in OneDrive for Business or SharePoint (not personal OneDrive consumer)
- The workbook must not be open for editing by the user in Excel desktop (can cause conflicts)

## Base URL Pattern

All Excel API calls start by locating the file in OneDrive, then appending `/workbook/`:

```
# By item ID
https://graph.microsoft.com/v1.0/me/drive/items/{item-id}/workbook/

# By path
https://graph.microsoft.com/v1.0/me/drive/root:/{path-to-file}:/workbook/
```

## Sessions

Sessions improve performance and consistency for multiple operations on the same workbook.

```python
import httpx

async def create_workbook_session(token, item_id, persist=True):
    """
    persist=True: Changes saved to file
    persist=False: Changes in-memory only (analysis/read scenarios)
    """
    url = f"https://graph.microsoft.com/v1.0/me/drive/items/{item_id}/workbook/createSession"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    payload = {"persistChanges": persist}

    async with httpx.AsyncClient() as client:
        r = await client.post(url, json=payload, headers=headers)
        r.raise_for_status()
        return r.json()["id"]  # session ID

# Use session ID in subsequent requests:
# headers["workbook-session-id"] = session_id
```

**Sessions expire** after ~5 minutes of inactivity (persistent) or ~7 minutes (non-persistent).
Refresh with:
```
POST /me/drive/items/{item-id}/workbook/refreshSession
workbook-session-id: {session-id}
```

## Worksheets

### List Worksheets

```python
import httpx

async def list_worksheets(token, item_id, session_id=None):
    url = f"https://graph.microsoft.com/v1.0/me/drive/items/{item_id}/workbook/worksheets"
    headers = {"Authorization": f"Bearer {token}"}
    if session_id:
        headers["workbook-session-id"] = session_id

    async with httpx.AsyncClient() as client:
        r = await client.get(url, headers=headers)
        r.raise_for_status()
        return r.json()["value"]
        # Each worksheet: {"id": "...", "name": "Sheet1", "position": 0, "visibility": "Visible"}
```

### Get a Worksheet by Name

```
GET /me/drive/items/{item-id}/workbook/worksheets/{worksheet-name-or-id}
```

### Add a Worksheet

```python
async def add_worksheet(token, item_id, name, session_id=None):
    url = f"https://graph.microsoft.com/v1.0/me/drive/items/{item_id}/workbook/worksheets"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    if session_id:
        headers["workbook-session-id"] = session_id

    async with httpx.AsyncClient() as client:
        r = await client.post(url, json={"name": name}, headers=headers)
        r.raise_for_status()
        return r.json()
```

### Delete a Worksheet

```
DELETE /me/drive/items/{item-id}/workbook/worksheets/{worksheet-id}
```

## Reading Cell Data (Ranges)

### Read a Range

```python
async def read_range(token, item_id, worksheet_name, address, session_id=None):
    """
    address: Excel-style range like 'A1:C10' or 'A1'
    """
    url = (
        f"https://graph.microsoft.com/v1.0/me/drive/items/{item_id}"
        f"/workbook/worksheets/{worksheet_name}/range(address='{address}')"
    )
    headers = {"Authorization": f"Bearer {token}"}
    if session_id:
        headers["workbook-session-id"] = session_id

    async with httpx.AsyncClient() as client:
        r = await client.get(url, headers=headers)
        r.raise_for_status()
        data = r.json()
        return data["values"]  # 2D array: [[row1col1, row1col2], [row2col1, ...]]
```

Response includes:
- `values`: 2D array of cell values
- `text`: 2D array of displayed text (formatted values)
- `formulas`: 2D array of formulas
- `numberFormat`: 2D array of format strings
- `address`: Absolute address (e.g., `Sheet1!A1:C10`)
- `rowCount`, `columnCount`

### Read Used Range

```
GET /me/drive/items/{item-id}/workbook/worksheets/{name}/usedRange
```

Returns the range containing all non-empty cells.

## Writing Cell Data

### Write to a Range (PATCH)

```python
async def write_range(token, item_id, worksheet_name, address, values, session_id=None):
    """
    values: 2D array matching the range dimensions
    [[row1col1, row1col2], [row2col1, row2col2]]
    """
    url = (
        f"https://graph.microsoft.com/v1.0/me/drive/items/{item_id}"
        f"/workbook/worksheets/{worksheet_name}/range(address='{address}')"
    )
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    if session_id:
        headers["workbook-session-id"] = session_id

    async with httpx.AsyncClient() as client:
        r = await client.patch(url, json={"values": values}, headers=headers)
        r.raise_for_status()
        return r.json()
```

### Write Formulas

```python
# Write formulas instead of values
payload = {
    "formulas": [["=A1+B1", "=SUM(A1:A10)"], ["=AVERAGE(B1:B5)", ""]]
}
# PATCH same URL as above with "formulas" key instead of "values"
```

### Write a Single Value to Entire Range (Broadcast)

If you send a single cell value for a multi-cell range, it fills all cells:
```python
payload = {"values": "Sample text"}  # Fills all cells in the range with "Sample text"
```

### Clear a Range

```
POST /me/drive/items/{item-id}/workbook/worksheets/{name}/range(address='A1:B10')/clear
Body: {"applyTo": "Contents"}  # or "Formats", "All"
```

## Tables

### List Tables

```
GET /me/drive/items/{item-id}/workbook/worksheets/{name}/tables
GET /me/drive/items/{item-id}/workbook/tables
```

### Create a Table

```python
async def create_table(token, item_id, worksheet_name, address, has_headers=True, session_id=None):
    url = f"https://graph.microsoft.com/v1.0/me/drive/items/{item_id}/workbook/worksheets/{worksheet_name}/tables/add"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    if session_id:
        headers["workbook-session-id"] = session_id

    payload = {"address": address, "hasHeaders": has_headers}

    async with httpx.AsyncClient() as client:
        r = await client.post(url, json=payload, headers=headers)
        r.raise_for_status()
        return r.json()
```

### Get Table Rows

```
GET /me/drive/items/{item-id}/workbook/tables/{table-id}/rows
```

Response: `{"value": [{"index": 0, "values": [[val1, val2, ...]]}, ...]}`

### Add a Row to a Table

```python
async def add_table_row(token, item_id, table_id, values, index=None, session_id=None):
    url = f"https://graph.microsoft.com/v1.0/me/drive/items/{item_id}/workbook/tables/{table_id}/rows"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    if session_id:
        headers["workbook-session-id"] = session_id

    payload = {"values": [values], "index": index}  # index=None appends at end

    async with httpx.AsyncClient() as client:
        r = await client.post(url, json=payload, headers=headers)
        r.raise_for_status()
        return r.json()
```

### Sort a Table

```
POST /me/drive/items/{item-id}/workbook/worksheets/{name}/tables/{table-id}/sort/apply
Body: {"fields": [{"key": 0, "ascending": true}]}
# key = column index (0-based)
```

### Filter a Table Column

```
POST /me/drive/items/{item-id}/workbook/worksheets/{name}/tables/{table-id}/columns/{col-id}/filter/apply
Body: {
    "criteria": {
        "filterOn": "custom",
        "criterion1": ">100",
        "operator": "and",
        "criterion2": "<500"
    }
}
```

### Clear a Table Filter

```
POST /me/drive/items/{item-id}/workbook/worksheets/{name}/tables/{table-id}/columns/{col-id}/filter/clear
```

## Charts

### List Charts

```
GET /me/drive/items/{item-id}/workbook/worksheets/{name}/charts
```

### Add a Chart

```python
async def add_chart(token, item_id, worksheet_name, chart_type, source_data, series_by="Auto", session_id=None):
    """
    chart_type: 'ColumnClustered', 'Bar', 'Line', 'Pie', 'XY', 'Area', etc.
    source_data: range address like 'A1:C10'
    """
    url = f"https://graph.microsoft.com/v1.0/me/drive/items/{item_id}/workbook/worksheets/{worksheet_name}/charts/Add"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    if session_id:
        headers["workbook-session-id"] = session_id

    payload = {"type": chart_type, "sourceData": source_data, "seriesBy": series_by}

    async with httpx.AsyncClient() as client:
        r = await client.post(url, json=payload, headers=headers)
        r.raise_for_status()
        return r.json()
```

### Get Chart as Image

```
GET /me/drive/items/{item-id}/workbook/worksheets/{name}/charts/{chart-id}/Image(width=800,height=600,fittingMode='fit')
```

Returns base64-encoded PNG string in `{"value": "base64string"}`.

## Built-in Functions

Call Excel functions server-side:

```python
async def call_excel_function(token, item_id, function_name, params, session_id=None):
    url = f"https://graph.microsoft.com/v1.0/me/drive/items/{item_id}/workbook/functions/{function_name}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    if session_id:
        headers["workbook-session-id"] = session_id

    async with httpx.AsyncClient() as client:
        r = await client.post(url, json=params, headers=headers)
        r.raise_for_status()
        return r.json()["value"]

# Examples:
# PMT: await call_excel_function(token, item_id, "pmt", {"rate": 0.05, "nper": 12, "pv": -10000})
# VLookup, Sum, Average, etc.
```

## Named Ranges

```
GET /me/drive/items/{item-id}/workbook/names
```

Returns named ranges/constants:
```json
{"value": [{"name": "TaxRate", "type": "Range", "value": "Sheet1!$B$2", "visible": true}]}
```

## Null and Empty Values

- Send `null` in a 2D array position to skip that cell (leave existing value)
- Send `""` (empty string) to clear a cell's value
- Reading empty cells returns `""`

## Tips

- **Use sessions** for multiple operations — significantly reduces latency
- **Batch reads** — read large ranges at once rather than cell by cell
- **`$select`** on worksheet list: `?$select=id,name,position`
- Excel API requires the workbook to be accessible in OneDrive for Business
- For large datasets, consider reading in chunks (row ranges like A1:Z1000, then A1001:Z2000)
- The `/usedRange` endpoint is efficient for getting the extent of data without knowing the exact bounds
