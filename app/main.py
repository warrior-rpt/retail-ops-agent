from app.agent.graph import analyze_node, plan_node, act_node
from app.memory.sales_data import SalesData
from dataclasses import asdict

def handler(event, context=None):
    results = []

    # Get all SKUs
    skus = SalesData.get_all_skus()

    for sku in skus:
        state = {}
        state["sku"] = sku

        # ANALYZE
        state = analyze_node(state)

        # PLAN
        state = plan_node(state)

        # ACT
        state = act_node(state)

        results.append({
            "sku": sku,
            "decision": asdict(state["final_decision"])  # Dataclass to dict
        })

    return results

