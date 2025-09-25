"""
Plotting Agent Models - State, result structures and input schemas for Plotting Agent
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List

from .base import BaseAgentState, BaseAgentResult

# Input schemas for tools
class PlotCreationInput(BaseModel):
    """Input schema for plot creation"""
    data: List[Dict[str, Any]] = Field(description="the data to plot")
    plot_type: Optional[str] = Field(description="Type of plot: bar, line, scatter, histogram, pie, box, heatmap")
    title: Optional[str] = Field(default=None, description="Title for the plot")
    x_column: Optional[str] = Field(default=None, description="Column name for x-axis")
    y_column: Optional[str] = Field(default=None, description="Column name for y-axis")

class DataAnalysisInput(BaseModel):
    """Input schema for data analysis"""
    data: List[Dict[str, Any]] = Field(description="the data to analyze")

# Agent state and result
class PlottingAgentState(BaseAgentState):
    """State for Plotting Agent extending base state"""
    plot_data: Optional[List[Dict[str, Any]]]
    plot_type: Optional[str]
    image_base64: Optional[str]
    figure_json: Optional[str]
    analysis_result: Optional[str]
    chart_config: Optional[Dict[str, Any]]

class PlottingAgentResult(BaseAgentResult):
    """Result structure for Plotting Agent"""
    def __init__(self, success: bool, plot_type: Optional[str] = None,
                 image_base64: Optional[str] = None,
                 figure_json: Optional[str] = None,
                 analysis: Optional[str] = None,
                 chart_config: Optional[Dict[str, Any]] = None,
                 error: Optional[str] = None):
        super().__init__(success, error)
        self.plot_type = plot_type or ""
        self.image_base64 = image_base64
        self.figure_json = figure_json
        self.analysis = analysis
        self.chart_config = chart_config
        self.agent_type = "plotting"
