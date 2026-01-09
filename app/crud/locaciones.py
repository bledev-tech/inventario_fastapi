from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.locacion import Locacion
from app.schemas.locacion import LocacionCreate, LocacionUpdate


def get(db: Session, *, tenant_id: int, locacion_id: int) -> Locacion | None:
    stmt = select(Locacion).where(
        Locacion.id == locacion_id,
        Locacion.tenant_id == tenant_id,
    )
    return db.execute(stmt).scalar_one_or_none()


def get_multi(db: Session, *, tenant_id: int, skip: int = 0, limit: int = 100) -> list[Locacion]:
    stmt = (
        select(Locacion)
        .where(Locacion.tenant_id == tenant_id)
        .order_by(Locacion.id)
        .offset(skip)
        .limit(limit)
    )
    result = db.execute(stmt)
    return result.scalars().all()


def create(db: Session, *, tenant_id: int, obj_in: LocacionCreate) -> Locacion:
    db_obj = Locacion(**obj_in.model_dump(), tenant_id=tenant_id)
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def update(db: Session, *, db_obj: Locacion, obj_in: LocacionUpdate) -> Locacion:
    update_data = obj_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_obj, field, value)
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj
