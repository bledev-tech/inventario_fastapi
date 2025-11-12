from __future__ import annotations

from datetime import date, datetime
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
    uom_id: int
    uom_nombre: str
    uom_abreviatura: str
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
    uom_id: int
    uom_nombre: str
    uom_abreviatura: str
    total_stock: Decimal


class InventarioTotalDia(BaseModel):
    fecha: date
    total_stock: Decimal
    total_productos: int
    items: list[InventarioTotalProducto]


class WeeklyInventoryFilters(BaseModel):
    categoria_ids: list[int]
    producto_ids: list[int]
    include_zero: bool


class WeeklyInventoryDay(BaseModel):
    date: date
    ingresos: Decimal
    egresos: Decimal
    neto: Decimal
    stock_end: Decimal


class WeeklyInventoryItem(BaseModel):
    producto_id: int
    producto_nombre: str
    sku: str | None
    categoria_id: int | None
    categoria_nombre: str | None
    uom_id: int
    uom_nombre: str
    uom_abreviatura: str
    stock_inicial: Decimal
    stock_final: Decimal
    total_ingresos: Decimal
    total_egresos: Decimal
    variation: Decimal
    daily: list[WeeklyInventoryDay]


class WeeklyInventoryTotals(BaseModel):
    productos: int
    stock_inicial: Decimal
    stock_final: Decimal
    total_ingresos: Decimal
    total_egresos: Decimal


class WeeklyInventoryMeta(BaseModel):
    generated_at: datetime
    week_start: date
    week_end: date
    filters: WeeklyInventoryFilters
    totals: WeeklyInventoryTotals


class WeeklyInventoryResponse(BaseModel):
    meta: WeeklyInventoryMeta
    items: list[WeeklyInventoryItem]
