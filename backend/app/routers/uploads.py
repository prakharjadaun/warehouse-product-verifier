import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import require_admin
from app.models.upload_job import JobStatus, UploadJob
from app.models.user import User
from app.schemas.upload_job import JobStatusOut
from app.tasks.ingest_task import bulk_ingest_task

router = APIRouter(prefix="/uploads", tags=["uploads"])

UPLOAD_DIR = Path("uploads/csv")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@router.post("/csv", status_code=202)
async def upload_csv(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
):
    if not file.filename or not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are accepted")

    job_id = uuid.uuid4()
    safe_name = f"{job_id}_{file.filename}"
    file_path = UPLOAD_DIR / safe_name

    contents = await file.read()
    with open(file_path, "wb") as f:
        f.write(contents)

    job = UploadJob(
        id=job_id,
        filename=file.filename,
        file_path=str(file_path),
        status=JobStatus.pending,
    )
    db.add(job)
    await db.flush()

    bulk_ingest_task.delay(str(job_id), str(file_path))

    return {"job_id": str(job_id), "status": "pending"}


@router.get("/{job_id}/status", response_model=JobStatusOut)
async def get_job_status(
    job_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
):
    result = await db.execute(select(UploadJob).where(UploadJob.id == job_id))
    job = result.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    total = job.total_rows or 0
    percent = round(job.processed_rows / total * 100, 1) if total > 0 else 0.0

    return JobStatusOut(
        job_id=job.id,
        status=job.status,
        total_rows=job.total_rows,
        processed_rows=job.processed_rows,
        progress_percent=percent,
        error_message=job.error_message,
    )


@router.get("", tags=["uploads"])
async def list_upload_jobs(
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
):
    result = await db.execute(
        select(UploadJob).order_by(UploadJob.created_at.desc()).limit(limit)
    )
    jobs = result.scalars().all()
    return [
        {
            "job_id": str(j.id),
            "filename": j.filename,
            "status": j.status,
            "total_rows": j.total_rows,
            "processed_rows": j.processed_rows,
            "progress_percent": round(j.processed_rows / j.total_rows * 100, 1) if j.total_rows else 0.0,
            "created_at": j.created_at.isoformat() if j.created_at else None,
            "completed_at": j.completed_at.isoformat() if j.completed_at else None,
            "error_message": j.error_message,
        }
        for j in jobs
    ]
