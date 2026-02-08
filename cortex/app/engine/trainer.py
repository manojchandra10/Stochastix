import os
import joblib
import numpy as np
import pandas as pd
import time
from cortex.app.engine.fetcher import fetch_data
from cortex.app.engine.model import train_model, build_model
from sklearn.preprocessing import MinMaxScaler

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# MODEL_DIR = os.path.join(BASE_DIR, "../../../models")
MODEL_DIR = os.path.join(BASE_DIR, "../../models") 

os.makedirs(MODEL_DIR, exist_ok=True)

def run_pipeline(target_curr):

    pair_code = f"EUR_{target_curr}"
    ticker = f"EUR{target_curr}"

    model_path = os.path.join(MODEL_DIR, f"{pair_code}.keras")
    scaler_path = os.path.join(MODEL_DIR, f"{pair_code}_scaler.joblib")

    if os.path.exists(model_path) and os.path.exists(scaler_path):
        print(f"⏩ SKIPPING {pair_code}: Model already exists.")
        return

    print(f"\n--- Starting Pipeline for {pair_code} (Source: ECB) ---")

    # Fetch Data
    df = fetch_data(ticker, start_date="2000-01-01")

    if df is None or len(df) < 300:
        print(f"Not enough data for {pair_code}. Skipping.")
        return

    df = df[df["Close"] > 0.0001]
    df.dropna(inplace=True)

    # CONVERT TO RETURNS
    df["Return"] = df["Close"].pct_change()
    df = df[(df["Return"] > -0.2) & (df["Return"] < 0.2)]
    df.dropna(inplace=True)

    if len(df) < 200:
        print("Data too short after cleaning.")
        return

    # Scaling
    data = df["Return"].values.reshape(-1, 1)
    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled_data = scaler.fit_transform(data)

    # Create Sequences
    X, y = [], []
    window_size = 180
    for i in range(window_size, len(scaled_data)):
        X.append(scaled_data[i - window_size:i, 0])
        y.append(scaled_data[i, 0])

    X, y = np.array(X), np.array(y)
    X = np.reshape(X, (X.shape[0], X.shape[1], 1))

    # Train
    print(f"Training {pair_code} on {len(X)} cleaned data points...")
    model = build_model((X.shape[1], 1))
    train_model(model, X, y, epochs=15, batch_size=32)

    # We already defined model_path and scaler_path at the top, so we save and reuse them here.
    model.save(model_path)
    joblib.dump(scaler, scaler_path)
    print(f"Model saved to {model_path} successfully.")

if __name__ == "__main__":
    currencies = [
        "GBP", "CHF", "USD", "INR", "JPY", "CZK", "DKK",  "HUF", "PLN", "RON", "SEK", 
        "ISK", "NOK", "TRY", "AUD", "BRL", "CAD", "CNY", "HKD", "IDR", "ILS", 
        "KRW", "MXN", "MYR", "NZD", "PHP", "SGD", "THB", "ZAR"
    ]

    print("Waking up Cortex Training Engine...")
    print(f"Checking for existing models in: {MODEL_DIR}")
    
    for currency in currencies:
        try:
            run_pipeline(currency)
            # Sleep 2 seconds only if we actually hit the API (if we skipped, loop is fast)
            # But the sleep is harmless either way.
            # We can check if file existed to avoid sleep, but keeping it simple is fine.
            # To be super efficient, we could move sleep inside run_pipeline before fetch.
            # But the current structure is clear and the sleep is short, so it's acceptable.
             
        except Exception as e:
            print(f"CRITICAL FAILURE for EUR_{currency}: {e}")