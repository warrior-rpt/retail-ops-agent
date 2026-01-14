from app.models.domain import AgentDecision
from app.agent.state import AgentState

def auto_approve_node(state: AgentState) -> AgentState:
    """
    Node for LOW risk operations.
    Decision is auto-approve. No tools invoked, tool_plan is explicitly empty.
    """
    decision = AgentDecision(
        decision="Auto-approved",
        actions=["No action required"],
        confidence=0.95,
        rationale="No significant operational risks detected."
    )

    # Explicitly show that no tools are invoked
    state["tool_plan"] = []
    state["tool_results"] = []

    state["final_decision"] = decision
    return state

