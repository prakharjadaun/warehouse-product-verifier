import uuid
from datetime import date, datetime

from pydantic import BaseModel

from app.models.verification_log import AIMatchStatus


class VerificationIn(BaseModel):
    wid: int
    operator_id: str | None = None


class VerificationOut(BaseModel):
    id: uuid.UUID
    wid: int
    operator_id: str | None
    db_mfg_date: date | None
    db_expiry_date: date | None
    ai_mfg_date: date | None
    ai_expiry_date: date | None
    ai_match_status: AIMatchStatus
    verified_at: datetime

    model_config = {"from_attributes": True}
