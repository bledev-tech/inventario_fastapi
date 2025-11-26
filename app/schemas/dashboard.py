from __future__ import annotations

from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class MovementTypePercentage(BaseModel):
    count: int = Field(..., ge=0)
    percentage: float = Field(..., ge=0)


class DashboardSummaryResponse(BaseModel):
    total_movements_last_7d: int = Field(..., ge=0)
    distinct_products_moved_last_7d: int = Field(..., ge=0)
    usage_vs_ingress_ratio_last_7d: Dict[str, MovementTypePercentage]
    adjustments_last_30d: int = Field(..., ge=0)


class RecentMovementItem(BaseModel):
    id: int
    fecha: datetime
    tipo: str
    producto_nombre: str
    from_locacion_nombre: Optional[str] = None
    to_locacion_nombre: Optional[str] = None
    persona_nombre: Optional[str] = None
    proveedor_nombre: Optional[str] = None
    cantidad: float
    nota: Optional[str] = None


class RecentMovementsResponse(BaseModel):
    items: List[RecentMovementItem]
    limit: int
    offset: int


class StockByLocationItem(BaseModel):
    locacion_id: int
    locacion_nombre: str
    stock_total: float


class StockByLocationResponse(BaseModel):
    items: List[StockByLocationItem]


class TopUsedProductItem(BaseModel):
    producto_id: int
    producto_nombre: str
    total_usado: float


class TopUsedProductsResponse(BaseModel):
    items: List[TopUsedProductItem]
    days: int
    limit: int


class TopCategoryItem(BaseModel):
    categoria_id: int
    categoria_nombre: str
    total_movimiento: float
    movimientos_count: int


class TopCategoriesResponse(BaseModel):
    items: List[TopCategoryItem]
    days: int
    limit: int


class AdjustmentProductItem(BaseModel):
    producto_id: int
    producto_nombre: str
    ajustes_count: int


class AdjustmentLocationItem(BaseModel):
    locacion_id: int
    locacion_nombre: str
    ajustes_count: int


class AdjustmentsMonitorResponse(BaseModel):
    total_adjustments: int
    top_products: List[AdjustmentProductItem]
    top_locations: List[AdjustmentLocationItem]
    days: int
