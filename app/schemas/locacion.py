from __future__ import annotations

from pydantic import BaseModel, Field


class LocacionBase(BaseModel):
    nombre: str = Field(..., min_length=1)
    activa: bool = True


class LocacionCreate(LocacionBase):
    pass


class LocacionUpdate(BaseModel):
    nombre: str | None = Field(default=None, min_length=1)
    activa: bool | None = None


class LocacionOut(LocacionBase):
    id: int

    class Config:
        from_attributes = True
