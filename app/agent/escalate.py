from app.models.domain import AgentDecision
from app.tools.notification import Notifier
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

    # 🔔 SNS notification ONLY here
    message = f"""
🚨 HIGH RISK DETECTED 🚨

SKU: {sku}

Detected Risks:
{chr(10).join(risks)}

Recommended Actions:
- Notify Operations Lead
- Open Incident Ticket
"""

    Notifier.send_email(
        subject=f"🚨 Retail Ops Escalation – {sku}",
        message=message.strip()
    )

    state["final_decision"] = decision
    return state

