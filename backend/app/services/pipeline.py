"""
pipeline.py — ETL Pipeline Orchestrator.

This is the heart of the data engineering project.
It wires together Extract → Transform → Load and:
  - Logs every run to the pipeline_runs table (audit trail)
  - Tracks timing, row counts, and errors
  - Can be triggered manually via API or automatically via scheduler

Pipeline flow:
  1. fetch_stock_prices()   → raw DataFrames
  2. transform_stock_prices() → clean dicts
  3. load_stock_prices()     → PostgreSQL insert

  4. fetch_news()            → raw article dicts
  5. transform_news()        → clean dicts
  6. load_news_articles()    → PostgreSQL insert
"""
from __future__ import annotations

import logging
import time
from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session

from app.config import WATCHLIST
from app.models.orm import PipelineRun
from app.services.fetcher import fetch_stock_prices, fetch_news
from app.services.transformer import transform_stock_prices, transform_news
from app.services.loader import load_stock_prices, load_news_articles

logger = logging.getLogger(__name__)


# ══════════════════════════════════════════════════════════════
# FULL PIPELINE
# ══════════════════════════════════════════════════════════════
def run_full_pipeline(
    db: Session,
    tickers: Optional[list] = None,
) -> PipelineRun:
    """
    Run the complete ETL pipeline: prices + news for all tickers.

    Args:
        db:      SQLAlchemy session
        tickers: Optional override list; defaults to WATCHLIST from config

    Returns:
        PipelineRun ORM object with results logged
    """
    tickers = tickers or WATCHLIST
    run = _start_run(db, run_type="full")

    total_inserted = 0
    total_skipped  = 0

    try:
        logger.info(f"Pipeline START — tickers={tickers}")

        # ── PRICES ─────────────────────────────────────────────
        logger.info("Step 1/4: Fetching stock prices...")
        raw_prices = fetch_stock_prices(tickers, days=30)

        logger.info("Step 2/4: Transforming stock prices...")
        clean_prices = transform_stock_prices(raw_prices)

        logger.info("Step 3/4: Loading stock prices into DB...")
        p_ins, p_skip = load_stock_prices(db, clean_prices)
        total_inserted += p_ins
        total_skipped  += p_skip

        # ── NEWS ───────────────────────────────────────────────
        logger.info("Step 4a: Fetching news articles...")
        raw_news = fetch_news(tickers, days=3)

        logger.info("Step 4b: Transforming news articles...")
        clean_news = transform_news(raw_news)

        logger.info("Step 4c: Loading news articles into DB...")
        n_ins, n_skip = load_news_articles(db, clean_news)
        total_inserted += n_ins
        total_skipped  += n_skip

        _finish_run(
            db, run,
            status="success",
            tickers_fetched=len(tickers),
            rows_inserted=total_inserted,
            rows_skipped=total_skipped,
        )
        logger.info(f"Pipeline DONE — inserted={total_inserted}, skipped={total_skipped}")

    except Exception as e:
        logger.error(f"Pipeline FAILED: {e}", exc_info=True)
        _finish_run(db, run, status="failed", error_message=str(e))

    return run


def run_prices_only(db: Session, tickers: Optional[list] = None) -> PipelineRun:
    """Run only the stock prices sub-pipeline."""
    tickers = tickers or WATCHLIST
    run = _start_run(db, run_type="prices")

    try:
        raw    = fetch_stock_prices(tickers, days=30)
        clean  = transform_stock_prices(raw)
        ins, sk = load_stock_prices(db, clean)
        _finish_run(db, run, status="success",
                    tickers_fetched=len(tickers), rows_inserted=ins, rows_skipped=sk)
    except Exception as e:
        _finish_run(db, run, status="failed", error_message=str(e))

    return run


def run_news_only(db: Session, tickers: Optional[list] = None) -> PipelineRun:
    """Run only the news sub-pipeline."""
    tickers = tickers or WATCHLIST
    run = _start_run(db, run_type="news")

    try:
        raw    = fetch_news(tickers, days=3)
        clean  = transform_news(raw)
        ins, sk = load_news_articles(db, clean)
        _finish_run(db, run, status="success",
                    tickers_fetched=len(tickers), rows_inserted=ins, rows_skipped=sk)
    except Exception as e:
        _finish_run(db, run, status="failed", error_message=str(e))

    return run


# ══════════════════════════════════════════════════════════════
# INTERNAL HELPERS
# ══════════════════════════════════════════════════════════════
def _start_run(db: Session, run_type: str) -> PipelineRun:
    """Create a PipelineRun row with status='running' and return it."""
    run = PipelineRun(
        run_type   = run_type,
        status     = "running",
        started_at = datetime.utcnow(),
    )
    db.add(run)
    db.commit()
    db.refresh(run)
    return run


def _finish_run(
    db: Session,
    run: PipelineRun,
    status: str,
    tickers_fetched: int = 0,
    rows_inserted:   int = 0,
    rows_skipped:    int = 0,
    error_message: Optional[str] = None,
) -> None:
    """Update PipelineRun with final status, counts, and duration."""
    finished = datetime.utcnow()
    duration = (finished - run.started_at).total_seconds()

    run.status          = status
    run.tickers_fetched = tickers_fetched
    run.rows_inserted   = rows_inserted
    run.rows_skipped    = rows_skipped
    run.error_message   = error_message
    run.finished_at     = finished
    run.duration_secs   = round(duration, 2)

    db.commit()
    db.refresh(run)
