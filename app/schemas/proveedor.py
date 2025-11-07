from __future__ import annotations

from pydantic import BaseModel, Field


class ProveedorBase(BaseModel):
    nombre: str = Field(..., min_length=1)
    activa: bool = True


class ProveedorCreate(ProveedorBase):
    pass


class ProveedorUpdate(BaseModel):
    nombre: str | None = Field(default=None, min_length=1)
    activa: bool | None = None


class ProveedorOut(ProveedorBase):
    id: int

    class Config:
        from_attributes = True
