import uuid as uuid_mod
from datetime import date
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.product import Product
from app.models.verification_log import AIMatchStatus, VerificationLog
from app.schemas.product import ProductOut
from app.schemas.verification_log import VerificationIn, VerificationOut
from app.services.ai_service import compare_dates, extract_dates_from_image

router = APIRouter(tags=["validation"])


@router.get("/products")
async def list_products(
    search: str | None = Query(None, description="Search by WID or EAN (exact or partial)"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    today = date.today()
    conditions = []
    if search and search.strip():
        try:
            numeric = int(search.strip())
            conditions.append(or_(Product.wid == numeric, Product.ean == numeric))
        except ValueError:
            pass  # non-numeric search returns all

    base_query = select(Product)
    count_query = select(func.count()).select_from(Product)
    if conditions:
        base_query = base_query.where(*conditions)
        count_query = count_query.where(*conditions)

    total = (await db.execute(count_query)).scalar_one()
    rows = (await db.execute(
        base_query.order_by(Product.wid).offset((page - 1) * page_size).limit(page_size)
    )).scalars().all()

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": [
            {
                "wid": p.wid,
                "ean": p.ean,
                "manufacturing_date": str(p.manufacturing_date),
                "expiry_date": str(p.expiry_date),
                "is_expired": p.expiry_date < today,
            }
            for p in rows
        ],
    }

IMAGES_DIR = Path("uploads/images")
IMAGES_DIR.mkdir(parents=True, exist_ok=True)


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


@router.post("/verifications/ai-extract", response_model=VerificationOut, status_code=201)
async def ai_extract_verification(
    wid: int = Form(...),
    operator_id: str | None = Form(None),
    image: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    image_bytes = await image.read()
    filename = f"{wid}_{uuid_mod.uuid4().hex}.jpg"
    image_path = IMAGES_DIR / filename
    with open(image_path, "wb") as f:
        f.write(image_bytes)

    result = await db.execute(select(Product).where(Product.wid == wid))
    product = result.scalar_one_or_none()

    try:
        extracted = extract_dates_from_image(image_bytes)
        ai_mfg = extracted["manufacturing_date"]
        ai_exp = extracted["expiry_date"]
        status_str = compare_dates(
            ai_mfg, ai_exp,
            product.manufacturing_date if product else None,
            product.expiry_date if product else None,
        )
        match_status = AIMatchStatus(status_str)
    except Exception:
        ai_mfg, ai_exp = None, None
        match_status = AIMatchStatus.error

    log = VerificationLog(
        wid=wid,
        operator_id=operator_id,
        image_path=str(image_path),
        db_mfg_date=product.manufacturing_date if product else None,
        db_expiry_date=product.expiry_date if product else None,
        ai_mfg_date=ai_mfg,
        ai_expiry_date=ai_exp,
        ai_match_status=match_status,
    )
    db.add(log)
    await db.flush()
    await db.refresh(log)
    return log
