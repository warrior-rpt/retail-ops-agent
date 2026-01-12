import re

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
        r"critical stockout",
        r"confirmed stockout", 
        r"supplier disruption confirmed",
        r"compliance violation",
        r"fraud detected",
        r"severe shortage",
        r"emergency"
    ]
    
    # MEDIUM risk indicators - operational concerns
    medium_keywords = [
        r"stockout risk",
        r"potential stockout",
        r"delay",
        r"trend",
        r"forecast",
        r"monitor",
        r"\breorder\b",  # Only match 'reorder' as a full word
        r"inventory low",
        r"demand spike"
    ]
    
    # Check for HIGH risk
    if any(re.search(keyword, text) for keyword in high_keywords):
        return "HIGH"
    
    # Check for MEDIUM risk
    if any(re.search(keyword, text) for keyword in medium_keywords):
        return "MEDIUM"
    
    return "LOW"
