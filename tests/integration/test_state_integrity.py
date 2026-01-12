from unittest.mock import patch
from app.agent.graph import build_graph

@patch("app.tools.notification.Notifier.send_email")
def test_medium_risk_does_not_escalate(mock_sns):
    graph = build_graph()

    result = graph.invoke({"sku": "SKU-003"})

    assert result["risk_level"] == "MEDIUM"
    assert "proposed_actions" in result
    assert mock_sns.called is False
