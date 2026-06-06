from datetime import date, datetime, timezone

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.verification_log import VerificationLog
from app.schemas.verification_log import VerificationOut

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/verifications")
async def get_verification_report(
    start_date: date = Query(...),
    end_date: date = Query(...),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    start_dt = datetime(start_date.year, start_date.month, start_date.day, tzinfo=timezone.utc)
    end_dt = datetime(end_date.year, end_date.month, end_date.day, 23, 59, 59, tzinfo=timezone.utc)

    base_filter = (
        VerificationLog.verified_at >= start_dt,
        VerificationLog.verified_at <= end_dt,
    )

    count_result = await db.execute(
        select(func.count()).where(*base_filter).select_from(VerificationLog)
    )
    total = count_result.scalar_one()

    rows_result = await db.execute(
        select(VerificationLog)
        .where(*base_filter)
        .order_by(VerificationLog.verified_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    items = rows_result.scalars().all()

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": [VerificationOut.model_validate(item) for item in items],
    }
