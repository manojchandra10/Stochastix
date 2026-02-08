import axios from 'axios';

const API_URL = 'http://localhost:8000/api/v1';

export interface ForecastPoint {
  date: string;
  rate: number;
  type?: 'history' | 'forecast' | 'indicative';
}

export interface PredictionResponse {
  pair: string;
  forecast: ForecastPoint[];
}

export interface SentimentResponse {
  pair: string;
  sentiment: {
    score: number;
    mood: string;
    headline_count: number;
    top_headline: string;
  };
}

export const fetchForecast = async (
  from: string,
  to: string,
  days: number = 30
): Promise<PredictionResponse> => {
  try {
    const response = await axios.post(`${API_URL}/predict`, {
      from_currency: from,
      to_currency: to,
      days: days
    });
    return response.data;
  } catch (error) {
    console.error('API Error:', error);
    throw error;
  }
};

export const fetchSentiment = async (
  from: string,
  to: string
): Promise<SentimentResponse> => {
  try {
    const response = await axios.post(`${API_URL}/sentiment`, {
      from_currency: from,
      to_currency: to
    });
    return response.data;
  } catch (error) {
    console.error('Sentiment API Error:', error);
    throw error;
  }
};

export interface ScorecardItem {
  currency: string;
  pred: string;
  actual: string;
  label: string;
  status: 'success' | 'danger' | 'warning';
}

export const fetchScoreboard = async (): Promise<ScorecardItem[]> => {
  try {
    const response = await axios.get(`${API_URL}/audit/scoreboard`);
    return response.data.scoreboard;
  } catch (error) {
    console.error("Scoreboard Error", error);
    return [];
  }
};