from fastapi import APIRouter, HTTPException, Depends, Header, status
from pydantic import BaseModel, field_validator
import os
import joblib
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import keras
from sqlalchemy.orm import Session
from sqlalchemy import func

# from cortex.app.engine.sentiment import get_market_sentiment
from cortex.app.core.database import get_db
from cortex.app.core.models import PredictionAudit
from cortex.app.engine.auditor import calculate_trust_label
from cortex.app.engine.fetcher import fetch_data

router = APIRouter()
logger = logging.getLogger("cortex.api")

MODEL_CACHE = {}
SUPPORTED_CURRENCIES = {
    "GBP", "CHF", "USD", "INR", "JPY", "CZK", "DKK", "HUF", "PLN", "RON", 
    "SEK", "ISK", "NOK", "TRY", "AUD", "BRL", "CAD", "CNY", "HKD", "IDR", 
    "ILS", "KRW", "MXN", "MYR", "NZD", "PHP", "SGD", "THB", "ZAR", "EUR"
}

class PredictionRequest(BaseModel):
    from_currency: str
    to_currency: str
    days: int = 30

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# MODEL_DIR = os.path.join(BASE_DIR, "../../../models")
MODEL_DIR = "/app/cortex/models"

def get_model_prediction(target_curr: str, days: int, window_size: int = 180):
    if target_curr == "EUR": return None, None
    pair_code = f"EUR_{target_curr}"
    model_path = os.path.join(MODEL_DIR, f"{pair_code}.keras")
    scaler_path = os.path.join(MODEL_DIR, f"{pair_code}_scaler.joblib")

    if not os.path.exists(model_path):
        print(f"CRITICAL: Model file missing at {model_path}")
        raise HTTPException(
            status_code=503, 
            detail=f"Model for {pair_code} not initialized."
        )

    model = keras.models.load_model(model_path)
    scaler = joblib.load(scaler_path)
    df = fetch_data(f"EUR{target_curr}")
    
    if df is None or len(df) < window_size:
        raise ValueError(f"Insufficient history for {pair_code}")

    latest_price = float(df["Close"].iloc[-1])
    df_calc = df.copy()
    df_calc["Return"] = df_calc["Close"].pct_change()
    df_calc.dropna(inplace=True)

    recent_returns = df_calc["Return"].values[-window_size:].reshape(-1, 1)
    current_batch = scaler.transform(recent_returns).reshape(1, window_size, 1)

    predicted_prices = []
    current_price = latest_price
    for _ in range(days):
        pred_scaled = model.predict(current_batch, verbose=0)[0, 0]
        pred_return = scaler.inverse_transform([[pred_scaled]])[0, 0]
        current_price = current_price * (1 + pred_return)
        predicted_prices.append(current_price)
        next_input = np.array([[[pred_scaled]]])
        current_batch = np.append(current_batch[:, 1:, :], next_input, axis=1)

    return df, predicted_prices

@router.post("/predict")
def predict_forecast(request: PredictionRequest, db: Session = Depends(get_db)):
    try:
        days, from_curr, to_curr = request.days, request.from_currency, request.to_currency
        
        if from_curr == "EUR":
            df_base, pred_base = None, [1.0] * days
        else:
            df_base, pred_base = get_model_prediction(from_curr, days)

        if to_curr == "EUR":
            df_quote, pred_quote = None, [1.0] * days
        else:
            df_quote, pred_quote = get_model_prediction(to_curr, days)

        if df_base is not None and df_quote is not None:
            common_index = df_base.index.intersection(df_quote.index)
            series_base = df_base.loc[common_index]["Close"]
            series_quote = df_quote.loc[common_index]["Close"]
        elif df_base is not None:
            series_base, series_quote = df_base["Close"], pd.Series(1.0, index=df_base.index)
        elif df_quote is not None:
            series_base, series_quote = pd.Series(1.0, index=df_quote.index), df_quote["Close"]
        else:
            raise HTTPException(status_code=400, detail="EUR/EUR is an identity pair.")

        history_series = series_quote / series_base
        final_predictions = [pred_quote[i] / pred_base[i] for i in range(days)]

        response_data = []
        recent_history = history_series.tail(30)
        for dt, rate in recent_history.items():
            response_data.append({"date": dt.strftime("%Y-%m-%d"), "rate": round(float(rate), 4), "type": "history"})

        latest_date, friday_rate = recent_history.index[-1], float(recent_history.iloc[-1])
        today, monday_rate = datetime.now().date(), final_predictions[0]
        gap_diff = monday_rate - friday_rate
        current_fill_date = latest_date.date() + timedelta(days=1)
        
        while current_fill_date <= today:
            days_passed = (current_fill_date - latest_date.date()).days
            bridge_rate = friday_rate + (gap_diff * min(days_passed * 0.33, 0.90))
            response_data.append({"date": current_fill_date.strftime("%Y-%m-%d"), "rate": round(bridge_rate, 4), "type": "indicative"})
            current_fill_date += timedelta(days=1)

        forecast_start_date = max(today + timedelta(days=1), latest_date.date() + timedelta(days=1))
        prediction_index, current_date_pointer = 0, forecast_start_date
        while prediction_index < len(final_predictions):
            if current_date_pointer.weekday() < 5:
                response_data.append({"date": current_date_pointer.strftime("%Y-%m-%d"), "rate": round(final_predictions[prediction_index], 4), "type": "forecast"})
                prediction_index += 1
            current_date_pointer += timedelta(days=1)
        
        return {"pair": f"{from_curr}_{to_curr}", "forecast": response_data}
    except Exception as e:
        if isinstance(e, HTTPException): raise e
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/audit/scoreboard")
def get_scoreboard(db: Session = Depends(get_db)):
    # audits
    pending = db.query(PredictionAudit).filter(PredictionAudit.is_resolved == False, PredictionAudit.target_date < datetime.now().date()).all()
    for record in pending:
        try:
            base, quote = record.currency_pair.split("_")
            df_base = fetch_data(f"EUR{base}", str(record.target_date))
            df_quote = fetch_data(f"EUR{quote}", str(record.target_date))
            v_b = 1.0 if base=="EUR" else (df_base["Close"].iloc[0] if df_base is not None else None)
            v_q = 1.0 if quote=="EUR" else (df_quote["Close"].iloc[0] if df_quote is not None else None)
            if v_b and v_q:
                actual_close = v_q / v_b
                implied_start = record.predicted_rate / (1 + record.predicted_change_pct)
                actual_change = (actual_close - implied_start) / implied_start
                record.actual_rate, record.actual_change_pct = actual_close, actual_change
                record.trust_label = calculate_trust_label(record.predicted_change_pct, actual_change)
                record.is_resolved = True
        except: continue
    db.commit()

    # Dynamic Scoreboard
    results = []
    unique_pairs = db.query(PredictionAudit.currency_pair).distinct().all()
    for (pair_name,) in unique_pairs:
        latest = db.query(PredictionAudit).filter(
            PredictionAudit.currency_pair == pair_name, 
            PredictionAudit.is_resolved == True
        ).order_by(PredictionAudit.target_date.desc()).first()
        
        if latest:
            results.append({
                "currency": latest.currency_pair.replace("_", "/"),
                "pred": f"{latest.predicted_change_pct*100:+.2f}%",
                "actual": f"{latest.actual_change_pct*100:+.2f}%",
                "label": latest.trust_label,
                "status": "success" if "Matched" in (latest.trust_label or "") else "danger"
            })
    return {"scoreboard": results}
