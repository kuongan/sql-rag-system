import logging
from typing import Dict, Any, List, Type
import json

from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.tools import BaseTool
from langchain_core.runnables import RunnableConfig

from app.models.agents.base import BaseAgentResult
from app.agents.base_agent import BaseAgent
from app.models.agents import PlottingAgentState, PlottingAgentResult
from .tools import PLOTTING_TOOLS
from .prompts import PLOTTING_AGENT_PROMPT

logger = logging.getLogger(__name__)

class PlottingAgent(BaseAgent[PlottingAgentState]):
    def __init__(self, model_name: str = "gemini-2.5-flash-lite", temperature: float = 0.0):
        super().__init__(
            agent_name="PlottingAgent",
            model_name=model_name,
            temperature=temperature,
            enable_memory=True
        )
        logger.info("PlottingAgent initialized with tools: %s", [t.name for t in self.tools])

    def _get_tools(self) -> List[BaseTool]:
        return PLOTTING_TOOLS

    def _get_agent_prompt(self) -> str:
        return PLOTTING_AGENT_PROMPT

    def _get_state_type(self) -> Type[PlottingAgentState]:
        return PlottingAgentState

    def _create_initial_state(self, query: str, conversation_id: str, **kwargs) -> PlottingAgentState:
        system_message = SystemMessage(content=self._get_agent_prompt())
        human_message = HumanMessage(content=query)
        plot_data = kwargs.get("plot_data", None)
        logger.info(f"Initial plot_data received: {type(plot_data)}")
        if plot_data is not None:
            if isinstance(plot_data, str):
                try:
                    import json
                    plot_data = json.loads(plot_data)
                    logger.info(f"Parsed plot_data from JSON string to: {type(plot_data)}")
                except Exception as e:
                    logger.warning(f"Could not parse plot_data as JSON: {e}")
                    try:
                        import ast
                        plot_data = ast.literal_eval(plot_data)
                        logger.info(f"Parsed plot_data with ast.literal_eval: {type(plot_data)}")
                    except Exception as e2:
                        logger.warning(f"Could not parse plot_data with ast: {e2}")        

        return PlottingAgentState(
            messages=[system_message, human_message],
            user_query=query,
            agent_type="plotting",
            conversation_id=conversation_id,
            metadata={},
            error=None,
            plot_data=plot_data,
            plot_type=None,
            image_base64=None,
            figure_json=None,
            analysis_result=None,
            chart_config=None
        )

    def _add_agent_context(self, messages, state):
        plot_data = state.get("plot_data") or state.get("metadata", {}).get("plot_data")
        if plot_data:
            context_msg = HumanMessage(
                content=f"""Plot data is available: {plot_data}\n\n""")
            return messages + [context_msg]
        return messages

    def _update_agent_state(self, state: PlottingAgentState, response):
        # Nếu response là AIMessage
        if hasattr(response, "additional_kwargs") and "function_call" in response.additional_kwargs:
            func_call = response.additional_kwargs["function_call"]
            args_str = func_call.get("arguments", "{}")
            try:
                args = json.loads(args_str)
            except Exception as e:
                logger.warning(f"Cannot parse function_call arguments: {e}")
                args = {}
            # Update state từ args dict
            state["plot_type"] = args.get("plot_type", state.get("plot_type"))
            state["image_base64"] = args.get("image_base64", state.get("image_base64"))
            state["figure_json"] = args.get("figure_json", state.get("figure_json"))
            state["chart_config"] = args.get("config", state.get("chart_config"))
            state["analysis_result"] = args.get("analysis", state.get("analysis_result"))
            state["error"] = args.get("error", state.get("error"))
        return state

    def _process_tool_result(self, state: PlottingAgentState, tool_name: str, result: Any):
        # Không return dict, chỉ update state
        if tool_name == "analyze_data":
            state["analysis_result"] = result
        elif tool_name in ["bar_chart", "line_chart", "pie_chart"]:
            state["plot_type"] = result.get("plot_type") if isinstance(result, dict) else None
            state["image_base64"] = result.get("image_base64") if isinstance(result, dict) else None
            state["figure_json"] = result.get("figure_json") if isinstance(result, dict) else None
            state["chart_config"] = result.get("config") if isinstance(result, dict) else None
        return state

    def _extract_result(self, final_state: PlottingAgentState) -> PlottingAgentResult:
        """
        Trích xuất kết quả cuối cùng từ state
        """
        success = final_state.get("image_base64") is not None or final_state.get("analysis_result") is not None
        return PlottingAgentResult(
            success=success,
            plot_type=final_state.get("plot_type"),
            image_base64=final_state.get("image_base64"),
            figure_json=final_state.get("figure_json"),
            analysis=final_state.get("analysis_result"),
            chart_config=final_state.get("chart_config"),
            error=final_state.get("error")
        )
        
    def create_visualization(self, data: list, plot_request: str, conversation_id: str = "default") -> PlottingAgentResult:
        return self.process(plot_request, conversation_id=conversation_id, plot_data=data)

plotting_agent = PlottingAgent()

# # Sample SQL-like data
# sample_data = [
#     {"flight_id": 1, "departure": "vt", "arrival": "hcm", "price": 120},
#     {"flight_id": 2, "departure": "Hn", "arrival": "Dn", "price": 80},
#     {"flight_id": 3, "departure": "hcm", "arrival": "Hn", "price": 130},
#     {"flight_id": 4, "departure": "Dn", "arrival": "Hn", "price": 90},
#     {"flight_id": 5, "departure": "Hn", "arrival": "Hue", "price": 70},
# ]

# # 1️⃣ Test analysis
# print("\n=== Agent Data Analysis Test ===")
# analysis_result = plotting_agent.create_visualization(
#     data=sample_data,
#     plot_request="Analyze the dataset and provide visualization recommendations",
#     conversation_id="test_analysis"
# )
# print("Success:", analysis_result.success)

# # 2️⃣ Test static plot
# print("\n=== Agent Static Plot Test (Bar) ===")
# static_result = plotting_agent.create_visualization(
#     data=sample_data,
#     plot_request="Create a pie plot of flight prices by departure city",
#     conversation_id="test_static"
# )
# print("Success:", static_result.success)
# print("Plot Type:", static_result.plot_type)
# print("Image Base64 (first 100 chars):", str(static_result.image_base64)[:100], "...")
# print("Error:", static_result.error, "\n")
