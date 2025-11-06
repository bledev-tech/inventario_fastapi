from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.producto import Producto
from app.schemas.producto import ProductoCreate, ProductoUpdate


def get(db: Session, producto_id: int) -> Producto | None:
    return db.get(Producto, producto_id)


def get_by_sku(db: Session, sku: str) -> Producto | None:
    return db.execute(select(Producto).where(Producto.sku == sku)).scalar_one_or_none()


def get_multi(db: Session, *, skip: int = 0, limit: int = 100) -> list[Producto]:
    stmt = select(Producto).order_by(Producto.id).offset(skip).limit(limit)
    result = db.execute(stmt)
    return result.scalars().all()


def create(db: Session, *, obj_in: ProductoCreate) -> Producto:
    db_obj = Producto(**obj_in.model_dump())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def update(db: Session, *, db_obj: Producto, obj_in: ProductoUpdate) -> Producto:
    update_data = obj_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_obj, field, value)
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def delete(db: Session, *, db_obj: Producto) -> None:
    db.delete(db_obj)
    db.commit()
