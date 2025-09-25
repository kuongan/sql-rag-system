from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from .base import BaseAgentState, BaseAgentResult

class AgentInput(BaseModel):
    """Input for agent execution"""
    query: str = Field(description="The user query to process")
    context: Optional[Any] = Field(default=None, description="Additional context or data")

class OrchestratorState(BaseAgentState):
    """State for ReAct Orchestrator"""
    actions_taken: List[Dict[str, Any]] = Field(default_factory=list)
    current_data: Optional[Dict[str, Any]] = Field(default=None)  # Store data between agents
    iteration_count: int = Field(default=0)

class OrchestratorResult(BaseAgentResult):
    """Result from orchestrator agent"""
    def __init__(self, success: bool, error: Optional[str] = None, 
                 actions_taken: List[Dict[str, Any]] = None,
                 final_data: Optional[Any] = None,
                 visualization: Optional[Dict[str, Any]] = None,
                 answer: Optional[str] = None,
                 thought: Optional[str] = None):
        super().__init__(success, error)
        self.actions_taken = actions_taken or []
        self.final_data = final_data
        self.visualization = visualization
        self.answer = answer
        self.thought = thought