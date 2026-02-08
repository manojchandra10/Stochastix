from sqlalchemy import Column, Integer, String, Float, Date, DateTime, Boolean
from sqlalchemy.sql import func
from cortex.app.core.database import Base

class PredictionAudit(Base):
    __tablename__ = "prediction_audits"

    id = Column(Integer, primary_key=True, index=True)
    currency_pair = Column(String, index=True)  # e.g. "GBP-INR"
    
    # the date of prediction 
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # The Target Date for which the prediction was made (e.g. 2024-07-01)
    target_date = Column(Date, index=True)
    
    # The Prediction
    predicted_rate = Column(Float)
    predicted_change_pct = Column(Float) # e.g. 0.005 (0.5%)
    
    # The Reality (Initially Null)
    actual_rate = Column(Float, nullable=True)
    actual_change_pct = Column(Float, nullable=True)
    
    # The Verdict
    trust_label = Column(String, nullable=True) # "Bullseye", "Conservative", "Diverged"
    is_resolved = Column(Boolean, default=False)