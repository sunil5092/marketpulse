"""
schemas.py — Pydantic models for API request/response serialization.
"""
from __future__ import annotations
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


# ── Stock Schemas ──────────────────────────────────────────────
class StockPriceOut(BaseModel):
    id:         int
    ticker:     str
    date:       datetime
    open:       float
    high:       float
    low:        float
    close:      float
    volume:     float
    pct_change: Optional[float]

    model_config = {"from_attributes": True}


class StockSummary(BaseModel):
    ticker:        str
    latest_close:  float
    prev_close:    float
    pct_change:    float
    day_high:      float
    day_low:       float
    week_high:     float
    week_low:      float
    avg_volume:    float
    data_points:   int


class StockHistory(BaseModel):
    ticker: str
    prices: List[StockPriceOut]


# ── News Schemas ───────────────────────────────────────────────
class NewsArticleOut(BaseModel):
    id:           int
    ticker:       Optional[str]
    title:        str
    description:  Optional[str]
    url:          str
    source:       Optional[str]
    published_at: Optional[datetime]
    sentiment:    Optional[str]

    model_config = {"from_attributes": True}


# ── Pipeline Schemas ───────────────────────────────────────────
class PipelineRunOut(BaseModel):
    id:              int
    run_type:        str
    status:          str
    tickers_fetched: int
    rows_inserted:   int
    rows_skipped:    int
    error_message:   Optional[str]
    started_at:      datetime
    finished_at:     Optional[datetime]
    duration_secs:   Optional[float]

    model_config = {"from_attributes": True}


class PipelineTriggerResponse(BaseModel):
    message:  str
    run_type: str


# ── Dashboard Schema ───────────────────────────────────────────
class DashboardData(BaseModel):
    watchlist:        List[StockSummary]
    recent_news:      List[NewsArticleOut]
    last_pipeline_run: Optional[PipelineRunOut]
    total_data_points: int


# ── Health ─────────────────────────────────────────────────────
class HealthResponse(BaseModel):
    status:   str
    service:  str
    version:  str
    db:       str          # "connected" | "error"
