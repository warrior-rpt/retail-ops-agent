import json
from unittest.mock import patch, MagicMock
from app.agent.graph import build_graph

@patch("app.agent.graph.llm")
def test_sku_001_low_risk_no_reorder(mock_llm):
    # Mock behavior: 
    # 1. Analyze node detects 'monitoring' and 'trends' which should now be LOW risk
    mock_analyze_response = MagicMock()
    mock_analyze_response.content = "No critical issues. Just some sales trends to monitor."
    
    # 2. Planning node (if it were reached, but it won't be because risk is LOW)
    # Actually, let's verify that it routes to auto_approve
    
    mock_llm.invoke.return_value = mock_analyze_response
    
    graph = build_graph()
    result = graph.invoke({"sku": "SKU-001"})
    
    # Assertions
    assert result["risk_level"] == "LOW"
    assert result["final_decision"].decision == "Auto-approved"
    assert result["tool_plan"] == []
    assert "No significant operational risks detected." in result["final_decision"].rationale

@patch("app.agent.graph.llm")
def test_medium_risk_correct_rationale(mock_llm):
    # Mock behavior:
    # 1. Analyze node returns MEDIUM risk
    mock_analyze_response = MagicMock()
    mock_analyze_response.content = "Inventory low. Stockout risk detected."
    
    # 2. Plan node returns custom rationale and no reorder tool (marginal risk)
    mock_plan_response = MagicMock()
    mock_plan_response.content = json.dumps({
        "actions": ["Watch daily sales"],
        "rationale": "Inventory is low but sales are stable for now. No immediate reorder needed.",
        "tool_plan": []
    })
    
    mock_llm.invoke.side_effect = [mock_analyze_response, mock_plan_response]
    
    graph = build_graph()
    result = graph.invoke({"sku": "SKU-001"})
    
    # Assertions
    assert result["risk_level"] == "MEDIUM"
    assert result["final_decision"].decision == "Operational Monitoring"
    assert result["final_decision"].rationale == "Inventory is low but sales are stable for now. No immediate reorder needed."
    assert result["tool_plan"] == []
