from datetime import date, datetime

from sqlalchemy import BigInteger, Date, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Product(Base):
    __tablename__ = "products"

    wid: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    ean: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    manufacturing_date: Mapped[date] = mapped_column(Date, nullable=False)
    expiry_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
