import unittest
import os
import string
from dotenv import load_dotenv
from py_sheets_db import PySheetsDB, TIMESTAMP_COLUMN

# Utility to get column letter (e.g., 0 -> A, 1 -> B)
# A robust version for multi-character columns:
def col_idx_to_letter(idx):
    letters = ""
    while idx >= 0:
        letters = chr(idx % 26 + ord('A')) + letters
        idx = idx // 26 - 1
    return letters

class TestPySheetsDB(unittest.TestCase):

    db_animals = None
    sheet_id = None
    sheets_key = None

    @classmethod
    def setUpClass(cls):
        load_dotenv()
        cls.sheets_key = os.getenv("SHEETS_KEY")
        cls.sheet_id = os.getenv("SHEET_ID")

        if not cls.sheets_key or not cls.sheet_id:
            raise unittest.SkipTest("SHEETS_KEY or SHEET_ID not found in .env file. Skipping tests.")

        cls.db_animals = PySheetsDB(token_file_or_key=cls.sheets_key, sheet_id=cls.sheet_id, table_name='animals', auto_timestamp=True)

    def test_01_read_animals_header(self):
        """Test reading from 'animals' sheet and verify header."""
        values = self.db_animals.get_sheet_values()
        self.assertIsNotNone(values, "Failed to get values from 'animals' sheet.")
        self.assertIsInstance(values, list, "Sheet values should be a list.")
        
        if not values:
            self.fail("'animals' sheet is empty or header is missing. Please ensure it has a header row with 'animal' and 'sound'.")
        
        header = values[0]
        header_lower = [h.lower() for h in header]
        self.assertIn('animal', header_lower, "Header 'animal' not found in 'animals' sheet.")
        self.assertIn('sound', header_lower, "Header 'sound' not found in 'animals' sheet.")
        
        # Check for timestamp column if auto_timestamp is True (which it is in setUpClass)
        self.assertIn(TIMESTAMP_COLUMN.lower(), header_lower, 
                        f"Timestamp column '{TIMESTAMP_COLUMN}' not found when auto_timestamp is True.")

    def test_02_add_row_animals(self):
        """Test adding a row to 'animals' sheet."""
        animal_name = "TestPyAnimalFromUnitTest"
        animal_sound = "TestPySound"
        new_animal_data = {'animal': animal_name, 'sound': animal_sound}
        
        initial_values = self.db_animals.get_sheet_values()
        initial_row_count = len(initial_values)

        self.db_animals.add_rows([new_animal_data])
        
        updated_values = self.db_animals.get_sheet_values()
        self.assertEqual(len(updated_values), initial_row_count + 1, 
                         "Row count did not increase by 1 after adding a row.")
        
        # Verify the added row's content. The new row is the last one.
        header = updated_values[0] # Get current header for correct mapping
        added_row_values = updated_values[-1]
        added_row_dict = dict(zip(header, added_row_values))

        self.assertEqual(added_row_dict.get('animal'), animal_name, "Added animal name does not match.")
        self.assertEqual(added_row_dict.get('sound'), animal_sound, "Added animal sound does not match.")
        
        # Verify timestamp column content if auto_timestamp is enabled
        self.assertIn(TIMESTAMP_COLUMN, added_row_dict, "Timestamp column missing in added row.")
        self.assertIsNotNone(added_row_dict[TIMESTAMP_COLUMN], "Timestamp value is None in added row.")
        self.assertTrue(str(added_row_dict[TIMESTAMP_COLUMN]).strip() != "", "Timestamp value is empty in added row.")

if __name__ == '__main__':
    unittest.main()
