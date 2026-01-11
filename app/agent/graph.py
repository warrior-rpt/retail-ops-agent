from langgraph.graph import StateGraph, END
from app.agent.state import AgentState
from app.agent.prompts import SYSTEM_PROMPT
from app.llm.bedrock_client import get_llm
from app.models.domain import AgentDecision
from app.memory.dynamo_repo import AgentMemory
from app.memory.sales_data import SalesData
from app.agent.risk import classify_risk
from app.agent.auto_approve import auto_approve_node
from app.agent.escalate import escalate_node

llm = get_llm()


def analyze_node(state: AgentState) -> AgentState:
    sku = state.get("sku", "SKU-A")  # Default if missing

    # Load past memory
    memory = AgentMemory.get_memory(sku)
    past_action = memory.get("last_action", "No past action")
    past_decision = memory.get("last_decision", "No past decision")

    # Load sales data
    sales_record = SalesData.get_sales(sku)

    prompt = f"""
{SYSTEM_PROMPT}

Analyze the following operational signals for SKU {sku} and identify risks.

Operational Data:
{sales_record}

Previous Memory:
Action: {past_action}
Decision: {past_decision}

Return a bullet list of detected risks.
"""

    response = llm.invoke(prompt)
    detected_risks = response.content.splitlines()

    risk_level = classify_risk(detected_risks)

    state.update({
        "detected_risks": detected_risks,
        "risk_level": risk_level
    })

    return state



def plan_node(state: AgentState) -> AgentState:
    risks = "\n".join(state.get("detected_risks", []))

    prompt = f"""
{SYSTEM_PROMPT}

Based on the following detected risks:

{risks}

Propose a prioritized list of actions.
Return only action statements.
"""

    response = llm.invoke(prompt)

    state["proposed_actions"] = response.content.splitlines()
    return state




def act_node(state: AgentState) -> AgentState:
    sku = state.get("sku", "UNKNOWN")
    actions = state.get("proposed_actions", [])

    executed_actions = [action for action in actions]

    decision = AgentDecision(
        decision="Inventory Reorder Recommended",
        actions=executed_actions,
        confidence=0.82,
        rationale="Detected stockout risk combined with demand spike."
    )

    # Save to memory
    AgentMemory.update_memory(
    sku=state["sku"],
    last_action="; ".join(executed_actions),
    last_decision=decision.decision
)


    state["final_decision"] = decision
    return state




def route_by_risk(state: dict) -> str:
    """
    LangGraph routing function.
    Must return the name of the next node.
    """
    return state["risk_level"]


def build_graph():
    graph = StateGraph(AgentState)

    graph.add_node("analyze", analyze_node)
    graph.add_node("plan", plan_node)
    graph.add_node("act", act_node)
    graph.add_node("auto_approve", auto_approve_node)
    graph.add_node("escalate", escalate_node)

    graph.set_entry_point("analyze")

    graph.add_conditional_edges(
        "analyze",
        route_by_risk,
        {
            "HIGH": "escalate",
            "MEDIUM": "plan",
            "LOW": "auto_approve"
        }
    )

    graph.add_edge("plan", "act")
    graph.add_edge("act", END)
    graph.add_edge("auto_approve", END)
    graph.add_edge("escalate", END)

    return graph.compile()
