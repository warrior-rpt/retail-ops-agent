from typing import TypedDict, List, Optional, Dict, Any
from app.models.domain import AgentDecision


class ToolPlan(TypedDict):
    tool_name: str
    reason: str
    arguments: Dict[str, Any]


class ToolResult(TypedDict):
    tool_name: str
    arguments: Dict[str, Any]
    result: Dict[str, Any]


class AgentState(TypedDict, total=False):
    # Core identity
    sku: str

    # Risk analysis
    risk_level: str
    detected_risks: List[str]

    # Optional summaries (if used)
    sales_summary: str
    inventory_summary: str

    # Planning & actions
    proposed_actions: List[str]
    rationale: str

    # TOOLING 
    tool_plan: List[ToolPlan]
    tool_results: List[ToolResult]

    # Final outcome
    final_decision: Optional[AgentDecision]

