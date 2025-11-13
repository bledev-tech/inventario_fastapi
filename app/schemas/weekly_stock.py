"""
Schemas para vistas de stock semanal
"""
from typing import Dict
from pydantic import BaseModel, Field


class DailyMovements(BaseModel):
    """Movimientos diarios de la semana"""
    monday: float | None = 0
    tuesday: float | None = 0
    wednesday: float | None = 0
    thursday: float | None = 0
    friday: float | None = 0
    saturday: float | None = 0
    sunday: float | None = 0


class WeeklyProduct(BaseModel):
    """Producto con datos semanales"""
    id: int
    name: str
    brand: str | None = None
    supplier: str | None = None
    initial_stock: float = Field(..., description="Stock al inicio de la semana")
    daily_movements: DailyMovements
    final_stock_realtime: float = Field(..., description="Stock actual en tiempo real")


class WeeklyCategory(BaseModel):
    """Categoría con sus productos y datos semanales"""
    category_id: int
    category_name: str
    products: list[WeeklyProduct]


class WeeklyStockResponse(BaseModel):
    """Respuesta completa de stock semanal"""
    week_start: str = Field(..., description="Fecha de inicio de semana (lunes) YYYY-MM-DD")
    categories: list[WeeklyCategory]
