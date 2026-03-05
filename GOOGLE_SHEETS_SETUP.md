# 📊 Google Sheets Registration Setup Guide

This guide will help you configure Google Sheets integration for storing user registrations.

## Step-by-Step Setup

### 1. Create a Google Cloud Project
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click on the project dropdown at the top
3. Click "NEW PROJECT"
4. Name it "Synopsis Registration" (or any name you prefer)
5. Click "CREATE"

### 2. Enable Required APIs
1. In the Cloud Console, go to "APIs & Services" → "Library"
2. Search for "Google Sheets API"
3. Click on it and press "ENABLE"
4. Go back and search for "Google Drive API"
5. Click on it and press "ENABLE"

### 3. Create a Service Account
1. Go to "APIs & Services" → "Credentials"
2. Click "CREATE CREDENTIALS"
3. Select "Service Account"
4. Fill in the details:
   - **Service account name**: "synopsis-bot"
   - **Service account ID**: (auto-generated)
   - Click "CREATE AND CONTINUE"
5. Skip optional steps and click "DONE"

### 4. Create and Download JSON Key
1. In the Credentials page, find your service account "synopsis-bot"
2. Click on it
3. Go to the "KEYS" tab
4. Click "ADD KEY" → "Create new key"
5. Select "JSON" format
6. Click "CREATE"
7. A JSON file will automatically download - **Save it as `credentials.json`** in your project root

### 5. Create a Google Sheet
1. Go to [Google Sheets](https://sheets.google.com/)
2. Create a new spreadsheet and name it "Synopsis Registrations"
3. Copy the URL from your browser (it will look like: `https://docs.google.com/spreadsheets/d/SHEET_ID/edit`)

### 6. Share the Sheet with Service Account
1. Open your spreadsheet
2. Click the "Share" button
3. Copy the service account email from your `credentials.json` file (it looks like `synopsis-bot@project-id.iam.gserviceaccount.com`)
4. Paste it in the Share dialog and give it **Editor** access
5. Click "Share"

### 7. Configure Environment Variables
Create or update your `.env` file with:

```env
GEMINI_API_KEY=your-gemini-api-key-here
GOOGLE_SHEET_URL=https://docs.google.com/spreadsheets/d/YOUR_SHEET_ID/edit
GOOGLE_SHEET_CREDENTIALS=credentials.json
```

Replace `YOUR_SHEET_ID` with the ID from your Google Sheet URL (the long string between `/d/` and `/edit`).

### 8. Install Dependencies
Make sure to install the required packages:

```bash
pip install -r requirements.txt
```

This installs:
- `gspread` - Google Sheets API client
- `google-auth-oauthlib` - Google authentication
- `google-auth-httplib2` - HTTP support

## Testing

To test if everything is set up correctly:

```bash
python -c "
from google_sheets_handler import GoogleSheetsHandler
import os

try:
    handler = GoogleSheetsHandler()
    handler.open_sheet(os.getenv('GOOGLE_SHEET_URL'))
    print('✅ Google Sheets connection successful!')
except Exception as e:
    print(f'❌ Error: {e}')
"
```

## Using the Registration Form

Once configured:

1. Run the Streamlit app: `streamlit run web_app.py`
2. Users will see the registration form on first login
3. Their data will be saved to both:
   - Local `registrations.csv` file
   - Your Google Sheet (if configured)

## Troubleshooting

### "Credentials file not found"
- Make sure `credentials.json` is in the same directory as `web_app.py`
- Check that `GOOGLE_SHEET_CREDENTIALS` environment variable is set correctly

### "Permission denied"
- Verify you shared the Google Sheet with the service account email
- Ensure the service account has "Editor" access

### "Sheet not found"
- Verify the `GOOGLE_SHEET_URL` is correct
- Make sure you're using the full spreadsheet URL (with `/edit` at the end)

### Missing APIs
- Return to Cloud Console and enable both:
  - Google Sheets API
  - Google Drive API

## Notes

- User data is saved locally first (in `registrations.csv`)
- Google Sheets sync is optional - if it fails, registrations still work
- The service account only needs access to the specific spreadsheet you share with it
- Keep your `credentials.json` file secure - don't commit it to version control

## Security Best Practices

1. Add `credentials.json` to `.gitignore` to prevent accidental upload
2. Regenerate credentials if they're ever exposed
3. Use strong Google account authentication (2FA)
4. Regularly audit who has access to your Google Sheet
