import logging
from datetime import datetime, timezone

import psycopg2

from app.celery_app import celery_app
from app.config import settings
from app.services.ingest_service import run_bulk_ingest

logger = logging.getLogger(__name__)


def _update_job(sync_url: str, job_id: str, **kwargs) -> None:
    conn = psycopg2.connect(sync_url)
    conn.autocommit = True
    cur = conn.cursor()
    set_clauses = ", ".join(f"{k} = %s" for k in kwargs)
    values = list(kwargs.values()) + [job_id]
    cur.execute(f"UPDATE upload_jobs SET {set_clauses} WHERE id = %s", values)
    cur.close()
    conn.close()


@celery_app.task(bind=True, max_retries=3)
def bulk_ingest_task(self, job_id: str, file_path: str) -> None:
    sync_url = settings.SYNC_DATABASE_URL
    logger.info("Starting bulk ingest for job %s", job_id)

    try:
        _update_job(sync_url, job_id, status="processing")

        with open(file_path) as f:
            total_rows = sum(1 for _ in f) - 1  # subtract header
        _update_job(sync_url, job_id, total_rows=total_rows)

        def on_progress(processed: int) -> None:
            _update_job(sync_url, job_id, processed_rows=processed)

        total = run_bulk_ingest(file_path, sync_url, on_progress)

        _update_job(
            sync_url,
            job_id,
            status="completed",
            processed_rows=total,
            completed_at=datetime.now(timezone.utc),
        )
        logger.info("Job %s completed: %d rows", job_id, total)

    except Exception as exc:
        logger.exception("Job %s failed: %s", job_id, exc)
        _update_job(sync_url, job_id, status="failed", error_message=str(exc))
        raise self.retry(exc=exc, countdown=10)
