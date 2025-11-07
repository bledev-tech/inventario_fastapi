from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.proveedor import Proveedor
from app.schemas.proveedor import ProveedorCreate, ProveedorUpdate


def get(db: Session, proveedor_id: int) -> Proveedor | None:
    return db.get(Proveedor, proveedor_id)


def get_by_nombre(db: Session, nombre: str) -> Proveedor | None:
    stmt = select(Proveedor).where(Proveedor.nombre == nombre)
    return db.execute(stmt).scalar_one_or_none()


def get_multi(db: Session, *, skip: int = 0, limit: int = 100) -> list[Proveedor]:
    stmt = select(Proveedor).order_by(Proveedor.nombre).offset(skip).limit(limit)
    return db.execute(stmt).scalars().all()


def create(db: Session, *, obj_in: ProveedorCreate) -> Proveedor:
    db_obj = Proveedor(**obj_in.model_dump())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def update(db: Session, *, db_obj: Proveedor, obj_in: ProveedorUpdate) -> Proveedor:
    update_data = obj_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_obj, field, value)
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def delete(db: Session, *, db_obj: Proveedor) -> None:
    db.delete(db_obj)
    db.commit()
