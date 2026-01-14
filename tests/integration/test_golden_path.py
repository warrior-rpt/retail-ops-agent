def test_supplier_disruption_escalation():
    from app.agent.graph import build_graph

    graph = build_graph()

    result = graph.invoke({"sku": "SKU-005"})

    assert result["risk_level"] == "HIGH"
    assert result["final_decision"].decision == "Escalation Required"
    assert "Critical stockout risk" in " ".join(result["detected_risks"])
    assert len(result["tool_plan"]) > 0
    assert result["tool_plan"][0]["tool_name"] == "send_sns_alert"
    assert result["tool_results"][0]["result"]["status"] == "sent"
