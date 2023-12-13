# PySheetsDB

Use a Google sheet as a simple database. Built with logging in mind. 

- Fetch table data
- Add row(s) to top or bottom
- Auto-add timestamp

**Destructive operations not supported.**

## Example
We'll call the tabs at the bottom of the sheet *tables*. `Sheet1` is the first default TABLE_NAME

`
rows = [{'first name' : 'alice', 'last name': 'adams'},{'last name' : 'barker', 'first name': 'bob'}]
_db.add_rows(rows, table_name='myTable1', insert_top=True)
`

will produce:

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
```
from py_sheets_db import PySheetsDB
_db = PySheetsDB([PATH_TO_KEY_JSON], [SHEET_ID])
```

**Read sheet**
```
print(_db.get_sheet_values())
```

**Update rows**
```
_db.add_rows(6, [['new', 'gnu'],['moar','more']])

_db.add_rows([{'col 1' : 'alice', 'col 2': 'adams'},{'col 2' : 'barker', 'col 1': 'bob'}], insert_top=True)

_db.insert_blank_row()
```

**Update cells**
```
_db.set_cell_text('A5', 'Hello')

# If you specify an id column in the constructor, you can use it to reference a row
_db = PySheetsDB([PATH_TO_KEY_JSON], [SHEET_ID], id_col_name='id')
_db.update_row_cell('PROJ-42', 'STATUS', 'complete')
```