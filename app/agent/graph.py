from langgraph.graph import StateGraph, END
from app.agent.state import AgentState
from app.agent.prompts import SYSTEM_PROMPT
from app.llm.bedrock_client import get_llm
from app.tools.sales import analyze_sales_trend
from app.tools.inventory import get_inventory_status
from app.models.domain import AgentDecision
from app.memory.dynamo_repo import AgentMemory
from app.memory.sales_data import SalesData

llm = get_llm()


def analyze_node(state: AgentState) -> AgentState:
    sku = state.get("sku", "SKU-A")  # Default if missing

    # Load past memory
    memory = AgentMemory.get_memory(sku)
    past_action = memory.get("last_action", "No past action")
    past_decision = memory.get("last_decision", "No past decision")

    # Load sales data
    sales_record = SalesData.get_sales(sku)
    last_7days_sales = sales_record.get("last_7days_sales", "0")
    forecast = sales_record.get("forecast", "0")

    prompt = f"""
{SYSTEM_PROMPT}

Analyze the following signals and identify operational risks.

Sales (last 7 days): {last_7days_sales}
Forecast: {forecast}

Previous Memory:
Action: {past_action}
Decision: {past_decision}

Return a bullet list of detected risks.
"""

    response = llm.invoke(prompt)

    state["sales_summary"] = f"Sales: {last_7days_sales}, Forecast: {forecast}"
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
