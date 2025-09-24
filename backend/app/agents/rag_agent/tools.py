"""
RAG Agent Tools - Document search and Q&A tools using FAISS
"""
import logging
import os
from typing import Dict, Any

from langchain_core.tools import tool
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from app.models.agents.rag import DocumentSearchInput, RAGQueryInput
from app.config import settings

logger = logging.getLogger(__name__)

_vector_store = None
_embeddings = None
_llm = None

def _get_vector_store():
    """Get or load FAISS vector store"""
    global _vector_store, _embeddings, _llm

    if _vector_store is None:
        try:
            # Initialize embeddings
            _embeddings = GoogleGenerativeAIEmbeddings(
                model=settings.EMBEDDING_MODEL,
                google_api_key=settings.GOOGLE_API_KEY
            )

            # Load FAISS
            faiss_store_path = settings.FAISS_STORE_PATH
            if os.path.exists(faiss_store_path):
                logger.info(f"Loading FAISS store from: {faiss_store_path}")
                _vector_store = FAISS.load_local(
                    faiss_store_path,
                    _embeddings,
                    allow_dangerous_deserialization=True
                )
                logger.info("FAISS vector store loaded successfully")
            else:
                raise FileNotFoundError(f"FAISS store not found at: {faiss_store_path}")

            # Init LLM
            _llm = ChatGoogleGenerativeAI(
                model=settings.LLM_MODEL,
                google_api_key=settings.GOOGLE_API_KEY,
                temperature=0.1
            )

        except Exception as e:
            logger.error(f"Error loading FAISS vector store: {e}")
            raise

    return _vector_store, _llm

# -----------------------------
# Tools
# -----------------------------
@tool("search_documents", args_schema=DocumentSearchInput, return_direct=True)
def search_documents(query: str, num_results: int = 10) -> Dict[str, Any]:
    """
    Search for relevant documents in the knowledge base using semantic similarity.
    """
    try:
        vector_store, _ = _get_vector_store()
        num_results = min(max(1, num_results), 10)
        docs = vector_store.similarity_search(query, k=num_results)

        if not docs:
            return {"query": query, "documents": [], "sources": []}

        documents = []
        sources = []
        for doc in docs:
            documents.append({
                "content": doc.page_content,
                "source": doc.metadata.get("source", "Unknown"),
                "page": doc.metadata.get("page", "Unknown"),
                "section": doc.metadata.get("section", "Unknown")
            })
            sources.append(f"Page {doc.metadata.get('page', 'Unknown')} - {doc.metadata.get('section', '')}")

        return {"query": query, "documents": documents, "sources": sources}

    except Exception as e:
        logger.error(f"Error in document search: {e}")
        return {"error": str(e), "query": query}

@tool("answer_question", args_schema=RAGQueryInput, return_direct=True)
def answer_question(question: str) -> Dict[str, Any]:
    """
    Answer questions using the document knowledge base with RAG.
    """
    try:
        vector_store, llm = _get_vector_store()
        docs = vector_store.similarity_search(question, k=10)

        if not docs:
            return {"answer": "No relevant documents found.", "sources": [], "confidence": 0.0}

        # Build context
        context = "\n\n".join([
            f"(Page {doc.metadata.get('page')} - {doc.metadata.get('section', 'Unknown')}) {doc.page_content}"
            for doc in docs
        ])

        # Prompt LLM
        prompt = f"""
        You are a Swiss Airlines assistant. Answer the question using the context below.
        Always cite sources with page numbers.

        Question: {question}

        Context:
        {context}

        Answer:
        """
        response = llm.invoke(prompt)

        sources = [
            f"Page {doc.metadata.get('page', 'Unknown')} - {doc.metadata.get('section', '')}"
            for doc in docs
        ]

        return {
            "answer": response.content,
            "sources": sources,
            "documents": [doc.page_content for doc in docs],
            "confidence": 0.8  
        }

    except Exception as e:
        logger.error(f"Error in RAG Q&A: {e}")
        return {"answer": None, "error": str(e), "confidence": 0.0}

@tool("get_document_info", return_direct=True)
def get_document_info() -> str:
    """
    Get information about the loaded document knowledge base.
    """
    try:
        vector_store, _ = _get_vector_store()
        info = f"Document Knowledge Base Information:\n"
        info += f"- Source: Swiss Airlines FAQ PDF\n"
        info += f"- Storage: FAISS store at {settings.FAISS_STORE_PATH}\n"
        info += f"- Embedding model: {settings.EMBEDDING_MODEL}\n"

        # Sample doc
        sample = vector_store.similarity_search("baggage", k=1)
        if sample:
            info += f"- Example content: {sample[0].page_content[:150]}...\n"

        return info
    except Exception as e:
        logger.error(f"Error getting document info: {e}")
        return f"Error: {str(e)}"

# Export
RAG_TOOLS = [search_documents, answer_question, get_document_info]
# print("=== TEST search_documents ===")
# res1 = search_documents.invoke({"query": "baggage policy", "num_results": 2})
# print(res1)

# print("=== TEST answer_question ===")
# res2 = answer_question.invoke({"question": "What is the checked baggage policy of Swiss Airlines?"})
# print(res2)
# res3 = get_document_info.invoke({})
# print(res3)