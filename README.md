# PySheetsDB

Use a Google sheet as a simple database. Built with logging in mind. 

- Fetch table data
- Add row(s) to top or bottom
- Auto-add timestamp
- Delete rows beyond a certain count

**Most destructive operations are not supported. However, `delete_rows_beyond()` is available.**

## Example
We'll call the tabs at the bottom of the sheet *tables*. The `table_name` parameter in the `PySheetsDB` constructor specifies which sheet (tab) to use. It defaults to 'Sheet1'.

If you initialize `_db = PySheetsDB(..., table_name='myTable1')` and then run:
`
rows = [{'first name' : 'alice', 'last name': 'adams'},{'last name' : 'barker', 'first name': 'bob'}]
_db.add_rows(rows, insert_top=True)
`

will produce (assuming `auto_timestamp=True` in the constructor, which is the default):

|first name |last name |UPDATED|
|------|-----|----|
|alice |adams |2023-10-16 16:01|
|bob |	barker |2023-10-16 16:21|

The "UPDATED" column will automatically be added if it's not present. You can suppress the timestamp in the DB constructor with `auto_timestamp = False`

## Setup
Operations are done by making a service account off your Google account and giving it access to a GSheet.

1. Create a Google Cloud Project at https://console.cloud.google.com
2. Create a service account at https://console.cloud.google.com/iam-admin/serviceaccounts?project=[PROJECT_NAME] We only need the email address, so actual permissions don't matter
3. Download JSON key file for service account. DO NOT STORE THIS IN A PUBLIC REPO
4. Create a Google Sheet and note the SHEET_ID in the url (longest string of letters and nums in url)
5. In Sheets, add the service account email as an editor
6. Include this package in your project, or just copy ./sheets_db.py

### Usage
```python
from py_sheets_db import PySheetsDB

_db = PySheetsDB(
    token_file_or_key=[PATH_TO_KEY_JSON_OR_BASE64_STRING],
    sheet_id=[SHEET_ID],
    table_name='Sheet1',        # Optional: Name of the sheet (tab) to use. Defaults to 'Sheet1'.
    read_only=False,            # Optional: Set to True to open in read-only mode. Defaults to False.
    auto_timestamp=True,        # Optional: Automatically add/update 'UPDATED' column. Defaults to True.
    id_col_name=None            # Optional: Name of the column to use as a unique ID for rows.
)
```

**Read sheet**
```
print(_db.get_sheet_values()) 
# Example Output: [['1', 'alice', 'adams'], ['2', 'bob', 'barker']]

# You can also specify a range (default is 'A:Z')
print(_db.get_sheet_values(range='A1:C10'))
```

**Update rows**
```
# Add rows using a list of dictionaries. Default is to add to bottom.
# The `raw` parameter (default True) determines if values are parsed by Sheets or taken as-is.
_db.add_rows([{'col 1' : 'alice', 'col 2': 'adams'},{'col 2' : 'barker', 'col 1': 'bob'}], insert_top=True, raw=True)

# Insert blank rows. Default is 1 row at index 2 (below a header row).
_db.insert_blank_rows(num_rows=1, index=2)
```

**Update cells**
```
# The `raw` parameter (default True) determines if values are parsed by Sheets or taken as-is.
_db.set_cell_text('A5', 'Hello', raw=True)

# If you specify an id column in the constructor, you can use it to reference a row
_db.update_row_cell('PROJ-42', 'STATUS', 'complete')
```

**Set Multiple Cell Values (Range)**
```python
# Set values for a range of cells. 'texts' should be a list of lists.
# Example: [['A1_val', 'B1_val'], ['A2_val', 'B2_val']] for range 'A1:B2'
_db.set_cell_range_texts(cell_range='A10:B11', texts=[['Hello', 'World'], ['PySheetsDB', 'Rocks!']], raw=True)
```

**Delete Rows**
```
# Delete all rows after a specified maximum number of rows.
# For example, to keep only the header and 100 data rows:
_db.delete_rows_beyond(max_rows=101) 