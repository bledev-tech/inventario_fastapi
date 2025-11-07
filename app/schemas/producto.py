from __future__ import annotations

from pydantic import BaseModel, Field


class ProductoBase(BaseModel):
    nombre: str = Field(..., min_length=1)
    sku: str | None = Field(default=None)
    activo: bool = True
    marca_id: int | None = Field(default=None, gt=0)
    categoria_id: int | None = Field(default=None, gt=0)


class ProductoCreate(ProductoBase):
    pass


class ProductoUpdate(BaseModel):
    nombre: str | None = Field(default=None, min_length=1)
    sku: str | None = None
    activo: bool | None = None
    marca_id: int | None = Field(default=None, gt=0)
    categoria_id: int | None = Field(default=None, gt=0)


class ProductoOut(ProductoBase):
    id: int

    class Config:
        from_attributes = True
