# PySheetsDB

Use a Google sheet as a simple database. Built with logging in mind. 

**Destructive operations NOT supported.**

- Add row(s) to top or bottom
- Auto-add timestamp
- Fetch table data

## Usage
1. Create a Google Cloud Project at https://console.cloud.google.com
2. Create a service account at https://console.cloud.google.com/iam-admin/serviceaccounts?project=[PROJECT_NAME] We only need the email address, so actual permissions don't matter
3. Download JSON key file for service account. DO NOT STORE THIS IN A PUBLIC REPO
4. Create a Google Sheet and note the SHEET_ID in the url (longest string of letters and nums in url)
5. Add the service account email as an editor
6. Include this package in your project, or just copy ./sheets_db.py

`_db = SheetsDB([PATH_TO_KEY_JSON], [SHEET_ID])
`

We'll call the tabs at the bottom of the sheet *tables*. `Sheet1` is the first default TABLE_NAME

`
rows = [{'col 1' : 'alice', 'col 2': 'adams'},{'col 2' : 'barker', 'col 1': 'bob'}]
_db.add_rows(rows, insert_top=True)
`

will produce:

|col 1 |col 2 |UPDATED|
|------|-----|----|
|alice |adams |2023-10-16 16:01|
|bob |	barker |2023-10-16 16:01|

The "UPDATE" column will automatically be added if it's not present. You can suppress the timestamp in the DB constructor with `auto_timestamp = False`