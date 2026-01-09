from __future__ import annotations

from datetime import date, datetime, timedelta

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app import crud
from app.api.deps import get_current_user, get_db
from decimal import Decimal

from app.models.user import User
from app.schemas.stock import (
    InventarioLocacion,
    InventarioTotalDia,
    StockItem,
    WeeklyInventoryFilters,
    WeeklyInventoryItem,
    WeeklyInventoryMeta,
    WeeklyInventoryResponse,
    WeeklyInventoryTotals,
)

router = APIRouter()


@router.get("/", response_model=list[StockItem])
def read_stock(
    *,
    producto_id: int | None = Query(default=None, gt=0),
    locacion_id: int | None = Query(default=None, gt=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[StockItem]:
    if producto_id is None and locacion_id is None:
        return crud.stock.get_all(db, tenant_id=current_user.tenant_id)
    return crud.stock.get_filtered(
        db,
        tenant_id=current_user.tenant_id,
        producto_id=producto_id,
        locacion_id=locacion_id,
    )


@router.get("/locaciones", response_model=list[InventarioLocacion])
def read_inventario_locaciones(
    *,
    include_zero: bool = Query(default=False, description="Incluir productos con stock cero"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[InventarioLocacion]:
    return crud.stock.get_grouped_by_locacion(
        db,
        tenant_id=current_user.tenant_id,
        include_zero=include_zero,
    )


@router.get("/total-diario", response_model=InventarioTotalDia)
def read_inventario_total_por_dia(
    *,
    fecha: date | None = Query(
        default=None,
        description="Fecha (UTC) para calcular el inventario acumulado. Si se omite se usa el dia actual.",
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> InventarioTotalDia:
    target_date = fecha or date.today()
    rows = crud.stock.get_total_por_dia(db, tenant_id=current_user.tenant_id, fecha=target_date)
    total_stock = sum((item["total_stock"] for item in rows), Decimal("0"))
    return InventarioTotalDia(
        fecha=target_date,
        total_stock=total_stock,
        total_productos=len(rows),
        items=rows,
    )


@router.get("/weekly", response_model=WeeklyInventoryResponse)
def read_inventario_semanal(
    *,
    start_date: date | None = Query(
        default=None,
        description="Fecha de inicio de la semana (lunes). Si se omite se usa la semana actual.",
    ),
    weeks: int = Query(
        default=1,
        ge=1,
        le=4,
        description="Cantidad de semanas consecutivas a incluir en el cálculo.",
    ),
    categoria_ids: list[int] | None = Query(default=None, alias="categoria_id"),
    producto_ids: list[int] | None = Query(default=None, alias="producto_id"),
    include_zero: bool = Query(default=False, description="Incluir productos sin movimientos o stock."),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> WeeklyInventoryResponse:
    reference = start_date or date.today()
    normalized_start = reference - timedelta(days=reference.weekday())
    total_days = (weeks * 7) - 1
    normalized_end = normalized_start + timedelta(days=total_days)

    dataset = crud.stock.get_weekly_inventory(
        db,
        tenant_id=current_user.tenant_id,
        start_date=normalized_start,
        end_date=normalized_end,
        categoria_ids=categoria_ids,
        producto_ids=producto_ids,
        include_zero=include_zero,
    )

    filters = WeeklyInventoryFilters(
        categoria_ids=categoria_ids or [],
        producto_ids=producto_ids or [],
        include_zero=include_zero,
    )

    totals = WeeklyInventoryTotals(**dataset["totals"])

    meta = WeeklyInventoryMeta(
        generated_at=datetime.utcnow(),
        week_start=normalized_start,
        week_end=normalized_end,
        filters=filters,
        totals=totals,
    )

    items = [WeeklyInventoryItem(**item) for item in dataset["items"]]

    return WeeklyInventoryResponse(meta=meta, items=items)
