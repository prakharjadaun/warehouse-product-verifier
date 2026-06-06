from datetime import date, datetime

from pydantic import BaseModel


class ProductOut(BaseModel):
    wid: int
    ean: int
    manufacturing_date: date
    expiry_date: date
    is_expired: bool
    created_at: datetime

    model_config = {"from_attributes": True}
