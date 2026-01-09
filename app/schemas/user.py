from pydantic import BaseModel, EmailStr, Field, field_validator

BCRYPT_MAX_BYTES = 72


class UserBase(BaseModel):
    email: EmailStr
    full_name: str | None = Field(default=None, max_length=255)


class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=BCRYPT_MAX_BYTES)
    is_superuser: bool = False

    @field_validator("password")
    @classmethod
    def validate_password_length(cls, value: str) -> str:
        if len(value.encode("utf-8")) > BCRYPT_MAX_BYTES:
            raise ValueError("Password must be at most 72 bytes for bcrypt")
        return value


class UserOut(UserBase):
    id: int
    is_active: bool
    is_superuser: bool
    tenant_id: int

    class Config:
        from_attributes = True
