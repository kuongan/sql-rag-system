#!/usr/bin/env python3
"""
Ingest PDF to FAISS Vector Store (Simplified)
Process PDF → Split → Embed → Save FAISS index
"""

import os
import json
import time
from pathlib import Path
import re
import dotenv
dotenv.load_dotenv()
import PyPDF2
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings


def extract_pdf_text(pdf_path: str) -> list:
    """Extract text from PDF file"""
    docs = []
    with open(pdf_path, "rb") as f:
        pdf_reader = PyPDF2.PdfReader(f)
        for page_num, page in enumerate(pdf_reader.pages, 1):
            text = page.extract_text()
            if text and text.strip():
                docs.append(Document(
                    page_content=text.strip(),
                    metadata={"page": page_num, "source": pdf_path}
                ))
    return docs


def split_documents(docs: list) -> list:
    """Split docs into semantic chunks"""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=600, chunk_overlap=200,
        separators=["\n\n", "\n", ".", " "]
    )
    section_pattern = re.compile(r"^(?:[A-Z][A-Za-z ]+|[0-9]+\.[0-9]+.*)$")
    chunks = []

    for doc in docs:
        lines = doc.page_content.splitlines()
        buf, section, sid = [], "Unknown", 0
        for line in lines:
            if section_pattern.match(line.strip()):
                if buf:
                    txt = "\n".join(buf).strip()
                    if len(txt.split()) > 5:
                        d = Document(
                            page_content=txt,
                            metadata={**doc.metadata, "section": section}
                        )
                        chunks.extend(splitter.split_documents([d]))
                    buf, sid = [], sid + 1
                section = line.strip()
            buf.append(line)

        if buf:
            txt = "\n".join(buf).strip()
            if len(txt.split()) > 5:
                d = Document(
                    page_content=txt,
                    metadata={**doc.metadata, "section": section}
                )
                chunks.extend(splitter.split_documents([d]))
    return chunks


def create_faiss_store(chunks: list, out_path: str):
    """Embed & save FAISS vector store"""
    api_key =  os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise RuntimeError("Missing GOOGLE_API_KEY")

    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/embedding-001",
        google_api_key=api_key
    )

    texts = [c.page_content for c in chunks]
    metas = [c.metadata for c in chunks]

    store = FAISS.from_texts(texts, embeddings, metas)

    os.makedirs(out_path, exist_ok=True)
    store.save_local(out_path)

    with open(os.path.join(out_path, "metadata.json"), "w") as f:
        json.dump({
            "total_chunks": len(chunks),
            "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "chunks": [
                {
                    "id": i,
                    "text": c.page_content,
                    "metadata": c.metadata
                }
                for i, c in enumerate(chunks)
            ]
        }, f, indent=2, ensure_ascii=False)



def main():
    pdf_path = "data/swiss_faq.pdf"
    out_path = "data/faiss_store"

    if not os.path.exists(pdf_path):
        print(f"Missing PDF: {pdf_path}")
        return 1

    docs = extract_pdf_text(pdf_path)
    if not docs:
        print("No text extracted")
        return 1

    chunks = split_documents(docs)
    if not chunks:
        print("No chunks created")
        return 1

    create_faiss_store(chunks, out_path)
    print(f"✅ Saved FAISS store with {len(chunks)} chunks → {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
