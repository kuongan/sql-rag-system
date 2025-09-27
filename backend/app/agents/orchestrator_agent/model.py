import logging
from typing import Dict, Any, List, Type
import json

from langchain_core.messages import SystemMessage, HumanMessage, BaseMessage, AIMessage
from langchain_core.tools import BaseTool
from app.agents.base_agent import BaseAgent
from app.models.agents.orchestrator import OrchestratorState, OrchestratorResult
from app.utils.manager import ConversationManager
from .tools import REACT_TOOLS
from .prompts import REACT_ORCHESTRATOR_PROMPT

logger = logging.getLogger(__name__)


class OrchestratorAgent(BaseAgent[OrchestratorState]):
    """
    ReAct-based Orchestrator Agent that coordinates other specialized agents
    """
    
    def __init__(self, model_name: str = "gemini-2.5-flash-lite", temperature: float = 0.1):
        super().__init__(
            agent_name="OrchestratorAgent",
            model_name=model_name,
            temperature=temperature,
            enable_memory=True
        )
        self.conversation_manager: ConversationManager = ConversationManager()
        logger.info("OrchestratorAgent initialized with tools: %s", [t.name for t in self.tools])

    def _get_tools(self) -> List[BaseTool]:
        return REACT_TOOLS

    def _get_agent_prompt(self) -> str:
        return REACT_ORCHESTRATOR_PROMPT

    def _get_state_type(self) -> Type[OrchestratorState]:
        return OrchestratorState

    def _create_initial_state(self, query: str, conversation_id: str, **kwargs) -> OrchestratorState:
        system_message = SystemMessage(content=self._get_agent_prompt())
        human_message = HumanMessage(content=f"User Query: {query}")
        
        return OrchestratorState(
            messages=[system_message, human_message],
            user_query=query,
            agent_type="orchestrator",
            conversation_id=conversation_id,
            metadata=kwargs,
            error=None,
            actions_taken=[],
            current_data=None,
            iteration_count=0
        )

    def _add_agent_context(self, messages: List[BaseMessage], state) -> List[BaseMessage]:
        """
        Add context about previous actions and current data 
        """
        context_msgs = []

        # Combine all previous actions into a single message
        actions_taken = state.get("actions_taken", [])
        if actions_taken:
            actions_content = ", ".join([str(action) for action in actions_taken])
            context_msgs.append(HumanMessage(content=f"Previous actions: {actions_content}"))

        # Add current data if available
        current_data = state.get("current_data")
        if current_data:
            context_msgs.append(HumanMessage(content=f"Current data context:\n{current_data}"))

        return messages + context_msgs
    
    def _preprocess_tool_args(self, tool_args: Dict[str, Any], state) -> Dict[str, Any]:
        """Add conversation_id and context to tool arguments"""
        # Always add conversation_id
        tool_args["conversation_id"] = state.get("conversation_id", "default")
        
        # For plotting agent, extract just the data array
        current_data = state.get("current_data")
        if current_data and isinstance(current_data, dict):
            # If it's a result from SQL agent, extract the data array
            if current_data.get("agent_type") == "sql" and current_data.get("data"):
                tool_args["context"] = current_data["data"]  # Just the data array
            elif not tool_args.get("context"):
                tool_args["context"] = current_data
            
        return tool_args
    
    def _update_agent_state(self, state, response):
        """
        Update the orchestrator state after LLM/tool response.
        """
        if hasattr(response, "additional_kwargs") and "function_call" in response.additional_kwargs:
            func_call = response.additional_kwargs["function_call"]
            args_str = func_call.get("arguments", "{}")
            try:
                args = json.loads(args_str)
            except Exception as e:
                logger.warning(f"Cannot parse function_call arguments: {e}")
                args = {}
            action = {
                "tool_name": func_call.get("name"),
                "args": args
            }
            state["actions_taken"] = state.get("actions_taken", [])
            state["actions_taken"].append(action)
            if "result" in args:
                state["current_data"] = args["result"]
            state["iteration_count"] = state.get("iteration_count", 0) + 1
        elif isinstance(response, AIMessage):
            state["iteration_count"] = state.get("iteration_count", 0) + 1
        return state

    def _process_tool_result(self, state, tool_name: str, result: Any):
        """Process tool results and update orchestrator state"""
        state["iteration_count"] = state.get("iteration_count", 0) + 1
        action_record = {
            "tool_name": tool_name,
            "success": result.get("success", False) if isinstance(result, dict) else False,
            "iteration": state["iteration_count"]
        }
        
        # Store full result data for later use
        if isinstance(result, dict):
            action_record["result"] = result
            if result.get("success"):
                state["current_data"] = result
        
        state["actions_taken"] = state.get("actions_taken", [])
        state["actions_taken"].append(action_record)
        logger.info(f"Orchestrator processed {tool_name} - Success: {action_record['success']}")
        return state

    def _needs_finalization(self, state) -> bool:
        actions_taken = state.get("actions_taken", [])
        iteration_count = state.get("iteration_count", 0)
        return len(actions_taken) > 0 and iteration_count < 5

    def _extract_result(self, final_state) -> OrchestratorResult:
        """
        Extract final answer combining agent's last message and last tool's result.
        """
        actions = final_state.get("actions_taken", [])
        current_data = final_state.get("current_data")
        thought = ""
        final_answer_parts = []

        if actions:
            last_tool_result = actions[-1].get("result") or {}
            if isinstance(last_tool_result, dict) and last_tool_result.get("answer"):
                final_answer_parts.append(last_tool_result["answer"])

        # Lấy content từ last_message nếu có
        messages = final_state.get("messages", [])
        if messages:
            last_message = messages[-1]
            if hasattr(last_message, "content"):
                content = last_message.content
                if "Thought:" in content and "Final Answer:" in content:
                    parts = content.split("Final Answer:")
                    thought = parts[0].replace("Thought:", "").strip()
                    final_answer_parts.append(parts[1].strip())
                elif "Final Answer:" in content:
                    final_answer_parts.append(content.split("Final Answer:")[-1].strip())
                else:
                    final_answer_parts.append(content)

        # Kết hợp các phần thành final_answer duy nhất
        final_answer = " ".join(final_answer_parts).strip()

        # Nếu final_data là RAG agent, ưu tiên answer từ RAG
        if current_data and isinstance(current_data, dict):
            if current_data.get("agent_type") == "rag" and current_data.get("answer"):
                final_answer = current_data["answer"]

        return OrchestratorResult(
            success=not bool(final_state.get("error")),
            error=final_state.get("error"),
            actions_taken=actions,
            final_data=current_data,
            answer=final_answer,
            thought=thought
        )


    def process(self, query: str, conversation_id: str = "default", **kwargs) -> OrchestratorResult:
        """
        Override base process method to handle OrchestratorResult properly
        """
        try:
            logger.info(f"{self.agent_name} processing query: {query[:100]}...")
            
            # Create initial state
            initial_state = self._create_initial_state(query, conversation_id, **kwargs)
            
            # Add any additional kwargs to metadata
            if kwargs:
                initial_state["metadata"] = initial_state.get("metadata", {})
                initial_state["metadata"].update(kwargs)
            
            from langchain_core.runnables import RunnableConfig
            config = RunnableConfig(
                configurable={"thread_id": conversation_id}
            ) if self.enable_memory else None
            
            final_state = self.graph.invoke(initial_state, config)
            
            return self._extract_result(final_state)
            
        except Exception as e:
            logger.error(f"Error processing query in {self.agent_name}: {e}")
            # Return proper OrchestratorResult for error case
            return OrchestratorResult(
                success=False,
                error=str(e),
                actions_taken=[],
                final_data=None,
                answer=f"Error: {str(e)}",
                thought=None
            )

    def process_with_conversation(self, query: str, conversation_id: str = "default", user_id: str = "anonymous", **kwargs) -> Dict[str, Any]:
        """
        Process query, store conversation history, and return structured result.
        """
        self.conversation_manager.add_message(conversation_id, user_id, {"role": "user", "content": query})
        try:
            result = self.process(query, conversation_id, **kwargs)
            if isinstance(result, dict):
                result = OrchestratorResult(**result)

            # Lấy answer từ final_data nếu là RAG tool
            final_answer = result.answer
            if result.final_data and isinstance(result.final_data, dict) and result.final_data.get("agent_type") == "rag":
                final_answer = result.final_data.get("answer", final_answer)

            actions_taken = result.actions_taken or []
            agents_used = list({a.get("tool_name", "unknown").replace("_agent", "") for a in actions_taken})
            thought = result.thought

            self.conversation_manager.add_message(conversation_id, user_id, {
                "role": "assistant",
                "content": final_answer,
                "actions": actions_taken,
                "thought": thought
            })

            return {
                "success": result.success,
                "final_answer": final_answer or "I processed your request.",
                "thought": thought,
                "data": result.final_data,  # Include actual data
                "actions_taken": actions_taken,
                "agents_used": agents_used,
                "conversation_history": self.conversation_manager.get_history(conversation_id, user_id),
                "conversation_id": conversation_id,
                "user_id": user_id
            }

        except Exception as e:
            error_msg = f"An error occurred: {str(e)}"
            self.conversation_manager.add_message(conversation_id, user_id, {"role": "assistant", "content": error_msg, "error": True})
            return {
                "success": False,
                "final_answer": error_msg,
                "actions_taken": ["Error occurred"],
                "agents_used": [],
                "conversation_history": self.conversation_manager.get_history(conversation_id, user_id),
                "conversation_id": conversation_id,
                "user_id": user_id
            }
# Initialize orchestrator agent
orchestrator_agent = OrchestratorAgent()

def main():
    print("\n=== Test 1: Greeting ===")
    query1 = "Create a bar chart showing the top 10 most popular flight destinations"
    result1 = orchestrator_agent.process_with_conversation(query=query1)
    print(json.dumps(result1, indent=2, ensure_ascii=False))

    # print("\n=== Test 2: SQL Data Query ===")
    # query2 = "Get the first 5 flights"
    # result2 = orchestrator_agent.process_with_conversation(query=query2)
    # print(json.dumps(result2, indent=2, ensure_ascii=False))

    # print("\n=== Test 3: RAG / Policy Query ===")
    # query3 = "What is the checked baggage policy of Swiss Airlines?"
    # result3 = orchestrator_agent.process_with_conversation(query=query3)
    # print(json.dumps(result3, indent=2, ensure_ascii=False))

    # print("\n=== Test 4: Visualization Request ===")
    # query4 = "Create a bar plot of flight prices "
    # result4 = orchestrator_agent.process_with_conversation(query=query4, user_id="test_user")
    # print(json.dumps(result4, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()

