import io

import pytest


@pytest.mark.asyncio
async def test_upload_csv_returns_job_id(client):
    csv_content = b"WID,EAN,Manufacturing_Date,Expiry_Date\n123,456,2024-01-01,2025-01-01\n"
    files = {"file": ("test.csv", io.BytesIO(csv_content), "text/csv")}
    response = await client.post("/uploads/csv", files=files)
    assert response.status_code == 202
    data = response.json()
    assert "job_id" in data
    assert data["status"] == "pending"


@pytest.mark.asyncio
async def test_upload_rejects_non_csv(client):
    files = {"file": ("data.txt", io.BytesIO(b"hello"), "text/plain")}
    response = await client.post("/uploads/csv", files=files)
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_get_job_status(client):
    csv_content = b"WID,EAN,Manufacturing_Date,Expiry_Date\n999,111,2024-01-01,2025-01-01\n"
    files = {"file": ("test2.csv", io.BytesIO(csv_content), "text/csv")}
    upload_resp = await client.post("/uploads/csv", files=files)
    job_id = upload_resp.json()["job_id"]

    status_resp = await client.get(f"/uploads/{job_id}/status")
    assert status_resp.status_code == 200
    data = status_resp.json()
    assert data["job_id"] == job_id
    assert data["status"] in ["pending", "processing", "completed", "failed"]


@pytest.mark.asyncio
async def test_get_job_status_not_found(client):
    response = await client.get("/uploads/00000000-0000-0000-0000-000000000000/status")
    assert response.status_code == 404
