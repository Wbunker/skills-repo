"""
Google Sheets Read/Write Script
Covers: reading ranges, writing cells, appending rows, batch operations.
"""
from typing import Optional, Any
from googleapiclient.errors import HttpError


# ---------------------------------------------------------------------------
# Reading
# ---------------------------------------------------------------------------

def get_range(service, spreadsheet_id: str, range_: str,
              value_render: str = 'FORMATTED_VALUE') -> list[list]:
    """
    Read a range of cells.

    Args:
        range_: A1 notation, e.g. 'Sheet1!A1:D10' or 'Sheet1'
        value_render: 'FORMATTED_VALUE' | 'UNFORMATTED_VALUE' | 'FORMULA'

    Returns:
        List of rows (list of lists). Empty rows and trailing empty cells are omitted.
    """
    result = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range=range_,
        valueRenderOption=value_render,
        dateTimeRenderOption='FORMATTED_STRING',
    ).execute()
    return result.get('values', [])


def get_ranges(service, spreadsheet_id: str, ranges: list[str],
               value_render: str = 'FORMATTED_VALUE') -> dict[str, list[list]]:
    """
    Read multiple ranges at once (one API call).

    Returns:
        Dict mapping range string -> rows.
    """
    result = service.spreadsheets().values().batchGet(
        spreadsheetId=spreadsheet_id,
        ranges=ranges,
        valueRenderOption=value_render,
    ).execute()
    return {
        vr['range']: vr.get('values', [])
        for vr in result.get('valueRanges', [])
    }


def get_all(service, spreadsheet_id: str, sheet_name: str = 'Sheet1') -> list[list]:
    """Read the entire contents of a sheet."""
    return get_range(service, spreadsheet_id, sheet_name)


def get_column(service, spreadsheet_id: str, column: str,
               sheet_name: str = 'Sheet1') -> list:
    """
    Read an entire column.

    Args:
        column: Column letter(s), e.g. 'A', 'B', 'AA'
    """
    rows = get_range(service, spreadsheet_id, f'{sheet_name}!{column}:{column}',
                     value_render='UNFORMATTED_VALUE')
    return [row[0] if row else '' for row in rows]


def rows_to_dicts(rows: list[list]) -> list[dict]:
    """
    Convert rows (list of lists) to list of dicts using first row as headers.

    Args:
        rows: Output from get_range() where first row is headers.

    Returns:
        List of dicts [{header: value, ...}, ...]
    """
    if not rows:
        return []
    headers = rows[0]
    result = []
    for row in rows[1:]:
        d = {}
        for i, header in enumerate(headers):
            d[header] = row[i] if i < len(row) else ''
        result.append(d)
    return result


def find_row(service, spreadsheet_id: str, search_value: Any,
             column: str = 'A', sheet_name: str = 'Sheet1') -> Optional[int]:
    """
    Find the first row index (1-based) where column matches search_value.

    Returns None if not found.
    """
    values = get_column(service, spreadsheet_id, column, sheet_name)
    for i, val in enumerate(values, start=1):
        if str(val) == str(search_value):
            return i
    return None


# ---------------------------------------------------------------------------
# Writing
# ---------------------------------------------------------------------------

def write_range(service, spreadsheet_id: str, range_: str,
                values: list[list], value_input: str = 'USER_ENTERED') -> dict:
    """
    Write values to a range.

    Args:
        range_: A1 notation starting cell, e.g. 'Sheet1!A1'
        values: List of rows (list of lists).
        value_input: 'USER_ENTERED' (interprets formulas) | 'RAW' (literal)

    Returns:
        Update response with updatedRows, updatedColumns, updatedCells.
    """
    return service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id,
        range=range_,
        valueInputOption=value_input,
        body={'values': values}
    ).execute()


def write_cell(service, spreadsheet_id: str, cell: str, value: Any,
               value_input: str = 'USER_ENTERED') -> dict:
    """Write a single cell value."""
    return write_range(service, spreadsheet_id, cell, [[value]], value_input)


def write_ranges(service, spreadsheet_id: str,
                 data: list[dict], value_input: str = 'USER_ENTERED') -> dict:
    """
    Write multiple ranges in one API call.

    Args:
        data: List of {'range': 'Sheet1!A1', 'values': [[...]]} dicts.

    Returns:
        Batch update response.
    """
    return service.spreadsheets().values().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body={
            'valueInputOption': value_input,
            'data': data
        }
    ).execute()


def dicts_to_rows(records: list[dict], headers: list[str] = None) -> list[list]:
    """
    Convert list of dicts to rows (list of lists) for writing.

    Args:
        records: List of dicts.
        headers: Column order. If None, uses keys from first record.

    Returns:
        [headers_row, row1, row2, ...]
    """
    if not records:
        return []
    if headers is None:
        headers = list(records[0].keys())
    rows = [headers]
    for record in records:
        rows.append([record.get(h, '') for h in headers])
    return rows


# ---------------------------------------------------------------------------
# Appending
# ---------------------------------------------------------------------------

def append_rows(service, spreadsheet_id: str, range_: str,
                values: list[list], value_input: str = 'USER_ENTERED') -> dict:
    """
    Append rows after the last row with data.

    Args:
        range_: Table range to detect the append location, e.g. 'Sheet1!A1'
        values: Rows to append.

    Returns:
        Response with updatedRange, updatedRows.
    """
    return service.spreadsheets().values().append(
        spreadsheetId=spreadsheet_id,
        range=range_,
        valueInputOption=value_input,
        insertDataOption='INSERT_ROWS',
        body={'values': values}
    ).execute()


def append_row(service, spreadsheet_id: str, values: list,
               sheet_name: str = 'Sheet1') -> dict:
    """Append a single row."""
    return append_rows(service, spreadsheet_id, f'{sheet_name}!A1', [values])


def append_dicts(service, spreadsheet_id: str, records: list[dict],
                 headers: list[str] = None, sheet_name: str = 'Sheet1') -> dict:
    """Append a list of dicts as rows (skips the header row)."""
    if not records:
        return {}
    if headers is None:
        headers = list(records[0].keys())
    rows = [[record.get(h, '') for h in headers] for record in records]
    return append_rows(service, spreadsheet_id, f'{sheet_name}!A1', rows)


# ---------------------------------------------------------------------------
# Clearing
# ---------------------------------------------------------------------------

def clear_range(service, spreadsheet_id: str, range_: str) -> dict:
    """Clear values in a range (keeps formatting)."""
    return service.spreadsheets().values().clear(
        spreadsheetId=spreadsheet_id,
        range=range_,
        body={}
    ).execute()


def clear_ranges(service, spreadsheet_id: str, ranges: list[str]) -> dict:
    """Clear multiple ranges at once."""
    return service.spreadsheets().values().batchClear(
        spreadsheetId=spreadsheet_id,
        body={'ranges': ranges}
    ).execute()


# ---------------------------------------------------------------------------
# Spreadsheet management
# ---------------------------------------------------------------------------

def create_spreadsheet(service, title: str,
                        sheet_names: list[str] = None) -> dict:
    """
    Create a new spreadsheet.

    Returns:
        Spreadsheet resource with spreadsheetId and spreadsheetUrl.
    """
    body = {'properties': {'title': title}}
    if sheet_names:
        body['sheets'] = [{'properties': {'title': name}} for name in sheet_names]

    return service.spreadsheets().create(
        body=body,
        fields='spreadsheetId,spreadsheetUrl,sheets.properties'
    ).execute()


def get_sheet_id(service, spreadsheet_id: str, sheet_name: str) -> Optional[int]:
    """Look up a sheet's integer ID by name."""
    spreadsheet = service.spreadsheets().get(
        spreadsheetId=spreadsheet_id,
        fields='sheets.properties'
    ).execute()
    for sheet in spreadsheet.get('sheets', []):
        if sheet['properties']['title'] == sheet_name:
            return sheet['properties']['sheetId']
    return None


def add_sheet(service, spreadsheet_id: str, title: str,
              tab_color: dict = None) -> int:
    """
    Add a new sheet tab.

    Args:
        tab_color: {'red': 0.0, 'green': 0.8, 'blue': 0.0} (0.0-1.0)

    Returns:
        New sheet's sheetId.
    """
    props = {'title': title}
    if tab_color:
        props['tabColor'] = tab_color

    result = service.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body={'requests': [{'addSheet': {'properties': props}}]}
    ).execute()
    return result['replies'][0]['addSheet']['properties']['sheetId']


def delete_sheet(service, spreadsheet_id: str, sheet_id: int):
    """Delete a sheet by its integer ID."""
    service.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body={'requests': [{'deleteSheet': {'sheetId': sheet_id}}]}
    ).execute()


def freeze_header_row(service, spreadsheet_id: str, sheet_id: int,
                       frozen_rows: int = 1):
    """Freeze the top N rows (typically the header)."""
    service.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body={
            'requests': [{
                'updateSheetProperties': {
                    'properties': {
                        'sheetId': sheet_id,
                        'gridProperties': {'frozenRowCount': frozen_rows}
                    },
                    'fields': 'gridProperties.frozenRowCount'
                }
            }]
        }
    ).execute()


def bold_header_row(service, spreadsheet_id: str, sheet_id: int,
                     num_columns: int, row_index: int = 0):
    """Bold the header row."""
    service.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body={
            'requests': [{
                'repeatCell': {
                    'range': {
                        'sheetId': sheet_id,
                        'startRowIndex': row_index,
                        'endRowIndex': row_index + 1,
                        'startColumnIndex': 0,
                        'endColumnIndex': num_columns
                    },
                    'cell': {
                        'userEnteredFormat': {
                            'textFormat': {'bold': True}
                        }
                    },
                    'fields': 'userEnteredFormat.textFormat.bold'
                }
            }]
        }
    ).execute()


# ---------------------------------------------------------------------------
# Example
# ---------------------------------------------------------------------------

if __name__ == '__main__':
    from auth import get_service

    sheets = get_service('sheets', 'v4',
                         scopes=['https://www.googleapis.com/auth/spreadsheets'])

    # Create a spreadsheet
    spreadsheet = create_spreadsheet(sheets, 'Test Spreadsheet', ['Data', 'Summary'])
    sid = spreadsheet['spreadsheetId']
    print(f"Created: {spreadsheet['spreadsheetUrl']}")

    # Write a header + data
    write_range(sheets, sid, 'Data!A1', [
        ['Name', 'Score', 'Grade'],
        ['Alice', 95, 'A'],
        ['Bob', 82, 'B'],
        ['Charlie', 91, 'A'],
    ])

    # Read it back as dicts
    rows = get_range(sheets, sid, 'Data!A1:C10')
    records = rows_to_dicts(rows)
    for r in records:
        print(r)

    # Append a new row
    append_row(sheets, sid, ['Diana', 88, 'B'], sheet_name='Data')
    print("Appended new row.")
