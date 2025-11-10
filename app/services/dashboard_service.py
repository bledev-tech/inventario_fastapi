from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone
from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy import func, or_, select, union_all
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, aliased

from app.models import (
    Locacion,
    Movimiento,
    Persona,
    Producto,
    Proveedor,
    TipoMovimiento,
    VistaStockActual,
)
from app.schemas.dashboard import (
    AdjustmentLocationItem,
    AdjustmentProductItem,
    AdjustmentsMonitorResponse,
    DashboardSummaryResponse,
    MovementTypePercentage,
    RecentMovementItem,
    RecentMovementsResponse,
    StockByLocationItem,
    StockByLocationResponse,
    TopUsedProductItem,
    TopUsedProductsResponse,
)

logger = logging.getLogger(__name__)


def _raise_db_error(exc: SQLAlchemyError) -> None:
    logger.exception("Error fetching dashboard data")
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Error fetching dashboard data",
    ) from exc


def _decimal_to_float(value: Decimal | None) -> float:
    return float(value) if value is not None else 0.0


def get_dashboard_summary(db: Session) -> DashboardSummaryResponse:
    now = datetime.now(timezone.utc)
    seven_days_ago = now - timedelta(days=7)
    thirty_days_ago = now - timedelta(days=30)

    try:
        totals_row = db.execute(
            select(
                func.count(Movimiento.id).label("total_movements"),
                func.count(func.distinct(Movimiento.producto_id)).label("distinct_products"),
            ).where(Movimiento.fecha >= seven_days_ago)
        ).one()

        total_movements = int(totals_row.total_movements or 0)
        distinct_products = int(totals_row.distinct_products or 0)

        ratio_rows = db.execute(
            select(
                Movimiento.tipo,
                func.count(Movimiento.id).label("count"),
            )
            .where(
                Movimiento.fecha >= seven_days_ago,
                Movimiento.tipo.in_([TipoMovimiento.ingreso, TipoMovimiento.uso]),
            )
            .group_by(Movimiento.tipo)
        ).all()

        ratio_counts: dict[TipoMovimiento, int] = {
            TipoMovimiento.ingreso: 0,
            TipoMovimiento.uso: 0,
        }
        for movement_type, count in ratio_rows:
            if movement_type in ratio_counts:
                ratio_counts[movement_type] = int(count or 0)

        ratio_total = sum(ratio_counts.values())
        ingreso_percentage = (
            ratio_counts[TipoMovimiento.ingreso] / ratio_total * 100 if ratio_total else 0.0
        )
        uso_percentage = (
            ratio_counts[TipoMovimiento.uso] / ratio_total * 100 if ratio_total else 0.0
        )

        adjustments_last_30d = int(
            db.execute(
                select(func.count(Movimiento.id)).where(
                    Movimiento.fecha >= thirty_days_ago,
                    Movimiento.tipo == TipoMovimiento.ajuste,
                )
            ).scalar_one()
            or 0
        )
    except SQLAlchemyError as exc:
        _raise_db_error(exc)

    return DashboardSummaryResponse(
        total_movements_last_7d=total_movements,
        distinct_products_moved_last_7d=distinct_products,
        usage_vs_ingress_ratio_last_7d={
            "ingreso": MovementTypePercentage(
                count=ratio_counts[TipoMovimiento.ingreso],
                percentage=ingreso_percentage,
            ),
            "uso": MovementTypePercentage(
                count=ratio_counts[TipoMovimiento.uso],
                percentage=uso_percentage,
            ),
        },
        adjustments_last_30d=adjustments_last_30d,
    )


def get_recent_movements(
    db: Session,
    *,
    limit: int,
    offset: int,
    tipo: TipoMovimiento | None = None,
    locacion_id: int | None = None,
    producto_id: int | None = None,
) -> RecentMovementsResponse:
    from_loc = aliased(Locacion, name="from_locacion")
    to_loc = aliased(Locacion, name="to_locacion")

    stmt = (
        select(
            Movimiento.id,
            Movimiento.fecha,
            Movimiento.tipo,
            Producto.nombre.label("producto_nombre"),
            from_loc.nombre.label("from_locacion_nombre"),
            to_loc.nombre.label("to_locacion_nombre"),
            Persona.nombre.label("persona_nombre"),
            Proveedor.nombre.label("proveedor_nombre"),
            Movimiento.cantidad,
            Movimiento.nota,
        )
        .join(Producto, Movimiento.producto_id == Producto.id)
        .outerjoin(from_loc, Movimiento.from_locacion_id == from_loc.id)
        .outerjoin(to_loc, Movimiento.to_locacion_id == to_loc.id)
        .outerjoin(Persona, Movimiento.persona_id == Persona.id)
        .outerjoin(Proveedor, Movimiento.proveedor_id == Proveedor.id)
    )

    filters = []
    if tipo is not None:
        filters.append(Movimiento.tipo == tipo)
    if producto_id is not None:
        filters.append(Movimiento.producto_id == producto_id)
    if locacion_id is not None:
        filters.append(
            or_(Movimiento.from_locacion_id == locacion_id, Movimiento.to_locacion_id == locacion_id)
        )
    if filters:
        stmt = stmt.where(*filters)

    stmt = stmt.order_by(Movimiento.fecha.desc(), Movimiento.id.desc()).limit(limit).offset(offset)

    try:
        rows = db.execute(stmt).all()
    except SQLAlchemyError as exc:
        _raise_db_error(exc)

    items = [
        RecentMovementItem(
            id=row.id,
            fecha=row.fecha,
            tipo=row.tipo.value if isinstance(row.tipo, TipoMovimiento) else str(row.tipo),
            producto_nombre=row.producto_nombre,
            from_locacion_nombre=row.from_locacion_nombre,
            to_locacion_nombre=row.to_locacion_nombre,
            persona_nombre=row.persona_nombre,
            proveedor_nombre=row.proveedor_nombre,
            cantidad=_decimal_to_float(row.cantidad),
            nota=row.nota,
        )
        for row in rows
    ]
    return RecentMovementsResponse(items=items, limit=limit, offset=offset)


def get_stock_by_location(db: Session, *, exclude_zero_stock: bool = True) -> StockByLocationResponse:
    stmt = (
        select(
            VistaStockActual.locacion_id,
            Locacion.nombre.label("locacion_nombre"),
            func.sum(VistaStockActual.stock).label("stock_total"),
        )
        .join(Locacion, VistaStockActual.locacion_id == Locacion.id)
        .group_by(VistaStockActual.locacion_id, Locacion.nombre)
        .order_by(Locacion.nombre.asc())
    )

    try:
        rows = db.execute(stmt).all()
    except SQLAlchemyError as exc:
        _raise_db_error(exc)

    items: list[StockByLocationItem] = []
    for row in rows:
        stock_total = _decimal_to_float(row.stock_total)
        if exclude_zero_stock and stock_total == 0:
            continue
        items.append(
            StockByLocationItem(
                locacion_id=row.locacion_id,
                locacion_nombre=row.locacion_nombre,
                stock_total=stock_total,
            )
        )

    return StockByLocationResponse(items=items)


def get_top_used_products(db: Session, *, days: int, limit: int) -> TopUsedProductsResponse:
    since = datetime.now(timezone.utc) - timedelta(days=days)

    stmt = (
        select(
            Movimiento.producto_id,
            Producto.nombre.label("producto_nombre"),
            func.sum(Movimiento.cantidad).label("total_usado"),
        )
        .join(Producto, Movimiento.producto_id == Producto.id)
        .where(
            Movimiento.fecha >= since,
            Movimiento.tipo == TipoMovimiento.uso,
        )
        .group_by(Movimiento.producto_id, Producto.nombre)
        .order_by(func.sum(Movimiento.cantidad).desc(), Producto.nombre.asc())
        .limit(limit)
    )

    try:
        rows = db.execute(stmt).all()
    except SQLAlchemyError as exc:
        _raise_db_error(exc)

    items = [
        TopUsedProductItem(
            producto_id=row.producto_id,
            producto_nombre=row.producto_nombre,
            total_usado=_decimal_to_float(row.total_usado),
        )
        for row in rows
    ]
    return TopUsedProductsResponse(items=items, days=days, limit=limit)


def get_adjustments_monitor(db: Session, *, days: int, top: int) -> AdjustmentsMonitorResponse:
    since = datetime.now(timezone.utc) - timedelta(days=days)
    base_filter = (
        Movimiento.fecha >= since,
        Movimiento.tipo == TipoMovimiento.ajuste,
    )

    try:
        total_adjustments = int(
            db.execute(
                select(func.count(Movimiento.id)).where(*base_filter)
            ).scalar_one()
            or 0
        )

        product_rows = db.execute(
            select(
                Movimiento.producto_id,
                Producto.nombre.label("producto_nombre"),
                func.count(Movimiento.id).label("ajustes_count"),
            )
            .join(Producto, Movimiento.producto_id == Producto.id)
            .where(*base_filter)
            .group_by(Movimiento.producto_id, Producto.nombre)
            .order_by(func.count(Movimiento.id).desc(), Producto.nombre.asc())
            .limit(top)
        ).all()

        from_loc_stmt = (
            select(Movimiento.from_locacion_id.label("locacion_id"))
            .where(*base_filter, Movimiento.from_locacion_id.is_not(None))
        )
        to_loc_stmt = (
            select(Movimiento.to_locacion_id.label("locacion_id"))
            .where(*base_filter, Movimiento.to_locacion_id.is_not(None))
        )
        loc_union = union_all(from_loc_stmt, to_loc_stmt).cte("ajuste_locaciones")

        location_rows = db.execute(
            select(
                Locacion.id.label("locacion_id"),
                Locacion.nombre.label("locacion_nombre"),
                func.count().label("ajustes_count"),
            )
            .select_from(Locacion)
            .join(loc_union, Locacion.id == loc_union.c.locacion_id)
            .group_by(Locacion.id, Locacion.nombre)
            .order_by(func.count().desc(), Locacion.nombre.asc())
            .limit(top)
        ).all()
    except SQLAlchemyError as exc:
        _raise_db_error(exc)

    top_products = [
        AdjustmentProductItem(
            producto_id=row.producto_id,
            producto_nombre=row.producto_nombre,
            ajustes_count=int(row.ajustes_count or 0),
        )
        for row in product_rows
    ]
    top_locations = [
        AdjustmentLocationItem(
            locacion_id=row.locacion_id,
            locacion_nombre=row.locacion_nombre,
            ajustes_count=int(row.ajustes_count or 0),
        )
        for row in location_rows
    ]

    return AdjustmentsMonitorResponse(
        total_adjustments=total_adjustments,
        top_products=top_products,
        top_locations=top_locations,
        days=days,
    )
