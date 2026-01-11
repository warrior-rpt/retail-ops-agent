from app.memory.sales_data import SalesData
from app.agent.graph import build_graph
from dataclasses import asdict

graph = build_graph()

def handler(event, context=None):
    results = []

    for sku in SalesData.get_all_skus():
        final_state = graph.invoke({"sku": sku})

        results.append({
            "sku": sku,
            "risk_level": final_state["risk_level"],
            "decision": asdict(final_state["final_decision"])
        })

    return results


