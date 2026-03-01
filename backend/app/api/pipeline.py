"""
pipeline.py — Endpoints for triggering the ETL pipeline and viewing run history.
"""
from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List

from app.database import get_db
from app.models.orm import PipelineRun
from app.models.schemas import PipelineRunOut, PipelineTriggerResponse
from app.services.pipeline import run_full_pipeline, run_prices_only, run_news_only

router = APIRouter(prefix="/pipeline", tags=["Pipeline"])


@router.post("/run", response_model=PipelineTriggerResponse)
def trigger_full_pipeline(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """
    Manually trigger the full ETL pipeline (prices + news).
    Runs in the background so the API responds immediately.
    Check /api/pipeline/runs to see the result.
    """
    background_tasks.add_task(run_full_pipeline, db)
    return PipelineTriggerResponse(
        message="Full pipeline triggered — running in background.",
        run_type="full",
    )


@router.post("/run/prices", response_model=PipelineTriggerResponse)
def trigger_prices_pipeline(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """Trigger only the stock prices sub-pipeline."""
    background_tasks.add_task(run_prices_only, db)
    return PipelineTriggerResponse(
        message="Prices pipeline triggered — running in background.",
        run_type="prices",
    )


@router.post("/run/news", response_model=PipelineTriggerResponse)
def trigger_news_pipeline(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """Trigger only the news articles sub-pipeline."""
    background_tasks.add_task(run_news_only, db)
    return PipelineTriggerResponse(
        message="News pipeline triggered — running in background.",
        run_type="news",
    )


@router.get("/runs", response_model=List[PipelineRunOut])
def get_pipeline_runs(
    limit: int = 20,
    db: Session = Depends(get_db),
):
    """
    Returns the audit log of past pipeline executions.
    Shows status, row counts, and duration for each run.
    """
    return (
        db.query(PipelineRun)
        .order_by(desc(PipelineRun.started_at))
        .limit(limit)
        .all()
    )


@router.get("/runs/latest", response_model=PipelineRunOut)
def get_latest_run(db: Session = Depends(get_db)):
    """Returns the most recent pipeline run."""
    run = (
        db.query(PipelineRun)
        .order_by(desc(PipelineRun.started_at))
        .first()
    )
    if not run:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="No pipeline runs found yet.")
    return run
