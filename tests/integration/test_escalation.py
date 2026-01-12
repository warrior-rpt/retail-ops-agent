from unittest.mock import patch
from app.agent.graph import build_graph

@patch("app.tools.notification.Notifier.send_email")
def test_high_risk_triggers_sns(mock_sns):
    graph = build_graph()

    result = graph.invoke({"sku": "SKU-005"})

    assert result["risk_level"] == "HIGH"
    assert mock_sns.called is True
