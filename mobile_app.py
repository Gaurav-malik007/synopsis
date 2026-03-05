"""
Synopsis Mobile Wrapper - Android/iOS compatible version using Streamlit
Optimized for mobile-first experience
"""

import os
import sys
import streamlit as st
from pathlib import Path

# --- Mobile Detection & Optimization ---
def is_mobile():
    """Detect if user is on mobile"""
    return "user_agent" in st.session_state or "mobile" in str(st.query_params).lower()

# --- Page Config for Mobile ---
st.set_page_config(
    page_title="Synopsis",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="collapsed",  # Start with sidebar collapsed on mobile
    menu_items=None  # Remove default menu
)

# --- Mobile-Optimized CSS ---
st.markdown("""
<style>
    /* Force full width on mobile */
    .main .block-container {
        padding-left: 0.5rem;
        padding-right: 0.5rem;
        max-width: 100%;
    }
    
    /* Hide header and footer for native app feel */
    header {display: none;}
    footer {display: none;}
    
    /* Mobile-first colors */
    body {
        background: #0F172A;
        color: #E2E8F0;
    }
    
    /* Optimize buttons for touch */
    button {
        padding: 0.75rem 1.5rem;
        font-size: 1rem;
        min-height: 44px;
    }
    
    /* Full width file uploader */
    [data-testid="stFileUploader"] {
        width: 100%;
    }
    
    /* Mobile-friendly tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 4px;
        width: 100%;
    }
    
    .stTabs [data-baseweb="tab"] {
        padding: 0.5rem;
        font-size: 0.8rem;
    }
    
    /* Mobile header */
    .mobile-header {
        background: linear-gradient(135deg, #0D9488 0%, #065F56 100%);
        padding: 1rem;
        border-radius: 0;
        margin: -1rem -0.5rem 1rem -0.5rem;
        text-align: center;
    }
    
    .mobile-header h1 {
        color: white;
        font-size: 1.5rem;
        margin: 0;
    }
    
    /* Touch-friendly cards */
    .mobile-card {
        background: #1E293B;
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 1rem;
        margin-bottom: 0.75rem;
        min-height: 60px;
        display: flex;
        align-items: center;
        cursor: pointer;
    }
    
    .mobile-card:active {
        background: #0D9488;
        transform: scale(0.98);
    }
</style>
""", unsafe_allow_html=True)

# --- Import original functions ---
sys.path.insert(0, str(Path(__file__).parent))
try:
    from web_app import (
        load_text_content, load_pdf_content, load_image_content,
        split_into_chunks, create_embedding, extract_topics,
        find_relevant_chunks, generate_answer, save_registration,
        get_gemini_client
    )
except ImportError:
    st.error("Could not load web_app functions. Make sure web_app.py is in the same directory.")
    st.stop()

# --- Session State ---
if "user_registered" not in st.session_state:
    st.session_state.user_registered = False
if "uploaded_files_info" not in st.session_state:
    st.session_state.uploaded_files_info = []
if "chunks_with_embeddings" not in st.session_state:
    st.session_state.chunks_with_embeddings = []
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# --- Mobile Header ---
st.markdown("""
<div class="mobile-header">
    <h1>🩺 Synopsis</h1>
    <p style="color: #99F6E4; margin: 0; font-size: 0.8rem;">MBBS Study Companion</p>
</div>
""", unsafe_allow_html=True)

# --- Mobile-First Upload Interface ---
st.markdown("## 📱 Upload Your Notes")

upload_col1, upload_col2 = st.columns(2)

with upload_col1:
    docs = st.file_uploader(
        "📄 Documents (PDF, TXT)",
        type=["pdf", "txt"],
        accept_multiple_files=True,
        key="mobile_docs"
    )

with upload_col2:
    photos = st.file_uploader(
        "📸 Photos of Notes",
        type=["jpg", "jpeg", "png", "webp", "heic"],
        accept_multiple_files=True,
        key="mobile_photos"
    )

# --- Process Uploads ---
if docs or photos:
    all_files = []
    if docs:
        all_files.extend(docs)
    if photos:
        all_files.extend(photos[:20])
    
    current_names = sorted([f.name for f in all_files])
    prev_names = sorted([info["name"] for info in st.session_state.uploaded_files_info])
    
    if current_names != prev_names:
        with st.spinner("Processing notes... 🔄"):
            progress_bar = st.progress(0)
            all_chunks = []
            
            for i, file in enumerate(all_files):
                progress_bar.progress((i + 1) / len(all_files))
                
                file_bytes = file.read()
                fname = file.name.lower()
                
                if fname.endswith(".txt"):
                    text = load_text_content(file_bytes, file.name)
                elif fname.endswith(".pdf"):
                    text = load_pdf_content(file_bytes, file.name)
                elif any(fname.endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.webp', '.heic']):
                    text = load_image_content(file_bytes, file.name)
                else:
                    continue
                
                if text and text.strip():
                    chunks = split_into_chunks(text)
                    for chunk in chunks:
                        all_chunks.append((chunk, file.name))
            
            # Create embeddings
            if all_chunks:
                progress_bar.progress(0)
                chunks_with_emb = []
                for i, (chunk, source) in enumerate(all_chunks):
                    progress_bar.progress((i + 1) / len(all_chunks))
                    emb = create_embedding(chunk)
                    if emb:
                        chunks_with_emb.append((chunk, source, emb))
                
                progress_bar.empty()
                st.session_state.chunks_with_embeddings = chunks_with_emb
                st.session_state.uploaded_files_info = [{"name": f.name} for f in all_files]
                st.success(f"✅ Loaded {len(chunks_with_emb)} chunks!")
                st.rerun()

# --- Mobile Tabs ---
if st.session_state.chunks_with_embeddings:
    st.markdown("---")
    
    tab1, tab2, tab3 = st.tabs(["💬 Questions", "📝 Quiz", "🧠 Cards"])
    
    with tab1:
        st.markdown("### Ask Your Notes")
        question = st.text_input("What would you like to know?", placeholder="e.g. What is photosynthesis?")
        
        if question:
            with st.spinner("Searching..."):
                relevant = find_relevant_chunks(question, st.session_state.chunks_with_embeddings, top_k=3)
                answer = generate_answer(question, relevant)
            
            st.markdown(f"**Answer:**\n{answer}")
            
            with st.expander("📚 Sources"):
                for chunk, source, score in relevant:
                    st.caption(f"📄 {source} ({score:.0%})")
    
    with tab2:
        st.info("📝 MCQ feature - Coming soon for mobile")
    
    with tab3:
        st.info("🧠 Flashcards feature - Coming soon for mobile")

else:
    st.markdown("---")
    st.markdown("""
    ### How to Get Started:
    
    1. **📄 Upload Notes** - Use the upload section above
    2. **💬 Ask Questions** - Chat with your notes using AI
    3. **📝 Take MCQs** - Auto-generated practice questions
    4. **🧠 Use Flashcards** - Active recall practice
    
    **Supported Formats:**
    - PDFs, Text files, Photos of notes
    - Upload up to 20 photos at once
    - Max 50MB per file
    """)

st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #94A3B8; font-size: 0.8rem; padding: 1rem;">
    <p>📱 Mobile Optimized • 🔒 Private Data • 🚀 Powered by AI</p>
</div>
""", unsafe_allow_html=True)
