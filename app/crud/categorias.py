from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.categoria import Categoria
from app.schemas.categoria import CategoriaCreate, CategoriaUpdate


def get(db: Session, categoria_id: int) -> Categoria | None:
    return db.get(Categoria, categoria_id)


def get_by_nombre(db: Session, nombre: str) -> Categoria | None:
    stmt = select(Categoria).where(Categoria.nombre == nombre)
    return db.execute(stmt).scalar_one_or_none()


def get_multi(db: Session, *, skip: int = 0, limit: int = 100) -> list[Categoria]:
    stmt = select(Categoria).order_by(Categoria.nombre).offset(skip).limit(limit)
    return db.execute(stmt).scalars().all()


def create(db: Session, *, obj_in: CategoriaCreate) -> Categoria:
    db_obj = Categoria(**obj_in.model_dump())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def update(db: Session, *, db_obj: Categoria, obj_in: CategoriaUpdate) -> Categoria:
    update_data = obj_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_obj, field, value)
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def delete(db: Session, *, db_obj: Categoria) -> None:
    db.delete(db_obj)
    db.commit()
