import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import base64
from typing import Optional, Dict, Any, List
from langchain_core.tools import tool
from app.models.agents.plotting import PlotCreationInput, DataAnalysisInput
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import base64
from typing import Optional, Dict, Any, List
from langchain_core.tools import tool
from pydantic import BaseModel, Field

# === Helper functions ===
def _save_plot(plot_type: str, title: str = None) -> str:
    os.makedirs("images", exist_ok=True)
    filename = f"images/{plot_type}.png"
    plt.title(title or f"{plot_type.capitalize()} Chart")
    plt.tight_layout()
    plt.savefig(filename, format="png", dpi=150, bbox_inches="tight")
    plt.close()
    with open(filename, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

# === Data analysis tool ===
@tool("analyze_data", args_schema=DataAnalysisInput)
def analyze_data(data: List[Dict[str, Any]]) -> str:
    """
    Analyze the input data and return a summary report including
    dataset shape, column types, numeric summaries, and plotting recommendations.
    """
    df = pd.DataFrame(data)
    
    analysis = f"📊 Data Analysis Report:\n\n"
    analysis += f"📈 Dataset Overview:\n"
    analysis += f"  • Shape: {df.shape[0]} rows × {df.shape[1]} columns\n"
    analysis += f"  • Columns: {list(df.columns)}\n\n"
    
    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
    categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
    
    analysis += f"📊 Column Types:\n"
    analysis += f"  • Numeric columns ({len(numeric_cols)}): {numeric_cols}\n"
    analysis += f"  • Categorical columns ({len(categorical_cols)}): {categorical_cols}\n\n"
    
    if numeric_cols:
        analysis += f"📈 Numeric Data Summary:\n"
        for col in numeric_cols[:3]:
            analysis += f"  • {col}: min={df[col].min():.2f}, max={df[col].max():.2f}, mean={df[col].mean():.2f}\n"
    
    analysis += f"Plotting Recommendations:\n"
    if categorical_cols and numeric_cols:
        analysis += f"  • X-axis (categorical): {categorical_cols[0]}\n"
        analysis += f"  • Y-axis (numeric): {numeric_cols[0]}\n"
        analysis += f"  • Plot types: bar, pie chart\n"
    elif len(numeric_cols) >= 2:
        analysis += f"  • X-axis: {numeric_cols[0]}\n"
        analysis += f"  • Y-axis: {numeric_cols[1]}\n"
        analysis += f"  • Plot types: scatter, line plot\n"
    elif categorical_cols:
        cat_col = categorical_cols[0]
        value_counts = df[cat_col].value_counts()
        analysis += f"  • Categories in '{cat_col}': {list(value_counts.index[:5])}...\n"
        analysis += f"  • Plot types: pie chart, bar chart of counts\n"
    
    return analysis

# === Plotting tools ===
@tool("bar_chart", args_schema=PlotCreationInput)
def bar_chart(data: List[Dict[str, Any]], plot_type: str, x_column: str, y_column: str, title: str = None) -> Dict[str, Any]:
    """
    Create a bar chart from the input data using x_column and y_column.
    Returns a dict with plot_type, image_base64, and config.
    """
    df = pd.DataFrame(data)
    sns.barplot(data=df, x=x_column, y=y_column)
    return {
        "plot_type": "bar",
        "image_base64": _save_plot("bar", title),
        "config": {"x_column": x_column, "y_column": y_column, "title": title}
    }

@tool("line_chart", args_schema=PlotCreationInput)
def line_chart(data: List[Dict[str, Any]], plot_type: str, x_column: str, y_column: str, title: str = None) -> Dict[str, Any]:
    """
    Create a line chart from the input data using x_column and y_column.
    Returns a dict with plot_type, image_base64, and config.
    """
    df = pd.DataFrame(data)
    plt.plot(df[x_column], df[y_column], marker="o")
    return {
        "plot_type": "line",
        "image_base64": _save_plot("line", title),
        "config": {"x_column": x_column, "y_column": y_column, "title": title}
    }

@tool("pie_chart", args_schema=PlotCreationInput)
def pie_chart(data: List[Dict[str, Any]],plot_type: str,  x_column: str, y_column: str, title: str = None) -> Dict[str, Any]:
    """
    Create a pie chart from the input data using x_column and y_column.
    Returns a dict with plot_type, image_base64, and config.
    """    
    df = pd.DataFrame(data)
    plt.pie(df[y_column], labels=df[x_column], autopct="%1.1f%%")
    return {
        "plot_type": "pie",
        "image_base64": _save_plot("pie", title),
        "config": {"x_column": x_column, "y_column": y_column, "title": title}
    }
PLOTTING_TOOLS = [analyze_data, bar_chart, line_chart, pie_chart ]


# === Test block ===
if __name__ == "__main__":
    sample_data = [
        {"city": "New York", "temperature": 22, "humidity": 65},
        {"city": "Los Angeles", "temperature": 28, "humidity": 55},
        {"city": "Chicago", "temperature": 18, "humidity": 70},
        {"city": "Houston", "temperature": 30, "humidity": 60},
        {"city": "Phoenix", "temperature": 35, "humidity": 20},
    ]

    # LangChain tool expects a dict with key 'data'
    print("=== TEST DATA ANALYSIS ===")
    analysis_result = analyze_data({"data": sample_data})
    print(analysis_result)

    print("\n=== TEST BAR CHART ===")
    bar_result = bar_chart({
        "data": sample_data,
        "plot_type": "bar",
        "x_column": "city",
        "y_column": "temperature",
        "title": "City Temperatures"
    })
    print(bar_result["config"])
    print("Image Base64 Length:", len(bar_result["image_base64"]))

    print("\n=== TEST LINE CHART ===")
    line_result = line_chart({
        "data": sample_data,
        "plot_type": "line",
        "x_column": "city",
        "y_column": "temperature",
        "title": "City Temperatures Over Cities"
    })
    print(line_result["config"])
    print("Image Base64 Length:", len(line_result["image_base64"]))

    print("\n=== TEST PIE CHART ===")
    pie_result = pie_chart({
        "data": sample_data,
        "plot_type": "pie",
        "x_column": "city",
        "y_column": "humidity",
        "title": "Humidity Distribution"
    })
    print(pie_result["config"])
    print("Image Base64 Length:", len(pie_result["image_base64"]))