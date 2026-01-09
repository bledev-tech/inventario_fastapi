from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.persona import Persona
from app.schemas.persona import PersonaCreate, PersonaUpdate


def get(db: Session, *, tenant_id: int, persona_id: int) -> Persona | None:
    stmt = select(Persona).where(
        Persona.id == persona_id,
        Persona.tenant_id == tenant_id,
    )
    return db.execute(stmt).scalar_one_or_none()


def get_by_nombre(db: Session, *, tenant_id: int, nombre: str) -> Persona | None:
    stmt = select(Persona).where(
        Persona.nombre == nombre,
        Persona.tenant_id == tenant_id,
    )
    return db.execute(stmt).scalar_one_or_none()


def get_multi(db: Session, *, tenant_id: int, skip: int = 0, limit: int = 100) -> list[Persona]:
    stmt = (
        select(Persona)
        .where(Persona.tenant_id == tenant_id)
        .order_by(Persona.nombre)
        .offset(skip)
        .limit(limit)
    )
    return db.execute(stmt).scalars().all()


def create(db: Session, *, tenant_id: int, obj_in: PersonaCreate) -> Persona:
    db_obj = Persona(**obj_in.model_dump(), tenant_id=tenant_id)
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def update(db: Session, *, db_obj: Persona, obj_in: PersonaUpdate) -> Persona:
    update_data = obj_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_obj, field, value)
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def delete(db: Session, *, db_obj: Persona) -> None:
    db.delete(db_obj)
    db.commit()
