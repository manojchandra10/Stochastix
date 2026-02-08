from pydantic import BaseModel
from typing import List, Optional
from datetime import date

class ForecastRequest(BaseModel):
    from_currency: str
    to_currency: str
    days: Optional[int] = 30  # Default to 30 days

class ForecastPoint(BaseModel):
    date: str
    rate: float
    label: Optional[str] = None # e.g., "Tomorrow", "1 Week"

class ForecastResponse(BaseModel):
    pair: str
    generated_at: str
    forecast: List[ForecastPoint]