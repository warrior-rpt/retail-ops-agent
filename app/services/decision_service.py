from app.agent.graph import build_agent_graph


def run_agent(event: dict):
    agent = build_agent_graph()

    initial_state = {
        "sales_summary": "",
        "inventory_summary": "",
        "detected_risks": [],
        "proposed_actions": [],
        "final_decision": None,
    }

    final_state = agent.invoke(initial_state)

    decision = final_state["final_decision"]

    return {
        "decision": decision.decision,
        "actions": decision.actions,
        "confidence": decision.confidence,
        "rationale": decision.rationale,
    }
