from app.models.domain import AgentDecision
from app.agent.state import AgentState


def escalate_node(state: AgentState) -> AgentState:
    sku = state["sku"]
    risks = state.get("detected_risks", [])

    decision = AgentDecision(
        decision="Escalation Required",
        actions=["Notify Operations Lead", "Open Incident Ticket"],
        confidence=0.9,
        rationale="Critical risk detected requiring human intervention."
    )

    # PLAN the tool usage
    state["tool_plan"] = [
        {
            "tool_name": "send_sns_alert",
            "reason": "Critical operational risk detected",
            "arguments": {
                "sku": sku,
                "severity": "HIGH",
                "message": (
                    f"HIGH RISK DETECTED for SKU {sku}. "
                    f"Detected risks: {', '.join(risks)}. "
                    "Immediate human intervention required."
                )
            }
        }
    ]

    state["final_decision"] = decision
    state["tool_results"] = []
    return state
