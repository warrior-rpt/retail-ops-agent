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
from app.agent.plan import plan_node
from app.tools import TOOLS
import json

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

    # Store summaries for downstream tool planning
    state.update({
        "detected_risks": detected_risks,
        "risk_level": risk_level,
        "sales_summary": f"Sales last 7 days: {sales_record.get('daily_sales', 'N/A')}",
        "inventory_summary": f"Inventory level: {sales_record.get('inventory_level', 'N/A')}"
    })

    return state








def act_node(state: AgentState) -> AgentState:
    """
    Execute planned actions and tools.
    """
    sku = state.get("sku", "UNKNOWN")
    actions = state.get("proposed_actions", [])
    tool_plan = state.get("tool_plan", [])
    executed_tools = []

    # Execute all tools in the plan
    for step in tool_plan:
        tool_name = step["tool_name"]
        args = step["arguments"]

        if tool_name not in TOOLS:
            print(f"[WARN] Tool '{tool_name}' not found in registry. Skipping.")
            continue

        tool_func = TOOLS[tool_name]
        result = tool_func(**args)

        executed_tools.append({
            "tool": tool_name,
            "args": args,
            "result": result
        })

    # Set final decision only if not already set by upstream nodes
    if "final_decision" not in state:
        has_reorder = any(t["tool_name"] == "reorder_inventory" for t in tool_plan)
        decision_str = "Inventory Reorder Recommended" if has_reorder else "Operational Monitoring"
        
        state["final_decision"] = AgentDecision(
            decision=decision_str,
            actions=actions,
            confidence=0.85,
            rationale=state.get("rationale", "Monitoring operational risks.")
        )

    # Save to memory (actions only, not tool results)
    AgentMemory.update_memory(
        sku=sku,
        last_action="; ".join(actions) if actions else "No action",
        last_decision=state["final_decision"].decision
    )

    # Update state
    state["tool_results"] = executed_tools

    return state




def route_by_risk(state: dict) -> str:
    """
    LangGraph routing function.
    Must return the name of the next node.
    """
    return state["risk_level"]


def save_graph_visualization(compiled_graph, output_path: str = "agent_graph.png"):
    """
    Generates and saves a PNG visualization of the compiled graph.
    """
    try:
        png_data = compiled_graph.get_graph().draw_mermaid_png()
        with open(output_path, "wb") as f:
            f.write(png_data)
        print(f"[INFO] Graph visualization saved to {output_path}")
    except Exception as e:
        print(f"[WARN] Could not generate graph visualization: {e}")


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
    graph.add_edge("auto_approve", "act")
    graph.add_edge("escalate", "act")
    graph.add_edge("act", END)

    return graph.compile()
