from app.models.domain import AgentDecision
from app.agent.state import AgentState

def auto_approve_node(state: AgentState) -> AgentState:
    decision = AgentDecision(
        decision="Auto-approved",
        actions=["No action required"],
        confidence=0.95,
        rationale="No significant operational risks detected."
    )

    state["final_decision"] = decision
    return state
