from __future__ import annotations

from decimal import Decimal

from pydantic import BaseModel


class StockItem(BaseModel):
    producto_id: int
    locacion_id: int
    stock: Decimal

    class Config:
        from_attributes = True


class InventarioProducto(BaseModel):
    producto_id: int
    producto_nombre: str
    sku: str | None
    activo: bool
    stock: Decimal


class InventarioLocacion(BaseModel):
    locacion_id: int
    locacion_nombre: str
    activa: bool
    total_stock: Decimal
    items: list[InventarioProducto]
