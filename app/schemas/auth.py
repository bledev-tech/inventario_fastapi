from pydantic import BaseModel, EmailStr, Field, field_validator

BCRYPT_MAX_BYTES = 72


class RegisterRequest(BaseModel):
    tenant_name: str = Field(..., min_length=2, max_length=200)
    tenant_slug: str | None = Field(default=None, min_length=2, max_length=200)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=BCRYPT_MAX_BYTES)
    full_name: str | None = Field(default=None, max_length=255)

    @field_validator("password")
    @classmethod
    def validate_password_length(cls, value: str) -> str:
        if len(value.encode("utf-8")) > BCRYPT_MAX_BYTES:
            raise ValueError("Password must be at most 72 bytes for bcrypt")
        return value
