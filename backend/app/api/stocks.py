"""
stocks.py — Endpoints for querying stock price data from the database.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional

from app.database import get_db
from app.models.orm import StockPrice
from app.models.schemas import StockPriceOut, StockSummary, StockHistory
from app.config import WATCHLIST

router = APIRouter(prefix="/stocks", tags=["Stocks"])


@router.get("/watchlist", response_model=List[str])
def get_watchlist():
    """Returns the configured list of tracked ticker symbols."""
    return WATCHLIST


@router.get("/summary", response_model=List[StockSummary])
def get_all_summaries(db: Session = Depends(get_db)):
    """
    Returns a summary card for each ticker in the watchlist.
    Used to populate the dashboard overview cards.
    """
    summaries = []

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

        summaries.append(StockSummary(
            ticker        = ticker,
            latest_close  = latest.close,
            prev_close    = prev.close,
            pct_change    = round(((latest.close - prev.close) / prev.close) * 100, 4),
            day_high      = latest.high,
            day_low       = latest.low,
            week_high     = max(highs[:7]),
            week_low      = min(lows[:7]),
            avg_volume    = round(sum(volumes) / len(volumes), 0),
            data_points   = len(rows),
        ))

    return summaries


@router.get("/{ticker}/history", response_model=StockHistory)
def get_stock_history(
    ticker: str,
    limit: int = Query(default=30, ge=1, le=365),
    db: Session = Depends(get_db),
):
    """
    Returns OHLCV price history for a single ticker.
    Used to render the line chart on the detail page.
    """
    ticker = ticker.upper()
    rows = (
        db.query(StockPrice)
        .filter(StockPrice.ticker == ticker)
        .order_by(StockPrice.date)
        .limit(limit)
        .all()
    )

    if not rows:
        raise HTTPException(
            status_code=404,
            detail=f"No price data found for ticker '{ticker}'. "
                   f"Run the pipeline first: POST /api/pipeline/run"
        )

    return StockHistory(ticker=ticker, prices=rows)


@router.get("/{ticker}/latest", response_model=StockPriceOut)
def get_latest_price(ticker: str, db: Session = Depends(get_db)):
    """Returns the most recent price record for a ticker."""
    ticker = ticker.upper()
    row = (
        db.query(StockPrice)
        .filter(StockPrice.ticker == ticker)
        .order_by(desc(StockPrice.date))
        .first()
    )
    if not row:
        raise HTTPException(status_code=404, detail=f"No data for {ticker}")
    return row
