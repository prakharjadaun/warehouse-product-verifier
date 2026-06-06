import pytest
from sqlalchemy import insert

from app.models.verification_log import AIMatchStatus, VerificationLog


@pytest.mark.asyncio
async def test_reports_returns_logs_in_range(client, db):
    await db.execute(
        insert(VerificationLog).values(
            wid=77001, operator_id="op1", ai_match_status=AIMatchStatus.skipped
        )
    )
    await db.commit()

    response = await client.get("/reports/verifications?start_date=2020-01-01&end_date=2099-12-31")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert data["total"] >= 1


@pytest.mark.asyncio
async def test_reports_empty_for_past_range(client):
    response = await client.get("/reports/verifications?start_date=2000-01-01&end_date=2000-01-02")
    assert response.status_code == 200
    assert response.json()["total"] == 0


@pytest.mark.asyncio
async def test_reports_pagination(client):
    response = await client.get(
        "/reports/verifications?start_date=2020-01-01&end_date=2099-12-31&page=1&page_size=2"
    )
    assert response.status_code == 200
    data = response.json()
    assert data["page"] == 1
    assert data["page_size"] == 2
    assert len(data["items"]) <= 2


@pytest.mark.asyncio
async def test_reports_missing_dates(client):
    response = await client.get("/reports/verifications")
    assert response.status_code == 422
