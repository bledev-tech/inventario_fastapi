from __future__ import annotations

from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.locacion import Locacion
from app.models.producto import Producto
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
            VistaStockActual.stock.label("stock"),
        )
        .join(Locacion, VistaStockActual.locacion_id == Locacion.id)
        .join(Producto, VistaStockActual.producto_id == Producto.id)
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
                "stock": stock,
            }
        )
        locacion["total_stock"] += stock

    return sorted(grouped.values(), key=lambda loc: loc["locacion_nombre"])
