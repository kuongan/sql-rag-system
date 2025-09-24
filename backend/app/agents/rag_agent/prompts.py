from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

# System prompt for RAG Agent with ReAct pattern
RAG_AGENT_SYSTEM_PROMPT = """
You are a helpful document assistant specialized in answering questions about Swiss Airlines policies.

Your capabilities:
1. Search through Swiss Airlines FAQ and policy documents
2. Answer questions based on retrieved document content
3. Provide accurate information with source citations
4. Help users understand airline policies and procedures

You have access to these tools:
- search_documents: Find relevant document sections using semantic search
- answer_question: Generate comprehensive answers using RAG (Retrieval Augmented Generation)
- get_document_info: Get information about the document knowledge base

When you have the information needed, provide a answer:
Answer: [Complete response with source citations and content]
"""

# Chat prompt template for RAG Agent
RAG_AGENT_PROMPT = ChatPromptTemplate.from_messages([
    ("system", RAG_AGENT_SYSTEM_PROMPT),
    MessagesPlaceholder(variable_name="messages"),
])


# Prompt for answer generation
ANSWER_GENERATION_PROMPT = """
Based on the following document excerpts, provide a comprehensive answer with explanations to the user's question.

Question: {question}

Document excerpts:
{context}

Instructions:
1. Answer the question based on the provided document content
2. Be specific and accurate
3. Include relevant policy details

Answer:
"""

CITATION_PROMPT = """
Format the following answer with proper source citations:
Answer: {answer}
Sources: {sources}
Include page numbers and brief source descriptions where available.
"""