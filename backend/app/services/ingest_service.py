import csv
import logging
from io import StringIO
from typing import Callable

import psycopg2

logger = logging.getLogger(__name__)

CHUNK_SIZE = 100_000       # 100K rows per COPY batch — 10x fewer staging round trips
PROGRESS_EVERY = 5        # update DB progress every N chunks (every 500K rows)


def run_bulk_ingest(
    file_path: str,
    sync_db_url: str,
    update_progress: Callable[[int], None],
) -> int:
    """
    Streams CSV into PostgreSQL using COPY for maximum throughput.
    Uses a temp staging table + UPSERT to handle WID conflicts gracefully.
    Returns total rows processed.
    """
    conn = psycopg2.connect(sync_db_url)
    conn.autocommit = False
    cur = conn.cursor()

    # Tune PostgreSQL session for bulk load performance
    cur.execute("SET synchronous_commit = OFF")
    cur.execute("SET work_mem = '256MB'")
    conn.commit()

    try:
        cur.execute("""
            CREATE TEMP TABLE products_staging (
                wid BIGINT,
                ean BIGINT,
                manufacturing_date DATE,
                expiry_date DATE
            )
        """)
        conn.commit()

        total_processed = 0
        chunk: list[tuple] = []
        chunk_count = 0

        with open(file_path, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                chunk.append((
                    int(row["WID"]),
                    int(row["EAN"]),
                    row["Manufacturing_Date"],
                    row["Expiry_Date"],
                ))
                if len(chunk) >= CHUNK_SIZE:
                    _copy_and_upsert(cur, chunk)
                    conn.commit()
                    total_processed += len(chunk)
                    chunk_count += 1
                    chunk = []
                    # Only write progress to DB every PROGRESS_EVERY chunks
                    if chunk_count % PROGRESS_EVERY == 0:
                        update_progress(total_processed)

        if chunk:
            _copy_and_upsert(cur, chunk)
            conn.commit()
            total_processed += len(chunk)

        # Always report final count
        update_progress(total_processed)
        return total_processed

    except Exception:
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()


def _copy_and_upsert(cur, chunk: list[tuple]) -> None:
    buffer = StringIO()
    writer = csv.writer(buffer)
    writer.writerows(chunk)
    buffer.seek(0)

    # copy_expert is faster than copy_from — uses PostgreSQL's native COPY protocol directly
    cur.copy_expert(
        "COPY products_staging (wid, ean, manufacturing_date, expiry_date) FROM STDIN WITH (FORMAT csv)",
        buffer,
    )

    cur.execute("""
        INSERT INTO products (wid, ean, manufacturing_date, expiry_date)
        SELECT wid, ean, manufacturing_date, expiry_date
        FROM products_staging
        ON CONFLICT (wid) DO UPDATE SET
            ean = EXCLUDED.ean,
            manufacturing_date = EXCLUDED.manufacturing_date,
            expiry_date = EXCLUDED.expiry_date;

        TRUNCATE TABLE products_staging;
    """)
