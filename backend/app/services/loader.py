"""
loader.py — ETL LOAD step.

Takes transformed records from transformer.py and:
  - Inserts new rows into PostgreSQL
  - Skips duplicates gracefully (upsert strategy)
  - Returns counts of inserted vs skipped rows

This is the final step of the ETL pipeline.
"""
from __future__ import annotations

import logging
from typing import List, Dict, Any, Tuple

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.models.orm import StockPrice, NewsArticle

logger = logging.getLogger(__name__)


# ══════════════════════════════════════════════════════════════
# STOCK PRICES LOADER
# ══════════════════════════════════════════════════════════════
def load_stock_prices(
    db: Session,
    records: List[Dict[str, Any]],
) -> Tuple[int, int]:
    """
    Insert transformed stock price records into the database.

    Strategy: try to insert each row; if a UniqueConstraint violation
    occurs (same ticker + date already exists), skip and count it.

    Returns:
        (inserted_count, skipped_count)
    """
    inserted = 0
    skipped  = 0

    for record in records:
        try:
            row = StockPrice(**record)
            db.add(row)
            db.flush()     # flush to catch constraint errors early
            inserted += 1

        except IntegrityError:
            db.rollback()
            skipped += 1

        except Exception as e:
            db.rollback()
            logger.error(f"Failed to insert stock price record: {e} | Record: {record}")
            skipped += 1

    try:
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"Final commit failed for stock prices: {e}")
        raise

    logger.info(f"Stock prices — inserted: {inserted}, skipped: {skipped}")
    return inserted, skipped


# ══════════════════════════════════════════════════════════════
# NEWS ARTICLES LOADER
# ══════════════════════════════════════════════════════════════
def load_news_articles(
    db: Session,
    records: List[Dict[str, Any]],
) -> Tuple[int, int]:
    """
    Insert transformed news article records into the database.

    Deduplication is handled by the unique constraint on `url`.

    Returns:
        (inserted_count, skipped_count)
    """
    inserted = 0
    skipped  = 0

    for record in records:
        try:
            row = NewsArticle(**record)
            db.add(row)
            db.flush()
            inserted += 1

        except IntegrityError:
            db.rollback()
            skipped += 1   # URL already exists — skip it

        except Exception as e:
            db.rollback()
            logger.error(f"Failed to insert news article: {e}")
            skipped += 1

    try:
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"Final commit failed for news articles: {e}")
        raise

    logger.info(f"News articles — inserted: {inserted}, skipped: {skipped}")
    return inserted, skipped
