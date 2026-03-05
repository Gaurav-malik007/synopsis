# 🚀 Streamlit Cloud Deployment Guide

Your GitHub repo is ready: https://github.com/Gaurav-malik007/synopsis

## Step-by-Step Deployment

### **Step 1: Go to Streamlit Cloud**
1. Open [share.streamlit.io](https://share.streamlit.io)
2. Click on your GitHub profile (top right)
3. Sign in with GitHub if prompted

### **Step 2: Deploy Your App**
1. Click **"New app"** button
2. Fill in the details:
   - **Repository**: `Gaurav-malik007/synopsis`
   - **Branch**: `main`
   - **Main file path**: `web_app.py`
3. Click **"Deploy"**

**Wait 2-3 minutes** for deployment to complete...

---

## Step 3: Configure Environment Variables (Secrets)

Once deployed, go to **Settings** (⚙️ icon, top right) → **Secrets**

Add these secrets:

```toml
GEMINI_API_KEY = "AIzaSyD09oNFnIEWuYxN4REETUG9x5xlVI6M9LE"
GOOGLE_SHEET_URL = "https://docs.google.com/spreadsheets/d/1i2VujcNWKDPiZ5d0y9N3H2dakro1cMYbyF2IRbw_3Ms/edit?gid=0#gid=0"
```

Then click **Save**

---

## Step 4: Handle Google Sheets Credentials

Since `credentials.json` is in `.gitignore`, you need to handle it specially on Streamlit Cloud.

### **Option A: Upload Credentials File (Recommended)**

1. In Streamlit Cloud, go to **Settings** → **Advanced settings**
2. Look for a way to upload files, OR
3. Use the built-in file manager to add `credentials.json`

### **Option B: Use Streamlit Secrets (Alternative)**

If Option A doesn't work, decode your `credentials.json` and add it to Secrets:

1. Open your local `credentials.json`
2. Go to Streamlit Settings → **Secrets**
3. Add the entire JSON content as:

```toml
[gcp_service_account]
type = "service_account"
project_id = "your-project-id"
private_key_id = "your-key-id"
private_key = "-----BEGIN PRIVATE KEY-----\n...your key...\n-----END PRIVATE KEY-----\n"
client_email = "synopsis-bot@your-project.iam.gserviceaccount.com"
client_id = "..."
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "https://..."
```

---

## Your App URL

Once deployed, your app will be available at:

```
https://gaurav-malik007-synopsis.streamlit.app
```

(The exact URL will be shown in Streamlit Cloud dashboard)

---

## What Users Will See

1. **Registration Form** (first time only)
   - Full Name
   - College/Institute
   - Batch/Year
   - Phone Number
   
2. **Data Storage**
   - Local CSV (if no Google Sheets)
   - Google Sheets (if configured)

3. **Main Features**
   - Ask Questions
   - MCQ Quiz
   - Flashcards
   - Topic Review

---

## Troubleshooting

### **App shows "Credentials file not found"**
→ You need to handle `credentials.json` as described in Step 4

### **Google Sheets not syncing**
→ Check that:
- GOOGLE_SHEET_URL is correct in Secrets
- Service account has Editor access to the sheet
- credentials.json is properly configured

### **Gemini API not working**
→ Verify GEMINI_API_KEY is correct in Secrets

### **App won't start**
→ Check Streamlit Cloud logs for error messages

---

## Quick Summary

1. ✅ Code on GitHub: https://github.com/Gaurav-malik007/synopsis
2. 🚀 Deploy to: https://share.streamlit.io
3. 🔐 Add Secrets: GEMINI_API_KEY + GOOGLE_SHEET_URL
4. 📄 Upload: credentials.json (if using Google Sheets)
5. 🎉 Live app in 2-3 minutes!

---

## Support

If you encounter issues:
1. Check Streamlit Cloud logs
2. Verify all environment variables
3. Ensure GitHub repo is public
4. Check that `web_app.py` exists in main branch

Happy deploying! 🎊
