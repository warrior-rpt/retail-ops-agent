from typing import Dict, Any

def reorder_inventory(sku: str, quantity: int) -> Dict[str, Any]:
    """
    Simulates inventory reorder.
    """
    print(f"[TOOL] Reorder triggered | SKU={sku} | Qty={quantity}")
    return {"status": "reordered"}
