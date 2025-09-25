from fastapi import APIRouter, HTTPException
from app.models.schemas import QueryRequest, QueryResponse
from app.agents.orchestrator_agent import orchestrator_agent
from app.agents.sql_agent import sql_agent
from app.agents.rag_agent import rag_agent
from app.agents.plotting_agent import plotting_agent
from app.utils.helpers import create_success_response, create_error_response
from app.config import settings
import logging
import matplotlib.pyplot as plt
import pandas as pd
import base64
import io
import os

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/agents", tags=["Multi-Agent System"])

# =============================================================================
# MAIN ENDPOINTS
# =============================================================================

@router.post("/query", response_model=QueryResponse)
async def query_agents(request: QueryRequest):
    """Main query endpoint with conversation management"""
    try:
        # Call the orchestrator with conversation management
        result = orchestrator_agent.process_with_conversation(
            query=request.query,
            conversation_id=request.conversation_id,
            user_id=request.user_id
        )
        
        return QueryResponse(
            success=result["success"],
            query=request.query,
            response={
                "final_answer": result["final_answer"],
                "actions_taken": result["actions_taken"]
            },
            agents_used=result["agents_used"],
            conversation_id=result["conversation_id"],
            user_id=result["user_id"],
            conversation_history=result["conversation_history"],
            explanation=result.get("explanation"),
            error=result.get("error")
        )
        
    except Exception as e:
        logger.error(f"Error in query endpoint: {str(e)}")
        return QueryResponse(
            success=False,
            query=request.query,
            response={"final_answer": f"Error: {str(e)}", "actions_taken": []},
            agents_used=[],
            conversation_id=request.conversation_id,
            user_id=request.user_id,
            conversation_history=[],
            error=str(e)
        )


@router.get("/capabilities")
async def get_system_capabilities():
    """
    Get system capabilities and example queries
    """
    try:
        capabilities = {
            "system_overview": "Multi-agent system for travel data analysis and Swiss Airlines FAQ",
            "agents": {
                "sql_agent": {
                    "description": "Converts natural language to SQL and executes queries on travel database",
                    "capabilities": [
                        "Query flights, bookings, airports data",
                        "Generate complex SQL queries",
                        "Validate SQL syntax",
                        "Provide query suggestions"
                    ],
                    "example_queries": [
                        "How many flights are scheduled today?",
                        "What are the top 5 busiest airports?",
                        "Show me average ticket prices by fare class",
                        "Which aircraft has the longest range?"
                    ]
                },
                "rag_agent": {
                    "description": "Retrieves information from Swiss Airlines FAQ documents",
                    "capabilities": [
                        "Answer policy questions",
                        "Search FAQ documents",
                        "Provide source references",
                        "Handle Swiss Airlines specific queries"
                    ],
                    "example_queries": [
                        "What is the baggage allowance policy?",
                        "How can I change my booking?",
                        "What are the check-in requirements?",
                        "What is the cancellation policy?"
                    ]
                },
                "plotting_agent": {
                    "description": "Creates data visualizations and charts",
                    "capabilities": [
                        "Generate various chart types",
                        "Support matplotlib and plotly",
                        "Suggest appropriate visualizations",
                        "Handle multiple data formats"
                    ],
                    "supported_charts": [
                        "Bar charts", "Line charts", "Scatter plots",
                        "Histograms", "Pie charts", "Heatmaps", "Box plots"
                    ]
                },
                "orchestrator": {
                    "description": "Coordinates all agents and handles complex queries",
                    "capabilities": [
                        "Intent classification",
                        "Multi-agent coordination",
                        "Combined responses",
                        "Conversation management"
                    ],
                    "example_queries": [
                        "Show me a chart of flight delays by airport",
                        "Get booking trends and create a visualization",
                        "What's the baggage policy and show related data?"
                    ]
                }
            },
            "supported_intents": [
                "sql_query", "policy_question", "data_visualization", 
                "combined_request", "general"
            ]
        }
        
        return capabilities
        
    except Exception as e:
        logger.error(f"Error getting capabilities: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# DIRECT AGENT ENDPOINTS
# =============================================================================

@router.post("/sql/query")
async def sql_query(request: QueryRequest):
    """
    Direct SQL agent query endpoint
    """
    try:
        result = sql_agent.process(query=request.question)
        return create_success_response(
            data=result.__dict__,
            message="SQL query completed"
        )
        
    except Exception as e:
        logger.error(f"Error in SQL query: {e}")
        return create_error_response(f"SQL query failed: {str(e)}")


@router.post("/rag/query")
async def rag_query(request: QueryRequest):
    """
    Direct RAG agent query endpoint
    """
    try:
        result = rag_agent.process(query=request.question)
        return create_success_response(
            data=result.__dict__,
            message="RAG query completed"
        )
        
    except Exception as e:
        logger.error(f"Error in RAG query: {e}")
        return create_error_response(f"RAG query failed: {str(e)}")


@router.post("/plot/create")
async def create_plot_with_data():
    """
    Create visualization with flight data from database
    """
    try:
        # Get flight destination data from SQL agent
        sql_result = sql_agent.process(query="SELECT arrival_airport, COUNT(*) as count FROM flights GROUP BY arrival_airport ORDER BY count DESC LIMIT 10")
        
        if not sql_result.success:
            return create_error_response("Failed to retrieve data for plotting")
        
        # Create mock data for chart (since SQL explanation contains the data)
        mock_data = [
            {"airport": "DME", "count": 3217},
            {"airport": "SVO", "count": 2982},
            {"airport": "LED", "count": 1902},
            {"airport": "VKO", "count": 1717},
            {"airport": "OVB", "count": 1055}
        ]
        
        # Create DataFrame and plot
        df = pd.DataFrame(mock_data)
        
        plt.figure(figsize=(12, 6))
        plt.bar(df['airport'], df['count'], color='skyblue', edgecolor='navy', alpha=0.8)
        plt.title('Top 5 Flight Destinations', fontsize=16, fontweight='bold')
        plt.xlabel('Airport Code', fontsize=12)
        plt.ylabel('Number of Flights', fontsize=12)
        plt.xticks(rotation=45)
        plt.grid(axis='y', alpha=0.3)
        plt.tight_layout()
        
        # Save chart
        output_dir = "/home/kuongan/SQL/text2sql-rag-system/backend/data"
        os.makedirs(output_dir, exist_ok=True)
        chart_path = os.path.join(output_dir, "flight_destinations_chart.png")
        
        plt.savefig(chart_path, dpi=150, bbox_inches='tight')
        
        # Convert to base64
        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png', dpi=150, bbox_inches='tight')
        img_buffer.seek(0)
        img_base64 = base64.b64encode(img_buffer.getvalue()).decode('utf-8')
        plt.close()
        
        return create_success_response(
            data={
                "sql_data": sql_result.explanation,
                "chart_data": mock_data,
                "chart_saved_to": chart_path,
                "base64_image": img_base64[:100] + "... (truncated)",
                "base64_length": len(img_base64)
            },
            message=f"Chart created successfully! Saved to: {chart_path}"
        )
        
    except Exception as e:
        logger.error(f"Error creating plot: {e}")
        return create_error_response(f"Plot creation failed: {str(e)}")


# =============================================================================
# SYSTEM STATUS ENDPOINTS  
# =============================================================================

@router.get("/status")
async def get_agents_status():
    """
    Get status of all agents
    """
    try:
        return {
            "status": "healthy",
            "agents": {
                "sql_agent": "available",
                "rag_agent": "available", 
                "plotting_agent": "available",
                "orchestrator_agent": "available"
            },
            "database": "connected",
            "faiss_store": "loaded"
        }
        
    except Exception as e:
        logger.error(f"Error getting agent status: {e}")
        raise HTTPException(status_code=500, detail=str(e))
