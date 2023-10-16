# This requires a frozen header row!

from googleapiclient.discovery import build
from google.oauth2 import service_account
import os.path
import datetime
import string

SHEETS_READ_ONLY_SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
SHEETS_READ_WRITE_SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

TIMESTAMP_COLUMN = 'UPDATED'

TIMESTAMP_FORMAT = '%Y-%m-%d %H:%M'

SHEETS_COL_LETTERS = list(string.ascii_uppercase)

class SheetsDB:
    _sheet_id = None
    _table_name = ''
    _table_id = None

    _service = None

    _num_cols = 0

    _col_name_to_idx = {}

    _auto_timestamp = False

    def __init__(self, token_file: str, sheet_id: str, table_name = 'Sheet1', read_only = False, auto_timestamp = True):
        if not os.path.exists(token_file):
            raise Exception("No token file!")
        
        self._sheet_id = sheet_id

        self._table_name = table_name

        self._auto_timestamp = auto_timestamp

        creds = service_account.Credentials.from_service_account_file(
        token_file, scopes=SHEETS_READ_ONLY_SCOPES if read_only else SHEETS_READ_WRITE_SCOPES)

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
            self.add_text_to_cell(f'{timestamp_idx}1', TIMESTAMP_COLUMN)
            header.append(TIMESTAMP_COLUMN)

        for i, h in enumerate(header):
            col_name = '' if not h else h
            self._col_name_to_idx[col_name] = i

    def get_sheet_values(self, range = 'A:Z'):
        result = self._service.values().get(spreadsheetId=self._sheet_id,range=f'{self._table_name}!{range}').execute()
        values = result.get('values', [])
        return values

    def add_text_to_cell(self, cell, text):        
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
                    "endIndex": index
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