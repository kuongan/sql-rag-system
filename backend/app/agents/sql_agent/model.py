"""
SQL Agent Model - Clean inheritance from BaseAgent
"""
import logging
from typing import  Any, List, Type
import re
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_core.tools import BaseTool
from app.agents.base_agent import BaseAgent
from app.models.agents import SQLAgentState, SQLAgentResult
from .tools import SQL_TOOLS
from .prompts import SQL_AGENT_SYSTEM_PROMPT

logger = logging.getLogger(__name__)

class SQLAgent(BaseAgent[SQLAgentState]):
    """
    SQL Agent for database querying with natural language to SQL conversion
    Inherits from BaseAgent for clean, extensible architecture
    """
    
    def __init__(self, model_name: str = "gemini-1.5-flash", temperature: float = 0.0):
        super().__init__(
            agent_name="SQLAgent",
            model_name=model_name,
            temperature=temperature,
            enable_memory=True
        )
        logger.info("SQL Agent initialized with database tools")
    
    def _get_tools(self) -> List[BaseTool]:
        """Get SQL-specific tools"""
        return SQL_TOOLS
    
    def _get_agent_prompt(self) -> str:
        """Get SQL agent prompt"""
        return SQL_AGENT_SYSTEM_PROMPT
    
    def _get_state_type(self) -> Type[SQLAgentState]:
        """Return the state type for this agent"""
        return SQLAgentState
      
    def _create_initial_state(self, query: str, conversation_id: str) -> SQLAgentState:
        """Create initial state for SQL processing"""
        # Add SQL-specific prompt to the query
        system_message = HumanMessage(content=f"{SQL_AGENT_SYSTEM_PROMPT}\n\nUser Query: {query}")
        
        return SQLAgentState(
            messages=[system_message],
            user_query=query,
            agent_type="sql",
            conversation_id=conversation_id,
            metadata={},
            error=None,
            sql_query=None,
            sql_data=None,
            row_count=None,
            database_schema=None
        )
    
    def _add_agent_context(self, messages: List[BaseMessage], state: SQLAgentState) -> List[BaseMessage]:
        """Add SQL-specific context to messages"""
        # If we have database schema info, add it to context
        if state.get("database_schema"):
            context_msg = HumanMessage(
                content=f"Database Schema Available:\n{state['database_schema']}"
            )
            return messages + [context_msg]
        return messages
    
    def _process_tool_result(self, state: SQLAgentState, tool_name: str, result: Any) -> SQLAgentState:
        """Process SQL tool results and update state (compact version)"""
        try:
            if tool_name == "get_database_schema":
                state["database_schema"] = str(result)
                logger.info("Database schema retrieved and stored in state")

            elif tool_name == "execute_sql_query":
                state["sql_query"], state["sql_data"], state["row_count"] = "", [], 0
                m = re.search(r"Results \((\d+) rows\):", result)
                if m:
                    state["row_count"] = int(m.group(1))
                m = re.search(r"SQL Query:\s*(.*)", result)
                if m:
                    state["sql_query"] = m.group(1).strip()
                data_rows = []
                for line in result.splitlines():
                    line = line.strip()
                    if line.startswith("Row ") and ":" in line:
                        data_part = line.split(":", 1)[1].strip()
                        if data_part.startswith("{") and data_part.endswith("}"):
                            try:
                                row_dict = eval(data_part)
                                if isinstance(row_dict, dict):
                                    data_rows.append(row_dict)
                            except Exception:
                                pass
                        elif data_part.startswith("(") and data_part.endswith(")"):
                            values = [v.strip().strip("'\"") for v in data_part[1:-1].split(",")]
                            data_rows.append({f"column_{i}": v for i, v in enumerate(values)})
                state["sql_data"] = data_rows
                state["row_count"] = len(data_rows)

                logger.info(f"SQL execution completed: {state['row_count']} rows returned")
            return state

        except Exception as e:
            logger.error(f"Error processing tool result: {e}")
            state["error"] = f"Error processing {tool_name} result: {str(e)}"
            return state
    
    def _extract_result(self, final_state: SQLAgentState) -> SQLAgentResult:
        """Extract SQL result from final state"""
        try:
            # Determine success based on whether we have data and no errors
            success = (final_state.get("sql_data") is not None and 
                      final_state.get("error") is None)
            
            # Create explanation from messages
            explanation = self._create_explanation(final_state)
            
            return SQLAgentResult(
                success=success,
                sql_query=final_state.get("sql_query"),
                data=final_state.get("sql_data", []),
                row_count=final_state.get("row_count", 0),
                explanation=explanation,
                error=final_state.get("error")
            )
            
        except Exception as e:
            logger.error(f"Error extracting SQL result: {e}")
            return SQLAgentResult(
                success=False,
                error=f"Error extracting result: {str(e)}"
            )
    
    def _create_explanation(self, state: SQLAgentState) -> str:
        """Create explanation from agent messages"""
        try:
            ai_messages = [
                msg.content for msg in state["messages"] 
                if isinstance(msg, AIMessage) and msg.content
            ]
            
            if ai_messages:
                return ai_messages[-1] 
            
            return "SQL query processed successfully"
            
        except Exception as e:
            logger.warning(f"Error creating explanation: {e}")
            return "SQL processing completed"
    
    def generate_sql(self, natural_language_query: str, conversation_id: str = "default") -> SQLAgentResult:
        """
        Generate and execute SQL from natural language query
        
        Args:
            natural_language_query: Natural language description of desired query
            conversation_id: Conversation ID for context
            
        Returns:
            SQLAgentResult with query results
        """
        return self.process(natural_language_query, conversation_id)
    
sql_agent = SQLAgent()


if __name__ == "__main__":
    print("=== TEST SQL AGENT ===")
    print("\n--- TEST 2: List 5 flights ---")
    result = sql_agent.generate_sql("List all airports with city and timezone.")
    print("Success:", result.success)
    print("SQL Query:", result.sql_query)
    print("Row Count:", result.row_count)
    print("Data:", result.data)
    print("Explanation:", result.explanation)
    print("Error:", result.error)

    print("\n--- TEST 3: Count bookings ---")
    result = sql_agent.generate_sql("the number of tickets sold in each fare class")
    print("Success:", result.success)
    print("SQL Query:", result.sql_query)
    print("Row Count:", result.row_count)
    print("Data:", result.data)
    print("Explanation:", result.explanation)
    print("Error:", result.error)