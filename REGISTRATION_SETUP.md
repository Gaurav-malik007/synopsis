# 📝 Registration System - Implementation Summary

## ✅ What's Been Added

Your RAG app now has a complete registration system with Google Sheets integration!

### 1. **Registration Form** (Already in web_app.py)
The registration window appears when a new user first launches the app with the following fields:
- 👤 **Full Name** - Student's complete name
- 🏫 **College / Medical Institute** - Medical college or institute name
- 📅 **Batch / Year** - Academic batch or year (e.g., "2022-2028" or "2nd Year")
- 📱 **Phone Number** - Contact phone number (7-15 digits)

**Where it is**: The form is in `web_app.py` lines 891-900

### 2. **Local Storage** (registrations.csv)
Registration data is always saved locally in a CSV file:
- **File**: `registrations.csv`
- **Columns**: Timestamp, Name, College, Batch, Phone
- **Updates automatically** - No additional configuration needed

### 3. **Google Sheets Integration** (NEW)
Optionally sync registrations to Google Sheets:
- **Module**: `google_sheets_handler.py` - Handles Google Sheets API
- **Function**: Enhanced `save_registration()` in `web_app.py`
- **Auto-creation**: Creates worksheet if it doesn't exist
- **Fallback**: If Google Sheets sync fails, data still saves to local CSV

### 4. **Setup Files Created**
- 📄 `GOOGLE_SHEETS_SETUP.md` - Complete step-by-step setup guide
- 📋 `credentials.example.json` - Template for credentials file
- 📋 `.env.example` - Updated with Google Sheets configuration options
- 🔐 `.gitignore` - Updated to exclude sensitive `credentials.json`

## 🚀 Quick Start

### For Local-Only Storage (Works Immediately!)
```bash
streamlit run web_app.py
```
User registrations will be saved to `registrations.csv` automatically.

### For Google Sheets Integration (Optional)
1. Follow the setup guide: Read `GOOGLE_SHEETS_SETUP.md`
2. Download Google service account credentials
3. Save as `credentials.json` in project root
4. Update `.env` with:
   ```env
   GOOGLE_SHEET_URL=https://docs.google.com/spreadsheets/d/YOUR_SHEET_ID/edit
   GOOGLE_SHEET_CREDENTIALS=credentials.json
   ```
5. Run: `streamlit run web_app.py`

## 📊 How Registration Works

### User Workflow:
1. User launches the app
2. Registration form appears
3. User fills in Name, College, Year, Phone
4. Form validates input
5. On submit:
   - ✅ Data saved to `registrations.csv`
   - ✅ (Optional) Data synced to Google Sheets
   - ✅ Welcome message shows
   - ✅ App loads and user can start using features

### Data Validations:
- ✅ Full Name: Required, non-empty
- ✅ College: Required, non-empty
- ✅ Batch/Year: Required, non-empty
- ✅ Phone: Required, 7-15 digits, supports +, -, (, )

## 📁 File Structure

```
├── web_app.py                      # Main Streamlit app
├── google_sheets_handler.py         # Google Sheets integration (NEW)
├── requirements.txt                 # Updated with gspread & google-auth
├── registrations.csv                # Local registration storage
├── GOOGLE_SHEETS_SETUP.md          # Setup guide (NEW)
├── .env.example                     # Updated config template
├── credentials.example.json         # Credentials template (NEW)
├── .gitignore                       # Updated to exclude credentials.json
└── ... (other files)
```

## 🔧 Technical Details

### Update to `requirements.txt`
Added three new packages for Google Sheets support:
```
gspread>=5.10.0                  # Google Sheets API client
google-auth-oauthlib>=1.0.0     # OAuth authentication
google-auth-httplib2>=0.2.0     # HTTP support
```

### New Google Sheets Handler Class
Located in `google_sheets_handler.py`:
```python
class GoogleSheetsHandler:
    - __init__(credentials_file, sheet_name)
    - authenticate()           # Setup Google auth
    - open_sheet(url_or_name) # Open spreadsheet
    - add_registration()       # Add registration row
    - get_all_registrations() # Retrieve all data
```

### Enhanced save_registration() Function
Now saves to both local CSV and Google Sheets:
1. Always saves to local `registrations.csv`
2. If Google Sheets configured, syncs there too
3. Graceful error handling - local saves never fail

## 🛡️ Security

- ✅ `credentials.json` is in `.gitignore` (won't be committed)
- ✅ Sensitive data not logged
- ✅ Service account has minimal permissions (only assigned sheet)
- ✅ HTTPS used for all Google Cloud communications

## 📋 Columns in Registration Sheet

Both CSV and Google Sheets have these columns:
| Field | Type | Example |
|-------|------|---------|
| Timestamp | DateTime | 2026-03-05 10:30:45 |
| Name | Text | Dr. Riya Sharma |
| College | Text | AIIMS Delhi |
| Batch | Text | 2022-2028 / 2nd Year |
| Phone | Text | 9876543210 |

## 🐛 Troubleshooting

### If registrations aren't saving to CSV:
- Check if the directory is writable
- Ensure `registrations.csv` file has correct permissions

### If Google Sheets sync isn't working:
- Verify `credentials.json` is in project root
- Check `GOOGLE_SHEET_URL` is correct in `.env`
- Ensure service account has "Editor" access to the sheet
- See detailed troubleshooting in `GOOGLE_SHEETS_SETUP.md`

### If validation is blocking registration:
- Ensure Name, College, Batch are non-empty
- Check phone number is 7-15 characters with digits/+/-/(/)

## ✨ Features

✅ User-friendly registration form with emojis  
✅ Real-time input validation  
✅ Error messages guide users to fix issues  
✅ Local CSV storage (always works)  
✅ Optional Google Sheets sync  
✅ Secure credentials handling  
✅ Session persistence (recognizes returning users)  
✅ Welcome message with user's first name  

## 🔄 What Happens on Re-launch?

Once a user has registered:
1. On next app launch, registration form is skipped
2. App loads directly to main features
3. Welcome message shows: "Welcome back, [FirstName]! 👋"
4. User can access: Q&A, MCQ Quiz, Flashcards, Topic Review

## 📞 Next Steps

1. **Test locally**: Run the app and complete registration
2. **(Optional) Set up Google Sheets**: Follow `GOOGLE_SHEETS_SETUP.md`
3. **Share the app**: Deploy and share with MBBS students!

---

**Questions?** Check the detailed guides:
- Local registration: Works out of the box ✨
- Google Sheets setup: See `GOOGLE_SHEETS_SETUP.md`
