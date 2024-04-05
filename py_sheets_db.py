# This requires a frozen header row!

from googleapiclient.discovery import build
from google.oauth2 import service_account
import os.path
import datetime
import string
import json

SHEETS_READ_ONLY_SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
SHEETS_READ_WRITE_SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

TIMESTAMP_COLUMN = 'UPDATED'

TIMESTAMP_FORMAT = '%Y-%m-%d %H:%M'

SHEETS_COL_LETTERS = list(string.ascii_uppercase)

class PySheetsDB:
    _sheet_id = None
    _table_name = ''
    _table_id = None

    _service = None

    _num_cols = 0

    _col_name_to_idx = {}

    _auto_timestamp = False

    _id_col_name = None

    def __init__(self, token_file_or_key: str, sheet_id: str, table_name = 'Sheet1', 
                 read_only = False, auto_timestamp = False, id_col_name=None):
        """
        token_file can also be the key string
        """
        is_token_file = True
        if not os.path.exists(token_file_or_key):
            print(f'Token is not file, falling back to string')
            is_token_file = False
        
        self._sheet_id = sheet_id

        self._table_name = table_name

        self._auto_timestamp = auto_timestamp

        self._id_col_name = id_col_name

        creds = None

        if is_token_file:
            creds = service_account.Credentials.from_service_account_file(
            token_file_or_key, scopes=SHEETS_READ_ONLY_SCOPES if read_only else SHEETS_READ_WRITE_SCOPES)
        else:
            # Convert the JSON string to a dictionary
            key_dict = json.loads(token_file_or_key)            
            creds = service_account.Credentials.from_service_account_info(
            key_dict, scopes=SHEETS_READ_ONLY_SCOPES if read_only else SHEETS_READ_WRITE_SCOPES)

        service = build('sheets', 'v4', credentials=creds)

        self._service = service.spreadsheets()

        self._table_name = table_name

        # Get table id
        spreadsheet_details = self._service.get(spreadsheetId=self._sheet_id).execute()
        for sheet in spreadsheet_details['sheets']:
            if sheet['properties']['title'] == self._table_name:
                self._table_id = sheet['properties']['sheetId']
                break   

        header = self.get_sheet_values(range='1:1')[0]

        self._num_cols = len(header)

        if auto_timestamp and TIMESTAMP_COLUMN not in header:
            timestamp_idx = SHEETS_COL_LETTERS[len(header)]
            self.set_cell_text(f'{timestamp_idx}1', TIMESTAMP_COLUMN)
            header.append(TIMESTAMP_COLUMN)

        # stupid python
        self._col_name_to_idx = {}

        # build map of column names to idx
        for i, h in enumerate(header):
            col_name = '' if not h else h
            self._col_name_to_idx[col_name] = i

    def get_sheet_values(self, range = 'A:Z'):
        """
        Returns a list of lists like
        [['1', 'alice', 'adams'], ['2', 'bob', 'barker']]
        """
        result = self._service.values().get(spreadsheetId=self._sheet_id,range=f'{self._table_name}!{range}').execute()
        values = result.get('values', [])
        return values

    def set_cell_text(self, cell, text):        
        # Build range for the cell
        cell_range = f'{self._table_name}!{cell}'
        
        # Set value for the cell
        body = {
            'values': [[text]] 
        }
        
        self._service.values().update(
            spreadsheetId=self._sheet_id, 
            range=cell_range,
            valueInputOption='RAW',
            body=body
        ).execute()

    def set_cell_range_texts(self, cell_range, texts):        
        # Build range for the cell
        cell_range = f'{self._table_name}!{cell_range}'
        
        # Set value for the cell
        body = {
            'values': texts 
        }
        
        response = self._service.values().update(
            spreadsheetId=self._sheet_id, 
            range=cell_range,
            valueInputOption='RAW',
            body=body
        ).execute()    
        print(response)    

    def _add_rows(self, rows_vals, insert_top = False): 
        row_num = 2
        if insert_top:
            # add blank rows
            self.insert_blank_rows(num_rows=len(rows_vals))
        else:
            values = self.get_sheet_values()
            row_num = len(values) + 1

        cell_range = f'{self._table_name}!A{row_num}'

        body = {
            'values': rows_vals
        }
        
        self._service.values().update(
            spreadsheetId=self._sheet_id, 
            range=cell_range,
            valueInputOption='RAW',
            body=body
        ).execute()

    # [{col_name1 : val1, col_name2 : val2}, ...]
    def add_rows(self, list_dicts_rows, insert_top = False):
        rows = []

        for d in list_dicts_rows:
            vals = [''] * self._num_cols
            for k in d.keys():
                idx = self._col_name_to_idx[k]
                val = d[k]
                vals[idx] = val

            if self._auto_timestamp:
                vals[self._col_name_to_idx[TIMESTAMP_COLUMN]] = self.now_human()    
            rows.append(vals)
        self._add_rows(rows, insert_top=insert_top)
    
    def now_human(self) -> str:
        return datetime.datetime.now().strftime(TIMESTAMP_FORMAT)
    
    def date_from_string(self, date_str: str):
        return datetime.strptime(date_str, TIMESTAMP_FORMAT)

    def insert_blank_rows(self, num_rows = 1, index=2):
        """Insert a blank row at the specified index. Note: Assumes a frozen header at index 1."""
        
        # Ensure index is above the header to avoid disrupting the frozen header
        if index <= 1:
            raise ValueError("Cannot insert a row at or below the header (index 1). Provide an index greater than 1.")
        
        requests = [{
            "insertDimension": {
                "range": {
                    "sheetId": self._table_id, 
                    "dimension": "ROWS",
                    "startIndex": index - 1,  # Convert to 0-based index for the Sheets API
                    "endIndex": index - 1 + num_rows
                },
                "inheritFromBefore": False
            }
        }]

        try:
            self._service.batchUpdate(
                spreadsheetId=self._sheet_id,
                body={'requests': requests}
            ).execute()
        except Exception as e:
            print(f"Failed to insert row at index {index}. Error: {e}")


    def update_row_cell(self, id, column_name, cell_val):
        if self._id_col_name is None:
            raise ValueError("ID column name not set")

        if column_name not in self._col_name_to_idx:
            raise ValueError(f"Column {column_name} does not exist")

        # Fetch all rows
        all_rows = self.get_sheet_values()

        # Find the row index with the matching ID
        id_col_idx = self._col_name_to_idx[self._id_col_name]
        target_row_idx = None
        for idx, row in enumerate(all_rows):
            if len(row) > id_col_idx and row[id_col_idx] == str(id):
                target_row_idx = idx + 1  # +1 to account for header row
                break

        if target_row_idx is None:
            raise ValueError(f"No row found with ID {id}")

        # Column index for the column to update
        col_idx = self._col_name_to_idx[column_name]
        col_letter = SHEETS_COL_LETTERS[col_idx]

        # Update the cell
        self.set_cell_text(f'{col_letter}{target_row_idx}', cell_val)

    def delete_rows_beyond(self, max_rows):
        spreadsheet_data = [
            {
                "deleteDimension": {
                    "range": {
                        "sheetId": self._table_id,
                        "dimension": "ROWS",
                        "startIndex": max_rows
                    }
                }
            }
        ]
        body = {"requests": spreadsheet_data}

        try:
            result = self._service.batchUpdate(
                spreadsheetId=self._sheet_id, body=body).execute()
            print("result " + str(result))
        except Exception as e:
            print("Unable to resize sheet. Exception " + str(e))