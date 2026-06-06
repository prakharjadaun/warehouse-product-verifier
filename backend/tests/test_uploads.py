import io

import pytest


@pytest.mark.asyncio
async def test_upload_csv_returns_job_id(authed_client):
    csv_content = b"WID,EAN,Manufacturing_Date,Expiry_Date\n123,456,2024-01-01,2025-01-01\n"
    files = {"file": ("test.csv", io.BytesIO(csv_content), "text/csv")}
    response = await authed_client.post("/uploads/csv", files=files)
    assert response.status_code == 202
    data = response.json()
    assert "job_id" in data
    assert data["status"] == "pending"


@pytest.mark.asyncio
async def test_upload_rejects_non_csv(authed_client):
    files = {"file": ("data.txt", io.BytesIO(b"hello"), "text/plain")}
    response = await authed_client.post("/uploads/csv", files=files)
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_upload_requires_auth(client):
    csv_content = b"WID,EAN,Manufacturing_Date,Expiry_Date\n1,2,2024-01-01,2025-01-01\n"
    files = {"file": ("test.csv", io.BytesIO(csv_content), "text/csv")}
    response = await client.post("/uploads/csv", files=files)
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_job_status(authed_client):
    csv_content = b"WID,EAN,Manufacturing_Date,Expiry_Date\n999,111,2024-01-01,2025-01-01\n"
    files = {"file": ("test2.csv", io.BytesIO(csv_content), "text/csv")}
    upload_resp = await authed_client.post("/uploads/csv", files=files)
    job_id = upload_resp.json()["job_id"]

    status_resp = await authed_client.get(f"/uploads/{job_id}/status")
    assert status_resp.status_code == 200
    data = status_resp.json()
    assert data["job_id"] == job_id
    assert data["status"] in ["pending", "processing", "completed", "failed"]


@pytest.mark.asyncio
async def test_get_job_status_not_found(authed_client):
    response = await authed_client.get("/uploads/00000000-0000-0000-0000-000000000000/status")
    assert response.status_code == 404
