from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app import crud
from app.api.deps import get_db
from app.schemas.stock import InventarioLocacion, StockItem

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
