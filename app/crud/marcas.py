from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.marca import Marca
from app.schemas.marca import MarcaCreate, MarcaUpdate


def get(db: Session, marca_id: int) -> Marca | None:
    return db.get(Marca, marca_id)


def get_by_nombre(db: Session, nombre: str) -> Marca | None:
    stmt = select(Marca).where(Marca.nombre == nombre)
    return db.execute(stmt).scalar_one_or_none()


def get_multi(db: Session, *, skip: int = 0, limit: int = 100) -> list[Marca]:
    stmt = select(Marca).order_by(Marca.nombre).offset(skip).limit(limit)
    return db.execute(stmt).scalars().all()


def create(db: Session, *, obj_in: MarcaCreate) -> Marca:
    db_obj = Marca(**obj_in.model_dump())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def update(db: Session, *, db_obj: Marca, obj_in: MarcaUpdate) -> Marca:
    update_data = obj_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_obj, field, value)
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def delete(db: Session, *, db_obj: Marca) -> None:
    db.delete(db_obj)
    db.commit()
