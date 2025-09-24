"""
RAG Agent Model - Clean inheritance from BaseAgent
"""
import logging
from typing import List, Any, Type
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_core.tools import BaseTool

from app.agents.base_agent import BaseAgent
from app.models.agents import RAGAgentState, RAGAgentResult
from .tools import RAG_TOOLS
from .prompts import RAG_AGENT_PROMPT

logger = logging.getLogger(__name__)

class RAGAgent(BaseAgent[RAGAgentState]):
    """
    RAG Agent for document Q&A using Swiss Airlines FAQ PDF
    """

    def __init__(self, model_name: str = "gemini-1.5-flash", temperature: float = 0.3):
        super().__init__(
            agent_name="RAGAgent",
            model_name=model_name,
            temperature=temperature,
            enable_memory=True
        )
        logger.info("RAG Agent initialized with document search tools")

    def _get_tools(self) -> List[BaseTool]:
        return RAG_TOOLS

    def _get_agent_prompt(self) -> str:
        return RAG_AGENT_PROMPT

    def _get_state_type(self) -> Type[RAGAgentState]:
        return RAGAgentState

    def _create_initial_state(self, query: str, conversation_id: str) -> RAGAgentState:
        system_message = HumanMessage(content=f"{RAG_AGENT_PROMPT}\n\nUser Query: {query}")
        return RAGAgentState(
            messages=[system_message],
            user_query=query,
            agent_type="rag",
            conversation_id=conversation_id,
            metadata={},
            error=None,
            retrieved_documents=None,
            document_sources=None,
            answer=None,
            confidence_score=None,
            search_query=None
        )

    def _add_agent_context(self, messages: List[BaseMessage], state: RAGAgentState) -> List[BaseMessage]:
        if state.get("retrieved_documents"):
            docs_context = "Retrieved Documents:\n"
            for i, doc in enumerate(state["retrieved_documents"][:5]):
                docs_context += f"{i+1}. {doc}...\n"
            return messages + [HumanMessage(content=docs_context)]
        return messages

    def _process_tool_result(self, state: RAGAgentState, tool_name: str, result: Any) -> RAGAgentState:
        try:
            if tool_name == "search_documents":
                state["retrieved_documents"] = result.get("documents", [])
                state["document_sources"] = result.get("sources", [])
                state["search_query"] = result.get("query", "")
            elif tool_name == "answer_question":
                state["answer"] = result.get("answer")
                state["confidence_score"] = result.get("confidence")
                state["document_sources"] = result.get("sources", [])
            elif tool_name == "get_document_info":
                state["metadata"]["doc_info"] = result
        except Exception as e:
            state["error"] = f"Error processing {tool_name} result: {str(e)}"
            logger.error(state["error"])
        return state

    def _extract_result(self, final_state: RAGAgentState) -> RAGAgentResult:
        try:
            return RAGAgentResult(
                success=final_state.get("answer") is not None,
                answer=final_state.get("answer"),
                sources=final_state.get("document_sources", []),
                retrieved_docs=final_state.get("retrieved_documents", []),
                confidence=final_state.get("confidence_score"),
                error=final_state.get("error")
            )
        except Exception as e:
            return RAGAgentResult(success=False, error=f"Error extracting result: {str(e)}")

    def answer_question(self, question: str, conversation_id: str = "default") -> RAGAgentResult:
        return self.process(question, conversation_id)

rag_agent = RAGAgent()

if __name__ == "__main__":
    print("=== TEST RAG AGENT ===")
    questions = [
        "What is the checked baggage policy of Swiss Airlines?",
        "How can I change my booking?",
        "Do I need to reconfirm my Swiss flight?",
        "What payment methods are accepted?"
    ]
    for q in questions:
        print(f"\n--- QUESTION: {q} ---")
        result = rag_agent.answer_question(q, conversation_id="test-123")
        print("Success:", result.success)
        print("Answer:", result.answer)
        print("Sources:", result.sources[:3])  # show 3 sources
        print("Confidence:", result.confidence)