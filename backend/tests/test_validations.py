from datetime import date

import pytest
from sqlalchemy.dialects.postgresql import insert

from app.models.product import Product
from app.models.verification_log import VerificationLog


@pytest.mark.asyncio
async def test_get_product_found(client, db):
    await db.execute(
        insert(Product).values(
            wid=55001, ean=12345,
            manufacturing_date=date(2024, 1, 1),
            expiry_date=date(2099, 1, 1),
        ).on_conflict_do_nothing()
    )
    await db.commit()

    response = await client.get("/products/55001")
    assert response.status_code == 200
    data = response.json()
    assert data["wid"] == 55001
    assert data["ean"] == 12345
    assert data["is_expired"] is False


@pytest.mark.asyncio
async def test_get_product_not_found(client):
    response = await client.get("/products/99999999")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_expired_product_flag(client, db):
    await db.execute(
        insert(Product).values(
            wid=55003, ean=77777,
            manufacturing_date=date(2020, 1, 1),
            expiry_date=date(2021, 1, 1),
        ).on_conflict_do_nothing()
    )
    await db.commit()

    response = await client.get("/products/55003")
    assert response.status_code == 200
    assert response.json()["is_expired"] is True


@pytest.mark.asyncio
async def test_post_verification_logs_event(client, db):
    await db.execute(
        insert(Product).values(
            wid=55002, ean=99999,
            manufacturing_date=date(2023, 1, 1),
            expiry_date=date(2099, 6, 1),
        ).on_conflict_do_nothing()
    )
    await db.commit()

    response = await client.post("/verifications", json={"wid": 55002, "operator_id": "op1"})
    assert response.status_code == 201
    data = response.json()
    assert data["wid"] == 55002
    assert data["ai_match_status"] == "skipped"


@pytest.mark.asyncio
async def test_post_verification_unknown_wid(client):
    response = await client.post("/verifications", json={"wid": 88888, "operator_id": "op2"})
    assert response.status_code == 201
    data = response.json()
    assert data["wid"] == 88888
    assert data["db_mfg_date"] is None
