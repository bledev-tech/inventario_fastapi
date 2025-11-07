from __future__ import annotations

from pydantic import BaseModel, Field


class PersonaBase(BaseModel):
    nombre: str = Field(..., min_length=1)
    activa: bool = True


class PersonaCreate(PersonaBase):
    pass


class PersonaUpdate(BaseModel):
    nombre: str | None = Field(default=None, min_length=1)
    activa: bool | None = None


class PersonaOut(PersonaBase):
    id: int

    class Config:
        from_attributes = True
