import json
from unittest.mock import patch, MagicMock
from app.agent.graph import build_graph

@patch("app.agent.plan.llm")
@patch("app.agent.graph.llm")
def test_medium_risk_forces_tool_invocation(mock_graph_llm, mock_plan_llm):
    """
    Verify that a MEDIUM risk situation (inventory below reorder point)
    results in a tool_plan containing reorder_inventory.
    """
    # 1. Mock Analyze Node (in graph.py) to return MEDIUM risk
    mock_analyze_response = MagicMock()
    mock_analyze_response.content = "Inventory level is 45 units, which is below the reorder point of 50. Stockout risk detected."
    mock_graph_llm.invoke.return_value = mock_analyze_response

    # 2. Mock Plan Node (in plan.py) to return a tool plan
    # We want to verify the logic that leads to this, but in unit-style integration 
    # we often mock the LLM final output. 
    # To truly test the prompt IMPROVEMENT, we'd need a real LLM call, 
    # but here we test that if the prompt works as intended, the state is correctly updated.
    mock_plan_response = MagicMock()
    mock_plan_response.content = json.dumps({
        "actions": ["Reorder inventory to maintain safety stock"],
        "rationale": "Inventory is below reorder point, triggering automated replenishment.",
        "tool_plan": [
            {
                "tool_name": "reorder_inventory",
                "reason": "Inventory below reorder point",
                "arguments": {"sku": "SKU-001", "quantity": 100}
            }
        ]
    })
    mock_plan_llm.invoke.return_value = mock_plan_response

    graph = build_graph()
    result = graph.invoke({"sku": "SKU-001"})

    # Assertions
    assert result["risk_level"] == "MEDIUM"
    assert len(result["tool_plan"]) > 0
    assert result["tool_plan"][0]["tool_name"] == "reorder_inventory"
    assert "reorder" in result["final_decision"].decision.lower()
