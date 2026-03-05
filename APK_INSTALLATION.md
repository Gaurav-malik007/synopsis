# 📦 APK Installation Guide for Synopsis

## Option 1: Install as Progressive Web App (PWA) - Easiest for Android ⭐

This method works on ANY Android or iOS phone and is the fastest way to get a home-screen app icon.

### Steps:
1. **Open the app in your phone browser**
   - Go to: https://synopsis.streamlit.app/
   
2. **Add to Home Screen (Android)**
   - Tap the **⋮ (three dots)** menu at top-right
   - Select **"Add to home screen"** or **"Install app"**
   - Tap **"Install"**
   - App will appear on your home screen as an icon
   
3. **Add to Home Screen (iPhone)**
   - Tap the **Share** button at bottom
   - Scroll and tap **"Add to Home Screen"**
   - Name it "Synopsis"
   - Tap **"Add"**

✅ The app will now work like a native app with offline caching!

---

## Option 2: Download Native APK - For Full App Experience

For a true native Android app experience, follow these steps:

### What You Need:
- Computer with Python 3.9+
- Android phone (Android 7+)
- ~1 GB free disk space
- 10-15 minutes

### Step 1: Download Files
1. Clone the Synopsis repository:
```bash
git clone https://github.com/Gaurav-malik007/synopsis.git
cd synopsis
```

2. Install build tools:
```bash
pip install buildozer cython
```

### Step 2: Configure Build
Create a file named `buildozer.spec` in the project folder (we've included one):

```bash
# The file is already included, just verify it exists
ls buildozer.spec
```

### Step 3: Build APK (Windows)
```bash
# This takes 5-10 minutes
buildozer android debug
```

**On Mac/Linux:**
```bash
# Install Java Development Kit first
brew install openjdk

buildozer android debug
```

### Step 4: Transfer to Phone
APK will be created at: `bin/synopsis-0.1-debug.apk`

Options to transfer:
1. **Email to yourself** and download on phone
2. **Use cloud drive** (Google Drive, Dropbox, OneDrive)
3. **Use USB cable** and file manager

### Step 5: Install on Android Phone
1. Download the APK file to your Android phone
2. Open Files/File Manager app
3. Find the `.apk` file
4. Tap it to install
5. If prompted "Unknown app source" → Tap Settings → Enable installation from this source
6. Complete installation
7. App appears in your app drawer

---

## Option 3: Use Pre-built APK (Simplest)

**We're preparing a pre-built APK download.** Check back soon or email for access.

---

## Troubleshooting APK Installation

### "App crashes on startup"
- Make sure you have latest Android (7.0+)
- Uninstall and reinstall
- Check storage space (min 100MB free)

### "Cannot download/transfer APK"
- Use PWA method instead (Option 1 - very reliable)
- Share via cloud drive link

### "Install blocked - Unknown source"
- Go to Settings → Apps → Special app access → Install unknown apps
- Select your file manager/browser
- Enable "Allow"

### "APK file is corrupted"
- Re-download from cloud link
- Verify file size is > 50MB

---

## Recommended: PWA Method

**Why PWA is better than APK:**
✅ No installation errors
✅ Works on ALL devices (Android, iOS, Windows, Mac)
✅ Auto-updates instantly
✅ Uses less storage
✅ Faster loading
✅ Offline support

**We recommend PWA (Option 1) unless you need offline-only functionality.**

---

## APK Build Specification

The APK includes:
- **Python 3.9** runtime
- **All dependencies** (streamlit, google-genai, PyPDF2, etc.)
- **Medical theme** - Same as web version
- **File permissions** - Camera for photo notes, Storage for documents
- **Network access** - For AI processing

**Size:** ~150-200 MB
**Requires:** Android 7.0+ (API 24+)
**Permissions:** Camera, Storage, Network

---

## Share APK with Others

Once built or downloaded:

### WhatsApp/Telegram:
1. Save APK to cloud (Google Drive, etc.)
2. Share the download link:
```
Hey! Download Synopsis - Free MBBS study app
📚 Upload notes → Ask questions
📝 Auto MCQs → 🲳 Flashcards
🔗 https://drive.google.com/...
```

### Email:
```
Subject: Synopsis - Medical Study App APK

Download the Synopsis app - AI-powered study companion for MBBS
Learn better with combined features:
- Chat with your notes
- Auto-generated MCQs  
- Flashcard practice
- Exam paper analysis

Download: [APK download link]
```

### College WhatsApp Group:
```
🩺 **SYNOPSIS - Free MBBS Study Companion App**

Finally a complete study solution! 
✅ Upload your notes (PDF/photos)
✅ AI asks MCQs (self-check)
✅ Flashcards for quick revision
✅ NO ads, NO tracking, COMPLETELY FREE

📱 Install: [Link to APK or PWA guide]

Works on all phones 📲
```

---

## Still Have Questions?

Check [MOBILE_GUIDE.md](MOBILE_GUIDE.md) for mobile usage tips.
