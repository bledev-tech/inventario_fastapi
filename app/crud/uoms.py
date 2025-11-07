from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.uom import UOM
from app.schemas.uom import UOMCreate, UOMUpdate


def get(db: Session, uom_id: int) -> UOM | None:
    return db.get(UOM, uom_id)


def get_by_nombre(db: Session, nombre: str) -> UOM | None:
    stmt = select(UOM).where(UOM.nombre == nombre)
    return db.execute(stmt).scalar_one_or_none()


def get_by_abreviatura(db: Session, abreviatura: str) -> UOM | None:
    stmt = select(UOM).where(UOM.abreviatura == abreviatura)
    return db.execute(stmt).scalar_one_or_none()


def get_multi(db: Session, *, skip: int = 0, limit: int = 100) -> list[UOM]:
    stmt = select(UOM).order_by(UOM.nombre).offset(skip).limit(limit)
    return db.execute(stmt).scalars().all()


def create(db: Session, *, obj_in: UOMCreate) -> UOM:
    db_obj = UOM(**obj_in.model_dump())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def update(db: Session, *, db_obj: UOM, obj_in: UOMUpdate) -> UOM:
    update_data = obj_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_obj, field, value)
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def delete(db: Session, *, db_obj: UOM) -> None:
    db.delete(db_obj)
    db.commit()
