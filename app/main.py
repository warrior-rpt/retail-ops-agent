from app.agent.graph import analyze_node, plan_node, act_node
from app.memory.sales_data import SalesData
from dataclasses import asdict
from app.tools.notification import Notifier

def handler(event, context=None):
    results = []

    skus = SalesData.get_all_skus()

    for sku in skus:
        state = {}
        state["sku"] = sku

        state = analyze_node(state)
        state = plan_node(state)
        state = act_node(state)

        results.append({
            "sku": sku,
            "decision": asdict(state["final_decision"])
        })

    # Send summary notification
    summary_msg = "\n".join(
        [f"{r['sku']}: {r['decision']['decision']}" for r in results]
    )
    Notifier.send_email("Retail Ops Agent Decisions", summary_msg)

    return results


