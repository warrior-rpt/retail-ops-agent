from unittest.mock import patch, MagicMock
from app.agent.graph import build_graph

@patch("app.agent.graph.llm")
def test_low_risk_auto_approval(mock_llm):
    # Mock LLM to return no risks
    mock_response = MagicMock()
    mock_response.content = "No significant operational risks detected."
    mock_llm.invoke.return_value = mock_response

    graph = build_graph()
    result = graph.invoke({"sku": "SKU-002"})

    assert result["risk_level"] == "LOW"
    assert result["final_decision"].decision == "Auto-approved"
