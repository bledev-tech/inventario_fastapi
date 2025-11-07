from __future__ import annotations

from datetime import date
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


class InventarioTotalProducto(BaseModel):
    producto_id: int
    producto_nombre: str
    sku: str | None
    total_stock: Decimal


class InventarioTotalDia(BaseModel):
    fecha: date
    total_stock: Decimal
    total_productos: int
    items: list[InventarioTotalProducto]
