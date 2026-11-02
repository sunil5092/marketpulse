"""
main.py — MarketPulse FastAPI application entry point.

Run locally:
    uvicorn app.main:app --reload --port 8000

Swagger docs:
    http://localhost:8000/docs
"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import CORS_ORIGINS, APP_ENV, WATCHLIST
from app.database import create_tables
from app.scheduler.jobs import start_scheduler, stop_scheduler
from app.api import health, stocks, news, pipeline, dashboard

# ── Logging ────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s — %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


# ── Lifespan (startup + shutdown) ──────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    # STARTUP
    logger.info("=" * 55)
    logger.info("  MarketPulse API starting...")
    logger.info(f"  ENV       : {APP_ENV}")
    logger.info(f"  Watchlist : {WATCHLIST}")

    create_tables()
    logger.info("  DB tables : created / verified ✓")

    start_scheduler()
    logger.info("  Scheduler : started ✓")
    logger.info("=" * 55)

    yield

    # SHUTDOWN
    stop_scheduler()
    logger.info("MarketPulse API shut down.")


# ── App ────────────────────────────────────────────────────────
app = FastAPI(
    title="MarketPulse API",
    description=(
        "Scheduled stock & financial news data pipeline (30-minute ETL).\n\n"
        "Fetches from Yahoo Finance + NewsAPI, transforms, and stores in PostgreSQL.\n"
        "Pipeline runs automatically every 30 minutes via APScheduler."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

# ── CORS ───────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if APP_ENV == "development" else CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ────────────────────────────────────────────────────
app.include_router(health.router,    prefix="/api")
app.include_router(stocks.router,    prefix="/api")
app.include_router(news.router,      prefix="/api")
app.include_router(pipeline.router,  prefix="/api")
app.include_router(dashboard.router, prefix="/api")


@app.get("/", tags=["Root"])
def root():
    return {
        "service": "MarketPulse API",
        "docs":    "/docs",
        "health":  "/api/health",
    }
