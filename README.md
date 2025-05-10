# PySheetsDB

Use a Google sheet as a simple database. Built with logging in mind.

## Features

- Fetch table data
- Add row(s) to top or bottom
- Auto-add timestamp column (`UPDATED`)
- Delete rows beyond a certain count

## Prerequisites

To use PySheetsDB, you need to set up a Google Cloud Project and a Service Account with access to your target Google Sheet.

1.  **Create/Select a Google Cloud Project:** Go to the [Google Cloud Console](https://console.cloud.google.com).
2.  **Enable Google Sheets API:** In your Google Cloud Project, ensure the [Google Sheets API](https://console.developers.google.com/apis/library/sheets.googleapis.com) is enabled.
3.  **Create a Service Account:**
    *   Navigate to `IAM & Admin` > `Service Accounts` in your project.
    *   Click `+ CREATE SERVICE ACCOUNT`.
    *   Give it a name (e.g., `pysheetsdb-user`). Granting specific roles at this stage is not strictly necessary for PySheetsDB if you manage sheet access directly, but you might grant `Editor` to the project if preferred.
    *   Click `DONE`.
4.  **Generate a Key:**
    *   Find your newly created service account, click the three dots (Actions) next to it, and select `Manage keys`.
    *   Click `ADD KEY` > `Create new key`.
    *   Choose `JSON` as the key type and click `CREATE`. A JSON key file will be downloaded.
    *   **Important:** Keep this JSON file secure. Do not commit it to public repositories. You can either use the path to this file or its base64 encoded content when initializing `PySheetsDB`.
5.  **Share your Google Sheet:**
    *   Open the Google Sheet you want to use.
    *   Click the `Share` button.
    *   Add the email address of the service account you created (e.g., `pysheetsdb-user@<your-project-id>.iam.gserviceaccount.com`) as an `Editor`.
6.  **Note your Sheet ID:** The `SHEET_ID` is a long string of letters and numbers in the URL of your Google Sheet (e.g., `https://docs.google.com/spreadsheets/d/SHEET_ID_IS_HERE/edit#gid=0`).

## Installation

1.  **Clone the repository or copy the script:**
    *   You can clone this repository: `git clone https://github.com/briandherbert/PySheetsDB.git`
    *   Alternatively, just copy the `py_sheets_db.py` file into your project.
2.  **Set up a virtual environment (recommended):**
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate  # On Windows: .venv\Scripts\activate
    ```
3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
    This will install `google-api-python-client` and `python-dotenv`.
4.  **Environment Variables:**
    *   Create a `.env` file in your project root:
        ```
        SHEETS_KEY="your_base64_encoded_service_account_key_or_path_to_json_file"
        SHEET_ID="your_google_sheet_id"
        ```
    *   Ensure `.env` is in your `.gitignore` file.

## Quick Start Example

This example demonstrates adding rows to a sheet named `myTable1`.

```python
from py_sheets_db import PySheetsDB
import os
from dotenv import load_dotenv

load_dotenv()

sheets_key = os.getenv("SHEETS_KEY")
sheet_id = os.getenv("SHEET_ID")

# Initialize with table_name='myTable1' and auto_timestamp=True
_db = PySheetsDB(token_file_or_key=sheets_key, sheet_id=sheet_id, table_name='myTable1', auto_timestamp=True)

rows_to_add = [
    {'first name': 'alice', 'last name': 'adams'},
    {'last name': 'barker', 'first name': 'bob'}
]
_db.add_rows(rows_to_add, insert_top=True)
```

This will produce the following in your 'myTable1' sheet (assuming `auto_timestamp=True`):

| first name | last name | UPDATED           |
|------------|-----------|-------------------|
| alice      | adams     | YYYY-MM-DD HH:MM  |
| bob        | barker    | YYYY-MM-DD HH:MM  |

*The `UPDATED` column is automatically added if not present when `auto_timestamp=True`.*

## Usage

### Initializing `PySheetsDB`

Import the class and initialize it with your credentials and sheet details:

```python
from py_sheets_db import PySheetsDB

_db = PySheetsDB(
    token_file_or_key=[PATH_TO_KEY_JSON_OR_BASE64_STRING], # Path to your service account JSON key file or its base64 encoded content
    sheet_id=[SHEET_ID],                            # The ID of your Google Sheet
    table_name='Sheet1',       # Optional: Name of the sheet (tab) to use. Defaults to 'Sheet1'.
    read_only=False,           # Optional: Set to True to open in read-only mode. Defaults to False.
    auto_timestamp=False,      # Optional: Automatically add/update 'UPDATED' column. Defaults to False.
    id_col_name=None           # Optional: Name of a column to use as a unique ID for rows (used by `update_row_cell`).
)
```

### API Methods

All methods operate on the `table_name` (sheet/tab) specified during initialization.

#### Reading Data

**`get_sheet_values(range='A:Z')`**

Fetches all values from the specified range. Defaults to 'A:Z'.

```python
all_data = _db.get_sheet_values()
# Example Output: [['Header1', 'Header2'], ['data1A', 'data1B'], ['data2A', 'data2B']]

specific_range_data = _db.get_sheet_values(range='A1:C10')
```

#### Modifying Rows

**`add_rows(list_dicts_rows, insert_top=False, raw=True)`**

Adds new rows from a list of dictionaries. Column names in dictionaries should match sheet headers.

-   `list_dicts_rows`: A list of dictionaries, where each dictionary represents a row (e.g., `[{'col_A': 'val1', 'col_B': 'val2'}]`).
-   `insert_top`: If `True`, rows are inserted at the top (below the header). Defaults to `False` (append to bottom).
-   `raw`: If `True` (default), values are entered as-is. If `False`, Sheets attempts to parse them (e.g., for formulas).

```python
_db.add_rows([{'col 1': 'alice', 'col 2': 'adams'}, {'col 1': 'bob', 'col 2': 'barker'}], insert_top=True)
```

**`insert_blank_rows(num_rows=1, index=2)`**

Inserts a specified number of blank rows at a given index.

-   `num_rows`: Number of blank rows to insert. Defaults to 1.
-   `index`: 1-based index where rows should be inserted. Defaults to 2 (i.e., below a header row at row 1).

```python
_db.insert_blank_rows(num_rows=3, index=5)
```

#### Modifying Cells

**`set_cell_text(cell, text, raw=True)`**

Sets the text for a single cell (e.g., 'A5', 'B10').

-   `raw`: If `True` (default), value is entered as-is.

```python
_db.set_cell_text('A5', 'Hello World', raw=True)
```

**`update_row_cell(id_val, col_name, new_text)`**

Updates a specific cell in a row identified by a unique ID. Requires `id_col_name` to be set during `PySheetsDB` initialization.
*(Note: This method seems to be missing from the current `py_sheets_db.py` provided earlier. If it exists, this is its typical usage.)*

```python
# Assuming _db was initialized with id_col_name='id'
_db.update_row_cell(id_val='PROJ-42', col_name='STATUS', new_text='Complete')
```

**`set_cell_range_texts(cell_range, texts, raw=True)`**

Sets values for a range of cells (e.g., 'A10:B11').

-   `texts`: A list of lists representing rows and their cell values (e.g., `[['A10_val', 'B10_val'], ['A11_val', 'B11_val']]`).
-   `raw`: If `True` (default), values are entered as-is.

```python
_db.set_cell_range_texts(cell_range='C1:D2', texts=[['New', 'Data'], ['More', 'Info']])
```

#### Deleting Data

**`delete_rows_beyond(max_rows)`**

Deletes all rows after a specified maximum number of rows, effectively keeping `max_rows` (including the header).

```python
# To keep only the header and the first 100 data rows:
_db.delete_rows_beyond(max_rows=101)
```

## Important Notes

-   **Header Row:** This library assumes your sheet has a frozen header row as the first row. Operations like `add_rows` (when `insert_top=True`) and `insert_blank_rows` are designed to work below this header.
-   **`auto_timestamp`:** If `auto_timestamp=True` is set during initialization (defaults to `False`), an `UPDATED` column is automatically managed. It's added if not present, and its value is set to the current timestamp when rows are added via `add_rows`.
-   **Destructive Operations:** Most destructive operations (like deleting specific columns or individual cells by clearing them) are not directly supported to encourage use as an append-friendly log or simple database. The `delete_rows_beyond` method is an exception for managing sheet size.