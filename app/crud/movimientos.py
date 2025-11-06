from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.movimiento import Movimiento
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
