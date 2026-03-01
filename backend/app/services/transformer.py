"""
transformer.py — ETL TRANSFORM step.

Takes raw data from fetcher.py and:
  - Cleans nulls, bad values, duplicates
  - Calculates derived fields (pct_change, sentiment)
  - Shapes data into dicts ready for the database loader

This is where your data cleaning skills shine — interviewers love this layer.
"""
from __future__ import annotations

import logging
import re
from datetime import datetime, timezone
from typing import List, Dict, Any

import pandas as pd

logger = logging.getLogger(__name__)

# ── Sentiment keywords for simple rule-based classification ───
_POSITIVE_WORDS = {
    "surge", "surges", "surged", "record", "beat", "beats", "growth",
    "grows", "gains", "gain", "rises", "rise", "rally", "profit",
    "profits", "strong", "jump", "jumps", "jumped", "upgrade",
    "upgraded", "bullish", "outperform", "revenue", "expands",
}

_NEGATIVE_WORDS = {
    "fall", "falls", "fell", "drop", "drops", "dropped", "decline",
    "declines", "declined", "loss", "losses", "miss", "misses",
    "missed", "cut", "cuts", "layoff", "layoffs", "crash", "crashes",
    "plunge", "plunges", "plunged", "downgrade", "downgraded",
    "bearish", "underperform", "concern", "concerns", "risk",
}


# ══════════════════════════════════════════════════════════════
# STOCK PRICES TRANSFORMER
# ══════════════════════════════════════════════════════════════
def transform_stock_prices(raw: Dict[str, pd.DataFrame]) -> List[Dict[str, Any]]:
    """
    Clean and transform raw OHLCV DataFrames into a list of dicts
    ready for database insertion.

    Transformations:
      - Drop rows with null Close prices
      - Round floats to 4 decimal places
      - Calculate day-over-day percentage change
      - Convert timezone-aware datetimes to UTC naive
      - Remove duplicate dates per ticker
    """
    records: List[Dict[str, Any]] = []

    for ticker, df in raw.items():
        if df.empty:
            continue

        try:
            df = df.copy()

            # ── 1. Drop nulls in critical columns ─────────────
            df = df.dropna(subset=["Close"])
            if df.empty:
                logger.warning(f"{ticker}: all rows had null Close — skipping")
                continue

            # ── 2. Sort by date ascending ──────────────────────
            df = df.sort_values("Date").reset_index(drop=True)

            # ── 3. Convert timezone-aware → UTC naive datetime ─
            df["Date"] = pd.to_datetime(df["Date"])
            if df["Date"].dt.tz is not None:
                df["Date"] = df["Date"].dt.tz_convert("UTC").dt.tz_localize(None)

            # ── 4. Calculate % change day-over-day ────────────
            df["pct_change"] = df["Close"].pct_change() * 100
            df["pct_change"] = df["pct_change"].round(4)

            # ── 5. Round OHLCV values ──────────────────────────
            for col in ["Open", "High", "Low", "Close"]:
                df[col] = df[col].round(4)
            df["Volume"] = df["Volume"].fillna(0).astype(float)

            # ── 6. Remove duplicates (same ticker + date) ──────
            df = df.drop_duplicates(subset=["Date"])

            # ── 7. Build list of dicts ─────────────────────────
            for _, row in df.iterrows():
                records.append({
                    "ticker":     ticker,
                    "date":       row["Date"].to_pydatetime(),
                    "open":       float(row["Open"]),
                    "high":       float(row["High"]),
                    "low":        float(row["Low"]),
                    "close":      float(row["Close"]),
                    "volume":     float(row["Volume"]),
                    "pct_change": None if pd.isna(row["pct_change"]) else float(row["pct_change"]),
                })

            logger.info(f"Transformed {len(records)} price records for {ticker}")

        except Exception as e:
            logger.error(f"Failed to transform prices for {ticker}: {e}")

    return records


# ══════════════════════════════════════════════════════════════
# NEWS ARTICLES TRANSFORMER
# ══════════════════════════════════════════════════════════════
def transform_news(raw_articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Clean and enrich raw NewsAPI articles.

    Transformations:
      - Remove articles with missing title or URL
      - Deduplicate by URL
      - Parse publishedAt into datetime
      - Apply rule-based sentiment classification
      - Truncate overly long descriptions
    """
    seen_urls: set = set()
    records: List[Dict[str, Any]] = []

    for article in raw_articles:
        try:
            title = (article.get("title") or "").strip()
            url   = (article.get("url")   or "").strip()

            # ── Skip if missing key fields ─────────────────────
            if not title or not url:
                continue

            # ── Deduplicate by URL ─────────────────────────────
            if url in seen_urls:
                continue
            seen_urls.add(url)

            # ── Skip removed articles ──────────────────────────
            if title == "[Removed]":
                continue

            # ── Parse published date ───────────────────────────
            published_at = None
            raw_date = article.get("publishedAt")
            if raw_date:
                try:
                    published_at = datetime.fromisoformat(
                        raw_date.replace("Z", "+00:00")
                    ).replace(tzinfo=None)
                except ValueError:
                    pass

            # ── Truncate description ───────────────────────────
            description = (article.get("description") or "").strip()
            if len(description) > 1000:
                description = description[:997] + "..."

            # ── Rule-based sentiment ───────────────────────────
            sentiment = _classify_sentiment(title + " " + description)

            # ── Source name ────────────────────────────────────
            source_obj = article.get("source") or {}
            source = source_obj.get("name", "") if isinstance(source_obj, dict) else ""

            records.append({
                "ticker":       article.get("_ticker"),
                "title":        title[:500],
                "description":  description or None,
                "url":          url[:1000],
                "source":       source[:200] if source else None,
                "published_at": published_at,
                "sentiment":    sentiment,
            })

        except Exception as e:
            logger.error(f"Failed to transform article: {e}")

    logger.info(f"Transformed {len(records)} news articles")
    return records


def _classify_sentiment(text: str) -> str:
    """
    Rule-based sentiment classification using keyword matching.
    Simple but effective for financial headlines.

    Returns: "positive" | "negative" | "neutral"
    """
    words = set(re.findall(r"\b[a-z]+\b", text.lower()))

    pos_hits = len(words & _POSITIVE_WORDS)
    neg_hits = len(words & _NEGATIVE_WORDS)

    if pos_hits > neg_hits:
        return "positive"
    elif neg_hits > pos_hits:
        return "negative"
    else:
        return "neutral"
