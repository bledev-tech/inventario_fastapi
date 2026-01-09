from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    email: EmailStr
    full_name: str | None = Field(default=None, max_length=255)


class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=128)
    is_superuser: bool = False


class UserOut(UserBase):
    id: int
    is_active: bool
    is_superuser: bool
    tenant_id: int

    class Config:
        from_attributes = True

