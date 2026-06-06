from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.product import Product
from app.models.verification_log import AIMatchStatus, VerificationLog
from app.schemas.product import ProductOut
from app.schemas.verification_log import VerificationIn, VerificationOut

router = APIRouter(tags=["validation"])


@router.get("/products/{wid}", response_model=ProductOut)
async def get_product(wid: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Product).where(Product.wid == wid))
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail=f"WID {wid} not found")

    return ProductOut(
        wid=product.wid,
        ean=product.ean,
        manufacturing_date=product.manufacturing_date,
        expiry_date=product.expiry_date,
        is_expired=product.expiry_date < date.today(),
        created_at=product.created_at,
    )


@router.post("/verifications", response_model=VerificationOut, status_code=201)
async def log_verification(body: VerificationIn, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Product).where(Product.wid == body.wid))
    product = result.scalar_one_or_none()

    log = VerificationLog(
        wid=body.wid,
        operator_id=body.operator_id,
        db_mfg_date=product.manufacturing_date if product else None,
        db_expiry_date=product.expiry_date if product else None,
        ai_match_status=AIMatchStatus.skipped,
    )
    db.add(log)
    await db.flush()
    await db.refresh(log)
    return log
