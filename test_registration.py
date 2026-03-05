from dotenv import load_dotenv
from google_sheets_handler import GoogleSheetsHandler
import os

load_dotenv()

try:
    h = GoogleSheetsHandler()
    h.open_sheet(os.getenv('GOOGLE_SHEET_URL'))
    result = h.add_registration('Test User', 'Test College', 'Test Batch', '9999999999')
    print(f'✅ {result["message"]}')
except Exception as e:
    print(f'❌ Error: {e}')
