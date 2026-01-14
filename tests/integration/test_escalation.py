from unittest.mock import patch
from app.agent.graph import build_graph

@patch("app.tools.notification.Notifier.send_email")
def test_high_risk_triggers_sns(mock_sns):
    graph = build_graph()

    result = graph.invoke({"sku": "SKU-005"})

    assert result["risk_level"] == "HIGH"
    assert any(tool["tool_name"] == "send_sns_alert" for tool in result["tool_plan"])
    assert any(res["tool"] == "send_sns_alert" and res["result"]["status"] == "sent" for res in result["tool_results"])
    assert mock_sns.called is True
