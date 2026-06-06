import uuid
from datetime import datetime

from pydantic import BaseModel

from app.models.upload_job import JobStatus


class JobStatusOut(BaseModel):
    job_id: uuid.UUID
    status: JobStatus
    total_rows: int | None
    processed_rows: int
    progress_percent: float
    error_message: str | None
