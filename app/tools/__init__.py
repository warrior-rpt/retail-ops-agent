from typing import Dict, Any
from app.tools.notification import Notifier

def send_sns_alert(sku: str, severity: str, message: str) -> Dict[str, Any]:
    """
    Sends an escalation alert via SNS.
    """
    subject = f" Retail Ops Escalation [{severity}] – {sku}"
    Notifier.send_email(subject=subject, message=message)
    print(f"[TOOL] SNS Alert Sent | SKU={sku} | Severity={severity}")
    return {"status": "sent"}


def reorder_inventory(sku: str, quantity: int) -> Dict[str, Any]:
    """
    Simulates inventory reorder.
    """
    print(f"[TOOL] Reorder triggered | SKU={sku} | Qty={quantity}")
    return {"status": "reordered"}

TOOLS = {
    "send_sns_alert": send_sns_alert,
    "reorder_inventory": reorder_inventory,
}
