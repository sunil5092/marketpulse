"""
dashboard.py — Single aggregated endpoint for the React dashboard.

Instead of making 4 separate API calls on page load,
the frontend calls /api/dashboard once and gets everything.
This is a common real-world pattern called a "BFF" (Backend for Frontend).
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import desc, func

from app.database import get_db
from app.models.orm import StockPrice, NewsArticle, PipelineRun
from app.models.schemas import DashboardData, StockSummary, NewsArticleOut, PipelineRunOut
from app.config import WATCHLIST

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("", response_model=DashboardData)
def get_dashboard(db: Session = Depends(get_db)):
    """
    Returns everything needed to render the main dashboard in one call:
    - Stock summary cards for all watchlist tickers
    - 10 most recent news articles
    - Most recent pipeline run status
    - Total data points in the database
    """

    # ── Stock summaries ────────────────────────────────────────
    watchlist_summaries = []
    for ticker in WATCHLIST:
        rows = (
            db.query(StockPrice)
            .filter(StockPrice.ticker == ticker)
            .order_by(desc(StockPrice.date))
            .limit(30)
            .all()
        )
        if len(rows) < 2:
            continue

        latest = rows[0]
        prev   = rows[1]
        closes  = [r.close  for r in rows]
        highs   = [r.high   for r in rows]
        lows    = [r.low    for r in rows]
        volumes = [r.volume for r in rows]

        watchlist_summaries.append(StockSummary(
            ticker        = ticker,
            latest_close  = latest.close,
            prev_close    = prev.close,
            pct_change    = round(((latest.close - prev.close) / prev.close) * 100, 4),
            day_high      = latest.high,
            day_low       = latest.low,
            week_high     = max(highs[:7]) if highs else latest.high,
            week_low      = min(lows[:7])  if lows  else latest.low,
            avg_volume    = round(sum(volumes) / len(volumes), 0),
            data_points   = len(rows),
        ))

    # ── Recent news ────────────────────────────────────────────
    recent_news = (
        db.query(NewsArticle)
        .order_by(desc(NewsArticle.published_at))
        .limit(10)
        .all()
    )

    # ── Last pipeline run ──────────────────────────────────────
    last_run = (
        db.query(PipelineRun)
        .order_by(desc(PipelineRun.started_at))
        .first()
    )

    # ── Total data points ──────────────────────────────────────
    total = db.query(func.count(StockPrice.id)).scalar() or 0

    return DashboardData(
        watchlist           = watchlist_summaries,
        recent_news         = [NewsArticleOut.model_validate(a) for a in recent_news],
        last_pipeline_run   = PipelineRunOut.model_validate(last_run) if last_run else None,
        total_data_points   = total,
    )
