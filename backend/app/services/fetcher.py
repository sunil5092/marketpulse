"""
fetcher.py — ETL EXTRACT step.

Pulls raw data from two sources:
  1. Yahoo Finance (via yfinance) — free, no API key needed
  2. NewsAPI                      — free tier (100 req/day), API key required

Both functions return raw pandas DataFrames / Python dicts.
The transformer (transformer.py) then cleans and shapes this data.
"""
from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any

import pandas as pd
import yfinance as yf
import requests

from app.config import NEWS_API_KEY

logger = logging.getLogger(__name__)


# ══════════════════════════════════════════════════════════════
# STOCK PRICES — Yahoo Finance (free, no key)
# ══════════════════════════════════════════════════════════════
def fetch_stock_prices(tickers: List[str], days: int = 30) -> Dict[str, pd.DataFrame]:
    """
    Fetch OHLCV price history for multiple tickers from Yahoo Finance.

    Args:
        tickers: List of stock ticker symbols e.g. ["AAPL", "GOOGL"]
        days:    Number of calendar days of history to fetch (default 30)

    Returns:
        Dict mapping ticker → DataFrame with columns:
        [Date, Open, High, Low, Close, Volume]
    """
    end   = datetime.now()
    start = end - timedelta(days=days)

    results: Dict[str, pd.DataFrame] = {}

    for ticker in tickers:
        try:
            logger.info(f"Fetching prices for {ticker}...")
            stock = yf.Ticker(ticker)
            df = stock.history(start=start, end=end, interval="1d")

            if df.empty:
                logger.warning(f"No price data returned for {ticker}")
                continue

            df = df.reset_index()
            df["Ticker"] = ticker

            # Keep only the columns we need
            df = df[["Date", "Open", "High", "Low", "Close", "Volume", "Ticker"]]
            results[ticker] = df
            logger.info(f"  {ticker}: {len(df)} rows fetched")

        except Exception as e:
            logger.error(f"Failed to fetch prices for {ticker}: {e}")

    return results


def fetch_single_stock_info(ticker: str) -> Dict[str, Any]:
    """
    Fetch live quote info for a single ticker (current price, market cap, etc.)
    Used for the real-time dashboard summary cards.
    """
    try:
        stock = yf.Ticker(ticker)
        info  = stock.info
        return {
            "ticker":         ticker,
            "current_price":  info.get("currentPrice") or info.get("regularMarketPrice"),
            "market_cap":     info.get("marketCap"),
            "pe_ratio":       info.get("trailingPE"),
            "52w_high":       info.get("fiftyTwoWeekHigh"),
            "52w_low":        info.get("fiftyTwoWeekLow"),
            "name":           info.get("longName", ticker),
        }
    except Exception as e:
        logger.error(f"Failed to fetch info for {ticker}: {e}")
        return {"ticker": ticker}


# ══════════════════════════════════════════════════════════════
# FINANCIAL NEWS — NewsAPI (free tier: 100 req/day)
# ══════════════════════════════════════════════════════════════
def fetch_news(tickers: List[str], days: int = 3) -> List[Dict[str, Any]]:
    """
    Fetch recent financial news articles for a list of tickers.

    Uses NewsAPI's /everything endpoint.
    Free tier allows 100 requests/day and articles up to 1 month old.

    Args:
        tickers: List of ticker symbols to search news for
        days:    How many days back to search (default 3)

    Returns:
        List of raw article dicts from NewsAPI
    """
    if not NEWS_API_KEY:
        logger.warning("NEWS_API_KEY not set — skipping news fetch. Get a free key at newsapi.org")
        return _get_mock_news(tickers)

    all_articles: List[Dict[str, Any]] = []
    from_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")

    for ticker in tickers:
        try:
            # Search for articles mentioning the company name / ticker
            query = f"{ticker} stock"
            url   = "https://newsapi.org/v2/everything"
            params = {
                "q":          query,
                "from":       from_date,
                "language":   "en",
                "sortBy":     "publishedAt",
                "pageSize":   5,           # 5 articles per ticker
                "apiKey":     NEWS_API_KEY,
            }

            resp = requests.get(url, params=params, timeout=10)
            resp.raise_for_status()
            data = resp.json()

            articles = data.get("articles", [])
            for article in articles:
                article["_ticker"] = ticker   # tag with which ticker this is for

            all_articles.extend(articles)
            logger.info(f"  News for {ticker}: {len(articles)} articles")

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch news for {ticker}: {e}")

    return all_articles


def _get_mock_news(tickers: List[str]) -> List[Dict[str, Any]]:
    """
    Returns realistic mock news when NEWS_API_KEY is not set.
    Lets you run and demo the full pipeline without an API key.
    """
    from datetime import timezone
    now = datetime.now(timezone.utc).isoformat()

    mock = [
        {
            "_ticker":    "AAPL",
            "title":      "Apple Reports Record iPhone Sales in Q4",
            "description":"Apple's latest earnings beat analyst expectations driven by strong iPhone demand.",
            "url":        "https://example.com/apple-q4-earnings",
            "source":     {"name": "TechCrunch"},
            "publishedAt": now,
        },
        {
            "_ticker":    "GOOGL",
            "title":      "Google Expands AI Features Across Search and Gmail",
            "description":"Alphabet announces major AI integration across its flagship products.",
            "url":        "https://example.com/google-ai-expansion",
            "source":     {"name": "The Verge"},
            "publishedAt": now,
        },
        {
            "_ticker":    "MSFT",
            "title":      "Microsoft Azure Revenue Jumps 31% Year Over Year",
            "description":"Cloud business continues to be Microsoft's primary growth driver.",
            "url":        "https://example.com/msft-azure-growth",
            "source":     {"name": "Bloomberg"},
            "publishedAt": now,
        },
        {
            "_ticker":    "NVDA",
            "title":      "Nvidia GPU Demand Surges on AI Training Workloads",
            "description":"Data center GPU shipments hit record highs as AI adoption accelerates.",
            "url":        "https://example.com/nvidia-gpu-demand",
            "source":     {"name": "Reuters"},
            "publishedAt": now,
        },
        {
            "_ticker":    "TSLA",
            "title":      "Tesla Cuts Prices in Key Markets to Boost Demand",
            "description":"Tesla reduces vehicle prices in the US and Europe amid rising competition.",
            "url":        "https://example.com/tesla-price-cuts",
            "source":     {"name": "CNBC"},
            "publishedAt": now,
        },
    ]

    # Only return articles for tickers in our watchlist
    return [a for a in mock if a["_ticker"] in tickers]
