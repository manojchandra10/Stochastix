import pandas as pd
import requests
import io
import logging
import requests_cache
from datetime import timedelta

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# SETUP CACHING FOR ECB RESPONSES
# Stores ECB responses for 1 hour to prevent redundant network calls.
session = requests_cache.CachedSession(
    'ecb_cache',
    expire_after=timedelta(hours=1) 
)

# Generic User-Agent to avoid being blocked by ECB. We are not scraping, just fetching data, but it's good practice to identify ourselves.
# We just need to tell ECB we are a script, not a malicious bot.
session.headers.update({
    "User-Agent": "Stochastix/1.0 (Student Project; Data Science Portfolio)",
    "Accept": "text/csv"
})

def fetch_data(ticker: str, start_date: str = "2000-01-01"):

    # Parse the target currency from the ticker
    # assume the input is always EUR vs X.
    target_currency = ticker.replace("EUR", "").replace("=X", "")
    
    # the "Identity" case (EUR vs EUR)
    if target_currency == "EUR":
        logger.warning("Requesting EUR-EUR rate. Returning 1.0 identity.")
        # dummy dataframe for EUR/EUR = 1.0
        dates = pd.date_range(start=start_date, end=pd.Timestamp.now())
        df = pd.DataFrame(index=dates)
        df["Close"] = 1.0
        return df

    logger.info(f"Fetching ECB data for EUR -> {target_currency} | Start: {start_date}")
    
    # ECB SDMX 2.1 REST API URL
    # Format: D.{CURRENCY}.EUR.SP00.A
    # D = Daily, SP00 = Spot, A = Average
    url = f"https://data-api.ecb.europa.eu/service/data/EXR/D.{target_currency}.EUR.SP00.A"
    
    params = {
        "startPeriod": start_date,
        "format": "csvdata" # request CSV for easier parsing
    }
    
    try:
        response = session.get(url, params=params)
        
        if response.status_code != 200:
            logger.warning(f"ECB API returned {response.status_code} for {target_currency}")
            return None

        # Parse CSV Response
        df = pd.read_csv(io.StringIO(response.text))
        
        # ECB CSV Columns: TIME_PERIOD, OBS_VALUE, etc.
        if "TIME_PERIOD" not in df.columns or "OBS_VALUE" not in df.columns:
            logger.error(f"Unexpected ECB format for {target_currency}")
            return None
            
        # Rename and Clean
        df = df.rename(columns={"TIME_PERIOD": "Date", "OBS_VALUE": "Close"})
        df["Date"] = pd.to_datetime(df["Date"])
        df.set_index("Date", inplace=True)
        
        # Sort chronologically
        df.sort_index(inplace=True)
        
        # Keep only the Close column
        df = df[["Close"]]
        
        # Ensure numeric data (ECB sometimes sends non-numeric flags)
        df = df.apply(pd.to_numeric, errors='coerce')
        df.dropna(inplace=True)
        
        logger.info(f"Successfully fetched {len(df)} rows for EUR{target_currency}.")
        return df

    except Exception as e:
        logger.error(f"Error fetching ECB data for {target_currency}: {str(e)}")
        return None