from __future__ import annotations

from pydantic import BaseModel, Field


class MarcaBase(BaseModel):
    nombre: str = Field(..., min_length=1)
    activa: bool = True


class MarcaCreate(MarcaBase):
    pass


class MarcaUpdate(BaseModel):
    nombre: str | None = Field(default=None, min_length=1)
    activa: bool | None = None


class MarcaOut(MarcaBase):
    id: int

    class Config:
        from_attributes = True
