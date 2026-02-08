import yfinance as yf
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import requests_cache
from datetime import timedelta
import logging

# Configure logger
logger = logging.getLogger(__name__)

# Ensure lexicon
try:
    nltk.data.find('vader_lexicon')
except LookupError:
    nltk.download('vader_lexicon')

# Cache for sentiment
session = requests_cache.CachedSession('sentiment_cache', expire_after=timedelta(hours=1))

def get_market_sentiment(pair_code: str):
    try:
        # Standardise ticker for Yahoo (Yahoo needs =X)
        ticker_symbol = f"{pair_code}=X"
        
        # Use a fresh session if needed, but here we use the cached one
        ticker = yf.Ticker(ticker_symbol, session=session)
        
        # WRAP THIS IN A TRY BLOCK specifically for the network call
        try:
            news_list = ticker.news
        except Exception as e:
            logger.warning(f"Yahoo Finance connection failed: {e}")
            return {"score": 0, "mood": "Neutral (Data Unavailable)", "headline_count": 0, "top_headline": ""}
        
        if not news_list:
            return {"score": 0, "mood": "Neutral", "headline_count": 0, "top_headline": ""}

        analyzer = SentimentIntensityAnalyzer()
        total_score = 0
        headlines = []

        for item in news_list:
            title = item.get('title', '')
            headlines.append(title)
            score = analyzer.polarity_scores(title)['compound']
            total_score += score

        avg_score = total_score / len(news_list)
        
        if avg_score > 0.05:
            mood = "Bullish (Positive)"
        elif avg_score < -0.05:
            mood = "Bearish (Negative)"
        else:
            mood = "Neutral"

        return {
            "score": round(avg_score, 2),
            "mood": mood,
            "headline_count": len(news_list),
            "top_headline": headlines[0] if headlines else ""
        }
    except Exception as e:
        # GLOBAL FAIL-SAFE: Never crash the app just because news is missing
        logger.error(f"Sentiment Engine Error: {e}")
        return {
            "score": 0,
            "mood": "Neutral",
            "headline_count": 0,
            "top_headline": "Sentiment analysis temporarily unavailable."
        }