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



def plan_node(state: AgentState) -> AgentState:
    sku = state.get("sku", "UNKNOWN")
    risk_level = state.get("risk_level", "UNKNOWN")
    risks = "\n".join(state.get("detected_risks", []))
    sales = state.get("sales_summary", "N/A")
    inventory = state.get("inventory_summary", "N/A")

    prompt = f"""
{SYSTEM_PROMPT}

Based on the following detected risks for SKU {sku} (Risk Level: {risk_level}):

Operational Context:
- {sales}
- {inventory}

Detected Risks:
{risks}

Propose a prioritized list of actions and decide if any automated tools should be used.
Available Tools:
- reorder_inventory(sku: str, quantity: int): Use ONLY if inventory is significantly low relative to demand.

RESPONSE FORMAT:
Your response MUST be a JSON object with three keys:
1. "actions": A list of strings representing prioritized action statements.
2. "rationale": A string explaining the reasoning behind the actions and tool usage.
3. "tool_plan": A list of tool call objects: {{"tool_name": "...", "reason": "...", "arguments": {{...}}}}

Example:
{{
  "actions": ["Check supplier lead times", "Review pricing strategy"],
  "rationale": "Inventory is approaching reorder point while sales are trending up. Pre-emptive reorder suggested.",
  "tool_plan": [
    {{
       "tool_name": "reorder_inventory",
       "reason": "Inventory level below reorder point",
       "arguments": {{"sku": "{sku}", "quantity": 100}}
    }}
  ]
}}

Return ONLY the JSON object.
"""

    response = llm.invoke(prompt)
    try:
        # Strip potential markdown formatting if LLM adds it
        content = response.content.strip()
        if content.startswith("```json"):
            content = content[7:-3].strip()
        elif content.startswith("```"):
             content = content[3:-3].strip()
        
        planning_result = json.loads(content)
        state["proposed_actions"] = planning_result.get("actions", [])
        state["tool_plan"] = planning_result.get("tool_plan", [])
        state["rationale"] = planning_result.get("rationale", "No rationale provided by agent.")
    except Exception as e:
        print(f"[ERROR] Failed to parse planning JSON: {e}")
        # Fallback to pure text actions if JSON parsing fails
        state["proposed_actions"] = [response.content]
        state["tool_plan"] = []

    state["tool_results"] = []  # Initialize/Reset
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
