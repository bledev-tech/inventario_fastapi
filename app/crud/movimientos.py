from __future__ import annotations

from datetime import date

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.models.movimiento import Movimiento, TipoMovimiento
from app.schemas.movimiento import MovimientoCreate


def create(db: Session, *, obj_in: MovimientoCreate) -> Movimiento:
    data = obj_in.model_dump()
    data["tipo"] = obj_in.tipo.value
    db_obj = Movimiento(**data)
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def get_multi_by_producto(
    db: Session,
    *,
    producto_id: int,
    skip: int = 0,
    limit: int = 100,
) -> list[Movimiento]:
    stmt = (
        select(Movimiento)
        .where(Movimiento.producto_id == producto_id)
        .order_by(Movimiento.fecha.desc())
        .offset(skip)
        .limit(limit)
    )
    return db.execute(stmt).scalars().all()


def get_multi(
    db: Session,
    *,
    skip: int = 0,
    limit: int = 100,
    producto_id: int | None = None,
    locacion_id: int | None = None,
    tipo: TipoMovimiento | None = None,
    persona_id: int | None = None,
    proveedor_id: int | None = None,
) -> list[Movimiento]:
    stmt = (
        select(Movimiento)
        .order_by(Movimiento.fecha.desc())
        .offset(skip)
        .limit(limit)
    )
    if producto_id is not None:
        stmt = stmt.where(Movimiento.producto_id == producto_id)
    if tipo is not None:
        stmt = stmt.where(Movimiento.tipo == tipo)
    if locacion_id is not None:
        stmt = stmt.where(
            or_(
                Movimiento.from_locacion_id == locacion_id,
                Movimiento.to_locacion_id == locacion_id,
            )
        )
    if persona_id is not None:
        stmt = stmt.where(Movimiento.persona_id == persona_id)
    if proveedor_id is not None:
        stmt = stmt.where(Movimiento.proveedor_id == proveedor_id)
    return db.execute(stmt).scalars().all()


def get_por_dia(db: Session, *, fecha: date) -> list[Movimiento]:
    stmt = (
        select(Movimiento)
        .where(func.date(Movimiento.fecha) == fecha)
        .order_by(Movimiento.fecha.desc())
    )
    return db.execute(stmt).scalars().all()
