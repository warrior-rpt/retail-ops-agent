from app.memory.sales_data import SalesData
from app.agent.graph import build_graph, save_graph_visualization
from dataclasses import asdict
from langsmith import traceable
import os

graph = build_graph()
save_graph_visualization(graph, "agent_graph.png")

@traceable(name="retail_ops_agent_handler", project_name=os.getenv("LANGSMITH_PROJECT", "pr-new-stab-27"))
def handler(event, context=None):
    results = []

    for sku in SalesData.get_all_skus():
        # Invoke graph with LangSmith metadata
        final_state = graph.invoke(
            {"sku": sku},
            config={
                "run_name": f"process_sku_{sku}",
                "metadata": {
                    "sku": sku,
                    "environment": "production"
                },
                "tags": ["retail-ops", f"sku-{sku}"]
            }
        )

        decision_dict = asdict(final_state["final_decision"])
        
        results.append({
            "sku": sku,
            "risk_level": final_state.get("risk_level"),
            "decision": asdict(final_state["final_decision"]),
            "tool_plan": final_state.get("tool_plan", []),
            "tool_results": final_state.get("tool_results", [])
        })

    return results


