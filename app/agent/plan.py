from app.agent.state import AgentState
from app.agent.prompts import SYSTEM_PROMPT
from app.llm.bedrock_client import get_llm
import json

llm = get_llm()

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

IMPORTANT: For MEDIUM risk levels, you are EXPECTED to propose an automated tool call unless there is a very strong reason not to.
Available Tools:
- reorder_inventory(sku: str, quantity: int): Use to mitigate stockout risk, low inventory, or whenever inventory is below reorder point.

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
