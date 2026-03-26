import PyPDF2
import json
import re
from pathlib import Path


def extract_pdf_content(pdf_path):
    """Extract text content from PDF file"""
    text_content = ""

    with open(pdf_path, "rb") as file:
        pdf_reader = PyPDF2.PdfReader(file)

        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            text_content += page.extract_text() + "\n"

    return text_content


def chunk_text(text, chunk_size=1000, overlap=200):
    """Split text into overlapping chunks"""
    # Clean up the text
    text = re.sub(r"\n+", "\n", text)
    text = re.sub(r"\s+", " ", text)

    chunks = []
    words = text.split()

    for i in range(0, len(words), chunk_size - overlap):
        chunk_words = words[i : i + chunk_size]
        chunk_text = " ".join(chunk_words)

        if chunk_text.strip():
            chunks.append(
                {
                    "chunk_id": f"chunk_{len(chunks) + 1}",
                    "content": chunk_text.strip(),
                    "metadata": {
                        "source": "marrakech-places-rag.pdf",
                        "chunk_index": len(chunks),
                    },
                }
            )

    return chunks


def main():
    # Path to the PDF file
    pdf_path = Path("backend/app/data/marrakech-places-rag.pdf")
    output_path = Path("backend/app/data/text_chunks.json")

    if not pdf_path.exists():
        print(f"PDF file not found: {pdf_path}")
        return

    print("Extracting content from PDF...")
    text_content = extract_pdf_content(pdf_path)

    print(f"Extracted {len(text_content)} characters from PDF")

    print("Creating text chunks...")
    chunks = chunk_text(text_content)

    print(f"Created {len(chunks)} chunks")

    # Save chunks to JSON file
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(chunks, f, indent=2, ensure_ascii=False)

    print(f"Saved chunks to {output_path}")

    # Print first few chunks for verification
    print("\nFirst 3 chunks preview:")
    for i, chunk in enumerate(chunks[:3]):
        print(f"\nChunk {i+1}:")
        print(f"Content: {chunk['content'][:200]}...")


if __name__ == "__main__":
    main()
