#temporary tempate for seeding the database with fake audit records for testing and demonstration purposes.
import sys
import os
from datetime import datetime, timedelta

# to import from 'cortex'
sys.path.append(os.getcwd())

from cortex.app.core.database import SessionLocal, engine, Base
from cortex.app.core.models import PredictionAudit

def seed_data():
    print("Force Clearing and Seeding Database...")
    
    # TO MAKE SURE tables exist
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()

    # the past dates
    today = datetime.now().date()
    yesterday = today - timedelta(days=1)
    two_days_ago = today - timedelta(days=2)
    
    try:
        # Wipe existing data to prevent format mismatches
        db.query(PredictionAudit).delete()
        
        fake_history = [
            # Case 1: Bullseye (High Trust)
            PredictionAudit(
                currency_pair="GBP_INR",
                target_date=yesterday,
                predicted_rate=105.50,
                predicted_change_pct=0.005,
                actual_rate=105.48,
                actual_change_pct=0.0048,
                trust_label="Direction Matched (High Trust)",
                is_resolved=True
            ),
            # Case 2: Conservative (Safe)
            PredictionAudit(
                currency_pair="GBP_USD",
                target_date=yesterday,
                predicted_rate=1.27,
                predicted_change_pct=0.001,
                actual_rate=1.28,
                actual_change_pct=0.005,
                trust_label="Direction Matched (Conservative)",
                is_resolved=True
            ),
            # Case 3: Diverged (Warning)
            PredictionAudit(
                currency_pair="GBP_EUR",
                target_date=two_days_ago,
                predicted_rate=1.15,
                predicted_change_pct=0.003,
                actual_rate=1.14,
                actual_change_pct=-0.001,
                trust_label="Direction Missed (Warning)",
                is_resolved=True
            ),
            # Case 4: Precision (Flat)
            PredictionAudit(
                currency_pair="USD_JPY",
                target_date=two_days_ago,
                predicted_rate=145.00,
                predicted_change_pct=0.000,
                actual_rate=145.05,
                actual_change_pct=0.0003,
                trust_label="Direction Accurate (Precision)",
                is_resolved=True
            )
        ]

        db.add_all(fake_history)
        db.commit()
        print("Successfully seeded with 4 fresh audit records.")
    except Exception as e:
        print(f"Error seeding data: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_data()