import csv

import psycopg2
import pytest

from app.config import settings
from app.services.ingest_service import run_bulk_ingest

SYNC_TEST_URL = settings.SYNC_DATABASE_URL.replace("/wms_dev", "/wms_test")


@pytest.fixture(scope="module", autouse=True)
def setup_products_table():
    conn = psycopg2.connect(SYNC_TEST_URL)
    conn.autocommit = True
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS products (
            wid BIGINT PRIMARY KEY,
            ean BIGINT NOT NULL,
            manufacturing_date DATE NOT NULL,
            expiry_date DATE NOT NULL,
            created_at TIMESTAMPTZ DEFAULT NOW()
        )
    """)
    cur.execute("TRUNCATE TABLE products")
    cur.close()
    conn.close()


def test_bulk_ingest_inserts_rows(tmp_path):
    csv_file = tmp_path / "test.csv"
    rows = [
        {"WID": "1001", "EAN": "9999", "Manufacturing_Date": "2024-01-01", "Expiry_Date": "2025-01-01"},
        {"WID": "1002", "EAN": "8888", "Manufacturing_Date": "2023-06-15", "Expiry_Date": "2024-06-15"},
    ]
    with open(csv_file, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["WID", "EAN", "Manufacturing_Date", "Expiry_Date"])
        writer.writeheader()
        writer.writerows(rows)

    progress_calls = []
    total = run_bulk_ingest(str(csv_file), SYNC_TEST_URL, lambda n: progress_calls.append(n))

    assert total == 2
    assert len(progress_calls) > 0

    conn = psycopg2.connect(SYNC_TEST_URL)
    cur = conn.cursor()
    cur.execute("SELECT wid, ean FROM products WHERE wid IN (1001, 1002) ORDER BY wid")
    result = cur.fetchall()
    cur.close()
    conn.close()

    assert result == [(1001, 9999), (1002, 8888)]


def test_bulk_ingest_upserts_on_conflict(tmp_path):
    csv_file = tmp_path / "upsert.csv"
    rows = [
        {"WID": "1001", "EAN": "7777", "Manufacturing_Date": "2024-03-01", "Expiry_Date": "2025-03-01"},
    ]
    with open(csv_file, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["WID", "EAN", "Manufacturing_Date", "Expiry_Date"])
        writer.writeheader()
        writer.writerows(rows)

    run_bulk_ingest(str(csv_file), SYNC_TEST_URL, lambda n: None)

    conn = psycopg2.connect(SYNC_TEST_URL)
    cur = conn.cursor()
    cur.execute("SELECT ean FROM products WHERE wid = 1001")
    row = cur.fetchone()
    cur.close()
    conn.close()

    assert row[0] == 7777  # updated, not duplicated
