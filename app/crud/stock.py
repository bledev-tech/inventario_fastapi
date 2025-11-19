from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal

from sqlalchemy import and_, case, func, select
from sqlalchemy.orm import Session

from app.models.categoria import Categoria
from app.models.locacion import Locacion
from app.models.movimiento import Movimiento, TipoMovimiento
from app.models.producto import Producto
from app.models.uom import UOM
from app.models.vista_stock import VistaStockActual


def get_all(db: Session) -> list[VistaStockActual]:
    return db.execute(select(VistaStockActual)).scalars().all()


def get_filtered(
    db: Session,
    *,
    producto_id: int | None = None,
    locacion_id: int | None = None,
) -> list[VistaStockActual]:
    stmt = select(VistaStockActual)
    if producto_id is not None:
        stmt = stmt.where(VistaStockActual.producto_id == producto_id)
    if locacion_id is not None:
        stmt = stmt.where(VistaStockActual.locacion_id == locacion_id)
    return db.execute(stmt).scalars().all()


def get_grouped_by_locacion(db: Session, *, include_zero: bool = False) -> list[dict]:
    stmt = (
        select(
            VistaStockActual.locacion_id.label("locacion_id"),
            Locacion.nombre.label("locacion_nombre"),
            Locacion.activa.label("locacion_activa"),
            VistaStockActual.producto_id.label("producto_id"),
            Producto.nombre.label("producto_nombre"),
            Producto.sku.label("producto_sku"),
            Producto.activo.label("producto_activo"),
            UOM.id.label("uom_id"),
            UOM.nombre.label("uom_nombre"),
            UOM.abreviatura.label("uom_abreviatura"),
            VistaStockActual.stock.label("stock"),
        )
        .join(Locacion, VistaStockActual.locacion_id == Locacion.id)
        .join(Producto, VistaStockActual.producto_id == Producto.id)
        .join(UOM, Producto.uom_id == UOM.id)
        .order_by(Locacion.nombre, Producto.nombre)
    )

    rows = db.execute(stmt).mappings().all()
    grouped: dict[int, dict] = {}

    for row in rows:
        stock: Decimal = row["stock"]
        if not include_zero and stock <= 0:
            continue

        locacion_id = row["locacion_id"]
        locacion = grouped.setdefault(
            locacion_id,
            {
                "locacion_id": locacion_id,
                "locacion_nombre": row["locacion_nombre"],
                "activa": row["locacion_activa"],
                "total_stock": Decimal("0"),
                "items": [],
            },
        )

        locacion["items"].append(
            {
                "producto_id": row["producto_id"],
                "producto_nombre": row["producto_nombre"],
                "sku": row["producto_sku"],
                "activo": row["producto_activo"],
                "uom_id": row["uom_id"],
                "uom_nombre": row["uom_nombre"],
                "uom_abreviatura": row["uom_abreviatura"],
                "stock": stock,
            }
        )
        locacion["total_stock"] += stock

    return sorted(grouped.values(), key=lambda loc: loc["locacion_nombre"])


def get_total_por_dia(db: Session, *, fecha: date) -> list[dict]:
    entrada_tipos = (TipoMovimiento.ingreso, TipoMovimiento.traspaso, TipoMovimiento.ajuste)
    salida_tipos = (TipoMovimiento.uso, TipoMovimiento.traspaso, TipoMovimiento.ajuste)

    ingreso_expr = case(
        (
            and_(
                Movimiento.to_locacion_id.isnot(None),
                Movimiento.tipo.in_(entrada_tipos),
            ),
            Movimiento.cantidad,
        ),
        else_=0,
    )
    salida_expr = case(
        (
            and_(
                Movimiento.from_locacion_id.isnot(None),
                Movimiento.tipo.in_(salida_tipos),
            ),
            Movimiento.cantidad,
        ),
        else_=0,
    )
    saldo_expr = ingreso_expr - salida_expr

    stmt = (
        select(
            Movimiento.producto_id.label("producto_id"),
            Producto.nombre.label("producto_nombre"),
            Producto.sku.label("sku"),
            UOM.id.label("uom_id"),
            UOM.nombre.label("uom_nombre"),
            UOM.abreviatura.label("uom_abreviatura"),
            func.coalesce(func.sum(saldo_expr), 0).label("total_stock"),
        )
        .join(Producto, Producto.id == Movimiento.producto_id)
        .join(UOM, Producto.uom_id == UOM.id)
        .where(func.date(Movimiento.fecha) <= fecha)
        .group_by(
            Movimiento.producto_id,
            Producto.nombre,
            Producto.sku,
            UOM.id,
            UOM.nombre,
            UOM.abreviatura,
        )
        .having(func.coalesce(func.sum(saldo_expr), 0) > 0)
        .order_by(Producto.nombre)
    )

    rows = db.execute(stmt).mappings().all()
    return [
        {
            "producto_id": row["producto_id"],
            "producto_nombre": row["producto_nombre"],
            "sku": row["sku"],
            "uom_id": row["uom_id"],
            "uom_nombre": row["uom_nombre"],
            "uom_abreviatura": row["uom_abreviatura"],
            "total_stock": row["total_stock"],
        }
        for row in rows
    ]


def get_weekly_inventory(
    db: Session,
    *,
    start_date: date,
    end_date: date,
    categoria_ids: list[int] | None = None,
    producto_ids: list[int] | None = None,
    include_zero: bool = False,
) -> dict:
    """Calcula el inventario diario por producto para el rango semanal solicitado."""

    entrada_tipos = (TipoMovimiento.ingreso, TipoMovimiento.traspaso, TipoMovimiento.ajuste)
    salida_tipos = (TipoMovimiento.uso, TipoMovimiento.traspaso, TipoMovimiento.ajuste)

    ingreso_expr = case(
        (
            and_(
                Movimiento.to_locacion_id.isnot(None),
                Movimiento.tipo.in_(entrada_tipos),
            ),
            Movimiento.cantidad,
        ),
        else_=0,
    )
    egreso_expr = case(
        (
            and_(
                Movimiento.from_locacion_id.isnot(None),
                Movimiento.tipo.in_(salida_tipos),
            ),
            Movimiento.cantidad,
        ),
        else_=0,
    )
    saldo_expr = ingreso_expr - egreso_expr
    fecha_col = func.date(Movimiento.fecha)

    pre_filters = []
    if categoria_ids:
        pre_filters.append(Producto.categoria_id.in_(categoria_ids))
    if producto_ids:
        pre_filters.append(Movimiento.producto_id.in_(producto_ids))

    base_cutoff = start_date - timedelta(days=1)

    base_stmt = (
        select(
            Movimiento.producto_id.label("producto_id"),
            Producto.nombre.label("producto_nombre"),
            Producto.sku.label("sku"),
            Producto.activo.label("activo"),
            Producto.categoria_id.label("categoria_id"),
            Categoria.nombre.label("categoria_nombre"),
            UOM.id.label("uom_id"),
            UOM.nombre.label("uom_nombre"),
            UOM.abreviatura.label("uom_abreviatura"),
            func.coalesce(func.sum(saldo_expr), 0).label("stock"),
        )
        .join(Producto, Producto.id == Movimiento.producto_id)
        .join(UOM, Producto.uom_id == UOM.id)
        .outerjoin(Categoria, Producto.categoria_id == Categoria.id)
        .where(fecha_col <= base_cutoff)
    )

    for condition in pre_filters:
        base_stmt = base_stmt.where(condition)

    base_stmt = base_stmt.group_by(
        Movimiento.producto_id,
        Producto.nombre,
        Producto.sku,
        Producto.activo,
        Producto.categoria_id,
        Categoria.nombre,
        UOM.id,
        UOM.nombre,
        UOM.abreviatura,
    )

    base_rows = db.execute(base_stmt).mappings().all()
    base_map: dict[int, dict] = {row["producto_id"]: dict(row) for row in base_rows}

    weekly_stmt = (
        select(
            Movimiento.producto_id.label("producto_id"),
            fecha_col.label("fecha"),
            func.coalesce(func.sum(ingreso_expr), 0).label("ingresos"),
            func.coalesce(func.sum(egreso_expr), 0).label("egresos"),
            func.coalesce(func.sum(saldo_expr), 0).label("neto"),
            Producto.nombre.label("producto_nombre"),
            Producto.sku.label("sku"),
            Producto.activo.label("activo"),
            Producto.categoria_id.label("categoria_id"),
            Categoria.nombre.label("categoria_nombre"),
            UOM.id.label("uom_id"),
            UOM.nombre.label("uom_nombre"),
            UOM.abreviatura.label("uom_abreviatura"),
        )
        .join(Producto, Producto.id == Movimiento.producto_id)
        .join(UOM, Producto.uom_id == UOM.id)
        .outerjoin(Categoria, Producto.categoria_id == Categoria.id)
        .where(fecha_col >= start_date)
        .where(fecha_col <= end_date)
    )

    for condition in pre_filters:
        weekly_stmt = weekly_stmt.where(condition)

    weekly_stmt = weekly_stmt.group_by(
        Movimiento.producto_id,
        fecha_col,
        Producto.nombre,
        Producto.sku,
        Producto.activo,
        Producto.categoria_id,
        Categoria.nombre,
        UOM.id,
        UOM.nombre,
        UOM.abreviatura,
    )

    weekly_rows = db.execute(weekly_stmt).mappings().all()

    product_meta: dict[int, dict] = {}
    daily_map: dict[tuple[int, date], dict] = {}

    for row in weekly_rows:
        producto_id = row["producto_id"]
        product_meta[producto_id] = {
            "producto_id": producto_id,
            "producto_nombre": row["producto_nombre"],
            "sku": row["sku"],
            "activo": row["activo"],
            "categoria_id": row["categoria_id"],
            "categoria_nombre": row["categoria_nombre"],
            "uom_id": row["uom_id"],
            "uom_nombre": row["uom_nombre"],
            "uom_abreviatura": row["uom_abreviatura"],
        }
        key = (producto_id, row["fecha"])
        current = daily_map.setdefault(
            key,
            {
                "ingresos": Decimal("0"),
                "egresos": Decimal("0"),
                "neto": Decimal("0"),
            },
        )
        current["ingresos"] += row["ingresos"]
        current["egresos"] += row["egresos"]
        current["neto"] += row["neto"]

    for producto_id, row in base_map.items():
        product_meta.setdefault(
            producto_id,
            {
                "producto_id": producto_id,
                "producto_nombre": row["producto_nombre"],
                "sku": row["sku"],
                "activo": row["activo"],
                "categoria_id": row["categoria_id"],
                "categoria_nombre": row["categoria_nombre"],
                "uom_id": row["uom_id"],
                "uom_nombre": row["uom_nombre"],
                "uom_abreviatura": row["uom_abreviatura"],
            },
        )

    producto_ids_considerados = set(product_meta.keys())

    if not producto_ids_considerados:
        # Consider incluir productos filtrados aunque no tengan movimientos
        meta_stmt = select(
            Producto.id,
            Producto.nombre,
            Producto.sku,
            Producto.activo,
            Producto.categoria_id,
            Categoria.nombre,
            UOM.id,
            UOM.nombre,
            UOM.abreviatura,
        ).join(UOM, Producto.uom_id == UOM.id).outerjoin(Categoria, Producto.categoria_id == Categoria.id)

        if categoria_ids:
            meta_stmt = meta_stmt.where(Producto.categoria_id.in_(categoria_ids))
        if producto_ids:
            meta_stmt = meta_stmt.where(Producto.id.in_(producto_ids))

        meta_rows = db.execute(meta_stmt).all()
        for (pid, nombre, sku, activo, cat_id, cat_nombre, uom_id, uom_nombre, uom_abrev) in meta_rows:
            product_meta[pid] = {
                "producto_id": pid,
                "producto_nombre": nombre,
                "sku": sku,
                "activo": activo,
                "categoria_id": cat_id,
                "categoria_nombre": cat_nombre,
                "uom_id": uom_id,
                "uom_nombre": uom_nombre,
                "uom_abreviatura": uom_abrev,
            }
        producto_ids_considerados = set(product_meta.keys())

    days: list[date] = []
    cursor = start_date
    while cursor <= end_date:
        days.append(cursor)
        cursor += timedelta(days=1)

    DecimalZero = Decimal("0")
    items: list[dict] = []
    total_stock_inicial = DecimalZero
    total_stock_final = DecimalZero
    total_ingresos = DecimalZero
    total_egresos = DecimalZero

    for producto_id in sorted(producto_ids_considerados):
        meta = product_meta.get(producto_id)
        if not meta:
            continue

        base_row = base_map.get(producto_id)
        stock_inicial = Decimal(base_row["stock"]) if base_row else DecimalZero
        running_stock = stock_inicial
        producto_tiene_datos = stock_inicial != DecimalZero
        producto_total_ingresos = DecimalZero
        producto_total_egresos = DecimalZero
        daily_records: list[dict] = []

        for day in days:
            daily = daily_map.get((producto_id, day))
            ingresos = daily["ingresos"] if daily else DecimalZero
            egresos = daily["egresos"] if daily else DecimalZero
            neto = daily["neto"] if daily else DecimalZero
            running_stock += neto
            if daily:
                producto_tiene_datos = True
            if ingresos:
                producto_total_ingresos += ingresos
            if egresos:
                producto_total_egresos += egresos

            if neto:
                producto_tiene_datos = True
            if running_stock:
                producto_tiene_datos = True

            daily_records.append(
                {
                    "date": day,
                    "ingresos": ingresos,
                    "egresos": egresos,
                    "neto": neto,
                    "stock_end": running_stock,
                }
            )

        stock_final = running_stock
        variation = stock_final - stock_inicial

        if not include_zero and not producto_tiene_datos:
            continue

        total_stock_inicial += stock_inicial
        total_stock_final += stock_final
        total_ingresos += producto_total_ingresos
        total_egresos += producto_total_egresos

        items.append(
            {
                "producto_id": producto_id,
                "producto_nombre": meta["producto_nombre"],
                "sku": meta["sku"],
                "categoria_id": meta["categoria_id"],
                "categoria_nombre": meta["categoria_nombre"],
                "uom_id": meta["uom_id"],
                "uom_nombre": meta["uom_nombre"],
                "uom_abreviatura": meta["uom_abreviatura"],
                "stock_inicial": stock_inicial,
                "stock_final": stock_final,
                "total_ingresos": producto_total_ingresos,
                "total_egresos": producto_total_egresos,
                "variation": variation,
                "daily": daily_records,
            }
        )

    return {
        "items": items,
        "totals": {
            "productos": len(items),
            "stock_inicial": total_stock_inicial,
            "stock_final": total_stock_final,
            "total_ingresos": total_ingresos,
            "total_egresos": total_egresos,
        },
    }
