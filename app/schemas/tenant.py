from pydantic import BaseModel, Field


class TenantBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=200)
    slug: str = Field(..., min_length=2, max_length=200)


class TenantCreate(TenantBase):
    pass


class TenantOut(TenantBase):
    id: int
    is_active: bool

    class Config:
        from_attributes = True

