"""
MBBS Notes RAG Agent - Powered by Google Gemini
=================================================
A smart study companion that answers questions about your MBBS notes
using Retrieval Augmented Generation (RAG) with Google Gemini AI.

How it works:
1. Loads your notes from the 'documents' folder (.txt and .pdf)
2. Splits them into smart chunks (paragraph-aware)
3. Creates embeddings (numerical representations) using Gemini
4. Finds the most relevant chunks when you ask a question
5. Uses Gemini AI to generate a clear, student-friendly answer
"""

import os
import sys
import math
from pathlib import Path
from dotenv import load_dotenv
from google import genai
from google.genai import types

# Fix Windows console encoding
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

# Load environment variables from .env file
load_dotenv()

# Configure Gemini client
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    print("\n[ERROR] GEMINI_API_KEY not found!")
    print("  Create a .env file with: GEMINI_API_KEY=your-key-here")
    print("  Get your key at: https://aistudio.google.com/apikey\n")
    exit(1)

client = genai.Client(api_key=GEMINI_API_KEY)


# --- Document Loading --------------------------------------------------------

def load_text_file(file_path):
    """Load a .txt file and return its content."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()


def extract_pdf_with_gemini(file_path):
    """
    Use Gemini to extract text from a scanned/image-based PDF.
    Uploads the PDF directly to Gemini's file API and uses the model
    to extract all text content - no extra dependencies needed.
    """
    try:
        print(f"    [*] Scanned PDF detected - using Gemini AI to extract text...")

        # Upload PDF directly to Gemini
        uploaded_file = client.files.upload(file=str(file_path))

        # Use Gemini to extract text from the PDF
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[
                uploaded_file,
                "Extract ALL the text from this PDF document exactly as written. "
                "Preserve headings, bullet points, numbered lists, and structure. "
                "If there are diagrams or images, describe them briefly in [brackets]. "
                "Output only the extracted text, no commentary."
            ]
        )

        text = response.text
        if text and text.strip():
            print(f"    [OK] Extracted text from {file_path.name} ({len(text):,} chars)")
            return text.strip()
        else:
            print(f"    [!] Gemini could not extract text from {file_path.name}")
            return None

    except Exception as e:
        print(f"  [!] Gemini extraction failed for {file_path.name}: {e}")
        return None


def load_pdf_file(file_path):
    """Load a .pdf file and return its text content.
    Tries PyPDF2 first (for text-based PDFs), falls back to
    Gemini Vision for scanned/image-based PDFs.
    """
    try:
        from PyPDF2 import PdfReader
        reader = PdfReader(file_path)
        text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n\n"

        # If we got text, return it
        if text.strip():
            return text.strip()

        # No text found - likely a scanned PDF, try Gemini vision
        print(f"    [!] No text found in {file_path.name} (likely scanned)")
        return extract_pdf_with_gemini(file_path)

    except ImportError:
        print(f"  [!] Skipping {file_path.name} -- install PyPDF2 for PDF support")
        return None
    except Exception as e:
        print(f"  [!] Error reading {file_path.name}: {e}")
        return None


def load_documents(folder_path="documents"):
    """
    Load all supported documents (.txt, .pdf) from the specified folder.

    Returns:
        List of tuples (filename, content)
    """
    documents = []
    doc_folder = Path(folder_path)

    # Create folder if it doesn't exist
    doc_folder.mkdir(exist_ok=True)

    # Load .txt files
    for file_path in sorted(doc_folder.glob("*.txt")):
        content = load_text_file(file_path)
        if content.strip():
            documents.append((file_path.name, content))

    # Load .pdf files
    for file_path in sorted(doc_folder.glob("*.pdf")):
        content = load_pdf_file(file_path)
        if content and content.strip():
            documents.append((file_path.name, content))

    return documents


# --- Text Chunking -----------------------------------------------------------

def split_into_chunks(text, chunk_size=800, overlap=100):
    """
    Split text into chunks with paragraph awareness and overlap.

    Medical notes often have headers, bullet points, and paragraphs.
    This splitter tries to keep paragraphs together and adds overlap
    so that context isn't lost at chunk boundaries.

    Args:
        text: The text to split
        chunk_size: Target size of each chunk in characters
        overlap: Number of characters to overlap between chunks

    Returns:
        List of text chunks
    """
    # Split by double newlines (paragraphs)
    paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]

    chunks = []
    current_chunk = []
    current_size = 0

    for para in paragraphs:
        para_size = len(para)

        # If a single paragraph is larger than chunk_size, split it by sentences
        if para_size > chunk_size:
            # Flush current chunk first
            if current_chunk:
                chunks.append('\n\n'.join(current_chunk))
                current_chunk = []
                current_size = 0

            # Split large paragraph by sentences
            sentences = para.replace('. ', '.\n').split('\n')
            temp_chunk = []
            temp_size = 0
            for sentence in sentences:
                if temp_size + len(sentence) > chunk_size and temp_chunk:
                    chunks.append(' '.join(temp_chunk))
                    # Keep last sentence for overlap
                    temp_chunk = [temp_chunk[-1]] if overlap > 0 else []
                    temp_size = len(temp_chunk[0]) if temp_chunk else 0
                temp_chunk.append(sentence)
                temp_size += len(sentence)
            if temp_chunk:
                chunks.append(' '.join(temp_chunk))
            continue

        # If adding this paragraph exceeds chunk_size, start new chunk
        if current_size + para_size > chunk_size and current_chunk:
            chunks.append('\n\n'.join(current_chunk))
            # Keep last paragraph for overlap
            if overlap > 0 and current_chunk:
                last = current_chunk[-1]
                current_chunk = [last] if len(last) < overlap * 2 else []
                current_size = len(last) if current_chunk else 0
            else:
                current_chunk = []
                current_size = 0

        current_chunk.append(para)
        current_size += para_size

    # Add remaining content
    if current_chunk:
        chunks.append('\n\n'.join(current_chunk))

    return chunks


# --- Gemini Embeddings -------------------------------------------------------

def create_embedding(text):
    """
    Create an embedding using Gemini's embedding model for document chunks.

    Returns:
        Embedding vector (list of floats)
    """
    result = client.models.embed_content(
        model="gemini-embedding-001",
        contents=text,
        config=types.EmbedContentConfig(task_type="RETRIEVAL_DOCUMENT")
    )
    return result.embeddings[0].values


def create_query_embedding(text):
    """
    Create an embedding for a query (uses RETRIEVAL_QUERY task type).

    Returns:
        Embedding vector (list of floats)
    """
    result = client.models.embed_content(
        model="gemini-embedding-001",
        contents=text,
        config=types.EmbedContentConfig(task_type="RETRIEVAL_QUERY")
    )
    return result.embeddings[0].values


# --- Similarity Search -------------------------------------------------------

def cosine_similarity(vec1, vec2):
    """
    Calculate cosine similarity between two vectors.

    Returns:
        Similarity score between -1 and 1 (higher = more similar)
    """
    dot_product = sum(a * b for a, b in zip(vec1, vec2))
    magnitude1 = math.sqrt(sum(a * a for a in vec1))
    magnitude2 = math.sqrt(sum(b * b for b in vec2))

    if magnitude1 == 0 or magnitude2 == 0:
        return 0.0

    return dot_product / (magnitude1 * magnitude2)


def find_relevant_chunks(question, chunks_with_embeddings, top_k=3):
    """
    Find the most relevant chunks for a question.

    Args:
        question: The user's question
        chunks_with_embeddings: List of (chunk_text, source_file, embedding) tuples
        top_k: Number of relevant chunks to return

    Returns:
        List of (chunk_text, source_file, score) tuples
    """
    # Get embedding for the question (using query task type for better results)
    question_embedding = create_query_embedding(question)

    # Calculate similarity for each chunk
    scored = []
    for chunk_text, source_file, chunk_embedding in chunks_with_embeddings:
        score = cosine_similarity(question_embedding, chunk_embedding)
        scored.append((chunk_text, source_file, score))

    # Sort by similarity and get top results
    scored.sort(key=lambda x: x[2], reverse=True)
    return scored[:top_k]


# --- Gemini Answer Generation ------------------------------------------------

SYSTEM_INSTRUCTION = (
    "You are an expert MBBS study assistant. You help medical students understand "
    "their notes clearly. Follow these rules:\n"
    "1. Answer based ONLY on the provided context from the student's notes.\n"
    "2. Use clear, student-friendly language while keeping proper medical terminology.\n"
    "3. When explaining complex concepts, break them down step by step.\n"
    "4. If the context contains relevant clinical correlations, mention them.\n"
    "5. If the answer is not in the context, say so honestly and suggest what "
    "topic the student might want to review.\n"
    "6. Use bullet points and structured formatting for clarity.\n"
    "7. At the end, briefly mention which source document(s) the answer came from."
)


def generate_answer(question, relevant_chunks):
    """
    Generate an answer using Gemini based on relevant context from MBBS notes.

    Args:
        question: The user's question
        relevant_chunks: List of (chunk_text, source_file, score) tuples

    Returns:
        AI-generated answer string
    """
    # Build context with source attribution
    context_parts = []
    for i, (chunk_text, source_file, score) in enumerate(relevant_chunks, 1):
        context_parts.append(f"[Source: {source_file}]\n{chunk_text}")

    context = "\n\n---\n\n".join(context_parts)

    prompt = f"""Based on the following excerpts from MBBS study notes, answer the student's question.

Context from notes:
{context}

Student's Question: {question}

Provide a clear, well-structured answer:"""

    # Use Gemini to generate the answer
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_INSTRUCTION,
            temperature=0.7,
            max_output_tokens=1000,
        )
    )
    return response.text


# --- Active Revision --------------------------------------------------------

import random
import json


def generate_mcqs(chunks_with_embeddings, num_questions=5):
    """
    Generate MCQ questions from random chunks of the notes.
    Uses Gemini to create exam-style questions.
    """
    # Pick random chunks as source material
    available = [c for c in chunks_with_embeddings]
    selected = random.sample(available, min(num_questions, len(available)))

    context = "\n\n---\n\n".join([chunk for chunk, _, _ in selected])

    prompt = f"""Based on the following MBBS study notes, generate exactly {num_questions} multiple choice questions (MCQs).

Notes:
{context}

Return the output as a valid JSON array. Each element should have:
- "question": the question text
- "options": an object with keys "A", "B", "C", "D" and their text values
- "correct": the correct option letter (A, B, C, or D)
- "explanation": a brief explanation of the correct answer

Return ONLY the JSON array, no other text. Example format:
[{{"question": "...", "options": {{"A": "...", "B": "...", "C": "...", "D": "..."}}, "correct": "A", "explanation": "..."}}]"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction="You are an MBBS exam question setter. Create clinically relevant, exam-style MCQs that test understanding, not just recall. Return only valid JSON.",
            temperature=0.8,
            max_output_tokens=2000,
        )
    )

    # Parse the JSON response
    text = response.text.strip()
    # Remove markdown code fences if present
    if text.startswith("```"):
        text = text.split("\n", 1)[1]
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()

    return json.loads(text)


def run_mcq_quiz(chunks_with_embeddings):
    """Run an interactive MCQ quiz session."""
    print("\n" + "=" * 60)
    print("MCQ QUIZ MODE")
    print("=" * 60)

    try:
        num = input("\nHow many questions? (default 5): ").strip()
        num_questions = int(num) if num else 5
    except ValueError:
        num_questions = 5

    print(f"\n[...] Generating {num_questions} MCQs from your notes...")

    try:
        mcqs = generate_mcqs(chunks_with_embeddings, num_questions)
    except Exception as e:
        print(f"\n[ERROR] Failed to generate MCQs: {e}")
        return

    score = 0
    total = len(mcqs)

    for i, mcq in enumerate(mcqs, 1):
        print(f"\n{'='*60}")
        print(f"  Question {i}/{total}")
        print(f"{'='*60}")
        print(f"\n  {mcq['question']}\n")

        for letter in ['A', 'B', 'C', 'D']:
            if letter in mcq['options']:
                print(f"    {letter}. {mcq['options'][letter]}")

        print()
        try:
            answer = input("  Your answer (A/B/C/D): ").strip().upper()
        except (EOFError, KeyboardInterrupt):
            print("\n\n  Quiz ended early.")
            break

        correct = mcq['correct'].upper()

        if answer == correct:
            print(f"\n  [CORRECT!] Well done!")
            score += 1
        else:
            print(f"\n  [WRONG] The correct answer is: {correct}")

        print(f"  Explanation: {mcq.get('explanation', 'N/A')}")

    print(f"\n{'='*60}")
    print(f"  QUIZ RESULTS: {score}/{total} correct ({score/total*100:.0f}%)")
    if score == total:
        print("  PERFECT SCORE! Excellent revision!")
    elif score >= total * 0.7:
        print("  Great job! Keep it up!")
    elif score >= total * 0.5:
        print("  Good effort! Review the topics you missed.")
    else:
        print("  Keep studying! Review your notes and try again.")
    print(f"{'='*60}")


def generate_flashcard_topic(chunks_with_embeddings):
    """
    Pick a random chunk and generate a flashcard-style question.
    Shows a topic/concept and asks user to recall before revealing.
    """
    chunk_text, source_file, _ = random.choice(chunks_with_embeddings)

    prompt = f"""Based on this study material, create ONE flashcard for active recall revision.

Study material:
{chunk_text}

Return as JSON with these fields:
- "front": A specific question or prompt about a key concept (e.g., "Name the branches of the left coronary artery and the areas they supply")
- "back": The detailed answer with key points in bullet format
- "topic": The topic name (e.g., "Coronary Arteries")
- "source": "{source_file}"

Return ONLY the JSON, no other text."""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction="You are an MBBS study assistant creating flashcards for active recall. Focus on high-yield, exam-relevant concepts. Return only valid JSON.",
            temperature=0.9,
            max_output_tokens=500,
        )
    )

    text = response.text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1]
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()

    return json.loads(text)


def run_flashcard_session(chunks_with_embeddings):
    """Run an interactive flashcard active recall session."""
    print("\n" + "=" * 60)
    print("FLASHCARD ACTIVE RECALL")
    print("=" * 60)
    print("\n  A topic will be shown. Try to recall the answer,")
    print("  then press ENTER to reveal it.\n")

    card_count = 0

    while True:
        print("-" * 60)
        print(f"\n[...] Generating flashcard...")

        try:
            card = generate_flashcard_topic(chunks_with_embeddings)
        except Exception as e:
            print(f"\n[ERROR] {e}")
            break

        card_count += 1
        print(f"\n  CARD #{card_count}  |  Topic: {card.get('topic', 'Unknown')}")
        print(f"  Source: {card.get('source', 'Unknown')}")
        print(f"\n{'~'*60}")
        print(f"\n  {card['front']}")
        print(f"\n{'~'*60}")

        try:
            input("\n  >> Think about your answer, then press ENTER to reveal...")
        except (EOFError, KeyboardInterrupt):
            print("\n\n  Session ended.")
            break

        print(f"\n  ANSWER:")
        print(f"  {'-'*50}")
        print(f"  {card['back']}")
        print(f"  {'-'*50}")

        try:
            self_score = input("\n  How did you do? [1] Forgot  [2] Partial  [3] Nailed it!  : ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n\n  Session ended.")
            break

        if self_score == "1":
            print("  >> Mark this topic for extra review!\n")
        elif self_score == "3":
            print("  >> Great recall! Moving on.\n")
        else:
            print("  >> Good effort, review once more later.\n")

        try:
            cont = input("  Continue? (Y/n): ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            break

        if cont == 'n':
            break

    print(f"\n  Completed {card_count} flashcard(s). Keep revising!")
    print("=" * 60)


def generate_topic_summary(chunks_with_embeddings):
    """Generate a concise topic summary from a random chunk for quick revision."""
    chunk_text, source_file, _ = random.choice(chunks_with_embeddings)

    prompt = f"""Create a concise revision summary of the following study material. 
Include:
- Key points as bullet points
- Important definitions
- Clinical correlations if any
- Memory aids / mnemonics if applicable

Study material:
{chunk_text}

Source: {source_file}"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction="You are an MBBS study assistant. Create concise, exam-focused revision summaries. Highlight high-yield facts.",
            temperature=0.7,
            max_output_tokens=800,
        )
    )
    return response.text, source_file


def run_topic_summary(chunks_with_embeddings):
    """Show a random topic summary for quick revision."""
    print("\n" + "=" * 60)
    print("QUICK TOPIC REVISION")
    print("=" * 60)

    while True:
        print(f"\n[...] Generating topic summary...")

        try:
            summary, source = generate_topic_summary(chunks_with_embeddings)
        except Exception as e:
            print(f"\n[ERROR] {e}")
            break

        print(f"\n{summary}")
        print(f"\n  [Source: {source}]")
        print("-" * 60)

        try:
            cont = input("\n  Next topic? (Y/n): ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            break

        if cont == 'n':
            break

    print("\n  Revision session complete!")
    print("=" * 60)


# --- CLI Interface ------------------------------------------------------------

def print_banner():
    """Print a styled welcome banner (ASCII-safe for Windows)."""
    print()
    print("+" + "=" * 60 + "+")
    print("|     MBBS Notes RAG Agent  (Powered by Gemini AI)         |")
    print("|     Your AI-Powered Study Companion                     |")
    print("+" + "=" * 60 + "+")
    print()


def print_sources(relevant_chunks):
    """Print the source documents used for the answer."""
    sources = set()
    for _, source_file, score in relevant_chunks:
        sources.add(f"  >> {source_file} (relevance: {score:.0%})")
    print("\n[SOURCES]")
    for src in sorted(sources):
        print(src)


def print_menu():
    """Print the main menu."""
    print("\n" + "=" * 60)
    print("  MAIN MENU")
    print("=" * 60)
    print()
    print("  [1] Ask a Question      - Q&A about your notes")
    print("  [2] MCQ Quiz            - Test yourself with MCQs")
    print("  [3] Flashcard Recall    - Active recall practice")
    print("  [4] Quick Topic Review  - Random topic summaries")
    print("  [q] Quit")
    print()


def run_qa_mode(chunks_with_embeddings):
    """Run a single Q&A interaction."""
    try:
        question = input(">> Your question: ").strip()
    except (EOFError, KeyboardInterrupt):
        return False

    if question.lower() in ['quit', 'exit', 'q', 'menu', 'back']:
        return False

    if not question:
        return True

    print("\n[...] Searching your notes and thinking...")

    try:
        relevant_chunks = find_relevant_chunks(
            question, chunks_with_embeddings, top_k=3
        )
        answer = generate_answer(question, relevant_chunks)

        print("\n" + "=" * 60)
        print("ANSWER:")
        print("=" * 60)
        print()
        print(answer)
        print_sources(relevant_chunks)
        print("\n" + "-" * 60)

    except Exception as e:
        print(f"\n[ERROR] {e}")
        print("        Please try rephrasing your question.\n")

    return True


def main():
    """Main function to run the MBBS Notes RAG Agent."""
    print_banner()

    # -- Step 1: Load documents --
    print("[*] Loading documents...")
    documents = load_documents()

    if not documents:
        print("\n[!] No documents found in the 'documents/' folder!")
        print("    Add your MBBS notes as .txt or .pdf files and try again.")
        print("    Supported formats: .txt, .pdf\n")
        return

    total_chars = 0
    print(f"\n    Found {len(documents)} document(s):")
    for filename, content in documents:
        total_chars += len(content)
        print(f"    - {filename} ({len(content):,} chars)")

    # -- Step 2: Chunk and embed --
    print(f"\n[*] Processing {total_chars:,} characters of notes...")
    all_chunks = []

    for filename, content in documents:
        chunks = split_into_chunks(content)
        for chunk in chunks:
            all_chunks.append((chunk, filename))

    print(f"    Split into {len(all_chunks)} chunks")
    print("    Creating embeddings (this may take a moment)...")

    chunks_with_embeddings = []
    for i, (chunk_text, source_file) in enumerate(all_chunks):
        embedding = create_embedding(chunk_text)
        chunks_with_embeddings.append((chunk_text, source_file, embedding))
        if (i + 1) % 5 == 0 or (i + 1) == len(all_chunks):
            print(f"    [OK] Embedded {i + 1}/{len(all_chunks)} chunks")

    # -- Step 3: Interactive menu loop --
    while True:
        print_menu()

        try:
            choice = input("  Your choice: ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print("\n\nGoodbye! Happy studying!")
            break

        if choice in ['q', 'quit', 'exit']:
            print("\nGoodbye! Happy studying!")
            break
        elif choice == '1':
            print("\n" + "-" * 60)
            print("[Q&A MODE] Ask questions about your notes. Type 'back' for menu.")
            print("-" * 60 + "\n")
            while run_qa_mode(chunks_with_embeddings):
                pass
        elif choice == '2':
            run_mcq_quiz(chunks_with_embeddings)
        elif choice == '3':
            run_flashcard_session(chunks_with_embeddings)
        elif choice == '4':
            run_topic_summary(chunks_with_embeddings)
        else:
            print("\n  [!] Invalid choice. Please enter 1, 2, 3, 4, or q.")


if __name__ == "__main__":
    main()
