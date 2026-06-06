import base64
import json
import logging
from datetime import date

from openai import AzureOpenAI

from app.config import settings

logger = logging.getLogger(__name__)

client = AzureOpenAI(
    azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
    api_key=settings.AZURE_OPENAI_API_KEY,
    api_version=settings.AZURE_LLM_API_VERSION,
)

SYSTEM_PROMPT = (
    "You are a warehouse quality control assistant. "
    "Your only task is to extract manufacturing and expiry dates from product label images."
)

USER_PROMPT = (
    "Look at this product label image. "
    "Extract the manufacturing date and expiry date. "
    'Return ONLY valid JSON in this exact format: {"manufacturing_date": "YYYY-MM-DD", "expiry_date": "YYYY-MM-DD"}. '
    "If a date is not visible or cannot be determined, use null for that field. "
    "No explanations — only the JSON object."
)


def extract_dates_from_image(image_bytes: bytes) -> dict:
    b64 = base64.b64encode(image_bytes).decode("utf-8")

    response = client.chat.completions.create(
        model=settings.AZURE_LLM_DEPLOYMENT,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": USER_PROMPT},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}},
                ],
            },
        ],
        max_tokens=150,
        temperature=0,
    )

    raw = response.choices[0].message.content
    logger.info("GPT-4o response: %s", raw)
    parsed = json.loads(raw)

    return {
        "manufacturing_date": _parse_date(parsed.get("manufacturing_date")),
        "expiry_date": _parse_date(parsed.get("expiry_date")),
    }


def _parse_date(value: str | None) -> date | None:
    if not value:
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        return None


def compare_dates(
    ai_mfg: date | None,
    ai_exp: date | None,
    db_mfg: date | None,
    db_exp: date | None,
) -> str:
    if ai_mfg is None and ai_exp is None:
        return "error"
    if ai_mfg == db_mfg and ai_exp == db_exp:
        return "match"
    return "mismatch"
