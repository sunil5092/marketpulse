"""
test_api.py — MarketPulse API test suite.

Run: cd backend && pytest tests/ -v
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_root():
    resp = client.get("/")
    assert resp.status_code == 200
    assert "MarketPulse" in resp.json()["service"]


def test_health():
    resp = client.get("/api/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert "db" in data


def test_watchlist():
    resp = client.get("/api/stocks/watchlist")
    assert resp.status_code == 200
    tickers = resp.json()
    assert isinstance(tickers, list)
    assert len(tickers) > 0
    assert "AAPL" in tickers


def test_stock_history_not_found():
    resp = client.get("/api/stocks/FAKEXYZ/history")
    assert resp.status_code == 404


def test_news_empty():
    resp = client.get("/api/news")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


def test_news_sentiment_filter():
    resp = client.get("/api/news?sentiment=positive")
    assert resp.status_code == 200


def test_news_sentiment_summary():
    resp = client.get("/api/news/sentiment-summary")
    assert resp.status_code == 200
    data = resp.json()
    assert "positive" in data
    assert "negative" in data
    assert "neutral"  in data
    assert "total"    in data


def test_pipeline_runs_empty():
    resp = client.get("/api/pipeline/runs")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


def test_dashboard():
    resp = client.get("/api/dashboard")
    assert resp.status_code == 200
    data = resp.json()
    assert "watchlist"          in data
    assert "recent_news"        in data
    assert "total_data_points"  in data
