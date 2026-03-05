# Project 1: MBBS Notes RAG Agent (Gemini AI)

## What is this?
An AI-powered study companion that answers questions about your **MBBS notes** using RAG (Retrieval Augmented Generation) with **Google Gemini AI**. Upload notes as PDFs, text files, or even photos of handwritten notes — then ask questions, take quizzes, and revise with flashcards.

## Features
- 🩺 **MBBS-focused** — Answers in student-friendly language with proper medical terminology
- 📄 **Multi-format support** — PDF, TXT, JPG, PNG, WebP, HEIC (handwritten photo notes!)
- 🧠 **Smart chunking** — Paragraph-aware splitting keeps context intact
- 🔍 **Semantic search** — Finds the most relevant parts of your notes using embeddings
- 📚 **Source attribution** — Shows which document and relevance score for each answer
- 🎯 **Topic filtering** — Auto-detects topics so you can focus MCQs & flashcards on specific areas
- 📝 **MCQ Quiz** — Auto-generated exam-style MCQs with explanations and detailed results
- 🧠 **Flashcards** — Active recall practice with self-rated difficulty tracking
- 📖 **Topic Review** — Quick revision summaries with key points and mnemonics
- 📸 **Photo Notes** — Upload photos of handwritten notes — Gemini Vision reads them
- 📋 **Registration System** — User registration form with support for local CSV and Google Sheets storage

## Prerequisites
- Python 3.8 or higher
- Google Gemini API key ([Get one free](https://aistudio.google.com/apikey))

## Quick Start

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Set up your API key
Create a `.env` file in this directory:
```
GEMINI_API_KEY=your-gemini-api-key-here
```

### 3. Run the web app (recommended)
```bash
streamlit run web_app.py
```

### 4. Or run the CLI version
```bash
python rag_app.py
```
(Place `.txt` or `.pdf` files in the `documents/` folder first)

## User Registration

When you first launch the web app, a registration form will appear asking for:
- **Full Name** — Your complete name
- **College** — Your medical college or institute name
- **Batch/Year** — Your academic batch or year (e.g., "2022-2028" or "2nd Year")
- **Phone Number** — Your contact number

**Registration data is stored in:**
- ✅ **Local CSV file** (`registrations.csv`) — Always saved automatically
- 📊 **Google Sheets** (Optional) — Follow [GOOGLE_SHEETS_SETUP.md](GOOGLE_SHEETS_SETUP.md) to enable

See [REGISTRATION_SETUP.md](REGISTRATION_SETUP.md) for detailed information about the registration system.

## How It Works
1. **Upload Documents** — Upload PDFs, text files, or photos of notes via the sidebar
2. **Smart Chunking** — Splits notes into paragraph-aware chunks with overlap
3. **Create Embeddings** — Uses Gemini `gemini-embedding-001` to vectorize chunks (cached for performance)
4. **Topic Detection** — Auto-extracts distinct topics from your notes
5. **Semantic Search** — Finds the most relevant chunks using cosine similarity
6. **Generate Answer** — Uses `gemini-2.5-flash` with an MBBS-tuned prompt

## Files
- `web_app.py` — Streamlit web interface (recommended)
- `rag_app.py` — CLI version
- `requirements.txt` — Python dependencies
- `documents/` — Sample MBBS notes
- `.env` — Your Gemini API key (create this)
- `.streamlit/config.toml` — Streamlit theme configuration

## Tips
- Start with one subject's notes at a time for more focused results
- Use the **Topic Filter** to focus MCQs and flashcards on specific areas
- The more detailed your notes, the better the answers
- Ask specific questions like _"Explain the conducting system of the heart"_
- Take photos of handwritten notes — the AI can read them too!
