from __future__ import annotations

from pydantic import BaseModel, Field


class CategoriaBase(BaseModel):
    nombre: str = Field(..., min_length=1)
    activa: bool = True


class CategoriaCreate(CategoriaBase):
    pass


class CategoriaUpdate(BaseModel):
    nombre: str | None = Field(default=None, min_length=1)
    activa: bool | None = None


class CategoriaOut(CategoriaBase):
    id: int

    class Config:
        from_attributes = True
