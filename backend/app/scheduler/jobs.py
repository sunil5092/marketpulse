"""
jobs.py — Background scheduler using APScheduler.

Runs the full ETL pipeline automatically every N minutes
(configured via PIPELINE_INTERVAL_MINUTES in .env).

This is what makes MarketPulse a real data pipeline —
not just a one-time script but a continuously running system.
"""
import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

from app.config import PIPELINE_INTERVAL_MINUTES
from app.database import SessionLocal
from app.services.pipeline import run_full_pipeline

logger = logging.getLogger(__name__)

# Global scheduler instance
scheduler = BackgroundScheduler(timezone="UTC")


def _scheduled_pipeline_job():
    """
    Wrapper that creates a DB session, runs the pipeline, and closes the session.
    This runs in a background thread managed by APScheduler.
    """
    logger.info("Scheduled pipeline job triggered")
    db = SessionLocal()
    try:
        run = run_full_pipeline(db)
        logger.info(
            f"Scheduled run complete — "
            f"status={run.status}, "
            f"inserted={run.rows_inserted}, "
            f"duration={run.duration_secs}s"
        )
    except Exception as e:
        logger.error(f"Scheduled pipeline job failed: {e}", exc_info=True)
    finally:
        db.close()


def start_scheduler():
    """Register and start the background scheduler."""
    scheduler.add_job(
        func=_scheduled_pipeline_job,
        trigger=IntervalTrigger(minutes=PIPELINE_INTERVAL_MINUTES),
        id="full_pipeline",
        name="Full ETL Pipeline",
        replace_existing=True,
        misfire_grace_time=60,   # if a run is missed, allow up to 60s late start
    )
    scheduler.start()
    logger.info(
        f"Scheduler started — pipeline runs every {PIPELINE_INTERVAL_MINUTES} minutes"
    )


def stop_scheduler():
    """Gracefully shut down the scheduler."""
    if scheduler.running:
        scheduler.shutdown(wait=False)
        logger.info("Scheduler stopped")
