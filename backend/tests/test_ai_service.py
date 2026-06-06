from datetime import date
from unittest.mock import MagicMock, patch

import pytest

from app.services.ai_service import compare_dates, extract_dates_from_image


def test_compare_dates_match():
    assert compare_dates(date(2024, 1, 1), date(2025, 1, 1), date(2024, 1, 1), date(2025, 1, 1)) == "match"


def test_compare_dates_mismatch_expiry():
    assert compare_dates(date(2024, 1, 1), date(2025, 6, 1), date(2024, 1, 1), date(2025, 1, 1)) == "mismatch"


def test_compare_dates_error_when_both_none():
    assert compare_dates(None, None, date(2024, 1, 1), date(2025, 1, 1)) == "error"


def test_compare_dates_partial_match_is_mismatch():
    assert compare_dates(date(2024, 1, 1), None, date(2024, 1, 1), date(2025, 1, 1)) == "mismatch"


@patch("app.services.ai_service.client")
def test_extract_dates_from_image_success(mock_client):
    mock_resp = MagicMock()
    mock_resp.choices[0].message.content = '{"manufacturing_date": "2024-01-15", "expiry_date": "2025-01-15"}'
    mock_client.chat.completions.create.return_value = mock_resp

    result = extract_dates_from_image(b"fake-image-bytes")

    assert result["manufacturing_date"] == date(2024, 1, 15)
    assert result["expiry_date"] == date(2025, 1, 15)


@patch("app.services.ai_service.client")
def test_extract_dates_handles_null_fields(mock_client):
    mock_resp = MagicMock()
    mock_resp.choices[0].message.content = '{"manufacturing_date": null, "expiry_date": "2025-06-01"}'
    mock_client.chat.completions.create.return_value = mock_resp

    result = extract_dates_from_image(b"fake-image-bytes")

    assert result["manufacturing_date"] is None
    assert result["expiry_date"] == date(2025, 6, 1)
