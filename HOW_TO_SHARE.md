# 📤 How to Share Synopsis App with Others

Your app can be shared in multiple ways depending on your audience and preferences.

---

## 🚀 **Option 1: Share Live Streamlit Cloud URL (EASIEST)**

Once your app is deployed on Streamlit Cloud, you get a public URL like:
```
https://gaurav-malik007-synopsis.streamlit.app
```

### **How to Share:**

**Step 1:** Get your app URL from Streamlit Cloud
- Go to [share.streamlit.io](https://share.streamlit.io)
- Find your deployed app
- Copy the URL (shown at the top)

**Step 2:** Share the URL
- **Email**: Send the link to students
- **WhatsApp**: Share the link directly
- **Class Group**: Post in your class chat
- **Social Media**: Share on Instagram/Facebook
- **College Portal**: If available, post on your college's LMS

### **What Students See:**
```
They click the link → App opens in browser
→ They register (Name, College, Year, Phone)
→ They can use all features immediately
```

### **Advantages:**
✅ Works on any device (phone, tablet, laptop)  
✅ No installation needed  
✅ Always up-to-date  
✅ No file management needed  
✅ Students can access anytime, anywhere  
✅ Their data saved to Google Sheets  

### **Disadvantages:**
❌ Requires internet connection  
❌ Streamlit free tier has usage limits  

---

## 📱 **Option 2: Share GitHub Repository (FOR DEVELOPERS)**

Share the source code so others can run it locally or fork it.

### **GitHub URL:**
```
https://github.com/Gaurav-malik007/synopsis
```

### **How Others Can Use It:**

**Step 1: Clone the repo**
```bash
git clone https://github.com/Gaurav-malik007/synopsis.git
cd synopsis
```

**Step 2: Install dependencies**
```bash
pip install -r requirements.txt
```

**Step 3: Set up environment**
Create `.env` file:
```
GEMINI_API_KEY=your-api-key-here
GOOGLE_SHEET_URL=your-sheet-url
GOOGLE_SHEET_CREDENTIALS=credentials.json
```

**Step 4: Run the app**
```bash
streamlit run web_app.py
```

### **Advantages:**
✅ Full control over code  
✅ Can customize the app  
✅ Works offline (after setup)  
✅ No usage limits  

### **Disadvantages:**
❌ Requires technical setup  
❌ Needs API keys  
❌ More complex for non-technical users  
❌ Requires local environment setup  

---

## 💻 **Option 3: Create Installation Guide for Others**

Create a step-by-step guide for college friends/students.

### **Create a SHARING_GUIDE.md file:**

```markdown
# 🩺 Synopsis - MBBS Study Companion

## Quick Start for Students

### Method 1: Use Online (Easiest)
1. Open: https://gaurav-malik007-synopsis.streamlit.app
2. Register with your details
3. Upload your notes and start studying!

### Method 2: Run Locally (Advanced)
See SETUP_LOCAL.md
```

---

## 📧 **Option 4: Email Sharing Template**

Send this to other students:

---

### **Email Template:**

---

**Subject:** 📚 Free MBBS Study Companion - Synopsis App

**Body:**

Hi [Name],

I've created a free AI-powered MBBS study companion called **Synopsis**. 

You can:
✅ Upload your notes (PDFs, text, photos)
✅ Ask questions about your content
✅ Take auto-generated MCQ quizzes
✅ Create flashcards for revision
✅ Analyze NEET PG & UPSC CMS papers
✅ Get AI explanations for concepts

**Try it now:** [APP_URL]

Just click, register, and start studying!

- Completely FREE
- Works on phone/tablet/laptop
- Your data saved securely
- Made for MBBS students

Share with your friends! 📖

---

---

## 📱 **Option 5: WhatsApp Group Sharing**

### **WhatsApp Message Template:**

```
🩺 SYNOPSIS - Free MBBS Study App!

💡 What it does:
📚 Upload notes → AI reads them
❓ Ask questions → Get instant answers
📝 Auto MCQs → Generated from your notes
🧠 Flashcards → Active recall practice
📊 Analyze papers → NEET PG & UPSC CMS

Link: [APP_URL]

✨ Features:
✅ Free forever
✅ Phone-friendly
✅ No ads
✅ Your data private
✅ Made by students, for students

Try it! → [APP_URL]

Share with your batch! 📖
```

---

## 🎓 **Option 6: College Prof/HOD Recommendation**

Share with faculty to recommend to students:

### **Professional Email to Faculty:**

---

**Subject:** Educational Tool - Synopsis MBBS Study App

Dear [Prof/Dr.],

I've developed an AI-powered study companion called "Synopsis" designed specifically for MBBS students.

**Key Features:**
- Personalized learning from student notes
- Instant explanations using AI
- Auto-generated practice MCQs
- Examination paper analysis (NEET PG, UPSC CMS)
- Flashcard system for revision

**URL:** [APP_URL]

**Benefits:**
- Reduces study time through AI assistance
- Encourages active learning
- Helps with exam preparation
- Completely free for students

Would you consider mentioning this to our batch? I can create a brief demo if helpful.

Thank you,
[Your Name]

---

---

## 📊 **Option 7: Create QR Code**

Convert your URL to a QR code for easy sharing:

### **Generate QR Code:**
1. Go to [QR Code Generator](https://www.qr-code-generator.com/)
2. Paste your app URL
3. Download the QR code image
4. Print or share digitally

### **Use Cases:**
- Print on class notices
- Share in class WhatsApp group
- Post on college bulletin boards
- Include in email signatures

---

## 📣 **Option 8: Social Media Sharing**

### **Instagram Post Example:**

```
Caption:
🩺 I built an AI MBBS study app!

Tired of boring revision? Meet Synopsis:
✅ Upload notes → AI explains
✅ Ask questions → Instant answers
✅ Auto MCQs → Focus by topic
✅ Analyze papers → NEET PG & UPSC trends
🎓 Free forever

Link in bio! [APP_URL]

Tag your study partners! 👇
#MBBS #StudyHack #MedicalStudents #AI
```

### **LinkedIn Post:**

```
🩺 Excited to share my latest project:

I've developed "Synopsis" - an AI-powered study companion 
tailored for MBBS students. 

Features:
• Intelligent note analysis
• Exam paper trend analysis
• Practice question generation
• Smart flashcard system

Available to all medical students. Check it out and share 
with your network!

[APP_URL]

#Healthcare #AI #MedicalEducation #EdTech
```

---

## 🎯 **Complete Sharing Checklist**

- [ ] **Get Streamlit Cloud URL** (after deployment)
- [ ] **Test the link** - Make sure it works
- [ ] **Create sharing message** - Copy template above
- [ ] **Share with classmates** - WhatsApp/email/social
- [ ] **Ask for feedback** - Help improve the app
- [ ] **Pin in group chats** - Easy access
- [ ] **Create QR code** - For posters
- [ ] **Share GitHub** - For developers who want to contribute

---

## 📊 **How Many Can Use?**

### **Streamlit Cloud Free Plan Limits:**
- ✅ **Unlimited users** (anyone with the link)
- ✅ **Unlimited access** (24/7)
- ⚠️ **1 hour monthly CPU time** per user (usually enough)
- ✅ **No payment required**

> If you exceed free limits, you can upgrade Streamlit Cloud plan ($5-15/month)

---

## 🔐 **Privacy & Security**

When sharing, students should know:
- ✅ Data saved locally on their computers (CSV)
- ✅ Optional Google Sheets sync (only if they set up)
- ✅ No tracking or ads
- ✅ Open source code (public GitHub)
- ✅ Their registration data kept private

---

## 📝 **FAQ for Students**

**Q: Do I need to install anything?**
A: No! Just open the link in your browser.

**Q: Is it free?**
A: Yes, completely free!

**Q: Can I upload my own notes?**
A: Yes! Upload PDFs, text files, or photos of notes.

**Q: Will my data be private?**
A: Yes! Your data stays with you locally.

**Q: Does it work on mobile?**
A: Yes! Works on phones, tablets, and computers.

**Q: Can we use it together in a study group?**
A: Yes! Each person has their own account.

**Q: What if I find a bug?**
A: Email me or submit an issue on GitHub!

---

## 🚀 **Recommended Sharing Strategy**

### **Week 1:**
- Share with close study group (5-10 friends)
- Gather feedback
- Fix any issues

### **Week 2:**
- Share with whole class (50-100 students)
- Create simple demo video (optional)
- Post QR code in class

### **Week 3+:**
- Share with other colleges (if scalable)
- Encourage forks on GitHub
- Keep improving based on feedback

---

## 📞 **Support When Sharing**

When others use your app, be ready to help with:

1. **"Can't access the app"**
   → Check internet connection
   → Try different browser
   → Clear browser cache

2. **"Registration not working"**
   → Check all fields are filled
   → Valid phone number format
   → Check for error messages

3. **"Notes not uploading"**
   → File size < 20 MB
   → Supported format (PDF, TXT, JPG)
   → Try different file

4. **"Google Sheets not syncing"**
   → Optional feature (CSV backup works)
   → Send setup instructions

---

## ✨ **Success Tips**

1. **Start Small** - Share with friends first
2. **Get Feedback** - Ask what they like/dislike
3. **Improve** - Make changes based on feedback
4. **Document** - Keep a README updated
5. **Be Responsive** - Help when they have issues
6. **Celebrate** - Share success metrics!

---

**Your app is ready to be shared! Pick one or more methods above and start reaching MBBS students! 🎉**
