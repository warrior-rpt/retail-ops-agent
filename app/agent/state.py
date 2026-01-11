from typing import TypedDict, List, Optional
from app.models.domain import AgentDecision


class AgentState(TypedDict):
    sku: str
    risk_level: str
    sales_summary: str
    inventory_summary: str
    detected_risks: List[str]
    proposed_actions: List[str]
    final_decision: Optional[AgentDecision]
