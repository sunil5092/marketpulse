"""
config.py — Reads all configuration from environment / .env file.
"""
import os
from dotenv import load_dotenv

load_dotenv()

# ── Database ───────────────────────────────────────────────────
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:password@localhost:5432/marketpulse"
)

# ── External APIs ──────────────────────────────────────────────
NEWS_API_KEY = os.getenv("NEWS_API_KEY", "")

# ── App ────────────────────────────────────────────────────────
APP_ENV  = os.getenv("APP_ENV", "development")
APP_PORT = int(os.getenv("APP_PORT", 8000))

CORS_ORIGINS = [
    o.strip()
    for o in os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
]

# ── Pipeline ───────────────────────────────────────────────────
PIPELINE_INTERVAL_MINUTES = int(os.getenv("PIPELINE_INTERVAL_MINUTES", 30))

# ── Watchlist ──────────────────────────────────────────────────
WATCHLIST = [
    t.strip()
    for t in os.getenv(
        "WATCHLIST",
        "AAPL,GOOGL,MSFT,AMZN,NVDA,TSLA,META,NFLX"
    ).split(",")
]
