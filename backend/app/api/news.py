"""
news.py — Endpoints for querying financial news from the database.
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional

from app.database import get_db
from app.models.orm import NewsArticle
from app.models.schemas import NewsArticleOut

router = APIRouter(prefix="/news", tags=["News"])


@router.get("", response_model=List[NewsArticleOut])
def get_news(
    ticker:    Optional[str] = Query(None, description="Filter by ticker symbol"),
    sentiment: Optional[str] = Query(None, description="Filter: positive | negative | neutral"),
    limit:     int           = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """
    Returns recent financial news articles with optional filtering.

    - Filter by ticker: ?ticker=AAPL
    - Filter by sentiment: ?sentiment=positive
    - Combine: ?ticker=NVDA&sentiment=positive
    """
    query = db.query(NewsArticle).order_by(desc(NewsArticle.published_at))

    if ticker:
        query = query.filter(NewsArticle.ticker == ticker.upper())

    if sentiment and sentiment in ("positive", "negative", "neutral"):
        query = query.filter(NewsArticle.sentiment == sentiment)

    return query.limit(limit).all()


@router.get("/sentiment-summary")
def get_sentiment_summary(
    ticker: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """
    Returns a count breakdown of positive / negative / neutral
    news articles, optionally filtered by ticker.
    Used to render the sentiment bar on the dashboard.
    """
    query = db.query(NewsArticle)
    if ticker:
        query = query.filter(NewsArticle.ticker == ticker.upper())

    articles = query.all()
    total    = len(articles)

    if total == 0:
        return {"positive": 0, "negative": 0, "neutral": 0, "total": 0}

    counts = {"positive": 0, "negative": 0, "neutral": 0}
    for a in articles:
        key = a.sentiment if a.sentiment in counts else "neutral"
        counts[key] += 1

    return {
        **counts,
        "total":             total,
        "positive_pct":      round(counts["positive"] / total * 100, 1),
        "negative_pct":      round(counts["negative"] / total * 100, 1),
        "neutral_pct":       round(counts["neutral"]  / total * 100, 1),
    }
