def classify_risk(detected_risks: list[str]) -> str:
    """
    Deterministic risk classification.
    """
    if not detected_risks:
        return "LOW"

    high_keywords = ["stockout", "compliance", "fraud", "critical"]
    medium_keywords = ["delay", "trend", "forecast", "monitor"]

    text = " ".join(detected_risks).lower()

    if any(k in text for k in high_keywords):
        return "HIGH"

    if any(k in text for k in medium_keywords):
        return "MEDIUM"

    return "LOW"
