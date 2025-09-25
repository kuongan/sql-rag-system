import logging
import json
from typing import Dict, Any, List, Optional
from langchain_core.tools import BaseTool, tool
from pydantic import BaseModel, Field
import ast
from app.agents.sql_agent.model import sql_agent
from app.agents.rag_agent.model import rag_agent 
from app.agents.plotting_agent.model import plotting_agent
from app.models.agents.orchestrator import AgentInput

logger = logging.getLogger(__name__)

@tool("sql_agent", args_schema=AgentInput)
def use_sql_agent(query: str, context: Optional[Any] = None, conversation_id: str = "default") -> Dict[str, Any]:
    """
    Execute SQL queries on the flight database. Use this for:
    - Searching flights by departure, arrival, price, date
    - Getting flight statistics and counts
    - Filtering and aggregating flight data
    - Any database-related queries about flights
    
    Returns structured data that can be used by other agents.
    """
    try:
        logger.info(f"SQL Agent called with query: {query}")
        
        # Use the SQL agent to process the query
        result = sql_agent.generate_sql(query, conversation_id)
        
        return {
            "success": result.success,
            "sql_query": result.sql_query,
            "data": result.data,
            "answer": result.explanation,
            "error": result.error,
            "agent_type": "sql"
        }
    except Exception as e:
        logger.error(f"Error in SQL agent: {e}")
        return {
            "success": False,
            "error": str(e),
            "agent_type": "sql"
        }

@tool("rag_agent", args_schema=AgentInput)
def use_rag_agent(query: str, context: Optional[Any] = None, conversation_id: str = "default") -> Dict[str, Any]:
    """
    Answer questions using Swiss Airlines policy documents. Use this for:
    - Swiss Airlines baggage policies
    - Flight booking procedures
    - Travel regulations and requirements
    - Customer service information
    - Any questions about Swiss Airlines services
    
    Returns detailed answers from official documentation.
    """
    try:
        logger.info(f"RAG Agent called with query: {query}")
        
        # Use the RAG agent to process the query
        result = rag_agent.answer_question(query, conversation_id)
        
        return {
            "success": result.success,
            "answer": result.answer,
            "data": result.sources,
            "confidence": result.confidence,
            "error": result.error,
            "agent_type": "rag"
        }
    except Exception as e:
        logger.error(f"Error in RAG agent: {e}")
        return {
            "success": False,
            "error": str(e),
            "agent_type": "rag"
        }

@tool("plotting_agent", args_schema=AgentInput)
def use_plotting_agent(query: str, context: Optional[Any] = None,  conversation_id: str = "default") -> Dict[str, Any]:
    """
    Create charts and visualizations from data. Use this for:
    - Creating bar charts, line charts, pie charts, scatter plots
    - Visualizing flight data trends
    - Data analysis and insights
    - Statistical summaries
    
    Context should contain the data to plot (list of dictionaries or JSON string).
    Returns base64 encoded images and analysis results.
    """
    try:
        logger.info(f"Plotting Agent called with query: {query}")
        
        # Parse context data if provided
        plot_data = None
        if context:
            try:
                # Try to parse as JSON first
                if isinstance(context, str):
                    plot_data = json.loads(context)
                else:
                    plot_data = context
            except json.JSONDecodeError:
                # Try ast.literal_eval for Python literal structures
                try:
                    plot_data = ast.literal_eval(context)
                except:
                    logger.warning(f"Could not parse context data: {context}")
        

        result = plotting_agent.create_visualization(plot_request=query,data = plot_data, conversation_id=conversation_id)
        
        return {
            "success": result.success,
            "plot_type": result.plot_type,
            "data": result.image_base64,
            "figure_json": result.figure_json,
            "analysis": result.analysis,
            "chart_config": result.chart_config,
            "error": result.error,
            "agent_type": "plotting"
        }
    except Exception as e:
        logger.error(f"Error in Plotting agent: {e}")
        return {
            "success": False,
            "error": str(e),
            "agent_type": "plotting"
        }      

REACT_TOOLS = [
    use_sql_agent,
    use_rag_agent, 
    use_plotting_agent
]

# Simple descriptions
TOOL_DESCRIPTIONS = {
    "sql_agent": "Generate SQL from natural language queries, execute on the database, and return structured results.",
    "rag_agent": "Answer questions from documents", 
    "plotting_agent": "Create charts and visualizations",
}

def get_orchestrator_tools() -> List[BaseTool]:

    """Get all orchestrator tools"""
    return REACT_TOOLS


def run_tests():

    print("\n=== Test sql_agent ===")
    query2 = "Get the first 5 flights"
    result2 = use_sql_agent.run({"query": query2})
    print(json.dumps(result2, indent=2, ensure_ascii=False))
    
    print("\n=== Test rag_agent ===")
    query3 = "What is the checked baggage policy of Swiss Airlines?"
    result3 = use_rag_agent.run({"query": query3})
    print(json.dumps(result3, indent=2, ensure_ascii=False))
    print("\n=== Test plotting_agent ===")
    query4 = "Create a static bar plot of flight prices by departure city using 'departure' as X and 'price' as Y"
    # Example context data  
    context4 = [
        {"departure": "Hanoi", "price": 120},
        {"departure": "Ho Chi Minh City", "price": 150},
        {"departure": "Da Nang", "price": 100},
    ]
    result4 = use_plotting_agent.run({"query": query4, "context": context4})
    print(json.dumps(result4, indent=2, ensure_ascii=False))
if __name__ == "__main__":
    run_tests()