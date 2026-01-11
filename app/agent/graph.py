from langgraph.graph import StateGraph, END
from app.agent.state import AgentState
from app.agent.prompts import SYSTEM_PROMPT
from app.llm.bedrock_client import get_llm
from app.tools.sales import analyze_sales_trend
from app.tools.inventory import get_inventory_status
from app.models.domain import AgentDecision

llm = get_llm()


def analyze_node(state: AgentState) -> AgentState:
    sales_summary = analyze_sales_trend(sku="SKU-A", region="US-WEST")
    inventory_summary = get_inventory_status(sku="SKU-A", region="US-WEST")

    prompt = f"""
{SYSTEM_PROMPT}

Analyze the following signals and identify operational risks.

Sales:
{sales_summary}

Inventory:
{inventory_summary}

Return a bullet list of detected risks.
"""

    response = llm.invoke(prompt)

    state["sales_summary"] = sales_summary
    state["inventory_summary"] = inventory_summary
    state["detected_risks"] = response.content.splitlines()

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
    actions = state.get("proposed_actions", [])

    # In a real system, this would dispatch real APIs
    executed_actions = []
    for action in actions:
        executed_actions.append(action)

    decision = AgentDecision(
        decision="Inventory Reorder Recommended",
        actions=executed_actions,
        confidence=0.82,
        rationale="Detected stockout risk combined with demand spike."
    )

    state["final_decision"] = decision
    return state



def build_agent_graph():
    graph = StateGraph(AgentState)

    graph.add_node("analyze", analyze_node)
    graph.add_node("plan", plan_node)
    graph.add_node("act", act_node)

    graph.set_entry_point("analyze")

    graph.add_edge("analyze", "plan")
    graph.add_edge("plan", "act")
    graph.add_edge("act", END)

    return graph.compile()
