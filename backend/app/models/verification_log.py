import enum
import uuid
from datetime import date, datetime

from sqlalchemy import BigInteger, Date, DateTime, Enum, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class AIMatchStatus(str, enum.Enum):
    match = "match"
    mismatch = "mismatch"
    skipped = "skipped"
    error = "error"


class VerificationLog(Base):
    __tablename__ = "verification_logs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    wid: Mapped[int] = mapped_column(BigInteger, nullable=False)
    operator_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    image_path: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    db_mfg_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    db_expiry_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    ai_mfg_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    ai_expiry_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    ai_match_status: Mapped[AIMatchStatus] = mapped_column(
        Enum(AIMatchStatus), default=AIMatchStatus.skipped
    )
    verified_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), index=True
    )
