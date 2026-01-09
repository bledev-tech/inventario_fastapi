from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.marca import Marca
from app.schemas.marca import MarcaCreate, MarcaUpdate


def get(db: Session, *, tenant_id: int, marca_id: int) -> Marca | None:
    stmt = select(Marca).where(
        Marca.id == marca_id,
        Marca.tenant_id == tenant_id,
    )
    return db.execute(stmt).scalar_one_or_none()


def get_by_nombre(db: Session, *, tenant_id: int, nombre: str) -> Marca | None:
    stmt = select(Marca).where(
        Marca.nombre == nombre,
        Marca.tenant_id == tenant_id,
    )
    return db.execute(stmt).scalar_one_or_none()


def get_multi(db: Session, *, tenant_id: int, skip: int = 0, limit: int = 100) -> list[Marca]:
    stmt = (
        select(Marca)
        .where(Marca.tenant_id == tenant_id)
        .order_by(Marca.nombre)
        .offset(skip)
        .limit(limit)
    )
    return db.execute(stmt).scalars().all()


def create(db: Session, *, tenant_id: int, obj_in: MarcaCreate) -> Marca:
    db_obj = Marca(**obj_in.model_dump(), tenant_id=tenant_id)
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
