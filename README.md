# Stochastix: AI-Powered Exchange Rate Forecasting

Stochastix is a full-stack financial intelligence web application designed to help international students and professionals navigate currency volatility. Born from the real-world challenge of timing tuition payments and student loan transfers, Stochastix provides 30-day neural forecasts for major currency pairs (GBP, USD, EUR, INR, and more).

[See Preview](https://github.com/manojchandra10/Stochastix/blob/main/Stochastix-Preview.pdf) or [View Live WebApp](https://www.deltaconvert.com/exchange-rate-prediction)

---

## Key Features
* **Neural Forecasting:** Uses a Deep Learning model (LSTM) trained on decades of European Central Bank (ECB) daily reference rates.
* **Performance Auditing:** A built-in "Oracle Scorecard" that compares past predictions against actual market outcomes, providing transparent trust labels (e.g., "High Trust," "Conservative").
* **Market Sentiment Analysis:** Integrates VADER sentiment analysis to process global financial news headlines, providing context to the technical forecast.
* **Weekend Bridging:** Custom logic to handle "indicative" rates during market closures, ensuring a seamless user experience 24/7.
* **Production-Ready Architecture:** Fully containerised with Docker and orchestrated with Nginx as a reverse proxy.

---

## The Tech Stack

| Layer | Technology |
| :--- | :--- |
| **Frontend** | React, TypeScript, Vite, Recharts (Data Visualisation), Lucide Icons |
| **Backend** | FastAPI (Python), SQLAlchemy (ORM), Pydantic (Validation) |
| **Data Science** | TensorFlow/Keras (LSTM), Scikit-Learn (Preprocessing), Pandas, NumPy |
| **Database** | PostgreSQL (Audit logs and historical tracking) |
| **DevOps** | Docker, Docker Compose, Nginx (Reverse Proxy) |

---

## Methodology

### 1. Data Pipeline
The engine fetches daily spot rates from the **European Central Bank (ECB) API**. Unlike standard price prediction, Stochastix predicts **percentage returns**, which helps the model generalise better across different currency magnitudes and reduces the impact of non-stationary data.

### 2. The Model: LSTM
The core is a **Long Short-Term Memory (LSTM)** recurrent neural network.
* **Window Size:** 180 business days of historical returns.
* **Architecture:** Multi-layered LSTM with Dropout layers to prevent overfitting.
* **Forecast Horizon:** 30 days, generated through a recursive step-ahead prediction strategy.

### 3. Trust Logic (The Oracle)
To bridge the gap between complex ML metrics and user confidence, Stochastix implements a custom auditing engine:
* **Directional Matching:** Did the model correctly predict if the rate would go Up or Down?
* **Magnitude Error:** Calculates the delta between predicted and actual change to assign labels like *Bullseye* or *Diverged*.

---

## Security & Scalability
* **Non-Root Execution:** Docker containers run as a restricted `appuser` for security.
* **CORS Protection:** Strict cross-origin resource sharing policies for production domains.
* **Environment Isolation:** Sensitive credentials (database URLs, Admin Secrets) are managed via environment variables and never committed to version control.
* **Scalable API:** Asynchronous endpoints built with FastAPI to handle high-concurrency requests.

---

## Project Structure
```text
stochastix/
├── cortex/            # FastAPI Backend & ML Engine
├── interface/         # React/TypeScript Frontend
├── nginx/             # Proxy Configurations
├── models/            # Serialised .keras models & scalers (Excluded from Git)
└── docker-compose.yml # Orchestration logic

