from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app import crud
from app.api.deps import get_db
from decimal import Decimal

from app.schemas.stock import InventarioLocacion, InventarioTotalDia, StockItem

router = APIRouter()


@router.get("/", response_model=list[StockItem])
def read_stock(
    *,
    producto_id: int | None = Query(default=None, gt=0),
    locacion_id: int | None = Query(default=None, gt=0),
    db: Session = Depends(get_db),
) -> list[StockItem]:
    if producto_id is None and locacion_id is None:
        return crud.stock.get_all(db)
    return crud.stock.get_filtered(db, producto_id=producto_id, locacion_id=locacion_id)


@router.get("/locaciones", response_model=list[InventarioLocacion])
def read_inventario_locaciones(
    *,
    include_zero: bool = Query(default=False, description="Incluir productos con stock cero"),
    db: Session = Depends(get_db),
) -> list[InventarioLocacion]:
    return crud.stock.get_grouped_by_locacion(db, include_zero=include_zero)


@router.get("/total-diario", response_model=InventarioTotalDia)
def read_inventario_total_por_dia(
    *,
    fecha: date | None = Query(
        default=None,
        description="Fecha (UTC) para calcular el inventario acumulado. Si se omite se usa el dia actual.",
    ),
    db: Session = Depends(get_db),
) -> InventarioTotalDia:
    target_date = fecha or date.today()
    rows = crud.stock.get_total_por_dia(db, fecha=target_date)
    total_stock = sum((item["total_stock"] for item in rows), Decimal("0"))
    return InventarioTotalDia(
        fecha=target_date,
        total_stock=total_stock,
        total_productos=len(rows),
        items=rows,
    )
