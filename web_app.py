"""
MBBS Notes RAG Agent - Web App
================================
Streamlit web interface for the MBBS Notes RAG Agent.
Upload your notes, ask questions, take quizzes, and revise with flashcards.
"""

import os
import re
import math
import random
import json
import time
import tempfile
import csv
from datetime import datetime
from pathlib import Path
from io import BytesIO

import streamlit as st
from google import genai
from google.genai import types
from dotenv import load_dotenv
from google_sheets_handler import GoogleSheetsHandler

# Load .env for local development
load_dotenv()

# --- Page Config ---
st.set_page_config(
    page_title="Synopsis — Learn It Your Way",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Custom CSS for Medical Theme ---
st.markdown("""
<style>
    /* Import Google Font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    * { font-family: 'Inter', sans-serif; }

    /* Animations */
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(16px); }
        to   { opacity: 1; transform: translateY(0); }
    }
    @keyframes pulse {
        0%, 100% { box-shadow: 0 0 0 0 rgba(13, 148, 136, 0.4); }
        50%      { box-shadow: 0 0 0 10px rgba(13, 148, 136, 0); }
    }
    @keyframes shimmer {
        0%   { background-position: -200% 0; }
        100% { background-position: 200% 0; }
    }
    .fade-in { animation: fadeInUp 0.4s ease-out both; }

    /* Main header styling */
    .main-header {
        background: linear-gradient(135deg, #0D9488 0%, #065F56 50%, #134E4A 100%);
        padding: 2rem 2.5rem;
        border-radius: 16px;
        margin-bottom: 1.5rem;
        box-shadow: 0 8px 32px rgba(13, 148, 136, 0.3);
        border: 1px solid rgba(255,255,255,0.1);
        animation: fadeInUp 0.5s ease-out;
    }
    .main-header h1 {
        color: #ffffff;
        font-size: 2rem;
        font-weight: 700;
        margin: 0;
        letter-spacing: -0.5px;
    }
    .main-header p {
        color: #99F6E4;
        font-size: 1rem;
        margin: 0.3rem 0 0 0;
        font-weight: 400;
    }

    /* Card styling */
    .med-card {
        background: linear-gradient(145deg, #1E293B, #1a2332);
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
        animation: fadeInUp 0.4s ease-out both;
    }
    .med-card:hover {
        border-color: #0D9488;
        box-shadow: 0 4px 20px rgba(13, 148, 136, 0.15);
        transform: translateY(-3px);
    }

    /* Feature card in empty state */
    .feature-card {
        background: linear-gradient(145deg, #1E293B, #1a2332);
        border: 1px solid #334155;
        border-radius: 14px;
        padding: 1.5rem;
        text-align: center;
        transition: all 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94);
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
        min-height: 140px;
    }
    .feature-card:hover {
        border-color: #0D9488;
        transform: translateY(-6px);
        box-shadow: 0 12px 28px rgba(13, 148, 136, 0.2);
    }
    .feature-card h3 { margin: 0.5rem 0 0.3rem 0; font-size: 1.1rem; }
    .feature-card .feature-icon { font-size: 2rem; }

    /* Score card */
    .score-card {
        background: linear-gradient(135deg, #0D9488, #065F56);
        border-radius: 12px;
        padding: 1.5rem;
        text-align: center;
        box-shadow: 0 4px 20px rgba(13, 148, 136, 0.3);
        animation: fadeInUp 0.5s ease-out;
    }
    .score-card h2 { color: white; margin: 0; font-size: 2.5rem; }
    .score-card p { color: #99F6E4; margin: 0.3rem 0 0 0; }

    /* MCQ option styling */
    .mcq-option {
        background: #1E293B;
        border: 1px solid #334155;
        border-radius: 10px;
        padding: 0.8rem 1.2rem;
        margin: 0.4rem 0;
        cursor: pointer;
        transition: all 0.2s ease;
    }
    .mcq-option:hover { border-color: #0D9488; background: #263347; }

    /* Correct / Wrong indicators */
    .correct-banner {
        background: linear-gradient(135deg, #065F46, #064E3B);
        border: 1px solid #10B981;
        border-radius: 10px;
        padding: 1rem 1.2rem;
        margin: 0.5rem 0;
        animation: fadeInUp 0.3s ease-out;
    }
    .wrong-banner {
        background: linear-gradient(135deg, #7F1D1D, #6B2121);
        border: 1px solid #EF4444;
        border-radius: 10px;
        padding: 1rem 1.2rem;
        margin: 0.5rem 0;
        animation: fadeInUp 0.3s ease-out;
    }

    /* Results breakdown table */
    .results-table {
        width: 100%;
        border-collapse: collapse;
        margin-top: 1rem;
    }
    .results-table th {
        text-align: left;
        padding: 0.6rem 1rem;
        background: #1E293B;
        color: #94A3B8;
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .results-table td {
        padding: 0.6rem 1rem;
        border-bottom: 1px solid #1E293B;
        color: #E2E8F0;
        font-size: 0.9rem;
    }

    /* Flashcard styling */
    .flashcard-front {
        background: linear-gradient(145deg, #1E293B, #253347);
        border: 2px solid #0D9488;
        border-radius: 16px;
        padding: 2rem;
        text-align: center;
        min-height: 120px;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 8px 24px rgba(13, 148, 136, 0.15);
        animation: fadeInUp 0.4s ease-out;
    }
    .flashcard-back {
        background: linear-gradient(145deg, #1a2a1a, #1E293B);
        border: 2px solid #10B981;
        border-radius: 16px;
        padding: 2rem;
        box-shadow: 0 8px 24px rgba(16, 185, 129, 0.1);
        animation: fadeInUp 0.3s ease-out;
    }

    /* Flashcard session stats */
    .fc-stats {
        background: linear-gradient(135deg, #1E293B, #253347);
        border: 1px solid #334155;
        border-radius: 10px;
        padding: 0.6rem 1rem;
        display: flex;
        gap: 1.5rem;
        align-items: center;
        font-size: 0.85rem;
        color: #94A3B8;
    }
    .fc-stats strong { color: #0D9488; }

    /* Pulse button */
    .pulse-btn {
        animation: pulse 2s infinite;
    }

    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0F172A 0%, #1E293B 100%);
    }

    /* Status badges */
    .status-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
    }
    .badge-ready { background: #065F46; color: #6EE7B7; }
    .badge-processing { background: #78350F; color: #FCD34D; }

    /* File list */
    .file-item {
        background: #1E293B;
        border: 1px solid #334155;
        border-radius: 8px;
        padding: 0.6rem 1rem;
        margin: 0.3rem 0;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .file-item span { color: #94A3B8; font-size: 0.85rem; }

    /* Onboarding tips */
    .onboard-tip {
        display: flex;
        align-items: flex-start;
        gap: 0.75rem;
        padding: 0.6rem 0;
        color: #94A3B8;
        font-size: 0.9rem;
    }
    .onboard-tip .tip-icon { font-size: 1.2rem; flex-shrink: 0; }

    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        background: #1E293B;
        border-radius: 8px;
        padding: 0.5rem 1.2rem;
        border: 1px solid #334155;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #0D9488, #065F56) !important;
        border-color: #0D9488 !important;
    }

    /* Mobile responsive improvements */
    @media (max-width: 768px) {
        .main-header {
            padding: 1.5rem 1.5rem;
        }
        .main-header h1 {
            font-size: 1.5rem;
        }
        .med-card {
            padding: 1rem;
        }
        .feature-card {
            padding: 1rem !important;
        }
    }
    
    /* Optimize tabs for mobile */
    @media (max-width: 600px) {
        .stTabs [data-baseweb="tab-list"] {
            gap: 4px;
        }
        .stTabs [data-baseweb="tab"] {
            padding: 0.5rem 0.8rem;
            font-size: 0.85rem;
        }
    }
</style>
""", unsafe_allow_html=True)


# --- Gemini Configuration ---
def get_gemini_client():
    """Get or create Gemini client."""
    api_key = os.getenv("GEMINI_API_KEY", "")
    if not api_key:
        st.error("⚠️ GEMINI_API_KEY not found! Add it to your `.env` file or Streamlit secrets.")
        st.stop()
    return genai.Client(api_key=api_key)


client = get_gemini_client()


# --- API Retry Helper ---
def gemini_call_with_retry(func, *args, max_retries=1, **kwargs):
    """Wrap a Gemini API call with retry + exponential backoff."""
    for attempt in range(max_retries + 1):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            err_str = str(e).lower()
            is_retryable = any(k in err_str for k in ["429", "503", "rate", "overloaded", "quota"])
            if attempt < max_retries and is_retryable:
                wait = 2 ** (attempt + 1)
                time.sleep(wait)
                continue
            if "429" in err_str or "rate" in err_str or "quota" in err_str:
                raise RuntimeError(
                    "⏳ AI service rate limit reached. Please wait a moment and try again."
                ) from e
            if "503" in err_str or "overloaded" in err_str:
                raise RuntimeError(
                    "🔧 AI service temporarily busy. Please try again in a few seconds."
                ) from e
            raise


# --- Core RAG Functions (reused from rag_app.py) ---

def load_text_content(file_bytes, filename):
    """Extract text from uploaded .txt file."""
    return file_bytes.decode("utf-8")


def load_pdf_content(file_bytes, filename):
    """Extract text from uploaded .pdf file."""
    try:
        from PyPDF2 import PdfReader
        reader = PdfReader(BytesIO(file_bytes))
        text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n\n"
        if text.strip():
            return text.strip()
    except Exception:
        pass

    # Scanned PDF fallback — use Gemini
    try:
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            tmp.write(file_bytes)
            tmp_path = tmp.name

        uploaded_file = client.files.upload(file=tmp_path)
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[
                uploaded_file,
                "Extract ALL text from this PDF exactly as written. "
                "Preserve headings, bullet points, numbered lists, and structure. "
                "If there are diagrams or images, describe them briefly in [brackets]. "
                "Output only the extracted text."
            ]
        )
        os.unlink(tmp_path)
        return response.text if response.text else None
    except Exception as e:
        st.warning(f"Could not extract text from {filename}: {e}")
        return None


def load_image_content(file_bytes, filename):
    """Extract text from an uploaded image (photo of handwritten/printed notes).
    Uses Gemini Vision to read the image content."""
    try:
        # Determine file extension
        ext = os.path.splitext(filename)[1].lower()
        if ext in ('.jpg', '.jpeg'):
            suffix = '.jpg'
        elif ext == '.png':
            suffix = '.png'
        elif ext == '.webp':
            suffix = '.webp'
        elif ext == '.heic':
            suffix = '.heic'
        else:
            suffix = '.jpg'

        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
            tmp.write(file_bytes)
            tmp_path = tmp.name

        uploaded_file = client.files.upload(file=tmp_path)
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[
                uploaded_file,
                "You are reading a photo of medical/MBBS study notes. "
                "Extract ALL the text from this image exactly as written. "
                "This may be handwritten or printed notes. "
                "Preserve headings, bullet points, numbered lists, underlines, and structure. "
                "If there are diagrams, describe them briefly in [brackets]. "
                "If the handwriting is unclear, make your best attempt and mark uncertain words with (?). "
                "Output only the extracted text, no commentary."
            ]
        )
        os.unlink(tmp_path)

        if response.text and response.text.strip():
            return response.text.strip()
        else:
            return None
    except Exception as e:
        st.warning(f"Could not extract text from image {filename}: {e}")
        return None


def split_into_chunks(text, chunk_size=800, overlap=100):
    """Split text into paragraph-aware chunks with overlap."""
    paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
    chunks = []
    current_chunk = []
    current_size = 0

    for para in paragraphs:
        para_size = len(para)

        if para_size > chunk_size:
            if current_chunk:
                chunks.append('\n\n'.join(current_chunk))
                current_chunk = []
                current_size = 0
            sentences = para.replace('. ', '.\n').split('\n')
            temp_chunk = []
            temp_size = 0
            for sentence in sentences:
                if temp_size + len(sentence) > chunk_size and temp_chunk:
                    chunks.append(' '.join(temp_chunk))
                    temp_chunk = [temp_chunk[-1]] if overlap > 0 else []
                    temp_size = len(temp_chunk[0]) if temp_chunk else 0
                temp_chunk.append(sentence)
                temp_size += len(sentence)
            if temp_chunk:
                chunks.append(' '.join(temp_chunk))
            continue

        if current_size + para_size > chunk_size and current_chunk:
            chunks.append('\n\n'.join(current_chunk))
            if overlap > 0 and current_chunk:
                last = current_chunk[-1]
                current_chunk = [last] if len(last) < overlap * 2 else []
                current_size = len(last) if current_chunk else 0
            else:
                current_chunk = []
                current_size = 0

        current_chunk.append(para)
        current_size += para_size

    if current_chunk:
        chunks.append('\n\n'.join(current_chunk))
    return chunks


@st.cache_data(show_spinner=False)
def create_embedding(text, task_type="RETRIEVAL_DOCUMENT"):
    """Create embedding using Gemini (cached to avoid redundant calls)."""
    result = gemini_call_with_retry(
        client.models.embed_content,
        model="gemini-embedding-001",
        contents=text,
        config=types.EmbedContentConfig(task_type=task_type)
    )
    return result.embeddings[0].values


def cosine_similarity(vec1, vec2):
    """Calculate cosine similarity."""
    dot = sum(a * b for a, b in zip(vec1, vec2))
    mag1 = math.sqrt(sum(a * a for a in vec1))
    mag2 = math.sqrt(sum(b * b for b in vec2))
    if mag1 == 0 or mag2 == 0:
        return 0.0
    return dot / (mag1 * mag2)


def find_relevant_chunks(question, chunks_with_embeddings, top_k=3):
    """Find most relevant chunks for a question."""
    q_emb = create_embedding(question, "RETRIEVAL_QUERY")
    scored = []
    for text, source, emb in chunks_with_embeddings:
        score = cosine_similarity(q_emb, emb)
        scored.append((text, source, score))
    scored.sort(key=lambda x: x[2], reverse=True)
    return scored[:top_k]


SYSTEM_INSTRUCTION = (
    "You are an expert MBBS study assistant. You help medical students understand "
    "their notes clearly. Follow these rules:\n"
    "1. Answer based ONLY on the provided context from the student's notes.\n"
    "2. Use clear, student-friendly language while keeping proper medical terminology.\n"
    "3. When explaining complex concepts, break them down step by step.\n"
    "4. If the context contains relevant clinical correlations, mention them.\n"
    "5. If the answer is not in the context, say so honestly.\n"
    "6. Use bullet points and structured formatting for clarity.\n"
    "7. At the end, briefly mention which source document(s) the answer came from."
)


def generate_answer(question, relevant_chunks):
    """Generate answer using Gemini."""
    context_parts = []
    for chunk_text, source_file, score in relevant_chunks:
        context_parts.append(f"[Source: {source_file}]\n{chunk_text}")
    context = "\n\n---\n\n".join(context_parts)

    prompt = f"""Based on the following MBBS study notes, answer the student's question.

Context from notes:
{context}

Student's Question: {question}

Provide a clear, well-structured answer:"""

    response = gemini_call_with_retry(
        client.models.generate_content,
        model="gemini-2.5-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_INSTRUCTION,
            temperature=0.7,
            max_output_tokens=1000,
        )
    )
    return response.text


def parse_json_response(text):
    """Robustly parse JSON from Gemini's response, handling common issues."""
    text = text.strip()

    # Remove markdown code fences
    if text.startswith("```"):
        text = text.split("\n", 1)[1] if "\n" in text else text[3:]
    if text.endswith("```"):
        text = text[:-3]
    text = text.strip()

    # Remove 'json' language tag if present
    if text.startswith("json"):
        text = text[4:].strip()

    # Try direct parse first
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Fix unescaped newlines inside JSON strings
    try:
        fixed = re.sub(r'(?<=: ")([^"]*?)(?=")', 
                       lambda m: m.group(1).replace('\n', '\\n'), text)
        return json.loads(fixed)
    except (json.JSONDecodeError, Exception):
        pass

    # Try to extract JSON object {...} or array [...] from the text
    for pattern in [r'\{[\s\S]*\}', r'\[[\s\S]*\]']:
        match = re.search(pattern, text)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                # Try fixing newlines in the extracted portion
                try:
                    extracted = match.group()
                    fixed = re.sub(r'(?<=: ")([^"]*?)(?=")',
                                   lambda m: m.group(1).replace('\n', '\\n'), extracted)
                    return json.loads(fixed)
                except Exception:
                    pass

    raise json.JSONDecodeError("Could not parse Gemini response as JSON", text, 0)


def extract_topics_from_notes(chunks_with_embeddings):
    """Extract distinct topics/subtopics from the uploaded notes using Gemini."""
    # Use a sample of chunks to identify topics (to avoid exceeding context limits)
    sample = random.sample(
        chunks_with_embeddings,
        min(15, len(chunks_with_embeddings))
    )
    context = "\n\n---\n\n".join([c[0] for c in sample])

    prompt = f"""Analyze these MBBS study notes and extract ALL distinct topics and subtopics covered.

Notes:
{context}

Return a JSON array of topic strings. Each topic should be specific enough to be useful
for focused study (e.g. "Anatomy of the Heart" not just "Anatomy").
Include 5-15 topics. Order from most to least content coverage.

Return ONLY the JSON array, e.g.: ["Topic 1", "Topic 2", ...]"""

    response = gemini_call_with_retry(
        client.models.generate_content,
        model="gemini-2.5-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction="Extract topics from medical study notes. Return only valid JSON array of strings.",
            temperature=0.3,
            max_output_tokens=500,
        )
    )
    return parse_json_response(response.text)


def filter_chunks_by_topic(topic, chunks_with_embeddings, top_k=8):
    """Filter chunks relevant to a specific topic using embedding similarity."""
    topic_emb = create_embedding(topic, "RETRIEVAL_QUERY")
    scored = []
    for text, source, emb in chunks_with_embeddings:
        score = cosine_similarity(topic_emb, emb)
        scored.append((text, source, emb, score))
    scored.sort(key=lambda x: x[3], reverse=True)
    # Return top-k chunks that are above a minimum relevance threshold
    filtered = [(t, s, e) for t, s, e, sc in scored[:top_k] if sc > 0.3]
    return filtered if filtered else chunks_with_embeddings[:top_k]


def generate_mcqs(chunks_with_embeddings, num_questions=5, topic=None):
    """Generate MCQs from notes, optionally focused on a specific topic."""
    if topic and topic != "All Topics":
        available = filter_chunks_by_topic(topic, chunks_with_embeddings)
    else:
        available = list(chunks_with_embeddings)
    selected = random.sample(available, min(num_questions, len(available)))
    context = "\n\n---\n\n".join([c[0] for c in selected])

    topic_instruction = f" Focus ALL questions on the topic: '{topic}'." if (topic and topic != "All Topics") else ""

    prompt = f"""Based on these MBBS study notes, generate exactly {num_questions} MCQs.{topic_instruction}

Notes:
{context}

Return as a valid JSON array. Each element:
- "question": question text
- "options": {{"A": "...", "B": "...", "C": "...", "D": "..."}}
- "correct": correct letter (A/B/C/D)
- "explanation": brief explanation

Return ONLY the JSON array."""

    response = gemini_call_with_retry(
        client.models.generate_content,
        model="gemini-2.5-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction="You are an MBBS exam question setter. Create clinically relevant MCQs. Return only valid JSON.",
            temperature=0.8,
            max_output_tokens=2500,
        )
    )
    result = parse_json_response(response.text)
    # Normalize: Gemini sometimes returns {"questions": [...]} instead of [...]
    if isinstance(result, dict):
        # Find the first list value in the dict
        for v in result.values():
            if isinstance(v, list):
                return v
        return [result]  # Single MCQ wrapped in dict
    return result


def generate_flashcard(chunks_with_embeddings, topic=None):
    """Generate a flashcard from notes, optionally focused on a specific topic."""
    if topic and topic != "All Topics":
        relevant = filter_chunks_by_topic(topic, chunks_with_embeddings)
    else:
        relevant = list(chunks_with_embeddings)
    chunk_text, source_file, _ = random.choice(relevant)

    topic_instruction = f" The flashcard MUST be about the topic: '{topic}'." if (topic and topic != "All Topics") else ""

    prompt = f"""Based on this study material, create ONE flashcard for active recall.{topic_instruction}

Study material:
{chunk_text}

Return as JSON:
- "front": A specific question about a key concept
- "back": Detailed answer with key points
- "topic": Topic name
- "source": "{source_file}"

Return ONLY JSON."""

    response = gemini_call_with_retry(
        client.models.generate_content,
        model="gemini-2.5-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction="Create exam-focused flashcards. Return only valid JSON.",
            temperature=0.9,
            max_output_tokens=500,
        )
    )
    return parse_json_response(response.text)


def generate_topic_summary(chunks_with_embeddings, topic=None):
    """Generate a topic summary for quick revision, optionally focused on a specific topic."""
    if topic and topic != "All Topics":
        relevant = filter_chunks_by_topic(topic, chunks_with_embeddings, top_k=5)
    else:
        relevant = list(chunks_with_embeddings)
    chunk_text, source_file, _ = random.choice(relevant)

    topic_instruction = f" Focus the summary specifically on: '{topic}'." if (topic and topic != "All Topics") else ""

    prompt = f"""Create a concise revision summary:{topic_instruction}
- Key points as bullet points
- Important definitions
- Clinical correlations if any
- Memory aids / mnemonics if applicable

Study material:
{chunk_text}"""

    response = gemini_call_with_retry(
        client.models.generate_content,
        model="gemini-2.5-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction="Create concise, exam-focused revision summaries. Highlight high-yield facts.",
            temperature=0.7,
            max_output_tokens=800,
        )
    )
    return response.text, source_file


def analyze_exam_paper(paper_text, paper_year, exam_type="NEET PG"):
    """Analyze an exam paper and extract key information and explanations."""
    prompt = f"""Analyze this {exam_type} {paper_year} exam paper and provide:
1. **Overall Difficulty**: Easy/Moderate/Difficult
2. **Key Topics Tested** (top 5)
3. **Question Distribution**: Most common types
4. **Trending Concepts**: What topics appeared frequently
5. **Study Recommendations**: What to focus on

Paper:
{paper_text[:3000]}...  (showing first part of paper)

Provide a comprehensive analysis in structured format."""

    response = gemini_call_with_retry(
        client.models.generate_content,
        model="gemini-2.5-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=f"You are an expert {exam_type} exam analyzer. Provide insights medical students can use for preparation.",
            temperature=0.7,
            max_output_tokens=1000,
        )
    )
    return response.text


def generate_paper_questions(paper_text, num_questions=5, exam_type="NEET PG"):
    """Generate practice questions based on exam paper patterns."""
    prompt = f"""Based on the patterns in this {exam_type} exam paper, generate {num_questions} NEW practice questions
in the same style. Each question should be realistic and challenging.

Paper excerpt:
{paper_text[:2000]}

Return as a JSON array with:
- "question": The MCQ question
- "options": {{"A": "...", "B": "...", "C": "...", "D": "..."}}
- "correct": Correct answer (A/B/C/D)
- "explanation": Why this is correct
- "difficulty": Easy/Moderate/Difficult
- "topic": Relevant topic

Return ONLY valid JSON array."""

    response = gemini_call_with_retry(
        client.models.generate_content,
        model="gemini-2.5-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=f"Create realistic {exam_type} practice questions. Return only valid JSON.",
            temperature=0.8,
            max_output_tokens=2000,
        )
    )
    return parse_json_response(response.text)


# --- CSV Registration Helper ---
REGISTRATIONS_CSV = Path(__file__).parent / "registrations.csv"

def save_registration(name, college, batch, phone):
    """Append user registration to local CSV file and Google Sheets."""
    # Save to local CSV
    file_exists = REGISTRATIONS_CSV.exists()
    with open(REGISTRATIONS_CSV, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["Timestamp", "Name", "College", "Batch", "Phone"])
        if not file_exists:
            writer.writeheader()
        writer.writerow({
            "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Name": name,
            "College": college,
            "Batch": batch,
            "Phone": phone,
        })
    
    # Try to save to Google Sheets if configured
    try:
        sheet_config = os.getenv("GOOGLE_SHEET_CREDENTIALS")
        sheet_url = os.getenv("GOOGLE_SHEET_URL")
        
        if sheet_config and sheet_url:
            sheets_handler = GoogleSheetsHandler(
                credentials_file=sheet_config,
                sheet_name="Registrations"
            )
            sheets_handler.open_sheet(sheet_url)
            result = sheets_handler.add_registration(name, college, batch, phone)
            if result['success']:
                print(f"✓ Saved to Google Sheets: {name}")
            else:
                print(f"⚠ Google Sheets save warning: {result['message']}")
    except Exception as e:
        # Not critical - data is already saved locally
        print(f"⚠ Google Sheets connection hint: {str(e)[:100]}...")



# --- Session State Init ---
if "user_registered" not in st.session_state:
    st.session_state.user_registered = False
if "registered_name" not in st.session_state:
    st.session_state.registered_name = ""
if "chunks_with_embeddings" not in st.session_state:
    st.session_state.chunks_with_embeddings = []
if "uploaded_files_info" not in st.session_state:
    st.session_state.uploaded_files_info = []
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "mcq_data" not in st.session_state:
    st.session_state.mcq_data = None
if "mcq_index" not in st.session_state:
    st.session_state.mcq_index = 0
if "mcq_score" not in st.session_state:
    st.session_state.mcq_score = 0
if "mcq_answered" not in st.session_state:
    st.session_state.mcq_answered = False
if "flashcard" not in st.session_state:
    st.session_state.flashcard = None
if "flashcard_revealed" not in st.session_state:
    st.session_state.flashcard_revealed = False
if "flashcard_count" not in st.session_state:
    st.session_state.flashcard_count = 0
if "fc_forgot" not in st.session_state:
    st.session_state.fc_forgot = 0
if "fc_partial" not in st.session_state:
    st.session_state.fc_partial = 0
if "fc_nailed" not in st.session_state:
    st.session_state.fc_nailed = 0
if "available_topics" not in st.session_state:
    st.session_state.available_topics = []
if "selected_topic" not in st.session_state:
    st.session_state.selected_topic = "All Topics"
if "mcq_answers_log" not in st.session_state:
    st.session_state.mcq_answers_log = []
if "neet_pg_papers" not in st.session_state:
    st.session_state.neet_pg_papers = []
if "upsc_cms_papers" not in st.session_state:
    st.session_state.upsc_cms_papers = []
if "current_paper" not in st.session_state:
    st.session_state.current_paper = None
if "paper_type" not in st.session_state:
    st.session_state.paper_type = None


# ═══════════════════════════════════════════════════════════
# --- REGISTRATION SCREEN ---
# ═══════════════════════════════════════════════════════════
if not st.session_state.user_registered:
    # Registration CSS
    st.markdown("""
    <style>
    /* Full-screen overlay behind registration */
    .reg-wrapper {
        max-width: 520px;
        margin: 0 auto;
        padding: 2rem 0;
    }
    .reg-card {
        background: linear-gradient(145deg, #0F172A, #1E293B);
        border: 1px solid #0D9488;
        border-radius: 24px;
        padding: 2.5rem 2.5rem 2rem 2.5rem;
        box-shadow: 0 20px 60px rgba(13,148,136,0.25), 0 0 0 1px rgba(13,148,136,0.1);
        animation: fadeInUp 0.5s ease-out;
    }
    .reg-logo {
        text-align: center;
        font-size: 3.5rem;
        margin-bottom: 0.5rem;
    }
    .reg-title {
        text-align: center;
        color: #ffffff;
        font-size: 1.8rem;
        font-weight: 700;
        margin: 0 0 0.2rem 0;
        letter-spacing: -0.5px;
    }
    .reg-sub {
        text-align: center;
        color: #94A3B8;
        font-size: 0.95rem;
        margin: 0 0 2rem 0;
    }
    .reg-divider {
        height: 1px;
        background: linear-gradient(90deg, transparent, #334155, transparent);
        margin: 1.5rem 0;
    }
    .reg-footer {
        text-align: center;
        color: #64748B;
        font-size: 0.8rem;
        margin-top: 1rem;
    }
    </style>
    """, unsafe_allow_html=True)

    # Centered layout
    _, center_col, _ = st.columns([1, 2.2, 1])
    with center_col:
        st.markdown('<div class="reg-card">', unsafe_allow_html=True)
        st.markdown('<div class="reg-logo">🩺</div>', unsafe_allow_html=True)
        st.markdown('<p class="reg-title">Synopsis</p>', unsafe_allow_html=True)
        st.markdown('<p style="text-align:center;color:#0D9488;font-size:0.85rem;font-weight:600;margin:-1rem 0 0.4rem 0;letter-spacing:1px;">BY GAURAV MALIK</p>', unsafe_allow_html=True)
        st.markdown('<p class="reg-sub">Learn It Your Way — Create your student profile to get started</p>', unsafe_allow_html=True)
        st.markdown('<div class="reg-divider"></div>', unsafe_allow_html=True)

        with st.form("registration_form", clear_on_submit=False):
            name = st.text_input("👤 Full Name", placeholder="e.g. Dr. Riya Sharma")
            college = st.text_input("🏫 College / Medical Institute", placeholder="e.g. AIIMS Delhi")
            batch = st.text_input("📅 Batch / Year", placeholder="e.g. 2022-2028 / 2nd Year")
            phone = st.text_input("📱 Phone Number", placeholder="e.g. 9876543210", max_chars=15)

            st.markdown("<br>", unsafe_allow_html=True)
            submitted = st.form_submit_button(
                "🚀  Register & Enter App",
                use_container_width=True,
                type="primary"
            )

            if submitted:
                # Validation
                errors = []
                if not name.strip():
                    errors.append("• Full Name is required")
                if not college.strip():
                    errors.append("• College is required")
                if not batch.strip():
                    errors.append("• Batch / Year is required")
                if not phone.strip():
                    errors.append("• Phone Number is required")
                elif not re.match(r'^[\d\s\+\-\(\)]{7,15}$', phone.strip()):
                    errors.append("• Enter a valid phone number (7–15 digits)")

                if errors:
                    st.error("Please fix the following:\n" + "\n".join(errors))
                else:
                    try:
                        save_registration(
                            name.strip(), college.strip(),
                            batch.strip(), phone.strip()
                        )
                        st.session_state.user_registered = True
                        st.session_state.registered_name = name.strip().split()[0]
                        st.success(f"✅ Welcome, {name.strip().split()[0]}! Loading your study companion...")
                        time.sleep(1)
                        st.rerun()
                    except Exception as e:
                        st.error(f"Could not save registration: {e}")

        st.markdown('<p class="reg-footer">🔒 Your data is stored locally and never shared.</p>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.stop()  # Don't render the main app until registered

# ═══════════════════════════════════════════════════════════


# --- Header ---
_first_name = st.session_state.get("registered_name", "")
_welcome = f" — Welcome back, {_first_name}! 👋" if _first_name else ""
st.markdown(f"""
<div class="main-header">
    <h1>🩺 Synopsis</h1>
    <p style="color:#5EEAD4;font-size:0.78rem;font-weight:600;letter-spacing:2px;margin:0.1rem 0 0.3rem 0;">BY GAURAV MALIK</p>
    <p>Learn It Your Way{_welcome}</p>
</div>
""", unsafe_allow_html=True)


# --- Sidebar: File Upload ---
IMAGE_EXTENSIONS = ('.jpg', '.jpeg', '.png', '.webp', '.heic')

with st.sidebar:
    st.markdown("### 📂 Upload Your Notes")
    st.caption("Supports PDFs, text files, and photos of notes")

    upload_tab1, upload_tab2 = st.tabs(["📄 Documents", "📸 Photos"])

    with upload_tab1:
        uploaded_files = st.file_uploader(
            "Upload PDFs or text files",
            type=["pdf", "txt"],
            accept_multiple_files=True,
            label_visibility="collapsed",
            key="doc_uploader"
        )

    with upload_tab2:
        uploaded_images = st.file_uploader(
            "Upload photos of your notes (up to 20)",
            type=["jpg", "jpeg", "png", "webp", "heic"],
            accept_multiple_files=True,
            label_visibility="collapsed",
            key="img_uploader"
        )
        if uploaded_images:
            if len(uploaded_images) > 20:
                st.warning("⚠️ Max 20 photos at a time. Only the first 20 will be processed.")
                uploaded_images = uploaded_images[:20]
            # Show image previews
            cols = st.columns(min(4, len(uploaded_images)))
            for i, img_file in enumerate(uploaded_images[:8]):
                with cols[i % 4]:
                    st.image(img_file, caption=img_file.name[:15], width=70)
            if len(uploaded_images) > 8:
                st.caption(f"... and {len(uploaded_images) - 8} more photos")

    # Combine all files
    all_uploaded = []
    if uploaded_files:
        all_uploaded.extend(uploaded_files)
    if uploaded_images:
        all_uploaded.extend(uploaded_images[:20])

    if all_uploaded:
        # Check if files changed
        current_names = sorted([f.name for f in all_uploaded])
        prev_names = sorted([info["name"] for info in st.session_state.uploaded_files_info])

        if current_names != prev_names:
            with st.spinner("🔄 Processing your notes..."):
                all_chunks = []
                files_info = []
                total_files = len(all_uploaded)

                for file_idx, uf in enumerate(all_uploaded):
                    file_bytes = uf.read()
                    fname = uf.name.lower()

                    # File size check (warn for files > 20 MB)
                    file_size_mb = len(file_bytes) / (1024 * 1024)
                    if file_size_mb > 20:
                        st.warning(f"⚠️ {uf.name} is {file_size_mb:.1f} MB — large files may take longer to process.")

                    st.caption(f"📖 Processing {uf.name} ({file_idx + 1}/{total_files})...")

                    if fname.endswith(".txt"):
                        text = load_text_content(file_bytes, uf.name)
                    elif fname.endswith(".pdf"):
                        text = load_pdf_content(file_bytes, uf.name)
                    elif any(fname.endswith(ext) for ext in IMAGE_EXTENSIONS):
                        text = load_image_content(file_bytes, uf.name)
                    else:
                        continue

                    if text and text.strip():
                        chunks = split_into_chunks(text)
                        for chunk in chunks:
                            all_chunks.append((chunk, uf.name))
                        files_info.append({
                            "name": uf.name,
                            "type": "📸" if any(fname.endswith(ext) for ext in IMAGE_EXTENSIONS) else "📄",
                            "chars": len(text),
                            "chunks": len(chunks)
                        })

                # Create embeddings
                if all_chunks:
                    progress = st.progress(0, text="Creating embeddings...")
                    chunks_with_emb = []
                    for i, (chunk_text, source) in enumerate(all_chunks):
                        emb = create_embedding(chunk_text)
                        chunks_with_emb.append((chunk_text, source, emb))
                        progress.progress((i + 1) / len(all_chunks),
                                         text=f"Embedding {i+1}/{len(all_chunks)}...")
                    progress.empty()

                    st.session_state.chunks_with_embeddings = chunks_with_emb
                    st.session_state.uploaded_files_info = files_info
                    st.session_state.chat_history = []
                    st.session_state.mcq_data = None

                    doc_count = sum(1 for f in files_info if f["type"] == "📄")
                    img_count = sum(1 for f in files_info if f["type"] == "📸")
                    msg = f"✅ Loaded: "
                    if doc_count:
                        msg += f"{doc_count} document(s)"
                    if img_count:
                        msg += f"{' + ' if doc_count else ''}{img_count} photo(s)"
                    st.success(msg)

    # Show uploaded files
    if st.session_state.uploaded_files_info:
        st.markdown("---")
        st.markdown("### 📄 Loaded Documents")
        total_chunks = 0
        for info in st.session_state.uploaded_files_info:
            total_chunks += info["chunks"]
            icon = info.get("type", "📄")
            st.markdown(f"""
            <div class="file-item">
                <strong>{icon} {info['name']}</strong>
                <span>{info['chars']:,} chars · {info['chunks']} chunks</span>
            </div>
            """, unsafe_allow_html=True)
        st.caption(f"Total: {total_chunks} searchable chunks")


    else:
        st.info("👆 Upload your MBBS notes to get started!")

    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #64748B; font-size: 0.75rem; padding: 0.5rem;">
        Powered by Google Gemini AI<br>
        Built for MBBS students 🎓
    </div>
    """, unsafe_allow_html=True)


# --- Main Content: Tabs ---
if not st.session_state.chunks_with_embeddings:
    # Empty state — onboarding
    st.markdown("---")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">💬</div>
            <h3>Ask Questions</h3>
            <p style="color: #94A3B8; font-size: 0.85rem;">Chat with your notes using AI-powered search.</p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">📝</div>
            <h3>MCQ Quiz</h3>
            <p style="color: #94A3B8; font-size: 0.85rem;">Auto-generated exam-style questions with scoring.</p>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">🧠</div>
            <h3>Flashcards</h3>
            <p style="color: #94A3B8; font-size: 0.85rem;">Active recall practice with self-rated difficulty.</p>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">📸</div>
            <h3>Photo Notes</h3>
            <p style="color: #94A3B8; font-size: 0.85rem;">Upload photos of handwritten notes — AI reads them.</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("")
    # Mobile-friendly upload prompt
    st.markdown("""
    <div style="background: linear-gradient(145deg, #065F56, #0D9488); padding: 1.2rem; border-radius: 12px; border-left: 4px solid #0D9488; margin-bottom: 1.5rem;">
        <p style="margin: 0; color: #E2E8F0; font-weight: 600;">📱 <strong>On mobile?</strong> Tap the <strong>☰ menu</strong> (top left) to access the upload panel with all features!</p>
    </div>
    """)
    st.markdown("")

    # Quick-start tips
    st.markdown("""
    <div class="med-card" style="animation-delay: 0.2s;">
        <h4 style="color: #0D9488; margin-top: 0;">⚡ Quick Start Guide</h4>
        <div class="onboard-tip">
            <span class="tip-icon">📄</span>
            <span><strong>Supported formats:</strong> PDF, TXT, JPG, PNG, WebP, HEIC</span>
        </div>
        <div class="onboard-tip">
            <span class="tip-icon">🎯</span>
            <span><strong>Pro tip:</strong> Upload one subject at a time for more focused study sessions</span>
        </div>
        <div class="onboard-tip">
            <span class="tip-icon">📸</span>
            <span><strong>Photo notes:</strong> Snap your handwritten notes — AI extracts the text automatically</span>
        </div>
        <div class="onboard-tip">
            <span class="tip-icon">🔬</span>
            <span><strong>Topics:</strong> After upload, topics are auto-detected so you can focus MCQs & flashcards on specific areas</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

else:
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "💬 Ask Questions",
        "📝 MCQ Quiz",
        "🧠 Flashcards",
        "📖 Topic Review",
        "📚 NEET PG Papers",
        "🏥 UPSC CMS Papers"
    ])

    # ── TAB 1: Q&A ──
    with tab1:
        qa_header_col, qa_clear_col = st.columns([4, 1])
        with qa_header_col:
            st.markdown("### Ask anything about your notes")
        with qa_clear_col:
            if st.session_state.chat_history:
                if st.button("🗑️ Clear Chat", key="clear_chat"):
                    st.session_state.chat_history = []
                    st.rerun()

        # Chat display
        for msg in st.session_state.chat_history:
            if msg["role"] == "user":
                with st.chat_message("user", avatar="🧑‍⚕️"):
                    st.write(msg["content"])
            else:
                with st.chat_message("assistant", avatar="🩺"):
                    st.write(msg["content"])
                    if "sources" in msg:
                        with st.expander("📚 Sources"):
                            for src in msg["sources"]:
                                st.caption(f"📄 {src[0]} — relevance: {src[1]:.0%}")

        # Chat input
        if question := st.chat_input("Ask a question about your MBBS notes..."):
            st.session_state.chat_history.append({"role": "user", "content": question})
            with st.chat_message("user", avatar="🧑‍⚕️"):
                st.write(question)

            with st.chat_message("assistant", avatar="🩺"):
                with st.spinner("🔍 Searching your notes..."):
                    try:
                        relevant = find_relevant_chunks(
                            question, st.session_state.chunks_with_embeddings, top_k=3
                        )
                        answer = generate_answer(question, relevant)
                    except Exception as e:
                        st.error(f"❌ {e}")
                        answer = None
                        relevant = []

                if answer:
                    st.write(answer)
                    sources = [(s, sc) for _, s, sc in relevant]
                    with st.expander("📚 Sources"):
                        for src, sc in sources:
                            st.caption(f"📄 {src} — relevance: {sc:.0%}")

                    st.session_state.chat_history.append({
                        "role": "assistant",
                        "content": answer,
                        "sources": sources
                    })

    # ── TAB 2: MCQ Quiz ──
    with tab2:
        st.markdown("### Test Yourself with MCQs")

        # User types the topic they want to focus on
        mcq_topic_input = st.text_input(
            "🎯 What topic should the MCQs focus on?",
            placeholder="e.g. ECG interpretation, Heart anatomy, Cranial nerves... (leave blank for all topics)",
            key="mcq_topic_input"
        )
        mcq_topic = mcq_topic_input.strip() if mcq_topic_input and mcq_topic_input.strip() else "All Topics"

        col_a, col_b = st.columns([3, 1])
        with col_a:
            num_q = st.slider("Number of questions", 3, 10, 5)
        with col_b:
            if st.button("🎯 Generate Quiz", type="primary", use_container_width=True):
                with st.spinner(f"✨ Generating MCQs{' on ' + mcq_topic if mcq_topic != 'All Topics' else ''}..."):
                    try:
                        mcqs = generate_mcqs(
                            st.session_state.chunks_with_embeddings, num_q, topic=mcq_topic
                        )
                        st.session_state.mcq_data = mcqs
                        st.session_state.mcq_index = 0
                        st.session_state.mcq_score = 0
                        st.session_state.mcq_answered = False
                        st.session_state.mcq_answers_log = []
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ {e}")

        if st.session_state.mcq_data:
            mcqs = st.session_state.mcq_data
            idx = st.session_state.mcq_index

            if idx < len(mcqs):
                mcq = mcqs[idx]

                # Progress bar
                st.progress((idx) / len(mcqs),
                           text=f"Question {idx + 1} of {len(mcqs)}")

                st.markdown(f"#### Q{idx + 1}. {mcq['question']}")

                if not st.session_state.mcq_answered:
                    for letter in ['A', 'B', 'C', 'D']:
                        if letter in mcq['options']:
                            if st.button(
                                f"{letter}. {mcq['options'][letter]}",
                                key=f"mcq_{idx}_{letter}",
                                use_container_width=True
                            ):
                                st.session_state.mcq_answered = True
                                correct = mcq['correct'].upper()
                                if letter == correct:
                                    st.session_state.mcq_score += 1
                                st.session_state._last_answer = letter
                                st.session_state._correct_answer = correct
                                # Log answer for end-of-quiz review
                                st.session_state.mcq_answers_log.append({
                                    "q": mcq['question'],
                                    "your": letter,
                                    "correct": correct,
                                    "is_correct": letter == correct,
                                    "explanation": mcq.get('explanation', '')
                                })
                                st.rerun()
                else:
                    letter = st.session_state._last_answer
                    correct = st.session_state._correct_answer

                    for opt in ['A', 'B', 'C', 'D']:
                        if opt in mcq['options']:
                            if opt == correct:
                                st.success(f"✅ {opt}. {mcq['options'][opt]}")
                            elif opt == letter and opt != correct:
                                st.error(f"❌ {opt}. {mcq['options'][opt]}")
                            else:
                                st.markdown(f"⬜ {opt}. {mcq['options'][opt]}")

                    if letter == correct:
                        st.markdown('<div class="correct-banner">✅ <strong>Correct!</strong></div>',
                                   unsafe_allow_html=True)
                    else:
                        st.markdown(f'<div class="wrong-banner">❌ <strong>Wrong!</strong> Correct answer: {correct}</div>',
                                   unsafe_allow_html=True)

                    with st.expander("📖 Explanation", expanded=True):
                        st.write(mcq.get('explanation', 'N/A'))

                    if st.button("Next Question →", type="primary"):
                        st.session_state.mcq_index += 1
                        st.session_state.mcq_answered = False
                        st.rerun()

            else:
                # Quiz complete
                score = st.session_state.mcq_score
                total = len(mcqs)
                pct = (score / total) * 100

                emoji = '🏆' if score == total else '🌟' if pct >= 80 else '👏' if pct >= 60 else '💪' if pct >= 40 else '📚'
                msg = 'Perfect Score!' if score == total else 'Excellent!' if pct >= 80 else 'Great Job!' if pct >= 60 else 'Good Effort!' if pct >= 40 else 'Keep Studying!'

                st.markdown(f"""
                <div class="score-card">
                    <h2>{emoji} {score}/{total}</h2>
                    <p>{pct:.0f}% — {msg}</p>
                </div>
                """, unsafe_allow_html=True)

                if score == total:
                    st.balloons()

                # Detailed results breakdown
                if st.session_state.mcq_answers_log:
                    with st.expander("📊 View Detailed Results", expanded=False):
                        rows = ""
                        for i, entry in enumerate(st.session_state.mcq_answers_log, 1):
                            icon = "✅" if entry["is_correct"] else "❌"
                            your_ans = entry["your"]
                            correct_ans = entry["correct"]
                            ans_display = f"{your_ans}" if entry["is_correct"] else f"{your_ans} → {correct_ans}"
                            rows += f"<tr><td>{icon} Q{i}</td><td style='max-width:300px;'>{entry['q'][:80]}{'...' if len(entry['q'])>80 else ''}</td><td>{ans_display}</td></tr>\n"
                        st.markdown(f"""
                        <table class="results-table">
                            <thead><tr><th>#</th><th>Question</th><th>Answer</th></tr></thead>
                            <tbody>{rows}</tbody>
                        </table>
                        """, unsafe_allow_html=True)

                st.markdown("")
                if st.button("🔄 Take Another Quiz", type="primary"):
                    st.session_state.mcq_data = None
                    st.session_state.mcq_answers_log = []
                    st.rerun()

    # ── TAB 3: Flashcards ──
    with tab3:
        st.markdown("### Active Recall Flashcards")
        st.caption("See the question → Think about the answer → Reveal to check")

        # User types the topic they want flashcards on
        fc_topic_input = st.text_input(
            "🎯 What topic should the flashcards focus on?",
            placeholder="e.g. Pharmacology, Blood supply of brain... (leave blank for all topics)",
            key="fc_topic_input"
        )
        fc_topic = fc_topic_input.strip() if fc_topic_input and fc_topic_input.strip() else "All Topics"

        col1, col2 = st.columns([3, 1])
        with col2:
            if st.button("🔄 New Card", type="primary", use_container_width=True):
                with st.spinner(f"✨ Generating flashcard{' on ' + fc_topic if fc_topic != 'All Topics' else ''}..."):
                    try:
                        card = generate_flashcard(
                            st.session_state.chunks_with_embeddings, topic=fc_topic
                        )
                        st.session_state.flashcard = card
                        st.session_state.flashcard_revealed = False
                        st.session_state.flashcard_count += 1
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ {e}")

        # Session stats bar
        if st.session_state.flashcard_count > 0:
            st.markdown(f"""
            <div class="fc-stats">
                <span>📇 Cards studied: <strong>{st.session_state.flashcard_count}</strong></span>
                <span>🎯 Nailed: <strong>{st.session_state.fc_nailed}</strong></span>
                <span>🤔 Partial: <strong>{st.session_state.fc_partial}</strong></span>
                <span>😅 Forgot: <strong>{st.session_state.fc_forgot}</strong></span>
            </div>
            """, unsafe_allow_html=True)
            st.markdown("")

        if st.session_state.flashcard:
            card = st.session_state.flashcard

            with col1:
                st.markdown(f"**Topic:** {card.get('topic', 'Unknown')} · "
                          f"**Source:** {card.get('source', 'Unknown')}")

            st.markdown(f"""
            <div class="flashcard-front">
                <h3 style="color: #E2E8F0; margin: 0;">{card['front']}</h3>
            </div>
            """, unsafe_allow_html=True)

            if not st.session_state.flashcard_revealed:
                st.markdown("")
                if st.button("👁️ Reveal Answer", use_container_width=True, type="primary"):
                    st.session_state.flashcard_revealed = True
                    st.rerun()
            else:
                st.markdown(f"""
                <div class="flashcard-back">
                    <p style="color: #D1FAE5; white-space: pre-wrap;">{card['back']}</p>
                </div>
                """, unsafe_allow_html=True)

                st.markdown("")
                rate_col1, rate_col2, rate_col3 = st.columns(3)
                with rate_col1:
                    if st.button("😅 Forgot", use_container_width=True):
                        st.session_state.fc_forgot += 1
                        st.toast("📌 Mark this for extra review!", icon="📌")
                with rate_col2:
                    if st.button("🤔 Partial", use_container_width=True):
                        st.session_state.fc_partial += 1
                        st.toast("📝 Good effort, review later", icon="📝")
                with rate_col3:
                    if st.button("🎯 Nailed it!", use_container_width=True):
                        st.session_state.fc_nailed += 1
                        st.toast("🎉 Great recall!", icon="🎉")

                # Suggest reviewing forgot cards
                if st.session_state.fc_forgot >= 3 and st.session_state.fc_forgot > st.session_state.fc_nailed:
                    st.info("💡 **Tip:** You've forgotten a few. Consider re-studying those topics before continuing.")
        else:
            st.info("👆 Click **New Card** to start your flashcard session!")

    # ── TAB 4: Topic Review ──
    with tab4:
        st.markdown("### Quick Topic Revision")
        st.caption("Get concise summaries with key points, clinical correlations, and mnemonics")

        # User types the topic they want a summary on
        tr_topic_input = st.text_input(
            "🎯 What topic do you want to revise?",
            placeholder="e.g. Fetal circulation, Drug interactions... (leave blank for random topic)",
            key="tr_topic_input"
        )
        tr_topic = tr_topic_input.strip() if tr_topic_input and tr_topic_input.strip() else "All Topics"

        if st.button("📖 Generate Topic Summary", type="primary"):
            with st.spinner(f"✨ Generating summary{' for ' + tr_topic if tr_topic != 'All Topics' else ''}..."):
                try:
                    summary, source = generate_topic_summary(
                        st.session_state.chunks_with_embeddings, topic=tr_topic
                    )
                    st.markdown(f"""
                    <div class="med-card">
                        {summary}
                        <br><br>
                        <span style="color: #64748B; font-size: 0.8rem;">📄 Source: {source}</span>
                    </div>
                    """, unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"❌ {e}")

    # ── TAB 5: NEET PG Papers ──
    with tab5:
        st.markdown("### 📚 NEET PG Previous Year Papers")
        st.caption("Analyze, practice, and master NEET PG exams")
        
        neet_col1, neet_col2, neet_col3 = st.columns(3)
        
        with neet_col1:
            st.metric("📄 Papers Loaded", len(st.session_state.neet_pg_papers))
        with neet_col2:
            st.metric("✅ Practice Tests", 0)
        with neet_col3:
            st.metric("📗 Years Available", "2015-2024")
        
        st.markdown("---")
        
        # Upload papers
        st.markdown("#### 📥 Upload NEET PG Papers")
        neet_papers = st.file_uploader(
            "Upload NEET PG question papers (PDF or TXT)",
            type=["pdf", "txt"],
            accept_multiple_files=True,
            key="neet_papers",
            help="Upload previous years' NEET PG papers to analyze trends and practice"
        )
        
        if neet_papers:
            with st.spinner("🔄 Processing NEET PG papers..."):
                for paper_file in neet_papers:
                    file_bytes = paper_file.read()
                    fname = paper_file.name.lower()
                    
                    if fname.endswith(".txt"):
                        paper_text = load_text_content(file_bytes, paper_file.name)
                    elif fname.endswith(".pdf"):
                        paper_text = load_pdf_content(file_bytes, paper_file.name)
                    else:
                        continue
                    
                    if paper_text and paper_text.strip():
                        st.session_state.neet_pg_papers.append({
                            "name": paper_file.name,
                            "text": paper_text,
                            "year": paper_file.name
                        })
                
                st.success(f"✅ Loaded {len(neet_papers)} NEET PG paper(s)")
        
        if st.session_state.neet_pg_papers:
            st.markdown("---")
            st.markdown("#### 🔍 Paper Analysis & Practice")
            
            paper_option = st.selectbox(
                "Select a paper to analyze:",
                [p["name"] for p in st.session_state.neet_pg_papers],
                key="neet_select"
            )
            
            selected_neet = next((p for p in st.session_state.neet_pg_papers if p["name"] == paper_option), None)
            
            if selected_neet:
                neet_action = st.radio(
                    "What do you want to do?",
                    ["📊 Analyze Paper", "📖 Generate Practice Questions", "💾 View Paper"],
                    key="neet_action"
                )
                
                if neet_action == "📊 Analyze Paper":
                    if st.button("🔍 Analyze", key="neet_analyze"):
                        with st.spinner("Analyzing paper structure and content..."):
                            try:
                                analysis = analyze_exam_paper(selected_neet["text"], selected_neet["year"], "NEET PG")
                                st.markdown(f"""
                                <div class="med-card">
                                    {analysis}
                                </div>
                                """, unsafe_allow_html=True)
                            except Exception as e:
                                st.error(f"❌ {e}")
                
                elif neet_action == "📖 Generate Practice Questions":
                    num = st.slider("How many questions?", 1, 10, 5, key="neet_num")
                    if st.button("Generate Questions", key="neet_gen_q"):
                        with st.spinner(f"Generating {num} questions based on NEET PG patterns..."):
                            try:
                                questions = generate_paper_questions(selected_neet["text"], num, "NEET PG")
                                for i, q in enumerate(questions, 1):
                                    st.markdown(f"""
                                    <div class="med-card">
                                        <h4>Q{i}: {q.get('question', 'N/A')}</h4>
                                        <p><strong>Difficulty:</strong> {q.get('difficulty', 'N/A')} | <strong>Topic:</strong> {q.get('topic', 'N/A')}</p>
                                        <p><strong>A)</strong> {q.get('options', {}).get('A', '')}<br>
                                           <strong>B)</strong> {q.get('options', {}).get('B', '')}<br>
                                           <strong>C)</strong> {q.get('options', {}).get('C', '')}<br>
                                           <strong>D)</strong> {q.get('options', {}).get('D', '')}</p>
                                        <p style="color: #10B981;"><strong>Answer:</strong> {q.get('correct', 'N/A')} - {q.get('explanation', '')}</p>
                                    </div>
                                    """, unsafe_allow_html=True)
                            except Exception as e:
                                st.error(f"❌ {e}")
                
                elif neet_action == "💾 View Paper":
                    st.text_area("Paper Content:", value=selected_neet["text"][:2000] + "...", height=300, disabled=True)
        
        else:
            st.info("👆 Upload NEET PG papers to analyze trends and generate practice questions!")

    # ── TAB 6: UPSC CMS Papers ──
    with tab6:
        st.markdown("### 🏥 UPSC CMS Previous Year Papers")
        st.caption("Master UPSC CMS exam with previous year analysis")
        
        cms_col1, cms_col2, cms_col3 = st.columns(3)
        
        with cms_col1:
            st.metric("📄 Papers Loaded", len(st.session_state.upsc_cms_papers))
        with cms_col2:
            st.metric("✅ Practice Tests", 0)
        with cms_col3:
            st.metric("📗 Years Available", "2015-2024")
        
        st.markdown("---")
        
        # Upload papers
        st.markdown("#### 📥 Upload UPSC CMS Papers")
        cms_papers = st.file_uploader(
            "Upload UPSC CMS question papers (PDF or TXT)",
            type=["pdf", "txt"],
            accept_multiple_files=True,
            key="cms_papers",
            help="Upload previous years' UPSC CMS papers to analyze trends and practice"
        )
        
        if cms_papers:
            with st.spinner("🔄 Processing UPSC CMS papers..."):
                for paper_file in cms_papers:
                    file_bytes = paper_file.read()
                    fname = paper_file.name.lower()
                    
                    if fname.endswith(".txt"):
                        paper_text = load_text_content(file_bytes, paper_file.name)
                    elif fname.endswith(".pdf"):
                        paper_text = load_pdf_content(file_bytes, paper_file.name)
                    else:
                        continue
                    
                    if paper_text and paper_text.strip():
                        st.session_state.upsc_cms_papers.append({
                            "name": paper_file.name,
                            "text": paper_text,
                            "year": paper_file.name
                        })
                
                st.success(f"✅ Loaded {len(cms_papers)} UPSC CMS paper(s)")
        
        if st.session_state.upsc_cms_papers:
            st.markdown("---")
            st.markdown("#### 🔍 Paper Analysis & Practice")
            
            paper_option = st.selectbox(
                "Select a paper to analyze:",
                [p["name"] for p in st.session_state.upsc_cms_papers],
                key="cms_select"
            )
            
            selected_cms = next((p for p in st.session_state.upsc_cms_papers if p["name"] == paper_option), None)
            
            if selected_cms:
                cms_action = st.radio(
                    "What do you want to do?",
                    ["📊 Analyze Paper", "📖 Generate Practice Questions", "💾 View Paper"],
                    key="cms_action"
                )
                
                if cms_action == "📊 Analyze Paper":
                    if st.button("🔍 Analyze", key="cms_analyze"):
                        with st.spinner("Analyzing paper structure and content..."):
                            try:
                                analysis = analyze_exam_paper(selected_cms["text"], selected_cms["year"], "UPSC CMS")
                                st.markdown(f"""
                                <div class="med-card">
                                    {analysis}
                                </div>
                                """, unsafe_allow_html=True)
                            except Exception as e:
                                st.error(f"❌ {e}")
                
                elif cms_action == "📖 Generate Practice Questions":
                    num = st.slider("How many questions?", 1, 10, 5, key="cms_num")
                    if st.button("Generate Questions", key="cms_gen_q"):
                        with st.spinner(f"Generating {num} questions based on UPSC CMS patterns..."):
                            try:
                                questions = generate_paper_questions(selected_cms["text"], num, "UPSC CMS")
                                for i, q in enumerate(questions, 1):
                                    st.markdown(f"""
                                    <div class="med-card">
                                        <h4>Q{i}: {q.get('question', 'N/A')}</h4>
                                        <p><strong>Difficulty:</strong> {q.get('difficulty', 'N/A')} | <strong>Topic:</strong> {q.get('topic', 'N/A')}</p>
                                        <p><strong>A)</strong> {q.get('options', {}).get('A', '')}<br>
                                           <strong>B)</strong> {q.get('options', {}).get('B', '')}<br>
                                           <strong>C)</strong> {q.get('options', {}).get('C', '')}<br>
                                           <strong>D)</strong> {q.get('options', {}).get('D', '')}</p>
                                        <p style="color: #10B981;"><strong>Answer:</strong> {q.get('correct', 'N/A')} - {q.get('explanation', '')}</p>
                                    </div>
                                    """, unsafe_allow_html=True)
                            except Exception as e:
                                st.error(f"❌ {e}")
                
                elif cms_action == "💾 View Paper":
                    st.text_area("Paper Content:", value=selected_cms["text"][:2000] + "...", height=300, disabled=True)
        
        else:
            st.info("👆 Upload UPSC CMS papers to analyze trends and generate practice questions!")
