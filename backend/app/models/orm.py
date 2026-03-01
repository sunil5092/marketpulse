"""
orm.py — SQLAlchemy ORM models (database tables).

Tables:
  stock_prices   → OHLCV data per ticker per day
  news_articles  → financial news headlines with sentiment label
  pipeline_runs  → audit log of every ETL pipeline execution
"""
from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Float, DateTime,
    Boolean, Text, UniqueConstraint, Index
)
from app.database import Base


class StockPrice(Base):
    """
    Daily OHLCV (Open/High/Low/Close/Volume) price data for each stock.
    One row per ticker per trading day.
    """
    __tablename__ = "stock_prices"

    id         = Column(Integer, primary_key=True, index=True)
    ticker     = Column(String(10), nullable=False)
    date       = Column(DateTime, nullable=False)
    open       = Column(Float, nullable=False)
    high       = Column(Float, nullable=False)
    low        = Column(Float, nullable=False)
    close      = Column(Float, nullable=False)
    volume     = Column(Float, nullable=False)
    pct_change = Column(Float, nullable=True)   # day-over-day % change
    created_at = Column(DateTime, default=datetime.utcnow)

    # Prevent duplicate rows for the same ticker + date
    __table_args__ = (
        UniqueConstraint("ticker", "date", name="uq_stock_ticker_date"),
        Index("ix_stock_ticker_date", "ticker", "date"),
    )

    def __repr__(self):
        return f"<StockPrice {self.ticker} {self.date.date()} close={self.close}>"


class NewsArticle(Base):
    """
    Financial news articles fetched from NewsAPI.
    Includes a simple rule-based sentiment label.
    """
    __tablename__ = "news_articles"

    id           = Column(Integer, primary_key=True, index=True)
    ticker       = Column(String(10), nullable=True)   # which stock this relates to
    title        = Column(String(500), nullable=False)
    description  = Column(Text, nullable=True)
    url          = Column(String(1000), nullable=False, unique=True)
    source       = Column(String(200), nullable=True)
    published_at = Column(DateTime, nullable=True)
    sentiment    = Column(String(10), nullable=True)   # positive / negative / neutral
    created_at   = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index("ix_news_ticker", "ticker"),
        Index("ix_news_published", "published_at"),
    )

    def __repr__(self):
        return f"<NewsArticle {self.ticker} '{self.title[:40]}...'>"


class PipelineRun(Base):
    """
    Audit log — records every ETL pipeline execution.
    Useful for monitoring, debugging, and demonstrating
    data engineering awareness in interviews.
    """
    __tablename__ = "pipeline_runs"

    id              = Column(Integer, primary_key=True, index=True)
    run_type        = Column(String(50), nullable=False)   # "prices" | "news" | "full"
    status          = Column(String(20), nullable=False)   # "success" | "failed" | "running"
    tickers_fetched = Column(Integer, default=0)
    rows_inserted   = Column(Integer, default=0)
    rows_skipped    = Column(Integer, default=0)
    error_message   = Column(Text, nullable=True)
    started_at      = Column(DateTime, default=datetime.utcnow)
    finished_at     = Column(DateTime, nullable=True)
    duration_secs   = Column(Float, nullable=True)

    def __repr__(self):
        return f"<PipelineRun {self.run_type} {self.status} rows={self.rows_inserted}>"
