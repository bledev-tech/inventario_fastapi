from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.categoria import Categoria
from app.schemas.categoria import CategoriaCreate, CategoriaUpdate


def get(db: Session, *, tenant_id: int, categoria_id: int) -> Categoria | None:
    stmt = select(Categoria).where(
        Categoria.id == categoria_id,
        Categoria.tenant_id == tenant_id,
    )
    return db.execute(stmt).scalar_one_or_none()


def get_by_nombre(db: Session, *, tenant_id: int, nombre: str) -> Categoria | None:
    stmt = select(Categoria).where(
        Categoria.nombre == nombre,
        Categoria.tenant_id == tenant_id,
    )
    return db.execute(stmt).scalar_one_or_none()


def get_multi(db: Session, *, tenant_id: int, skip: int = 0, limit: int = 100) -> list[Categoria]:
    stmt = (
        select(Categoria)
        .where(Categoria.tenant_id == tenant_id)
        .order_by(Categoria.nombre)
        .offset(skip)
        .limit(limit)
    )
    return db.execute(stmt).scalars().all()


def create(db: Session, *, tenant_id: int, obj_in: CategoriaCreate) -> Categoria:
    db_obj = Categoria(**obj_in.model_dump(), tenant_id=tenant_id)
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
