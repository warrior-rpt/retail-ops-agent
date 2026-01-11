from dataclasses import dataclass
from datetime import datetime
from typing import List


@dataclass
class SalesMetric:
    sku: str
    region: str
    daily_units_sold: int
    timestamp: datetime


@dataclass
class InventoryLevel:
    sku: str
    region: str
    available_units: int
    reorder_threshold: int


@dataclass
class AgentDecision:
    decision: str
    actions: List[str]
    confidence: float
    rationale: str
