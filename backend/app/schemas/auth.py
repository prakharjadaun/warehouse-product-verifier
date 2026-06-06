import uuid
from pydantic import BaseModel, EmailStr
from app.models.user import UserRole


class LoginOut(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserCreateIn(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    role: UserRole


class UserOut(BaseModel):
    id: uuid.UUID
    email: str
    full_name: str
    role: UserRole
    is_active: bool

    model_config = {"from_attributes": True}
