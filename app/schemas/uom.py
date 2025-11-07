from __future__ import annotations

from pydantic import BaseModel, Field


class UOMBase(BaseModel):
    nombre: str = Field(..., min_length=1)
    abreviatura: str = Field(..., min_length=1, max_length=10)
    descripcion: str | None = None
    activa: bool = True


class UOMCreate(UOMBase):
    pass


class UOMUpdate(BaseModel):
    nombre: str | None = Field(default=None, min_length=1)
    abreviatura: str | None = Field(default=None, min_length=1, max_length=10)
    descripcion: str | None = Field(default=None)
    activa: bool | None = None


class UOMOut(UOMBase):
    id: int

    class Config:
        from_attributes = True
