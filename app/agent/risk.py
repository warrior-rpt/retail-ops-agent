def classify_risk(detected_risks: list[str]) -> str:
    """
    Deterministic risk classification based on detected risks.
    
    HIGH: Critical situations requiring immediate human intervention
    MEDIUM: Operational concerns requiring planning and action
    LOW: Routine operations with no significant risks
    """
    if not detected_risks:
        return "LOW"
    
    # Join all risks into a single text for analysis
    text = " ".join(detected_risks).lower()
    
    # HIGH risk indicators - truly critical situations
    high_keywords = [
        "critical stockout",
        "confirmed stockout", 
        "supplier disruption confirmed",
        "compliance violation",
        "fraud detected",
        "severe shortage",
        "emergency"
    ]
    
    # MEDIUM risk indicators - operational concerns
    medium_keywords = [
        "stockout risk",
        "potential stockout",
        "delay",
        "trend",
        "forecast",
        "monitor",
        "reorder",
        "inventory low",
        "demand spike"
    ]
    
    # Check for HIGH risk (use stricter matching)
    if any(keyword in text for keyword in high_keywords):
        return "HIGH"
    
    # Check for MEDIUM risk
    if any(keyword in text for keyword in medium_keywords):
        return "MEDIUM"
    
    return "LOW"
